use actix_web::http::header::{HeaderName, HeaderValue};
use actix_web::{http::StatusCode, web, HttpRequest, HttpResponse};
use ahash::AHashMap;
use bytes::Bytes;
use futures_util::stream;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyTuple};
use std::io::ErrorKind;
use std::sync::Arc;
use tokio::fs::File;
use tokio::io::AsyncReadExt;

use crate::cors::{add_cors_headers_rust, add_cors_preflight_headers};
use crate::error;
use crate::middleware;
use crate::middleware::auth::populate_auth_context;
use crate::request::PyRequest;
use crate::router::parse_query_string;
use crate::state::{AppState, GLOBAL_ROUTER, ROUTE_METADATA, TASK_LOCALS};
use crate::streaming::{create_python_stream, create_sse_stream};
use crate::validation::{parse_cookies_inline, validate_auth_and_guards, AuthGuardResult};

// Reuse the global Python asyncio event loop created at server startup (TASK_LOCALS)

pub async fn handle_request(
    req: HttpRequest,
    body: web::Bytes,
    state: web::Data<Arc<AppState>>,
) -> HttpResponse {
    let method = req.method().as_str().to_string();
    let path = req.path().to_string();

    // Clone path and method for error handling
    let path_clone = path.clone();
    let method_clone = method.clone();

    let router = GLOBAL_ROUTER.get().expect("Router not initialized");

    // Find the route for the requested method and path
    // RouteMatch enum allows us to skip path param processing for static routes
    let (route_handler, path_params, handler_id, is_static_route_from_router) = {
        if let Some(route_match) = router.find(&method, &path) {
            let is_static = route_match.is_static();
            let handler_id = route_match.handler_id();
            let handler = Python::attach(|py| route_match.route().handler.clone_ref(py));
            let path_params = route_match.path_params(); // No allocation for static routes
            (handler, path_params, handler_id, is_static)
        } else {
            // No explicit handler found - check for automatic OPTIONS
            if method == "OPTIONS" {
                let available_methods = router.find_all_methods(&path);
                if !available_methods.is_empty() {
                    let allow_header = available_methods.join(", ");
                    let mut response = HttpResponse::NoContent()
                        .insert_header(("Allow", allow_header))
                        .insert_header(("Content-Type", "application/json"))
                        .finish();

                    // Try to find ANY route at this path to get CORS metadata
                    // Check methods in order: GET, POST, PUT, PATCH, DELETE
                    let methods_to_try = ["GET", "POST", "PUT", "PATCH", "DELETE"];
                    let mut found_cors = false;

                    for try_method in methods_to_try {
                        if let Some(route_match) = router.find(try_method, &path) {
                            let handler_id = route_match.handler_id();
                            let route_meta = ROUTE_METADATA
                                .get()
                                .and_then(|meta_map| meta_map.get(&handler_id).cloned());

                            if let Some(ref meta) = route_meta {
                                if let Some(ref cors_cfg) = meta.cors_config {
                                    let origin =
                                        req.headers().get("origin").and_then(|v| v.to_str().ok());

                                    let origin_allowed = add_cors_headers_rust(
                                        &mut response,
                                        origin,
                                        cors_cfg,
                                        &state,
                                    );

                                    if origin_allowed {
                                        add_cors_preflight_headers(&mut response, cors_cfg);
                                    }
                                    found_cors = true;
                                    break;
                                }
                            }
                        }
                    }

                    // If no route-level CORS found, use global CORS config
                    if !found_cors {
                        if let Some(ref global_cors) = state.global_cors_config {
                            let origin = req.headers().get("origin").and_then(|v| v.to_str().ok());
                            let origin_allowed =
                                add_cors_headers_rust(&mut response, origin, global_cors, &state);
                            if origin_allowed {
                                add_cors_preflight_headers(&mut response, global_cors);
                            }
                        }
                    }

                    return response;
                }
            }

            // Handle OPTIONS preflight for non-existent routes
            // IMPORTANT: Preflight MUST return 2xx status for browser to proceed with actual request
            // Browsers reject preflight responses with non-2xx status codes (like 404)
            if method == "OPTIONS" {
                if let Some(ref global_cors) = state.global_cors_config {
                    let origin = req.headers().get("origin").and_then(|v| v.to_str().ok());
                    let mut response = HttpResponse::NoContent().finish();
                    let origin_allowed =
                        add_cors_headers_rust(&mut response, origin, global_cors, &state);
                    if origin_allowed {
                        add_cors_preflight_headers(&mut response, global_cors);
                    }
                    return response;
                }
            }

            // Route not found - return 404 with CORS headers if global CORS is configured
            // This ensures browsers can read the 404 error message
            let mut response = HttpResponse::NotFound()
                .content_type("application/json")
                .body(r#"{"detail":"Not Found"}"#);

            // Add CORS headers using global config for 404 responses
            if let Some(ref global_cors) = state.global_cors_config {
                let origin = req.headers().get("origin").and_then(|v| v.to_str().ok());
                add_cors_headers_rust(&mut response, origin, global_cors, &state);
            }

            return response;
        }
    };

    // Get parsed route metadata (Rust-native) - clone to release DashMap lock immediately
    // This trade-off: small clone cost < lock contention across concurrent requests
    // NOTE: Fetch metadata EARLY so we can use optimization flags to skip unnecessary parsing
    let route_metadata = ROUTE_METADATA
        .get()
        .and_then(|meta_map| meta_map.get(&handler_id).cloned());

    // Optimization: Only parse query string if handler needs it
    // This saves ~0.5-1ms per request for handlers that don't use query params
    let needs_query = route_metadata
        .as_ref()
        .map(|m| m.needs_query)
        .unwrap_or(true);

    let query_params = if needs_query {
        if let Some(q) = req.uri().query() {
            parse_query_string(q)
        } else {
            AHashMap::new()
        }
    } else {
        AHashMap::new()
    };

    // Optimization: Check if handler needs headers
    // Headers are still needed for auth/rate limiting middleware, so we extract them for Rust
    // but can skip passing them to Python when the handler doesn't use Header() params
    let needs_headers = route_metadata
        .as_ref()
        .map(|m| m.needs_headers)
        .unwrap_or(true);

    // Extract headers early for middleware processing - pre-allocate with typical size
    // Headers are ALWAYS needed in Rust for middleware (auth, rate limiting, CORS)
    let mut headers: AHashMap<String, String> = AHashMap::with_capacity(16);

    // SECURITY: Use limits from AppState (configured once at startup)
    const MAX_HEADERS: usize = 100;
    let max_header_size = state.max_header_size;
    let mut header_count = 0;

    for (name, value) in req.headers().iter() {
        // Check header count limit
        header_count += 1;
        if header_count > MAX_HEADERS {
            return HttpResponse::BadRequest()
                .content_type("text/plain; charset=utf-8")
                .body("Too many headers");
        }

        if let Ok(v) = value.to_str() {
            // SECURITY: Validate header value size
            if v.len() > max_header_size {
                return HttpResponse::BadRequest()
                    .content_type("text/plain; charset=utf-8")
                    .body(format!(
                        "Header value too large (max {} bytes)",
                        max_header_size
                    ));
            }

            headers.insert(name.as_str().to_ascii_lowercase(), v.to_string());
        }
    }

    // Get peer address for rate limiting fallback
    let peer_addr = req.peer_addr().map(|addr| addr.ip().to_string());

    // Compute skip flags (e.g., skip compression)
    let skip_compression = route_metadata
        .as_ref()
        .map(|m| m.skip.contains("compression"))
        .unwrap_or(false);

    // Process rate limiting (Rust-native, no GIL)
    if let Some(ref route_meta) = route_metadata {
        if let Some(ref rate_config) = route_meta.rate_limit_config {
            if let Some(response) = middleware::rate_limit::check_rate_limit(
                handler_id,
                &headers,
                peer_addr.as_deref(),
                rate_config,
            ) {
                return response;
            }
        }
    }

    // Execute authentication and guards using shared validation logic
    let auth_ctx = if let Some(ref route_meta) = route_metadata {
        match validate_auth_and_guards(&headers, &route_meta.auth_backends, &route_meta.guards) {
            AuthGuardResult::Allow(ctx) => ctx,
            AuthGuardResult::Unauthorized => {
                return HttpResponse::Unauthorized()
                    .content_type("application/json")
                    .body(r#"{"detail":"Authentication required"}"#);
            }
            AuthGuardResult::Forbidden => {
                return HttpResponse::Forbidden()
                    .content_type("application/json")
                    .body(r#"{"detail":"Permission denied"}"#);
            }
        }
    } else {
        None
    };

    // Optimization: Only parse cookies if handler needs them
    // Cookie parsing can be expensive for requests with many cookies
    let needs_cookies = route_metadata
        .as_ref()
        .map(|m| m.needs_cookies)
        .unwrap_or(true);

    let cookies = if needs_cookies {
        parse_cookies_inline(headers.get("cookie").map(|s| s.as_str()))
    } else {
        AHashMap::new()
    };

    // For static routes, path_params is already an empty AHashMap from RouteMatch::Static
    // No additional processing needed - the router already optimized this
    // is_static_route_from_router is derived from RouteMatch at lookup time
    let _ = is_static_route_from_router; // Acknowledge the flag (used for future optimizations)

    // Check if this is a HEAD request (needed for body stripping after Python handler)
    let is_head_request = method == "HEAD";

    // All handlers (sync and async) go through async dispatch path
    // Sync handlers are executed in thread pool via sync_to_thread() in Python layer
    let fut = match Python::attach(|py| -> PyResult<_> {
        let dispatch = state.dispatch.clone_ref(py);
        let handler = route_handler.clone_ref(py);

        // Create context dict only if auth context is present
        let context = if let Some(ref auth) = auth_ctx {
            let ctx_dict = PyDict::new(py);
            let ctx_py = ctx_dict.unbind();
            populate_auth_context(&ctx_py, auth, py);
            Some(ctx_py)
        } else {
            None
        };

        // Optimization: Only pass headers to Python if handler needs them
        // Headers are already extracted for Rust middleware (auth, rate limiting, CORS)
        // but we can avoid copying them to Python if handler doesn't use Header() params
        let headers_for_python = if needs_headers {
            headers.clone()
        } else {
            AHashMap::new()
        };

        let request = PyRequest {
            method,
            path,
            body: body.to_vec(),
            path_params, // For static routes, this is already empty from RouteMatch::Static
            query_params,
            headers: headers_for_python,
            cookies,
            context,
            user: None,
            state: PyDict::new(py).unbind(), // Empty state dict for middleware and dynamic attributes
        };
        let request_obj = Py::new(py, request)?;

        // Reuse the global event loop locals initialized at server startup
        let locals = TASK_LOCALS.get().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("Asyncio loop not initialized")
        })?;

        // Call dispatch (always returns a coroutine since _dispatch is async)
        let coroutine = dispatch.call1(py, (handler, request_obj, handler_id))?;
        pyo3_async_runtimes::into_future_with_locals(locals, coroutine.into_bound(py))
    }) {
        Ok(f) => f,
        Err(e) => {
            return Python::attach(|py| {
                e.restore(py);
                if let Some(exc) = PyErr::take(py) {
                    let exc_value = exc.value(py);
                    error::handle_python_exception(
                        py,
                        exc_value,
                        &path_clone,
                        &method_clone,
                        state.debug,
                    )
                } else {
                    error::build_error_response(
                        py,
                        500,
                        "Handler error: failed to create coroutine".to_string(),
                        vec![],
                        None,
                        state.debug,
                    )
                }
            });
        }
    };

    match fut.await {
        Ok(result_obj) => {
            // Fast-path: extract and copy body in single GIL acquisition (eliminates separate GIL for drop)
            let fast_tuple: Option<(u16, Vec<(String, String)>, Vec<u8>)> = Python::attach(|py| {
                let obj = result_obj.bind(py);
                let tuple = obj.cast::<PyTuple>().ok()?;
                if tuple.len() != 3 {
                    return None;
                }

                // 0: status
                let status_code: u16 = tuple.get_item(0).ok()?.extract::<u16>().ok()?;

                // 1: headers
                let resp_headers: Vec<(String, String)> = tuple
                    .get_item(1)
                    .ok()?
                    .extract::<Vec<(String, String)>>()
                    .ok()?;

                // 2: body (bytes) - copy within GIL, drop Python object before releasing GIL
                let body_obj = tuple.get_item(2).ok()?;
                let pybytes = body_obj.cast::<PyBytes>().ok()?;
                let body_vec = pybytes.as_bytes().to_vec();
                // Python object drops automatically when this scope ends (still holding GIL)
                Some((status_code, resp_headers, body_vec))
            });

            if let Some((status_code, resp_headers, body_bytes)) = fast_tuple {
                let status = StatusCode::from_u16(status_code).unwrap_or(StatusCode::OK);
                let mut file_path: Option<String> = None;
                let mut headers: Vec<(String, String)> = Vec::with_capacity(resp_headers.len());
                for (k, v) in resp_headers {
                    if k.eq_ignore_ascii_case("x-bolt-file-path") {
                        file_path = Some(v);
                    } else {
                        headers.push((k, v));
                    }
                }
                if let Some(path) = file_path {
                    // Use direct tokio file I/O instead of NamedFile
                    // NamedFile::into_response() does expensive synchronous work (MIME detection, ETag, etc.)
                    // Python already provides content-type, so we skip all that overhead
                    return match File::open(&path).await {
                        Ok(mut file) => {
                            // Get file size
                            let file_size = match file.metadata().await {
                                Ok(metadata) => metadata.len(),
                                Err(e) => {
                                    return HttpResponse::InternalServerError()
                                        .content_type("text/plain; charset=utf-8")
                                        .body(format!("Failed to read file metadata: {}", e));
                                }
                            };

                            // For small files (<10MB), read into memory for better performance
                            // This avoids chunked encoding and allows proper Content-Length header
                            let file_bytes = if file_size < 10 * 1024 * 1024 {
                                let mut buffer = Vec::with_capacity(file_size as usize);
                                match file.read_to_end(&mut buffer).await {
                                    Ok(_) => buffer,
                                    Err(e) => {
                                        return HttpResponse::InternalServerError()
                                            .content_type("text/plain; charset=utf-8")
                                            .body(format!("Failed to read file: {}", e));
                                    }
                                }
                            } else {
                                // For large files, use streaming (or empty body for HEAD)
                                let mut builder = HttpResponse::build(status);
                                for (k, v) in headers {
                                    if let Ok(name) = HeaderName::try_from(k) {
                                        if let Ok(val) = HeaderValue::try_from(v) {
                                            builder.append_header((name, val));
                                        }
                                    }
                                }
                                if skip_compression {
                                    builder.append_header(("content-encoding", "identity"));
                                }

                                // HEAD requests must have empty body per RFC 7231
                                if is_head_request {
                                    return builder.body(Vec::<u8>::new());
                                }

                                // Create streaming response with 64KB chunks
                                let stream = stream::unfold(file, |mut file| async move {
                                    let mut buffer = vec![0u8; 64 * 1024];
                                    match file.read(&mut buffer).await {
                                        Ok(0) => None, // EOF
                                        Ok(n) => {
                                            buffer.truncate(n);
                                            Some((
                                                Ok::<_, std::io::Error>(Bytes::from(buffer)),
                                                file,
                                            ))
                                        }
                                        Err(e) => Some((Err(e), file)),
                                    }
                                });
                                return builder.streaming(stream);
                            };

                            // Build response with file bytes (small file path)
                            let mut builder = HttpResponse::build(status);

                            // Apply headers from Python (already includes content-type)
                            for (k, v) in headers {
                                if let Ok(name) = HeaderName::try_from(k) {
                                    if let Ok(val) = HeaderValue::try_from(v) {
                                        builder.append_header((name, val));
                                    }
                                }
                            }

                            if skip_compression {
                                builder.append_header(("content-encoding", "identity"));
                            }

                            // HEAD requests must have empty body per RFC 7231
                            let response_body = if is_head_request {
                                Vec::new()
                            } else {
                                file_bytes
                            };
                            builder.body(response_body)
                        }
                        Err(e) => {
                            // Return appropriate HTTP status based on error kind
                            match e.kind() {
                                ErrorKind::NotFound => HttpResponse::NotFound()
                                    .content_type("text/plain; charset=utf-8")
                                    .body("File not found"),
                                ErrorKind::PermissionDenied => HttpResponse::Forbidden()
                                    .content_type("text/plain; charset=utf-8")
                                    .body("Permission denied"),
                                _ => HttpResponse::InternalServerError()
                                    .content_type("text/plain; charset=utf-8")
                                    .body(format!("File error: {}", e)),
                            }
                        }
                    };
                } else {
                    // Non-file response path: body already copied within GIL scope above
                    let mut builder = HttpResponse::build(status);
                    for (k, v) in headers {
                        builder.append_header((k, v));
                    }
                    if skip_compression {
                        builder.append_header(("Content-Encoding", "identity"));
                    }

                    // HEAD requests must have empty body per RFC 7231
                    let response_body = if is_head_request {
                        Vec::new()
                    } else {
                        body_bytes
                    };
                    let mut response = builder.body(response_body);

                    // Add CORS headers if configured (NO GIL - uses Rust-native config)
                    if let Some(ref route_meta) = route_metadata {
                        if let Some(ref cors_cfg) = route_meta.cors_config {
                            let origin = req.headers().get("origin").and_then(|v| v.to_str().ok());
                            let _ = add_cors_headers_rust(&mut response, origin, cors_cfg, &state);
                        }
                    }

                    return response;
                }
            } else {
                // Fallback: handle tuple by extracting Vec<u8> under the GIL (compat path)
                if let Ok((status_code, resp_headers, body_bytes)) = Python::attach(|py| {
                    result_obj.extract::<(u16, Vec<(String, String)>, Vec<u8>)>(py)
                }) {
                    let status = StatusCode::from_u16(status_code).unwrap_or(StatusCode::OK);
                    let mut file_path: Option<String> = None;
                    let mut headers: Vec<(String, String)> = Vec::with_capacity(resp_headers.len());
                    for (k, v) in resp_headers {
                        if k.eq_ignore_ascii_case("x-bolt-file-path") {
                            file_path = Some(v);
                        } else {
                            headers.push((k, v));
                        }
                    }
                    if let Some(path) = file_path {
                        return match File::open(&path).await {
                            Ok(mut file) => {
                                let file_size = match file.metadata().await {
                                    Ok(metadata) => metadata.len(),
                                    Err(e) => {
                                        return HttpResponse::InternalServerError()
                                            .content_type("text/plain; charset=utf-8")
                                            .body(format!("Failed to read file metadata: {}", e));
                                    }
                                };
                                let file_bytes = if file_size < 10 * 1024 * 1024 {
                                    let mut buffer = Vec::with_capacity(file_size as usize);
                                    match file.read_to_end(&mut buffer).await {
                                        Ok(_) => buffer,
                                        Err(e) => {
                                            return HttpResponse::InternalServerError()
                                                .content_type("text/plain; charset=utf-8")
                                                .body(format!("Failed to read file: {}", e));
                                        }
                                    }
                                } else {
                                    let mut builder = HttpResponse::build(status);
                                    for (k, v) in headers {
                                        if let Ok(name) = HeaderName::try_from(k) {
                                            if let Ok(val) = HeaderValue::try_from(v) {
                                                builder.append_header((name, val));
                                            }
                                        }
                                    }
                                    if skip_compression {
                                        builder.append_header(("content-encoding", "identity"));
                                    }
                                    if is_head_request {
                                        return builder.body(Vec::<u8>::new());
                                    }
                                    let stream = stream::unfold(file, |mut file| async move {
                                        let mut buffer = vec![0u8; 64 * 1024];
                                        match file.read(&mut buffer).await {
                                            Ok(0) => None,
                                            Ok(n) => {
                                                buffer.truncate(n);
                                                Some((
                                                    Ok::<_, std::io::Error>(Bytes::from(buffer)),
                                                    file,
                                                ))
                                            }
                                            Err(e) => Some((Err(e), file)),
                                        }
                                    });
                                    return builder.streaming(stream);
                                };
                                let mut builder = HttpResponse::build(status);
                                for (k, v) in headers {
                                    if let Ok(name) = HeaderName::try_from(k) {
                                        if let Ok(val) = HeaderValue::try_from(v) {
                                            builder.append_header((name, val));
                                        }
                                    }
                                }
                                if skip_compression {
                                    builder.append_header(("content-encoding", "identity"));
                                }
                                let response_body = if is_head_request {
                                    Vec::new()
                                } else {
                                    file_bytes
                                };
                                builder.body(response_body)
                            }
                            Err(e) => match e.kind() {
                                ErrorKind::NotFound => HttpResponse::NotFound()
                                    .content_type("text/plain; charset=utf-8")
                                    .body("File not found"),
                                ErrorKind::PermissionDenied => HttpResponse::Forbidden()
                                    .content_type("text/plain; charset=utf-8")
                                    .body("Permission denied"),
                                _ => HttpResponse::InternalServerError()
                                    .content_type("text/plain; charset=utf-8")
                                    .body(format!("File error: {}", e)),
                            },
                        };
                    } else {
                        let mut builder = HttpResponse::build(status);
                        for (k, v) in headers {
                            builder.append_header((k, v));
                        }
                        if skip_compression {
                            builder.append_header(("Content-Encoding", "identity"));
                        }
                        let response_body = if is_head_request {
                            Vec::new()
                        } else {
                            body_bytes
                        };
                        let mut response = builder.body(response_body);
                        if let Some(ref route_meta) = route_metadata {
                            if let Some(ref cors_cfg) = route_meta.cors_config {
                                let origin =
                                    req.headers().get("origin").and_then(|v| v.to_str().ok());
                                let _ =
                                    add_cors_headers_rust(&mut response, origin, cors_cfg, &state);
                            }
                        }
                        return response;
                    }
                }
                let streaming = Python::attach(|py| {
                    let obj = result_obj.bind(py);
                    let is_streaming = (|| -> PyResult<bool> {
                        let m = py.import("django_bolt.responses")?;
                        let cls = m.getattr("StreamingResponse")?;
                        obj.is_instance(&cls)
                    })()
                    .unwrap_or(false);
                    if !is_streaming && !obj.hasattr("content").unwrap_or(false) {
                        return None;
                    }
                    let status_code: u16 = obj
                        .getattr("status_code")
                        .and_then(|v| v.extract())
                        .unwrap_or(200);
                    let mut headers: Vec<(String, String)> = Vec::new();
                    if let Ok(hobj) = obj.getattr("headers") {
                        if let Ok(hdict) = hobj.cast::<PyDict>() {
                            for (k, v) in hdict {
                                if let (Ok(ks), Ok(vs)) =
                                    (k.extract::<String>(), v.extract::<String>())
                                {
                                    headers.push((ks, vs));
                                }
                            }
                        }
                    }
                    let media_type: String = obj
                        .getattr("media_type")
                        .and_then(|v| v.extract())
                        .unwrap_or_else(|_| "application/octet-stream".to_string());
                    let has_ct = headers
                        .iter()
                        .any(|(k, _)| k.eq_ignore_ascii_case("content-type"));
                    if !has_ct {
                        headers.push(("content-type".to_string(), media_type.clone()));
                    }
                    let content_obj: Py<PyAny> = match obj.getattr("content") {
                        Ok(c) => c.unbind(),
                        Err(_) => return None,
                    };
                    // Extract pre-computed is_async_generator metadata (detected at StreamingResponse instantiation)
                    let is_async_generator: bool = obj
                        .getattr("is_async_generator")
                        .and_then(|v| v.extract())
                        .unwrap_or(false);
                    Some((
                        status_code,
                        headers,
                        media_type,
                        content_obj,
                        is_async_generator,
                    ))
                });

                if let Some((status_code, headers, media_type, content_obj, is_async_generator)) =
                    streaming
                {
                    let status = StatusCode::from_u16(status_code).unwrap_or(StatusCode::OK);
                    let mut builder = HttpResponse::build(status);
                    for (k, v) in headers {
                        builder.append_header((k, v));
                    }
                    if media_type == "text/event-stream" {
                        // HEAD requests must have empty body per RFC 7231
                        if is_head_request {
                            builder.content_type("text/event-stream");
                            builder.append_header(("X-Accel-Buffering", "no"));
                            builder.append_header((
                                "Cache-Control",
                                "no-cache, no-store, must-revalidate",
                            ));
                            builder.append_header(("Pragma", "no-cache"));
                            builder.append_header(("Expires", "0"));
                            if skip_compression {
                                builder.append_header(("Content-Encoding", "identity"));
                            }
                            return builder.body(Vec::<u8>::new());
                        }

                        let final_content_obj = content_obj;
                        builder.append_header(("X-Accel-Buffering", "no"));
                        builder.append_header((
                            "Cache-Control",
                            "no-cache, no-store, must-revalidate",
                        ));
                        builder.append_header(("Pragma", "no-cache"));
                        builder.append_header(("Expires", "0"));
                        if skip_compression {
                            builder.append_header(("Content-Encoding", "identity"));
                        }
                        builder.content_type("text/event-stream");

                        let stream = create_sse_stream(final_content_obj, is_async_generator);
                        return builder.streaming(stream);
                    } else {
                        // HEAD requests must have empty body per RFC 7231
                        if is_head_request {
                            if skip_compression {
                                builder.append_header(("Content-Encoding", "identity"));
                            }
                            return builder.body(Vec::<u8>::new());
                        }

                        let final_content = content_obj;
                        // Use unified streaming for all streaming responses (sync and async)
                        if skip_compression {
                            builder.append_header(("Content-Encoding", "identity"));
                        }
                        let stream = create_python_stream(final_content, is_async_generator);
                        return builder.streaming(stream);
                    }
                } else {
                    return Python::attach(|py| {
                        error::build_error_response(
                        py,
                        500,
                        "Handler returned unsupported response type (expected tuple or StreamingResponse)".to_string(),
                        vec![],
                        None,
                        state.debug,
                    )
                    });
                }
            }
        }
        Err(e) => {
            // Use new error handler for Python exceptions during handler execution
            return Python::attach(|py| {
                // Convert PyErr to exception instance
                e.restore(py);
                if let Some(exc) = PyErr::take(py) {
                    let exc_value = exc.value(py);
                    error::handle_python_exception(
                        py,
                        exc_value,
                        &path_clone,
                        &method_clone,
                        state.debug,
                    )
                } else {
                    error::build_error_response(
                        py,
                        500,
                        "Handler execution error".to_string(),
                        vec![],
                        None,
                        state.debug,
                    )
                }
            });
        }
    }
}

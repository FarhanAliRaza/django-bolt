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

use crate::error;
use crate::middleware;
use crate::middleware::auth::populate_auth_context;
use crate::request::PyRequest;
use crate::response_builder;
use crate::responses;
use crate::router::parse_query_string;
use crate::state::{AppState, GLOBAL_ROUTER, ROUTE_METADATA, TASK_LOCALS};
use crate::streaming::{create_python_stream, create_sse_stream};
use crate::validation::{parse_cookies_inline, validate_auth_and_guards, AuthGuardResult};

// Reuse the global Python asyncio event loop created at server startup (TASK_LOCALS)

/// Build an HTTP response for a file path.
/// Handles both small files (loaded into memory) and large files (streamed).
pub async fn build_file_response(
    file_path: &str,
    status: StatusCode,
    headers: Vec<(String, String)>,
    skip_compression: bool,
    is_head_request: bool,
) -> HttpResponse {
    match File::open(file_path).await {
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
            if file_size < 10 * 1024 * 1024 {
                let mut buffer = Vec::with_capacity(file_size as usize);
                match file.read_to_end(&mut buffer).await {
                    Ok(_) => {
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
                        let body = if is_head_request { Vec::new() } else { buffer };
                        builder.body(body)
                    }
                    Err(e) => HttpResponse::InternalServerError()
                        .content_type("text/plain; charset=utf-8")
                        .body(format!("Failed to read file: {}", e)),
                }
            } else {
                // For large files, use streaming
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
                            Some((Ok::<_, std::io::Error>(Bytes::from(buffer)), file))
                        }
                        Err(e) => Some((Err(e), file)),
                    }
                });
                builder.streaming(stream)
            }
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
    }
}

/// Handle Python errors and convert to HTTP response
pub fn handle_python_error(py: Python<'_>, err: PyErr, path: &str, method: &str, debug: bool) -> HttpResponse {
    err.restore(py);
    if let Some(exc) = PyErr::take(py) {
        let exc_value = exc.value(py);
        error::handle_python_exception(py, exc_value, path, method, debug)
    } else {
        error::build_error_response(py, 500, "Handler execution error".to_string(), vec![], None, debug)
    }
}

/// Extract headers from request with validation
/// OPTIMIZATION: HeaderName::as_str() already returns lowercase (http crate canonical form)
/// so we skip the redundant to_ascii_lowercase() call (~50ns saved per header)
pub fn extract_headers(
    req: &HttpRequest,
    max_header_size: usize,
) -> Result<AHashMap<String, String>, HttpResponse> {
    const MAX_HEADERS: usize = 100;
    let mut headers: AHashMap<String, String> = AHashMap::with_capacity(16);
    let mut header_count = 0;

    for (name, value) in req.headers().iter() {
        header_count += 1;
        if header_count > MAX_HEADERS {
            return Err(responses::error_400_too_many_headers());
        }
        if let Ok(v) = value.to_str() {
            if v.len() > max_header_size {
                return Err(responses::error_400_header_too_large(max_header_size));
            }
            // HeaderName::as_str() returns lowercase already (http crate stores canonically)
            headers.insert(name.as_str().to_owned(), v.to_owned());
        }
    }
    Ok(headers)
}

pub async fn handle_request(
    req: HttpRequest,
    body: web::Bytes,
    state: web::Data<Arc<AppState>>,
) -> HttpResponse {
    // Keep as &str - no allocation, only clone on error paths
    let method = req.method().as_str();
    let path = req.path();

    let router = GLOBAL_ROUTER.get().expect("Router not initialized");

    // Find the route for the requested method and path
    // RouteMatch enum allows us to skip path param processing for static routes
    // OPTIMIZATION: Defer handler clone_ref to single GIL acquisition later
    // This eliminates one GIL acquisition per request (~1-3µs saved)
    let (path_params, handler_id) = {
        if let Some(route_match) = router.find(method, path) {
            let handler_id = route_match.handler_id();
            let path_params = route_match.path_params(); // No allocation for static routes
            (path_params, handler_id)
        } else {
            // No explicit handler found - check for automatic OPTIONS
            if method == "OPTIONS" {
                let available_methods = router.find_all_methods(path);
                if !available_methods.is_empty() {
                    let allow_header = available_methods.join(", ");
                    // CORS headers will be added by CorsMiddleware
                    return HttpResponse::NoContent()
                        .insert_header(("Allow", allow_header))
                        .insert_header(("Content-Type", "application/json"))
                        .finish();
                }
            }

            // Handle OPTIONS preflight for non-existent routes
            // IMPORTANT: Preflight MUST return 2xx status for browser to proceed with actual request
            // Browsers reject preflight responses with non-2xx status codes (like 404)
            if method == "OPTIONS" {
                // Check if global CORS is configured
                if state.global_cors_config.is_some() {
                    // CORS headers will be added by CorsMiddleware
                    return HttpResponse::NoContent().finish();
                }
            }

            // Route not found - return 404
            // CORS headers will be added by CorsMiddleware if configured
            return responses::error_404();
        }
    };

    // Store method/path as owned for Python (needed after route_match is dropped)
    // OPTIMIZATION: Use compact strings to reduce allocation overhead
    let method_owned = method.to_string();
    let path_owned = path.to_string();

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

    // Compute skip_cors flag for CorsMiddleware
    let skip_cors = route_metadata
        .as_ref()
        .map(|m| m.skip.contains("cors"))
        .unwrap_or(false);

    // Extract and validate headers
    let headers = match extract_headers(&req, state.max_header_size) {
        Ok(h) => h,
        Err(response) => return response,
    };

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
                &method,
                &path,
            ) {
                // CORS headers will be added by CorsMiddleware
                return response;
            }
        }
    }

    // Execute authentication and guards using shared validation logic
    let auth_ctx = if let Some(ref route_meta) = route_metadata {
        match validate_auth_and_guards(&headers, &route_meta.auth_backends, &route_meta.guards) {
            AuthGuardResult::Allow(ctx) => ctx,
            AuthGuardResult::Unauthorized => {
                // CORS headers will be added by CorsMiddleware
                return responses::error_401();
            }
            AuthGuardResult::Forbidden => {
                // CORS headers will be added by CorsMiddleware
                return responses::error_403();
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


    // Check if this is a HEAD request (needed for body stripping after Python handler)
    let is_head_request = method == "HEAD";

    // All handlers (sync and async) go through async dispatch path
    // Sync handlers are executed in thread pool via sync_to_thread() in Python layer
    // OPTIMIZATION: Single GIL acquisition for handler clone + dispatch call
    let fut = match Python::attach(|py| -> PyResult<_> {
        // Get handler directly from router (O(1) for static routes)
        // This defers clone_ref to here, eliminating earlier GIL acquisition
        let handler = router
            .find(&method_owned, &path_owned)
            .map(|rm| rm.route().handler.clone_ref(py))
            .ok_or_else(|| {
                pyo3::exceptions::PyRuntimeError::new_err("Route not found during dispatch")
            })?;
        let dispatch = state.dispatch.clone_ref(py);

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
            method: method_owned.clone(),
            path: path_owned.clone(),
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
                handle_python_error(py, e, &path_owned, &method_owned, state.debug)
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
                if let Some(fpath) = file_path {
                    return build_file_response(&fpath, status, headers, skip_compression, is_head_request).await;
                } else {
                    // Non-file response path: body already copied within GIL scope above
                    // Use optimized response builder
                    let response_body = if is_head_request {
                        Vec::new()
                    } else {
                        body_bytes
                    };

                    let mut response = response_builder::build_response_with_headers(
                        status,
                        headers,
                        skip_compression,
                        response_body,
                    );

                    // Set skip-cors marker if @skip_middleware("cors") is used
                    if skip_cors {
                        response
                            .headers_mut()
                            .insert("x-bolt-skip-cors".parse().unwrap(), "true".parse().unwrap());
                    }

                    // CORS headers will be added by CorsMiddleware
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
                    if let Some(fpath) = file_path {
                        return build_file_response(&fpath, status, headers, skip_compression, is_head_request).await;
                    } else {
                        let mut builder = HttpResponse::build(status);
                        for (k, v) in headers {
                            builder.append_header((k, v));
                        }
                        if skip_compression {
                            builder.append_header(("Content-Encoding", "identity"));
                        }
                        // Set skip-cors marker if @skip_middleware("cors") is used
                        if skip_cors {
                            builder.append_header(("x-bolt-skip-cors", "true"));
                        }
                        let response_body = if is_head_request {
                            Vec::new()
                        } else {
                            body_bytes
                        };
                        // CORS headers will be added by CorsMiddleware
                        return builder.body(response_body);
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

                    if media_type == "text/event-stream" {
                        // HEAD requests must have empty body per RFC 7231
                        if is_head_request {
                            // Use optimized SSE response builder (batches all SSE headers)
                            let mut builder = response_builder::build_sse_response(
                                status,
                                headers,
                                skip_compression,
                            );
                            let mut response = builder.body(Vec::<u8>::new());

                            // Set skip-cors marker if @skip_middleware("cors") is used
                            if skip_cors {
                                response
                                    .headers_mut()
                                    .insert("x-bolt-skip-cors".parse().unwrap(), "true".parse().unwrap());
                            }

                            // CORS headers will be added by CorsMiddleware
                            return response;
                        }

                        // Use optimized SSE response builder (batches all SSE headers)
                        let final_content_obj = content_obj;
                        let mut builder = response_builder::build_sse_response(
                            status,
                            headers,
                            skip_compression,
                        );
                        let stream = create_sse_stream(final_content_obj, is_async_generator);
                        let mut response = builder.streaming(stream);

                        // Set skip-cors marker if @skip_middleware("cors") is used
                        if skip_cors {
                            response
                                .headers_mut()
                                .insert("x-bolt-skip-cors".parse().unwrap(), "true".parse().unwrap());
                        }

                        // CORS headers will be added by CorsMiddleware
                        return response;
                    } else {
                        // Non-SSE streaming responses
                        let mut builder = HttpResponse::build(status);
                        for (k, v) in headers {
                            builder.append_header((k, v));
                        }

                        // HEAD requests must have empty body per RFC 7231
                        if is_head_request {
                            if skip_compression {
                                builder.append_header(("Content-Encoding", "identity"));
                            }
                            // Set skip-cors marker if @skip_middleware("cors") is used
                            if skip_cors {
                                builder.append_header(("x-bolt-skip-cors", "true"));
                            }
                            // CORS headers will be added by CorsMiddleware
                            return builder.body(Vec::<u8>::new());
                        }

                        let final_content = content_obj;
                        // Use unified streaming for all streaming responses (sync and async)
                        if skip_compression {
                            builder.append_header(("Content-Encoding", "identity"));
                        }
                        // Set skip-cors marker if @skip_middleware("cors") is used
                        if skip_cors {
                            builder.append_header(("x-bolt-skip-cors", "true"));
                        }
                        let stream = create_python_stream(final_content, is_async_generator);
                        // CORS headers will be added by CorsMiddleware
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
            return Python::attach(|py| {
                handle_python_error(py, e, &path_owned, &method_owned, state.debug)
            });
        }
    }
}

use actix_web::http::header::{HeaderName, HeaderValue};
use actix_web::{http::StatusCode, web, HttpRequest, HttpResponse};
use ahash::AHashMap;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::Arc;
use tokio::fs::File;
use tokio::io::AsyncReadExt;
use futures_util::stream::{self, StreamExt};
use bytes::Bytes;

use crate::direct_stream;
use crate::error;
use crate::middleware;
use crate::middleware::auth::{authenticate, populate_auth_context};
use crate::permissions::{evaluate_guards, GuardResult};
use crate::request::PyRequest;
use crate::router::parse_query_string;
use crate::state::{AppState, GLOBAL_ROUTER, MIDDLEWARE_METADATA, ROUTE_METADATA, TASK_LOCALS};
use crate::streaming::create_python_stream;

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
    let (route_handler, path_params, handler_id) = {
        if let Some((route, path_params, handler_id)) = router.find(&method, &path) {
            (
                Python::attach(|py| route.handler.clone_ref(py)),
                path_params,
                handler_id,
            )
        } else {
            // Automatic OPTIONS handling: if no explicit OPTIONS handler exists,
            // check if other methods are registered for this path and return Allow header
            if method == "OPTIONS" {
                let available_methods = router.find_all_methods(&path);
                if !available_methods.is_empty() {
                    // Return 200 OK with Allow header listing available methods
                    let allow_header = available_methods.join(", ");
                    return HttpResponse::Ok()
                        .insert_header(("Allow", allow_header))
                        .content_type("application/json")
                        .body(b"{}".to_vec());
                }
            }

            return HttpResponse::NotFound()
                .content_type("text/plain; charset=utf-8")
                .body("Not Found");
        }
    };

    let query_params = if let Some(q) = req.uri().query() {
        parse_query_string(q)
    } else {
        AHashMap::new()
    };

    // Extract headers early for middleware processing - pre-allocate with typical size
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
                    .body(format!("Header value too large (max {} bytes)", max_header_size));
            }

            headers.insert(name.as_str().to_ascii_lowercase(), v.to_string());
        }
    }

    // Get peer address for rate limiting fallback
    let peer_addr = req.peer_addr().map(|addr| addr.ip().to_string());

    // Check for middleware metadata (Python-based, for backward compatibility)
    let middleware_meta = MIDDLEWARE_METADATA.get().and_then(|meta_map| {
        meta_map
            .get(&handler_id)
            .map(|m| Python::attach(|py| m.clone_ref(py)))
    });

    // Get parsed route metadata (Rust-native)
    let route_metadata = ROUTE_METADATA
        .get()
        .and_then(|meta_map| meta_map.get(&handler_id).cloned());
    // Compute skip flags (e.g., skip compression)
    let skip_compression = route_metadata
        .as_ref()
        .map(|m| m.skip.contains("compression"))
        .unwrap_or(false);

    // Process old-style middleware (CORS preflight, rate limiting, auth)
    if let Some(ref meta) = middleware_meta {
        if let Some(early_response) = middleware::process_middleware(
            &method,
            &path,
            &headers,
            peer_addr.as_deref(),
            handler_id,
            meta,
        )
        .await
        {
            return early_response;
        }
    }

    // Execute authentication and guards (new system)
    let auth_ctx = if let Some(ref route_meta) = route_metadata {
        if !route_meta.auth_backends.is_empty() {
            authenticate(&headers, &route_meta.auth_backends)
        } else {
            None
        }
    } else {
        None
    };

    // Evaluate guards
    if let Some(ref route_meta) = route_metadata {
        if !route_meta.guards.is_empty() {
            match evaluate_guards(&route_meta.guards, auth_ctx.as_ref()) {
                GuardResult::Allow => {
                    // Pass through
                }
                GuardResult::Unauthorized => {
                    return HttpResponse::Unauthorized()
                        .content_type("application/json")
                        .body(r#"{"detail":"Authentication required"}"#);
                }
                GuardResult::Forbidden => {
                    return HttpResponse::Forbidden()
                        .content_type("application/json")
                        .body(r#"{"detail":"Permission denied"}"#);
                }
            }
        }
    }

    // Pre-parse cookies outside of GIL
    let mut cookies: AHashMap<String, String> = AHashMap::with_capacity(8);
    if let Some(raw_cookie) = headers.get("cookie") {
        for pair in raw_cookie.split(';') {
            let part = pair.trim();
            if let Some(eq) = part.find('=') {
                let (k, v) = part.split_at(eq);
                let v2 = &v[1..];
                if !k.is_empty() {
                    cookies.insert(k.to_string(), v2.to_string());
                }
            }
        }
    }

    // Check if this is a HEAD request (needed for body stripping after Python handler)
    let is_head_request = method == "HEAD";

    // Single GIL acquisition for all Python operations
    let fut = match Python::attach(|py| -> PyResult<_> {
        // Clone Python objects
        let dispatch = state.dispatch.clone_ref(py);
        let handler = route_handler.clone_ref(py);

        // Create context dict if middleware or auth is present
        let context = if middleware_meta.is_some() || auth_ctx.is_some() {
            let ctx_dict = PyDict::new(py);
            let ctx_py = ctx_dict.unbind();
            // Populate with auth context if present
            if let Some(ref auth) = auth_ctx {
                populate_auth_context(&ctx_py, auth, py);
            }
            Some(ctx_py)
        } else {
            None
        };

        let request = PyRequest {
            method,
            path,
            body: body.to_vec(),
            path_params,
            query_params,
            headers,
            cookies,
            context,
        };
        let request_obj = Py::new(py, request)?;

        let locals_owned;
        let locals = if let Some(globals) = TASK_LOCALS.get() {
            globals
        } else {
            locals_owned = pyo3_async_runtimes::tokio::get_current_locals(py)?;
            &locals_owned
        };

        // Pass handler_id to dispatch so it can lookup the original API instance
        let coroutine = dispatch.call1(py, (handler, request_obj, handler_id))?;
        pyo3_async_runtimes::into_future_with_locals(&locals, coroutine.into_bound(py))
    }) {
        Ok(f) => f,
        Err(e) => {
            // Use new error handler
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
            let tuple_result: Result<(u16, Vec<(String, String)>, Vec<u8>), _> =
                Python::attach(|py| result_obj.extract(py));
            if let Ok((status_code, resp_headers, body_bytes)) = tuple_result {
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
                                            Some((Ok::<_, std::io::Error>(Bytes::from(buffer)), file))
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
                            let response_body = if is_head_request { Vec::new() } else { file_bytes };
                            builder.body(response_body)
                        }
                        Err(e) => {
                            // Return appropriate HTTP status based on error kind
                            use std::io::ErrorKind;
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
                    let mut builder = HttpResponse::build(status);
                    for (k, v) in headers {
                        builder.append_header((k, v));
                    }
                    if skip_compression {
                        builder.append_header(("Content-Encoding", "identity"));
                    }
                    // HEAD requests must have empty body per RFC 7231
                    let response_body = if is_head_request { Vec::new() } else { body_bytes };
                    let mut response = builder.body(response_body);

                    // Add CORS headers if middleware is configured
                    if let Some(ref meta) = middleware_meta {
                        let origin = req.headers().get("origin").and_then(|v| v.to_str().ok());
                        middleware::add_cors_headers(&mut response, origin, meta);
                    }

                    return response;
                }
            } else {
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
                        if let Ok(hdict) = hobj.downcast::<PyDict>() {
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
                    Some((status_code, headers, media_type, content_obj))
                });

                if let Some((status_code, headers, media_type, content_obj)) = streaming {
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

                        let mut final_content_obj = content_obj;
                        // Combine async check and wrapping into single GIL acquisition
                        let (is_async_sse, wrapped_content) = Python::attach(|py| {
                            let obj = final_content_obj.bind(py);
                            let has_async = obj.hasattr("__aiter__").unwrap_or(false)
                                || obj.hasattr("__anext__").unwrap_or(false);
                            if !has_async {
                                return (false, None);
                            }
                            // Try to wrap async iterator
                            let wrapped = (|| -> Option<Py<PyAny>> {
                                let collector_module =
                                    py.import("django_bolt.async_collector").ok()?;
                                let collector_class =
                                    collector_module.getattr("AsyncToSyncCollector").ok()?;
                                collector_class
                                    .call1((obj.clone(), 5, 1))
                                    .ok()
                                    .map(|w| w.unbind())
                            })();
                            (wrapped.is_none(), wrapped)
                        });
                        if let Some(w) = wrapped_content {
                            final_content_obj = w;
                        }
                        if is_async_sse {
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
                            return builder.streaming(create_python_stream(final_content_obj));
                        } else {
                            match direct_stream::create_sse_response(final_content_obj) {
                                Ok(mut resp) => {
                                    if skip_compression {
                                        if let Ok(val) = HeaderValue::try_from("identity") {
                                            resp.headers_mut().insert(
                                                actix_web::http::header::CONTENT_ENCODING,
                                                val,
                                            );
                                        }
                                    }
                                    return resp;
                                }
                                Err(_) => {
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
                                    return builder.content_type("text/event-stream").body("");
                                }
                            }
                        }
                    } else {
                        // HEAD requests must have empty body per RFC 7231
                        if is_head_request {
                            if skip_compression {
                                builder.append_header(("Content-Encoding", "identity"));
                            }
                            return builder.body(Vec::<u8>::new());
                        }

                        let mut final_content = content_obj;
                        // Combine async check and wrapping into single GIL acquisition
                        let (needs_async_stream, wrapped_content) = Python::attach(|py| {
                            let obj = final_content.bind(py);
                            let has_async = obj.hasattr("__aiter__").unwrap_or(false)
                                || obj.hasattr("__anext__").unwrap_or(false);
                            if !has_async {
                                return (false, None);
                            }
                            // Try to wrap async iterator
                            let wrapped = (|| -> Option<Py<PyAny>> {
                                let collector_module =
                                    py.import("django_bolt.async_collector").ok()?;
                                let collector_class =
                                    collector_module.getattr("AsyncToSyncCollector").ok()?;
                                collector_class
                                    .call1((obj.clone(), 20, 2))
                                    .ok()
                                    .map(|w| w.unbind())
                            })();
                            (wrapped.is_none(), wrapped)
                        });

                        if needs_async_stream {
                            if skip_compression {
                                builder.append_header(("Content-Encoding", "identity"));
                            }
                            let stream = create_python_stream(final_content);
                            return builder.streaming(stream);
                        }

                        if let Some(w) = wrapped_content {
                            final_content = w;
                        }
                        {
                            let mut direct = direct_stream::PythonDirectStream::new(final_content);
                            if let Some(body) = direct.try_collect_small() {
                                if skip_compression {
                                    builder.append_header(("Content-Encoding", "identity"));
                                }
                                return builder.body(body);
                            }
                            if skip_compression {
                                builder.append_header(("Content-Encoding", "identity"));
                            }
                            return builder.streaming(Box::pin(direct));
                        }
                    }
                } else {
                    return Python::with_gil(|py| {
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

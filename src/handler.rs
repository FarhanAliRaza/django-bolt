use actix_web::http::header::{HeaderName, HeaderValue};
use actix_web::{http::StatusCode, web, HttpRequest, HttpResponse};
use ahash::AHashMap;
use bytes::Bytes;
use futures_util::stream;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::Duration;
use tokio::fs::File;
use tokio::io::AsyncReadExt;

use crate::error;
use crate::metadata::CorsConfig;
use crate::middleware;
use crate::middleware::auth::{authenticate, populate_auth_context};
use crate::permissions::{evaluate_guards, GuardResult};
use crate::request::PyRequest;
use crate::router::parse_query_string;
use crate::state::{
    AppState, GLOBAL_ROUTER, MIDDLEWARE_METADATA, RESPONSE_CHANNELS, ROUTE_METADATA,
};

/// Request ID counter for queue-based system
static REQUEST_ID_COUNTER: AtomicU64 = AtomicU64::new(1);

/// Add CORS headers to response using Rust-native config (NO GIL required)
fn add_cors_headers_rust(
    response: &mut HttpResponse,
    request_origin: Option<&str>,
    cors_config: &CorsConfig,
    global_origins: &[String],
) {
    let origins = if !cors_config.origins.is_empty() {
        &cors_config.origins
    } else if !global_origins.is_empty() {
        global_origins
    } else {
        return;
    };

    let is_wildcard = origins.iter().any(|o| o == "*");
    if is_wildcard && cors_config.credentials {
        return;
    }

    let origin_to_use = if is_wildcard {
        "*"
    } else if let Some(req_origin) = request_origin {
        if origins.iter().any(|o| o == req_origin) {
            req_origin
        } else {
            return;
        }
    } else {
        origins.first().map(|s| s.as_str()).unwrap_or("*")
    };

    if let Ok(val) = HeaderValue::from_str(origin_to_use) {
        response
            .headers_mut()
            .insert(actix_web::http::header::ACCESS_CONTROL_ALLOW_ORIGIN, val);
    }

    if origin_to_use != "*" {
        response.headers_mut().insert(
            actix_web::http::header::VARY,
            HeaderValue::from_static("Origin"),
        );
    }

    if cors_config.credentials {
        response.headers_mut().insert(
            actix_web::http::header::ACCESS_CONTROL_ALLOW_CREDENTIALS,
            HeaderValue::from_static("true"),
        );
    }

    if !cors_config.expose_headers.is_empty() {
        let expose_str = cors_config.expose_headers.join(", ");
        if let Ok(val) = HeaderValue::from_str(&expose_str) {
            response
                .headers_mut()
                .insert(actix_web::http::header::ACCESS_CONTROL_EXPOSE_HEADERS, val);
        }
    }
}

pub async fn handle_request(
    req: HttpRequest,
    body: web::Bytes,
    state: web::Data<Arc<AppState>>,
) -> HttpResponse {
    let method = req.method().as_str().to_string();
    let path = req.path().to_string();

    let path_clone = path.clone();
    let method_clone = method.clone();

    let router = GLOBAL_ROUTER.get().expect("Router not initialized");

    // ===== PHASE 1: Route matching (NO GIL) =====
    let (_route_ref, path_params, handler_id) = {
        if let Some((route, path_params, handler_id)) = router.find(&method, &path) {
            (route, path_params, handler_id)
        } else {
            if method == "OPTIONS" {
                let available_methods = router.find_all_methods(&path);
                if !available_methods.is_empty() {
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

    // ===== PHASE 2: Extract headers, cookies (NO GIL) =====
    let mut headers: AHashMap<String, String> = AHashMap::with_capacity(16);
    const MAX_HEADERS: usize = 100;
    let max_header_size = state.max_header_size;
    let mut header_count = 0;

    for (name, value) in req.headers().iter() {
        header_count += 1;
        if header_count > MAX_HEADERS {
            return HttpResponse::BadRequest()
                .content_type("text/plain; charset=utf-8")
                .body("Too many headers");
        }

        if let Ok(v) = value.to_str() {
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

    let peer_addr = req.peer_addr().map(|addr| addr.ip().to_string());

    let middleware_meta_ref = MIDDLEWARE_METADATA
        .get()
        .and_then(|meta_map| meta_map.get(&handler_id));

    let route_metadata = ROUTE_METADATA
        .get()
        .and_then(|meta_map| meta_map.get(&handler_id).cloned());

    let skip_compression = route_metadata
        .as_ref()
        .map(|m| m.skip.contains("compression"))
        .unwrap_or(false);

    // ===== PHASE 3: Process middleware (CORS preflight, rate limiting) =====
    if let Some(meta_ref) = middleware_meta_ref {
        if let Some(early_response) = middleware::process_middleware(
            &method,
            &path,
            &headers,
            peer_addr.as_deref(),
            handler_id,
            meta_ref,
            Some(&state.cors_allowed_origins),
        )
        .await
        {
            return early_response;
        }
    }

    // ===== PHASE 4: Authentication and guards (NO GIL) =====
    let auth_ctx = if let Some(ref route_meta) = route_metadata {
        if !route_meta.auth_backends.is_empty() {
            authenticate(&headers, &route_meta.auth_backends)
        } else {
            None
        }
    } else {
        None
    };

    if let Some(ref route_meta) = route_metadata {
        if !route_meta.guards.is_empty() {
            match evaluate_guards(&route_meta.guards, auth_ctx.as_ref()) {
                GuardResult::Allow => {}
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

    let is_head_request = method == "HEAD";

    // ===== PHASE 5: Queue-based submission (SINGLE GIL acquisition, NO await on Python) =====

    // Check if Python queue is available
    let _python_queue_present = match &state.python_queue {
        Some(q) => q,
        None => {
            return HttpResponse::InternalServerError()
                .content_type("text/plain; charset=utf-8")
                .body("Python event loop worker not initialized");
        }
    };

    // Generate unique request ID
    let request_id = REQUEST_ID_COUNTER.fetch_add(1, Ordering::Relaxed);

    // Create oneshot channel for response
    let (response_tx, response_rx) = tokio::sync::oneshot::channel();

    // Store channel in global map
    if let Some(channels) = RESPONSE_CHANNELS.get() {
        channels.lock().unwrap().insert(request_id, response_tx);
    }

    // Submit request to Python queue via thread-safe Python helper (SINGLE GIL ACQUISITION, NON-BLOCKING)
    eprintln!(
        "[django-bolt] Submitting request {} via submit_from_rust for handler {}",
        request_id, handler_id
    );
    let submit_result = Python::attach(|py| -> PyResult<()> {
        // Create context dict if needed
        let context = if middleware_meta_ref.is_some() || auth_ctx.is_some() {
            let ctx_dict = PyDict::new(py);
            let ctx_py = ctx_dict.unbind();
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

        // Convert to dict for Python queue
        let request_dict = request_obj.bind(py).call_method0("to_dict")?;

        // Submit to queue using thread-safe helper to avoid cross-thread put_nowait
        let worker_module = py.import("django_bolt.event_loop_worker")?;
        let submit_fn = worker_module.getattr("submit_from_rust")?;
        submit_fn.call1(((request_id, handler_id, request_dict),))?;
        eprintln!(
            "[django-bolt] Request {} handed off to worker loop",
            request_id
        );

        Ok(())
    });

    if let Err(e) = submit_result {
        // Failed to submit - return error
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
                    "Failed to submit request to queue".to_string(),
                    vec![],
                    None,
                    state.debug,
                )
            }
        });
    }

    // ===== PHASE 6: Await response from Python worker (NO GIL - pure Rust async) =====
    match tokio::time::timeout(Duration::from_secs(30), response_rx).await {
        Ok(Ok((status_code, resp_headers, body_bytes))) => {
            // Got response from Python - build HTTP response
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
                // File response handling
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
                                        Some((Ok::<_, std::io::Error>(Bytes::from(buffer)), file))
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
                    Err(e) => {
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
                // Regular response
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

                // Add CORS headers if configured (NO GIL)
                if let Some(ref route_meta) = route_metadata {
                    if let Some(ref cors_cfg) = route_meta.cors_config {
                        let origin = req.headers().get("origin").and_then(|v| v.to_str().ok());
                        add_cors_headers_rust(
                            &mut response,
                            origin,
                            cors_cfg,
                            &state.cors_allowed_origins,
                        );
                    }
                }

                return response;
            }
        }
        Ok(Err(_)) => {
            // Channel was closed without sending
            return HttpResponse::InternalServerError()
                .content_type("text/plain; charset=utf-8")
                .body("Python worker channel closed unexpectedly");
        }
        Err(_) => {
            // Timeout waiting for response
            return HttpResponse::GatewayTimeout()
                .content_type("text/plain; charset=utf-8")
                .body("Request timeout waiting for Python worker");
        }
    }
}

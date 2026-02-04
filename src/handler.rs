use actix_multipart::Multipart;
use actix_web::http::header::{HeaderName, HeaderValue};
use actix_web::{http::StatusCode, web, HttpRequest, HttpResponse};
use ahash::AHashMap;
use bytes::Bytes;
use futures_util::stream;
use futures_util::StreamExt;
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyBytes, PyDict, PyList, PyTuple};
use std::collections::HashMap;
use std::io::ErrorKind;
use std::sync::Arc;
use tokio::fs::File;
use tokio::io::AsyncReadExt;

use crate::error;
use crate::form_parsing::{
    parse_multipart, parse_urlencoded, FileContent, FileInfo, FormParseResult, ValidationError,
    DEFAULT_MAX_PARTS, DEFAULT_MEMORY_LIMIT,
};
use crate::middleware;
use crate::middleware::auth::populate_auth_context;
use crate::request::PyRequest;
use crate::request_pipeline::validate_typed_params;
use crate::response_builder;
use crate::response_meta::ResponseMeta;
use crate::responses;
use crate::router::parse_query_string;
use crate::state::{AppState, GLOBAL_ROUTER, ROUTE_METADATA, TASK_LOCALS};
use crate::streaming::{create_python_stream, create_sse_stream};
use crate::type_coercion::{params_to_py_dict, CoercedValue};
use crate::validation::{parse_cookies_inline, validate_auth_and_guards, AuthGuardResult};

// Cache Python classes for type construction (avoids repeated imports)
static UUID_CLASS: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static DECIMAL_CLASS: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static DATETIME_CLASS: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static DATE_CLASS: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static TIME_CLASS: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static STREAMING_RESPONSE_CLASS: PyOnceLock<Py<PyAny>> = PyOnceLock::new();

fn get_streaming_response_class(py: Python<'_>) -> &Py<PyAny> {
    STREAMING_RESPONSE_CLASS.get_or_init(py, || {
        py.import("django_bolt.responses")
            .unwrap()
            .getattr("StreamingResponse")
            .unwrap()
            .unbind()
    })
}

fn get_uuid_class(py: Python<'_>) -> &Py<PyAny> {
    UUID_CLASS.get_or_init(py, || {
        py.import("uuid").unwrap().getattr("UUID").unwrap().unbind()
    })
}

fn get_decimal_class(py: Python<'_>) -> &Py<PyAny> {
    DECIMAL_CLASS.get_or_init(py, || {
        py.import("decimal")
            .unwrap()
            .getattr("Decimal")
            .unwrap()
            .unbind()
    })
}

fn get_datetime_class(py: Python<'_>) -> &Py<PyAny> {
    DATETIME_CLASS.get_or_init(py, || {
        py.import("datetime")
            .unwrap()
            .getattr("datetime")
            .unwrap()
            .unbind()
    })
}

fn get_date_class(py: Python<'_>) -> &Py<PyAny> {
    DATE_CLASS.get_or_init(py, || {
        py.import("datetime")
            .unwrap()
            .getattr("date")
            .unwrap()
            .unbind()
    })
}

fn get_time_class(py: Python<'_>) -> &Py<PyAny> {
    TIME_CLASS.get_or_init(py, || {
        py.import("datetime")
            .unwrap()
            .getattr("time")
            .unwrap()
            .unbind()
    })
}

// Reuse the global Python asyncio event loop created at server startup (TASK_LOCALS)

/// Build an HTTP response for a file path.
/// Handles both small files (loaded into memory) and large files (streamed).
/// Note: Not inlined as it's async and relatively large
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
/// OPTIMIZATION: #[inline(never)] on error path - keeps hot path code smaller
#[inline(never)]
pub fn handle_python_error(
    py: Python<'_>,
    err: PyErr,
    path: &str,
    method: &str,
    debug: bool,
) -> HttpResponse {
    err.restore(py);
    if let Some(exc) = PyErr::take(py) {
        let exc_value = exc.value(py);
        error::handle_python_exception(py, exc_value, path, method, debug)
    } else {
        error::build_error_response(
            py,
            500,
            "Handler execution error".to_string(),
            vec![],
            None,
            debug,
        )
    }
}

/// Extract headers from request with validation
/// OPTIMIZATION: HeaderName::as_str() already returns lowercase (http crate canonical form)
/// so we skip the redundant to_ascii_lowercase() call (~50ns saved per header)
/// OPTIMIZATION: #[inline] on hot path - called on every request
#[inline]
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

/// Build HTTP 422 response for validation errors
pub fn build_validation_error_response(error: &ValidationError) -> HttpResponse {
    let body = serde_json::json!({
        "detail": [error.to_json()]
    });
    HttpResponse::UnprocessableEntity()
        .content_type("application/json")
        .body(body.to_string())
}

/// Convert CoercedValue to Python object
///
/// Constructs actual Python typed objects (uuid.UUID, decimal.Decimal, datetime, etc.)
/// instead of strings, eliminating double-parsing on the Python side.
pub fn coerced_value_to_py(py: Python<'_>, value: &CoercedValue) -> Py<PyAny> {
    match value {
        // Primitives - direct conversion
        CoercedValue::Int(v) => v.into_pyobject(py).unwrap().into_any().unbind(),
        CoercedValue::Float(v) => v.into_pyobject(py).unwrap().into_any().unbind(),
        CoercedValue::Bool(v) => v.into_pyobject(py).unwrap().to_owned().unbind().into_any(),
        CoercedValue::String(v) => v.into_pyobject(py).unwrap().into_any().unbind(),

        // UUID: construct Python uuid.UUID object
        CoercedValue::Uuid(v) => get_uuid_class(py).call1(py, (v.to_string(),)).unwrap(),

        // Decimal: construct Python decimal.Decimal object
        CoercedValue::Decimal(v) => get_decimal_class(py).call1(py, (v.to_string(),)).unwrap(),

        // DateTime (with timezone): construct Python datetime.datetime
        CoercedValue::DateTime(v) => {
            let iso_str = v.to_rfc3339().replace('Z', "+00:00");
            get_datetime_class(py)
                .call_method1(py, "fromisoformat", (iso_str,))
                .unwrap()
        }

        // NaiveDateTime: construct Python datetime.datetime (no timezone)
        CoercedValue::NaiveDateTime(v) => get_datetime_class(py)
            .call_method1(py, "fromisoformat", (v.to_string(),))
            .unwrap(),

        // Date: construct Python datetime.date
        CoercedValue::Date(v) => get_date_class(py)
            .call_method1(py, "fromisoformat", (v.to_string(),))
            .unwrap(),

        // Time: construct Python datetime.time
        CoercedValue::Time(v) => get_time_class(py)
            .call_method1(py, "fromisoformat", (v.to_string(),))
            .unwrap(),

        CoercedValue::Null => py.None(),
    }
}

/// Convert FileInfo to Python dict
pub fn file_info_to_py(py: Python<'_>, file: &FileInfo) -> PyResult<Py<PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("filename", &file.filename)?;
    dict.set_item("content_type", &file.content_type)?;
    dict.set_item("size", file.size)?;

    match &file.content {
        FileContent::Memory(bytes) => {
            dict.set_item("content", PyBytes::new(py, bytes))?;
            dict.set_item("temp_path", py.None())?;
        }
        FileContent::Disk(temp_file) => {
            // For disk-spooled files, pass the temp path instead of content
            dict.set_item("content", py.None())?;
            dict.set_item("temp_path", temp_file.path().to_string_lossy().to_string())?;
        }
    }

    Ok(dict.unbind())
}

/// Convert FormParseResult to Python dicts
pub fn form_result_to_py(
    py: Python<'_>,
    result: &FormParseResult,
) -> PyResult<(Py<PyDict>, Py<PyDict>)> {
    // Convert form_map
    let form_dict = PyDict::new(py);
    for (key, value) in &result.form_map {
        form_dict.set_item(key, coerced_value_to_py(py, value))?;
    }

    // Convert files_map - each field can have multiple files
    let files_dict = PyDict::new(py);
    for (field_name, files) in &result.files_map {
        if files.len() == 1 {
            // Single file - store directly
            let file_dict = file_info_to_py(py, &files[0])?;
            files_dict.set_item(field_name, file_dict)?;
        } else {
            // Multiple files - store as list
            let file_list = PyList::empty(py);
            for file in files {
                let file_dict = file_info_to_py(py, file)?;
                file_list.append(file_dict)?;
            }
            files_dict.set_item(field_name, file_list)?;
        }
    }

    Ok((form_dict.unbind(), files_dict.unbind()))
}

pub async fn handle_request(
    req: HttpRequest,
    mut payload: web::Payload,
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
            let raw_params = route_match.path_params(); // No allocation for static routes

            // URL-decode path parameters for consistency with query string parsing
            // This ensures /items/hello%20world correctly yields id="hello world"
            let path_params: AHashMap<String, String> = if raw_params.is_empty() {
                raw_params
            } else {
                raw_params
                    .into_iter()
                    .map(|(k, v)| {
                        let decoded = urlencoding::decode(&v)
                            .unwrap_or_else(|_| std::borrow::Cow::Borrowed(&v))
                            .into_owned();
                        (k, decoded)
                    })
                    .collect()
            };
            (path_params, handler_id)
        } else {
            // No route found - check for trailing slash redirect FIRST
            // This only runs when route doesn't match (minimal overhead)
            // Starlette-style: redirect to canonical URL if alternate path exists
            if path != "/" {
                let alternate_path = if path.ends_with('/') {
                    path.trim_end_matches('/').to_string()
                } else {
                    format!("{}/", path)
                };

                // Try alternate path - if it matches, send 308 redirect
                if router.find(method, &alternate_path).is_some() {
                    let query = req.query_string();
                    let location = if query.is_empty() {
                        alternate_path
                    } else {
                        format!("{}?{}", alternate_path, query)
                    };
                    return HttpResponse::PermanentRedirect() // 308
                        .insert_header(("Location", location))
                        .finish();
                }
            }

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

    // Type validation for path and query parameters (Rust-native, no GIL)
    // This validates parameter types before GIL acquisition, returning 422 for invalid types
    // Performance: Eliminates Python's convert_primitive() overhead for invalid requests
    if let Some(ref route_meta) = route_metadata {
        if let Some(response) =
            validate_typed_params(&path_params, &query_params, &route_meta.param_types)
        {
            return response;
        }
    }

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

    // Determine if form parsing is needed and get content type
    let needs_form_parsing = route_metadata
        .as_ref()
        .map(|m| m.needs_form_parsing)
        .unwrap_or(false);

    let content_type = headers
        .get("content-type")
        .map(|s| s.as_str())
        .unwrap_or("");

    let is_multipart = content_type.starts_with("multipart/form-data");
    let is_urlencoded = content_type.starts_with("application/x-www-form-urlencoded");

    // Read body from payload (before form parsing consumes it for multipart)
    // For multipart, we need the payload stream directly
    let (body, form_result): (Vec<u8>, Option<FormParseResult>) =
        if needs_form_parsing && is_multipart {
            // Multipart form parsing - uses the payload stream directly
            let form_type_hints = route_metadata
                .as_ref()
                .map(|m| &m.form_type_hints)
                .cloned()
                .unwrap_or_default();
            let file_constraints = route_metadata
                .as_ref()
                .map(|m| &m.file_constraints)
                .cloned()
                .unwrap_or_default();
            let max_upload_size = route_metadata
                .as_ref()
                .map(|m| m.max_upload_size)
                .unwrap_or(1024 * 1024);
            let memory_spool_threshold = route_metadata
                .as_ref()
                .map(|m| m.memory_spool_threshold)
                .unwrap_or(DEFAULT_MEMORY_LIMIT);

            // Create Multipart from the payload
            let multipart = Multipart::new(req.headers(), payload);

            match parse_multipart(
                multipart,
                &form_type_hints,
                &file_constraints,
                max_upload_size,
                memory_spool_threshold,
                DEFAULT_MAX_PARTS,
            )
            .await
            {
                Ok(result) => (Vec::new(), Some(result)),
                Err(validation_error) => {
                    return build_validation_error_response(&validation_error);
                }
            }
        } else {
            // Read payload as bytes (for non-multipart requests)
            let mut body_bytes = web::BytesMut::new();
            while let Some(chunk) = payload.next().await {
                match chunk {
                    Ok(data) => body_bytes.extend_from_slice(&data),
                    Err(e) => {
                        return HttpResponse::BadRequest()
                            .content_type("application/json")
                            .body(format!(
                                "{{\"error\": \"Failed to read request body: {}\"}}",
                                e
                            ));
                    }
                }
            }
            let body = body_bytes.freeze();

            // URL-encoded form parsing
            if needs_form_parsing && is_urlencoded {
                let form_type_hints = route_metadata
                    .as_ref()
                    .map(|m| &m.form_type_hints)
                    .cloned()
                    .unwrap_or_default();

                match parse_urlencoded(&body, &form_type_hints) {
                    Ok(form_map) => {
                        let result = FormParseResult {
                            form_map,
                            files_map: HashMap::new(),
                        };
                        (body.to_vec(), Some(result))
                    }
                    Err(validation_error) => {
                        return build_validation_error_response(&validation_error);
                    }
                }
            } else {
                (body.to_vec(), None)
            }
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

        // Get type hints for type coercion
        let param_types = route_metadata
            .as_ref()
            .map(|m| &m.param_types)
            .cloned()
            .unwrap_or_default();

        // Create typed dicts - convert values to Python types
        let path_params_dict = params_to_py_dict(py, &path_params, &param_types)?;
        let query_params_dict = params_to_py_dict(py, &query_params, &param_types)?;
        let headers_dict = params_to_py_dict(py, &headers_for_python, &param_types)?;
        let cookies_dict = params_to_py_dict(py, &cookies, &param_types)?;

        // Create form_map and files_map from form parsing result
        let (form_map_dict, files_map_dict) = if let Some(ref result) = form_result {
            form_result_to_py(py, result)?
        } else {
            (PyDict::new(py).unbind(), PyDict::new(py).unbind())
        };

        let request = PyRequest {
            method: method_owned.clone(),
            path: path_owned.clone(),
            body: body.clone(),
            path_params: path_params_dict.unbind(),
            query_params: query_params_dict.unbind(),
            headers: headers_dict.unbind(),
            cookies: cookies_dict.unbind(),
            context,
            user: None,
            state: PyDict::new(py).unbind(), // Empty state dict for middleware and dynamic attributes
            form_map: form_map_dict,
            files_map: files_map_dict,
            meta_cache: std::sync::OnceLock::new(), // Lazy META - zero hot-path cost
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
            // Try new ResponseMeta format first: (status, meta_tuple, body)
            // Performance: All header building happens in Rust using static strings
            let parsed_meta =
                Python::attach(|py| response_builder::try_extract_response_meta(py, &result_obj));

            // Handle new ResponseMeta format
            if let Some(parsed) = parsed_meta {
                let status = StatusCode::from_u16(parsed.status_code).unwrap_or(StatusCode::OK);

                // Check for file serving: x-bolt-file-path in custom headers
                if let Some(fpath) = response_builder::extract_file_path_from_meta(&parsed.meta) {
                    let headers = response_builder::meta_to_headers_without_file_path(&parsed.meta);
                    return build_file_response(
                        &fpath,
                        status,
                        headers,
                        skip_compression,
                        is_head_request,
                    )
                    .await;
                }

                let response_body = if is_head_request {
                    Vec::new()
                } else {
                    parsed.body
                };

                let mut response = response_builder::build_response_from_meta(
                    status,
                    parsed.meta,
                    response_body,
                    skip_compression,
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

            // Fallback to old format: (status, headers_list, body)
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
                    return build_file_response(
                        &fpath,
                        status,
                        headers,
                        skip_compression,
                        is_head_request,
                    )
                    .await;
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
                        return build_file_response(
                            &fpath,
                            status,
                            headers,
                            skip_compression,
                            is_head_request,
                        )
                        .await;
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
                // Check for tuple with StreamingResponse body (middleware path)
                // This handles the case where serialize_response returns (status, headers/meta, StreamingResponse)
                // allowing streaming responses to work with middleware (CORS, rate limiting, etc.)
                let streaming_tuple = Python::attach(|py| {
                    let obj = result_obj.bind(py);
                    let tuple = obj.cast::<PyTuple>().ok()?;
                    if tuple.len() != 3 {
                        return None;
                    }
                    // Extract body (element 2) and check if it's a StreamingResponse
                    let body_obj = tuple.get_item(2).ok()?;
                    let streaming_cls = get_streaming_response_class(py);
                    if !body_obj
                        .is_instance(streaming_cls.bind(py))
                        .unwrap_or(false)
                    {
                        return None;
                    }

                    // Extract headers: try new ResponseMeta format first, then legacy format
                    let meta_or_headers = tuple.get_item(1).ok()?;
                    let tuple_headers: Vec<(String, String)> =
                        if meta_or_headers.is_instance_of::<PyTuple>() {
                            // New ResponseMeta format: build headers from meta
                            let meta = ResponseMeta::from_python(&meta_or_headers).ok()?;
                            response_builder::meta_to_headers(&meta)
                        } else {
                            // Legacy format: list of header tuples
                            meta_or_headers.extract::<Vec<(String, String)>>().ok()?
                        };

                    let media_type: String = body_obj
                        .getattr(pyo3::intern!(py, "media_type"))
                        .and_then(|v| v.extract())
                        .unwrap_or_else(|_| "application/octet-stream".to_string());
                    let content_obj: Py<PyAny> = body_obj
                        .getattr(pyo3::intern!(py, "content"))
                        .ok()?
                        .unbind();
                    let is_async_generator: bool = body_obj
                        .getattr(pyo3::intern!(py, "is_async_generator"))
                        .and_then(|v| v.extract())
                        .unwrap_or(false);
                    // Use headers from the tuple (processed by middleware) rather than StreamingResponse.headers
                    Some((tuple_headers, media_type, content_obj, is_async_generator))
                });
                if let Some((headers, media_type, content_obj, is_async_generator)) =
                    streaming_tuple
                {
                    // Extract status from tuple element 0
                    // Headers already include content-type from serialize_response
                    let status = Python::attach(|py| {
                        let obj = result_obj.bind(py);
                        if let Ok(tuple) = obj.cast::<PyTuple>() {
                            tuple
                                .get_item(0)
                                .ok()
                                .and_then(|v| v.extract::<u16>().ok())
                                .map(|s| StatusCode::from_u16(s).unwrap_or(StatusCode::OK))
                                .unwrap_or(StatusCode::OK)
                        } else {
                            StatusCode::OK
                        }
                    });

                    if media_type == "text/event-stream" {
                        if is_head_request {
                            let mut builder = response_builder::build_sse_response(
                                status,
                                headers,
                                skip_compression,
                            );
                            let mut response = builder.body(Vec::<u8>::new());
                            if skip_cors {
                                response.headers_mut().insert(
                                    "x-bolt-skip-cors".parse().unwrap(),
                                    "true".parse().unwrap(),
                                );
                            }
                            return response;
                        }
                        let stream = create_sse_stream(content_obj, is_async_generator);
                        let mut response =
                            response_builder::build_sse_response(status, headers, skip_compression)
                                .streaming(stream);
                        if skip_cors {
                            response.headers_mut().insert(
                                "x-bolt-skip-cors".parse().unwrap(),
                                "true".parse().unwrap(),
                            );
                        }
                        return response;
                    } else {
                        // Non-SSE streaming responses
                        let mut builder = HttpResponse::build(status);
                        for (k, v) in headers {
                            builder.append_header((k, v));
                        }
                        if is_head_request {
                            if skip_compression {
                                builder.append_header(("Content-Encoding", "identity"));
                            }
                            if skip_cors {
                                builder.append_header(("x-bolt-skip-cors", "true"));
                            }
                            return builder.body(Vec::<u8>::new());
                        }
                        if skip_compression {
                            builder.append_header(("Content-Encoding", "identity"));
                        }
                        if skip_cors {
                            builder.append_header(("x-bolt-skip-cors", "true"));
                        }
                        let stream = create_python_stream(content_obj, is_async_generator);
                        return builder.streaming(stream);
                    }
                }
                let streaming = Python::attach(|py| {
                    let obj = result_obj.bind(py);
                    // Use cached StreamingResponse class to avoid repeated imports
                    let streaming_cls = get_streaming_response_class(py);
                    let is_streaming = obj.is_instance(streaming_cls.bind(py)).unwrap_or(false);
                    // OPTIMIZATION: Use interned strings for attribute checks
                    if !is_streaming && !obj.hasattr(pyo3::intern!(py, "content")).unwrap_or(false)
                    {
                        return None;
                    }
                    let status_code: u16 = obj
                        .getattr(pyo3::intern!(py, "status_code"))
                        .and_then(|v| v.extract())
                        .unwrap_or(200);
                    let mut headers: Vec<(String, String)> = Vec::new();
                    if let Ok(hobj) = obj.getattr(pyo3::intern!(py, "headers")) {
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
                        .getattr(pyo3::intern!(py, "media_type"))
                        .and_then(|v| v.extract())
                        .unwrap_or_else(|_| "application/octet-stream".to_string());
                    let has_ct = headers
                        .iter()
                        .any(|(k, _)| k.eq_ignore_ascii_case("content-type"));
                    if !has_ct {
                        headers.push(("content-type".to_string(), media_type.clone()));
                    }
                    let content_obj: Py<PyAny> = match obj.getattr(pyo3::intern!(py, "content")) {
                        Ok(c) => c.unbind(),
                        Err(_) => return None,
                    };
                    // Extract pre-computed is_async_generator metadata (detected at StreamingResponse instantiation)
                    let is_async_generator: bool = obj
                        .getattr(pyo3::intern!(py, "is_async_generator"))
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
                                response.headers_mut().insert(
                                    "x-bolt-skip-cors".parse().unwrap(),
                                    "true".parse().unwrap(),
                                );
                            }

                            // CORS headers will be added by CorsMiddleware
                            return response;
                        }

                        // Use optimized SSE response builder (batches all SSE headers)
                        let final_content_obj = content_obj;
                        let mut builder =
                            response_builder::build_sse_response(status, headers, skip_compression);
                        let stream = create_sse_stream(final_content_obj, is_async_generator);
                        let mut response = builder.streaming(stream);

                        // Set skip-cors marker if @skip_middleware("cors") is used
                        if skip_cors {
                            response.headers_mut().insert(
                                "x-bolt-skip-cors".parse().unwrap(),
                                "true".parse().unwrap(),
                            );
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

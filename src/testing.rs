/// Testing utilities for django-bolt
/// Provides synchronous request handler for in-memory testing without subprocess/network
///
/// Key design: Reuses production middleware code (rate limiting, CORS, auth, guards)
/// to ensure tests validate the actual request pipeline. HttpResponse is converted
/// to simple tuples at the end for easy test assertions.
use actix_web::HttpResponse;
use ahash::AHashMap;
use pyo3::prelude::*;
use pyo3::types::PyDict;

use crate::middleware;
use crate::middleware::auth::populate_auth_context;
use crate::request::PyRequest;
use crate::router::parse_query_string;
use crate::state::{GLOBAL_ROUTER, ROUTE_METADATA, TASK_LOCALS};
use crate::validation::{parse_cookies_inline, validate_auth_and_guards, AuthGuardResult};

/// Convert HttpResponse to test tuple format (status, headers, body)
/// This allows tests to use simple tuple assertions while validating real middleware
fn http_response_to_tuple(response: HttpResponse) -> (u16, Vec<(String, String)>, Vec<u8>) {
    let status = response.status().as_u16();

    let headers: Vec<(String, String)> = response
        .headers()
        .iter()
        .map(|(name, value)| {
            (
                name.as_str().to_string(),
                value.to_str().unwrap_or("").to_string(),
            )
        })
        .collect();

    let body = response.into_body();
    // Extract body bytes from actix_web::body::BoxBody
    // For testing, we assume the body is already materialized
    use actix_web::body::MessageBody;
    let body_bytes = match body.try_into_bytes() {
        Ok(bytes) => bytes.to_vec(),
        Err(_) => Vec::new(), // Streaming bodies return empty for now
    };

    (status, headers, body_bytes)
}

/// Handle a test request synchronously
/// Returns (status_code, headers, body_bytes)
///
/// This function replicates the core logic from handle_request but:
/// 1. Takes raw request parameters instead of Actix types
/// 2. Runs synchronously for test execution
/// 3. Returns simple tuple instead of HttpResponse
/// 4. Supports both async and sync dispatch
#[pyfunction]
#[allow(clippy::too_many_arguments)]
pub fn handle_test_request(
    py: Python<'_>,
    method: String,
    path: String,
    headers: Vec<(String, String)>,
    body: Vec<u8>,
    query_string: Option<String>,
    dispatch: Py<PyAny>,
    dispatch_sync: Py<PyAny>,
    _debug: Option<bool>,
) -> PyResult<(u16, Vec<(String, String)>, Vec<u8>)> {
    let router = GLOBAL_ROUTER
        .get()
        .ok_or_else(|| pyo3::exceptions::PyRuntimeError::new_err("Router not initialized"))?;

    // Route matching
    let (route, path_params, handler_id) = {
        if let Some((route, params, id)) = router.find(&method, &path) {
            (route.handler.clone_ref(py), params, id)
        } else {
            return Ok((
                404,
                vec![(
                    "content-type".to_string(),
                    "text/plain; charset=utf-8".to_string(),
                )],
                b"Not Found".to_vec(),
            ));
        }
    };

    // Parse query string
    let query_params = if let Some(q) = query_string {
        parse_query_string(&q)
    } else {
        AHashMap::new()
    };

    // Convert headers to map (lowercase keys)
    let mut header_map: AHashMap<String, String> = AHashMap::with_capacity(headers.len());
    for (name, value) in headers.iter() {
        header_map.insert(name.to_ascii_lowercase(), value.clone());
    }

    // Get metadata
    let route_metadata = ROUTE_METADATA
        .get()
        .and_then(|meta_map| meta_map.get(&handler_id).cloned());

    // Process rate limiting (same as production)
    // Note: peer_addr is None in tests, rate limiting uses headers only
    if let Some(ref route_meta) = route_metadata {
        if let Some(ref rate_config) = route_meta.rate_limit_config {
            if let Some(response) = middleware::rate_limit::check_rate_limit(
                handler_id,
                &header_map,
                None, // peer_addr not available in sync testing
                rate_config,
            ) {
                return Ok(http_response_to_tuple(response));
            }
        }
    }

    // Execute authentication and guards using shared validation logic (same as production)
    let auth_ctx = if let Some(ref route_meta) = route_metadata {
        match validate_auth_and_guards(&header_map, &route_meta.auth_backends, &route_meta.guards) {
            AuthGuardResult::Allow(ctx) => ctx,
            AuthGuardResult::Unauthorized => {
                return Ok((
                    401,
                    vec![("content-type".to_string(), "application/json".to_string())],
                    br#"{"detail":"Authentication required"}"#.to_vec(),
                ));
            }
            AuthGuardResult::Forbidden => {
                return Ok((
                    403,
                    vec![("content-type".to_string(), "application/json".to_string())],
                    br#"{"detail":"Permission denied"}"#.to_vec(),
                ));
            }
        }
    } else {
        None
    };

    // Parse cookies using shared inline function (same as production)
    let cookies = parse_cookies_inline(header_map.get("cookie").map(|s| s.as_str()));

    // Create context dict only if auth context is present
    let context = if let Some(ref auth) = auth_ctx {
        let ctx_dict = PyDict::new(py);
        let ctx_py = ctx_dict.unbind();
        populate_auth_context(&ctx_py, auth, py);
        Some(ctx_py)
    } else {
        None
    };

    // Create PyRequest
    let request = PyRequest {
        method: method.clone(),
        path: path.clone(),
        body,
        path_params,
        query_params,
        headers: header_map,
        cookies,
        context,
        user: None,
    };
    let request_obj = Py::new(py, request)?;

    // Check if handler is async or sync from metadata
    let is_async_handler = route_metadata
        .as_ref()
        .and_then(|meta| Some(meta.is_async.unwrap_or(true)))
        .unwrap_or(true); // Default to async for backward compatibility

    // Route to sync or async dispatch based on handler type
    let result_obj = if !is_async_handler {
        // Sync handler path: call dispatch_sync directly (no coroutine, no await)
        dispatch_sync.call1(py, (route, request_obj, handler_id))?
    } else {
        // Async handler path: call dispatch and await coroutine
        // Create or get event loop locals
        let locals_owned;
        let locals = if let Some(globals) = TASK_LOCALS.get() {
            globals
        } else {
            locals_owned = pyo3_async_runtimes::tokio::get_current_locals(py)?;
            &locals_owned
        };

        // Call dispatch to get coroutine
        let coroutine = dispatch.call1(py, (route, request_obj, handler_id))?;

        // Convert to future and await it
        let fut = pyo3_async_runtimes::into_future_with_locals(&locals, coroutine.into_bound(py))?;

        // For test context, ensure we have a tokio runtime
        // Check if runtime exists, if not initialize one
        match tokio::runtime::Handle::try_current() {
            Ok(handle) => {
                // Runtime exists, use it
                handle.block_on(fut).map_err(|e| {
                    pyo3::exceptions::PyRuntimeError::new_err(format!(
                        "Handler execution failed: {}",
                        e
                    ))
                })?
            }
            Err(_) => {
                // No runtime, create a new one for testing
                pyo3_async_runtimes::tokio::init(tokio::runtime::Builder::new_current_thread());
                pyo3_async_runtimes::tokio::get_runtime()
                    .block_on(fut)
                    .map_err(|e| {
                        pyo3::exceptions::PyRuntimeError::new_err(format!(
                            "Handler execution failed: {}",
                            e
                        ))
                    })?
            }
        }
    };

    // Extract response
    let tuple_result: Result<(u16, Vec<(String, String)>, Vec<u8>), _> = result_obj.extract(py);

    if let Ok((status_code, resp_headers, body_bytes)) = tuple_result {
        // Filter out special headers
        let headers: Vec<(String, String)> = resp_headers
            .into_iter()
            .filter(|(k, _)| !k.eq_ignore_ascii_case("x-bolt-file-path"))
            .collect();

        Ok((status_code, headers, body_bytes))
    } else {
        // Check if it's a StreamingResponse
        let is_streaming = (|| -> PyResult<bool> {
            let obj = result_obj.bind(py);
            let m = py.import("django_bolt.responses")?;
            let cls = m.getattr("StreamingResponse")?;
            obj.is_instance(&cls)
        })()
        .unwrap_or(false);

        if is_streaming {
            // For streaming responses in tests, we collect all chunks
            let obj = result_obj.bind(py);
            let status_code: u16 = obj
                .getattr("status_code")
                .and_then(|v| v.extract())
                .unwrap_or(200);

            let mut resp_headers: Vec<(String, String)> = Vec::new();
            if let Ok(hobj) = obj.getattr("headers") {
                if let Ok(hdict) = hobj.downcast::<PyDict>() {
                    for (k, v) in hdict {
                        if let (Ok(ks), Ok(vs)) = (k.extract::<String>(), v.extract::<String>()) {
                            resp_headers.push((ks, vs));
                        }
                    }
                }
            }

            // Try to collect streaming content
            let content_obj = obj.getattr("content")?;
            let mut collected_body = Vec::new();

            // Check if it's an async iterator
            let has_aiter = content_obj.hasattr("__aiter__").unwrap_or(false);

            if has_aiter {
                // For async iterators, we need to consume them
                // This is a simplified version - in real tests, streaming might be tested differently
                collected_body =
                    b"[streaming content - use AsyncTestClient for full streaming test]".to_vec();
            } else {
                // Try to iterate synchronously
                if let Ok(iter) = content_obj.try_iter() {
                    for item in iter {
                        if let Ok(chunk) = item {
                            // Try to extract as bytes
                            if let Ok(bytes_vec) = chunk.extract::<Vec<u8>>() {
                                collected_body.extend_from_slice(&bytes_vec);
                            } else if let Ok(s) = chunk.extract::<String>() {
                                collected_body.extend_from_slice(s.as_bytes());
                            }
                        }
                    }
                }
            }

            Ok((status_code, resp_headers, collected_body))
        } else {
            Err(pyo3::exceptions::PyTypeError::new_err(
                "Handler returned unsupported response type (expected tuple or StreamingResponse)",
            ))
        }
    }
}

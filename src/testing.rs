/// Testing utilities for django-bolt
/// Provides synchronous request handler for in-memory testing without subprocess/network
use ahash::AHashMap;
use pyo3::prelude::*;
use pyo3::types::PyDict;

use crate::middleware::auth::{authenticate, populate_auth_context};
use crate::permissions::{evaluate_guards, GuardResult};
use crate::request::PyRequest;
use crate::router::parse_query_string;
use crate::state::{GLOBAL_ROUTER, MIDDLEWARE_METADATA, ROUTE_METADATA, TASK_LOCALS};

/// Handle a test request synchronously
/// Returns (status_code, headers, body_bytes)
///
/// This function replicates the core logic from handle_request but:
/// 1. Takes raw request parameters instead of Actix types
/// 2. Runs synchronously for test execution
/// 3. Returns simple tuple instead of HttpResponse
#[pyfunction]
pub fn handle_test_request(
    py: Python<'_>,
    method: String,
    path: String,
    headers: Vec<(String, String)>,
    body: Vec<u8>,
    query_string: Option<String>,
    dispatch: Py<PyAny>,
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
    let middleware_meta = MIDDLEWARE_METADATA
        .get()
        .and_then(|meta_map| meta_map.get(&handler_id).map(|m| m.clone_ref(py)));

    let route_metadata = ROUTE_METADATA
        .get()
        .and_then(|meta_map| meta_map.get(&handler_id).cloned());

    // Note: Middleware processing (CORS, rate limiting) is async
    // For testing, we skip async middleware checks and go directly to handler
    // The test client can still test middleware by checking the response

    // Authentication (synchronous part)
    let auth_ctx = if let Some(ref route_meta) = route_metadata {
        if !route_meta.auth_backends.is_empty() {
            authenticate(&header_map, &route_meta.auth_backends)
        } else {
            None
        }
    } else {
        None
    };

    // Guards evaluation
    if let Some(ref route_meta) = route_metadata {
        if !route_meta.guards.is_empty() {
            match evaluate_guards(&route_meta.guards, auth_ctx.as_ref()) {
                GuardResult::Allow => {
                    // Continue
                }
                GuardResult::Unauthorized => {
                    return Ok((
                        401,
                        vec![("content-type".to_string(), "application/json".to_string())],
                        br#"{"detail":"Authentication required"}"#.to_vec(),
                    ));
                }
                GuardResult::Forbidden => {
                    return Ok((
                        403,
                        vec![("content-type".to_string(), "application/json".to_string())],
                        br#"{"detail":"Permission denied"}"#.to_vec(),
                    ));
                }
            }
        }
    }

    // Parse cookies
    let mut cookies: AHashMap<String, String> = AHashMap::with_capacity(8);
    if let Some(raw_cookie) = header_map.get("cookie") {
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

    // Create context dict
    let context = if middleware_meta.is_some() || auth_ctx.is_some() {
        let ctx_dict = PyDict::new(py);
        let ctx_py = ctx_dict.unbind();
        if let Some(ref auth) = auth_ctx {
            populate_auth_context(&ctx_py, auth, py);
        }
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
    };
    let request_obj = Py::new(py, request)?;

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
    let result_obj = match tokio::runtime::Handle::try_current() {
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

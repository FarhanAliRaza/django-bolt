use ahash::AHashMap;
use dashmap::DashMap;
use once_cell::sync::OnceCell;
use parking_lot::RwLock;
use pyo3::ffi::c_str;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

use crate::metadata::RouteMetadata;
use crate::middleware::auth::{authenticate, populate_auth_context};
use crate::permissions::{evaluate_guards, GuardResult};
use crate::request::PyRequest;
use crate::router::{parse_query_string, Router};

// Actix testing imports
use actix_web::dev::Service;
use actix_web::{test, web, App};
use bytes::Bytes;

// Macro for conditional debug output - only enabled with DJANGO_BOLT_TEST_DEBUG env var
macro_rules! test_debug {
    ($($arg:tt)*) => {
        if std::env::var("DJANGO_BOLT_TEST_DEBUG").is_ok() {
            eprintln!($($arg)*);
        }
    };
}

/// Test-only application state stored per instance (identified by app_id)
pub struct TestApp {
    pub router: Router,
    pub middleware_metadata: AHashMap<usize, Py<PyAny>>, // raw Python metadata for compatibility
    pub route_metadata: AHashMap<usize, RouteMetadata>,  // parsed Rust metadata
    pub dispatch: Py<PyAny>,
    pub event_loop: Option<Py<PyAny>>, // store loop; create TaskLocals per call
    pub cors_allowed_origins: Vec<String>, // global CORS origins for testing
}

static TEST_REGISTRY: OnceCell<DashMap<u64, Arc<RwLock<TestApp>>>> = OnceCell::new();
static TEST_ID_GEN: AtomicU64 = AtomicU64::new(1);

fn registry() -> &'static DashMap<u64, Arc<RwLock<TestApp>>> {
    TEST_REGISTRY.get_or_init(|| DashMap::new())
}

#[pyfunction]
pub fn create_test_app(
    py: Python<'_>,
    dispatch: Py<PyAny>,
    _debug: bool,
    cors_allowed_origins: Option<Vec<String>>,
) -> PyResult<u64> {
    let app = TestApp {
        router: Router::new(),
        middleware_metadata: AHashMap::new(),
        route_metadata: AHashMap::new(),
        dispatch: dispatch.clone_ref(py),
        event_loop: None,
        cors_allowed_origins: cors_allowed_origins.unwrap_or_default(),
    };
    let id = TEST_ID_GEN.fetch_add(1, Ordering::Relaxed);
    registry().insert(id, Arc::new(RwLock::new(app)));
    Ok(id)
}

#[pyfunction]
pub fn destroy_test_app(app_id: u64) -> PyResult<()> {
    registry().remove(&app_id);
    Ok(())
}

#[pyfunction]
pub fn register_test_routes(
    _py: Python<'_>,
    app_id: u64,
    routes: Vec<(String, String, usize, Py<PyAny>)>,
) -> PyResult<()> {
    let Some(entry) = registry().get(&app_id) else {
        return Err(pyo3::exceptions::PyKeyError::new_err("Invalid test app id"));
    };
    let mut app = entry.write();
    for (method, path, handler_id, handler) in routes {
        app.router.register(&method, &path, handler_id, handler)?;
    }
    Ok(())
}

#[pyfunction]
pub fn register_test_middleware_metadata(
    py: Python<'_>,
    app_id: u64,
    metadata: Vec<(usize, Py<PyAny>)>,
) -> PyResult<()> {
    let Some(entry) = registry().get(&app_id) else {
        return Err(pyo3::exceptions::PyKeyError::new_err("Invalid test app id"));
    };
    let mut app = entry.write();

    for (handler_id, meta) in metadata {
        app.middleware_metadata
            .insert(handler_id, meta.clone_ref(py));

        if let Ok(py_dict) = meta.bind(py).downcast::<PyDict>() {
            match RouteMetadata::from_python(py_dict, py) {
                Ok(parsed) => {
                    app.route_metadata.insert(handler_id, parsed);
                }
                Err(e) => {
                    test_debug!(
                        "Warning: Failed to parse metadata for handler {}: {}",
                        handler_id,
                        e
                    );
                }
            }
        }
    }
    Ok(())
}

#[pyfunction]
pub fn set_test_task_locals(py: Python<'_>, app_id: u64, event_loop: Py<PyAny>) -> PyResult<()> {
    let Some(entry) = registry().get(&app_id) else {
        return Err(pyo3::exceptions::PyKeyError::new_err("Invalid test app id"));
    };
    let mut app = entry.write();
    app.event_loop = Some(event_loop.clone_ref(py));
    Ok(())
}

#[pyfunction]
pub fn ensure_test_runtime(py: Python<'_>, app_id: u64) -> PyResult<()> {
    let Some(entry) = registry().get(&app_id) else {
        return Err(pyo3::exceptions::PyKeyError::new_err("Invalid test app id"));
    };
    let mut app = entry.write();

    // Create event loop if not present
    if app.event_loop.is_none() {
        let asyncio = py.import("asyncio")?;
        let ev = asyncio.call_method0("new_event_loop")?;
        app.event_loop = Some(ev.unbind().into());
    }
    Ok(())
}

#[pyfunction]
pub fn handle_test_request_for(
    py: Python<'_>,
    app_id: u64,
    method: String,
    path: String,
    headers: Vec<(String, String)>,
    body: Vec<u8>,
    query_string: Option<String>,
) -> PyResult<(u16, Vec<(String, String)>, Vec<u8>)> {
    let entry = registry()
        .get(&app_id)
        .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("Invalid test app id"))?;

    // Snapshot needed fields under a read lock and perform route match
    test_debug!(
        "[test_state] start app_id={} method={} path={} headers={} body_len={} query={:?}",
        app_id,
        method,
        path,
        headers.len(),
        body.len(),
        query_string
    );
    let dispatch: Py<PyAny>;
    let (route, path_params, handler_id): (Py<PyAny>, AHashMap<String, String>, usize);
    let route_meta_opt: Option<RouteMetadata>;
    let middleware_present: bool;
    let event_loop_obj_opt: Option<Py<PyAny>>;
    {
        let app = entry.read();
        dispatch = app.dispatch.clone_ref(py);

        // Route matching
        if let Some((r, params, id)) = app.router.find(&method, &path) {
            route = r.handler.clone_ref(py);
            path_params = params;
            handler_id = id;
        } else {
            // Automatic OPTIONS handling: if no explicit OPTIONS handler exists,
            // check if other methods are registered for this path and return Allow header
            if method == "OPTIONS" {
                let available_methods = app.router.find_all_methods(&path);
                if !available_methods.is_empty() {
                    // Return 200 OK with Allow header listing available methods
                    let allow_header = available_methods.join(", ");
                    return Ok((
                        200,
                        vec![
                            ("content-type".to_string(), "application/json".to_string()),
                            ("allow".to_string(), allow_header),
                        ],
                        b"{}".to_vec(),
                    ));
                }
            }

            return Ok((
                404,
                vec![(
                    "content-type".to_string(),
                    "text/plain; charset=utf-8".to_string(),
                )],
                b"Not Found".to_vec(),
            ));
        }

        // Snapshot metadata and loop
        route_meta_opt = app.route_metadata.get(&handler_id).cloned();
        middleware_present = app.middleware_metadata.get(&handler_id).is_some();
        event_loop_obj_opt = app.event_loop.as_ref().map(|ev| ev.clone_ref(py));
    }
    test_debug!(
        "[test_state] matched handler_id={} path_params={:?} middleware_present={}",
        handler_id,
        path_params,
        middleware_present
    );

    // Parse query string
    let query_params = if let Some(q) = query_string {
        parse_query_string(&q)
    } else {
        AHashMap::new()
    };

    // Convert headers to map (lowercase keys)
    let mut header_map: AHashMap<String, String> = AHashMap::with_capacity(headers.len());
    for (name, value) in headers.iter() {
        let lower = name.to_ascii_lowercase();
        header_map.insert(lower.clone(), value.clone());
        if lower.contains('-') {
            let underscore_key = lower.replace('-', "_");
            header_map
                .entry(underscore_key)
                .or_insert_with(|| value.clone());
        }
    }

    // Authentication (synchronous part)
    let auth_ctx = if let Some(route_meta) = route_meta_opt.as_ref() {
        if !route_meta.auth_backends.is_empty() {
            authenticate(&header_map, &route_meta.auth_backends)
        } else {
            None
        }
    } else {
        None
    };

    // Guards evaluation
    if let Some(route_meta) = route_meta_opt.as_ref() {
        if !route_meta.guards.is_empty() {
            match evaluate_guards(&route_meta.guards, auth_ctx.as_ref()) {
                GuardResult::Allow => {}
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

    // Create context dict only if auth context is present
    let context = if let Some(ref auth) = auth_ctx {
        let ctx_dict = PyDict::new(py);
        let ctx_py = ctx_dict.unbind();
        populate_auth_context(&ctx_py, auth, py);
        Some(ctx_py)
    } else {
        None
    };
    test_debug!(
        "[test_state] request context built auth_present={} headers_len={} cookies_len={}",
        auth_ctx.is_some(),
        header_map.len(),
        cookies.len()
    );

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

    // Call dispatch to get coroutine
    let coroutine = dispatch.call1(py, (route, request_obj, handler_id))?;
    test_debug!("[test_state] obtained coroutine");

    // Instead of using pyo3_async_runtimes which requires a running event loop,
    // let's run the coroutine directly using asyncio.run() or loop.run_until_complete()
    let asyncio = py.import("asyncio")?;
    test_debug!("[test_state] imported asyncio");

    // Get or create event loop
    let loop_obj = if let Some(ev_obj) = event_loop_obj_opt {
        test_debug!("[test_state] using stored event loop");
        ev_obj.into_bound(py)
    } else {
        test_debug!("[test_state] getting current event loop");
        // Try to get current loop, or create new one
        match asyncio.call_method0("get_event_loop") {
            Ok(l) => l,
            Err(_) => {
                test_debug!("[test_state] creating new event loop");
                let l = asyncio.call_method0("new_event_loop")?;
                asyncio.call_method1("set_event_loop", (&l,))?;
                // Store it for reuse
                if let Some(entry2) = registry().get(&app_id) {
                    entry2.write().event_loop = Some(l.clone().unbind());
                }
                l
            }
        }
    };

    test_debug!("[test_state] running coroutine with run_until_complete");
    let result_obj = loop_obj.call_method1("run_until_complete", (coroutine,))?;
    test_debug!("[test_state] coroutine completed");
    let result_obj = result_obj.unbind();

    // Debug: check what type we got back
    let type_name = result_obj
        .bind(py)
        .get_type()
        .name()
        .map(|s| s.to_string())
        .unwrap_or_else(|_| "unknown".to_string());
    test_debug!("[test_state] result type: {}", type_name);

    // Extract response (tuple fast-path)
    let tuple_result: Result<(u16, Vec<(String, String)>, Vec<u8>), _> = result_obj.extract(py);
    test_debug!(
        "[test_state] tuple extraction succeeded: {}",
        tuple_result.is_ok()
    );
    if let Ok((status_code, resp_headers, body_bytes)) = tuple_result {
        // Filter out special headers
        let headers: Vec<(String, String)> = resp_headers
            .into_iter()
            .filter(|(k, _)| !k.eq_ignore_ascii_case("x-bolt-file-path"))
            .collect();

        // HEAD requests must have empty body per RFC 7231
        let response_body = if method == "HEAD" {
            Vec::new()
        } else {
            body_bytes
        };

        test_debug!(
            "[test_state] returning tuple status={} headers_len={} body_len={}",
            status_code,
            headers.len(),
            response_body.len()
        );
        return Ok((status_code, headers, response_body));
    }

    // Streaming: collect best-effort
    let is_streaming = (|| -> PyResult<bool> {
        let obj = result_obj.bind(py);
        let m = py.import("django_bolt.responses")?;
        let cls = m.getattr("StreamingResponse")?;
        obj.is_instance(&cls)
    })()
    .unwrap_or(false);

    test_debug!("[test_state] is_streaming: {}", is_streaming);

    if is_streaming {
        test_debug!("[test_state] handling streaming response");
        let obj = result_obj.bind(py);
        let status_code: u16 = obj
            .getattr("status_code")
            .and_then(|v| v.extract())
            .unwrap_or(200);
        test_debug!("[test_state] extracted status_code: {}", status_code);

        let mut resp_headers: Vec<(String, String)> = Vec::new();
        test_debug!("[test_state] extracting headers...");
        if let Ok(hobj) = obj.getattr("headers") {
            let header_type = hobj
                .get_type()
                .name()
                .map(|s| s.to_string())
                .unwrap_or_else(|_| "unknown".to_string());
            test_debug!("[test_state] got headers object, type: {}", header_type);
            if let Ok(hdict) = hobj.downcast::<PyDict>() {
                test_debug!("[test_state] headers is a dict");
                for (k, v) in hdict {
                    if let (Ok(ks), Ok(vs)) = (k.extract::<String>(), v.extract::<String>()) {
                        resp_headers.push((ks, vs));
                    }
                }
            } else if hobj.hasattr("items").unwrap_or(false) {
                // Try as dict-like with items() method
                test_debug!("[test_state] headers has items() method");
                if let Ok(items_method) = hobj.call_method0("items") {
                    if let Ok(items_iter) = items_method.try_iter() {
                        for item in items_iter {
                            if let Ok(pair) = item {
                                if let Ok(tuple) = pair.extract::<(String, String)>() {
                                    resp_headers.push(tuple);
                                }
                            }
                        }
                    }
                }
            }
        }

        // Add media_type as content-type if provided
        let is_sse = if let Ok(media_type) = obj
            .getattr("media_type")
            .and_then(|v| v.extract::<String>())
        {
            let is_event_stream = media_type.contains("event-stream");
            if !resp_headers
                .iter()
                .any(|(k, _)| k.eq_ignore_ascii_case("content-type"))
            {
                resp_headers.push(("content-type".to_string(), media_type));
            }
            is_event_stream
        } else {
            false
        };

        // Add SSE-friendly headers if this is an SSE response
        if is_sse {
            if !resp_headers
                .iter()
                .any(|(k, _)| k.eq_ignore_ascii_case("x-accel-buffering"))
            {
                resp_headers.push(("x-accel-buffering".to_string(), "no".to_string()));
            }
            if !resp_headers
                .iter()
                .any(|(k, _)| k.eq_ignore_ascii_case("cache-control"))
            {
                resp_headers.push(("cache-control".to_string(), "no-cache".to_string()));
            }
        }

        // Collect streaming content best-effort
        let mut content_obj = obj.getattr("content")?;
        // If content is callable (generator function), call it to get the generator
        if content_obj.is_callable() {
            test_debug!("[test_state] content is callable, calling it...");
            content_obj = content_obj.call0()?;
        }
        let mut collected_body = Vec::new();
        let has_aiter = content_obj.hasattr("__aiter__").unwrap_or(false);
        if has_aiter {
            // For async generators, we need to consume them with the event loop
            // Create a list from the async generator
            let _asyncio = py.import("asyncio")?;
            let list_from_agen =
                |agen: &Bound<PyAny>, loop_obj: &Bound<PyAny>| -> PyResult<Vec<Vec<u8>>> {
                    let loop_ref = loop_obj.clone();

                    // Use asyncio.run_until_complete to consume the async generator
                    let py_code = c_str!(
                        r#"
async def consume_agen(agen):
    chunks = []
    async for chunk in agen:
        if isinstance(chunk, bytes):
            chunks.append(chunk)
        elif isinstance(chunk, str):
            chunks.append(chunk.encode('utf-8'))
        elif isinstance(chunk, bytearray):
            chunks.append(bytes(chunk))
        elif isinstance(chunk, memoryview):
            chunks.append(bytes(chunk))
    return chunks
"#
                    );
                    let locals = pyo3::types::PyDict::new(py);
                    py.run(py_code, None, Some(&locals))?;
                    let consume_fn = locals.get_item("consume_agen")?.unwrap();
                    let coro = consume_fn.call1((agen,))?;
                    let result = loop_ref.call_method1("run_until_complete", (coro,))?;
                    result.extract()
                };

            match list_from_agen(&content_obj, &loop_obj) {
                Ok(chunks) => {
                    for chunk in chunks {
                        collected_body.extend_from_slice(&chunk);
                    }
                }
                Err(e) => {
                    test_debug!(
                        "[test_state] warning: failed to consume async generator: {}",
                        e
                    );
                    collected_body = b"[error consuming async streaming content]".to_vec();
                }
            }
        } else if let Ok(iter) = content_obj.try_iter() {
            for item in iter {
                if let Ok(chunk) = item {
                    if let Ok(bytes_vec) = chunk.extract::<Vec<u8>>() {
                        collected_body.extend_from_slice(&bytes_vec);
                    } else if let Ok(s) = chunk.extract::<String>() {
                        collected_body.extend_from_slice(s.as_bytes());
                    }
                }
            }
        }

        // HEAD requests must have empty body per RFC 7231
        let response_body = if method == "HEAD" {
            Vec::new()
        } else {
            collected_body
        };
        return Ok((status_code, resp_headers, response_body));
    }

    Err(pyo3::exceptions::PyTypeError::new_err(
        "Handler returned unsupported response type (expected tuple or StreamingResponse)",
    ))
}

#[pyfunction]
pub fn handle_actix_http_request(
    _py: Python<'_>,
    app_id: u64,
    method: String,
    path: String,
    headers: Vec<(String, String)>,
    body: Vec<u8>,
    query_string: Option<String>,
) -> PyResult<(u16, Vec<(String, String)>, Vec<u8>)> {
    // We need to run this in a tokio runtime since actix test functions are async
    let runtime = tokio::runtime::Runtime::new().map_err(|e| {
        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to create runtime: {}", e))
    })?;

    runtime.block_on(async {
        // Verify test app exists
        let reg = registry();
        let entry = reg.get(&app_id).ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Test app {} not found", app_id))
        })?;
        drop(entry);

        // Create custom handler that uses per-instance router via handle_test_request_for
        let handler = move |req: actix_web::HttpRequest, body: web::Bytes| {
            async move {
                // Extract request info
                let method = req.method().as_str().to_uppercase();
                let path = req.path().to_string();
                let query_string = req.query_string();
                let query = if query_string.is_empty() {
                    None
                } else {
                    Some(query_string.to_string())
                };

                // Extract headers
                let headers: Vec<(String, String)> = req
                    .headers()
                    .iter()
                    .map(|(k, v)| (k.as_str().to_string(), v.to_str().unwrap_or("").to_string()))
                    .collect();

                let body_bytes = body.to_vec();

                // Get request origin for CORS
                let request_origin = req
                    .headers()
                    .get("origin")
                    .and_then(|v| v.to_str().ok())
                    .map(|s| s.to_string());

                // Check if this is a CORS preflight (OPTIONS request)
                let is_preflight = method == "OPTIONS"
                    && request_origin.is_some()
                    && req.headers().contains_key("access-control-request-method");

                // Get middleware config from route metadata and global CORS origins
                let (
                    cors_config,
                    rate_limit_config,
                    handler_id_opt,
                    should_skip_cors,
                    should_skip_compression,
                    global_cors_origins,
                ) = Python::attach(
                    |_py| -> (
                        Option<crate::metadata::CorsConfig>,
                        Option<crate::metadata::RateLimitConfig>,
                        Option<usize>,
                        bool,
                        bool,
                        Vec<String>,
                    ) {
                        let Some(entry) = registry().get(&app_id) else {
                            return (None, None, None, false, false, vec![]);
                        };
                        let app = entry.read();

                        // Capture global CORS origins
                        let global_origins = app.cors_allowed_origins.clone();

                        // For preflight, we need to check the actual route method, not OPTIONS
                        let lookup_method = if is_preflight {
                            // Get the requested method from Access-Control-Request-Method header
                            req.headers()
                                .get("access-control-request-method")
                                .and_then(|v| v.to_str().ok())
                                .map(|s| s.to_uppercase())
                                .unwrap_or_else(|| method.clone())
                        } else {
                            method.clone()
                        };

                        // Find the route to get handler_id
                        if let Some((_route, _params, handler_id)) =
                            app.router.find(&lookup_method, &path)
                        {
                            // Get route metadata
                            if let Some(route_meta) = app.route_metadata.get(&handler_id) {
                                // Check if CORS is skipped
                                let skip_cors = route_meta.skip.contains("cors");
                                // Check if compression is skipped
                                let skip_compression = route_meta.skip.contains("compression");

                                // Use parsed Rust configs directly
                                let cors_cfg = route_meta.cors_config.clone();
                                let rate_cfg = route_meta.rate_limit_config.clone();

                                return (
                                    cors_cfg,
                                    rate_cfg,
                                    Some(handler_id),
                                    skip_cors,
                                    skip_compression,
                                    global_origins,
                                );
                            }
                        }
                        (None, None, None, false, false, global_origins)
                    },
                );

                // Handle CORS preflight - MUST validate origin per RFC 6454
                if is_preflight && !should_skip_cors {
                    if let Some(ref cors_cfg) = cors_config {
                        use actix_web::http::header::{
                            ACCESS_CONTROL_ALLOW_CREDENTIALS, ACCESS_CONTROL_ALLOW_HEADERS,
                            ACCESS_CONTROL_ALLOW_METHODS, ACCESS_CONTROL_ALLOW_ORIGIN,
                            ACCESS_CONTROL_MAX_AGE, VARY,
                        };
                        use actix_web::HttpResponse;

                        // Merge route-specific origins with global origins
                        let origins = if !cors_cfg.origins.is_empty() {
                            &cors_cfg.origins
                        } else if !global_cors_origins.is_empty() {
                            &global_cors_origins
                        } else {
                            // No CORS configured - reject preflight
                            return Ok(HttpResponse::Forbidden()
                                .content_type("text/plain; charset=utf-8")
                                .body("CORS not configured"));
                        };

                        let is_wildcard = origins.iter().any(|o| o == "*");

                        // Wildcard + credentials is invalid per CORS spec
                        if is_wildcard && cors_cfg.credentials {
                            // Reflect origin instead of using wildcard
                            if let Some(req_origin) = request_origin.as_deref() {
                                let mut response = HttpResponse::NoContent();
                                response.insert_header((ACCESS_CONTROL_ALLOW_ORIGIN, req_origin));
                                response.insert_header((VARY, "Origin"));
                                response.insert_header((ACCESS_CONTROL_ALLOW_CREDENTIALS, "true"));
                                response.insert_header((
                                    ACCESS_CONTROL_ALLOW_METHODS,
                                    cors_cfg.methods.join(", "),
                                ));
                                response.insert_header((
                                    ACCESS_CONTROL_ALLOW_HEADERS,
                                    cors_cfg.headers.join(", "),
                                ));
                                response.insert_header((
                                    ACCESS_CONTROL_MAX_AGE,
                                    cors_cfg.max_age.to_string(),
                                ));
                                // CRITICAL: Add Vary headers for preflight (RFC 7234)
                                response.insert_header((
                                    VARY,
                                    "Access-Control-Request-Method, Access-Control-Request-Headers",
                                ));
                                return Ok(response.finish());
                            }
                            // No origin header, reject
                            return Ok(HttpResponse::Forbidden().finish());
                        }

                        // Handle wildcard without credentials
                        if is_wildcard {
                            let mut response = HttpResponse::NoContent();
                            response.insert_header((ACCESS_CONTROL_ALLOW_ORIGIN, "*"));
                            response.insert_header((
                                ACCESS_CONTROL_ALLOW_METHODS,
                                cors_cfg.methods.join(", "),
                            ));
                            response.insert_header((
                                ACCESS_CONTROL_ALLOW_HEADERS,
                                cors_cfg.headers.join(", "),
                            ));
                            response.insert_header((
                                ACCESS_CONTROL_MAX_AGE,
                                cors_cfg.max_age.to_string(),
                            ));
                            // CRITICAL: Add Vary headers for preflight (RFC 7234)
                            response.insert_header((
                                VARY,
                                "Access-Control-Request-Method, Access-Control-Request-Headers",
                            ));
                            return Ok(response.finish());
                        }

                        // CRITICAL: Validate origin from request header
                        let req_origin = match request_origin.as_deref() {
                            Some(o) => o,
                            None => {
                                // No origin header, reject preflight
                                return Ok(HttpResponse::Forbidden()
                                    .content_type("text/plain; charset=utf-8")
                                    .body("Missing Origin header"));
                            }
                        };

                        // Check if request origin is in allowed origins list
                        if !origins.iter().any(|o| o == req_origin) {
                            // CRITICAL: Origin not allowed, reject preflight
                            return Ok(HttpResponse::Forbidden()
                                .content_type("text/plain; charset=utf-8")
                                .body("Origin not allowed"));
                        }

                        // Origin validated - add preflight headers
                        let mut response = HttpResponse::NoContent();
                        response.insert_header((ACCESS_CONTROL_ALLOW_ORIGIN, req_origin));
                        response.insert_header((VARY, "Origin"));
                        response.insert_header((
                            ACCESS_CONTROL_ALLOW_METHODS,
                            cors_cfg.methods.join(", "),
                        ));
                        response.insert_header((
                            ACCESS_CONTROL_ALLOW_HEADERS,
                            cors_cfg.headers.join(", "),
                        ));
                        response
                            .insert_header((ACCESS_CONTROL_MAX_AGE, cors_cfg.max_age.to_string()));

                        if cors_cfg.credentials {
                            response.insert_header((ACCESS_CONTROL_ALLOW_CREDENTIALS, "true"));
                        }

                        // CRITICAL: Add Vary headers for preflight per RFC 7234
                        response.insert_header((
                            VARY,
                            "Access-Control-Request-Method, Access-Control-Request-Headers",
                        ));

                        return Ok(response.finish());
                    }
                }

                // Check rate limiting
                if let (Some(handler_id), Some(rate_cfg)) =
                    (handler_id_opt, rate_limit_config.as_ref())
                {
                    use crate::middleware::rate_limit::check_rate_limit;
                    // Convert headers to AHashMap
                    let header_map: ahash::AHashMap<String, String> = headers
                        .iter()
                        .map(|(k, v)| (k.to_lowercase(), v.clone()))
                        .collect();
                    if let Some(response) =
                        check_rate_limit(handler_id, &header_map, None, rate_cfg)
                    {
                        return Ok(response);
                    }
                }

                // Call handle_test_request_for which does all the routing/auth/guards
                let result = Python::attach(|py| {
                    handle_test_request_for(
                        py,
                        app_id,
                        method.clone(),
                        path.clone(),
                        headers.clone(),
                        body_bytes,
                        query,
                    )
                });

                match result {
                    Ok((status_code, mut resp_headers, resp_body)) => {
                        // Add Content-Encoding: identity header if compression should be skipped
                        if should_skip_compression {
                            resp_headers.push(("content-encoding".to_string(), "identity".to_string()));
                        }

                        let mut response = actix_web::HttpResponse::build(
                            actix_web::http::StatusCode::from_u16(status_code)
                                .unwrap_or(actix_web::http::StatusCode::OK),
                        );
                        for (name, value) in &resp_headers {
                            response.insert_header((name.as_str(), value.as_str()));
                        }

                        let mut http_response = response.body(resp_body);

                        // Add CORS headers to response if not skipped
                        if !should_skip_cors {
                            if let Some(ref cors_cfg) = cors_config {
                                use actix_web::http::header::{
                                    ACCESS_CONTROL_ALLOW_CREDENTIALS, ACCESS_CONTROL_ALLOW_ORIGIN,
                                    ACCESS_CONTROL_EXPOSE_HEADERS, VARY,
                                };

                                // Merge route-specific origins with global origins
                                let origins = if !cors_cfg.origins.is_empty() {
                                    &cors_cfg.origins
                                } else if !global_cors_origins.is_empty() {
                                    &global_cors_origins
                                } else {
                                    // No CORS configured, skip
                                    return Ok::<_, actix_web::Error>(http_response);
                                };

                                let is_wildcard = origins.iter().any(|o| o == "*");
                                if is_wildcard && cors_cfg.credentials {
                                    // Invalid configuration - skip adding headers
                                    return Ok::<_, actix_web::Error>(http_response);
                                }

                                // Determine origin to use
                                let origin_to_use = if is_wildcard {
                                    "*"
                                } else if let Some(req_origin) = request_origin.as_deref() {
                                    if origins.iter().any(|o| o == req_origin) {
                                        req_origin
                                    } else {
                                        return Ok::<_, actix_web::Error>(http_response);
                                        // Origin not allowed
                                    }
                                } else {
                                    origins.first().map(|s| s.as_str()).unwrap_or("*")
                                };

                                // Add headers
                                http_response.headers_mut().insert(
                                    ACCESS_CONTROL_ALLOW_ORIGIN,
                                    origin_to_use.parse().unwrap(),
                                );

                                if origin_to_use != "*" {
                                    http_response
                                        .headers_mut()
                                        .insert(VARY, "Origin".parse().unwrap());
                                }

                                if cors_cfg.credentials {
                                    http_response.headers_mut().insert(
                                        ACCESS_CONTROL_ALLOW_CREDENTIALS,
                                        "true".parse().unwrap(),
                                    );
                                }

                                if !cors_cfg.expose_headers.is_empty() {
                                    http_response.headers_mut().insert(
                                        ACCESS_CONTROL_EXPOSE_HEADERS,
                                        cors_cfg.expose_headers.join(", ").parse().unwrap(),
                                    );
                                }
                            }
                        }

                        Ok::<_, actix_web::Error>(http_response)
                    }
                    Err(e) => Ok(actix_web::HttpResponse::InternalServerError()
                        .body(format!("Handler error: {}", e))),
                }
            }
        };

        // Create Actix test service with middleware
        let app = test::init_service(
            App::new()
                .wrap(crate::middleware::compression::CompressionMiddleware::new())
                // CORS handled in handler closure (preflight + response headers)
                // Rate limiting handled in handler closure (per-route state)
                .default_service(web::route().to(handler)),
        )
        .await;

        // Build full URI
        let uri = if let Some(qs) = query_string {
            format!("{}?{}", path, qs)
        } else {
            path
        };

        // Create test request
        let mut req = test::TestRequest::with_uri(&uri);

        // Set method
        req = match method.to_uppercase().as_str() {
            "GET" => req.method(actix_web::http::Method::GET),
            "POST" => req.method(actix_web::http::Method::POST),
            "PUT" => req.method(actix_web::http::Method::PUT),
            "PATCH" => req.method(actix_web::http::Method::PATCH),
            "DELETE" => req.method(actix_web::http::Method::DELETE),
            "OPTIONS" => req.method(actix_web::http::Method::OPTIONS),
            "HEAD" => req.method(actix_web::http::Method::HEAD),
            _ => req.method(actix_web::http::Method::GET),
        };

        // Set headers
        for (name, value) in headers {
            req = req.insert_header((name, value));
        }

        // Set body
        if !body.is_empty() {
            req = req.set_payload(Bytes::from(body));
        }

        // Call service
        let request = req.to_request();
        let response = app.call(request).await.map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Service call failed: {}", e))
        })?;

        // Extract response
        let status = response.status().as_u16();

        let resp_headers: Vec<(String, String)> = response
            .headers()
            .iter()
            .map(|(k, v)| (k.as_str().to_string(), v.to_str().unwrap_or("").to_string()))
            .collect();

        let resp_body = test::read_body(response).await.to_vec();

        Ok((status, resp_headers, resp_body))
    })
}

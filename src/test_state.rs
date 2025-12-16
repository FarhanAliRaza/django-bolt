use ahash::AHashMap;
use dashmap::DashMap;
use once_cell::sync::OnceCell;
use parking_lot::RwLock;
use pyo3::ffi::c_str;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

use crate::core_handler::{
    build_py_request, get_effective_cors_config, needs_cookies, needs_headers,
    process_handler_result, process_request_pre_dispatch, CoreHandlerResult,
    PreDispatchResult, RequestDependencies, RequestInput,
};
use crate::cors::apply_cors_to_vec;
use crate::handler::headers_vec_to_map;
use crate::metadata::{CorsConfig, RouteMetadata};
use crate::middleware::auth::{authenticate, populate_auth_context};
use crate::permissions::{evaluate_guards, GuardResult};
use crate::router::Router;
use crate::websocket::WebSocketRouter;

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
///
/// Uses Arc for router/route_metadata to allow sharing with production handler tests
/// without requiring Clone on Router (which would be expensive due to Py<PyAny>)
pub struct TestApp {
    pub router: Arc<Router>,
    pub websocket_router: WebSocketRouter, // WebSocket routes for testing
    pub middleware_metadata: AHashMap<usize, Py<PyAny>>, // raw Python metadata for compatibility
    pub route_metadata: Arc<AHashMap<usize, RouteMetadata>>, // parsed Rust metadata
    pub dispatch: Py<PyAny>,
    pub event_loop: Option<Py<PyAny>>, // store loop; create TaskLocals per call
    pub global_cors_config: Option<CorsConfig>, // global CORS config for testing (same as production)
}

static TEST_REGISTRY: OnceCell<DashMap<u64, Arc<RwLock<TestApp>>>> = OnceCell::new();
static TEST_ID_GEN: AtomicU64 = AtomicU64::new(1);

fn registry() -> &'static DashMap<u64, Arc<RwLock<TestApp>>> {
    TEST_REGISTRY.get_or_init(|| DashMap::new())
}

#[pyfunction]
#[pyo3(signature = (dispatch, _debug, cors_config=None))]
pub fn create_test_app(
    py: Python<'_>,
    dispatch: Py<PyAny>,
    _debug: bool,
    cors_config: Option<&Bound<'_, PyDict>>,
) -> PyResult<u64> {
    // Parse CORS config from Python dict (same format as production server)
    let global_cors_config = if let Some(cors_dict) = cors_config {
        Some(parse_cors_config_from_dict(cors_dict)?)
    } else {
        None
    };

    let app = TestApp {
        router: Arc::new(Router::new()),
        websocket_router: WebSocketRouter::new(),
        middleware_metadata: AHashMap::new(),
        route_metadata: Arc::new(AHashMap::new()),
        dispatch: dispatch.clone_ref(py),
        event_loop: None,
        global_cors_config,
    };
    let id = TEST_ID_GEN.fetch_add(1, Ordering::Relaxed);
    registry().insert(id, Arc::new(RwLock::new(app)));
    Ok(id)
}

/// Parse CORS config from a Python dict
fn parse_cors_config_from_dict(dict: &Bound<'_, PyDict>) -> PyResult<CorsConfig> {
    use actix_web::http::header::HeaderValue;
    use ahash::AHashSet;

    // Extract origins
    let origins: Vec<String> = dict
        .get_item("origins")?
        .map(|v| v.extract().unwrap_or_default())
        .unwrap_or_default();

    // Build origin_set for O(1) lookup
    let origin_set: AHashSet<String> = origins.iter().cloned().collect();

    // Check for wildcard
    let allow_all_origins = origins.iter().any(|o| o == "*");

    // Extract credentials
    let credentials: bool = dict
        .get_item("credentials")?
        .map(|v| v.extract().unwrap_or(false))
        .unwrap_or(false);

    // Extract methods with defaults
    let methods: Vec<String> = dict
        .get_item("methods")?
        .map(|v| v.extract().unwrap_or_default())
        .unwrap_or_else(|| {
            vec![
                "GET".to_string(),
                "POST".to_string(),
                "PUT".to_string(),
                "PATCH".to_string(),
                "DELETE".to_string(),
                "OPTIONS".to_string(),
            ]
        });

    // Extract headers with defaults
    let headers: Vec<String> = dict
        .get_item("headers")?
        .map(|v| v.extract().unwrap_or_default())
        .unwrap_or_else(|| {
            vec![
                "accept".to_string(),
                "accept-encoding".to_string(),
                "authorization".to_string(),
                "content-type".to_string(),
                "dnt".to_string(),
                "origin".to_string(),
                "user-agent".to_string(),
                "x-csrftoken".to_string(),
                "x-requested-with".to_string(),
            ]
        });

    // Extract expose_headers
    let expose_headers: Vec<String> = dict
        .get_item("expose_headers")?
        .map(|v| v.extract().unwrap_or_default())
        .unwrap_or_default();

    // Extract max_age
    let max_age: u32 = dict
        .get_item("max_age")?
        .map(|v| v.extract().unwrap_or(86400))
        .unwrap_or(86400);

    // Build pre-computed strings
    let methods_str = methods.join(", ");
    let headers_str = headers.join(", ");
    let expose_headers_str = expose_headers.join(", ");
    let max_age_str = max_age.to_string();

    // Build cached HeaderValues
    let methods_header = HeaderValue::from_str(&methods_str).ok();
    let headers_header = HeaderValue::from_str(&headers_str).ok();
    let expose_headers_header = if !expose_headers_str.is_empty() {
        HeaderValue::from_str(&expose_headers_str).ok()
    } else {
        None
    };
    let max_age_header = HeaderValue::from_str(&max_age_str).ok();

    Ok(CorsConfig {
        origins,
        origin_regexes: vec![], // TODO: support regex in tests if needed
        compiled_origin_regexes: vec![],
        origin_set,
        allow_all_origins,
        credentials,
        methods,
        headers,
        expose_headers,
        max_age,
        methods_str,
        headers_str,
        expose_headers_str,
        max_age_str,
        methods_header,
        headers_header,
        expose_headers_header,
        max_age_header,
    })
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
    // Get mutable access to router - only works when this is the only Arc reference
    let router = Arc::get_mut(&mut app.router).ok_or_else(|| {
        pyo3::exceptions::PyRuntimeError::new_err("Cannot register routes while router is in use")
    })?;
    for (method, path, handler_id, handler) in routes {
        router.register(&method, &path, handler_id, handler)?;
    }
    Ok(())
}

#[pyfunction]
pub fn register_test_websocket_routes(
    _py: Python<'_>,
    app_id: u64,
    routes: Vec<(String, usize, Py<PyAny>, Option<Py<PyAny>>)>,
) -> PyResult<()> {
    let Some(entry) = registry().get(&app_id) else {
        return Err(pyo3::exceptions::PyKeyError::new_err("Invalid test app id"));
    };
    let mut app = entry.write();
    for (path, handler_id, handler, injector) in routes {
        app.websocket_router
            .register(&path, handler_id, handler, injector)?;
    }
    Ok(())
}

/// Find a WebSocket route for the given path in a test app
#[allow(dead_code)] // Reserved for future WebSocket testing utilities
pub fn find_test_websocket_route(app_id: u64) -> Option<Arc<RwLock<TestApp>>> {
    registry().get(&app_id).map(|entry| entry.clone())
}

/// Handle WebSocket test request - simulates the WebSocket connection flow
/// This is called from Python's WebSocketTestClient to route through Rust
///
/// Now includes full security checks matching production:
/// - Origin validation (using same CORS config as HTTP)
/// - Rate limiting (reuses HTTP rate limit infrastructure)
/// - Connection limits
/// - Authentication and guards
#[pyfunction]
pub fn handle_test_websocket(
    py: Python<'_>,
    app_id: u64,
    path: String,
    headers: Vec<(String, String)>,
    query_string: Option<String>,
) -> PyResult<(bool, usize, Py<PyAny>, Py<PyAny>, Py<PyAny>)> {
    // Returns: (found, handler_id, handler, path_params_dict, scope_dict)
    // If found is false, handler_id is 0 and handler/path_params/scope are None

    let entry = registry()
        .get(&app_id)
        .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("Invalid test app id"))?;

    let app = entry.read();

    // Convert headers to AHashMap for security checks
    let mut header_map: AHashMap<String, String> = AHashMap::with_capacity(headers.len());
    for (name, value) in headers.iter() {
        header_map.insert(name.to_lowercase(), value.clone());
    }

    // ===== SECURITY CHECK 1: Origin Validation =====
    // Uses same CORS config as HTTP (like FastAPI)
    let origin = header_map.get("origin");
    if let Some(origin_value) = origin {
        // Cross-origin request - must validate against CORS config
        let origin_allowed = if let Some(ref cors_config) = app.global_cors_config {
            // Check allow_all_origins
            if cors_config.allow_all_origins {
                true
            } else {
                // O(1) HashSet lookup
                cors_config.origin_set.contains(origin_value)
                    || cors_config
                        .compiled_origin_regexes
                        .iter()
                        .any(|re| re.is_match(origin_value))
            }
        } else {
            // SECURITY: No CORS configured = deny all cross-origin requests (fail-secure)
            false
        };

        if !origin_allowed {
            return Err(pyo3::exceptions::PyPermissionError::new_err(format!(
                "Origin not allowed: {}. Configure CORS_ALLOWED_ORIGINS in Django settings.",
                origin_value
            )));
        }
    }
    // No origin header = same-origin request, allowed

    // Normalize trailing slash for consistent matching
    // WebSocket clients typically don't follow redirects, so we normalize server-side
    let normalized_path = if path.len() > 1 && path.ends_with('/') {
        &path[..path.len() - 1]
    } else {
        &path
    };

    // Look up the WebSocket route
    let (route, path_params) = match app.websocket_router.find(normalized_path) {
        Some((route, params)) => (route, params),
        None => {
            // Return not found
            return Ok((false, 0, py.None(), py.None(), py.None()));
        }
    };

    let handler_id = route.handler_id;
    let handler = route.handler.clone_ref(py);

    // ===== SECURITY CHECK 2: Rate Limiting =====
    // Reuses same rate limit infrastructure as HTTP
    if let Some(route_meta) = app.route_metadata.get(&handler_id) {
        if let Some(ref rate_config) = route_meta.rate_limit_config {
            if let Some(_response) = crate::middleware::rate_limit::check_rate_limit(
                handler_id,
                &header_map,
                Some("127.0.0.1"), // Test client IP
                rate_config,
                "GET", // Method not available in WebSocket upgrade
                &path,
            ) {
                return Err(pyo3::exceptions::PyPermissionError::new_err(
                    "Rate limit exceeded",
                ));
            }
        }
    }

    // ===== SECURITY CHECK 3: Authentication & Guards =====
    if let Some(route_meta) = app.route_metadata.get(&handler_id) {
        // Authenticate using real auth backends (JWT, API key, etc.)
        let auth_ctx = if !route_meta.auth_backends.is_empty() {
            authenticate(&header_map, &route_meta.auth_backends)
        } else {
            None
        };

        // Evaluate guards
        if !route_meta.guards.is_empty() {
            match evaluate_guards(&route_meta.guards, auth_ctx.as_ref()) {
                GuardResult::Allow => {}
                GuardResult::Unauthorized => {
                    return Err(pyo3::exceptions::PyPermissionError::new_err(
                        "Authentication required",
                    ));
                }
                GuardResult::Forbidden => {
                    return Err(pyo3::exceptions::PyPermissionError::new_err(
                        "Permission denied",
                    ));
                }
            }
        }
    }

    // Build path_params dict
    let path_params_dict = pyo3::types::PyDict::new(py);
    for (k, v) in path_params.iter() {
        path_params_dict.set_item(k, v)?;
    }

    // Build scope dict (ASGI-style)
    let scope_dict = pyo3::types::PyDict::new(py);
    scope_dict.set_item("type", "websocket")?;
    scope_dict.set_item("path", &path)?;

    // Query string as bytes
    let qs_bytes = query_string.as_ref().map(|s| s.as_bytes()).unwrap_or(b"");
    scope_dict.set_item("query_string", pyo3::types::PyBytes::new(py, qs_bytes))?;

    // Headers as dict (lowercase keys)
    let headers_dict = pyo3::types::PyDict::new(py);
    for (k, v) in headers.iter() {
        headers_dict.set_item(k.to_lowercase(), v)?;
    }
    scope_dict.set_item("headers", headers_dict)?;

    // Path params
    scope_dict.set_item("path_params", &path_params_dict)?;

    // Parse cookies from headers
    let cookies_dict = pyo3::types::PyDict::new(py);
    for (k, v) in headers.iter() {
        if k.to_lowercase() == "cookie" {
            for pair in v.split(';') {
                let pair = pair.trim();
                if let Some(eq_pos) = pair.find('=') {
                    let key = &pair[..eq_pos];
                    let value = &pair[eq_pos + 1..];
                    cookies_dict.set_item(key, value)?;
                }
            }
        }
    }
    scope_dict.set_item("cookies", cookies_dict)?;

    // Client address
    let client_tuple = pyo3::types::PyTuple::new(py, &["127.0.0.1", "12345"])?;
    scope_dict.set_item("client", client_tuple)?;

    // Add auth context to scope if present
    if let Some(route_meta) = app.route_metadata.get(&handler_id) {
        let auth_ctx = if !route_meta.auth_backends.is_empty() {
            authenticate(&header_map, &route_meta.auth_backends)
        } else {
            None
        };

        if let Some(ref auth) = auth_ctx {
            let ctx_dict = pyo3::types::PyDict::new(py);
            populate_auth_context(&ctx_dict.clone().unbind(), auth, py);
            scope_dict.set_item("auth_context", ctx_dict)?;
        }
    }

    Ok((
        true,
        handler_id,
        handler,
        path_params_dict.into(),
        scope_dict.into(),
    ))
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

        if let Ok(py_dict) = meta.bind(py).cast::<PyDict>() {
            match RouteMetadata::from_python(py_dict, py) {
                Ok(parsed) => {
                    // Use Arc::make_mut to get mutable access
                    Arc::make_mut(&mut app.route_metadata).insert(handler_id, parsed);
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

/// Helper to add CORS headers to a Vec (for test responses that return tuples)
/// Uses the unified CORS implementation from cors.rs
fn add_cors_headers_to_vec(
    resp_headers: &mut Vec<(String, String)>,
    header_map: &AHashMap<String, String>,
    cors_cfg: Option<&CorsConfig>,
    global_cors_cfg: Option<&CorsConfig>,
) {
    if let Some(cfg) = cors_cfg {
        let request_origin = header_map.get("origin").map(|s| s.as_str());
        // Use global origin_set and regexes for fallback (same as production middleware)
        let global_origin_set = global_cors_cfg.map(|g| &g.origin_set);
        let global_regexes = global_cors_cfg
            .filter(|g| !g.compiled_origin_regexes.is_empty())
            .map(|g| g.compiled_origin_regexes.as_slice());
        apply_cors_to_vec(resp_headers, request_origin, cfg, global_origin_set, global_regexes);
    }
}

/// Handle test request using the SAME core logic as production handler.
/// This function uses the shared process_request_pre_dispatch from core_handler.rs
/// to ensure test and production code paths are identical.
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

    test_debug!(
        "[test_state] start app_id={} method={} path={} headers={} body_len={} query={:?}",
        app_id,
        method,
        path,
        headers.len(),
        body.len(),
        query_string
    );

    // Convert headers to map (lowercase keys) using shared function
    let header_map = headers_vec_to_map(&headers);

    // Build RequestInput (same structure used by production handler)
    let input = RequestInput {
        method: method.clone(),
        path: path.clone(),
        headers: header_map.clone(),
        body: body.clone(),
        query_string: query_string.clone(),
        peer_addr: None, // Not available in sync testing
    };

    // Build RequestDependencies from TestApp
    let (dispatch, router_ref, route_metadata_ref, global_cors_config, event_loop_obj_opt) = {
        let app = entry.read();
        (
            app.dispatch.clone_ref(py),
            Arc::clone(&app.router),
            Arc::clone(&app.route_metadata),
            app.global_cors_config.clone(),
            app.event_loop.as_ref().map(|ev| ev.clone_ref(py)),
        )
    };

    // Create route_metadata lookup function (same pattern as production)
    let route_metadata_lookup = |handler_id: usize| -> Option<RouteMetadata> {
        route_metadata_ref.get(&handler_id).cloned()
    };

    let deps = RequestDependencies {
        router: &router_ref,
        route_metadata: &route_metadata_lookup,
        global_cors_config: global_cors_config.as_ref(),
        dispatch: &dispatch,
        debug: true,
    };

    // Use SHARED core logic for pre-dispatch (route matching, auth, rate limiting, etc.)
    let pre_result = process_request_pre_dispatch(&input, &deps);

    // Handle pre-dispatch result
    let (handler, handler_id, path_params, query_params, auth_ctx, route_metadata, skip_compression, skip_cors, is_head_request) = match pre_result {
        PreDispatchResult::Error(result) => {
            // Convert CoreHandlerResult to tuple
            return Ok(result.to_tuple());
        }
        PreDispatchResult::Ready {
            handler,
            handler_id,
            path_params,
            query_params,
            auth_ctx,
            route_metadata,
            skip_compression,
            skip_cors,
            is_head_request,
        } => (handler, handler_id, path_params, query_params, auth_ctx, route_metadata, skip_compression, skip_cors, is_head_request),
    };

    test_debug!(
        "[test_state] matched handler_id={} path_params={:?}",
        handler_id,
        path_params
    );

    // Build PyRequest using shared function from core_handler
    let request_obj = build_py_request(
        py,
        &input,
        path_params,
        query_params,
        auth_ctx.as_ref(),
        needs_headers(route_metadata.as_ref()),
        needs_cookies(route_metadata.as_ref()),
        &header_map,
    )?;

    // Get or create event loop (test-specific async execution)
    let asyncio = py.import("asyncio")?;
    let loop_obj = if let Some(ev_obj) = event_loop_obj_opt {
        test_debug!("[test_state] using stored event loop");
        ev_obj.into_bound(py)
    } else {
        test_debug!("[test_state] getting current event loop");
        match asyncio.call_method0("get_event_loop") {
            Ok(l) => l,
            Err(_) => {
                test_debug!("[test_state] creating new event loop");
                let l = asyncio.call_method0("new_event_loop")?;
                asyncio.call_method1("set_event_loop", (&l,))?;
                if let Some(entry2) = registry().get(&app_id) {
                    entry2.write().event_loop = Some(l.clone().unbind());
                }
                l
            }
        }
    };

    // Call dispatch (test uses run_until_complete instead of into_future_with_locals)
    test_debug!("[test_state] calling dispatch");
    let coroutine = dispatch.call1(py, (handler, request_obj, handler_id))?;
    test_debug!("[test_state] running coroutine with run_until_complete");
    let result_obj = loop_obj
        .call_method1("run_until_complete", (coroutine,))?
        .unbind();

    // Get effective CORS config for response processing
    let effective_cors = get_effective_cors_config(route_metadata.as_ref(), global_cors_config.as_ref());
    let request_origin = header_map.get("origin").map(|s| s.as_str());

    // Process handler result using SHARED core logic
    let core_result = process_handler_result(
        py,
        result_obj.clone_ref(py),
        skip_compression,
        skip_cors,
        is_head_request,
        request_origin,
        effective_cors,
        true, // debug
    );

    // Handle the core result
    match core_result {
        CoreHandlerResult::Simple(status, headers, body) => {
            test_debug!(
                "[test_state] returning simple response status={} headers_len={} body_len={}",
                status,
                headers.len(),
                body.len()
            );
            Ok((status, headers, body))
        }
        CoreHandlerResult::File { path: file_path, status, headers, .. } => {
            // For tests, read file synchronously
            test_debug!("[test_state] file response: {}", file_path);
            match std::fs::read(&file_path) {
                Ok(content) => Ok((status.as_u16(), headers, content)),
                Err(_) => Ok((404, vec![("content-type".to_string(), "text/plain".to_string())], b"File not found".to_vec())),
            }
        }
        CoreHandlerResult::Streaming { status, headers, content, is_async_generator, .. } => {
            // Collect streaming content for tests
            test_debug!("[test_state] streaming response");
            let collected_body = collect_streaming_content(py, &content, is_async_generator, &loop_obj)?;
            let response_body = if is_head_request { Vec::new() } else { collected_body };
            Ok((status.as_u16(), headers, response_body))
        }
        CoreHandlerResult::Error(resp) => {
            let status = resp.status().as_u16();
            let headers: Vec<(String, String)> = resp
                .headers()
                .iter()
                .map(|(k, v)| (k.as_str().to_string(), v.to_str().unwrap_or("").to_string()))
                .collect();
            Ok((status, headers, Vec::new()))
        }
    }
}

/// Helper to collect streaming content for tests
fn collect_streaming_content(
    py: Python<'_>,
    content: &Py<PyAny>,
    is_async_generator: bool,
    loop_obj: &Bound<PyAny>,
) -> PyResult<Vec<u8>> {
    use pyo3::ffi::c_str;

    let content_obj = content.bind(py);
    let mut collected_body = Vec::new();

    // If content is callable (generator function), call it to get the generator
    let content_obj = if content_obj.is_callable() {
        test_debug!("[test_state] content is callable, calling it...");
        content_obj.call0()?
    } else {
        content_obj.clone()
    };

    if is_async_generator || content_obj.hasattr("__aiter__").unwrap_or(false) {
        // Consume async generator
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
        let coro = consume_fn.call1((&content_obj,))?;
        let chunks: Vec<Vec<u8>> = loop_obj.call_method1("run_until_complete", (coro,))?.extract()?;
        for chunk in chunks {
            collected_body.extend_from_slice(&chunk);
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

    Ok(collected_body)
}

/// Handle test request through Actix test service with full middleware stack.
///
/// This function routes requests through:
/// 1. Actix test service (same as production)
/// 2. CorsMiddleware (same as production)
/// 3. CompressionMiddleware (same as production)
/// 4. Core handler using shared core_handler.rs logic
///
/// The only difference from production is the async execution model:
/// - Production uses into_future_with_locals (requires running asyncio loop)
/// - Tests use run_until_complete (synchronous execution)
#[pyfunction]
pub fn handle_actix_http_request(
    py: Python<'_>,
    app_id: u64,
    method: String,
    path: String,
    headers: Vec<(String, String)>,
    body: Vec<u8>,
    query_string: Option<String>,
) -> PyResult<(u16, Vec<(String, String)>, Vec<u8>)> {
    use crate::middleware::compression::CompressionMiddleware;
    use crate::middleware::cors::CorsMiddleware;
    use crate::state::AppState;

    // Build AppState from TestApp with injected router/metadata
    let app_state = {
        let entry = registry()
            .get(&app_id)
            .ok_or_else(|| pyo3::exceptions::PyRuntimeError::new_err(format!("Test app {} not found", app_id)))?;
        let app = entry.read();
        Arc::new(AppState {
            dispatch: app.dispatch.clone_ref(py),
            debug: true,
            max_header_size: 8192,
            global_cors_config: app.global_cors_config.clone(),
            cors_origin_regexes: Vec::new(),
            global_compression_config: None,
            // Inject test router and metadata - handler will use these via state.get_router()
            router: Some(Arc::clone(&app.router)),
            route_metadata: Some(Arc::clone(&app.route_metadata)),
        })
    };

    // Clone data needed for the async handler
    let app_state_for_handler = Arc::clone(&app_state);

    // Create a tokio runtime for the Actix test
    let runtime = tokio::runtime::Runtime::new().map_err(|e| {
        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to create runtime: {}", e))
    })?;

    runtime.block_on(async {
        // Handler that uses SAME core logic as production handler.rs
        // Uses process_request_pre_dispatch + process_handler_result from core_handler.rs
        let handler = move |req: actix_web::HttpRequest, body_bytes: web::Bytes| {
            let state = app_state_for_handler.clone();
            async move {
                let method = req.method().as_str().to_uppercase();
                let path = req.path().to_string();
                let query_string = req.uri().query().map(|q| q.to_string());
                let body_vec = body_bytes.to_vec();

                // Extract headers as Vec for the test handler
                let headers: Vec<(String, String)> = req
                    .headers()
                    .iter()
                    .map(|(k, v)| (k.as_str().to_string(), v.to_str().unwrap_or("").to_string()))
                    .collect();

                // Get app_id from registry to call handle_test_request_for
                // This uses the shared core_handler logic (process_request_pre_dispatch etc.)
                let result = Python::attach(|py| {
                    // Find app_id by matching state dispatch
                    for entry in registry().iter() {
                        let app = entry.read();
                        // Use dispatch pointer comparison
                        if std::ptr::eq(
                            app.dispatch.as_ptr(),
                            state.dispatch.as_ptr(),
                        ) {
                            return handle_test_request_for(
                                py,
                                *entry.key(),
                                method.clone(),
                                path.clone(),
                                headers.clone(),
                                body_vec.clone(),
                                query_string.clone(),
                            );
                        }
                    }
                    Err(pyo3::exceptions::PyRuntimeError::new_err("App not found in registry"))
                });

                match result {
                    Ok((status_code, resp_headers, resp_body)) => {
                        let http_response = crate::response_builder::build_response_with_headers(
                            actix_web::http::StatusCode::from_u16(status_code)
                                .unwrap_or(actix_web::http::StatusCode::OK),
                            resp_headers,
                            false, // skip_compression handled by middleware
                            resp_body,
                        );
                        Ok::<_, actix_web::Error>(http_response)
                    }
                    Err(e) => Ok(actix_web::HttpResponse::InternalServerError()
                        .body(format!("Handler error: {}", e))),
                }
            }
        };

        // Create Actix test service with PRODUCTION middleware stack
        let app = test::init_service(
            App::new()
                .app_data(web::Data::new(app_state))
                .app_data(web::PayloadConfig::new(1 * 1024 * 1024))
                .wrap(CompressionMiddleware::new())
                .wrap(CorsMiddleware::new())
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

        // Call service - goes through production middleware stack
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

// =============================================================================
// PRODUCTION HANDLER TEST - Uses exact same code path as production
// =============================================================================

/// Test function that uses the PRODUCTION handler with injected state.
///
/// This is the recommended way to test: it uses the exact same middleware stack
/// and handler code as production, ensuring tests accurately validate production behavior.
///
/// The only difference from production is that router/metadata are injected via AppState
/// instead of using global state.
#[pyfunction]
pub fn handle_request_production(
    py: Python<'_>,
    app_id: u64,
    method: String,
    path: String,
    headers: Vec<(String, String)>,
    body: Vec<u8>,
    query_string: Option<String>,
) -> PyResult<(u16, Vec<(String, String)>, Vec<u8>)> {
    use crate::handler::handle_request;
    use crate::middleware::compression::CompressionMiddleware;
    use crate::middleware::cors::CorsMiddleware;
    use crate::state::{AppState, TASK_LOCALS};

    // Ensure TASK_LOCALS is initialized (same as server startup)
    // This is needed because production handler.rs uses TASK_LOCALS for async dispatch
    if TASK_LOCALS.get().is_none() {
        let asyncio = py.import("asyncio")?;
        let ev = asyncio.call_method0("new_event_loop")?;
        asyncio.call_method1("set_event_loop", (&ev,))?;
        let locals = pyo3_async_runtimes::TaskLocals::new(ev.clone()).copy_context(py)?;
        let _ = TASK_LOCALS.set(locals);
    }

    // Get TestApp state
    let entry = registry()
        .get(&app_id)
        .ok_or_else(|| pyo3::exceptions::PyRuntimeError::new_err(format!("Test app {} not found", app_id)))?;

    // Build AppState with injected router/metadata from TestApp
    let app_state = {
        let app = entry.read();
        Arc::new(AppState {
            dispatch: app.dispatch.clone_ref(py),
            debug: true,
            max_header_size: 8192,
            global_cors_config: app.global_cors_config.clone(),
            cors_origin_regexes: Vec::new(),
            global_compression_config: None,
            // INJECT test router and metadata - clone the Arc, not the inner value
            router: Some(Arc::clone(&app.router)),
            route_metadata: Some(Arc::clone(&app.route_metadata)),
        })
    };
    drop(entry);

    // Run in tokio runtime
    pyo3_async_runtimes::tokio::get_runtime().block_on(async move {
        // Create test service with PRODUCTION middleware stack
        let app = test::init_service(
            App::new()
                .app_data(web::Data::new(app_state))
                .app_data(web::PayloadConfig::new(1 * 1024 * 1024)) // 1MB max
                .wrap(CompressionMiddleware::new())
                .wrap(CorsMiddleware::new())
                // Use PRODUCTION handler - same exact code path!
                .default_service(web::route().to(handle_request)),
        )
        .await;

        // Build URI
        let uri = if let Some(qs) = query_string {
            format!("{}?{}", path, qs)
        } else {
            path
        };

        // Create test request
        let mut req = test::TestRequest::with_uri(&uri);
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

use ahash::AHashMap;
use dashmap::DashMap;
use once_cell::sync::OnceCell;
use parking_lot::RwLock;
use pyo3::ffi::c_str;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

use crate::cors::{add_cors_response_headers, add_preflight_headers_simple};
use crate::handler::headers_vec_to_map;
use crate::metadata::{CorsConfig, RouteMetadata};
use crate::middleware::auth::{authenticate, populate_auth_context};
use crate::permissions::{evaluate_guards, GuardResult};
use crate::request::PyRequest;
use crate::router::{parse_query_string, Router};
use crate::validation::{parse_cookies_inline, validate_auth_and_guards, AuthGuardResult};
use crate::websocket::WebSocketRouter;

// Actix testing imports
use actix_web::dev::Service;
use actix_web::http::header::{
    ACCESS_CONTROL_ALLOW_CREDENTIALS, ACCESS_CONTROL_ALLOW_ORIGIN, VARY,
};
use actix_web::{test, web, App, HttpResponse};
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
    pub websocket_router: WebSocketRouter, // WebSocket routes for testing
    pub middleware_metadata: AHashMap<usize, Py<PyAny>>, // raw Python metadata for compatibility
    pub route_metadata: AHashMap<usize, RouteMetadata>, // parsed Rust metadata
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
        router: Router::new(),
        websocket_router: WebSocketRouter::new(),
        middleware_metadata: AHashMap::new(),
        route_metadata: AHashMap::new(),
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
    for (method, path, handler_id, handler) in routes {
        app.router.register(&method, &path, handler_id, handler)?;
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

/// Helper to add CORS headers to a Vec (for test responses that return tuples)
fn add_cors_headers_to_vec(
    resp_headers: &mut Vec<(String, String)>,
    header_map: &AHashMap<String, String>,
    cors_cfg: Option<&CorsConfig>,
) {
    if let Some(cfg) = cors_cfg {
        let request_origin = header_map.get("origin").map(|s| s.as_str());
        let mut temp_resp = HttpResponse::Ok().finish();
        let origin_allowed = add_cors_response_headers(
            &mut temp_resp,
            request_origin,
            &cfg.origins,
            cfg.credentials,
            &cfg.expose_headers,
        );
        if origin_allowed {
            for (name, value) in temp_resp.headers().iter() {
                let name_str = name.as_str();
                if name_str.starts_with("access-control") || name_str == "vary" {
                    if let Ok(val_str) = value.to_str() {
                        resp_headers.push((name_str.to_string(), val_str.to_string()));
                    }
                }
            }
        }
    }
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
    let global_cors_config: Option<CorsConfig>;
    {
        let app = entry.read();
        dispatch = app.dispatch.clone_ref(py);
        // Capture global CORS config for error responses (same as production handler.rs)
        global_cors_config = app.global_cors_config.clone();

        // Route matching
        if let Some(route_match) = app.router.find(&method, &path) {
            // Get handler_id first (borrows), then handler (borrows), then path_params (moves)
            handler_id = route_match.handler_id();
            route = route_match.route().handler.clone_ref(py);
            path_params = route_match.path_params(); // Consumes route_match
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

            // 404 response - add CORS headers if global CORS is configured (same as handler.rs)
            let mut resp_headers = vec![("content-type".to_string(), "text/plain; charset=utf-8".to_string())];
            let temp_header_map = headers_vec_to_map(&headers);
            add_cors_headers_to_vec(&mut resp_headers, &temp_header_map, global_cors_config.as_ref());
            return Ok((404, resp_headers, b"Not Found".to_vec()));
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

    // Convert headers to map (lowercase keys) using shared function
    let header_map = headers_vec_to_map(&headers);

    // Authentication and guards using shared validation logic
    let auth_ctx = if let Some(route_meta) = route_meta_opt.as_ref() {
        match validate_auth_and_guards(&header_map, &route_meta.auth_backends, &route_meta.guards) {
            AuthGuardResult::Allow(ctx) => ctx,
            AuthGuardResult::Unauthorized => {
                let mut resp_headers = vec![("content-type".to_string(), "application/json".to_string())];
                add_cors_headers_to_vec(&mut resp_headers, &header_map, route_meta.cors_config.as_ref().or(global_cors_config.as_ref()));
                return Ok((401, resp_headers, br#"{"detail":"Authentication required"}"#.to_vec()));
            }
            AuthGuardResult::Forbidden => {
                let mut resp_headers = vec![("content-type".to_string(), "application/json".to_string())];
                add_cors_headers_to_vec(&mut resp_headers, &header_map, route_meta.cors_config.as_ref().or(global_cors_config.as_ref()));
                return Ok((403, resp_headers, br#"{"detail":"Permission denied"}"#.to_vec()));
            }
        }
    } else {
        None
    };

    // Capture request origin for CORS on success responses (before header_map is moved into PyRequest)
    let request_origin_for_cors = header_map.get("origin").map(|s| s.to_string());

    // Parse cookies using shared function
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
        user: None,
        state: PyDict::new(py).unbind(), // Empty state dict for middleware and dynamic attributes
    };
    let request_obj = Py::new(py, request)?;

    // Get or create event loop upfront (needed for all handlers and streaming responses)
    let asyncio = py.import("asyncio")?;
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

    // All handlers (sync and async) go through async dispatch
    // Sync handlers are executed in thread pool via sync_to_thread() in Python layer
    test_debug!("[test_state] calling dispatch");
    let coroutine = dispatch.call1(py, (route, request_obj, handler_id))?;
    test_debug!("[test_state] obtained coroutine");

    test_debug!("[test_state] running coroutine with run_until_complete");
    let result_obj = loop_obj
        .call_method1("run_until_complete", (coroutine,))?
        .unbind();

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
        let mut headers: Vec<(String, String)> = resp_headers
            .into_iter()
            .filter(|(k, _)| !k.eq_ignore_ascii_case("x-bolt-file-path"))
            .collect();

        // Add CORS headers for successful responses (same as handler.rs lines 502-508)
        // Get effective CORS config: route-level first, then global fallback
        // Also check if CORS is skipped via @skip_middleware("cors")
        let skip_cors = route_meta_opt
            .as_ref()
            .map(|m| m.skip.contains("cors"))
            .unwrap_or(false);

        if !skip_cors {
            let cors_cfg = route_meta_opt
                .as_ref()
                .and_then(|m| m.cors_config.as_ref())
                .or(global_cors_config.as_ref());

            if let Some(cfg) = cors_cfg {
                // Use request_origin_for_cors captured earlier (before header_map was moved)
                let request_origin = request_origin_for_cors.as_deref();

                // Use shared CORS function (same as production)
                let mut temp_resp = HttpResponse::Ok().finish();
                let origin_allowed = add_cors_response_headers(
                    &mut temp_resp,
                    request_origin,
                    &cfg.origins,
                    cfg.credentials,
                    &cfg.expose_headers,
                );
                if origin_allowed {
                    // Extract CORS headers from temp response to tuple format
                    for (name, value) in temp_resp.headers().iter() {
                        let name_str = name.as_str();
                        if name_str.starts_with("access-control") || name_str == "vary" {
                            if let Ok(val_str) = value.to_str() {
                                headers.push((name_str.to_string(), val_str.to_string()));
                            }
                        }
                    }
                }
            }
        }

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
            if let Ok(hdict) = hobj.cast::<PyDict>() {
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

                // Get middleware config from route metadata and global CORS config
                let (
                    cors_config,
                    rate_limit_config,
                    handler_id_opt,
                    should_skip_cors,
                    should_skip_compression,
                    global_cors_config,
                ) = Python::attach(
                    |_py| -> (
                        Option<crate::metadata::CorsConfig>,
                        Option<crate::metadata::RateLimitConfig>,
                        Option<usize>,
                        bool,
                        bool,
                        Option<crate::metadata::CorsConfig>,
                    ) {
                        let Some(entry) = registry().get(&app_id) else {
                            return (None, None, None, false, false, None);
                        };
                        let app = entry.read();

                        // Capture global CORS config (same structure as production)
                        let global_cors = app.global_cors_config.clone();

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
                        if let Some(route_match) = app.router.find(&lookup_method, &path) {
                            let handler_id = route_match.handler_id();
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
                                    global_cors,
                                );
                            }
                        }
                        (None, None, None, false, false, global_cors)
                    },
                );

                // Handle CORS preflight - MUST validate origin per RFC 6454
                if is_preflight && !should_skip_cors {
                    // Get effective CORS config: route-level, then global
                    let effective_config = cors_config.as_ref().or(global_cors_config.as_ref());

                    let Some(cors_cfg) = effective_config else {
                        // No CORS configured - reject preflight
                        return Ok(HttpResponse::Forbidden()
                            .content_type("text/plain; charset=utf-8")
                            .body("CORS not configured"));
                    };

                    // Get effective origins (route-level or global)
                    let effective_origins = if !cors_cfg.origins.is_empty() {
                        &cors_cfg.origins
                    } else if let Some(ref global) = global_cors_config {
                        &global.origins
                    } else {
                        &cors_cfg.origins
                    };

                    let is_wildcard =
                        cors_cfg.allow_all_origins || effective_origins.iter().any(|o| o == "*");

                    // Wildcard + credentials is invalid per CORS spec
                    if is_wildcard && cors_cfg.credentials {
                        // Reflect origin instead of using wildcard
                        if let Some(req_origin) = request_origin.as_deref() {
                            let mut response = HttpResponse::NoContent();
                            response.insert_header((ACCESS_CONTROL_ALLOW_ORIGIN, req_origin));
                            response.insert_header((VARY, "Origin"));
                            response.insert_header((ACCESS_CONTROL_ALLOW_CREDENTIALS, "true"));
                            // Use shared helper for preflight headers
                            let mut resp = response.finish();
                            add_preflight_headers_simple(
                                &mut resp,
                                &cors_cfg.methods,
                                &cors_cfg.headers,
                                cors_cfg.max_age as u64,
                            );
                            return Ok(resp);
                        }
                        // No origin header, reject
                        return Ok(HttpResponse::Forbidden().finish());
                    }

                    // Handle wildcard without credentials
                    if is_wildcard {
                        let mut response = HttpResponse::NoContent();
                        response.insert_header((ACCESS_CONTROL_ALLOW_ORIGIN, "*"));
                        let mut resp = response.finish();
                        add_preflight_headers_simple(
                            &mut resp,
                            &cors_cfg.methods,
                            &cors_cfg.headers,
                            cors_cfg.max_age as u64,
                        );
                        return Ok(resp);
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
                    if !effective_origins.iter().any(|o| o == req_origin) {
                        // CRITICAL: Origin not allowed, reject preflight
                        return Ok(HttpResponse::Forbidden()
                            .content_type("text/plain; charset=utf-8")
                            .body("Origin not allowed"));
                    }

                    // Origin validated - add preflight headers
                    let mut response = HttpResponse::NoContent();
                    response.insert_header((ACCESS_CONTROL_ALLOW_ORIGIN, req_origin));
                    response.insert_header((VARY, "Origin"));

                    if cors_cfg.credentials {
                        response.insert_header((ACCESS_CONTROL_ALLOW_CREDENTIALS, "true"));
                    }

                    let mut resp = response.finish();
                    add_preflight_headers_simple(
                        &mut resp,
                        &cors_cfg.methods,
                        &cors_cfg.headers,
                        cors_cfg.max_age as u64,
                    );
                    return Ok(resp);
                }

                // Check rate limiting
                if let (Some(handler_id), Some(rate_cfg)) =
                    (handler_id_opt, rate_limit_config.as_ref())
                {
                    // Convert headers to AHashMap
                    let header_map: ahash::AHashMap<String, String> = headers
                        .iter()
                        .map(|(k, v)| (k.to_lowercase(), v.clone()))
                        .collect();
                    if let Some(response) = crate::middleware::rate_limit::check_rate_limit(
                        handler_id,
                        &header_map,
                        None,
                        rate_cfg,
                        &method,
                        &path,
                    ) {
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
                    Ok((status_code, resp_headers, resp_body)) => {
                        // Use shared response builder (same as production handler.rs)
                        // This ensures consistent header handling, including multiple Set-Cookie
                        let http_response = crate::response_builder::build_response_with_headers(
                            actix_web::http::StatusCode::from_u16(status_code)
                                .unwrap_or(actix_web::http::StatusCode::OK),
                            resp_headers,
                            should_skip_compression,
                            resp_body,
                        );

                        // NOTE: CORS headers are NOT added here - they must be added by handle_test_request_for
                        // to match production behavior in handler.rs. This ensures tests accurately validate
                        // that CORS headers are added at error return points in the request handling code.

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
                .app_data(web::PayloadConfig::new(1 * 1024 * 1024)) // 1MB max payload (matches BOLT_MAX_UPLOAD_SIZE default)
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

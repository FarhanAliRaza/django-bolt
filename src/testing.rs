//! Async testing infrastructure for django-bolt using Actix Web's official test utilities.
//!
//! This module provides testing capabilities that:
//! - Use Actix Web's native test framework (`actix_web::test`)
//! - Run asynchronously in Rust (native async, no blocking)
//! - Reuse production code paths (handle_request, middleware, CORS, etc.)
//! - Support per-instance test apps (no global state conflicts)
//!
//! The test infrastructure mirrors the production server configuration exactly,
//! ensuring tests validate the actual request pipeline.

use actix_web::dev::Service;
use actix_web::http::header::HeaderValue;
use actix_web::middleware::NormalizePath;
use actix_web::{test, web, App, HttpRequest, HttpResponse};
use ahash::AHashMap;
use bytes::Bytes;
use dashmap::DashMap;
use once_cell::sync::OnceCell;
use parking_lot::RwLock;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

use crate::metadata::{CorsConfig, RouteMetadata};
use crate::middleware::compression::CompressionMiddleware;
use crate::middleware::cors::CorsMiddleware;
use crate::router::Router;
use crate::state::{AppState, TASK_LOCALS};
use crate::websocket::WebSocketRouter;

/// One-time initialization flag for async runtime
static ASYNC_RUNTIME_INITIALIZED: std::sync::Once = std::sync::Once::new();

/// Initialize TASK_LOCALS for test environment if not already set.
/// This is required for SSE/streaming responses that use async generators.
fn ensure_task_locals_initialized() {
    use std::sync::mpsc;

    // Only initialize once
    ASYNC_RUNTIME_INITIALIZED.call_once(|| {
        // Initialize pyo3_async_runtimes tokio runtime (like production server)
        let runtime_builder = tokio::runtime::Builder::new_multi_thread();
        pyo3_async_runtimes::tokio::init(runtime_builder);

        // Channel to signal when event loop is ready
        let (tx, rx) = mpsc::channel();

        // Create event loop and start it in background thread
        let loop_obj_opt: Option<Py<PyAny>> = Python::attach(|py| {
            let asyncio = match py.import("asyncio") {
                Ok(m) => m,
                Err(_) => {
                    return None;
                }
            };

            let event_loop = match asyncio.call_method0("new_event_loop") {
                Ok(ev) => ev,
                Err(_) => {
                    return None;
                }
            };

            // Create TaskLocals with the event loop
            match pyo3_async_runtimes::TaskLocals::new(event_loop.clone()).copy_context(py) {
                Ok(locals) => {
                    let _ = TASK_LOCALS.set(locals);
                    Some(event_loop.unbind())
                }
                Err(_) => None,
            }
        });

        // GIL is now released - spawn background thread to run event loop
        if let Some(loop_obj) = loop_obj_opt {
            std::thread::spawn(move || {
                Python::attach(|py| {
                    let asyncio = match py.import("asyncio") {
                        Ok(m) => m,
                        Err(_) => {
                            let _ = tx.send(());
                            return;
                        }
                    };
                    let ev = loop_obj.bind(py);
                    let _ = asyncio.call_method1("set_event_loop", (ev.as_any(),));

                    // Signal that we're about to run forever
                    let _ = tx.send(());
                    let _ = ev.call_method0("run_forever");
                });
            });

            // Wait for the background thread to signal it's ready
            let _ = rx.recv_timeout(std::time::Duration::from_secs(5));
            // Give it a tiny bit more time to actually enter run_forever
            std::thread::sleep(std::time::Duration::from_millis(10));
        }
    });
}

/// Test application state stored per instance
pub struct TestAppState {
    pub router: Arc<Router>,
    pub websocket_router: Arc<WebSocketRouter>,
    pub route_metadata: Arc<AHashMap<usize, RouteMetadata>>,
    pub dispatch: Py<PyAny>,
    pub global_cors_config: Option<CorsConfig>,
    pub debug: bool,
    pub max_payload_size: usize,
}

/// Registry for test app instances
static TEST_REGISTRY: OnceCell<DashMap<u64, Arc<RwLock<TestAppState>>>> = OnceCell::new();
static TEST_ID_GEN: AtomicU64 = AtomicU64::new(1);

fn registry() -> &'static DashMap<u64, Arc<RwLock<TestAppState>>> {
    TEST_REGISTRY.get_or_init(DashMap::new)
}

/// Parse CORS config from a Python dict (matches production server parsing)
fn parse_cors_config_from_dict(dict: &Bound<'_, PyDict>) -> PyResult<CorsConfig> {
    use ahash::AHashSet;

    let origins: Vec<String> = dict
        .get_item("origins")?
        .map(|v| v.extract().unwrap_or_default())
        .unwrap_or_default();

    let origin_set: AHashSet<String> = origins.iter().cloned().collect();
    let allow_all_origins = origins.iter().any(|o| o == "*");

    let credentials: bool = dict
        .get_item("credentials")?
        .map(|v| v.extract().unwrap_or(false))
        .unwrap_or(false);

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

    let expose_headers: Vec<String> = dict
        .get_item("expose_headers")?
        .map(|v| v.extract().unwrap_or_default())
        .unwrap_or_default();

    let max_age: u32 = dict
        .get_item("max_age")?
        .map(|v| v.extract().unwrap_or(86400))
        .unwrap_or(86400);

    // Build pre-computed strings and cached HeaderValues
    let methods_str = methods.join(", ");
    let headers_str = headers.join(", ");
    let expose_headers_str = expose_headers.join(", ");
    let max_age_str = max_age.to_string();

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
        origin_regexes: vec![],
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

/// Create a test app instance and return its ID
#[pyfunction]
#[pyo3(signature = (dispatch, debug, cors_config=None))]
pub fn create_test_app(
    py: Python<'_>,
    dispatch: Py<PyAny>,
    debug: bool,
    cors_config: Option<&Bound<'_, PyDict>>,
) -> PyResult<u64> {
    let global_cors_config = if let Some(cors_dict) = cors_config {
        Some(parse_cors_config_from_dict(cors_dict)?)
    } else {
        None
    };

    // Read max payload size from Django settings (same as production server)
    // Default to 10MB for tests to handle large file uploads
    let max_payload_size: usize = (|| -> PyResult<usize> {
        let django_conf = py.import("django.conf")?;
        let settings = django_conf.getattr("settings")?;
        settings.getattr("BOLT_MAX_UPLOAD_SIZE")?.extract::<usize>()
    })()
    .unwrap_or(10 * 1024 * 1024); // Default to 10MB for tests

    let app = TestAppState {
        router: Arc::new(Router::new()),
        websocket_router: Arc::new(WebSocketRouter::new()),
        route_metadata: Arc::new(AHashMap::new()),
        dispatch: dispatch.clone_ref(py),
        global_cors_config,
        debug,
        max_payload_size,
    };

    let id = TEST_ID_GEN.fetch_add(1, Ordering::Relaxed);
    registry().insert(id, Arc::new(RwLock::new(app)));
    Ok(id)
}

/// Destroy a test app instance
#[pyfunction]
pub fn destroy_test_app(app_id: u64) -> PyResult<()> {
    registry().remove(&app_id);
    Ok(())
}

/// Register HTTP routes for a test app
#[pyfunction]
pub fn register_test_routes(
    _py: Python<'_>,
    app_id: u64,
    routes: Vec<(String, String, usize, Py<PyAny>)>,
) -> PyResult<()> {
    let entry = registry()
        .get(&app_id)
        .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("Invalid test app id"))?;

    let mut app = entry.write();

    // Create a new router with the routes
    let mut router = Router::new();
    for (method, path, handler_id, handler) in routes {
        router.register(&method, &path, handler_id, handler)?;
    }
    app.router = Arc::new(router);
    Ok(())
}

/// Register WebSocket routes for a test app
#[pyfunction]
pub fn register_test_websocket_routes(
    _py: Python<'_>,
    app_id: u64,
    routes: Vec<(String, usize, Py<PyAny>, Option<Py<PyAny>>)>,
) -> PyResult<()> {
    let entry = registry()
        .get(&app_id)
        .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("Invalid test app id"))?;

    let mut app = entry.write();

    let mut ws_router = WebSocketRouter::new();
    for (path, handler_id, handler, injector) in routes {
        ws_router.register(&path, handler_id, handler, injector)?;
    }
    app.websocket_router = Arc::new(ws_router);
    Ok(())
}

/// Register middleware metadata for a test app
#[pyfunction]
pub fn register_test_middleware_metadata(
    py: Python<'_>,
    app_id: u64,
    metadata: Vec<(usize, Py<PyAny>)>,
) -> PyResult<()> {
    let entry = registry()
        .get(&app_id)
        .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("Invalid test app id"))?;

    let mut app = entry.write();

    let mut parsed_metadata: AHashMap<usize, RouteMetadata> = AHashMap::new();

    for (handler_id, meta) in metadata {
        if let Ok(py_dict) = meta.bind(py).cast::<PyDict>() {
            if let Ok(parsed) = RouteMetadata::from_python(py_dict, py) {
                // Inject global CORS config if route doesn't have explicit config
                let mut route_meta = parsed;
                if route_meta.cors_config.is_none() && !route_meta.skip.contains("cors") {
                    route_meta.cors_config = app.global_cors_config.clone();
                }
                parsed_metadata.insert(handler_id, route_meta);
            }
        }
    }

    app.route_metadata = Arc::new(parsed_metadata);
    Ok(())
}

/// Handle a test request using Actix's native test infrastructure.
///
/// This function:
/// 1. Creates an Actix test service matching production configuration
/// 2. Executes the request using a local tokio runtime
/// 3. Returns the response as (status_code, headers, body)
///
/// The request flows through the exact same code path as production:
/// - NormalizePath middleware
/// - CorsMiddleware
/// - CompressionMiddleware
/// - handle_request handler
///
/// Note: This is a synchronous function because Actix test utilities are !Send
/// and cannot be used with pyo3_async_runtimes::future_into_py. We create
/// a local tokio runtime for each request instead.
#[pyfunction]
pub fn test_request(
    _py: Python<'_>,
    app_id: u64,
    method: String,
    path: String,
    headers: Vec<(String, String)>,
    body: Vec<u8>,
    query_string: Option<String>,
) -> PyResult<(u16, Vec<(String, String)>, Vec<u8>)> {
    // Ensure TASK_LOCALS is initialized for SSE/streaming support
    ensure_task_locals_initialized();

    // Get test app state
    let entry = registry()
        .get(&app_id)
        .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("Invalid test app id"))?;

    let app_state = entry.clone();
    drop(entry); // Release DashMap lock

    // Use the global runtime (initialized by pyo3_async_runtimes::tokio::init())
    // This ensures handler execution and streaming use the same runtime context
    let runtime_handle = pyo3_async_runtimes::tokio::get_runtime();

    runtime_handle.block_on(async {
        // Read test app state
        let (router, route_metadata, dispatch, global_cors_config, debug, max_payload_size) = {
            let state = app_state.read();
            (
                state.router.clone(),
                state.route_metadata.clone(),
                Python::attach(|py| state.dispatch.clone_ref(py)),
                state.global_cors_config.clone(),
                state.debug,
                state.max_payload_size,
            )
        };

        // Build AppState matching production
        // Include router and route_metadata so CorsMiddleware can find route-level CORS config
        let app_state_arc = Arc::new(AppState {
            dispatch,
            debug,
            max_header_size: 8192,
            global_cors_config: global_cors_config.clone(),
            cors_origin_regexes: vec![],
            global_compression_config: None,
            router: Some(router.clone()),
            route_metadata: Some(route_metadata.clone()),
        });

        // Clone the Arc values for the handler closure
        let router_for_handler = router.clone();
        let metadata_for_handler = route_metadata.clone();

        // Create the test handler that uses per-instance state
        let handler = move |req: HttpRequest, body: web::Bytes| {
            let router = router_for_handler.clone();
            let metadata = metadata_for_handler.clone();

            async move { handle_test_request_internal(req, body, router, metadata).await }
        };

        // Create Actix test service with production middleware stack
        let app = test::init_service(
            App::new()
                .app_data(web::Data::new(app_state_arc.clone()))
                .app_data(web::PayloadConfig::new(max_payload_size))
                .wrap(NormalizePath::trim())
                .wrap(CorsMiddleware::new())
                .wrap(CompressionMiddleware::new())
                .default_service(web::to(handler)),
        )
        .await;

        // Build full URI
        let uri = if let Some(qs) = query_string {
            format!("{}?{}", path, qs)
        } else {
            path.clone()
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

        // Execute request
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

        // Use test::read_body which handles various body types including Encoder
        let resp_body = test::read_body(response).await.to_vec();

        Ok((status, resp_headers, resp_body))
    })
}

/// Internal handler for test requests that uses per-instance state.
/// This mirrors the production `handle_request` but uses the provided router and metadata.
async fn handle_test_request_internal(
    req: HttpRequest,
    body: web::Bytes,
    router: Arc<Router>,
    route_metadata: Arc<AHashMap<usize, RouteMetadata>>,
) -> HttpResponse {
    use crate::handler::{extract_headers, handle_python_error};
    use crate::middleware;
    use crate::middleware::auth::populate_auth_context;
    use crate::request::PyRequest;
    use crate::response_builder;
    use crate::responses;
    use crate::router::parse_query_string;
    use crate::validation::{parse_cookies_inline, validate_auth_and_guards, AuthGuardResult};
    use actix_web::http::StatusCode;
    use pyo3::types::{PyBytes, PyTuple};

    let method = req.method().as_str();
    let path = req.path();

    // Get state from app data
    let state = match req.app_data::<web::Data<Arc<AppState>>>() {
        Some(s) => s.get_ref().clone(),
        None => {
            return HttpResponse::InternalServerError().body("App state not found");
        }
    };

    // Find route
    let (route_handler, path_params, handler_id) = {
        if let Some(route_match) = router.find(method, path) {
            let handler_id = route_match.handler_id();
            let handler = Python::attach(|py| route_match.route().handler.clone_ref(py));
            let path_params = route_match.path_params();
            (handler, path_params, handler_id)
        } else {
            // Automatic OPTIONS handling
            if method == "OPTIONS" {
                let available_methods = router.find_all_methods(path);
                if !available_methods.is_empty() {
                    let allow_header = available_methods.join(", ");
                    return HttpResponse::NoContent()
                        .insert_header(("Allow", allow_header))
                        .insert_header(("Content-Type", "application/json"))
                        .finish();
                }

                // Handle OPTIONS preflight for non-existent routes
                if state.global_cors_config.is_some() {
                    return HttpResponse::NoContent().finish();
                }
            }

            return responses::error_404();
        }
    };

    // Get route metadata
    let route_meta = route_metadata.get(&handler_id).cloned();

    // Parse query string
    let needs_query = route_meta.as_ref().map(|m| m.needs_query).unwrap_or(true);
    let query_params = if needs_query {
        if let Some(q) = req.uri().query() {
            parse_query_string(q)
        } else {
            AHashMap::new()
        }
    } else {
        AHashMap::new()
    };

    // Extract headers
    let needs_headers = route_meta.as_ref().map(|m| m.needs_headers).unwrap_or(true);
    let skip_cors = route_meta
        .as_ref()
        .map(|m| m.skip.contains("cors"))
        .unwrap_or(false);
    let skip_compression = route_meta
        .as_ref()
        .map(|m| m.skip.contains("compression"))
        .unwrap_or(false);

    let headers = match extract_headers(&req, state.max_header_size) {
        Ok(h) => h,
        Err(response) => return response,
    };

    let peer_addr = req.peer_addr().map(|addr| addr.ip().to_string());

    // Rate limiting
    if let Some(ref meta) = route_meta {
        if let Some(ref rate_config) = meta.rate_limit_config {
            if let Some(response) = middleware::rate_limit::check_rate_limit(
                handler_id,
                &headers,
                peer_addr.as_deref(),
                rate_config,
                method,
                path,
            ) {
                return response;
            }
        }
    }

    // Auth and guards
    let auth_ctx = if let Some(ref meta) = route_meta {
        match validate_auth_and_guards(&headers, &meta.auth_backends, &meta.guards) {
            AuthGuardResult::Allow(ctx) => ctx,
            AuthGuardResult::Unauthorized => return responses::error_401(),
            AuthGuardResult::Forbidden => return responses::error_403(),
        }
    } else {
        None
    };

    // Cookies
    let needs_cookies = route_meta.as_ref().map(|m| m.needs_cookies).unwrap_or(true);
    let cookies = if needs_cookies {
        parse_cookies_inline(headers.get("cookie").map(|s| s.as_str()))
    } else {
        AHashMap::new()
    };

    let is_head_request = method == "HEAD";

    // Execute handler using run_coroutine_threadsafe to submit to background event loop
    // This reuses the global event loop instead of creating one per request via asyncio.run()
    let result_obj = match Python::attach(|py| -> PyResult<Py<PyAny>> {
        let dispatch = state.dispatch.clone_ref(py);
        let handler = route_handler.clone_ref(py);

        let context = if let Some(ref auth) = auth_ctx {
            let ctx_dict = PyDict::new(py);
            let ctx_py = ctx_dict.unbind();
            populate_auth_context(&ctx_py, auth, py);
            Some(ctx_py)
        } else {
            None
        };

        let headers_for_python = if needs_headers {
            headers.clone()
        } else {
            AHashMap::new()
        };

        let request = PyRequest {
            method: method.to_string(),
            path: path.to_string(),
            body: body.to_vec(),
            path_params,
            query_params,
            headers: headers_for_python,
            cookies,
            context,
            user: None,
            state: PyDict::new(py).unbind(),
        };
        let request_obj = Py::new(py, request)?;

        // Get the event loop from TASK_LOCALS (initialized by ensure_task_locals_initialized)
        let locals = TASK_LOCALS.get().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("Asyncio loop not initialized")
        })?;
        let event_loop = locals.event_loop(py);

        // Call dispatch to get a coroutine
        let coroutine = dispatch.call1(py, (handler, request_obj, handler_id))?;

        // Submit coroutine to background event loop using run_coroutine_threadsafe
        // This returns a concurrent.futures.Future that we can wait on
        let asyncio = py.import("asyncio")?;
        let future = asyncio.call_method1("run_coroutine_threadsafe", (coroutine, event_loop))?;

        // Wait for the result (releases GIL while waiting)
        let result = future.call_method0("result")?;
        Ok(result.unbind())
    }) {
        Ok(r) => r,
        Err(e) => {
            return Python::attach(|py| handle_python_error(py, e, path, method, state.debug));
        }
    };

    // Process the result
    match Ok::<_, PyErr>(result_obj) {
        Ok(result_obj) => {
            // Fast-path: tuple extraction
            let fast_tuple: Option<(u16, Vec<(String, String)>, Vec<u8>)> = Python::attach(|py| {
                let obj = result_obj.bind(py);
                let tuple = obj.cast::<PyTuple>().ok()?;
                if tuple.len() != 3 {
                    return None;
                }

                let status_code: u16 = tuple.get_item(0).ok()?.extract::<u16>().ok()?;
                let resp_headers: Vec<(String, String)> = tuple
                    .get_item(1)
                    .ok()?
                    .extract::<Vec<(String, String)>>()
                    .ok()?;
                let body_obj = tuple.get_item(2).ok()?;
                let pybytes = body_obj.cast::<PyBytes>().ok()?;
                let body_vec = pybytes.as_bytes().to_vec();
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
                    return crate::handler::build_file_response(
                        &fpath,
                        status,
                        headers,
                        skip_compression,
                        is_head_request,
                    )
                    .await;
                } else {
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

                    if skip_cors {
                        response
                            .headers_mut()
                            .insert("x-bolt-skip-cors".parse().unwrap(), "true".parse().unwrap());
                    }

                    return response;
                }
            }

            // Fallback: streaming response handling
            if let Ok((status_code, resp_headers, body_bytes)) =
                Python::attach(|py| result_obj.extract::<(u16, Vec<(String, String)>, Vec<u8>)>(py))
            {
                let status = StatusCode::from_u16(status_code).unwrap_or(StatusCode::OK);
                let mut headers: Vec<(String, String)> = Vec::with_capacity(resp_headers.len());

                for (k, v) in resp_headers {
                    if !k.eq_ignore_ascii_case("x-bolt-file-path") {
                        headers.push((k, v));
                    }
                }

                let mut builder = HttpResponse::build(status);
                for (k, v) in headers {
                    builder.append_header((k, v));
                }

                if skip_compression {
                    builder.append_header(("Content-Encoding", "identity"));
                }
                if skip_cors {
                    builder.append_header(("x-bolt-skip-cors", "true"));
                }

                let response_body = if is_head_request {
                    Vec::new()
                } else {
                    body_bytes
                };

                return builder.body(response_body);
            }

            // Streaming response path
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
                            if let (Ok(ks), Ok(vs)) = (k.extract::<String>(), v.extract::<String>())
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

                // For tests, collect streaming content synchronously instead of async streaming
                // This avoids issues with event loop contexts
                let collected_body = Python::attach(|py| -> Vec<u8> {
                    let mut chunks: Vec<u8> = Vec::new();
                    let content = content_obj.bind(py);

                    if is_async_generator {
                        // For async generators, use asyncio to collect
                        let asyncio = match py.import("asyncio") {
                            Ok(m) => m,
                            Err(_) => return chunks,
                        };

                        // Create a coroutine that collects all items
                        let locals = PyDict::new(py);
                        let code = pyo3::ffi::c_str!(
                            r#"
async def _collect_async_gen(gen):
    result = []
    async for item in gen:
        if isinstance(item, bytes):
            result.append(item)
        elif isinstance(item, bytearray):
            result.append(bytes(item))
        elif isinstance(item, memoryview):
            result.append(bytes(item))
        elif isinstance(item, str):
            result.append(item.encode('utf-8'))
        else:
            result.append(str(item).encode('utf-8'))
    return b''.join(result)
"#
                        );
                        if py.run(code, None, Some(&locals)).is_ok() {
                            if let Ok(Some(collect_fn)) = locals.get_item("_collect_async_gen") {
                                if let Ok(coro) = collect_fn.call1((content,)) {
                                    if let Ok(result) = asyncio.call_method1("run", (coro,)) {
                                        if let Ok(bytes) = result.extract::<Vec<u8>>() {
                                            chunks = bytes;
                                        }
                                    }
                                }
                            }
                        }
                    } else {
                        // Sync generator - iterate directly
                        if let Ok(iter) = content.try_iter() {
                            for item in iter {
                                if let Ok(item) = item {
                                    if let Ok(bytes) = item.extract::<Vec<u8>>() {
                                        chunks.extend(bytes);
                                    } else if let Ok(s) = item.extract::<String>() {
                                        chunks.extend(s.as_bytes());
                                    }
                                }
                            }
                        }
                    }

                    chunks
                });

                if media_type == "text/event-stream" {
                    if is_head_request {
                        let mut builder =
                            response_builder::build_sse_response(status, headers, skip_compression);
                        let mut response = builder.body(Vec::<u8>::new());
                        if skip_cors {
                            response.headers_mut().insert(
                                "x-bolt-skip-cors".parse().unwrap(),
                                "true".parse().unwrap(),
                            );
                        }
                        return response;
                    }

                    let mut builder =
                        response_builder::build_sse_response(status, headers, skip_compression);
                    let mut response = builder.body(collected_body);
                    if skip_cors {
                        response
                            .headers_mut()
                            .insert("x-bolt-skip-cors".parse().unwrap(), "true".parse().unwrap());
                    }
                    return response;
                } else {
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

                    return builder.body(collected_body);
                }
            }

            // Unsupported response type
            Python::attach(|py| {
                crate::error::build_error_response(
                    py,
                    500,
                    "Handler returned unsupported response type".to_string(),
                    vec![],
                    None,
                    state.debug,
                )
            })
        }
        Err(e) => Python::attach(|py| handle_python_error(py, e, path, method, state.debug)),
    }
}

/// Handle WebSocket test request - validates and routes WebSocket connections
#[pyfunction]
pub fn handle_test_websocket(
    py: Python<'_>,
    app_id: u64,
    path: String,
    headers: Vec<(String, String)>,
    query_string: Option<String>,
) -> PyResult<(bool, usize, Py<PyAny>, Py<PyAny>, Py<PyAny>)> {
    use crate::middleware::auth::authenticate;
    use crate::permissions::{evaluate_guards, GuardResult};

    let entry = registry()
        .get(&app_id)
        .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("Invalid test app id"))?;

    let app = entry.read();

    // Convert headers to map
    let mut header_map: AHashMap<String, String> = AHashMap::with_capacity(headers.len());
    for (name, value) in headers.iter() {
        header_map.insert(name.to_lowercase(), value.clone());
    }

    // Origin validation for WebSocket
    let origin = header_map.get("origin");
    if let Some(origin_value) = origin {
        let origin_allowed = if let Some(ref cors_config) = app.global_cors_config {
            if cors_config.allow_all_origins {
                true
            } else {
                cors_config.origin_set.contains(origin_value)
                    || cors_config
                        .compiled_origin_regexes
                        .iter()
                        .any(|re| re.is_match(origin_value))
            }
        } else {
            false // No CORS = deny cross-origin
        };

        if !origin_allowed {
            return Err(pyo3::exceptions::PyPermissionError::new_err(format!(
                "Origin not allowed: {}",
                origin_value
            )));
        }
    }

    // Normalize path
    let normalized_path = if path.len() > 1 && path.ends_with('/') {
        &path[..path.len() - 1]
    } else {
        &path
    };

    // Find WebSocket route
    let (route, path_params) = match app.websocket_router.find(normalized_path) {
        Some((route, params)) => (route, params),
        None => return Ok((false, 0, py.None(), py.None(), py.None())),
    };

    let handler_id = route.handler_id;
    let handler = route.handler.clone_ref(py);

    // Rate limiting for WebSocket
    if let Some(route_meta) = app.route_metadata.get(&handler_id) {
        if let Some(ref rate_config) = route_meta.rate_limit_config {
            if crate::middleware::rate_limit::check_rate_limit(
                handler_id,
                &header_map,
                Some("127.0.0.1"),
                rate_config,
                "GET",
                &path,
            )
            .is_some()
            {
                return Err(pyo3::exceptions::PyPermissionError::new_err(
                    "Rate limit exceeded",
                ));
            }
        }
    }

    // Auth and guards for WebSocket
    if let Some(route_meta) = app.route_metadata.get(&handler_id) {
        let auth_ctx = if !route_meta.auth_backends.is_empty() {
            authenticate(&header_map, &route_meta.auth_backends)
        } else {
            None
        };

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

    // Build scope dict
    let scope_dict = pyo3::types::PyDict::new(py);
    scope_dict.set_item("type", "websocket")?;
    scope_dict.set_item("path", &path)?;

    let qs_bytes = query_string.as_ref().map(|s| s.as_bytes()).unwrap_or(b"");
    scope_dict.set_item("query_string", pyo3::types::PyBytes::new(py, qs_bytes))?;

    let headers_dict = pyo3::types::PyDict::new(py);
    for (k, v) in headers.iter() {
        headers_dict.set_item(k.to_lowercase(), v)?;
    }
    scope_dict.set_item("headers", headers_dict)?;
    scope_dict.set_item("path_params", &path_params_dict)?;

    // Parse cookies
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

    let client_tuple = pyo3::types::PyTuple::new(py, &["127.0.0.1", "12345"])?;
    scope_dict.set_item("client", client_tuple)?;

    // Add auth context if present
    if let Some(route_meta) = app.route_metadata.get(&handler_id) {
        let auth_ctx = if !route_meta.auth_backends.is_empty() {
            authenticate(&header_map, &route_meta.auth_backends)
        } else {
            None
        };

        if let Some(ref auth) = auth_ctx {
            let ctx_dict = pyo3::types::PyDict::new(py);
            crate::middleware::auth::populate_auth_context(&ctx_dict.clone().unbind(), auth, py);
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

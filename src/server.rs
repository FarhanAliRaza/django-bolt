use actix_http::KeepAlive;
use actix_web::{self as aw, middleware::Compress, web, App, HttpServer};
use ahash::AHashMap;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use socket2::{Domain, Protocol, Socket, Type};
use std::net::{IpAddr, SocketAddr};
use std::sync::Arc;

use crate::handler::handle_request;
use crate::metadata::RouteMetadata;
use crate::router::Router;
use crate::state::{AppState, GLOBAL_ROUTER, MIDDLEWARE_METADATA, ROUTE_METADATA, TASK_LOCALS, RESPONSE_CHANNELS, HANDLER_MAP, ResponseChannels};

#[pyfunction]
pub fn register_routes(
    py: Python<'_>,
    routes: Vec<(String, String, usize, Py<PyAny>)>,
) -> PyResult<()> {
    let mut router = Router::new();
    let mut handler_map = AHashMap::new();

    for (method, path, handler_id, handler) in routes {
        router.register(&method, &path, handler_id, handler.clone_ref(py))?;
        // Build handler map for Python event loop worker
        handler_map.insert(handler_id, handler);
    }

    GLOBAL_ROUTER
        .set(Arc::new(router))
        .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Router already initialized"))?;

    HANDLER_MAP
        .set(Arc::new(handler_map))
        .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Handler map already initialized"))?;

    Ok(())
}

#[pyfunction]
pub fn register_middleware_metadata(
    py: Python<'_>,
    metadata: Vec<(usize, Py<PyAny>)>,
) -> PyResult<()> {
    let mut metadata_map = AHashMap::new();
    let mut parsed_metadata_map = AHashMap::new();

    for (handler_id, meta) in metadata {
        // Store raw Python metadata for backward compatibility
        metadata_map.insert(handler_id, meta.clone_ref(py));

        // Parse into typed Rust metadata
        if let Ok(py_dict) = meta.bind(py).downcast::<PyDict>() {
            match RouteMetadata::from_python(py_dict, py) {
                Ok(parsed) => {
                    parsed_metadata_map.insert(handler_id, parsed);
                }
                Err(e) => {
                    eprintln!("Warning: Failed to parse metadata for handler {}: {}", handler_id, e);
                }
            }
        }
    }

    MIDDLEWARE_METADATA
        .set(Arc::new(metadata_map))
        .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Middleware metadata already initialized"))?;

    ROUTE_METADATA
        .set(Arc::new(parsed_metadata_map))
        .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Route metadata already initialized"))?;

    Ok(())
}

#[pyfunction]
pub fn start_server_async(
    py: Python<'_>,
    dispatch: Py<PyAny>,
    host: String,
    port: u16,
    compression_config: Option<Py<PyAny>>,
) -> PyResult<()> {
    if GLOBAL_ROUTER.get().is_none() {
        return Err(pyo3::exceptions::PyRuntimeError::new_err("Routes not registered"));
    }

    pyo3_async_runtimes::tokio::init(tokio::runtime::Builder::new_multi_thread());

    let loop_obj: Py<PyAny> = {
        let asyncio = py.import("asyncio")?;
        let ev = asyncio.call_method0("new_event_loop")?;
        let locals = pyo3_async_runtimes::TaskLocals::new(ev.clone()).copy_context(py)?;
        let _ = TASK_LOCALS.set(locals);
        ev.unbind().into()
    };
    std::thread::spawn(move || {
        Python::attach(|py| {
            let asyncio = py.import("asyncio").expect("import asyncio");
            let ev = loop_obj.bind(py);
            let _ = asyncio.call_method1("set_event_loop", (ev.as_any(),));
            let _ = ev.call_method0("run_forever");
        });
    });

    // Get configuration from Django settings ONCE at startup (not per-request)
    let (debug, max_header_size, cors_allowed_origins) = Python::attach(|py| {
        let debug = (|| -> PyResult<bool> {
            let django_conf = py.import("django.conf")?;
            let settings = django_conf.getattr("settings")?;
            settings.getattr("DEBUG")?.extract::<bool>()
        })().unwrap_or(false);

        let max_header_size = (|| -> PyResult<usize> {
            let django_conf = py.import("django.conf")?;
            let settings = django_conf.getattr("settings")?;
            settings.getattr("BOLT_MAX_HEADER_SIZE")?.extract::<usize>()
        })().unwrap_or(8192); // Default 8KB

        let cors_allowed_origins = (|| -> PyResult<Vec<String>> {
            let django_conf = py.import("django.conf")?;
            let settings = django_conf.getattr("settings")?;
            settings.getattr("BOLT_CORS_ALLOWED_ORIGINS")?.extract::<Vec<String>>()
        })().unwrap_or_else(|_| vec![]); // Default empty (secure)

        (debug, max_header_size, cors_allowed_origins)
    });

    // Initialize response channels for Phase 3
    let response_channels: ResponseChannels = Arc::new(std::sync::Mutex::new(AHashMap::new()));
    RESPONSE_CHANNELS
        .set(response_channels.clone())
        .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Response channels already initialized"))?;

    // Create Python asyncio.Queue for event loop worker and get submit function
    let (python_queue, send_response_fn, submit_fn) = Python::attach(|py| -> PyResult<_> {
        let asyncio = py.import("asyncio")?;
        let queue = asyncio.call_method0("Queue")?;

        // Get send_response function from _core module
        let core_module = py.import("django_bolt._core")?;
        let send_response = core_module.getattr("send_response")?;

        // Get submit_from_rust function for thread-safe queue submission
        let worker_module = py.import("django_bolt.event_loop_worker")?;
        let submit_from_rust = worker_module.getattr("submit_from_rust")?;

        Ok((queue.unbind(), send_response.unbind(), submit_from_rust.unbind()))
    })?;

    // Start Python event loop worker thread
    let queue_clone = Python::attach(|py| python_queue.clone_ref(py));
    let dispatch_clone = Python::attach(|py| dispatch.clone_ref(py));
    let handler_map = HANDLER_MAP.get().expect("Handler map not initialized").clone();

    std::thread::spawn(move || {
        Python::attach(|py| {
            let worker_module = py.import("django_bolt.event_loop_worker")
                .expect("Failed to import event_loop_worker");

            let start_fn = worker_module.getattr("start_event_loop_worker")
                .expect("Failed to get start_event_loop_worker");

            // Convert handler_map to Python dict
            let py_handler_map = pyo3::types::PyDict::new(py);
            for (handler_id, handler) in handler_map.as_ref() {
                let _ = py_handler_map.set_item(*handler_id, handler.bind(py));
            }

            // Start worker (blocks in this thread)
            if let Err(e) = start_fn.call1((
                queue_clone.bind(py),
                send_response_fn.bind(py),
                py_handler_map,
                dispatch_clone.bind(py),
            )) {
                eprintln!("[django-bolt] ERROR: Event loop worker failed: {}", e);
                e.restore(py);
                if let Some(traceback) = PyErr::take(py) {
                    eprintln!("[django-bolt] Traceback: {}", traceback);
                }
            }
        });
    });

    let app_state = Arc::new(AppState {
        dispatch: dispatch.into(),
        debug,
        max_header_size,
        cors_allowed_origins,
        python_queue: Some(python_queue),
    });

    // Note: compression_config is provided but not used yet in Rust
    // Actix's Compress middleware is always enabled and automatically negotiates
    // with client based on Accept-Encoding header. It only compresses when:
    // 1. Client sends Accept-Encoding: gzip, br, etc.
    // 2. Response is large enough (default 1KB threshold)
    // 3. Content-Type is compressible
    //
    // Future: Use compression_config to configure levels, algorithms, etc.
    let _use_compression = compression_config.is_some();

    py.detach(|| {
        aw::rt::System::new()
            .block_on(async move {
                let workers: usize = std::env::var("DJANGO_BOLT_WORKERS")
                    .ok()
                    .and_then(|s| s.parse::<usize>().ok())
                    .filter(|&w| w >= 1)
                    .unwrap_or(2);
                {
                    let server = HttpServer::new(move || {
                        App::new()
                            .app_data(web::Data::new(app_state.clone()))
                            .wrap(Compress::default())  // Always enabled, client-negotiated
                            .default_service(web::route().to(handle_request))
                    })
                    .keep_alive(KeepAlive::Os)
                    .client_request_timeout(std::time::Duration::from_secs(0))
                    .workers(workers);

                    let use_reuse_port = std::env::var("DJANGO_BOLT_REUSE_PORT")
                        .ok()
                        .map(|v| v == "1" || v.eq_ignore_ascii_case("true"))
                        .unwrap_or(false);

                    if use_reuse_port {
                        let ip: IpAddr = host.parse().unwrap_or(IpAddr::from([0, 0, 0, 0]));
                        let domain = match ip { IpAddr::V4(_) => Domain::IPV4, IpAddr::V6(_) => Domain::IPV6 };
                        let socket = Socket::new(domain, Type::STREAM, Some(Protocol::TCP))
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
                        socket.set_reuse_address(true)
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
                        #[cfg(not(target_os = "windows"))]
                        socket.set_reuse_port(true)
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
                        let addr = SocketAddr::new(ip, port);
                        socket.bind(&addr.into())
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
                        socket.listen(1024)
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
                        let listener: std::net::TcpListener = socket.into();
                        listener.set_nonblocking(true)
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
                        server.listen(listener)
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?
                            .run().await
                    } else {
                        server.bind((host.as_str(), port))
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?
                            .run().await
                    }
                }
            })
            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, format!("{:?}", e)))
    })
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Server error: {}", e)))?;

    Ok(())
}



use actix_http::KeepAlive;
use actix_web::{self as aw, middleware::Compress, web, App, HttpServer};
use ahash::AHashMap;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use socket2::{Domain, Protocol, Socket, Type};
use std::net::{IpAddr, SocketAddr};
use std::sync::Arc;

use crate::handler::handle_request;
use crate::metadata::{CorsConfig, RouteMetadata};
use crate::router::Router;
use crate::state::{AppState, GLOBAL_ROUTER, ROUTE_METADATA, ROUTE_METADATA_TEMP, TASK_LOCALS};

#[pyfunction]
pub fn register_routes(
    _py: Python<'_>,
    routes: Vec<(String, String, usize, Py<PyAny>)>,
) -> PyResult<()> {
    let mut router = Router::new();
    for (method, path, handler_id, handler) in routes {
        router.register(&method, &path, handler_id, handler.into())?;
    }
    GLOBAL_ROUTER
        .set(Arc::new(router))
        .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Router already initialized"))?;
    Ok(())
}

#[pyfunction]
pub fn register_middleware_metadata(
    py: Python<'_>,
    metadata: Vec<(usize, Py<PyAny>)>,
) -> PyResult<()> {
    let mut parsed_metadata_map = AHashMap::new();

    for (handler_id, meta) in metadata {
        // Parse Python metadata into typed Rust metadata
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

    ROUTE_METADATA_TEMP
        .set(parsed_metadata_map)
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
    let (debug, max_header_size, cors_config_data) = Python::attach(|py| {
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

        // Read django-cors-headers compatible CORS settings
        let cors_data = (|| -> PyResult<(Vec<String>, Vec<String>, bool, bool, Option<Vec<String>>, Option<Vec<String>>, Option<Vec<String>>, Option<u32>)> {
            let django_conf = py.import("django.conf")?;
            let settings = django_conf.getattr("settings")?;

            let origins = settings.getattr("CORS_ALLOWED_ORIGINS")
                .and_then(|o| o.extract::<Vec<String>>())
                .unwrap_or_else(|_| vec![]);

            let origin_regexes = settings.getattr("CORS_ALLOWED_ORIGIN_REGEXES")
                .and_then(|r| r.extract::<Vec<String>>())
                .unwrap_or_else(|_| vec![]);

            let allow_all = settings.getattr("CORS_ALLOW_ALL_ORIGINS")
                .and_then(|a| a.extract::<bool>())
                .unwrap_or(false);

            let credentials = settings.getattr("CORS_ALLOW_CREDENTIALS")
                .and_then(|c| c.extract::<bool>())
                .unwrap_or(false);

            let methods = settings.getattr("CORS_ALLOW_METHODS")
                .and_then(|m| m.extract::<Vec<String>>())
                .ok();

            let headers = settings.getattr("CORS_ALLOW_HEADERS")
                .and_then(|h| h.extract::<Vec<String>>())
                .ok();

            let expose_headers = settings.getattr("CORS_EXPOSE_HEADERS")
                .and_then(|e| e.extract::<Vec<String>>())
                .ok();

            let max_age = settings.getattr("CORS_PREFLIGHT_MAX_AGE")
                .and_then(|a| a.extract::<u32>())
                .ok();

            Ok((origins, origin_regexes, allow_all, credentials, methods, headers, expose_headers, max_age))
        })().unwrap_or_else(|_| (vec![], vec![], false, false, None, None, None, None));

        (debug, max_header_size, cors_data)
    });

    // Unpack CORS configuration data
    let (origins, origin_regex_patterns, allow_all, credentials, methods, headers, expose_headers, max_age) = cors_config_data;

    // Validate CORS configuration: wildcard + credentials is invalid per spec
    if allow_all && credentials {
        eprintln!("[django-bolt] Warning: CORS_ALLOW_ALL_ORIGINS=True with CORS_ALLOW_CREDENTIALS=True is invalid.");
        eprintln!("[django-bolt] Per CORS spec, wildcard origin (*) cannot be used with credentials.");
        eprintln!("[django-bolt] CORS will reflect the request origin instead of using wildcard.");
    }

    // Build global CORS config if any CORS settings are configured
    let global_cors_config = if !origins.is_empty() || !origin_regex_patterns.is_empty() || allow_all {
        let mut cors_origins = origins.clone();

        // If CORS_ALLOW_ALL_ORIGINS = True, use wildcard
        if allow_all {
            cors_origins = vec!["*".to_string()];
        }

        Some(CorsConfig::from_django_settings(
            cors_origins,
            origin_regex_patterns.clone(),
            allow_all,
            credentials,
            methods,
            headers,
            expose_headers,
            max_age,
        ))
    } else {
        None
    };

    // Compile origin regex patterns at startup (zero runtime overhead)
    let cors_origin_regexes: Vec<regex::Regex> = origin_regex_patterns.iter()
        .filter_map(|pattern| {
            regex::Regex::new(pattern).ok().or_else(|| {
                eprintln!("[django-bolt] Warning: Invalid CORS origin regex pattern: {}", pattern);
                None
            })
        })
        .collect();

    // Inject global CORS config into routes that don't have explicit config
    if let (Some(ref global_config), Some(metadata_temp)) = (&global_cors_config, ROUTE_METADATA_TEMP.get()) {
        // Clone the metadata HashMap to make it mutable
        let mut updated_metadata = metadata_temp.clone();

        for (_handler_id, route_meta) in updated_metadata.iter_mut() {
            // Inject CORS if:
            // 1. Route doesn't have explicit cors_config
            // 2. CORS not skipped via @skip_middleware("cors")
            let should_inject = route_meta.cors_config.is_none()
                && !route_meta.skip.contains("cors");

            if should_inject {
                route_meta.cors_config = Some(global_config.clone());
            }
        }

        // Set the final ROUTE_METADATA with updated version (only set once)
        let _ = ROUTE_METADATA.set(Arc::new(updated_metadata));
    } else if let Some(metadata_temp) = ROUTE_METADATA_TEMP.get() {
        // No global CORS config, just use the metadata as-is
        let _ = ROUTE_METADATA.set(Arc::new(metadata_temp.clone()));
    }

    let app_state = Arc::new(AppState {
        dispatch: dispatch.into(),
        debug,
        max_header_size,
        global_cors_config,
        cors_origin_regexes,
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



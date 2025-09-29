use actix_http::KeepAlive;
use actix_web::{self as aw, web, App, HttpServer};
use pyo3::prelude::*;
use socket2::{Domain, Protocol, Socket, Type};
use std::net::{IpAddr, SocketAddr};
use std::sync::Arc;
use tokio::sync::RwLock;

use crate::handler::handle_request;
use crate::router::Router;
use crate::state::{AppState, GLOBAL_ROUTER, TASK_LOCALS};

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
        .set(Arc::new(RwLock::new(router)))
        .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Router already initialized"))?;
    Ok(())
}

#[pyfunction]
pub fn start_server_async(
    py: Python<'_>,
    dispatch: Py<PyAny>,
    host: String,
    port: u16,
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

    let app_state = Arc::new(AppState { dispatch: dispatch.into() });

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



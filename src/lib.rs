use actix_http::KeepAlive;
use actix_web::{self as aw, http::StatusCode, web, App, HttpRequest, HttpResponse, HttpServer};
use ahash::AHashMap;
use once_cell::sync::OnceCell;
use pyo3::{
    prelude::*,
    types::{PyBytes, PyDict},
};
use pyo3_asyncio_0_21 as pyo3_asyncio;
use pyo3_asyncio_0_21::TaskLocals;
use socket2::{Domain, Protocol, Socket, Type};
use std::net::{IpAddr, SocketAddr};
use std::sync::Arc;
use tokio::sync::RwLock;

mod json;
mod router;
use router::{parse_query_string, Router};

#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

static mut GLOBAL_ROUTER: Option<Arc<RwLock<Router>>> = None;
static TASK_LOCALS: OnceCell<TaskLocals> = OnceCell::new();

struct AppState {
    dispatch: Py<PyAny>,
}

#[pyclass]
struct PyRequest {
    method: String,
    path: String,
    body: Vec<u8>,
    path_params: AHashMap<String, String>,
    query_params: AHashMap<String, String>,
}

#[pymethods]
impl PyRequest {
    #[getter]
    fn method(&self) -> &str {
        &self.method
    }

    #[getter]
    fn path(&self) -> &str {
        &self.path
    }

    #[getter]
    fn body<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new_bound(py, &self.body)
    }

    fn get<'py>(&self, py: Python<'py>, key: &str, default: Option<PyObject>) -> PyObject {
        match key {
            "method" => self.method.clone().into_py(py),
            "path" => self.path.clone().into_py(py),
            "body" => PyBytes::new_bound(py, &self.body).into_py(py),
            "params" => {
                let d = PyDict::new_bound(py);
                for (k, v) in &self.path_params {
                    let _ = d.set_item(k, v);
                }
                d.into_py(py)
            }
            "query" => {
                let d = PyDict::new_bound(py);
                for (k, v) in &self.query_params {
                    let _ = d.set_item(k, v);
                }
                d.into_py(py)
            }
            _ => default.unwrap_or_else(|| py.None()),
        }
    }

    fn __getitem__<'py>(&self, py: Python<'py>, key: &str) -> PyResult<PyObject> {
        match key {
            "method" => Ok(self.method.clone().into_py(py)),
            "path" => Ok(self.path.clone().into_py(py)),
            "body" => Ok(PyBytes::new_bound(py, &self.body).into_py(py)),
            "params" => {
                let d = PyDict::new_bound(py);
                for (k, v) in &self.path_params {
                    let _ = d.set_item(k, v);
                }
                Ok(d.into_py(py))
            }
            "query" => {
                let d = PyDict::new_bound(py);
                for (k, v) in &self.query_params {
                    let _ = d.set_item(k, v);
                }
                Ok(d.into_py(py))
            }
            _ => Err(pyo3::exceptions::PyKeyError::new_err(key.to_string())),
        }
    }
}

async fn handle_request(
    req: HttpRequest,
    body: web::Bytes,
    state: web::Data<Arc<AppState>>,
) -> HttpResponse {
    let method = req.method().as_str().to_string();
    let path = req.path().to_string();

    // No Rust fast paths; route all requests through Python

    // Get the global router
    let router = unsafe { GLOBAL_ROUTER.as_ref().expect("Router not initialized") };

    // Find route in Rust router
    let router_guard = router.read().await;
    let route_match = router_guard.find(&method, &path);
    drop(router_guard);

    if let Some((route, path_params)) = route_match {
        // Parse query parameters
        let query_params = if let Some(q) = req.uri().query() {
            parse_query_string(q)
        } else {
            AHashMap::new()
        };

        // Skip copying headers to minimize GIL work unless needed

        // Call async Python handler via pyo3-asyncio on Actix/Tokio runtime
        let dispatch = state.dispatch.clone();
        let handler = route.handler.clone();

        // Build coroutine under GIL briefly and convert to a Rust Future
        let fut = match Python::with_gil(|py| -> PyResult<_> {
            let request = PyRequest {
                method,
                path,
                body: body.to_vec(),
                path_params,
                query_params,
            };
            let request_obj = Py::new(py, request)?;

            // Use global background asyncio loop locals if available; otherwise, best-effort current locals
            let locals = if let Some(globals) = TASK_LOCALS.get() {
                globals.clone()
            } else {
                pyo3_asyncio::tokio::get_current_locals(py)?
            };

            // Call dispatch with handler and request to get coroutine
            let coroutine = dispatch.call1(py, (handler, request_obj))?;

            // Convert coroutine into a Rust Future scheduled on Tokio using explicit locals
            pyo3_asyncio::into_future_with_locals(&locals, coroutine.into_bound(py))
        }) {
            Ok(f) => f,
            Err(e) => {
                return HttpResponse::InternalServerError()
                    .content_type("text/plain; charset=utf-8")
                    .body(format!("Handler error (create coroutine): {}", e));
            }
        };

        // Await the Python coroutine without holding the GIL
        match fut.await {
            Ok(result_obj) => {
                // Extract the response tuple while holding the GIL briefly
                match Python::with_gil(|py| -> PyResult<(u16, Vec<(String, String)>, Vec<u8>)> {
                    result_obj.extract(py)
                }) {
                    Ok((status_code, resp_headers, body_bytes)) => {
                        let status = StatusCode::from_u16(status_code).unwrap_or(StatusCode::OK);
                        let mut builder = HttpResponse::build(status);
                        for (k, v) in resp_headers {
                            builder.append_header((k, v));
                        }

                        builder.body(body_bytes)
                    }
                    Err(e) => HttpResponse::InternalServerError()
                        .content_type("text/plain; charset=utf-8")
                        .body(format!("Handler error (extract): {}", e)),
                }
            }
            Err(e) => HttpResponse::InternalServerError()
                .content_type("text/plain; charset=utf-8")
                .body(format!("Handler error (await): {}", e)),
        }
    } else {
        HttpResponse::NotFound()
            .content_type("text/plain; charset=utf-8")
            .body("Not Found")
    }
}

#[pyfunction]
fn register_routes(
    _py: Python<'_>,
    routes: Vec<(String, String, usize, PyObject)>,
) -> PyResult<()> {
    let mut router = Router::new();

    for (method, path, handler_id, handler) in routes {
        router.register(&method, &path, handler_id, handler.into())?;
    }

    unsafe {
        GLOBAL_ROUTER = Some(Arc::new(RwLock::new(router)));
    }

    Ok(())
}

#[pyfunction]
fn start_server_async(py: Python<'_>, dispatch: PyObject, host: String, port: u16) -> PyResult<()> {
    // Ensure router is initialized
    unsafe {
        if GLOBAL_ROUTER.is_none() {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Routes not registered",
            ));
        }
    }

    // Initialize pyo3-asyncio for the main thread (Tokio integration)
    pyo3_asyncio::tokio::init(tokio::runtime::Builder::new_multi_thread());

    // Create a dedicated Python asyncio loop and store TaskLocals for use by into_future_with_locals
    let loop_obj: Py<PyAny> = {
        let asyncio = py.import_bound("asyncio")?;
        let ev = asyncio.call_method0("new_event_loop")?;
        let locals = TaskLocals::new(ev.clone()).copy_context(py)?;
        let _ = TASK_LOCALS.set(locals);
        ev.unbind().into()
    };
    // Start the loop in a Python-owned thread using run_forever
    std::thread::spawn(move || {
        Python::with_gil(|py| {
            let asyncio = py.import_bound("asyncio").expect("import asyncio");
            let ev = loop_obj.bind(py);
            let _ = asyncio.call_method1("set_event_loop", (ev.as_any(),));

            let _ = ev.call_method0("run_forever");
        });
    });

    let app_state = Arc::new(AppState {
        dispatch: dispatch.into(),
    });

    // Run Actix server on Actix system; keep pyo3-asyncio initialized so per-worker loops exist.
    py.allow_threads(|| {
        aw::rt::System::new()
            .block_on(async move {
                // Determine Actix worker count (default 2; override with DJANGO_BOLT_WORKERS)
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
                        // Build a SO_REUSEPORT listener
                        let ip: IpAddr = host.parse().unwrap_or(IpAddr::from([0, 0, 0, 0]));
                        let domain = match ip {
                            IpAddr::V4(_) => Domain::IPV4,
                            IpAddr::V6(_) => Domain::IPV6,
                        };
                        let socket = Socket::new(domain, Type::STREAM, Some(Protocol::TCP))
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
                        socket
                            .set_reuse_address(true)
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
                        #[cfg(not(target_os = "windows"))]
                        socket
                            .set_reuse_port(true)
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
                        let addr = SocketAddr::new(ip, port);
                        socket
                            .bind(&addr.into())
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
                        socket
                            .listen(1024)
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
                        let listener: std::net::TcpListener = socket.into();
                        listener
                            .set_nonblocking(true)
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;

                        server
                            .listen(listener)
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?
                            .run()
                            .await
                    } else {
                        server
                            .bind((host.as_str(), port))
                            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?
                            .run()
                            .await
                    }
                }
            })
            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, format!("{:?}", e)))
    })
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Server error: {}", e)))?;

    Ok(())
}

/// Python module: django_bolt._core
#[pymodule]
fn _core(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(register_routes, m)?)?;
    m.add_function(wrap_pyfunction!(start_server_async, m)?)?;
    Ok(())
}

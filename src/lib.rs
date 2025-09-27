use actix_files::NamedFile;
use actix_http::KeepAlive;
use actix_web::http::header::{HeaderName, HeaderValue};
use actix_web::web::Bytes;
use actix_web::{self as aw, http::StatusCode, web, App, HttpRequest, HttpResponse, HttpServer};
use ahash::AHashMap;
use futures_util::stream;
use futures_util::Stream;
use once_cell::sync::OnceCell;

fn convert_python_chunk(value: &Bound<'_, PyAny>) -> Option<Bytes> {
    if let Ok(py_bytes) = value.downcast::<PyBytes>() {
        return Some(Bytes::copy_from_slice(py_bytes.as_bytes()));
    }

    if let Ok(py_str) = value.downcast::<PyString>() {
        return Some(Bytes::from(py_str.to_string_lossy().into_owned()));
    }

    if let Ok(py_bytearray) = value.downcast::<PyByteArray>() {
        // Safety: PyByteArray exposes a contiguous buffer owned by Python.
        return Some(Bytes::copy_from_slice(unsafe { py_bytearray.as_bytes() }));
    }

    if let Ok(memory_view) = value.downcast::<PyMemoryView>() {
        if let Ok(bytes_obj) = memory_view.call_method0("tobytes") {
            if let Ok(py_bytes) = bytes_obj.downcast::<PyBytes>() {
                return Some(Bytes::copy_from_slice(py_bytes.as_bytes()));
            }
        }
    }

    if value.hasattr("__bytes__").unwrap_or(false) {
        if let Ok(buffer) = value.call_method0("__bytes__") {
            if let Ok(py_bytes) = buffer.downcast::<PyBytes>() {
                return Some(Bytes::copy_from_slice(py_bytes.as_bytes()));
            }
        }
    }

    if let Ok(py_str) = value.str() {
        return Some(Bytes::from(py_str.to_string()));
    }

    None
}
use pyo3::{
    prelude::*,
    types::{PyByteArray, PyBytes, PyDict, PyMemoryView, PyString},
};
use std::time::Instant;

mod direct_stream;
use pyo3_async_runtimes as pyo3_asyncio;
use pyo3_async_runtimes::TaskLocals;
use socket2::{Domain, Protocol, Socket, Type};
use std::net::{IpAddr, SocketAddr};
use std::pin::Pin;
use std::sync::Arc;
use tokio::sync::{mpsc, RwLock};

mod json;
mod router;
use router::{parse_query_string, Router};

#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

static GLOBAL_ROUTER: OnceCell<Arc<RwLock<Router>>> = OnceCell::new();
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
    headers: AHashMap<String, String>,
    cookies: AHashMap<String, String>,
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
    fn body<'py>(&self, py: Python<'py>) -> Py<PyAny> {
        PyBytes::new(py, &self.body).into_any().unbind()
    }

    fn get<'py>(&self, py: Python<'py>, key: &str, default: Option<Py<PyAny>>) -> Py<PyAny> {
        match key {
            "method" => PyString::new(py, &self.method).into_any().unbind(),
            "path" => PyString::new(py, &self.path).into_any().unbind(),
            "body" => PyBytes::new(py, &self.body).into_any().unbind(),
            "params" => {
                let d = PyDict::new(py);
                for (k, v) in &self.path_params {
                    let _ = d.set_item(k, v);
                }
                d.into_any().unbind()
            }
            "query" => {
                let d = PyDict::new(py);
                for (k, v) in &self.query_params {
                    let _ = d.set_item(k, v);
                }
                d.into_any().unbind()
            }
            "headers" => {
                let d = PyDict::new(py);
                for (k, v) in &self.headers {
                    let _ = d.set_item(k, v);
                }
                d.into_any().unbind()
            }
            "cookies" => {
                let d = PyDict::new(py);
                for (k, v) in &self.cookies {
                    let _ = d.set_item(k, v);
                }
                d.into_any().unbind()
            }
            _ => default.unwrap_or_else(|| py.None()),
        }
    }

    fn __getitem__<'py>(&self, py: Python<'py>, key: &str) -> PyResult<Py<PyAny>> {
        match key {
            "method" => Ok(PyString::new(py, &self.method).into_any().unbind()),
            "path" => Ok(PyString::new(py, &self.path).into_any().unbind()),
            "body" => Ok(PyBytes::new(py, &self.body).into_any().unbind()),
            "params" => {
                let d = PyDict::new(py);
                for (k, v) in &self.path_params {
                    let _ = d.set_item(k, v);
                }
                Ok(d.into_any().unbind())
            }
            "query" => {
                let d = PyDict::new(py);
                for (k, v) in &self.query_params {
                    let _ = d.set_item(k, v);
                }
                Ok(d.into_any().unbind())
            }
            "headers" => {
                let d = PyDict::new(py);
                for (k, v) in &self.headers {
                    let _ = d.set_item(k, v);
                }
                Ok(d.into_any().unbind())
            }
            "cookies" => {
                let d = PyDict::new(py);
                for (k, v) in &self.cookies {
                    let _ = d.set_item(k, v);
                }
                Ok(d.into_any().unbind())
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
    let router = GLOBAL_ROUTER.get().expect("Router not initialized");

    // Find route in Rust router
    let (route_handler, path_params) = {
        let router_guard = router.read().await;
        match router_guard.find(&method, &path) {
            Some((route, path_params)) => (
                Python::attach(|py| route.handler.clone_ref(py)),
                path_params,
            ),
            None => {
                return HttpResponse::NotFound()
                    .content_type("text/plain; charset=utf-8")
                    .body("Not Found");
            }
        }
    };

    // Parse query parameters
    let query_params = if let Some(q) = req.uri().query() {
        parse_query_string(q)
    } else {
        AHashMap::new()
    };

    // Skip copying headers to minimize GIL work unless needed

    // Call async Python handler via pyo3-asyncio on Actix/Tokio runtime
    let (dispatch, handler) =
        Python::attach(|py| (state.dispatch.clone_ref(py), route_handler.clone_ref(py)));

    // Build coroutine under GIL briefly and convert to a Rust Future
    let fut = match Python::attach(|py| -> PyResult<_> {
        // Collect headers (lower-case keys)
        let mut headers: AHashMap<String, String> = AHashMap::new();
        for (name, value) in req.headers().iter() {
            if let Ok(v) = value.to_str() {
                headers.insert(name.as_str().to_ascii_lowercase(), v.to_string());
            }
        }
        // Parse cookies from Cookie header
        let mut cookies: AHashMap<String, String> = AHashMap::new();
        if let Some(raw_cookie) = headers.get("cookie").cloned() {
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

        let request = PyRequest {
            method,
            path,
            body: body.to_vec(),
            path_params,
            query_params,
            headers,
            cookies,
        };
        let request_obj = Py::new(py, request)?;

        // Use global background asyncio loop locals if available; otherwise, best-effort current locals
        let locals_owned;
        let locals = if let Some(globals) = TASK_LOCALS.get() {
            globals
        } else {
            locals_owned = pyo3_asyncio::tokio::get_current_locals(py)?;
            &locals_owned
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
            // Try tuple result first
            let tuple_result: Result<(u16, Vec<(String, String)>, Vec<u8>), _> =
                Python::attach(|py| result_obj.extract(py));
            if let Ok((status_code, resp_headers, body_bytes)) = tuple_result {
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
                if let Some(path) = file_path {
                    return match NamedFile::open_async(&path).await {
                        Ok(file) => {
                            let mut response = file.into_response(&req);
                            response.head_mut().status = status;
                            for (k, v) in headers {
                                if let Ok(name) = HeaderName::try_from(k) {
                                    if let Ok(val) = HeaderValue::try_from(v) {
                                        response.headers_mut().insert(name, val);
                                    }
                                }
                            }
                            response
                        }
                        Err(e) => HttpResponse::InternalServerError()
                            .content_type("text/plain; charset=utf-8")
                            .body(format!("File open error: {}", e)),
                    };
                } else {
                    let mut builder = HttpResponse::build(status);
                    for (k, v) in headers {
                        builder.append_header((k, v));
                    }
                    return builder.body(body_bytes);
                }
            } else {
                // Try treat as StreamingResponse
                let streaming = Python::attach(|py| {
                    let obj = result_obj.bind(py);

                    // Positive identification via isinstance if available
                    let is_streaming = (|| -> PyResult<bool> {
                        let m = py.import("django_bolt.responses")?;
                        let cls = m.getattr("StreamingResponse")?;
                        obj.is_instance(&cls)
                    })()
                    .unwrap_or(false);

                    // Or structural check for 'content'
                    if !is_streaming && !obj.hasattr("content").unwrap_or(false) {
                        return None;
                    }

                    let status_code: u16 = obj
                        .getattr("status_code")
                        .and_then(|v| v.extract())
                        .unwrap_or(200);

                    let mut headers: Vec<(String, String)> = Vec::new();
                    if let Ok(hobj) = obj.getattr("headers") {
                        if let Ok(hdict) = hobj.downcast::<PyDict>() {
                            for (k, v) in hdict {
                                if let (Ok(ks), Ok(vs)) =
                                    (k.extract::<String>(), v.extract::<String>())
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
                    Some((status_code, headers, media_type, content_obj))
                });

                if let Some((status_code, headers, media_type, content_obj)) = streaming {
                    let status = StatusCode::from_u16(status_code).unwrap_or(StatusCode::OK);
                    let mut builder = HttpResponse::build(status);
                    for (k, v) in headers {
                        builder.append_header((k, v));
                    }
                    if media_type == "text/event-stream" {
                        // Determine if the content is async; async SSE needs the channel-based path
                        let is_async_sse = Python::attach(|py| {
                            let obj = content_obj.bind(py);
                            obj.hasattr("__aiter__").unwrap_or(false)
                                || obj.hasattr("__anext__").unwrap_or(false)
                        });

                        if is_async_sse {
                            // Async SSE: use async bridge but still force SSE headers
                            builder.append_header(("X-Accel-Buffering", "no"));
                            builder.append_header((
                                "Cache-Control",
                                "no-cache, no-store, must-revalidate",
                            ));
                            builder.append_header(("Pragma", "no-cache"));
                            builder.append_header(("Expires", "0"));
                            builder.append_header(("Expires", "0"));
                            builder.content_type("text/event-stream");

                            return builder.streaming(create_python_stream(content_obj));
                        } else {
                            // Sync SSE can use the optimized direct stream path
                            return direct_stream::create_sse_response(content_obj).unwrap_or_else(
                                |_| {
                                    builder.append_header(("X-Accel-Buffering", "no"));
                                    builder.append_header((
                                        "Cache-Control",
                                        "no-cache, no-store, must-revalidate",
                                    ));
                                    builder.append_header(("Pragma", "no-cache"));
                                    builder.append_header(("Expires", "0"));
                                    builder.content_type("text/event-stream").body("")
                                },
                            );
                        }
                    } else {
                        // Check if it's async first
                        let is_async = Python::attach(|py| {
                            let obj = content_obj.bind(py);
                            obj.hasattr("__aiter__").unwrap_or(false)
                                || obj.hasattr("__anext__").unwrap_or(false)
                        });

                        if is_async {
                            // Async iterators - use original streaming for now
                            let stream = create_python_stream(content_obj);
                            return builder.streaming(stream);
                        } else {
                            // For sync streaming, use direct stream
                            let mut direct = direct_stream::PythonDirectStream::new(content_obj);

                            // Try to collect small responses
                            if let Some(body) = direct.try_collect_small() {
                                return builder.body(body);
                            }

                            // Large response - use streaming
                            return builder.streaming(Box::pin(direct));
                        }
                    }
                } else {
                    return HttpResponse::InternalServerError()
                        .content_type("text/plain; charset=utf-8")
                        .body("Handler error: unsupported response type (expected tuple or StreamingResponse)");
                }
            }
        }
        Err(e) => {
            return HttpResponse::InternalServerError()
                .content_type("text/plain; charset=utf-8")
                .body(format!("Handler error (await): {}", e));
        }
    }
}

#[pyfunction]
fn register_routes(
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
fn start_server_async(
    py: Python<'_>,
    dispatch: Py<PyAny>,
    host: String,
    port: u16,
) -> PyResult<()> {
    // Ensure router is initialized
    if GLOBAL_ROUTER.get().is_none() {
        return Err(pyo3::exceptions::PyRuntimeError::new_err(
            "Routes not registered",
        ));
    }

    // Initialize pyo3-asyncio for the main thread (Tokio integration)
    pyo3_asyncio::tokio::init(tokio::runtime::Builder::new_multi_thread());

    // Create a dedicated Python asyncio loop and store TaskLocals for use by into_future_with_locals
    let loop_obj: Py<PyAny> = {
        let asyncio = py.import("asyncio")?;
        let ev = asyncio.call_method0("new_event_loop")?;
        let locals = TaskLocals::new(ev.clone()).copy_context(py)?;
        let _ = TASK_LOCALS.set(locals);
        ev.unbind().into()
    };
    // Start the loop in a Python-owned thread using run_forever
    std::thread::spawn(move || {
        Python::attach(|py| {
            let asyncio = py.import("asyncio").expect("import asyncio");
            let ev = loop_obj.bind(py);
            let _ = asyncio.call_method1("set_event_loop", (ev.as_any(),));

            let _ = ev.call_method0("run_forever");
        });
    });

    let app_state = Arc::new(AppState {
        dispatch: dispatch.into(),
    });

    // Run Actix server on Actix system; keep pyo3-asyncio initialized so per-worker loops exist.
    py.detach(|| {
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

fn create_python_stream(
    content: Py<PyAny>,
) -> Pin<Box<dyn Stream<Item = Result<Bytes, std::io::Error>> + Send>> {
    let debug_timing = std::env::var("DJANGO_BOLT_DEBUG_TIMING").is_ok();
    let start_time = if debug_timing {
        Some(Instant::now())
    } else {
        None
    };

    let channel_capacity: usize = std::env::var("DJANGO_BOLT_STREAM_CHANNEL_CAPACITY")
        .ok()
        .and_then(|v| v.parse::<usize>().ok())
        .filter(|&n| n > 0)
        .unwrap_or(8);

    // Resolve content to an iterator/generator target and detect async iterator support
    let resolve_start = if debug_timing {
        Some(Instant::now())
    } else {
        None
    };
    let (resolved_target, is_async_iter) = Python::attach(|py| {
        let mut target = content.clone_ref(py);
        let obj = content.bind(py);
        if obj.is_callable() {
            if let Ok(new_obj) = obj.call0() {
                target = new_obj.unbind();
            }
        }
        let b = target.bind(py);
        let has_async =
            b.hasattr("__aiter__").unwrap_or(false) || b.hasattr("__anext__").unwrap_or(false);
        (target, has_async)
    });

    if let Some(start) = resolve_start {
        eprintln!(
            "[TIMING] Iterator resolution: {:?}, is_async={}",
            start.elapsed(),
            is_async_iter
        );
    }

    let (tx, rx) = mpsc::channel::<Result<Bytes, std::io::Error>>(channel_capacity);

    if is_async_iter {
        // Async generator path: use pyo3-asyncio to await __anext__ in a Tokio task
        let debug_async = debug_timing;
        tokio::spawn(async move {
            let mut chunk_count = 0u32;
            let mut total_gil_time = std::time::Duration::ZERO;
            let mut total_await_time = std::time::Duration::ZERO;
            let mut total_send_time = std::time::Duration::ZERO;
            let task_start = if debug_async {
                Some(Instant::now())
            } else {
                None
            };
            // Initialize async iterator
            let async_iter: Option<Py<PyAny>> = Python::attach(|py| {
                let b = resolved_target.bind(py);
                if debug_async {
                    eprintln!(
                        "[DEBUG] Checking async iterator: has __aiter__={}, has __anext__={}",
                        b.hasattr("__aiter__").unwrap_or(false),
                        b.hasattr("__anext__").unwrap_or(false)
                    );
                }
                if b.hasattr("__aiter__").unwrap_or(false) {
                    match b.call_method0("__aiter__") {
                        Ok(it) => {
                            if debug_async {
                                eprintln!("[DEBUG] Successfully called __aiter__");
                            }
                            Some(it.unbind())
                        }
                        Err(e) => {
                            if debug_async {
                                eprintln!("[DEBUG] Failed to call __aiter__: {}", e);
                            }
                            None
                        }
                    }
                } else if b.hasattr("__anext__").unwrap_or(false) {
                    if debug_async {
                        eprintln!("[DEBUG] Using object as async iterator directly");
                    }
                    Some(resolved_target.clone_ref(py))
                } else {
                    if debug_async {
                        eprintln!("[DEBUG] Object is not an async iterator");
                    }
                    None
                }
            });

            if async_iter.is_none() {
                // Send an error to the channel instead of silently returning
                let _ = tx
                    .send(Err(std::io::Error::new(
                        std::io::ErrorKind::InvalidData,
                        "Failed to initialize async iterator",
                    )))
                    .await;
                return;
            }
            let async_iter = async_iter.unwrap();

            // Prime first future outside the loop
            let mut next_fut_opt = Python::attach(|py| {
                let awaitable = match async_iter.bind(py).call_method0("__anext__") {
                    Ok(a) => a,
                    Err(e) => {
                        if e.is_instance_of::<pyo3::exceptions::PyStopAsyncIteration>(py) {
                            return None;
                        }
                        return None;
                    }
                };

                let locals_owned;
                let locals = if let Some(globals) = TASK_LOCALS.get() {
                    globals
                } else {
                    match pyo3_asyncio::tokio::get_current_locals(py) {
                        Ok(locals) => {
                            locals_owned = locals;
                            &locals_owned
                        }
                        Err(_) => return None,
                    }
                };

                match pyo3_asyncio::into_future_with_locals(&locals, awaitable) {
                    Ok(f) => Some(f),
                    Err(_) => None,
                }
            });

            if debug_async {
                eprintln!(
                    "[DEBUG] First future priming result: {}",
                    next_fut_opt.is_some()
                );
            }

            while let Some(fut) = next_fut_opt {
                // Await current item
                let await_start = if debug_async {
                    Some(Instant::now())
                } else {
                    None
                };
                if debug_async {
                    eprintln!("[DEBUG] About to await future");
                }
                let next_obj = match fut.await {
                    Ok(obj) => {
                        if debug_async {
                            eprintln!("[DEBUG] Successfully awaited future");
                        }
                        obj
                    }
                    Err(e) => {
                        if debug_async {
                            eprintln!("[DEBUG] Failed to await future: {}", e);
                        }
                        break;
                    }
                };
                if let Some(start) = await_start {
                    total_await_time += start.elapsed();
                }

                // Convert current item and pipeline creation of the next future in a single GIL block
                let gil_start = if debug_async {
                    Some(Instant::now())
                } else {
                    None
                };
                let (bytes_opt, new_next_fut_opt) = Python::attach(|py| {
                    // Convert current chunk to Bytes
                    let v = next_obj.bind(py);
                    let chunk_bytes = convert_python_chunk(&v);

                    // Prepare the next future now to reduce GIL crossings
                    let next_future_opt = {
                        let res = async_iter.bind(py).call_method0("__anext__");
                        match res {
                            Ok(awaitable) => {
                                let locals_owned;
                                let locals = if let Some(globals) = TASK_LOCALS.get() {
                                    globals
                                } else {
                                    match pyo3_asyncio::tokio::get_current_locals(py) {
                                        Ok(locals) => {
                                            locals_owned = locals;
                                            &locals_owned
                                        }
                                        Err(_) => return (chunk_bytes, None),
                                    }
                                };

                                match pyo3_asyncio::into_future_with_locals(&locals, awaitable) {
                                    Ok(f) => Some(f),
                                    Err(_) => None,
                                }
                            }
                            Err(e) => {
                                if e.is_instance_of::<pyo3::exceptions::PyStopAsyncIteration>(py) {
                                    None
                                } else {
                                    None
                                }
                            }
                        }
                    };

                    (chunk_bytes, next_future_opt)
                });

                if let Some(start) = gil_start {
                    total_gil_time += start.elapsed();
                }

                // Send current chunk
                if let Some(bytes) = bytes_opt {
                    if debug_async {
                        eprintln!("[DEBUG] Sending chunk of {} bytes", bytes.len());
                    }
                    let send_start = if debug_async {
                        Some(Instant::now())
                    } else {
                        None
                    };
                    if tx.send(Ok(bytes)).await.is_err() {
                        if debug_async {
                            eprintln!("[DEBUG] Failed to send chunk to channel");
                        }
                        break;
                    }
                    if let Some(start) = send_start {
                        total_send_time += start.elapsed();
                    }
                    chunk_count += 1;
                    if debug_async {
                        eprintln!("[DEBUG] Successfully sent chunk #{}", chunk_count);
                    }
                } else {
                    if debug_async {
                        eprintln!("[DEBUG] Chunk conversion failed, breaking");
                    }
                    break;
                }

                // Continue with next future or finish
                next_fut_opt = new_next_fut_opt;
            }

            if let Some(start) = task_start {
                let total = start.elapsed();
                eprintln!("[TIMING] Async streaming complete:");
                eprintln!("  Total time: {:?}", total);
                eprintln!("  Chunks sent: {}", chunk_count);
                eprintln!(
                    "  GIL time: {:?} ({:.1}%)",
                    total_gil_time,
                    (total_gil_time.as_secs_f64() / total.as_secs_f64()) * 100.0
                );
                eprintln!(
                    "  Await time: {:?} ({:.1}%)",
                    total_await_time,
                    (total_await_time.as_secs_f64() / total.as_secs_f64()) * 100.0
                );
                eprintln!(
                    "  Send time: {:?} ({:.1}%)",
                    total_send_time,
                    (total_send_time.as_secs_f64() / total.as_secs_f64()) * 100.0
                );
                if chunk_count > 0 {
                    eprintln!("  Avg per chunk: {:?}", total / chunk_count);
                }
            }
        });
    } else {
        // Single blocking worker per stream: pump sync iterator and send chunks
        let debug_sync = debug_timing;
        tokio::task::spawn_blocking(move || {
            let mut iterator: Option<Py<PyAny>> = None;
            let mut chunk_count = 0u32;
            let mut total_gil_time = std::time::Duration::ZERO;
            let mut total_send_time = std::time::Duration::ZERO;
            let task_start = if debug_sync {
                Some(Instant::now())
            } else {
                None
            };

            loop {
                // Pull next chunk under the GIL
                let gil_start = if debug_sync {
                    Some(Instant::now())
                } else {
                    None
                };
                let next: Option<Bytes> = Python::attach(|py| {
                    if iterator.is_none() {
                        let iter_target = resolved_target.clone_ref(py);
                        let bound = iter_target.bind(py);
                        let iter_obj = if bound.hasattr("__next__").unwrap_or(false) {
                            iter_target
                        } else if bound.hasattr("__iter__").unwrap_or(false) {
                            match bound.call_method0("__iter__") {
                                Ok(it) => it.unbind(),
                                Err(_) => return None,
                            }
                        } else {
                            return None;
                        };
                        iterator = Some(iter_obj);
                    }

                    let it = iterator.as_ref().unwrap().bind(py);
                    match it.call_method0("__next__") {
                        Ok(value) => convert_python_chunk(&value),
                        Err(err) => {
                            if err.is_instance_of::<pyo3::exceptions::PyStopIteration>(py) {
                                None
                            } else {
                                None
                            }
                        }
                    }
                });

                if let Some(start) = gil_start {
                    total_gil_time += start.elapsed();
                }

                match next {
                    Some(bytes) => {
                        let send_start = if debug_sync {
                            Some(Instant::now())
                        } else {
                            None
                        };
                        if tx.blocking_send(Ok(bytes)).is_err() {
                            break;
                        }
                        if let Some(start) = send_start {
                            total_send_time += start.elapsed();
                        }
                        chunk_count += 1;
                    }
                    None => {
                        break;
                    }
                }
            }

            if let Some(start) = task_start {
                let total = start.elapsed();
                eprintln!("[TIMING] Sync streaming complete:");
                eprintln!("  Total time: {:?}", total);
                eprintln!("  Chunks sent: {}", chunk_count);
                eprintln!(
                    "  GIL time: {:?} ({:.1}%)",
                    total_gil_time,
                    (total_gil_time.as_secs_f64() / total.as_secs_f64()) * 100.0
                );
                eprintln!(
                    "  Send time: {:?} ({:.1}%)",
                    total_send_time,
                    (total_send_time.as_secs_f64() / total.as_secs_f64()) * 100.0
                );
                if chunk_count > 0 {
                    eprintln!("  Avg per chunk: {:?}", total / chunk_count);
                }
            }
            // sender dropped -> stream ends
        });
    }

    let s = stream::unfold(rx, |mut rx| async move {
        match rx.recv().await {
            Some(item) => Some((item, rx)),
            None => None,
        }
    });

    Box::pin(s)
}

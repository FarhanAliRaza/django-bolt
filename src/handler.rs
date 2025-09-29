use actix_files::NamedFile;
use actix_web::http::header::{HeaderName, HeaderValue};
use actix_web::{http::StatusCode, web, HttpRequest, HttpResponse};
use ahash::AHashMap;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::Arc;

use crate::request::PyRequest;
use crate::router::parse_query_string;
use crate::state::{AppState, GLOBAL_ROUTER, TASK_LOCALS};
use crate::streaming::create_python_stream;
use crate::direct_stream;

pub async fn handle_request(
    req: HttpRequest,
    body: web::Bytes,
    state: web::Data<Arc<AppState>>,
) -> HttpResponse {
    let method = req.method().as_str().to_string();
    let path = req.path().to_string();

    let router = GLOBAL_ROUTER.get().expect("Router not initialized");

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

    let query_params = if let Some(q) = req.uri().query() {
        parse_query_string(q)
    } else {
        AHashMap::new()
    };

    let (dispatch, handler) = Python::attach(|py| (state.dispatch.clone_ref(py), route_handler.clone_ref(py)));

    let fut = match Python::attach(|py| -> PyResult<_> {
        let mut headers: AHashMap<String, String> = AHashMap::new();
        for (name, value) in req.headers().iter() {
            if let Ok(v) = value.to_str() {
                headers.insert(name.as_str().to_ascii_lowercase(), v.to_string());
            }
        }
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

        let locals_owned;
        let locals = if let Some(globals) = TASK_LOCALS.get() { globals } else {
            locals_owned = pyo3_async_runtimes::tokio::get_current_locals(py)?;
            &locals_owned
        };

        let coroutine = dispatch.call1(py, (handler, request_obj))?;
        pyo3_async_runtimes::into_future_with_locals(&locals, coroutine.into_bound(py))
    }) {
        Ok(f) => f,
        Err(e) => {
            return HttpResponse::InternalServerError()
                .content_type("text/plain; charset=utf-8")
                .body(format!("Handler error (create coroutine): {}", e));
        }
    };

    match fut.await {
        Ok(result_obj) => {
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
                    for (k, v) in headers { builder.append_header((k, v)); }
                    return builder.body(body_bytes);
                }
            } else {
                let streaming = Python::attach(|py| {
                    let obj = result_obj.bind(py);
                    let is_streaming = (|| -> PyResult<bool> {
                        let m = py.import("django_bolt.responses")?;
                        let cls = m.getattr("StreamingResponse")?;
                        obj.is_instance(&cls)
                    })().unwrap_or(false);
                    if !is_streaming && !obj.hasattr("content").unwrap_or(false) { return None; }
                    let status_code: u16 = obj.getattr("status_code").and_then(|v| v.extract()).unwrap_or(200);
                    let mut headers: Vec<(String, String)> = Vec::new();
                    if let Ok(hobj) = obj.getattr("headers") {
                        if let Ok(hdict) = hobj.downcast::<PyDict>() {
                            for (k, v) in hdict {
                                if let (Ok(ks), Ok(vs)) = (k.extract::<String>(), v.extract::<String>()) { headers.push((ks, vs)); }
                            }
                        }
                    }
                    let media_type: String = obj.getattr("media_type").and_then(|v| v.extract()).unwrap_or_else(|_| "application/octet-stream".to_string());
                    let has_ct = headers.iter().any(|(k, _)| k.eq_ignore_ascii_case("content-type"));
                    if !has_ct { headers.push(("content-type".to_string(), media_type.clone())); }
                    let content_obj: Py<PyAny> = match obj.getattr("content") { Ok(c) => c.unbind(), Err(_) => return None };
                    Some((status_code, headers, media_type, content_obj))
                });

                if let Some((status_code, headers, media_type, content_obj)) = streaming {
                    let status = StatusCode::from_u16(status_code).unwrap_or(StatusCode::OK);
                    let mut builder = HttpResponse::build(status);
                    for (k, v) in headers { builder.append_header((k, v)); }
                    if media_type == "text/event-stream" {
                        let mut final_content_obj = content_obj;
                        let mut is_async_sse = false;
                        let has_async = Python::attach(|py| {
                            let obj = final_content_obj.bind(py);
                            obj.hasattr("__aiter__").unwrap_or(false) || obj.hasattr("__anext__").unwrap_or(false)
                        });
                        if has_async {
                            let wrapped = Python::attach(|py| -> Option<Py<PyAny>> {
                                match py.import("django_bolt.async_collector") {
                                    Ok(collector_module) => {
                                        if let Ok(collector_class) = collector_module.getattr("AsyncToSyncCollector") {
                                            let b = final_content_obj.bind(py);
                                            match collector_class.call1((b.clone(), 5, 1)) {
                                                Ok(wrapped) => return Some(wrapped.unbind()),
                                                Err(_) => {}
                                            }
                                        }
                                    }
                                    Err(_) => {}
                                }
                                None
                            });
                            if let Some(w) = wrapped { final_content_obj = w; is_async_sse = false; } else { is_async_sse = true; }
                        }
                        if is_async_sse {
                            builder.append_header(("X-Accel-Buffering", "no"));
                            builder.append_header(("Cache-Control", "no-cache, no-store, must-revalidate"));
                            builder.append_header(("Pragma", "no-cache"));
                            builder.append_header(("Expires", "0"));
                            builder.content_type("text/event-stream");
                            return builder.streaming(create_python_stream(final_content_obj));
                        } else {
                            return direct_stream::create_sse_response(final_content_obj).unwrap_or_else(|_| {
                                builder.append_header(("X-Accel-Buffering", "no"));
                                builder.append_header(("Cache-Control", "no-cache, no-store, must-revalidate"));
                                builder.append_header(("Pragma", "no-cache"));
                                builder.append_header(("Expires", "0"));
                                builder.content_type("text/event-stream").body("")
                            });
                        }
                    } else {
                        let mut final_content = content_obj;
                        let is_async = Python::attach(|py| {
                            let obj = final_content.bind(py);
                            obj.hasattr("__aiter__").unwrap_or(false) || obj.hasattr("__anext__").unwrap_or(false)
                        });

                        if is_async {
                            let wrapped = Python::attach(|py| -> Option<Py<PyAny>> {
                                match py.import("django_bolt.async_collector") {
                                    Ok(collector_module) => {
                                        if let Ok(collector_class) = collector_module.getattr("AsyncToSyncCollector") {
                                            let b = final_content.bind(py);
                                            match collector_class.call1((b.clone(), 20, 2)) {
                                                Ok(wrapped) => return Some(wrapped.unbind()),
                                                Err(_) => {}
                                            }
                                        }
                                    }
                                    Err(_) => {}
                                }
                                None
                            });
                            if let Some(w) = wrapped { final_content = w; } else {
                                let stream = create_python_stream(final_content);
                                return builder.streaming(stream);
                            }
                        }
                        {
                            let mut direct = direct_stream::PythonDirectStream::new(final_content);
                            if let Some(body) = direct.try_collect_small() { return builder.body(body); }
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



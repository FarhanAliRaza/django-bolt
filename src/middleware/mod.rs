pub mod cors;
pub mod rate_limit;
pub mod auth;

use actix_web::HttpResponse;
use ahash::AHashMap;
use pyo3::prelude::*;
use std::collections::HashMap;

/// Process middleware metadata and return early response if needed
pub async fn process_middleware(
    method: &str,
    _path: &str,
    headers: &AHashMap<String, String>,
    handler_id: usize,
    metadata: &Py<PyAny>,
) -> Option<HttpResponse> {
    // Check for OPTIONS preflight
    if method == "OPTIONS" {
        return Python::attach(|py| {
            if let Ok(meta) = metadata.extract::<HashMap<String, Py<PyAny>>>(py) {
                if let Some(middleware_list) = meta.get("middleware") {
                    // Check if CORS is enabled
                    if let Ok(middlewares) = middleware_list.extract::<Vec<HashMap<String, Py<PyAny>>>>(py) {
                        for mw in middlewares {
                            if let Some(mw_type) = mw.get("type") {
                                if let Ok(type_str) = mw_type.extract::<String>(py) {
                                    if type_str == "cors" {
                                        return Some(cors::handle_preflight(&mw, py));
                                    }
                                }
                            }
                        }
                    }
                }
            }
            None
        })
    }
    
    // Process other middleware
    Python::attach(|py| {
        if let Ok(meta) = metadata.extract::<HashMap<String, Py<PyAny>>>(py) {
            if let Some(middleware_list) = meta.get("middleware") {
                if let Ok(middlewares) = middleware_list.extract::<Vec<HashMap<String, Py<PyAny>>>>(py) {
                    for mw in middlewares {
                        if let Some(mw_type) = mw.get("type") {
                            if let Ok(type_str) = mw_type.extract::<String>(py) {
                                match type_str.as_str() {
                                    "rate_limit" => {
                                        if let Some(response) = rate_limit::check_rate_limit(handler_id, headers, &mw, py) {
                                            return Some(response);
                                        }
                                    }
                                    "auth" => {
                                        if let Some(response) = auth::check_auth(headers, &mw, py) {
                                            return Some(response);
                                        }
                                    }
                                    _ => {}
                                }
                            }
                        }
                    }
                }
            }
        }
        None
    })
}

/// Add CORS headers to response if needed
pub fn add_cors_headers(
    response: &mut HttpResponse,
    origin: Option<&str>,
    metadata: &Py<PyAny>,
) {
    Python::attach(|py| {
        if let Ok(meta) = metadata.extract::<HashMap<String, Py<PyAny>>>(py) {
            if let Some(middleware_list) = meta.get("middleware") {
                if let Ok(middlewares) = middleware_list.extract::<Vec<HashMap<String, Py<PyAny>>>>(py) {
                    for mw in middlewares {
                        if let Some(mw_type) = mw.get("type") {
                            if let Ok(type_str) = mw_type.extract::<String>(py) {
                                if type_str == "cors" {
                                    cors::add_cors_headers_to_response(response, origin, &mw, py);
                                    break;
                                }
                            }
                        }
                    }
                }
            }
        }
    });
}
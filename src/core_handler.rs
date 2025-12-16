//! Core request handling logic shared between production and test handlers
//!
//! This module provides the unified request handling pipeline that is used by:
//! - Production: `handler.rs` via Actix Web
//! - Tests: `test_state.rs` via per-instance test apps
//! - Testing: `testing.rs` via global router
//!
//! The goal is to have ONE code path for request handling, ensuring tests
//! accurately validate production behavior.

use actix_web::http::StatusCode;
use actix_web::HttpResponse;
use ahash::AHashMap;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyTuple};

use crate::error;
use crate::handler::build_file_response;
use crate::metadata::{CorsConfig, RouteMetadata};
use crate::middleware;
use crate::middleware::auth::populate_auth_context;
use crate::request::PyRequest;
use crate::response_builder;
use crate::responses;
use crate::router::{parse_query_string, RouteMatch, Router};
use crate::streaming::{create_python_stream, create_sse_stream};
use crate::validation::{parse_cookies_inline, validate_auth_and_guards, AuthGuardResult};

/// Input data for request handling (extracted from HttpRequest or test parameters)
pub struct RequestInput {
    pub method: String,
    pub path: String,
    pub headers: AHashMap<String, String>,
    pub body: Vec<u8>,
    pub query_string: Option<String>,
    pub peer_addr: Option<String>,
}

/// Dependencies needed for request handling
/// This abstraction allows tests to provide per-instance router/metadata
/// while production uses global state
pub struct RequestDependencies<'a> {
    /// Route handler and metadata lookup
    pub router: &'a Router,
    /// Route metadata by handler_id
    pub route_metadata: &'a dyn Fn(usize) -> Option<RouteMetadata>,
    /// Global CORS config (may be None)
    pub global_cors_config: Option<&'a CorsConfig>,
    /// Python dispatch function
    pub dispatch: &'a Py<PyAny>,
    /// Debug mode flag
    pub debug: bool,
}

/// Result of core request handling that can be converted to HttpResponse or tuple
pub enum CoreHandlerResult {
    /// Simple response (status, headers, body)
    Simple(u16, Vec<(String, String)>, Vec<u8>),
    /// File response (needs async file reading)
    File {
        path: String,
        status: StatusCode,
        headers: Vec<(String, String)>,
        skip_compression: bool,
        is_head_request: bool,
    },
    /// Streaming response
    Streaming {
        status: StatusCode,
        headers: Vec<(String, String)>,
        content: Py<PyAny>,
        is_async_generator: bool,
        media_type: String,
        skip_compression: bool,
        skip_cors: bool,
        is_head_request: bool,
    },
    /// Error response
    Error(HttpResponse),
}

impl CoreHandlerResult {
    /// Convert to simple tuple format (for tests)
    pub fn to_tuple(self) -> (u16, Vec<(String, String)>, Vec<u8>) {
        match self {
            CoreHandlerResult::Simple(status, headers, body) => (status, headers, body),
            CoreHandlerResult::File { status, headers, .. } => {
                // For tests, file responses need to be read synchronously
                (status.as_u16(), headers, b"[file content]".to_vec())
            }
            CoreHandlerResult::Streaming {
                status, headers, ..
            } => {
                // For tests, streaming is collected elsewhere
                (status.as_u16(), headers, b"[streaming content]".to_vec())
            }
            CoreHandlerResult::Error(resp) => {
                let status = resp.status().as_u16();
                let headers: Vec<(String, String)> = resp
                    .headers()
                    .iter()
                    .map(|(k, v)| (k.as_str().to_string(), v.to_str().unwrap_or("").to_string()))
                    .collect();
                (status, headers, Vec::new())
            }
        }
    }
}

/// Parsed route match result
pub struct MatchedRoute {
    pub handler: Py<PyAny>,
    pub handler_id: usize,
    pub path_params: AHashMap<String, String>,
}

/// Find route in router and return matched route info
pub fn find_route(
    router: &Router,
    method: &str,
    path: &str,
) -> Option<MatchedRoute> {
    router.find(method, path).map(|route_match| {
        let handler_id = route_match.handler_id();
        let handler = Python::attach(|py| route_match.route().handler.clone_ref(py));
        let path_params = route_match.path_params();
        MatchedRoute {
            handler,
            handler_id,
            path_params,
        }
    })
}

/// Handle automatic OPTIONS for routes that don't have explicit OPTIONS handler
pub fn handle_automatic_options(
    router: &Router,
    path: &str,
    global_cors_config: Option<&CorsConfig>,
) -> Option<CoreHandlerResult> {
    let available_methods = router.find_all_methods(path);
    if !available_methods.is_empty() {
        let allow_header = available_methods.join(", ");
        return Some(CoreHandlerResult::Simple(
            204,
            vec![
                ("allow".to_string(), allow_header),
                ("content-type".to_string(), "application/json".to_string()),
            ],
            Vec::new(),
        ));
    }

    // Handle OPTIONS preflight for non-existent routes
    if global_cors_config.is_some() {
        return Some(CoreHandlerResult::Simple(204, Vec::new(), Vec::new()));
    }

    None
}

/// Build 404 response with CORS headers if configured
pub fn build_404_response(
    request_origin: Option<&str>,
    global_cors_config: Option<&CorsConfig>,
) -> CoreHandlerResult {
    let mut headers = vec![(
        "content-type".to_string(),
        "text/plain; charset=utf-8".to_string(),
    )];

    // Add CORS headers if configured
    if let Some(cors_cfg) = global_cors_config {
        add_cors_headers_to_vec(&mut headers, request_origin, cors_cfg);
    }

    CoreHandlerResult::Simple(404, headers, b"Not Found".to_vec())
}

/// Build 401 Unauthorized response with CORS headers
pub fn build_401_response(
    request_origin: Option<&str>,
    cors_config: Option<&CorsConfig>,
) -> CoreHandlerResult {
    let mut headers = vec![("content-type".to_string(), "application/json".to_string())];

    if let Some(cors_cfg) = cors_config {
        add_cors_headers_to_vec(&mut headers, request_origin, cors_cfg);
    }

    CoreHandlerResult::Simple(
        401,
        headers,
        br#"{"detail":"Authentication required"}"#.to_vec(),
    )
}

/// Build 403 Forbidden response with CORS headers
pub fn build_403_response(
    request_origin: Option<&str>,
    cors_config: Option<&CorsConfig>,
) -> CoreHandlerResult {
    let mut headers = vec![("content-type".to_string(), "application/json".to_string())];

    if let Some(cors_cfg) = cors_config {
        add_cors_headers_to_vec(&mut headers, request_origin, cors_cfg);
    }

    CoreHandlerResult::Simple(403, headers, br#"{"detail":"Permission denied"}"#.to_vec())
}

/// Add CORS headers to a Vec - uses unified implementation from cors.rs
pub fn add_cors_headers_to_vec(
    resp_headers: &mut Vec<(String, String)>,
    request_origin: Option<&str>,
    cors_cfg: &CorsConfig,
) {
    // Use the unified CORS function from cors.rs
    crate::cors::apply_cors_to_vec(resp_headers, request_origin, cors_cfg, None, None);
}

/// Check rate limiting using the shared rate limit infrastructure
/// Returns Some(response) if rate limited, None if allowed
pub fn check_rate_limit(
    handler_id: usize,
    headers: &AHashMap<String, String>,
    peer_addr: Option<&str>,
    route_metadata: &RouteMetadata,
    method: &str,
    path: &str,
) -> Option<CoreHandlerResult> {
    if let Some(ref rate_config) = route_metadata.rate_limit_config {
        if let Some(response) = middleware::rate_limit::check_rate_limit(
            handler_id,
            headers,
            peer_addr,
            rate_config,
            method,
            path,
        ) {
            let status = response.status().as_u16();
            let headers: Vec<(String, String)> = response
                .headers()
                .iter()
                .map(|(k, v)| (k.as_str().to_string(), v.to_str().unwrap_or("").to_string()))
                .collect();
            return Some(CoreHandlerResult::Simple(
                status,
                headers,
                responses::get_rate_limit_body(1),
            ));
        }
    }
    None
}

/// Validate authentication and guards for a request
/// Returns the auth context if successful, or an error response
pub fn validate_request_auth(
    headers: &AHashMap<String, String>,
    route_metadata: &RouteMetadata,
    request_origin: Option<&str>,
    cors_config: Option<&CorsConfig>,
) -> Result<Option<crate::middleware::auth::AuthContext>, CoreHandlerResult> {
    match validate_auth_and_guards(headers, &route_metadata.auth_backends, &route_metadata.guards) {
        AuthGuardResult::Allow(ctx) => Ok(ctx),
        AuthGuardResult::Unauthorized => {
            Err(build_401_response(request_origin, cors_config))
        }
        AuthGuardResult::Forbidden => {
            Err(build_403_response(request_origin, cors_config))
        }
    }
}

/// Build PyRequest object for Python handler dispatch
pub fn build_py_request(
    py: Python<'_>,
    input: &RequestInput,
    path_params: AHashMap<String, String>,
    query_params: AHashMap<String, String>,
    auth_ctx: Option<&crate::middleware::auth::AuthContext>,
    needs_headers: bool,
    needs_cookies: bool,
    headers: &AHashMap<String, String>,
) -> PyResult<Py<PyRequest>> {
    // Create context dict only if auth context is present
    let context = if let Some(auth) = auth_ctx {
        let ctx_dict = PyDict::new(py);
        let ctx_py = ctx_dict.unbind();
        populate_auth_context(&ctx_py, auth, py);
        Some(ctx_py)
    } else {
        None
    };

    // Only pass headers to Python if handler needs them
    let headers_for_python = if needs_headers {
        headers.clone()
    } else {
        AHashMap::new()
    };

    // Only parse cookies if handler needs them
    let cookies = if needs_cookies {
        parse_cookies_inline(headers.get("cookie").map(|s| s.as_str()))
    } else {
        AHashMap::new()
    };

    let request = PyRequest {
        method: input.method.clone(),
        path: input.path.clone(),
        body: input.body.clone(),
        path_params,
        query_params,
        headers: headers_for_python,
        cookies,
        context,
        user: None,
        state: PyDict::new(py).unbind(),
    };

    Py::new(py, request)
}

/// Process the result from Python handler dispatch
/// This is the core response processing logic shared by all handlers
pub fn process_handler_result(
    py: Python<'_>,
    result_obj: Py<PyAny>,
    skip_compression: bool,
    skip_cors: bool,
    is_head_request: bool,
    request_origin: Option<&str>,
    cors_config: Option<&CorsConfig>,
    debug: bool,
) -> CoreHandlerResult {
    // Fast-path: try to extract as tuple (status, headers, body)
    let fast_tuple: Option<(u16, Vec<(String, String)>, Vec<u8>)> = {
        let obj = result_obj.bind(py);
        let tuple = match obj.cast::<PyTuple>() {
            Ok(t) => t,
            Err(_) => {
                // Not a tuple, try other response types
                return process_non_tuple_response(
                    py,
                    result_obj,
                    skip_compression,
                    skip_cors,
                    is_head_request,
                    request_origin,
                    cors_config,
                    debug,
                );
            }
        };

        if tuple.len() != 3 {
            return process_non_tuple_response(
                py,
                result_obj,
                skip_compression,
                skip_cors,
                is_head_request,
                request_origin,
                cors_config,
                debug,
            );
        }

        // Extract tuple elements
        let status_code: u16 = match tuple.get_item(0).ok().and_then(|v| v.extract().ok()) {
            Some(s) => s,
            None => {
                return process_non_tuple_response(
                    py,
                    result_obj,
                    skip_compression,
                    skip_cors,
                    is_head_request,
                    request_origin,
                    cors_config,
                    debug,
                )
            }
        };

        let resp_headers: Vec<(String, String)> = match tuple
            .get_item(1)
            .ok()
            .and_then(|v| v.extract().ok())
        {
            Some(h) => h,
            None => {
                return process_non_tuple_response(
                    py,
                    result_obj,
                    skip_compression,
                    skip_cors,
                    is_head_request,
                    request_origin,
                    cors_config,
                    debug,
                )
            }
        };

        let body_obj = match tuple.get_item(2) {
            Ok(b) => b,
            Err(_) => {
                return process_non_tuple_response(
                    py,
                    result_obj,
                    skip_compression,
                    skip_cors,
                    is_head_request,
                    request_origin,
                    cors_config,
                    debug,
                )
            }
        };

        let body_vec = match body_obj.cast::<PyBytes>() {
            Ok(pybytes) => pybytes.as_bytes().to_vec(),
            Err(_) => match body_obj.extract::<Vec<u8>>() {
                Ok(v) => v,
                Err(_) => {
                    return process_non_tuple_response(
                        py,
                        result_obj,
                        skip_compression,
                        skip_cors,
                        is_head_request,
                        request_origin,
                        cors_config,
                        debug,
                    )
                }
            },
        };

        Some((status_code, resp_headers, body_vec))
    };

    if let Some((status_code, resp_headers, body_bytes)) = fast_tuple {
        // Process tuple response
        let mut file_path: Option<String> = None;
        let mut headers: Vec<(String, String)> = Vec::with_capacity(resp_headers.len());

        for (k, v) in resp_headers {
            if k.eq_ignore_ascii_case("x-bolt-file-path") {
                file_path = Some(v);
            } else {
                headers.push((k, v));
            }
        }

        // Handle file response
        if let Some(fpath) = file_path {
            return CoreHandlerResult::File {
                path: fpath,
                status: StatusCode::from_u16(status_code).unwrap_or(StatusCode::OK),
                headers,
                skip_compression,
                is_head_request,
            };
        }

        // Add CORS headers if not skipped
        if !skip_cors {
            if let Some(cors_cfg) = cors_config {
                add_cors_headers_to_vec(&mut headers, request_origin, cors_cfg);
            }
        }

        // Handle HEAD request
        let response_body = if is_head_request {
            Vec::new()
        } else {
            body_bytes
        };

        CoreHandlerResult::Simple(status_code, headers, response_body)
    } else {
        // This shouldn't happen as we handle non-tuple above
        CoreHandlerResult::Simple(
            500,
            vec![("content-type".to_string(), "application/json".to_string())],
            br#"{"detail":"Internal error processing response"}"#.to_vec(),
        )
    }
}

/// Process non-tuple responses (StreamingResponse, etc.)
fn process_non_tuple_response(
    py: Python<'_>,
    result_obj: Py<PyAny>,
    skip_compression: bool,
    skip_cors: bool,
    is_head_request: bool,
    request_origin: Option<&str>,
    cors_config: Option<&CorsConfig>,
    debug: bool,
) -> CoreHandlerResult {
    let obj = result_obj.bind(py);

    // Check if it's a StreamingResponse
    let is_streaming = (|| -> PyResult<bool> {
        let m = py.import("django_bolt.responses")?;
        let cls = m.getattr("StreamingResponse")?;
        obj.is_instance(&cls)
    })()
    .unwrap_or(false);

    if !is_streaming && !obj.hasattr("content").unwrap_or(false) {
        return CoreHandlerResult::Error(error::build_error_response(
            py,
            500,
            "Handler returned unsupported response type (expected tuple or StreamingResponse)"
                .to_string(),
            vec![],
            None,
            debug,
        ));
    }

    // Extract streaming response data
    let status_code: u16 = obj
        .getattr("status_code")
        .and_then(|v| v.extract())
        .unwrap_or(200);

    let mut headers: Vec<(String, String)> = Vec::new();
    if let Ok(hobj) = obj.getattr("headers") {
        if let Ok(hdict) = hobj.cast::<PyDict>() {
            for (k, v) in hdict {
                if let (Ok(ks), Ok(vs)) = (k.extract::<String>(), v.extract::<String>()) {
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
        Err(_) => {
            return CoreHandlerResult::Error(error::build_error_response(
                py,
                500,
                "StreamingResponse missing content".to_string(),
                vec![],
                None,
                debug,
            ))
        }
    };

    let is_async_generator: bool = obj
        .getattr("is_async_generator")
        .and_then(|v| v.extract())
        .unwrap_or(false);

    // Add CORS headers if not skipped
    if !skip_cors {
        if let Some(cors_cfg) = cors_config {
            add_cors_headers_to_vec(&mut headers, request_origin, cors_cfg);
        }
    }

    CoreHandlerResult::Streaming {
        status: StatusCode::from_u16(status_code).unwrap_or(StatusCode::OK),
        headers,
        content: content_obj,
        is_async_generator,
        media_type,
        skip_compression,
        skip_cors,
        is_head_request,
    }
}

/// Get effective CORS config (route-level or global fallback)
pub fn get_effective_cors_config<'a>(
    route_metadata: Option<&'a RouteMetadata>,
    global_cors_config: Option<&'a CorsConfig>,
) -> Option<&'a CorsConfig> {
    route_metadata
        .and_then(|m| m.cors_config.as_ref())
        .or(global_cors_config)
}

/// Check if CORS should be skipped for this route
pub fn should_skip_cors(route_metadata: Option<&RouteMetadata>) -> bool {
    route_metadata
        .map(|m| m.skip.contains("cors"))
        .unwrap_or(false)
}

/// Check if compression should be skipped for this route
pub fn should_skip_compression(route_metadata: Option<&RouteMetadata>) -> bool {
    route_metadata
        .map(|m| m.skip.contains("compression"))
        .unwrap_or(false)
}

/// Check if handler needs query parameters
pub fn needs_query_params(route_metadata: Option<&RouteMetadata>) -> bool {
    route_metadata.map(|m| m.needs_query).unwrap_or(true)
}

/// Check if handler needs headers
pub fn needs_headers(route_metadata: Option<&RouteMetadata>) -> bool {
    route_metadata.map(|m| m.needs_headers).unwrap_or(true)
}

/// Check if handler needs cookies
pub fn needs_cookies(route_metadata: Option<&RouteMetadata>) -> bool {
    route_metadata.map(|m| m.needs_cookies).unwrap_or(true)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;

    #[test]
    fn test_add_cors_headers_wildcard() {
        use ahash::AHashSet;

        let cors_cfg = CorsConfig {
            origins: vec!["*".to_string()],
            origin_regexes: vec![],
            compiled_origin_regexes: vec![],
            origin_set: AHashSet::new(),
            allow_all_origins: true,
            credentials: false,
            methods: vec![],
            headers: vec![],
            expose_headers: vec![],
            max_age: 86400,
            methods_str: String::new(),
            headers_str: String::new(),
            expose_headers_str: String::new(),
            max_age_str: "86400".to_string(),
            methods_header: None,
            headers_header: None,
            expose_headers_header: None,
            max_age_header: None,
        };

        let mut headers = Vec::new();
        add_cors_headers_to_vec(&mut headers, Some("https://example.com"), &cors_cfg);

        assert!(headers.iter().any(|(k, v)| k == "access-control-allow-origin" && v == "*"));
    }

    #[test]
    fn test_should_skip_cors() {
        // Test with None metadata
        assert!(!should_skip_cors(None));

        // Test with metadata that doesn't skip CORS
        let meta = RouteMetadata::default();
        assert!(!should_skip_cors(Some(&meta)));

        // Test with metadata that skips CORS
        let mut skip_set = HashSet::new();
        skip_set.insert("cors".to_string());
        let meta_skip = RouteMetadata {
            skip: skip_set,
            ..Default::default()
        };
        assert!(should_skip_cors(Some(&meta_skip)));
    }
}

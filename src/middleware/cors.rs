use actix_web::http::header::{
    ACCESS_CONTROL_ALLOW_CREDENTIALS, ACCESS_CONTROL_ALLOW_HEADERS,
    ACCESS_CONTROL_ALLOW_METHODS, ACCESS_CONTROL_ALLOW_ORIGIN,
    ACCESS_CONTROL_EXPOSE_HEADERS, ACCESS_CONTROL_MAX_AGE, VARY,
};
use actix_web::http::StatusCode;
use actix_web::HttpResponse;
use pyo3::prelude::*;
use std::collections::HashMap;

/// Get allowed origins from route config only (no per-request Django settings lookup)
/// The Python middleware compiler should have already merged Django settings into route config
fn get_allowed_origins(config: &HashMap<String, Py<PyAny>>, py: Python) -> Vec<String> {
    config
        .get("origins")
        .and_then(|o| o.extract::<Vec<String>>(py).ok())
        .unwrap_or_else(|| vec![])
}

pub fn handle_preflight(config: &HashMap<String, Py<PyAny>>, py: Python) -> HttpResponse {
    let mut builder = HttpResponse::build(StatusCode::NO_CONTENT);

    // Get allowed origins - try Django settings first, then config
    let origins = get_allowed_origins(config, py);

    // SECURITY: If no origins configured, reject
    if origins.is_empty() {
        return HttpResponse::Forbidden()
            .content_type("text/plain; charset=utf-8")
            .body("CORS not configured for this endpoint");
    }

    // Get credentials flag
    let allow_credentials = config
        .get("credentials")
        .and_then(|c| c.extract::<bool>(py).ok())
        .unwrap_or(false);

    // SECURITY: Validate that wildcard is not combined with credentials
    let is_wildcard = origins.contains(&"*".to_string());
    if is_wildcard && allow_credentials {
        return HttpResponse::InternalServerError()
            .content_type("text/plain; charset=utf-8")
            .body("CORS misconfiguration: Cannot use wildcard '*' with credentials=true");
    }

    // For simplicity, use first origin or *
    let origin = origins.first().unwrap_or(&"*".to_string()).clone();
    builder.insert_header((ACCESS_CONTROL_ALLOW_ORIGIN, origin));

    // Get allowed methods
    let methods = config
        .get("methods")
        .and_then(|m| m.extract::<Vec<String>>(py).ok())
        .unwrap_or_else(|| vec![
            "GET".to_string(),
            "POST".to_string(),
            "PUT".to_string(),
            "PATCH".to_string(),
            "DELETE".to_string(),
            "OPTIONS".to_string(),
        ]);
    builder.insert_header((ACCESS_CONTROL_ALLOW_METHODS, methods.join(", ")));

    // Get allowed headers
    let headers = config
        .get("headers")
        .and_then(|h| h.extract::<Vec<String>>(py).ok())
        .unwrap_or_else(|| vec!["Content-Type".to_string(), "Authorization".to_string()]);
    builder.insert_header((ACCESS_CONTROL_ALLOW_HEADERS, headers.join(", ")));

    // Add credentials header if enabled (already validated above)
    if allow_credentials {
        builder.insert_header((ACCESS_CONTROL_ALLOW_CREDENTIALS, "true"));
    }

    // Max age
    let max_age = config
        .get("max_age")
        .and_then(|a| a.extract::<u32>(py).ok())
        .unwrap_or(3600);
    builder.insert_header((ACCESS_CONTROL_MAX_AGE, max_age.to_string()));

    // Add Vary header for preflight
    if !is_wildcard {
        builder.insert_header((VARY, "Origin, Access-Control-Request-Method, Access-Control-Request-Headers"));
    }

    builder.finish()
}

pub fn add_cors_headers_to_response(
    response: &mut HttpResponse,
    request_origin: Option<&str>,
    config: &HashMap<String, Py<PyAny>>,
    py: Python,
) {
    // Get allowed origins - try Django settings first, then config
    let origins = get_allowed_origins(config, py);

    // SECURITY: If no origins configured, don't add CORS headers
    if origins.is_empty() {
        return;
    }

    // Get credentials flag
    let allow_credentials = config
        .get("credentials")
        .and_then(|c| c.extract::<bool>(py).ok())
        .unwrap_or(false);

    // SECURITY: Validate wildcard + credentials (skip adding headers if misconfigured)
    let is_wildcard = origins.contains(&"*".to_string());
    if is_wildcard && allow_credentials {
        // Don't add headers - invalid configuration
        return;
    }

    // Check if request origin is allowed
    let origin_to_use = if is_wildcard {
        "*".to_string()
    } else if let Some(req_origin) = request_origin {
        if origins.iter().any(|o| o == req_origin) {
            req_origin.to_string()
        } else {
            return; // Origin not allowed
        }
    } else {
        origins.first().unwrap_or(&"*".to_string()).clone()
    };

    response.headers_mut().insert(
        ACCESS_CONTROL_ALLOW_ORIGIN,
        origin_to_use.parse().unwrap(),
    );

    // Add Vary: Origin header when not using wildcard
    if origin_to_use != "*" {
        response.headers_mut().insert(
            VARY,
            "Origin".parse().unwrap(),
        );
    }

    // Add credentials header if enabled (already validated above)
    if allow_credentials {
        response.headers_mut().insert(
            ACCESS_CONTROL_ALLOW_CREDENTIALS,
            "true".parse().unwrap(),
        );
    }

    // Add exposed headers if specified
    if let Some(expose) = config.get("expose_headers") {
        if let Ok(headers) = expose.extract::<Vec<String>>(py) {
            response.headers_mut().insert(
                ACCESS_CONTROL_EXPOSE_HEADERS,
                headers.join(", ").parse().unwrap(),
            );
        }
    }
}
//! Shared CORS handling functions used by both production middleware and test_state.rs
//!
//! This module provides the core CORS functionality:
//! - `add_cors_headers_with_config` - Add CORS headers using CorsConfig (for middleware)
//! - `add_preflight_headers_with_config` - Add preflight headers using CorsConfig (for middleware)
//! - `add_cors_response_headers` - Simple version for test_state.rs
//! - `add_preflight_headers_simple` - Simple version for test_state.rs

use actix_web::http::header::{
    HeaderMap, HeaderValue, ACCESS_CONTROL_ALLOW_CREDENTIALS, ACCESS_CONTROL_ALLOW_HEADERS,
    ACCESS_CONTROL_ALLOW_METHODS, ACCESS_CONTROL_ALLOW_ORIGIN, ACCESS_CONTROL_EXPOSE_HEADERS,
    ACCESS_CONTROL_MAX_AGE, VARY,
};
use actix_web::HttpResponse;

use crate::metadata::CorsConfig;
use crate::state::AppState;

/// Add CORS headers to a HeaderMap using CorsConfig (supports regex patterns)
/// This is the core function used by CorsMiddleware
/// Returns true if CORS headers were added (origin was allowed), false otherwise
pub fn add_cors_headers_with_config(
    headers: &mut HeaderMap,
    request_origin: Option<&str>,
    cors_config: &CorsConfig,
    state: &AppState,
) -> bool {
    // Check if CORS_ALLOW_ALL_ORIGINS is True with credentials (invalid per spec)
    if cors_config.allow_all_origins && cors_config.credentials {
        // Per CORS spec, wildcard + credentials is invalid. Reflect the request origin instead.
        if let Some(req_origin) = request_origin {
            if let Ok(val) = HeaderValue::from_str(req_origin) {
                headers.insert(ACCESS_CONTROL_ALLOW_ORIGIN, val);
            }
            headers.append(VARY, HeaderValue::from_static("Origin"));
            headers.insert(
                ACCESS_CONTROL_ALLOW_CREDENTIALS,
                HeaderValue::from_static("true"),
            );

            if let Some(ref cached_val) = cors_config.expose_headers_header {
                headers.insert(ACCESS_CONTROL_EXPOSE_HEADERS, cached_val.clone());
            }
            return true;
        }
        return false;
    }

    // Handle allow_all_origins (wildcard) without credentials
    if cors_config.allow_all_origins {
        headers.insert(
            ACCESS_CONTROL_ALLOW_ORIGIN,
            HeaderValue::from_static("*"),
        );
        if let Some(ref cached_val) = cors_config.expose_headers_header {
            headers.insert(ACCESS_CONTROL_EXPOSE_HEADERS, cached_val.clone());
        }
        return true;
    }

    // Skip work if no Origin header present
    let req_origin = match request_origin {
        Some(o) => o,
        None => return false,
    };

    // Use route-level origin_set first (O(1) lookup), then fall back to global
    let origin_set = if !cors_config.origin_set.is_empty() {
        &cors_config.origin_set
    } else if let Some(ref global_config) = state.global_cors_config {
        &global_config.origin_set
    } else {
        return false;
    };

    // Check exact match using O(1) hash set lookup
    let exact_match = origin_set.contains(req_origin);

    // Check regex match using route-level regexes, then global regexes
    let regex_match = if !cors_config.compiled_origin_regexes.is_empty() {
        cors_config
            .compiled_origin_regexes
            .iter()
            .any(|re| re.is_match(req_origin))
    } else {
        !state.cors_origin_regexes.is_empty()
            && state
                .cors_origin_regexes
                .iter()
                .any(|re| re.is_match(req_origin))
    };

    if !exact_match && !regex_match {
        return false;
    }

    // Reflect the request origin
    if let Ok(val) = HeaderValue::from_str(req_origin) {
        headers.insert(ACCESS_CONTROL_ALLOW_ORIGIN, val);
    }
    headers.append(VARY, HeaderValue::from_static("Origin"));

    if cors_config.credentials {
        headers.insert(
            ACCESS_CONTROL_ALLOW_CREDENTIALS,
            HeaderValue::from_static("true"),
        );
    }

    if let Some(ref cached_val) = cors_config.expose_headers_header {
        headers.insert(ACCESS_CONTROL_EXPOSE_HEADERS, cached_val.clone());
    }

    true
}

/// Add CORS preflight headers to a HeaderMap using CorsConfig
/// This is the core function used by CorsMiddleware for OPTIONS requests
pub fn add_preflight_headers_with_config(headers: &mut HeaderMap, cors_config: &CorsConfig) {
    if let Some(ref cached_val) = cors_config.methods_header {
        headers.insert(ACCESS_CONTROL_ALLOW_METHODS, cached_val.clone());
    }

    if let Some(ref cached_val) = cors_config.headers_header {
        headers.insert(ACCESS_CONTROL_ALLOW_HEADERS, cached_val.clone());
    }

    if let Some(ref cached_val) = cors_config.max_age_header {
        headers.insert(ACCESS_CONTROL_MAX_AGE, cached_val.clone());
    }

    // Add Vary headers for preflight requests (check for duplicates)
    let has_preflight_vary = headers
        .get(VARY)
        .and_then(|v| v.to_str().ok())
        .map(|v| v.contains("Access-Control-Request-Method"))
        .unwrap_or(false);

    if !has_preflight_vary {
        headers.append(
            VARY,
            HeaderValue::from_static("Access-Control-Request-Method, Access-Control-Request-Headers"),
        );
    }
}

/// Add CORS headers for simple responses (not preflight)
/// Used by test_state.rs - works with simple vectors instead of CorsConfig
pub fn add_cors_response_headers(
    response: &mut HttpResponse,
    request_origin: Option<&str>,
    origins: &[String],
    credentials: bool,
    expose_headers: &[String],
) -> bool {
    let is_wildcard = origins.iter().any(|o| o == "*");

    // Wildcard + credentials is invalid per CORS spec
    if is_wildcard && credentials {
        // Reflect origin instead of using wildcard
        if let Some(req_origin) = request_origin {
            if let Ok(val) = HeaderValue::from_str(req_origin) {
                response
                    .headers_mut()
                    .insert(ACCESS_CONTROL_ALLOW_ORIGIN, val);
            }
            response
                .headers_mut()
                .append(VARY, HeaderValue::from_static("Origin"));
            response.headers_mut().insert(
                ACCESS_CONTROL_ALLOW_CREDENTIALS,
                HeaderValue::from_static("true"),
            );

            if !expose_headers.is_empty() {
                if let Ok(val) = HeaderValue::from_str(&expose_headers.join(", ")) {
                    response
                        .headers_mut()
                        .insert(ACCESS_CONTROL_EXPOSE_HEADERS, val);
                }
            }
            return true;
        }
        return false;
    }

    // Handle wildcard without credentials
    if is_wildcard {
        response
            .headers_mut()
            .insert(ACCESS_CONTROL_ALLOW_ORIGIN, HeaderValue::from_static("*"));
        if !expose_headers.is_empty() {
            if let Ok(val) = HeaderValue::from_str(&expose_headers.join(", ")) {
                response
                    .headers_mut()
                    .insert(ACCESS_CONTROL_EXPOSE_HEADERS, val);
            }
        }
        return true;
    }

    // Check if origin is in allowed list
    let req_origin = match request_origin {
        Some(o) => o,
        None => return false,
    };

    if !origins.iter().any(|o| o == req_origin) {
        return false; // Origin not allowed
    }

    // Add headers
    if let Ok(val) = HeaderValue::from_str(req_origin) {
        response
            .headers_mut()
            .insert(ACCESS_CONTROL_ALLOW_ORIGIN, val);
    }
    response
        .headers_mut()
        .append(VARY, HeaderValue::from_static("Origin"));

    if credentials {
        response.headers_mut().insert(
            ACCESS_CONTROL_ALLOW_CREDENTIALS,
            HeaderValue::from_static("true"),
        );
    }

    if !expose_headers.is_empty() {
        if let Ok(val) = HeaderValue::from_str(&expose_headers.join(", ")) {
            response
                .headers_mut()
                .insert(ACCESS_CONTROL_EXPOSE_HEADERS, val);
        }
    }

    true
}

/// Build preflight response headers using simple vectors
/// Used by test_state.rs - works with simple vectors instead of CorsConfig
pub fn add_preflight_headers_simple(
    response: &mut HttpResponse,
    methods: &[String],
    headers: &[String],
    max_age: u64,
) {
    if !methods.is_empty() {
        if let Ok(val) = HeaderValue::from_str(&methods.join(", ")) {
            response
                .headers_mut()
                .insert(ACCESS_CONTROL_ALLOW_METHODS, val);
        }
    }

    if !headers.is_empty() {
        if let Ok(val) = HeaderValue::from_str(&headers.join(", ")) {
            response
                .headers_mut()
                .insert(ACCESS_CONTROL_ALLOW_HEADERS, val);
        }
    }

    if let Ok(val) = HeaderValue::from_str(&max_age.to_string()) {
        response.headers_mut().insert(ACCESS_CONTROL_MAX_AGE, val);
    }

    // Add Vary headers for preflight requests
    response.headers_mut().insert(
        VARY,
        HeaderValue::from_static("Access-Control-Request-Method, Access-Control-Request-Headers"),
    );
}

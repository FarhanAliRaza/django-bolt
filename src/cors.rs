//! Shared CORS handling functions used by both production handler.rs and test_state.rs
//!
//! This module provides the core CORS functionality:
//! - `add_cors_headers` - Add CORS headers to actual responses
//! - `add_cors_preflight_headers` - Add headers for OPTIONS preflight responses
//! - `is_origin_allowed` - Check if an origin is in the allowed list
//!
//! Both the production Actix server and the test infrastructure use these functions
//! to ensure consistent CORS behavior.

use actix_web::http::header::{
    HeaderValue, ACCESS_CONTROL_ALLOW_CREDENTIALS, ACCESS_CONTROL_ALLOW_HEADERS,
    ACCESS_CONTROL_ALLOW_METHODS, ACCESS_CONTROL_ALLOW_ORIGIN, ACCESS_CONTROL_EXPOSE_HEADERS,
    ACCESS_CONTROL_MAX_AGE, VARY,
};
use actix_web::HttpResponse;

use crate::metadata::CorsConfig;
use crate::state::AppState;

/// Add CORS headers to response using Rust-native config (NO GIL required)
/// Returns true if CORS headers were added (origin was allowed), false otherwise
/// This replaces the Python-based CORS header addition
pub fn add_cors_headers_rust(
    response: &mut HttpResponse,
    request_origin: Option<&str>,
    cors_config: &CorsConfig,
    state: &AppState,
) -> bool {
    // Check if CORS_ALLOW_ALL_ORIGINS is True with credentials (invalid per spec)
    if cors_config.allow_all_origins && cors_config.credentials {
        // Per CORS spec, wildcard + credentials is invalid. Reflect the request origin instead.
        if let Some(req_origin) = request_origin {
            if let Ok(val) = HeaderValue::from_str(req_origin) {
                response
                    .headers_mut()
                    .insert(ACCESS_CONTROL_ALLOW_ORIGIN, val);
            }
            // Add Vary: Origin when reflecting origin (append, don't replace)
            response
                .headers_mut()
                .append(VARY, HeaderValue::from_static("Origin"));

            response.headers_mut().insert(
                ACCESS_CONTROL_ALLOW_CREDENTIALS,
                HeaderValue::from_static("true"),
            );

            // Add exposed headers using cached HeaderValue
            if let Some(ref cached_val) = cors_config.expose_headers_header {
                response
                    .headers_mut()
                    .insert(ACCESS_CONTROL_EXPOSE_HEADERS, cached_val.clone());
            }
            return true; // Origin allowed
        }
        // No origin header, skip CORS
        return false;
    }

    // Handle allow_all_origins (wildcard) without credentials
    if cors_config.allow_all_origins {
        response
            .headers_mut()
            .insert(ACCESS_CONTROL_ALLOW_ORIGIN, HeaderValue::from_static("*"));

        // Add exposed headers using cached HeaderValue
        if let Some(ref cached_val) = cors_config.expose_headers_header {
            response
                .headers_mut()
                .insert(ACCESS_CONTROL_EXPOSE_HEADERS, cached_val.clone());
        }
        return true; // Origin allowed (wildcard)
    }

    // Skip work if no Origin header present
    let req_origin = match request_origin {
        Some(o) => o,
        None => return false, // No origin header, no CORS needed
    };

    // Use route-level origin_set first (O(1) lookup), then fall back to global
    let origin_set = if !cors_config.origin_set.is_empty() {
        &cors_config.origin_set
    } else if let Some(ref global_config) = state.global_cors_config {
        &global_config.origin_set
    } else {
        // No CORS configured
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

    // Origin not allowed
    if !exact_match && !regex_match {
        return false;
    }

    // Reflect the request origin (always when we get here)
    if let Ok(val) = HeaderValue::from_str(req_origin) {
        response
            .headers_mut()
            .insert(ACCESS_CONTROL_ALLOW_ORIGIN, val);
    }

    // Always add Vary: Origin when reflecting origin (append, don't replace)
    response
        .headers_mut()
        .append(VARY, HeaderValue::from_static("Origin"));

    // Add credentials header if enabled
    if cors_config.credentials {
        response.headers_mut().insert(
            ACCESS_CONTROL_ALLOW_CREDENTIALS,
            HeaderValue::from_static("true"),
        );
    }

    // Add exposed headers using cached HeaderValue (zero allocations)
    if let Some(ref cached_val) = cors_config.expose_headers_header {
        response
            .headers_mut()
            .insert(ACCESS_CONTROL_EXPOSE_HEADERS, cached_val.clone());
    }

    true // Origin allowed
}

/// Add CORS preflight headers for OPTIONS requests (uses cached HeaderValue - zero allocations)
pub fn add_cors_preflight_headers(response: &mut HttpResponse, cors_config: &CorsConfig) {
    // Use cached HeaderValue for methods (zero allocations)
    if let Some(ref cached_val) = cors_config.methods_header {
        response
            .headers_mut()
            .insert(ACCESS_CONTROL_ALLOW_METHODS, cached_val.clone());
    }

    // Use cached HeaderValue for headers (zero allocations)
    if let Some(ref cached_val) = cors_config.headers_header {
        response
            .headers_mut()
            .insert(ACCESS_CONTROL_ALLOW_HEADERS, cached_val.clone());
    }

    // Use cached HeaderValue for max_age (zero allocations)
    if let Some(ref cached_val) = cors_config.max_age_header {
        response
            .headers_mut()
            .insert(ACCESS_CONTROL_MAX_AGE, cached_val.clone());
    }

    // Add Vary headers for preflight requests
    // Per spec, vary on Access-Control-Request-Method and Access-Control-Request-Headers
    response.headers_mut().insert(
        VARY,
        HeaderValue::from_static("Access-Control-Request-Method, Access-Control-Request-Headers"),
    );
}

/// Add CORS headers for simple responses (not preflight)
/// This is a simplified version that handles the common case of adding response headers
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

/// Build preflight response headers using simple vectors (for test_state.rs)
/// This is used when we don't have a full CorsConfig with cached HeaderValues
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

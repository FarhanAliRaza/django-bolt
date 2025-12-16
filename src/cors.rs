//! Unified CORS handling - Single implementation for production and tests
//!
//! This module provides the SINGLE source of truth for all CORS functionality:
//! - `apply_cors_headers` - Add CORS headers to HeaderMap (used by middleware and tests)
//! - `apply_cors_preflight` - Add preflight headers (used by middleware and tests)
//!
//! Both production middleware and test handlers use these functions, ensuring
//! identical CORS behavior in tests and production.

use actix_web::http::header::{
    HeaderMap, HeaderValue, ACCESS_CONTROL_ALLOW_CREDENTIALS, ACCESS_CONTROL_ALLOW_HEADERS,
    ACCESS_CONTROL_ALLOW_METHODS, ACCESS_CONTROL_ALLOW_ORIGIN, ACCESS_CONTROL_EXPOSE_HEADERS,
    ACCESS_CONTROL_MAX_AGE, VARY,
};
use actix_web::HttpResponse;
use regex::Regex;

use crate::metadata::CorsConfig;
use crate::state::AppState;

// =============================================================================
// UNIFIED CORS IMPLEMENTATION - Single source of truth
// =============================================================================

/// Apply CORS headers to a HeaderMap - UNIFIED implementation for production and tests
///
/// This is the SINGLE function for CORS header handling. Both production middleware
/// and test handlers must use this function to ensure identical behavior.
///
/// # Parameters
/// - `headers`: HeaderMap to add CORS headers to
/// - `request_origin`: The Origin header from the request (None for same-origin)
/// - `cors_config`: The CORS configuration (route-level or global)
/// - `global_origin_set`: Optional global origin set for fallback (from AppState or TestApp)
/// - `global_regexes`: Optional global regex patterns for fallback
///
/// # Returns
/// true if CORS headers were added (origin was allowed), false otherwise
#[inline]
pub fn apply_cors_headers(
    headers: &mut HeaderMap,
    request_origin: Option<&str>,
    cors_config: &CorsConfig,
    global_origin_set: Option<&ahash::AHashSet<String>>,
    global_regexes: Option<&[Regex]>,
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
    } else if let Some(global_set) = global_origin_set {
        global_set
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
    } else if let Some(regexes) = global_regexes {
        !regexes.is_empty() && regexes.iter().any(|re| re.is_match(req_origin))
    } else {
        false
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

/// Apply CORS preflight headers - UNIFIED implementation
///
/// This is the SINGLE function for CORS preflight handling.
#[inline]
pub fn apply_cors_preflight(headers: &mut HeaderMap, cors_config: &CorsConfig) {
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

/// Apply CORS headers to a Vec<(String, String)> - for test handlers returning tuples
///
/// This is a convenience wrapper that converts between HeaderMap and Vec formats,
/// while using the unified apply_cors_headers implementation internally.
#[inline]
pub fn apply_cors_to_vec(
    resp_headers: &mut Vec<(String, String)>,
    request_origin: Option<&str>,
    cors_config: &CorsConfig,
    global_origin_set: Option<&ahash::AHashSet<String>>,
    global_regexes: Option<&[Regex]>,
) -> bool {
    let mut header_map = HeaderMap::new();

    let allowed = apply_cors_headers(
        &mut header_map,
        request_origin,
        cors_config,
        global_origin_set,
        global_regexes,
    );

    if allowed {
        for (name, value) in header_map.iter() {
            let name_str = name.as_str();
            if name_str.starts_with("access-control") || name_str == "vary" {
                if let Ok(val_str) = value.to_str() {
                    resp_headers.push((name_str.to_string(), val_str.to_string()));
                }
            }
        }
    }

    allowed
}

/// Apply CORS preflight headers to a Vec<(String, String)> - for test handlers
#[inline]
pub fn apply_cors_preflight_to_vec(
    resp_headers: &mut Vec<(String, String)>,
    cors_config: &CorsConfig,
) {
    let mut header_map = HeaderMap::new();
    apply_cors_preflight(&mut header_map, cors_config);

    for (name, value) in header_map.iter() {
        if let Ok(val_str) = value.to_str() {
            resp_headers.push((name.as_str().to_string(), val_str.to_string()));
        }
    }
}

// =============================================================================
// LEGACY COMPATIBILITY - Will be removed after full migration
// =============================================================================

/// DEPRECATED: Use apply_cors_headers instead
/// This wrapper provides backwards compatibility with AppState-based calls
pub fn add_cors_headers_with_config(
    headers: &mut HeaderMap,
    request_origin: Option<&str>,
    cors_config: &CorsConfig,
    state: &AppState,
) -> bool {
    apply_cors_headers(
        headers,
        request_origin,
        cors_config,
        state.global_cors_config.as_ref().map(|c| &c.origin_set),
        if state.cors_origin_regexes.is_empty() {
            None
        } else {
            Some(state.cors_origin_regexes.as_slice())
        },
    )
}

/// DEPRECATED: Use apply_cors_preflight instead
/// Wrapper for backwards compatibility with middleware
#[inline]
pub fn add_preflight_headers_with_config(headers: &mut HeaderMap, cors_config: &CorsConfig) {
    apply_cors_preflight(headers, cors_config);
}

/// DEPRECATED: Use apply_cors_to_vec or apply_cors_headers instead
/// Legacy function - kept for compatibility during migration
pub fn add_cors_response_headers(
    response: &mut HttpResponse,
    request_origin: Option<&str>,
    origins: &[String],
    credentials: bool,
    expose_headers: &[String],
) -> bool {
    // Build a temporary CorsConfig to use the unified function
    let is_wildcard = origins.iter().any(|o| o == "*");
    let origin_set: ahash::AHashSet<String> = origins.iter().cloned().collect();

    let cors_config = CorsConfig {
        origins: origins.to_vec(),
        origin_regexes: vec![],
        compiled_origin_regexes: vec![],
        origin_set,
        allow_all_origins: is_wildcard,
        credentials,
        methods: vec![],
        headers: vec![],
        expose_headers: expose_headers.to_vec(),
        max_age: 3600,
        methods_str: String::new(),
        headers_str: String::new(),
        expose_headers_str: expose_headers.join(", "),
        max_age_str: "3600".to_string(),
        methods_header: None,
        headers_header: None,
        expose_headers_header: if expose_headers.is_empty() {
            None
        } else {
            HeaderValue::from_str(&expose_headers.join(", ")).ok()
        },
        max_age_header: None,
    };

    apply_cors_headers(response.headers_mut(), request_origin, &cors_config, None, None)
}

/// DEPRECATED: Use apply_cors_preflight_to_vec instead
pub fn add_preflight_headers_simple(
    response: &mut HttpResponse,
    methods: &[String],
    headers_list: &[String],
    max_age: u64,
) {
    let cors_config = CorsConfig {
        origins: vec![],
        origin_regexes: vec![],
        compiled_origin_regexes: vec![],
        origin_set: ahash::AHashSet::new(),
        allow_all_origins: false,
        credentials: false,
        methods: methods.to_vec(),
        headers: headers_list.to_vec(),
        expose_headers: vec![],
        max_age: max_age as u32,
        methods_str: methods.join(", "),
        headers_str: headers_list.join(", "),
        expose_headers_str: String::new(),
        max_age_str: max_age.to_string(),
        methods_header: HeaderValue::from_str(&methods.join(", ")).ok(),
        headers_header: HeaderValue::from_str(&headers_list.join(", ")).ok(),
        expose_headers_header: None,
        max_age_header: HeaderValue::from_str(&max_age.to_string()).ok(),
    };

    apply_cors_preflight(response.headers_mut(), &cors_config);
}

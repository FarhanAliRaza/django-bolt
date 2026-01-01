/// Route metadata parsing from Python to Rust types
///
/// This module handles parsing Python metadata dicts into strongly-typed
/// Rust enums at registration time, eliminating per-request GIL overhead.
use actix_web::http::header::HeaderValue;
use ahash::AHashSet;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use regex::Regex;
use std::collections::{HashMap, HashSet};

use crate::middleware::auth::AuthBackend;
use crate::permissions::Guard;

/// CORS configuration parsed at startup
#[derive(Debug, Clone)]
pub struct CorsConfig {
    pub origins: Vec<String>,
    pub origin_regexes: Vec<String>, // Stored as strings for serialization
    pub compiled_origin_regexes: Vec<Regex>, // Compiled regex patterns for O(1) matching
    pub origin_set: AHashSet<String>, // O(1) lookup for exact origin matches
    pub allow_all_origins: bool,
    pub credentials: bool,
    pub methods: Vec<String>,
    pub headers: Vec<String>,
    pub expose_headers: Vec<String>,
    pub max_age: u32,
    // Pre-computed header strings to avoid per-request allocations
    pub methods_str: String,
    pub headers_str: String,
    pub expose_headers_str: String,
    pub max_age_str: String,
    // Pre-cached HeaderValue for zero-allocation header injection
    pub methods_header: Option<HeaderValue>,
    pub headers_header: Option<HeaderValue>,
    pub expose_headers_header: Option<HeaderValue>,
    pub max_age_header: Option<HeaderValue>,
}

impl Default for CorsConfig {
    fn default() -> Self {
        let methods = vec![
            "GET".to_string(),
            "POST".to_string(),
            "PUT".to_string(),
            "PATCH".to_string(),
            "DELETE".to_string(),
            "OPTIONS".to_string(),
        ];
        let headers = vec!["Content-Type".to_string(), "Authorization".to_string()];
        let expose_headers = vec![];
        let max_age = 3600;

        let methods_str = methods.join(", ");
        let headers_str = headers.join(", ");
        let expose_headers_str = expose_headers.join(", ");
        let max_age_str = max_age.to_string();

        // Pre-cache HeaderValue for zero-allocation header injection
        let methods_header = HeaderValue::from_str(&methods_str).ok();
        let headers_header = HeaderValue::from_str(&headers_str).ok();
        let expose_headers_header = if expose_headers.is_empty() {
            None
        } else {
            HeaderValue::from_str(&expose_headers_str).ok()
        };
        let max_age_header = HeaderValue::from_str(&max_age_str).ok();

        CorsConfig {
            origins: vec![],
            origin_regexes: vec![],
            compiled_origin_regexes: vec![],
            origin_set: AHashSet::new(),
            allow_all_origins: false,
            credentials: false,
            methods_str,
            headers_str,
            expose_headers_str,
            max_age_str,
            methods,
            headers,
            expose_headers,
            max_age,
            methods_header,
            headers_header,
            expose_headers_header,
            max_age_header,
        }
    }
}

impl CorsConfig {
    /// Create CorsConfig from Django settings (django-cors-headers compatible)
    pub fn from_django_settings(
        origins: Vec<String>,
        origin_regexes: Vec<String>,
        allow_all_origins: bool,
        allow_credentials: bool,
        allow_methods: Option<Vec<String>>,
        allow_headers: Option<Vec<String>>,
        expose_headers: Option<Vec<String>>,
        max_age: Option<u32>,
    ) -> Self {
        let mut config = CorsConfig::default();

        // Build origin set for O(1) lookups
        config.origin_set = origins.iter().cloned().collect();
        config.origins = origins;

        // Compile origin regex patterns at startup
        config.origin_regexes = origin_regexes.clone();
        config.compiled_origin_regexes = origin_regexes
            .iter()
            .filter_map(|pattern| {
                Regex::new(pattern).ok().or_else(|| {
                    eprintln!(
                        "[django-bolt] Warning: Invalid route-level CORS origin regex pattern: {}",
                        pattern
                    );
                    None
                })
            })
            .collect();

        config.allow_all_origins = allow_all_origins;
        config.credentials = allow_credentials;

        if let Some(methods) = allow_methods {
            config.methods_str = methods.join(", ");
            config.methods_header = HeaderValue::from_str(&config.methods_str).ok();
            config.methods = methods;
        }

        if let Some(headers) = allow_headers {
            config.headers_str = headers.join(", ");
            config.headers_header = HeaderValue::from_str(&config.headers_str).ok();
            config.headers = headers;
        }

        if let Some(expose) = expose_headers {
            config.expose_headers_str = expose.join(", ");
            config.expose_headers_header = if !expose.is_empty() {
                HeaderValue::from_str(&config.expose_headers_str).ok()
            } else {
                None
            };
            config.expose_headers = expose;
        }

        if let Some(age) = max_age {
            config.max_age_str = age.to_string();
            config.max_age_header = HeaderValue::from_str(&config.max_age_str).ok();
            config.max_age = age;
        }

        config
    }
}

/// Rate limiting configuration parsed at startup
#[derive(Debug, Clone)]
pub struct RateLimitConfig {
    pub rps: u32,
    pub burst: u32,
    pub key_type: String,
}

impl Default for RateLimitConfig {
    fn default() -> Self {
        RateLimitConfig {
            rps: 100,
            burst: 200,
            key_type: "ip".to_string(),
        }
    }
}

/// Compression configuration parsed at startup
#[derive(Debug, Clone)]
pub struct CompressionConfig {
    pub backend: String,        // "gzip", "brotli", "zstd"
    pub minimum_size: usize,    // Minimum response size to compress (bytes)
    pub gzip_fallback: bool,    // Fall back to gzip if backend not supported
}

impl Default for CompressionConfig {
    fn default() -> Self {
        CompressionConfig {
            backend: "brotli".to_string(),
            minimum_size: 500,
            gzip_fallback: true,
        }
    }
}

/// Complete route metadata including middleware, auth, and guards
#[derive(Debug, Clone)]
pub struct RouteMetadata {
    pub auth_backends: Vec<AuthBackend>,
    pub guards: Vec<Guard>,
    pub skip: HashSet<String>,
    pub cors_config: Option<CorsConfig>,
    pub rate_limit_config: Option<RateLimitConfig>,

    // Optimization flags (skip unused parsing)
    // These are computed in Python at route registration time via static analysis
    pub needs_query: bool,
    pub needs_headers: bool,
    pub needs_cookies: bool,
    #[allow(dead_code)] // Reserved for future optimization
    pub needs_path_params: bool,
    #[allow(dead_code)] // Reserved for future optimization
    pub is_static_route: bool,
}

impl RouteMetadata {
    /// Parse Python metadata dict into strongly-typed Rust metadata
    pub fn from_python(py_meta: &Bound<'_, PyDict>, py: Python) -> PyResult<Self> {
        let mut auth_backends = Vec::new();
        let mut guards = Vec::new();
        let mut skip: HashSet<String> = HashSet::new();

        // Parse middleware list and extract CORS and rate_limit configs
        let mut cors_config: Option<CorsConfig> = None;
        let mut rate_limit_config: Option<RateLimitConfig> = None;

        if let Ok(Some(mw_list)) = py_meta.get_item("middleware") {
            if let Ok(py_list) = mw_list.extract::<Vec<HashMap<String, Py<PyAny>>>>() {
                for mw_dict in py_list {
                    if let Some(mw_type) = mw_dict.get("type") {
                        if let Ok(type_str) = mw_type.extract::<String>(py) {
                            // Parse CORS config separately for fast access
                            if type_str == "cors" && cors_config.is_none() {
                                cors_config = parse_cors_config(&mw_dict, py);
                            }

                            // Parse rate_limit config separately for fast access
                            if type_str == "rate_limit" && rate_limit_config.is_none() {
                                rate_limit_config = parse_rate_limit_config(&mw_dict, py);
                            }
                        }
                    }
                }
            }
        }

        // Parse auth backends
        if let Ok(Some(auth_list)) = py_meta.get_item("auth_backends") {
            if let Ok(py_backends) = auth_list.extract::<Vec<HashMap<String, Py<PyAny>>>>() {
                for backend_dict in py_backends {
                    if let Some(backend) = parse_auth_backend(&backend_dict, py) {
                        auth_backends.push(backend);
                    }
                }
            }
        }

        // Parse guards
        if let Ok(Some(guard_list)) = py_meta.get_item("guards") {
            if let Ok(py_guards) = guard_list.extract::<Vec<HashMap<String, Py<PyAny>>>>() {
                for guard_dict in py_guards {
                    if let Some(guard) = parse_guard(&guard_dict, py) {
                        guards.push(guard);
                    }
                }
            }
        }

        // Parse skip list (e.g., ["compression", "cors"]) into a set
        if let Ok(Some(skip_list)) = py_meta.get_item("skip") {
            if let Ok(names) = skip_list.extract::<Vec<String>>() {
                for name in names {
                    skip.insert(name.to_lowercase());
                }
            }
        }

        // Parse optimization flags (default to true for backward compatibility)
        // These flags indicate which request components the handler actually needs
        let needs_query = py_meta
            .get_item("needs_query")
            .ok()
            .flatten()
            .and_then(|v| v.extract::<bool>().ok())
            .unwrap_or(true);

        let needs_headers = py_meta
            .get_item("needs_headers")
            .ok()
            .flatten()
            .and_then(|v| v.extract::<bool>().ok())
            .unwrap_or(true);

        let needs_cookies = py_meta
            .get_item("needs_cookies")
            .ok()
            .flatten()
            .and_then(|v| v.extract::<bool>().ok())
            .unwrap_or(true);

        let needs_path_params = py_meta
            .get_item("needs_path_params")
            .ok()
            .flatten()
            .and_then(|v| v.extract::<bool>().ok())
            .unwrap_or(true);

        let is_static_route = py_meta
            .get_item("is_static_route")
            .ok()
            .flatten()
            .and_then(|v| v.extract::<bool>().ok())
            .unwrap_or(false);

        Ok(RouteMetadata {
            auth_backends,
            guards,
            skip,
            cors_config,
            rate_limit_config,
            needs_query,
            needs_headers,
            needs_cookies,
            needs_path_params,
            is_static_route,
        })
    }
}

/// Parse CORS configuration from middleware dict
fn parse_cors_config(dict: &HashMap<String, Py<PyAny>>, py: Python) -> Option<CorsConfig> {
    let mut config = CorsConfig::default();

    // Parse origins and build origin set for O(1) lookups
    if let Some(origins_py) = dict.get("origins") {
        if let Ok(origins) = origins_py.extract::<Vec<String>>(py) {
            // Detect wildcard origin
            config.allow_all_origins = origins.iter().any(|o| o == "*");
            config.origin_set = origins.iter().cloned().collect();
            config.origins = origins;
        }
    }

    // Parse origin_regexes and compile them at startup
    if let Some(regexes_py) = dict.get("origin_regexes") {
        if let Ok(regex_patterns) = regexes_py.extract::<Vec<String>>(py) {
            config.origin_regexes = regex_patterns.clone();
            config.compiled_origin_regexes = regex_patterns.iter()
                .filter_map(|pattern| {
                    Regex::new(pattern).ok().or_else(|| {
                        eprintln!("[django-bolt] Warning: Invalid route-level CORS origin regex pattern: {}", pattern);
                        None
                    })
                })
                .collect();
        }
    }

    // Parse credentials
    if let Some(cred_py) = dict.get("credentials") {
        if let Ok(cred) = cred_py.extract::<bool>(py) {
            config.credentials = cred;
        }
    }

    // Parse methods (optional, has defaults)
    if let Some(methods_py) = dict.get("methods") {
        if let Ok(methods) = methods_py.extract::<Vec<String>>(py) {
            config.methods_str = methods.join(", ");
            config.methods_header = HeaderValue::from_str(&config.methods_str).ok();
            config.methods = methods;
        }
    }

    // Parse headers (optional, has defaults)
    if let Some(headers_py) = dict.get("headers") {
        if let Ok(headers) = headers_py.extract::<Vec<String>>(py) {
            config.headers_str = headers.join(", ");
            config.headers_header = HeaderValue::from_str(&config.headers_str).ok();
            config.headers = headers;
        }
    }

    // Parse expose_headers (optional)
    if let Some(expose_py) = dict.get("expose_headers") {
        if let Ok(expose) = expose_py.extract::<Vec<String>>(py) {
            config.expose_headers_str = expose.join(", ");
            config.expose_headers_header = if !expose.is_empty() {
                HeaderValue::from_str(&config.expose_headers_str).ok()
            } else {
                None
            };
            config.expose_headers = expose;
        }
    }

    // Parse max_age (optional)
    if let Some(age_py) = dict.get("max_age") {
        if let Ok(age) = age_py.extract::<u32>(py) {
            config.max_age_str = age.to_string();
            config.max_age_header = HeaderValue::from_str(&config.max_age_str).ok();
            config.max_age = age;
        }
    }

    Some(config)
}

/// Parse rate limiting configuration from middleware dict
fn parse_rate_limit_config(
    dict: &HashMap<String, Py<PyAny>>,
    py: Python,
) -> Option<RateLimitConfig> {
    let mut config = RateLimitConfig::default();

    // Parse rps (required)
    if let Some(rps_py) = dict.get("rps") {
        if let Ok(rps) = rps_py.extract::<u32>(py) {
            config.rps = rps;
        }
    }

    // Parse burst (optional, defaults to 2x rps)
    if let Some(burst_py) = dict.get("burst") {
        if let Ok(burst) = burst_py.extract::<u32>(py) {
            config.burst = burst;
        }
    } else {
        // If burst not specified, default to 2x rps
        config.burst = config.rps * 2;
    }

    // Parse key_type (optional, defaults to "ip")
    if let Some(key_py) = dict.get("key") {
        if let Ok(key_type) = key_py.extract::<String>(py) {
            config.key_type = key_type;
        }
    }

    Some(config)
}

/// Parse a single auth backend from Python dict
fn parse_auth_backend(dict: &HashMap<String, Py<PyAny>>, py: Python) -> Option<AuthBackend> {
    let backend_type = dict.get("type")?.extract::<String>(py).ok()?;

    match backend_type.as_str() {
        "jwt" => {
            let secret = dict.get("secret")?.extract::<String>(py).ok()?;
            let algorithms = dict
                .get("algorithms")
                .and_then(|a| a.extract::<Vec<String>>(py).ok())
                .unwrap_or_else(|| vec!["HS256".to_string()]);
            let header = dict
                .get("header")
                .and_then(|h| h.extract::<String>(py).ok())
                .unwrap_or_else(|| "authorization".to_string());
            let audience = dict
                .get("audience")
                .and_then(|a| a.extract::<String>(py).ok());
            let issuer = dict
                .get("issuer")
                .and_then(|i| i.extract::<String>(py).ok());

            Some(AuthBackend::JWT {
                secret,
                algorithms,
                header,
                audience,
                issuer,
            })
        }
        "api_key" => {
            let api_keys_list = dict
                .get("api_keys")
                .and_then(|k| k.extract::<Vec<String>>(py).ok())
                .unwrap_or_default();
            let api_keys: HashSet<String> = api_keys_list.into_iter().collect();

            let header = dict
                .get("header")
                .and_then(|h| h.extract::<String>(py).ok())
                .unwrap_or_else(|| "x-api-key".to_string());

            let key_permissions = dict
                .get("key_permissions")
                .and_then(|kp| kp.extract::<HashMap<String, Vec<String>>>(py).ok())
                .unwrap_or_default();

            Some(AuthBackend::APIKey {
                api_keys,
                header,
                key_permissions,
            })
        }
        _ => None,
    }
}

/// Parse a single guard from Python dict
fn parse_guard(dict: &HashMap<String, Py<PyAny>>, py: Python) -> Option<Guard> {
    let guard_type = dict.get("type")?.extract::<String>(py).ok()?;

    match guard_type.as_str() {
        "allow_any" => Some(Guard::AllowAny),
        "is_authenticated" => Some(Guard::IsAuthenticated),
        "is_superuser" => Some(Guard::IsSuperuser),
        "is_staff" => Some(Guard::IsStaff),
        "has_permission" => {
            let perm = dict.get("permission")?.extract::<String>(py).ok()?;
            Some(Guard::HasPermission(perm))
        }
        "has_any_permission" => {
            let perms = dict.get("permissions")?.extract::<Vec<String>>(py).ok()?;
            Some(Guard::HasAnyPermission(perms))
        }
        "has_all_permissions" => {
            let perms = dict.get("permissions")?.extract::<Vec<String>>(py).ok()?;
            Some(Guard::HasAllPermissions(perms))
        }
        _ => None,
    }
}

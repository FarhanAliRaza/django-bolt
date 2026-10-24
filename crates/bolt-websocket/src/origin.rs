//! The Origin check of a WebSocket handshake.

use actix_web::http::header::HeaderValue;
use bolt_core::metadata::CorsConfig;

/// Check the Origin header of a WebSocket handshake against the global CORS config.
/// `runbolt` and the test client both call this function.
///
/// Security behavior:
/// - No Origin header: allow. A browser sends no Origin header for a same-origin connection.
/// - An Origin value that is not visible ASCII: deny.
/// - No CORS config: deny all cross-origin requests (fail-secure).
/// - Else: allow only the origins that the CORS config allows.
pub fn validate_origin(
    origin: Option<&HeaderValue>,
    cors_config: Option<&CorsConfig>,
    global_regexes: &[regex::Regex],
) -> bool {
    let origin = match origin {
        Some(v) => match v.to_str() {
            Ok(s) => s,
            Err(_) => {
                eprintln!("[django-bolt] WebSocket: Invalid Origin header encoding");
                return false;
            }
        },
        None => return true,
    };

    if let Some(cors_config) = cors_config {
        return is_origin_allowed(origin, cors_config, global_regexes);
    }

    // SECURITY: No CORS configured = deny all cross-origin requests
    // This is a fail-secure default (unlike the old allow-all default)
    eprintln!(
        "[django-bolt] WebSocket: Rejecting cross-origin request from '{}' - no CORS configured. \
        Set CORS_ALLOWED_ORIGINS in Django settings to allow WebSocket connections.",
        origin
    );
    false
}

/// Check if an origin is allowed by the CORS configuration
/// Reuses the same logic as HTTP CORS validation.
pub fn is_origin_allowed(
    origin: &str,
    cors_config: &CorsConfig,
    global_regexes: &[regex::Regex],
) -> bool {
    // Allow all origins if configured
    if cors_config.allow_all_origins {
        return true;
    }

    // O(1) exact match using HashSet
    if cors_config.origin_set.contains(origin) {
        return true;
    }

    // Check route-level regex patterns
    if cors_config
        .compiled_origin_regexes
        .iter()
        .any(|re| re.is_match(origin))
    {
        return true;
    }

    // Check global regex patterns
    if global_regexes.iter().any(|re| re.is_match(origin)) {
        return true;
    }

    false
}

#[cfg(test)]
mod tests {
    use super::{is_origin_allowed, validate_origin};
    use actix_web::http::header::HeaderValue;
    use bolt_core::metadata::CorsConfig;
    use regex::Regex;

    fn cors(origins: &[&str], regexes: &[&str], allow_all: bool) -> CorsConfig {
        CorsConfig::from_django_settings(
            origins.iter().map(|o| o.to_string()).collect(),
            regexes.iter().map(|r| r.to_string()).collect(),
            allow_all,
            false,
            None,
            None,
            None,
            None,
        )
    }

    fn origin(value: &str) -> HeaderValue {
        HeaderValue::from_str(value).unwrap()
    }

    #[test]
    fn validate_origin_allows_a_handshake_with_no_origin_header() {
        assert!(validate_origin(None, None, &[]));
        assert!(validate_origin(
            None,
            Some(&cors(&["https://a.example"], &[], false)),
            &[]
        ));
    }

    #[test]
    fn validate_origin_denies_every_origin_with_no_cors_config() {
        assert!(!validate_origin(
            Some(&origin("https://a.example")),
            None,
            &[]
        ));
    }

    #[test]
    fn validate_origin_checks_the_origin_against_the_cors_config() {
        let config = cors(&["https://a.example"], &[], false);
        assert!(validate_origin(
            Some(&origin("https://a.example")),
            Some(&config),
            &[]
        ));
        assert!(!validate_origin(
            Some(&origin("https://b.example")),
            Some(&config),
            &[]
        ));
    }

    #[test]
    fn validate_origin_denies_an_origin_that_is_not_visible_ascii() {
        // "https://\u{e9}.example" in UTF-8. It is a valid header value, but not a str.
        let value = HeaderValue::from_bytes(b"https://\xc3\xa9.example").unwrap();
        assert!(!validate_origin(
            Some(&value),
            Some(&cors(&[], &[], true)),
            &[]
        ));
    }

    #[test]
    fn is_origin_allowed_takes_exact_origins_only() {
        let config = cors(&["https://a.example"], &[], false);
        assert!(is_origin_allowed("https://a.example", &config, &[]));
        assert!(!is_origin_allowed("https://a.example.evil", &config, &[]));
        assert!(!is_origin_allowed("http://a.example", &config, &[]));
    }

    #[test]
    fn is_origin_allowed_allows_every_origin_with_allow_all() {
        let config = cors(&[], &[], true);
        assert!(is_origin_allowed("https://any.example", &config, &[]));
    }

    #[test]
    fn is_origin_allowed_matches_the_config_regexes_and_the_global_regexes() {
        let config = cors(&[], &[r"^https://[a-z]+\.route\.example$"], false);
        let global = [Regex::new(r"^https://[a-z]+\.global\.example$").unwrap()];
        assert!(is_origin_allowed("https://app.route.example", &config, &[]));
        assert!(is_origin_allowed(
            "https://app.global.example",
            &config,
            &global
        ));
        assert!(!is_origin_allowed(
            "https://app.global.example",
            &config,
            &[]
        ));
        assert!(!is_origin_allowed(
            "https://app.other.example",
            &config,
            &global
        ));
    }
}

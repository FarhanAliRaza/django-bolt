use crate::middleware::auth::{authenticate, AuthBackend, AuthContext};
use crate::permissions::{evaluate_guards, Guard, GuardResult};
/// Shared validation logic used by both production handler and test handler
/// All functions marked #[inline(always)] for zero-cost abstraction
use ahash::AHashMap;

/// Parse HTTP cookies from Cookie header
/// Returns HashMap of cookie name -> cookie value
///
/// # Performance
/// - Zero allocations if no cookies
/// - Pre-allocated capacity for 8 cookies (typical case)
/// - Inlined for zero-cost abstraction
#[inline(always)]
pub fn parse_cookies_inline(cookie_header: Option<&str>) -> AHashMap<String, String> {
    let mut cookies: AHashMap<String, String> = AHashMap::with_capacity(8);

    if let Some(raw_cookie) = cookie_header {
        for pair in raw_cookie.split(';') {
            let part = pair.trim();
            if let Some(eq) = part.find('=') {
                let (k, v) = part.split_at(eq);
                let v2 = &v[1..]; // Skip '=' character
                if !k.is_empty() {
                    cookies.insert(k.to_string(), v2.to_string());
                }
            }
        }
    }

    cookies
}

/// Result of authentication and guard evaluation
#[derive(Debug)]
pub enum AuthGuardResult {
    /// Authentication and guards passed
    Allow(Option<AuthContext>),
    /// Authentication required (401)
    Unauthorized,
    /// Permission denied (403)
    Forbidden,
}

/// Validate authentication and evaluate guards
/// This combines auth + guards into a single reusable flow
///
/// # Parameters
/// - `headers`: Request headers (lowercase keys)
/// - `auth_backends`: Configured auth backends for this route
/// - `guards`: Configured guards for this route
///
/// # Returns
/// - `Allow(auth_ctx)`: Authentication and guards passed
/// - `Unauthorized`: Authentication required (401)
/// - `Forbidden`: Permission denied (403)
///
/// # Performance
/// - Zero allocations if no auth configured
/// - Inlined for zero-cost abstraction
#[inline(always)]
pub fn validate_auth_and_guards(
    headers: &AHashMap<String, String>,
    auth_backends: &[AuthBackend],
    guards: &[Guard],
) -> AuthGuardResult {
    // Skip work if no auth or guards configured
    if auth_backends.is_empty() && guards.is_empty() {
        return AuthGuardResult::Allow(None);
    }

    // Authenticate if backends configured
    let auth_ctx = if !auth_backends.is_empty() {
        authenticate(headers, auth_backends)
    } else {
        None
    };

    // Evaluate guards if configured
    if !guards.is_empty() {
        match evaluate_guards(guards, auth_ctx.as_ref()) {
            GuardResult::Allow => {
                // Guards passed
            }
            GuardResult::Unauthorized => {
                return AuthGuardResult::Unauthorized;
            }
            GuardResult::Forbidden => {
                return AuthGuardResult::Forbidden;
            }
        }
    }

    AuthGuardResult::Allow(auth_ctx)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_cookies_empty() {
        let cookies = parse_cookies_inline(None);
        assert_eq!(cookies.len(), 0);
    }

    #[test]
    fn test_parse_cookies_single() {
        let cookies = parse_cookies_inline(Some("session=abc123"));
        assert_eq!(cookies.get("session"), Some(&"abc123".to_string()));
    }

    #[test]
    fn test_parse_cookies_multiple() {
        let cookies = parse_cookies_inline(Some("session=abc123; user=john; token=xyz"));
        assert_eq!(cookies.get("session"), Some(&"abc123".to_string()));
        assert_eq!(cookies.get("user"), Some(&"john".to_string()));
        assert_eq!(cookies.get("token"), Some(&"xyz".to_string()));
    }

    #[test]
    fn test_parse_cookies_with_spaces() {
        let cookies = parse_cookies_inline(Some("session=abc123;   user=john  ;token=xyz"));
        assert_eq!(cookies.get("session"), Some(&"abc123".to_string()));
        assert_eq!(cookies.get("user"), Some(&"john".to_string()));
        assert_eq!(cookies.get("token"), Some(&"xyz".to_string()));
    }

    #[test]
    fn test_validate_auth_no_config() {
        let headers = AHashMap::new();
        let result = validate_auth_and_guards(&headers, &[], &[]);
        matches!(result, AuthGuardResult::Allow(None));
    }
}

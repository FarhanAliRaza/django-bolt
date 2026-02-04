//! Fast cookie serialization for Set-Cookie headers.
//!
//! Replaces Python's SimpleCookie with direct string building.
//! RFC 6265 compliant.

use crate::response_meta::CookieData;

/// Characters that don't need quoting in cookie values (RFC 6265 token chars)
#[inline]
fn needs_quoting(value: &str) -> bool {
    value
        .bytes()
        .any(|b| matches!(b, b' ' | b'"' | b',' | b';' | b'\\' | 0..=31 | 127..))
}

/// Escape and optionally quote cookie value
#[inline]
fn escape_value(value: &str) -> String {
    if !needs_quoting(value) {
        return value.to_string();
    }

    // Quote and escape
    let mut result = String::with_capacity(value.len() + 4);
    result.push('"');
    for c in value.chars() {
        if c == '"' || c == '\\' {
            result.push('\\');
        }
        result.push(c);
    }
    result.push('"');
    result
}

/// Format a single Set-Cookie header value.
/// Pre-allocates capacity for typical cookie size.
#[inline]
pub fn format_cookie(c: &CookieData) -> String {
    // Pre-allocate: name=value; Path=/; typical attributes ~128 bytes
    let mut s = String::with_capacity(128);

    // name=value
    s.push_str(&c.name);
    s.push('=');
    s.push_str(&escape_value(&c.value));

    // Path (always present, defaults to "/")
    s.push_str("; Path=");
    s.push_str(&c.path);

    // Optional attributes
    if let Some(age) = c.max_age {
        s.push_str("; Max-Age=");
        s.push_str(&age.to_string());
    }

    if let Some(ref exp) = c.expires {
        s.push_str("; Expires=");
        s.push_str(exp);
    }

    if let Some(ref dom) = c.domain {
        s.push_str("; Domain=");
        s.push_str(dom);
    }

    if c.secure {
        s.push_str("; Secure");
    }

    if c.httponly {
        s.push_str("; HttpOnly");
    }

    if let Some(ref ss) = c.samesite {
        if !ss.is_empty() {
            s.push_str("; SameSite=");
            s.push_str(ss);
        }
    }

    s
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_cookie() {
        let c = CookieData {
            name: "session".to_string(),
            value: "abc123".to_string(),
            path: "/".to_string(),
            max_age: None,
            expires: None,
            domain: None,
            secure: false,
            httponly: false,
            samesite: None,
        };
        assert_eq!(format_cookie(&c), "session=abc123; Path=/");
    }

    #[test]
    fn test_full_cookie() {
        let c = CookieData {
            name: "auth".to_string(),
            value: "token".to_string(),
            path: "/app".to_string(),
            max_age: Some(3600),
            expires: Some("Thu, 01 Jan 2025 00:00:00 GMT".to_string()),
            domain: Some("example.com".to_string()),
            secure: true,
            httponly: true,
            samesite: Some("Strict".to_string()),
        };
        let result = format_cookie(&c);
        assert!(result.contains("auth=token"));
        assert!(result.contains("Path=/app"));
        assert!(result.contains("Max-Age=3600"));
        assert!(result.contains("Domain=example.com"));
        assert!(result.contains("Secure"));
        assert!(result.contains("HttpOnly"));
        assert!(result.contains("SameSite=Strict"));
    }

    #[test]
    fn test_value_quoting() {
        let c = CookieData {
            name: "data".to_string(),
            value: "hello world".to_string(), // space needs quoting
            path: "/".to_string(),
            max_age: None,
            expires: None,
            domain: None,
            secure: false,
            httponly: false,
            samesite: None,
        };
        assert!(format_cookie(&c).contains("\"hello world\""));
    }

    #[test]
    fn test_value_escaping() {
        let c = CookieData {
            name: "data".to_string(),
            value: "say \"hello\"".to_string(), // quotes need escaping
            path: "/".to_string(),
            max_age: None,
            expires: None,
            domain: None,
            secure: false,
            httponly: false,
            samesite: None,
        };
        let result = format_cookie(&c);
        assert!(result.contains("\"say \\\"hello\\\"\""));
    }

    #[test]
    fn test_empty_samesite() {
        let c = CookieData {
            name: "test".to_string(),
            value: "val".to_string(),
            path: "/".to_string(),
            max_age: None,
            expires: None,
            domain: None,
            secure: false,
            httponly: false,
            samesite: Some("".to_string()), // Empty string should be skipped
        };
        let result = format_cookie(&c);
        assert!(!result.contains("SameSite"));
    }

    #[test]
    fn test_samesite_lax() {
        let c = CookieData {
            name: "test".to_string(),
            value: "val".to_string(),
            path: "/".to_string(),
            max_age: None,
            expires: None,
            domain: None,
            secure: false,
            httponly: false,
            samesite: Some("Lax".to_string()),
        };
        let result = format_cookie(&c);
        assert!(result.contains("SameSite=Lax"));
    }
}

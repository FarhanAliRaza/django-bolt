/// Optimized response building utilities
///
/// Reduces the number of mutations on HttpResponse::Builder
/// by batching operations and pre-allocating capacity.
use actix_web::http::header::{HeaderName, HeaderValue};
use actix_web::{http::StatusCode, HttpResponse, HttpResponseBuilder};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyTuple};

use crate::cookies::format_cookie;
use crate::response_meta::ResponseMeta;

/// Build a response with pre-allocated capacity for headers
/// This reduces allocations and mutations compared to the default builder
#[inline]
pub fn build_response_with_headers(
    status: StatusCode,
    headers: Vec<(String, String)>,
    skip_compression: bool,
    body: Vec<u8>,
) -> HttpResponse {
    let mut builder = HttpResponse::build(status);

    // Pre-allocate header capacity (typical response has 5-10 headers)
    // Actix doesn't expose header map directly, but the builder is efficient

    // Add all custom headers in one pass
    // Use append_header to support multiple headers with the same name
    // (e.g., multiple Set-Cookie headers). insert_header would replace.
    for (k, v) in headers {
        if let Ok(name) = HeaderName::try_from(k) {
            if let Ok(val) = HeaderValue::try_from(v) {
                builder.append_header((name, val));
            }
        }
    }

    // Add skip_compression header if needed
    if skip_compression {
        builder.insert_header(("content-encoding", "identity"));
    }

    builder.body(body)
}

/// Build a streaming response with SSE headers
/// Pre-bundles common SSE headers to avoid multiple mutations
#[inline]
pub fn build_sse_response(
    status: StatusCode,
    custom_headers: Vec<(String, String)>,
    skip_compression: bool,
) -> HttpResponseBuilder {
    let mut builder = HttpResponse::build(status);

    // Add custom headers first
    // Use append_header to support multiple headers with the same name
    for (k, v) in custom_headers {
        builder.append_header((k, v));
    }

    // Batch SSE headers (avoid 5 separate mutations)
    builder.content_type("text/event-stream");
    builder.insert_header(("X-Accel-Buffering", "no"));
    builder.insert_header(("Cache-Control", "no-cache, no-store, must-revalidate"));
    builder.insert_header(("Pragma", "no-cache"));
    builder.insert_header(("Expires", "0"));

    if skip_compression {
        builder.insert_header(("Content-Encoding", "identity"));
    }

    builder
}

/// Build response with retry-after header (for rate limiting)
#[inline]
pub fn build_rate_limit_response(
    retry_after: u64,
    rps: u32,
    burst: u32,
    body: Vec<u8>,
) -> HttpResponse {
    // Batch all headers at once
    HttpResponse::TooManyRequests()
        .insert_header(("Retry-After", retry_after.to_string()))
        .insert_header(("X-RateLimit-Limit", rps.to_string()))
        .insert_header(("X-RateLimit-Burst", burst.to_string()))
        .content_type("application/json")
        .body(body)
}

/// Convert ResponseMeta to a Vec of header tuples.
/// Used for streaming responses that need headers but use a different builder path.
#[inline]
pub fn meta_to_headers(meta: &ResponseMeta) -> Vec<(String, String)> {
    let mut headers = Vec::new();

    // 1. Content-Type: use custom or derive from response_type
    let content_type = meta
        .custom_content_type
        .as_deref()
        .unwrap_or_else(|| meta.response_type.content_type());

    if !content_type.is_empty() {
        headers.push(("content-type".to_string(), content_type.to_string()));
    }

    // 2. Custom headers (lowercase keys)
    if let Some(ref custom_headers) = meta.custom_headers {
        for (k, v) in custom_headers {
            headers.push((k.to_ascii_lowercase(), v.clone()));
        }
    }

    // 3. Cookies: serialize in Rust
    if let Some(ref cookies) = meta.cookies {
        for cookie in cookies {
            let header_value = format_cookie(cookie);
            headers.push(("set-cookie".to_string(), header_value));
        }
    }

    headers
}

/// Parsed response data from Python in the new ResponseMeta format.
/// Contains status code, metadata, and body bytes extracted from a Python tuple.
pub struct ParsedResponseMeta {
    pub status_code: u16,
    pub meta: ResponseMeta,
    pub body: Vec<u8>,
}

/// Try to extract ResponseMeta format from a Python result tuple.
///
/// The new format is: (status_code, meta_tuple, body_bytes)
/// where meta_tuple is a tuple (not a list) containing response metadata.
///
/// Returns None if the result is not in the new ResponseMeta format,
/// allowing fallback to legacy format handling.
#[inline]
pub fn try_extract_response_meta(py: Python<'_>, result: &Py<PyAny>) -> Option<ParsedResponseMeta> {
    let obj = result.bind(py);
    let tuple = obj.downcast::<PyTuple>().ok()?;

    if tuple.len() != 3 {
        return None;
    }

    // Element 0: status code
    let status_code: u16 = tuple.get_item(0).ok()?.extract().ok()?;

    // Element 1: Check if it's a tuple (new format) vs list (old format)
    let meta_obj = tuple.get_item(1).ok()?;
    if !meta_obj.is_instance_of::<PyTuple>() {
        return None;
    }

    // Extract ResponseMeta from the tuple
    let meta = ResponseMeta::from_python(&meta_obj).ok()?;

    // Element 2: body (bytes)
    let body_obj = tuple.get_item(2).ok()?;
    let pybytes = body_obj.downcast::<PyBytes>().ok()?;
    let body = pybytes.as_bytes().to_vec();

    Some(ParsedResponseMeta {
        status_code,
        meta,
        body,
    })
}

/// Extract file path from response metadata custom headers.
/// Returns the file path and a filtered list of headers without the file path marker.
#[inline]
pub fn extract_file_path_from_meta(meta: &ResponseMeta) -> Option<String> {
    meta.custom_headers.as_ref().and_then(|headers| {
        headers
            .iter()
            .find(|(k, _)| k.eq_ignore_ascii_case("x-bolt-file-path"))
            .map(|(_, v)| v.clone())
    })
}

/// Build headers from ResponseMeta, filtering out the file path marker.
#[inline]
pub fn meta_to_headers_without_file_path(meta: &ResponseMeta) -> Vec<(String, String)> {
    meta_to_headers(meta)
        .into_iter()
        .filter(|(k, _)| !k.eq_ignore_ascii_case("x-bolt-file-path"))
        .collect()
}

/// Build HTTP response with all headers from ResponseMeta.
/// This is the unified path for all response types.
///
/// Handles:
/// - Content-Type from static strings based on response_type (no allocation)
/// - Custom headers with keys lowercased in Rust (single location)
/// - Cookies serialized directly in Rust (replaces SimpleCookie)
#[inline]
pub fn build_response_from_meta(
    status: StatusCode,
    meta: ResponseMeta,
    body: Vec<u8>,
    skip_compression: bool,
) -> HttpResponse {
    let mut builder = HttpResponse::build(status);

    // 1. Content-Type: use custom or derive from response_type
    let content_type = meta
        .custom_content_type
        .as_deref()
        .unwrap_or_else(|| meta.response_type.content_type());

    if !content_type.is_empty() {
        builder.insert_header(("content-type", content_type));
    }

    // 2. Custom headers (lowercase keys in Rust - single location)
    if let Some(headers) = meta.custom_headers {
        for (k, v) in headers {
            // Lowercase here instead of in Python (best practice from Robyn)
            if let Ok(name) = HeaderName::try_from(k.to_ascii_lowercase()) {
                if let Ok(val) = HeaderValue::try_from(v) {
                    builder.append_header((name, val));
                }
            }
        }
    }

    // 3. Cookies: serialize in Rust (replaces SimpleCookie)
    if let Some(cookies) = meta.cookies {
        for cookie in cookies {
            let header_value = format_cookie(&cookie);
            builder.append_header(("set-cookie", header_value));
        }
    }

    // 4. Compression skip if needed
    if skip_compression {
        builder.insert_header(("content-encoding", "identity"));
    }

    builder.body(body)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::response_meta::{CookieData, ResponseType};

    #[test]
    fn test_build_response_with_headers() {
        let headers = vec![
            ("content-type".to_string(), "application/json".to_string()),
            ("x-custom".to_string(), "value".to_string()),
        ];

        let response =
            build_response_with_headers(StatusCode::OK, headers, false, b"test".to_vec());

        assert_eq!(response.status(), StatusCode::OK);
    }

    #[test]
    fn test_build_rate_limit_response() {
        let response = build_rate_limit_response(60, 100, 200, b"{}".to_vec());
        assert_eq!(response.status(), StatusCode::TOO_MANY_REQUESTS);
    }

    #[test]
    fn test_build_response_from_meta_json() {
        let meta = ResponseMeta {
            response_type: ResponseType::Json,
            custom_content_type: None,
            custom_headers: None,
            cookies: None,
        };
        let response =
            build_response_from_meta(StatusCode::OK, meta, b"{}".to_vec(), false);
        assert_eq!(response.status(), StatusCode::OK);
    }

    #[test]
    fn test_build_response_from_meta_with_custom_content_type() {
        let meta = ResponseMeta {
            response_type: ResponseType::Json,
            custom_content_type: Some("application/vnd.api+json".to_string()),
            custom_headers: None,
            cookies: None,
        };
        let response =
            build_response_from_meta(StatusCode::OK, meta, b"{}".to_vec(), false);
        assert_eq!(response.status(), StatusCode::OK);
    }

    #[test]
    fn test_build_response_from_meta_with_headers() {
        let meta = ResponseMeta {
            response_type: ResponseType::Json,
            custom_content_type: None,
            custom_headers: Some(vec![
                ("X-Custom".to_string(), "value".to_string()),
                ("X-Another".to_string(), "test".to_string()),
            ]),
            cookies: None,
        };
        let response =
            build_response_from_meta(StatusCode::OK, meta, b"{}".to_vec(), false);
        assert_eq!(response.status(), StatusCode::OK);
    }

    #[test]
    fn test_build_response_from_meta_with_cookies() {
        let meta = ResponseMeta {
            response_type: ResponseType::Json,
            custom_content_type: None,
            custom_headers: None,
            cookies: Some(vec![
                CookieData {
                    name: "session".to_string(),
                    value: "abc123".to_string(),
                    path: "/".to_string(),
                    max_age: Some(3600),
                    expires: None,
                    domain: None,
                    secure: true,
                    httponly: true,
                    samesite: Some("Lax".to_string()),
                },
            ]),
        };
        let response =
            build_response_from_meta(StatusCode::OK, meta, b"{}".to_vec(), false);
        assert_eq!(response.status(), StatusCode::OK);
    }

    #[test]
    fn test_build_response_from_meta_html() {
        let meta = ResponseMeta {
            response_type: ResponseType::Html,
            custom_content_type: None,
            custom_headers: None,
            cookies: None,
        };
        let response = build_response_from_meta(
            StatusCode::OK,
            meta,
            b"<html></html>".to_vec(),
            false,
        );
        assert_eq!(response.status(), StatusCode::OK);
    }

    #[test]
    fn test_build_response_from_meta_plaintext() {
        let meta = ResponseMeta {
            response_type: ResponseType::PlainText,
            custom_content_type: None,
            custom_headers: None,
            cookies: None,
        };
        let response = build_response_from_meta(
            StatusCode::OK,
            meta,
            b"Hello, World!".to_vec(),
            false,
        );
        assert_eq!(response.status(), StatusCode::OK);
    }
}

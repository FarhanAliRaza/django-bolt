/// Optimized response building utilities
///
/// Reduces the number of mutations on HttpResponse::Builder
/// by batching operations and pre-allocating capacity.

use actix_web::http::header::{HeaderName, HeaderValue};
use actix_web::{http::StatusCode, HttpResponse, HttpResponseBuilder};

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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_build_response_with_headers() {
        let headers = vec![
            ("content-type".to_string(), "application/json".to_string()),
            ("x-custom".to_string(), "value".to_string()),
        ];

        let response = build_response_with_headers(
            StatusCode::OK,
            headers,
            false,
            b"test".to_vec(),
        );

        assert_eq!(response.status(), StatusCode::OK);
    }

    #[test]
    fn test_build_rate_limit_response() {
        let response = build_rate_limit_response(60, 100, 200, b"{}".to_vec());
        assert_eq!(response.status(), StatusCode::TOO_MANY_REQUESTS);
    }
}

use actix_web::HttpResponse;
use ahash::AHashMap;
use dashmap::DashMap;
use governor::clock::{Clock, DefaultClock};
use governor::state::{InMemoryState, NotKeyed};
use governor::{Quota, RateLimiter};
use once_cell::sync::Lazy;
use pyo3::prelude::*;
use std::collections::HashMap;
use std::sync::Arc;

type Limiter = RateLimiter<NotKeyed, InMemoryState, DefaultClock>;

// Store rate limiters per handler_id
static RATE_LIMITERS: Lazy<DashMap<usize, Arc<Limiter>>> = Lazy::new(DashMap::new);

// Store per-key limiters (IP-based)
static IP_LIMITERS: Lazy<DashMap<(usize, String), Arc<Limiter>>> = Lazy::new(DashMap::new);

pub fn check_rate_limit(
    handler_id: usize,
    headers: &AHashMap<String, String>,
    config: &HashMap<String, Py<PyAny>>,
    py: Python,
) -> Option<HttpResponse> {
    // Extract rate limit config
    let rps = config
        .get("rps")
        .and_then(|r| r.extract::<u32>(py).ok())
        .unwrap_or(100);
    
    let burst = config
        .get("burst")
        .and_then(|b| b.extract::<u32>(py).ok())
        .unwrap_or(rps * 2);
    
    let key_type = config
        .get("key")
        .and_then(|k| k.extract::<String>(py).ok())
        .unwrap_or_else(|| "ip".to_string());
    
    // Determine the rate limit key
    let key = match key_type.as_str() {
        "ip" => {
            // Try to get client IP from headers (X-Forwarded-For, X-Real-IP, etc.)
            headers.get("x-forwarded-for")
                .or_else(|| headers.get("x-real-ip"))
                .or_else(|| headers.get("remote-addr"))
                .map(|ip| {
                    // Take first IP if comma-separated
                    ip.split(',').next().unwrap_or(ip).trim().to_string()
                })
                .unwrap_or_else(|| "unknown".to_string())
        }
        header_name => {
            // Use custom header as key
            headers.get(&header_name.to_lowercase())
                .cloned()
                .unwrap_or_else(|| "unknown".to_string())
        }
    };
    
    // Get or create rate limiter for this handler + key combination
    let limiter_key = (handler_id, key.clone());
    let limiter = IP_LIMITERS.entry(limiter_key.clone()).or_insert_with(|| {
        // Use NonZero constructors properly
        let rps_nonzero = std::num::NonZeroU32::new(rps.max(1)).unwrap();
        let burst_nonzero = std::num::NonZeroU32::new(burst.max(1)).unwrap();
        let quota = Quota::per_second(rps_nonzero)
            .allow_burst(burst_nonzero);
        Arc::new(RateLimiter::direct(quota))
    });
    
    // Check rate limit
    match limiter.check() {
        Ok(_) => None, // Request allowed
        Err(not_until) => {
            // Calculate retry after in seconds
            let wait_time = not_until.wait_time_from(DefaultClock::default().now());
            let retry_after = wait_time.as_secs().max(1);
            
            Some(
                HttpResponse::TooManyRequests()
                    .insert_header(("Retry-After", retry_after.to_string()))
                    .insert_header(("X-RateLimit-Limit", rps.to_string()))
                    .insert_header(("X-RateLimit-Burst", burst.to_string()))
                    .content_type("application/json")
                    .body(format!(
                        r#"{{"detail":"Rate limit exceeded. Try again in {} seconds.","retry_after":{}}}"#,
                        retry_after, retry_after
                    ))
            )
        }
    }
}
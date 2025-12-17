use ahash::AHashMap;
use once_cell::sync::OnceCell;
use pyo3::prelude::*;
use pyo3_async_runtimes::TaskLocals;
use regex::Regex;
use std::sync::Arc;
use std::sync::atomic::AtomicU64;

use crate::metadata::{CompressionConfig, CorsConfig, RouteMetadata};
use crate::router::Router;
use crate::websocket::WebSocketRouter;

pub struct AppState {
    pub dispatch: Py<PyAny>,
    pub debug: bool,
    pub max_header_size: usize,
    pub global_cors_config: Option<CorsConfig>,           // Global CORS configuration from Django settings
    pub cors_origin_regexes: Vec<Regex>,                  // Compiled regex patterns for origin matching
    pub global_compression_config: Option<CompressionConfig>, // Global compression configuration used by middleware
    pub router: Option<Arc<Router>>,                      // Router (used by test infrastructure, optional in production)
    pub route_metadata: Option<Arc<AHashMap<usize, RouteMetadata>>>, // Route metadata (used by test infrastructure)
}

pub static GLOBAL_ROUTER: OnceCell<Arc<Router>> = OnceCell::new();
pub static GLOBAL_WEBSOCKET_ROUTER: OnceCell<Arc<WebSocketRouter>> = OnceCell::new();
pub static TASK_LOCALS: OnceCell<TaskLocals> = OnceCell::new(); // reuse global python event loop
pub static ROUTE_METADATA: OnceCell<Arc<AHashMap<usize, RouteMetadata>>> = OnceCell::new();
pub static ROUTE_METADATA_TEMP: OnceCell<AHashMap<usize, RouteMetadata>> = OnceCell::new(); // Temporary storage before CORS injection

// Sync streaming thread limiting to prevent thread exhaustion DoS
// Tracks number of active sync streaming threads (each uses an OS thread)
pub static ACTIVE_SYNC_STREAMING_THREADS: AtomicU64 = AtomicU64::new(0);

/// Get the configured maximum concurrent sync streaming threads
/// Default: 1000 if not configured
/// Reads from (in order of precedence):
/// 1. Environment variable: DJANGO_BOLT_MAX_SYNC_STREAMING_THREADS
/// 2. Django setting: BOLT_MAX_SYNC_STREAMING_THREADS
/// 3. Default: 1000
pub fn get_max_sync_streaming_threads() -> u64 {
    // Check environment variable first
    if let Ok(val) = std::env::var("DJANGO_BOLT_MAX_SYNC_STREAMING_THREADS") {
        if let Ok(n) = val.parse::<u64>() {
            if n > 0 {
                return n;
            }
        }
    }

    // Check Django settings via Python
    let limit = Python::attach(|py| {
        if let Ok(django_module) = py.import("django.conf") {
            if let Ok(settings) = django_module.getattr("settings") {
                if let Ok(limit_obj) = settings.getattr("BOLT_MAX_SYNC_STREAMING_THREADS") {
                    if let Ok(n) = limit_obj.extract::<u64>() {
                        if n > 0 {
                            return Some(n);
                        }
                    }
                }
            }
        }
        None
    });

    limit.unwrap_or(1000)  // Default to 1000
}

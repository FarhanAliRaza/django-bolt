use ahash::AHashMap;
use once_cell::sync::OnceCell;
use pyo3::prelude::*;
use pyo3_async_runtimes::TaskLocals;
use regex::Regex;
use std::sync::Arc;

use crate::metadata::{CorsConfig, RouteMetadata};
use crate::router::Router;

pub struct AppState {
    pub dispatch: Py<PyAny>,
    pub debug: bool,
    pub max_header_size: usize,
    pub global_cors_config: Option<CorsConfig>, // Global CORS configuration from Django settings
    pub cors_origin_regexes: Vec<Regex>, // Compiled regex patterns for origin matching
}

pub static GLOBAL_ROUTER: OnceCell<Arc<Router>> = OnceCell::new();
pub static TASK_LOCALS: OnceCell<TaskLocals> = OnceCell::new(); // reuse global python event loop
pub static ROUTE_METADATA: OnceCell<Arc<AHashMap<usize, RouteMetadata>>> = OnceCell::new();
pub static ROUTE_METADATA_TEMP: OnceCell<AHashMap<usize, RouteMetadata>> = OnceCell::new(); // Temporary storage before CORS injection

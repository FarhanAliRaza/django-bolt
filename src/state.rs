use ahash::AHashMap;
use once_cell::sync::OnceCell;
use pyo3::prelude::*;
use pyo3_async_runtimes::TaskLocals;
use std::sync::Arc;

use crate::metadata::RouteMetadata;
use crate::router::Router;

pub struct AppState {
    pub dispatch: Py<PyAny>,
    pub debug: bool,
    pub max_header_size: usize,
    pub cors_allowed_origins: Vec<String>,
}

pub static GLOBAL_ROUTER: OnceCell<Arc<Router>> = OnceCell::new();
pub static TASK_LOCALS: OnceCell<TaskLocals> = OnceCell::new(); // reuse global python event loop
pub static ROUTE_METADATA: OnceCell<Arc<AHashMap<usize, RouteMetadata>>> = OnceCell::new();

use ahash::AHashMap;
use once_cell::sync::OnceCell;
use pyo3::prelude::*;
use pyo3_async_runtimes::TaskLocals;
use std::sync::{Arc, Mutex};
use tokio::sync::oneshot;

use crate::router::Router;
use crate::metadata::RouteMetadata;

pub struct AppState {
    pub dispatch: Py<PyAny>,
    pub debug: bool,
    pub max_header_size: usize,
    pub cors_allowed_origins: Vec<String>,
    pub python_queue: Option<Py<PyAny>>, // asyncio.Queue for Python event loop
}

/// Response channels for Python event loop worker
/// Maps request_id -> oneshot channel to send response back
pub type ResponseChannels = Arc<Mutex<AHashMap<u64, oneshot::Sender<(u16, Vec<(String, String)>, Vec<u8>)>>>>;

pub static GLOBAL_ROUTER: OnceCell<Arc<Router>> = OnceCell::new();
pub static TASK_LOCALS: OnceCell<TaskLocals> = OnceCell::new();
pub static MIDDLEWARE_METADATA: OnceCell<Arc<AHashMap<usize, Py<PyAny>>>> = OnceCell::new();
pub static ROUTE_METADATA: OnceCell<Arc<AHashMap<usize, RouteMetadata>>> = OnceCell::new();
pub static RESPONSE_CHANNELS: OnceCell<ResponseChannels> = OnceCell::new();
pub static HANDLER_MAP: OnceCell<Arc<AHashMap<usize, Py<PyAny>>>> = OnceCell::new();

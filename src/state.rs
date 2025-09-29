use once_cell::sync::OnceCell;
use pyo3::prelude::*;
use pyo3_async_runtimes::TaskLocals;
use std::sync::Arc;
use tokio::sync::RwLock;

use crate::router::Router;

pub struct AppState {
    pub dispatch: Py<PyAny>,
}

pub static GLOBAL_ROUTER: OnceCell<Arc<RwLock<Router>>> = OnceCell::new();
pub static TASK_LOCALS: OnceCell<TaskLocals> = OnceCell::new();

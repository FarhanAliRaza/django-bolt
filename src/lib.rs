use pyo3::prelude::*;

mod direct_stream;
mod error;
mod handler;
mod json;
mod metadata;
mod middleware;
mod permissions;
mod request;
mod router;
mod server;
mod state;
mod streaming;

#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

#[pymodule]
fn _core(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    use crate::server::{register_middleware_metadata, register_routes, start_server_async};
    m.add_function(wrap_pyfunction!(register_routes, m)?)?;
    m.add_function(wrap_pyfunction!(register_middleware_metadata, m)?)?;
    m.add_function(wrap_pyfunction!(start_server_async, m)?)?;
    Ok(())
}

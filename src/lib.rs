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
mod test_state;
mod testing;

#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

#[pymodule]
fn _core(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    use crate::server::{register_middleware_metadata, register_routes, start_server_async};
    use crate::test_state::{
        create_test_app, destroy_test_app, ensure_test_runtime, handle_test_request_for,
        register_test_middleware_metadata, register_test_routes, set_test_task_locals,
        handle_actix_http_request,
    };
    use crate::testing::handle_test_request;
    m.add_function(wrap_pyfunction!(register_routes, m)?)?;
    m.add_function(wrap_pyfunction!(register_middleware_metadata, m)?)?;
    m.add_function(wrap_pyfunction!(start_server_async, m)?)?;
    m.add_function(wrap_pyfunction!(handle_test_request, m)?)?;
    // Test-only instance APIs
    m.add_function(wrap_pyfunction!(create_test_app, m)?)?;
    m.add_function(wrap_pyfunction!(destroy_test_app, m)?)?;
    m.add_function(wrap_pyfunction!(register_test_routes, m)?)?;
    m.add_function(wrap_pyfunction!(register_test_middleware_metadata, m)?)?;
    m.add_function(wrap_pyfunction!(set_test_task_locals, m)?)?;
    m.add_function(wrap_pyfunction!(ensure_test_runtime, m)?)?;
    m.add_function(wrap_pyfunction!(handle_test_request_for, m)?)?;
    m.add_function(wrap_pyfunction!(handle_actix_http_request, m)?)?;
    Ok(())
}

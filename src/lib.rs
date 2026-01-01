use pyo3::prelude::*;

mod cors;
mod error;
mod handler;
mod json;
mod metadata;
mod middleware;
mod permissions;
mod request;
mod response_builder;
mod responses;
mod router;
mod server;
mod state;
mod streaming;
mod testing;
mod validation;
mod websocket;

#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

#[pymodule]
fn _core(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    use crate::server::{
        register_middleware_metadata, register_routes, register_websocket_routes,
        start_server_async,
    };
    use crate::testing::{
        create_test_app, destroy_test_app, handle_test_websocket, register_test_middleware_metadata,
        register_test_routes, register_test_websocket_routes, test_request,
    };

    // Production server functions
    m.add_function(wrap_pyfunction!(register_routes, m)?)?;
    m.add_function(wrap_pyfunction!(register_websocket_routes, m)?)?;
    m.add_function(wrap_pyfunction!(register_middleware_metadata, m)?)?;
    m.add_function(wrap_pyfunction!(start_server_async, m)?)?;

    // Test infrastructure functions (async-native, uses Actix test utilities)
    m.add_function(wrap_pyfunction!(create_test_app, m)?)?;
    m.add_function(wrap_pyfunction!(destroy_test_app, m)?)?;
    m.add_function(wrap_pyfunction!(register_test_routes, m)?)?;
    m.add_function(wrap_pyfunction!(register_test_websocket_routes, m)?)?;
    m.add_function(wrap_pyfunction!(register_test_middleware_metadata, m)?)?;
    m.add_function(wrap_pyfunction!(test_request, m)?)?;
    m.add_function(wrap_pyfunction!(handle_test_websocket, m)?)?;

    Ok(())
}

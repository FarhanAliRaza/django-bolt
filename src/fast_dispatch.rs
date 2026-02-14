//! Fast dispatch: Moves Python dispatch overhead into Rust.
//!
//! KEY INSIGHT FROM BENCHMARKING:
//! Each Python→Rust FFI boundary crossing costs ~0.5-1µs. Calling separate
//! Rust functions from Python is SLOWER than pure Python. The win ONLY comes
//! from doing everything in ONE Rust call to amortize the crossing cost.
//!
//! This module provides:
//! - `DispatchInfo`: Pre-compiled dispatch decisions stored at registration time
//! - `fast_serialize_json`: Bypasses Python isinstance chain for dict/list→JSON
//! - `fast_dispatch_full`: ENTIRE dispatch in one FFI call (inject + call + serialize)

use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyDict, PyList, PyTuple};

// Cached Python objects (initialized once, reused forever)
static JSON_ENCODE: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static RESPONSE_META_JSON: PyOnceLock<Py<PyAny>> = PyOnceLock::new();

fn get_json_encode(py: Python<'_>) -> &Py<PyAny> {
    JSON_ENCODE.get_or_init(py, || {
        py.import("django_bolt._json")
            .unwrap()
            .getattr("encode")
            .unwrap()
            .unbind()
    })
}

fn get_response_meta_json(py: Python<'_>) -> &Py<PyAny> {
    RESPONSE_META_JSON.get_or_init(py, || {
        let elements: Vec<Py<PyAny>> = vec![
            "json".into_pyobject(py).unwrap().into_any().unbind(),
            py.None(),
            py.None(),
            py.None(),
        ];
        let tuple = PyTuple::new(py, &elements).unwrap();
        tuple.into_any().unbind()
    })
}

/// Handler dispatch mode (replaces string comparison on meta["mode"])
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum DispatchMode {
    RequestOnly = 0,
    Mixed = 1,
}

/// Injection plan entry: how to extract one parameter.
/// Stored at registration time, used at request time.
#[derive(Debug)]
pub struct ParamPlan {
    pub name: String,
    /// 0=path, 1=query
    pub source: u8,
    /// Default value (None means required)
    pub default: Option<Py<PyAny>>,
}

/// Pre-compiled dispatch information.
#[pyclass]
pub struct DispatchInfo {
    pub mode: DispatchMode,
    pub is_async: bool,
    pub is_blocking: bool,
    pub default_status_code: u16,
    pub has_middleware: bool,
    pub has_response_type: bool,
    pub has_file_uploads: bool,
    pub injector: Option<Py<PyAny>>,
    pub injector_is_async: bool,
    pub handler_id: u64,
    /// Pre-compiled injection plan (for simple path/query handlers)
    /// Each entry: (param_name, source_id, default_value)
    pub param_plan: Vec<ParamPlan>,
    /// True if param_plan can be used (no body, no header, no cookie, no deps)
    pub use_fast_inject: bool,
}

#[pymethods]
impl DispatchInfo {
    #[new]
    #[pyo3(signature = (
        handler_id,
        mode = 1,
        is_async = true,
        is_blocking = false,
        default_status_code = 200,
        has_middleware = false,
        has_response_type = false,
        has_file_uploads = false,
        injector = None,
        injector_is_async = false,
        param_plan = None,
    ))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        handler_id: u64,
        mode: u8,
        is_async: bool,
        is_blocking: bool,
        default_status_code: u16,
        has_middleware: bool,
        has_response_type: bool,
        has_file_uploads: bool,
        injector: Option<Py<PyAny>>,
        injector_is_async: bool,
        param_plan: Option<Vec<(String, u8, Option<Py<PyAny>>)>>,
    ) -> Self {
        let plan: Vec<ParamPlan> = param_plan
            .unwrap_or_default()
            .into_iter()
            .map(|(name, source, default)| ParamPlan {
                name,
                source,
                default,
            })
            .collect();
        let use_fast_inject = !plan.is_empty();

        DispatchInfo {
            handler_id,
            mode: if mode == 0 {
                DispatchMode::RequestOnly
            } else {
                DispatchMode::Mixed
            },
            is_async,
            is_blocking,
            default_status_code,
            has_middleware,
            has_response_type,
            has_file_uploads,
            injector,
            injector_is_async,
            param_plan: plan,
            use_fast_inject,
        }
    }

    #[getter]
    fn handler_id(&self) -> u64 {
        self.handler_id
    }

    #[getter]
    fn mode_int(&self) -> u8 {
        self.mode as u8
    }
}

/// Fast JSON serialization — bypasses isinstance chain.
///
/// Returns None if result is not dict/list (fallback to Python).
#[pyfunction]
pub fn fast_serialize_json(
    py: Python<'_>,
    result: &Bound<'_, PyAny>,
    status_code: u16,
) -> PyResult<Option<Py<PyAny>>> {
    if !result.is_instance_of::<PyDict>() && !result.is_instance_of::<PyList>() {
        return Ok(None);
    }

    let encode = get_json_encode(py);
    let body_bytes = encode.call1(py, (result,))?;
    let meta = get_response_meta_json(py);

    let status_obj: Py<PyAny> = status_code.into_pyobject(py).unwrap().into_any().unbind();
    let tuple = PyTuple::new(py, &[status_obj, meta.clone_ref(py), body_bytes])?;

    Ok(Some(tuple.into_any().unbind()))
}

/// FULL dispatch in ONE FFI call.
///
/// This is the core optimization: instead of Python calling 5+ functions
/// (meta lookup, injector, handler, serialize_response), this single Rust
/// function does everything, amortizing the FFI boundary crossing cost.
///
/// For sync handlers that return dict/list with no middleware/response_type:
/// 1. Read params from request dicts (Rust dict access via PyO3)
/// 2. Call handler with extracted args (one Python call)
/// 3. Type-check result and call json.encode (one Python call)
/// 4. Build response tuple (Rust)
///
/// Total: 2 Python calls + Rust logic, vs current 15-25 Python bytecodes.
#[pyfunction]
pub fn fast_dispatch_full(
    py: Python<'_>,
    handler: &Bound<'_, PyAny>,
    request: &Bound<'_, PyAny>,
    info: &DispatchInfo,
) -> PyResult<Py<PyAny>> {
    // 1. Extract args based on mode
    let result = match info.mode {
        DispatchMode::RequestOnly => {
            // handler(request) — zero injection needed
            handler.call1((request,))?
        }
        DispatchMode::Mixed => {
            if info.use_fast_inject {
                // FAST PATH: extract params inline in Rust (no Python injector call)
                // Access request.params and request.query as Python dicts
                let path_params = request.getattr("params")?;
                let path_dict = path_params.downcast::<PyDict>()?;

                let query_params = request.getattr("query")?;
                let query_dict = query_params.downcast::<PyDict>()?;

                // Build args list from pre-compiled plan
                let args = PyList::empty(py);
                for param in &info.param_plan {
                    let value = if param.source == 0 {
                        // Path param (required)
                        path_dict
                            .get_item(&param.name)?
                            .ok_or_else(|| {
                                pyo3::exceptions::PyKeyError::new_err(format!(
                                    "Missing required path parameter: {}",
                                    param.name
                                ))
                            })?
                            .unbind()
                    } else {
                        // Query param (may have default)
                        match query_dict.get_item(&param.name)? {
                            Some(v) => v.unbind(),
                            None => match &param.default {
                                Some(d) => d.clone_ref(py),
                                None => {
                                    return Err(pyo3::exceptions::PyKeyError::new_err(
                                        format!(
                                            "Missing required query parameter: {}",
                                            param.name
                                        ),
                                    ))
                                }
                            },
                        }
                    };
                    args.append(value.bind(py))?;
                }

                let args_tuple = args.to_tuple();
                handler.call1(&args_tuple)?
            } else if let Some(ref injector) = info.injector {
                // SLOW PATH: use Python injector (for body, header, cookie, deps)
                let injection_result = injector.call1(py, (request,))?;
                let bound = injection_result.bind(py);
                let tuple = bound.downcast::<PyTuple>()?;
                let args_list = tuple.get_item(0)?;
                let kwargs_obj = tuple.get_item(1)?;

                let args_as_list = args_list.downcast::<PyList>()?;
                let kwargs_dict = kwargs_obj.downcast::<PyDict>()?;

                let items: Vec<Bound<'_, PyAny>> = args_as_list.iter().collect();
                let args_tuple = PyTuple::new(py, &items)?;

                if kwargs_dict.is_empty() {
                    handler.call1(&args_tuple)?
                } else {
                    handler.call(&args_tuple, Some(&kwargs_dict))?
                }
            } else {
                handler.call0()?
            }
        }
    };

    // 2. Fast JSON serialization (C-level type check + msgspec encode)
    if result.is_instance_of::<PyDict>() || result.is_instance_of::<PyList>() {
        let encode = get_json_encode(py);
        let body_bytes = encode.call1(py, (&result,))?;
        let meta = get_response_meta_json(py);

        let status_obj: Py<PyAny> = info
            .default_status_code
            .into_pyobject(py)
            .unwrap()
            .into_any()
            .unbind();
        let tuple =
            PyTuple::new(py, &[status_obj, meta.clone_ref(py), body_bytes])?;
        return Ok(tuple.into_any().unbind());
    }

    // 3. Non-dict/list result — signal Python fallback needed
    Err(pyo3::exceptions::PyValueError::new_err(
        "fast_dispatch: non-dict/list result, use Python fallback",
    ))
}

// Keep individual functions for standalone use / testing

#[pyfunction]
pub fn fast_dispatch_sync(
    py: Python<'_>,
    handler: &Bound<'_, PyAny>,
    request: &Bound<'_, PyAny>,
    info: &DispatchInfo,
) -> PyResult<Py<PyAny>> {
    fast_dispatch_full(py, handler, request, info)
}

#[pyfunction]
pub fn fast_inject_path_only(
    py: Python<'_>,
    request: &Bound<'_, PyAny>,
    param_names: Vec<String>,
) -> PyResult<Py<PyAny>> {
    let params_dict = request.getattr("params")?;
    let params = params_dict.downcast::<PyDict>()?;

    let args = PyList::empty(py);
    for name in &param_names {
        let value = params.get_item(name)?.ok_or_else(|| {
            pyo3::exceptions::PyKeyError::new_err(format!(
                "Missing required path parameter: {}",
                name
            ))
        })?;
        args.append(value)?;
    }

    let kwargs = PyDict::new(py);
    let tuple = PyTuple::new(py, vec![args.as_any(), kwargs.as_any()])?;
    Ok(tuple.into_any().unbind())
}

#[pyfunction]
pub fn fast_inject_query_only(
    py: Python<'_>,
    request: &Bound<'_, PyAny>,
    param_specs: Vec<(String, Py<PyAny>)>,
) -> PyResult<Py<PyAny>> {
    let query_obj = request.getattr("query")?;
    let query = query_obj.downcast::<PyDict>()?;

    let args = PyList::empty(py);
    for (name, default) in &param_specs {
        let value: Py<PyAny> = match query.get_item(name)? {
            Some(v) => v.unbind(),
            None => default.clone_ref(py),
        };
        args.append(value.bind(py))?;
    }

    let kwargs = PyDict::new(py);
    let tuple = PyTuple::new(py, vec![args.as_any(), kwargs.as_any()])?;
    Ok(tuple.into_any().unbind())
}

#[pyfunction]
pub fn fast_inject_simple(
    py: Python<'_>,
    request: &Bound<'_, PyAny>,
    param_specs: Vec<(String, u8, Py<PyAny>)>,
) -> PyResult<Py<PyAny>> {
    let params_obj = request.getattr("params")?;
    let params = params_obj.downcast::<PyDict>()?;
    let query_obj = request.getattr("query")?;
    let query = query_obj.downcast::<PyDict>()?;

    let args = PyList::empty(py);
    for (name, source, default) in &param_specs {
        let value: Py<PyAny> = if *source == 0 {
            params
                .get_item(name)?
                .ok_or_else(|| {
                    pyo3::exceptions::PyKeyError::new_err(format!(
                        "Missing required path parameter: {}",
                        name
                    ))
                })?
                .unbind()
        } else {
            match query.get_item(name)? {
                Some(v) => v.unbind(),
                None => default.clone_ref(py),
            }
        };
        args.append(value.bind(py))?;
    }

    let kwargs = PyDict::new(py);
    let tuple = PyTuple::new(py, vec![args.as_any(), kwargs.as_any()])?;
    Ok(tuple.into_any().unbind())
}

use ahash::AHashMap;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyString};

#[pyclass]
pub struct PyRequest {
    pub method: String,
    pub path: String,
    pub body: Vec<u8>,
    pub path_params: AHashMap<String, String>,
    pub query_params: AHashMap<String, String>,
    pub headers: AHashMap<String, String>,
    pub cookies: AHashMap<String, String>,
    pub context: Option<Py<PyDict>>,  // Middleware context data
}

#[pymethods]
impl PyRequest {
    #[getter]
    fn method(&self) -> &str {
        &self.method
    }

    #[getter]
    fn path(&self) -> &str {
        &self.path
    }

    #[getter]
    fn body<'py>(&self, py: Python<'py>) -> Py<PyAny> {
        PyBytes::new(py, &self.body).into_any().unbind()
    }

    #[getter]
    fn context<'py>(&self, py: Python<'py>) -> Py<PyAny> {
        match &self.context {
            Some(ctx) => ctx.clone_ref(py).into_any(),
            None => py.None()
        }
    }

    fn get<'py>(&self, py: Python<'py>, key: &str, default: Option<Py<PyAny>>) -> Py<PyAny> {
        match key {
            "method" => PyString::new(py, &self.method).into_any().unbind(),
            "path" => PyString::new(py, &self.path).into_any().unbind(),
            "body" => PyBytes::new(py, &self.body).into_any().unbind(),
            "params" => {
                let d = PyDict::new(py);
                for (k, v) in &self.path_params {
                    let _ = d.set_item(k, v);
                }
                d.into_any().unbind()
            }
            "query" => {
                let d = PyDict::new(py);
                for (k, v) in &self.query_params {
                    let _ = d.set_item(k, v);
                }
                d.into_any().unbind()
            }
            "headers" => {
                let d = PyDict::new(py);
                for (k, v) in &self.headers {
                    let _ = d.set_item(k, v);
                }
                d.into_any().unbind()
            }
            "cookies" => {
                let d = PyDict::new(py);
                for (k, v) in &self.cookies {
                    let _ = d.set_item(k, v);
                }
                d.into_any().unbind()
            }
            "auth" | "context" => match &self.context {
                Some(ctx) => ctx.clone_ref(py).into_any(),
                None => py.None()
            }
            _ => default.unwrap_or_else(|| py.None()),
        }
    }

    fn __getitem__<'py>(&self, py: Python<'py>, key: &str) -> PyResult<Py<PyAny>> {
        match key {
            "method" => Ok(PyString::new(py, &self.method).into_any().unbind()),
            "path" => Ok(PyString::new(py, &self.path).into_any().unbind()),
            "body" => Ok(PyBytes::new(py, &self.body).into_any().unbind()),
            "params" => {
                let d = PyDict::new(py);
                for (k, v) in &self.path_params {
                    let _ = d.set_item(k, v);
                }
                Ok(d.into_any().unbind())
            }
            "query" => {
                let d = PyDict::new(py);
                for (k, v) in &self.query_params {
                    let _ = d.set_item(k, v);
                }
                Ok(d.into_any().unbind())
            }
            "headers" => {
                let d = PyDict::new(py);
                for (k, v) in &self.headers {
                    let _ = d.set_item(k, v);
                }
                Ok(d.into_any().unbind())
            }
            "cookies" => {
                let d = PyDict::new(py);
                for (k, v) in &self.cookies {
                    let _ = d.set_item(k, v);
                }
                Ok(d.into_any().unbind())
            }
            "context" => Ok(match &self.context {
                Some(ctx) => ctx.clone_ref(py).into_any(),
                None => py.None()
            }),
            _ => Err(pyo3::exceptions::PyKeyError::new_err(key.to_string())),
        }
    }

    /// Convert request to dict for Python queue
    fn to_dict<'py>(&self, py: Python<'py>) -> PyResult<Py<PyDict>> {
        let d = PyDict::new(py);

        d.set_item("method", &self.method)?;
        d.set_item("path", &self.path)?;
        d.set_item("body", PyBytes::new(py, &self.body))?;

        let params_dict = PyDict::new(py);
        for (k, v) in &self.path_params {
            params_dict.set_item(k, v)?;
        }
        d.set_item("params", params_dict)?;

        let query_dict = PyDict::new(py);
        for (k, v) in &self.query_params {
            query_dict.set_item(k, v)?;
        }
        d.set_item("query", query_dict)?;

        let headers_dict = PyDict::new(py);
        for (k, v) in &self.headers {
            headers_dict.set_item(k, v)?;
        }
        d.set_item("headers", headers_dict)?;

        let cookies_dict = PyDict::new(py);
        for (k, v) in &self.cookies {
            cookies_dict.set_item(k, v)?;
        }
        d.set_item("cookies", cookies_dict)?;

        match &self.context {
            Some(ctx) => d.set_item("context", ctx.clone_ref(py))?,
            None => d.set_item("context", py.None())?,
        }

        Ok(d.unbind())
    }
}

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
    pub context: Option<Py<PyDict>>, // Middleware context data
    // None if no auth context or user not found
    pub user: Option<Py<PyAny>>,
    pub state: Py<PyDict>, // Arbitrary state for middleware AND dynamic attributes (e.g. _messages)
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
            None => py.None(),
        }
    }

    /// Get the user object (LazyUser proxy set by Python's _dispatch).
    ///
    /// Returns a LazyUser proxy that loads the user from the database
    /// on first access (no await needed in handler code).
    ///
    /// Returns:
    /// - LazyUser proxy if authentication succeeded
    /// - None if no auth context or authentication failed
    #[getter]
    fn user<'py>(&self, py: Python<'py>) -> Py<PyAny> {
        match &self.user {
            Some(user) => user.clone_ref(py),
            None => py.None(),
        }
    }

    /// Set the user object (called by Django middleware via DjangoMiddlewareStack).
    ///
    /// This allows Django's AuthenticationMiddleware to set request.user
    /// just like in standard Django.
    #[setter]
    fn set_user(&mut self, value: Py<PyAny>) {
        self.user = Some(value);
    }

    /// Get headers as a dict for middleware access.
    ///
    /// Example:
    ///     auth_header = request.headers.get("authorization")
    #[getter]
    fn headers<'py>(&self, py: Python<'py>) -> Py<PyDict> {
        let d = PyDict::new(py);
        for (k, v) in &self.headers {
            let _ = d.set_item(k, v);
        }
        d.unbind()
    }

    /// Get cookies as a dict for middleware access.
    ///
    /// Example:
    ///     session_id = request.cookies.get("session_id")
    #[getter]
    fn cookies<'py>(&self, py: Python<'py>) -> Py<PyDict> {
        let d = PyDict::new(py);
        for (k, v) in &self.cookies {
            let _ = d.set_item(k, v);
        }
        d.unbind()
    }

    /// Get query params as a dict for middleware access.
    ///
    /// Example:
    ///     page = request.query.get("page", "1")
    #[getter]
    fn query<'py>(&self, py: Python<'py>) -> Py<PyDict> {
        let d = PyDict::new(py);
        for (k, v) in &self.query_params {
            let _ = d.set_item(k, v);
        }
        d.unbind()
    }

    /// Get the state dict for middleware to store arbitrary data.
    ///
    /// This follows the Starlette pattern where middleware can store
    /// request-scoped data that persists through the request lifecycle.
    ///
    /// Example:
    ///     request.state["request_id"] = "abc123"
    ///     request.state["tenant"] = tenant_obj
    #[getter]
    fn state<'py>(&self, py: Python<'py>) -> Py<PyDict> {
        self.state.clone_ref(py)
    }

    /// Get the async user loader (Django-style).
    ///
    /// Returns the async user callable set by Django's AuthenticationMiddleware.
    /// Use this in async handlers to load the user without blocking:
    ///
    ///     user = await request.auser()
    ///
    /// This follows Django's pattern where `request.auser` is an async callable
    /// that loads the user from the database asynchronously.
    ///
    /// Returns:
    ///     Async callable that returns the user when awaited.
    ///     If Django middleware is not configured, returns a callable that
    ///     returns AnonymousUser (matching Django's behavior).
    #[getter]
    fn auser<'py>(&self, py: Python<'py>) -> PyResult<Py<PyAny>> {
        // Get "auser" from state dict (set by Django middleware adapter)
        let state_dict = self.state.bind(py);
        match state_dict.get_item("auser") {
            Ok(Some(auser)) => Ok(auser.unbind()),
            _ => {
                // Return async callable that returns AnonymousUser
                // This matches Django's behavior when AuthenticationMiddleware isn't configured
                let django_bolt_module = py.import("django_bolt.auth.anonymous")?;
                let auser_fallback = django_bolt_module.getattr("auser_fallback")?;
                Ok(auser_fallback.unbind())
            }
        }
    }

    /// Get the full path with query string (Django-compatible).
    ///
    /// Example:
    ///     /users?page=2&limit=10
    ///
    /// This matches Django's HttpRequest.get_full_path() method.
    fn get_full_path(&self) -> String {
        if self.query_params.is_empty() {
            self.path.clone()
        } else {
            let query_string: String = self
                .query_params
                .iter()
                .map(|(k, v)| format!("{}={}", k, v))
                .collect::<Vec<_>>()
                .join("&");
            format!("{}?{}", self.path, query_string)
        }
    }

    /// Build absolute URI (Django-compatible).
    ///
    /// Example:
    ///     http://example.com/users?page=2
    ///
    /// This matches Django's HttpRequest.build_absolute_uri() method.
    /// Uses Host header to determine the scheme and host.
    #[pyo3(signature = (location=None))]
    fn build_absolute_uri(&self, location: Option<&str>) -> String {
        // Get host from headers (or use default)
        let host = self
            .headers
            .get("host")
            .map(|s| s.as_str())
            .unwrap_or("localhost");

        // Determine scheme (check for X-Forwarded-Proto or default to http)
        let scheme = self
            .headers
            .get("x-forwarded-proto")
            .map(|s| s.as_str())
            .unwrap_or("http");

        // If location is provided, use it; otherwise use current path
        let path = location.unwrap_or_else(|| &self.path);

        // Build full URL
        if self.query_params.is_empty() || location.is_some() {
            format!("{}://{}{}", scheme, host, path)
        } else {
            let query_string: String = self
                .query_params
                .iter()
                .map(|(k, v)| format!("{}={}", k, v))
                .collect::<Vec<_>>()
                .join("&");
            format!("{}://{}{}?{}", scheme, host, path, query_string)
        }
    }

    #[pyo3(signature = (key, /, default=None))]
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
                None => default.unwrap_or_else(|| py.None()),
            },
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
                None => py.None(),
            }),
            _ => Err(pyo3::exceptions::PyKeyError::new_err(key.to_string())),
        }
    }

    fn __setitem__(&mut self, key: &str, value: Py<PyAny>) -> PyResult<()> {
        match key {
            "user" => {
                // Allow Python's _dispatch to set LazyUser proxy (loads user on first access)
                self.user = Some(value);
                Ok(())
            }
            _ => Err(pyo3::exceptions::PyKeyError::new_err(key.to_string())),
        }
    }

    /// Get unknown attributes from state dict.
    ///
    /// This enables Django middleware to read arbitrary attributes on the request
    /// object (e.g., request._messages) which are stored in the state dict.
    /// Note: __getattr__ is only called when attribute is NOT found via normal lookup.
    ///
    /// Example:
    ///     messages = request._messages  # Reads from state["_messages"]
    fn __getattr__(&self, py: Python<'_>, name: &str) -> PyResult<Py<PyAny>> {
        let state_dict = self.state.bind(py);
        match state_dict.get_item(name)? {
            Some(value) => Ok(value.unbind()),
            None => Err(pyo3::exceptions::PyAttributeError::new_err(format!(
                "'Request' object has no attribute '{}'",
                name
            ))),
        }
    }
}

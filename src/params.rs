/// Parameter metadata and type conversion for hot path optimization
use ahash::AHashMap;
use pyo3::prelude::*;
use pyo3::types::{PyFloat, PyInt, PyString};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use once_cell::sync::Lazy;

/// Parameter type for conversion
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ParamType {
    /// String (no conversion)
    Str,
    /// Integer (parse i64)
    Int,
    /// Float (parse f64)
    Float,
    /// Boolean (parse bool)
    Bool,
    /// Any/unknown type (no conversion, pass as string)
    Any,
}

/// Parameter source location
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ParamSource {
    Path,
    Query,
    Header,
    Cookie,
}

/// Metadata for a single parameter
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ParamMetadata {
    /// Parameter name (or alias)
    pub name: String,
    /// Source location
    pub source: ParamSource,
    /// Target type
    pub param_type: ParamType,
    /// Whether parameter is optional
    pub optional: bool,
}

/// Collection of parameter metadata for a route
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct RouteParamMetadata {
    pub params: Vec<ParamMetadata>,
}

impl RouteParamMetadata {
    pub fn new() -> Self {
        Self {
            params: Vec::new(),
        }
    }

    pub fn add_param(&mut self, param: ParamMetadata) {
        self.params.push(param);
    }
}

// Boolean true values (case-sensitive for fast path)
static BOOL_TRUE_VALUES: Lazy<HashSet<&'static str>> = Lazy::new(|| {
    let mut set = HashSet::new();
    set.insert("1");
    set.insert("true");
    set.insert("t");
    set.insert("yes");
    set.insert("y");
    set.insert("on");
    set.insert("True");
    set.insert("TRUE");
    set.insert("Yes");
    set.insert("YES");
    set.insert("On");
    set.insert("ON");
    set
});

static BOOL_FALSE_VALUES: Lazy<HashSet<&'static str>> = Lazy::new(|| {
    let mut set = HashSet::new();
    set.insert("0");
    set.insert("false");
    set.insert("f");
    set.insert("no");
    set.insert("n");
    set.insert("off");
    set.insert("False");
    set.insert("FALSE");
    set.insert("No");
    set.insert("NO");
    set.insert("Off");
    set.insert("OFF");
    set
});

/// Convert string to Python object based on parameter type
/// Returns Ok(Some(py_obj)) if converted, Ok(None) if missing and optional, Err if invalid
pub fn convert_param_value(
    py: Python,
    value: Option<&str>,
    param_type: ParamType,
    param_name: &str,
    optional: bool,
) -> PyResult<Option<Py<PyAny>>> {
    match value {
        Some(v) => {
            let py_obj: Py<PyAny> = match param_type {
                ParamType::Str => PyString::new(py, v).into(),
                ParamType::Int => {
                    // Fast path: parse i64 in Rust, convert to Python int
                    match v.parse::<i64>() {
                        Ok(i) => PyInt::new(py, i).into(),
                        Err(_) => {
                            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                                "Invalid integer value for parameter '{}': '{}'",
                                param_name, v
                            )))
                        }
                    }
                }
                ParamType::Float => {
                    // Fast path: parse f64 in Rust, convert to Python float
                    match v.parse::<f64>() {
                        Ok(f) => PyFloat::new(py, f).into(),
                        Err(_) => {
                            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                                "Invalid float value for parameter '{}': '{}'",
                                param_name, v
                            )))
                        }
                    }
                }
                ParamType::Bool => {
                    // TODO: Fast O(1) boolean conversion in Rust
                    // For now, pass as string and let Python handle conversion
                    // This preserves existing behavior while infrastructure is being built
                    PyString::new(py, v).into()
                }
                ParamType::Any => {
                    // No conversion, return as string
                    PyString::new(py, v).into()
                }
            };
            Ok(Some(py_obj))
        }
        None => {
            if optional {
                Ok(None)
            } else {
                Err(pyo3::exceptions::PyValueError::new_err(format!(
                    "Missing required parameter: '{}'",
                    param_name
                )))
            }
        }
    }
}

/// Convert parameters based on metadata
/// Returns AHashMap<String, Py<PyAny>> with converted values
pub fn convert_params(
    py: Python,
    path_params: &AHashMap<String, String>,
    query_params: &AHashMap<String, String>,
    headers: &AHashMap<String, String>,
    cookies: &AHashMap<String, String>,
    metadata: &RouteParamMetadata,
) -> PyResult<AHashMap<String, Py<PyAny>>> {
    let mut converted = AHashMap::with_capacity(metadata.params.len());

    for param in &metadata.params {
        let value = match param.source {
            ParamSource::Path => path_params.get(&param.name).map(|s| s.as_str()),
            ParamSource::Query => query_params.get(&param.name).map(|s| s.as_str()),
            ParamSource::Header => {
                // Headers are lowercase in the map
                let key = param.name.to_ascii_lowercase();
                headers.get(&key).map(|s| s.as_str())
            }
            ParamSource::Cookie => cookies.get(&param.name).map(|s| s.as_str()),
        };

        if let Some(py_obj) = convert_param_value(py, value, param.param_type, &param.name, param.optional)? {
            converted.insert(param.name.clone(), py_obj);
        }
    }

    Ok(converted)
}

#[cfg(test)]
mod tests {
    use super::*;
    use pyo3::Python;

    #[test]
    fn test_convert_int() {
        Python::with_gil(|py| {
            let result = convert_param_value(py, Some("42"), ParamType::Int, "test", false).unwrap();
            assert!(result.is_some());
            let val: i64 = result.unwrap().extract(py).unwrap();
            assert_eq!(val, 42);
        });
    }

    #[test]
    fn test_convert_bool_true() {
        Python::with_gil(|py| {
            for value in &["1", "true", "True", "TRUE", "yes", "on"] {
                let result = convert_param_value(py, Some(value), ParamType::Bool, "test", false).unwrap();
                assert!(result.is_some());
                let val: bool = result.unwrap().extract(py).unwrap();
                assert!(val, "Failed for value: {}", value);
            }
        });
    }

    #[test]
    fn test_convert_bool_false() {
        Python::with_gil(|py| {
            for value in &["0", "false", "False", "FALSE", "no", "off"] {
                let result = convert_param_value(py, Some(value), ParamType::Bool, "test", false).unwrap();
                assert!(result.is_some());
                let val: bool = result.unwrap().extract(py).unwrap();
                assert!(!val, "Failed for value: {}", value);
            }
        });
    }
}

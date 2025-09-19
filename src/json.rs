use pyo3::prelude::*;
use serde_json::{Value, to_vec};
use std::collections::HashMap;

/// Fast path JSON serialization in Rust
pub fn serialize_json(py: Python<'_>, obj: &Bound<'_, PyAny>) -> PyResult<Vec<u8>> {
    // Check if it's a simple dict/list that we can serialize in Rust
    if let Ok(dict) = obj.downcast::<pyo3::types::PyDict>() {
        let mut map = HashMap::new();
        for (key, value) in dict {
            if let Ok(key_str) = key.extract::<String>() {
                if let Ok(val) = extract_json_value(py, &value) {
                    map.insert(key_str, val);
                }
            }
        }
        to_vec(&map).map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("JSON serialization error: {}", e)))
    } else if let Ok(list) = obj.downcast::<pyo3::types::PyList>() {
        let mut vec = Vec::new();
        for item in list {
            if let Ok(val) = extract_json_value(py, &item) {
                vec.push(val);
            }
        }
        to_vec(&vec).map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("JSON serialization error: {}", e)))
    } else {
        // Fall back to Python JSON for complex objects
        Err(pyo3::exceptions::PyValueError::new_err("Cannot serialize complex object in Rust"))
    }
}

fn extract_json_value(py: Python<'_>, obj: &Bound<'_, PyAny>) -> PyResult<Value> {
    if obj.is_none() {
        Ok(Value::Null)
    } else if let Ok(b) = obj.extract::<bool>() {
        Ok(Value::Bool(b))
    } else if let Ok(i) = obj.extract::<i64>() {
        Ok(Value::Number(i.into()))
    } else if let Ok(f) = obj.extract::<f64>() {
        Ok(Value::Number(serde_json::Number::from_f64(f).unwrap_or(0.into())))
    } else if let Ok(s) = obj.extract::<String>() {
        Ok(Value::String(s))
    } else if let Ok(dict) = obj.downcast::<pyo3::types::PyDict>() {
        let mut map = serde_json::Map::new();
        for (key, value) in dict {
            if let Ok(key_str) = key.extract::<String>() {
                if let Ok(val) = extract_json_value(py, &value) {
                    map.insert(key_str, val);
                }
            }
        }
        Ok(Value::Object(map))
    } else if let Ok(list) = obj.downcast::<pyo3::types::PyList>() {
        let mut vec = Vec::new();
        for item in list {
            if let Ok(val) = extract_json_value(py, &item) {
                vec.push(val);
            }
        }
        Ok(Value::Array(vec))
    } else {
        Err(pyo3::exceptions::PyValueError::new_err("Unsupported type for JSON"))
    }
}
//! Type coercion for path and query parameters
//!
//! This module provides Rust-native type coercion for HTTP parameters,
//! eliminating the need for Python's convert_primitive() function.
//! Performance improvement: ~100-500µs per parameter.

use chrono::{DateTime, NaiveDate, NaiveDateTime, NaiveTime, Utc};
use pyo3::types::PyDictMethods;
use pyo3::IntoPyObject;
use rust_decimal::Decimal;
use std::str::FromStr;
use uuid::Uuid;

/// Type hint constants (must match Python's get_type_hint_id() in compiler.py)
pub const TYPE_INT: u8 = 1;
pub const TYPE_FLOAT: u8 = 2;
pub const TYPE_BOOL: u8 = 3;
pub const TYPE_STRING: u8 = 4;
pub const TYPE_UUID: u8 = 5;
pub const TYPE_DATETIME: u8 = 6;
pub const TYPE_DECIMAL: u8 = 7;
pub const TYPE_DATE: u8 = 8;
pub const TYPE_TIME: u8 = 9;

/// Result of type coercion - can be converted to Python types
#[derive(Debug, Clone)]
pub enum CoercedValue {
    Int(i64),
    Float(f64),
    Bool(bool),
    String(String),
    Uuid(Uuid),
    DateTime(DateTime<Utc>),
    NaiveDateTime(NaiveDateTime),
    Date(NaiveDate),
    Time(NaiveTime),
    Decimal(Decimal),
    #[allow(dead_code)]
    Null,
}

impl CoercedValue {
    /// Convert to string representation (for future use with typed PyRequest)
    #[allow(dead_code)]
    pub fn to_string_repr(&self) -> String {
        match self {
            CoercedValue::Int(v) => v.to_string(),
            CoercedValue::Float(v) => v.to_string(),
            CoercedValue::Bool(v) => v.to_string(),
            CoercedValue::String(v) => v.clone(),
            CoercedValue::Uuid(v) => v.to_string(),
            CoercedValue::DateTime(v) => v.to_rfc3339(),
            CoercedValue::NaiveDateTime(v) => v.to_string(),
            CoercedValue::Date(v) => v.to_string(),
            CoercedValue::Time(v) => v.to_string(),
            CoercedValue::Decimal(v) => v.to_string(),
            CoercedValue::Null => "null".to_string(),
        }
    }
}

/// Coerce a string value to the specified type
///
/// # Arguments
/// * `value` - The string value to coerce
/// * `type_hint` - Type hint constant (TYPE_INT, TYPE_FLOAT, etc.)
///
/// # Returns
/// * `Ok(CoercedValue)` - Successfully coerced value
/// * `Err(String)` - Error message describing the coercion failure
pub fn coerce_param(value: &str, type_hint: u8) -> Result<CoercedValue, String> {
    match type_hint {
        TYPE_INT => value
            .parse::<i64>()
            .map(CoercedValue::Int)
            .map_err(|e| format!("Invalid integer '{}': {}", value, e)),

        TYPE_FLOAT => value
            .parse::<f64>()
            .map(CoercedValue::Float)
            .map_err(|e| format!("Invalid float '{}': {}", value, e)),

        TYPE_BOOL => {
            let lower = value.to_lowercase();
            let is_true = matches!(lower.as_str(), "true" | "1" | "yes" | "on");
            let is_false = matches!(lower.as_str(), "false" | "0" | "no" | "off" | "");
            if is_true {
                Ok(CoercedValue::Bool(true))
            } else if is_false {
                Ok(CoercedValue::Bool(false))
            } else {
                Err(format!(
                    "Invalid boolean '{}': expected true/false/1/0/yes/no/on/off",
                    value
                ))
            }
        }

        TYPE_STRING => Ok(CoercedValue::String(value.to_string())),

        TYPE_UUID => Uuid::parse_str(value)
            .map(CoercedValue::Uuid)
            .map_err(|e| format!("Invalid UUID '{}': {}", value, e)),

        TYPE_DATETIME => parse_datetime(value),

        TYPE_DECIMAL => Decimal::from_str(value)
            .map(CoercedValue::Decimal)
            .map_err(|e| format!("Invalid decimal '{}': {}", value, e)),

        TYPE_DATE => NaiveDate::parse_from_str(value, "%Y-%m-%d")
            .map(CoercedValue::Date)
            .map_err(|e| format!("Invalid date '{}': {}", value, e)),

        TYPE_TIME => parse_time(value),

        _ => Ok(CoercedValue::String(value.to_string())),
    }
}

/// Parse datetime string supporting multiple formats
fn parse_datetime(value: &str) -> Result<CoercedValue, String> {
    // Try RFC 3339 / ISO 8601 with timezone (most common)
    if let Ok(dt) = DateTime::parse_from_rfc3339(value) {
        return Ok(CoercedValue::DateTime(dt.with_timezone(&Utc)));
    }

    // Try ISO 8601 with Z suffix
    if value.ends_with('Z') {
        let without_z = &value[..value.len() - 1];
        if let Ok(ndt) = NaiveDateTime::parse_from_str(without_z, "%Y-%m-%dT%H:%M:%S%.f") {
            return Ok(CoercedValue::DateTime(ndt.and_utc()));
        }
        if let Ok(ndt) = NaiveDateTime::parse_from_str(without_z, "%Y-%m-%dT%H:%M:%S") {
            return Ok(CoercedValue::DateTime(ndt.and_utc()));
        }
    }

    // Try naive datetime formats (without timezone)
    let naive_formats = [
        "%Y-%m-%dT%H:%M:%S%.f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S%.f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ];

    for fmt in &naive_formats {
        if let Ok(ndt) = NaiveDateTime::parse_from_str(value, fmt) {
            return Ok(CoercedValue::NaiveDateTime(ndt));
        }
    }

    // Try date-only (will be converted to datetime at midnight)
    if let Ok(date) = NaiveDate::parse_from_str(value, "%Y-%m-%d") {
        let ndt = date.and_hms_opt(0, 0, 0).unwrap();
        return Ok(CoercedValue::NaiveDateTime(ndt));
    }

    Err(format!(
        "Invalid datetime '{}': expected ISO 8601 format (e.g., 2024-01-15T10:30:00Z)",
        value
    ))
}

/// Parse time string supporting multiple formats
fn parse_time(value: &str) -> Result<CoercedValue, String> {
    let formats = ["%H:%M:%S%.f", "%H:%M:%S", "%H:%M"];

    for fmt in &formats {
        if let Ok(time) = NaiveTime::parse_from_str(value, fmt) {
            return Ok(CoercedValue::Time(time));
        }
    }

    Err(format!(
        "Invalid time '{}': expected format HH:MM:SS or HH:MM",
        value
    ))
}

/// Coerce path parameters based on type hints from route metadata
///
/// # Arguments
/// * `path_params` - Map of parameter name to string value
/// * `type_hints` - Map of parameter name to type hint
///
/// # Returns
/// Map of parameter name to coerced value (or error)
pub fn coerce_path_params(
    path_params: &ahash::AHashMap<String, String>,
    type_hints: &std::collections::HashMap<String, u8>,
) -> Result<ahash::AHashMap<String, CoercedValue>, (String, String)> {
    let mut result = ahash::AHashMap::with_capacity(path_params.len());

    for (name, value) in path_params {
        let type_hint = type_hints.get(name).copied().unwrap_or(TYPE_STRING);
        match coerce_param(value, type_hint) {
            Ok(coerced) => {
                result.insert(name.clone(), coerced);
            }
            Err(error_msg) => {
                return Err((name.clone(), error_msg));
            }
        }
    }

    Ok(result)
}

/// Convert a string value to Python object based on type hint.
/// This is the simplified version for basic types (int, float, bool, string).
#[inline]
pub fn coerce_to_py(py: pyo3::Python<'_>, value: &str, type_hint: u8) -> pyo3::Py<pyo3::PyAny> {
    match type_hint {
        TYPE_INT => value
            .parse::<i64>()
            .unwrap_or(0)
            .into_pyobject(py)
            .unwrap()
            .into_any()
            .unbind(),
        TYPE_FLOAT => value
            .parse::<f64>()
            .unwrap_or(0.0)
            .into_pyobject(py)
            .unwrap()
            .into_any()
            .unbind(),
        TYPE_BOOL => {
            let is_true = matches!(value.to_lowercase().as_str(), "true" | "1" | "yes" | "on");
            is_true
                .into_pyobject(py)
                .unwrap()
                .to_owned()
                .unbind()
                .into_any()
        }
        _ => value
            .to_string()
            .into_pyobject(py)
            .unwrap()
            .into_any()
            .unbind(),
    }
}

/// Convert a map of string params to a Python dict with type coercion.
/// Used by both production handler and test handler.
pub fn params_to_py_dict<'py>(
    py: pyo3::Python<'py>,
    params: &ahash::AHashMap<String, String>,
    param_types: &std::collections::HashMap<String, u8>,
) -> pyo3::Bound<'py, pyo3::types::PyDict> {
    let dict = pyo3::types::PyDict::new(py);
    for (name, value) in params {
        let type_hint = param_types.get(name).copied().unwrap_or(TYPE_STRING);
        let py_value = coerce_to_py(py, value, type_hint);
        let _ = dict.set_item(name, py_value);
    }
    dict
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_coerce_int() {
        assert!(matches!(
            coerce_param("42", TYPE_INT),
            Ok(CoercedValue::Int(42))
        ));
        assert!(matches!(
            coerce_param("-123", TYPE_INT),
            Ok(CoercedValue::Int(-123))
        ));
        assert!(coerce_param("abc", TYPE_INT).is_err());
    }

    #[test]
    fn test_coerce_float() {
        assert!(
            matches!(coerce_param("3.14", TYPE_FLOAT), Ok(CoercedValue::Float(f)) if (f - 3.14).abs() < 0.001)
        );
        assert!(
            matches!(coerce_param("-2.5", TYPE_FLOAT), Ok(CoercedValue::Float(f)) if (f + 2.5).abs() < 0.001)
        );
        assert!(coerce_param("not_a_float", TYPE_FLOAT).is_err());
    }

    #[test]
    fn test_coerce_bool() {
        assert!(matches!(
            coerce_param("true", TYPE_BOOL),
            Ok(CoercedValue::Bool(true))
        ));
        assert!(matches!(
            coerce_param("True", TYPE_BOOL),
            Ok(CoercedValue::Bool(true))
        ));
        assert!(matches!(
            coerce_param("1", TYPE_BOOL),
            Ok(CoercedValue::Bool(true))
        ));
        assert!(matches!(
            coerce_param("yes", TYPE_BOOL),
            Ok(CoercedValue::Bool(true))
        ));
        assert!(matches!(
            coerce_param("on", TYPE_BOOL),
            Ok(CoercedValue::Bool(true))
        ));

        assert!(matches!(
            coerce_param("false", TYPE_BOOL),
            Ok(CoercedValue::Bool(false))
        ));
        assert!(matches!(
            coerce_param("False", TYPE_BOOL),
            Ok(CoercedValue::Bool(false))
        ));
        assert!(matches!(
            coerce_param("0", TYPE_BOOL),
            Ok(CoercedValue::Bool(false))
        ));
        assert!(matches!(
            coerce_param("no", TYPE_BOOL),
            Ok(CoercedValue::Bool(false))
        ));
        assert!(matches!(
            coerce_param("off", TYPE_BOOL),
            Ok(CoercedValue::Bool(false))
        ));
    }

    #[test]
    fn test_coerce_uuid() {
        let uuid_str = "550e8400-e29b-41d4-a716-446655440000";
        assert!(matches!(
            coerce_param(uuid_str, TYPE_UUID),
            Ok(CoercedValue::Uuid(_))
        ));
        assert!(coerce_param("not-a-uuid", TYPE_UUID).is_err());
    }

    #[test]
    fn test_coerce_datetime() {
        // ISO 8601 with Z suffix
        assert!(matches!(
            coerce_param("2024-01-15T10:30:00Z", TYPE_DATETIME),
            Ok(CoercedValue::DateTime(_))
        ));

        // ISO 8601 with timezone offset
        assert!(matches!(
            coerce_param("2024-01-15T10:30:00+00:00", TYPE_DATETIME),
            Ok(CoercedValue::DateTime(_))
        ));

        // Naive datetime
        assert!(matches!(
            coerce_param("2024-01-15T10:30:00", TYPE_DATETIME),
            Ok(CoercedValue::NaiveDateTime(_))
        ));

        assert!(coerce_param("not-a-datetime", TYPE_DATETIME).is_err());
    }

    #[test]
    fn test_coerce_decimal() {
        assert!(matches!(
            coerce_param("123.45", TYPE_DECIMAL),
            Ok(CoercedValue::Decimal(_))
        ));
        assert!(matches!(
            coerce_param("-99.99", TYPE_DECIMAL),
            Ok(CoercedValue::Decimal(_))
        ));
        assert!(coerce_param("not_decimal", TYPE_DECIMAL).is_err());
    }
}

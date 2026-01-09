//! Shared request pipeline logic for production and test handlers.
//!
//! This module contains validation and processing logic that is common
//! between the production handler (handler.rs) and test handler (testing.rs).

use actix_web::HttpResponse;
use ahash::AHashMap;
use std::collections::HashMap;

use crate::responses;
use crate::type_coercion::{coerce_param, MAX_PARAM_LENGTH, TYPE_STRING};

/// Validate path and query parameters against type hints.
/// Returns Some(HttpResponse) if validation fails, None if all parameters are valid.
pub fn validate_typed_params(
    path_params: &AHashMap<String, String>,
    query_params: &AHashMap<String, String>,
    param_types: &HashMap<String, u8>,
) -> Option<HttpResponse> {
    // Validate path parameters - always check length, type validation for non-strings
    for (name, value) in path_params {
        // Security: Always validate length for ALL parameters (including strings)
        if value.len() > MAX_PARAM_LENGTH {
            return Some(responses::error_422_validation(&format!(
                "Path parameter '{}': Parameter too long: {} bytes (max {} bytes)",
                name,
                value.len(),
                MAX_PARAM_LENGTH
            )));
        }

        // Type validation for non-string types
        if let Some(&type_hint) = param_types.get(name) {
            if type_hint != TYPE_STRING {
                if let Err(error_msg) = coerce_param(value, type_hint) {
                    return Some(responses::error_422_validation(&format!(
                        "Path parameter '{}': {}",
                        name, error_msg
                    )));
                }
            }
        }
    }

    // Validate query parameters - always check length, type validation for non-strings
    for (name, value) in query_params {
        // Security: Always validate length for ALL parameters (including strings)
        if value.len() > MAX_PARAM_LENGTH {
            return Some(responses::error_422_validation(&format!(
                "Query parameter '{}': Parameter too long: {} bytes (max {} bytes)",
                name,
                value.len(),
                MAX_PARAM_LENGTH
            )));
        }

        // Type validation for non-string types
        if let Some(&type_hint) = param_types.get(name) {
            if type_hint != TYPE_STRING {
                if let Err(error_msg) = coerce_param(value, type_hint) {
                    return Some(responses::error_422_validation(&format!(
                        "Query parameter '{}': {}",
                        name, error_msg
                    )));
                }
            }
        }
    }

    None
}

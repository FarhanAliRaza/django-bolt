use actix_web::HttpResponse;
use ahash::AHashMap;
use jsonwebtoken::{decode, Algorithm, DecodingKey, Validation};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::IntoPyObjectExt;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};

#[derive(Debug, Serialize, Deserialize)]
struct Claims {
    sub: Option<String>,  // Subject (user ID)
    exp: Option<i64>,     // Expiry time
    iat: Option<i64>,     // Issued at
    nbf: Option<i64>,     // Not before
    aud: Option<String>,  // Audience
    iss: Option<String>,  // Issuer
    jti: Option<String>,  // JWT ID
    #[serde(flatten)]
    extra: HashMap<String, serde_json::Value>,  // Any extra claims
}

pub fn check_auth(
    headers: &AHashMap<String, String>,
    config: &HashMap<String, Py<PyAny>>,
    py: Python,
) -> Option<HttpResponse> {
    // Get auth mode
    let mode = config
        .get("mode")
        .and_then(|m| m.extract::<String>(py).ok())
        .unwrap_or_else(|| "jwt".to_string());
    
    // Get header name
    let header_name = config
        .get("header")
        .and_then(|h| h.extract::<String>(py).ok())
        .unwrap_or_else(|| "authorization".to_string())
        .to_lowercase();
    
    // Get auth header value
    let auth_header = headers.get(&header_name);
    
    match mode.as_str() {
        "jwt" => check_jwt_auth(auth_header, config, py),
        "api_key" => check_api_key_auth(auth_header, config, py),
        _ => None, // Unknown mode, allow through
    }
}

fn check_jwt_auth(
    auth_header: Option<&String>,
    config: &HashMap<String, Py<PyAny>>,
    py: Python,
) -> Option<HttpResponse> {
    // Extract token from header
    let token = match auth_header {
        Some(header) => {
            // Remove "Bearer " prefix if present
            if header.starts_with("Bearer ") {
                &header[7..]
            } else {
                header
            }
        }
        None => {
            return Some(
                HttpResponse::Unauthorized()
                    .insert_header(("WWW-Authenticate", "Bearer"))
                    .content_type("application/json")
                    .body(r#"{"detail":"Missing authorization header"}"#)
            );
        }
    };
    
    // Get JWT config - require a secret
    let secret = match config.get("secret").and_then(|s| s.extract::<String>(py).ok()) {
        Some(s) if !s.is_empty() => s,
        _ => {
            // No secret provided - this is a configuration error
            return Some(
                HttpResponse::InternalServerError()
                    .content_type("application/json")
                    .body(r#"{"detail":"JWT authentication requires a secret. Set 'secret' in @auth_required() or ensure Django SECRET_KEY is configured."}"#)
            );
        }
    };
    
    let algorithms = config
        .get("algorithms")
        .and_then(|a| a.extract::<Vec<String>>(py).ok())
        .unwrap_or_else(|| vec!["HS256".to_string()]);
    
    // Map string algorithms to jsonwebtoken Algorithm enum
    let algorithm = match algorithms.first().map(|s| s.as_str()).unwrap_or("HS256") {
        "HS256" => Algorithm::HS256,
        "HS384" => Algorithm::HS384,
        "HS512" => Algorithm::HS512,
        "RS256" => Algorithm::RS256,
        "RS384" => Algorithm::RS384,
        "RS512" => Algorithm::RS512,
        "ES256" => Algorithm::ES256,
        "ES384" => Algorithm::ES384,
        _ => Algorithm::HS256,
    };
    
    // Create validation
    let mut validation = Validation::new(algorithm);
    validation.validate_exp = true;
    validation.validate_nbf = true;
    
    // Decode token
    let key = DecodingKey::from_secret(secret.as_bytes());
    match decode::<Claims>(&token, &key, &validation) {
        Ok(_token_data) => {
            // Token is valid - we could store claims in context here
            // For now, we'll just allow the request through
            None
        }
        Err(err) => {
            Some(
                HttpResponse::Unauthorized()
                    .insert_header(("WWW-Authenticate", "Bearer"))
                    .content_type("application/json")
                    .body(format!(r#"{{"detail":"Invalid JWT token: {}"}}"#, err))
            )
        }
    }
}

fn check_api_key_auth(
    auth_header: Option<&String>,
    config: &HashMap<String, Py<PyAny>>,
    py: Python,
) -> Option<HttpResponse> {
    // Get API key from header
    let api_key = match auth_header {
        Some(key) => {
            // Remove "Bearer " or "ApiKey " prefix if present
            if key.starts_with("Bearer ") {
                &key[7..]
            } else if key.starts_with("ApiKey ") {
                &key[7..]
            } else {
                key
            }
        }
        None => {
            return Some(
                HttpResponse::Unauthorized()
                    .insert_header(("WWW-Authenticate", "ApiKey"))
                    .content_type("application/json")
                    .body(r#"{"detail":"Missing API key"}"#)
            );
        }
    };
    
    // Get valid API keys
    let valid_keys = config
        .get("api_keys")
        .and_then(|k| k.extract::<HashSet<String>>(py).ok())
        .unwrap_or_else(HashSet::new);
    
    if valid_keys.is_empty() || valid_keys.contains(api_key) {
        None // Allow through
    } else {
        Some(
            HttpResponse::Unauthorized()
                .insert_header(("WWW-Authenticate", "ApiKey"))
                .content_type("application/json")
                .body(r#"{"detail":"Invalid API key"}"#)
        )
    }
}

/// Store authentication claims in PyRequest context
pub fn store_auth_claims(
    context: &Py<PyDict>,
    claims: HashMap<String, serde_json::Value>,
    py: Python,
) {
    let dict = context.bind(py);
    
    // Store user_id if present
    if let Some(sub) = claims.get("sub") {
        if let Some(user_id) = sub.as_str() {
            let _ = dict.set_item("user_id", user_id);
        }
    }
    
    // Store all claims as dict
    let claims_dict = PyDict::new(py);
    for (key, value) in claims {
        let py_value = match value {
            serde_json::Value::String(s) => s.into_py_any(py).unwrap_or_else(|_| py.None()),
            serde_json::Value::Number(n) => {
                if let Some(i) = n.as_i64() {
                    i.into_py_any(py).unwrap_or_else(|_| py.None())
                } else if let Some(f) = n.as_f64() {
                    f.into_py_any(py).unwrap_or_else(|_| py.None())
                } else {
                    py.None()
                }
            }
            serde_json::Value::Bool(b) => b.into_py_any(py).unwrap_or_else(|_| py.None()),
            _ => py.None(),
        };
        let _ = claims_dict.set_item(key, py_value);
    }
    let _ = dict.set_item("auth_claims", claims_dict);
}
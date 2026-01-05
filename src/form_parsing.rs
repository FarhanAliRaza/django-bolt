//! Form parsing module for URL-encoded and multipart form data
//!
//! Provides Rust-native form parsing with type coercion and file validation,
//! eliminating Python GIL overhead for form-heavy endpoints.

use actix_multipart::Multipart;
use actix_web::web::Bytes;
use futures_util::StreamExt;
use std::collections::HashMap;
use std::io::Write;
use tempfile::NamedTempFile;

use crate::type_coercion::{coerce_param, CoercedValue, TYPE_STRING};

/// Memory limit for in-memory file storage (1MB default)
pub const DEFAULT_MEMORY_LIMIT: usize = 1024 * 1024;

/// Maximum number of multipart parts allowed
pub const DEFAULT_MAX_PARTS: usize = 100;

/// File content - either in memory or spooled to disk
#[derive(Debug)]
pub enum FileContent {
    /// Small files kept in memory
    Memory(Vec<u8>),
    /// Large files spooled to temporary file on disk
    Disk(NamedTempFile),
}

impl FileContent {
    /// Get the file content as bytes (reads from disk if spooled)
    pub fn as_bytes(&self) -> std::io::Result<Vec<u8>> {
        match self {
            FileContent::Memory(bytes) => Ok(bytes.clone()),
            FileContent::Disk(file) => std::fs::read(file.path()),
        }
    }

    /// Get the temp file path if spooled to disk
    pub fn temp_path(&self) -> Option<&std::path::Path> {
        match self {
            FileContent::Memory(_) => None,
            FileContent::Disk(file) => Some(file.path()),
        }
    }

    /// Check if file is in memory
    pub fn is_in_memory(&self) -> bool {
        matches!(self, FileContent::Memory(_))
    }
}

/// File information with disk spooling support
#[derive(Debug)]
pub struct FileInfo {
    pub filename: String,
    pub content: FileContent,
    pub content_type: String,
    pub size: usize,
}

/// File field constraints for validation
#[derive(Debug, Clone, Default)]
pub struct FileFieldConstraints {
    pub max_size: Option<usize>,
    pub min_size: Option<usize>,
    pub allowed_types: Option<Vec<String>>,
    pub max_files: Option<usize>,
}

/// Validation error with detailed context
#[derive(Debug)]
pub struct ValidationError {
    pub error_type: String,
    pub loc: Vec<String>,
    pub msg: String,
    pub ctx: HashMap<String, serde_json::Value>,
}

impl ValidationError {
    pub fn file_too_large(field: &str, max_size: usize, actual_size: usize) -> Self {
        let mut ctx = HashMap::new();
        ctx.insert("max_size".to_string(), serde_json::json!(max_size));
        ctx.insert("actual_size".to_string(), serde_json::json!(actual_size));
        ValidationError {
            error_type: "file_too_large".to_string(),
            loc: vec!["body".to_string(), field.to_string()],
            msg: format!("File exceeds maximum size of {} bytes", max_size),
            ctx,
        }
    }

    pub fn file_too_small(field: &str, min_size: usize, actual_size: usize) -> Self {
        let mut ctx = HashMap::new();
        ctx.insert("min_size".to_string(), serde_json::json!(min_size));
        ctx.insert("actual_size".to_string(), serde_json::json!(actual_size));
        ValidationError {
            error_type: "file_too_small".to_string(),
            loc: vec!["body".to_string(), field.to_string()],
            msg: format!("File is below minimum size of {} bytes", min_size),
            ctx,
        }
    }

    pub fn invalid_content_type(field: &str, allowed_types: &[String], actual_type: &str) -> Self {
        let mut ctx = HashMap::new();
        ctx.insert(
            "allowed_types".to_string(),
            serde_json::json!(allowed_types),
        );
        ctx.insert("actual_type".to_string(), serde_json::json!(actual_type));
        ValidationError {
            error_type: "file_invalid_content_type".to_string(),
            loc: vec!["body".to_string(), field.to_string()],
            msg: format!("Invalid content type '{}'", actual_type),
            ctx,
        }
    }

    pub fn too_many_files(field: &str, max_files: usize, actual_count: usize) -> Self {
        let mut ctx = HashMap::new();
        ctx.insert("max_files".to_string(), serde_json::json!(max_files));
        ctx.insert("actual_count".to_string(), serde_json::json!(actual_count));
        ValidationError {
            error_type: "file_too_many".to_string(),
            loc: vec!["body".to_string(), field.to_string()],
            msg: "Too many files uploaded".to_string(),
            ctx,
        }
    }

    pub fn type_coercion_error(field: &str, expected_type: &str, error_msg: &str) -> Self {
        let mut ctx = HashMap::new();
        ctx.insert(
            "expected_type".to_string(),
            serde_json::json!(expected_type),
        );
        ctx.insert("error".to_string(), serde_json::json!(error_msg));
        ValidationError {
            error_type: "type_error".to_string(),
            loc: vec!["body".to_string(), field.to_string()],
            msg: format!("Invalid value for field '{}': {}", field, error_msg),
            ctx,
        }
    }

    /// Convert to JSON for HTTP 422 response
    pub fn to_json(&self) -> serde_json::Value {
        serde_json::json!({
            "type": self.error_type,
            "loc": self.loc,
            "msg": self.msg,
            "ctx": self.ctx
        })
    }
}

/// Result of form parsing
pub struct FormParseResult {
    pub form_map: HashMap<String, CoercedValue>,
    pub files_map: HashMap<String, Vec<FileInfo>>,
}

/// Parse URL-encoded form data (application/x-www-form-urlencoded)
pub fn parse_urlencoded(
    body: &Bytes,
    type_hints: &HashMap<String, u8>,
) -> Result<HashMap<String, CoercedValue>, ValidationError> {
    let mut result = HashMap::new();

    // Parse URL-encoded body
    let parsed: Vec<(String, String)> =
        serde_urlencoded::from_bytes(body).map_err(|e| ValidationError {
            error_type: "parse_error".to_string(),
            loc: vec!["body".to_string()],
            msg: format!("Failed to parse form data: {}", e),
            ctx: HashMap::new(),
        })?;

    // Group values by key (handle multiple values for same key)
    let mut grouped: HashMap<String, Vec<String>> = HashMap::new();
    for (key, value) in parsed {
        grouped.entry(key).or_default().push(value);
    }

    // Coerce values based on type hints
    for (key, values) in grouped {
        let type_hint = type_hints.get(&key).copied().unwrap_or(TYPE_STRING);

        // For single values, coerce directly
        // For multiple values, use first value (matching Python behavior)
        let value = values.first().map(|s| s.as_str()).unwrap_or("");

        match coerce_param(value, type_hint) {
            Ok(coerced) => {
                result.insert(key, coerced);
            }
            Err(error_msg) => {
                return Err(ValidationError::type_coercion_error(
                    &key,
                    type_hint_name(type_hint),
                    &error_msg,
                ));
            }
        }
    }

    Ok(result)
}

/// Parse multipart form data with disk spooling for large files
pub async fn parse_multipart(
    mut payload: Multipart,
    type_hints: &HashMap<String, u8>,
    file_constraints: &HashMap<String, FileFieldConstraints>,
    max_upload_size: usize,
    memory_limit: usize,
    max_parts: usize,
) -> Result<FormParseResult, ValidationError> {
    let mut form_map: HashMap<String, CoercedValue> = HashMap::new();
    let mut files_map: HashMap<String, Vec<FileInfo>> = HashMap::new();
    let mut part_count = 0;

    while let Some(item) = payload.next().await {
        let mut field = item.map_err(|e| ValidationError {
            error_type: "multipart_error".to_string(),
            loc: vec!["body".to_string()],
            msg: format!("Failed to read multipart field: {}", e),
            ctx: HashMap::new(),
        })?;

        part_count += 1;
        if part_count > max_parts {
            return Err(ValidationError {
                error_type: "too_many_parts".to_string(),
                loc: vec!["body".to_string()],
                msg: format!("Too many multipart parts (max {})", max_parts),
                ctx: HashMap::new(),
            });
        }

        // Get content disposition - skip if not present
        let Some(content_disposition) = field.content_disposition() else {
            continue;
        };

        let field_name = content_disposition
            .get_name()
            .unwrap_or("unknown")
            .to_string();

        // Check if it's a file upload (has filename)
        if let Some(filename) = content_disposition.get_filename() {
            let filename = filename.to_string();
            let content_type = field
                .content_type()
                .map(|m| m.to_string())
                .unwrap_or_else(|| "application/octet-stream".to_string());

            // Read file content with size limit and disk spooling
            let file_info = read_file_content(
                &mut field,
                &filename,
                &content_type,
                max_upload_size,
                memory_limit,
            )
            .await?;

            // Validate file if constraints exist
            if let Some(constraints) = file_constraints.get(&field_name) {
                validate_file(&file_info, &field_name, constraints)?;
            }

            // Add to files_map
            files_map
                .entry(field_name.clone())
                .or_default()
                .push(file_info);

            // Validate max_files constraint
            if let Some(constraints) = file_constraints.get(&field_name) {
                if let Some(max_files) = constraints.max_files {
                    let count = files_map.get(&field_name).map(|v| v.len()).unwrap_or(0);
                    if count > max_files {
                        return Err(ValidationError::too_many_files(
                            &field_name,
                            max_files,
                            count,
                        ));
                    }
                }
            }
        } else {
            // Regular form field
            let mut value_bytes = Vec::new();
            while let Some(chunk) = field.next().await {
                let data = chunk.map_err(|e| ValidationError {
                    error_type: "read_error".to_string(),
                    loc: vec!["body".to_string(), field_name.clone()],
                    msg: format!("Failed to read field data: {}", e),
                    ctx: HashMap::new(),
                })?;
                value_bytes.extend_from_slice(&data);
            }

            let value = String::from_utf8_lossy(&value_bytes).to_string();

            // Type coercion
            let type_hint = type_hints.get(&field_name).copied().unwrap_or(TYPE_STRING);
            match coerce_param(&value, type_hint) {
                Ok(coerced) => {
                    form_map.insert(field_name, coerced);
                }
                Err(error_msg) => {
                    return Err(ValidationError::type_coercion_error(
                        &field_name,
                        type_hint_name(type_hint),
                        &error_msg,
                    ));
                }
            }
        }
    }

    Ok(FormParseResult {
        form_map,
        files_map,
    })
}

/// Read file content with disk spooling for large files
async fn read_file_content(
    field: &mut actix_multipart::Field,
    filename: &str,
    content_type: &str,
    max_size: usize,
    memory_limit: usize,
) -> Result<FileInfo, ValidationError> {
    let mut size: usize = 0;
    let mut buffer = Vec::new();
    let mut temp_file: Option<NamedTempFile> = None;

    while let Some(chunk) = field.next().await {
        let data = chunk.map_err(|e| ValidationError {
            error_type: "read_error".to_string(),
            loc: vec!["body".to_string()],
            msg: format!("Failed to read file data: {}", e),
            ctx: HashMap::new(),
        })?;

        size += data.len();

        // Check max size limit
        if size > max_size {
            return Err(ValidationError::file_too_large("file", max_size, size));
        }

        // Decide whether to keep in memory or spool to disk
        if temp_file.is_none() && size <= memory_limit {
            // Keep in memory
            buffer.extend_from_slice(&data);
        } else {
            // Spool to disk
            if temp_file.is_none() {
                // Create temp file and write existing buffer
                let mut tf = NamedTempFile::new().map_err(|e| ValidationError {
                    error_type: "io_error".to_string(),
                    loc: vec!["body".to_string()],
                    msg: format!("Failed to create temp file: {}", e),
                    ctx: HashMap::new(),
                })?;
                tf.write_all(&buffer).map_err(|e| ValidationError {
                    error_type: "io_error".to_string(),
                    loc: vec!["body".to_string()],
                    msg: format!("Failed to write to temp file: {}", e),
                    ctx: HashMap::new(),
                })?;
                buffer.clear();
                temp_file = Some(tf);
            }

            // Write chunk to temp file
            if let Some(ref mut tf) = temp_file {
                tf.write_all(&data).map_err(|e| ValidationError {
                    error_type: "io_error".to_string(),
                    loc: vec!["body".to_string()],
                    msg: format!("Failed to write to temp file: {}", e),
                    ctx: HashMap::new(),
                })?;
            }
        }
    }

    let content = if let Some(tf) = temp_file {
        FileContent::Disk(tf)
    } else {
        FileContent::Memory(buffer)
    };

    Ok(FileInfo {
        filename: filename.to_string(),
        content,
        content_type: content_type.to_string(),
        size,
    })
}

/// Validate a file against constraints
fn validate_file(
    file: &FileInfo,
    field_name: &str,
    constraints: &FileFieldConstraints,
) -> Result<(), ValidationError> {
    // Check max_size
    if let Some(max_size) = constraints.max_size {
        if file.size > max_size {
            return Err(ValidationError::file_too_large(
                field_name, max_size, file.size,
            ));
        }
    }

    // Check min_size
    if let Some(min_size) = constraints.min_size {
        if file.size < min_size {
            return Err(ValidationError::file_too_small(
                field_name, min_size, file.size,
            ));
        }
    }

    // Check allowed_types with wildcard matching
    if let Some(ref allowed_types) = constraints.allowed_types {
        if !is_content_type_allowed(&file.content_type, allowed_types) {
            return Err(ValidationError::invalid_content_type(
                field_name,
                allowed_types,
                &file.content_type,
            ));
        }
    }

    Ok(())
}

/// Check if content type matches any allowed pattern (supports wildcards like "image/*")
fn is_content_type_allowed(content_type: &str, allowed_types: &[String]) -> bool {
    for pattern in allowed_types {
        if pattern == "*" || pattern == "*/*" {
            return true;
        }

        if pattern.ends_with("/*") {
            // Wildcard pattern like "image/*"
            let prefix = &pattern[..pattern.len() - 1]; // "image/"
            if content_type.starts_with(prefix) {
                return true;
            }
        } else if pattern == content_type {
            // Exact match
            return true;
        }
    }
    false
}

/// Get human-readable type name from type hint
fn type_hint_name(type_hint: u8) -> &'static str {
    use crate::type_coercion::*;
    match type_hint {
        TYPE_INT => "int",
        TYPE_FLOAT => "float",
        TYPE_BOOL => "bool",
        TYPE_STRING => "str",
        TYPE_UUID => "UUID",
        TYPE_DATETIME => "datetime",
        TYPE_DECIMAL => "Decimal",
        TYPE_DATE => "date",
        TYPE_TIME => "time",
        _ => "unknown",
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_content_type_allowed_exact() {
        let allowed = vec!["image/png".to_string(), "image/jpeg".to_string()];
        assert!(is_content_type_allowed("image/png", &allowed));
        assert!(is_content_type_allowed("image/jpeg", &allowed));
        assert!(!is_content_type_allowed("image/gif", &allowed));
        assert!(!is_content_type_allowed("application/pdf", &allowed));
    }

    #[test]
    fn test_is_content_type_allowed_wildcard() {
        let allowed = vec!["image/*".to_string()];
        assert!(is_content_type_allowed("image/png", &allowed));
        assert!(is_content_type_allowed("image/jpeg", &allowed));
        assert!(is_content_type_allowed("image/gif", &allowed));
        assert!(!is_content_type_allowed("application/pdf", &allowed));
    }

    #[test]
    fn test_is_content_type_allowed_all() {
        let allowed = vec!["*/*".to_string()];
        assert!(is_content_type_allowed("image/png", &allowed));
        assert!(is_content_type_allowed("application/pdf", &allowed));
        assert!(is_content_type_allowed("text/plain", &allowed));
    }

    #[test]
    fn test_parse_urlencoded() {
        let body = Bytes::from("name=John&age=30&active=true");
        let mut type_hints = HashMap::new();
        type_hints.insert("name".to_string(), TYPE_STRING);
        type_hints.insert("age".to_string(), crate::type_coercion::TYPE_INT);
        type_hints.insert("active".to_string(), crate::type_coercion::TYPE_BOOL);

        let result = parse_urlencoded(&body, &type_hints).unwrap();

        assert!(matches!(
            result.get("name"),
            Some(CoercedValue::String(s)) if s == "John"
        ));
        assert!(matches!(result.get("age"), Some(CoercedValue::Int(30))));
        assert!(matches!(
            result.get("active"),
            Some(CoercedValue::Bool(true))
        ));
    }

    #[test]
    fn test_validation_error_json() {
        let err = ValidationError::file_too_large("avatar", 1024, 2048);
        let json = err.to_json();

        assert_eq!(json["type"], "file_too_large");
        assert_eq!(json["loc"], serde_json::json!(["body", "avatar"]));
        assert_eq!(json["ctx"]["max_size"], 1024);
        assert_eq!(json["ctx"]["actual_size"], 2048);
    }
}

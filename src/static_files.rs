//! Static file serving with Django integration.
//!
//! Uses actix-files for efficient file serving with proper HTTP semantics:
//! - Streaming (memory efficient for large files)
//! - ETag and Last-Modified headers
//! - If-None-Match / If-Modified-Since support (304 responses)
//! - Range requests for resumable downloads
//! - Content-Type detection
//!
//! File lookup order:
//! 1. Configured directories (STATIC_ROOT, STATICFILES_DIRS) - fast path
//! 2. Django's staticfiles finders (for app static files like admin)

use actix_files::NamedFile;
use actix_web::{http::header, web, HttpRequest, HttpResponse};
use pyo3::prelude::*;
use std::path::{Path, PathBuf};

/// Find a static file in the configured directories (fast path)
fn find_in_directories(relative_path: &str, directories: &[String]) -> Option<PathBuf> {
    // Security: prevent directory traversal
    if relative_path.contains("..") || relative_path.starts_with('/') {
        return None;
    }

    for dir in directories {
        let full_path = Path::new(dir).join(relative_path);

        // Verify the resolved path is still within the directory (prevent symlink attacks)
        if let Ok(canonical) = full_path.canonicalize() {
            if let Ok(dir_canonical) = Path::new(dir).canonicalize() {
                if canonical.starts_with(&dir_canonical) && canonical.is_file() {
                    return Some(canonical);
                }
            }
        }
    }
    None
}

/// Find a static file using Django's staticfiles finders (for app-level static files)
fn find_with_django_finders(relative_path: &str) -> Option<PathBuf> {
    Python::attach(|py| {
        // Import the find_static_file function from django_bolt.admin.static
        let static_module = py.import("django_bolt.admin.static").ok()?;
        let find_fn = static_module.getattr("find_static_file").ok()?;

        // Call the Python function
        let result = find_fn.call1((relative_path,)).ok()?;

        // Extract the path string
        if result.is_none() {
            return None;
        }

        let path_str: String = result.extract().ok()?;
        Some(PathBuf::from(path_str))
    })
}

/// Handler for static file requests
///
/// Uses actix-files NamedFile which provides:
/// - Streaming responses (memory efficient)
/// - Automatic ETag generation
/// - Last-Modified headers
/// - Conditional request handling (304 Not Modified)
/// - Range request support
/// - Content-Type detection
/// - CSP headers from Django settings (pre-built at server startup)
pub async fn handle_static_file(
    req: HttpRequest,
    path: web::Path<String>,
    directories: web::Data<Vec<String>>,
    csp_header: web::Data<Option<String>>,
) -> actix_web::Result<HttpResponse> {
    // Strip leading slash if present (route captures include it)
    let relative_path = path.into_inner();
    let relative_path = relative_path.trim_start_matches('/');

    // Security check
    if relative_path.contains("..") {
        return Err(actix_web::error::ErrorBadRequest("Invalid path"));
    }

    // Try to find the file (fast path first, then Django finders)
    let file_path = find_in_directories(&relative_path, directories.as_ref())
        .or_else(|| find_with_django_finders(&relative_path));

    let file_path = match file_path {
        Some(p) => p,
        None => {
            return Err(actix_web::error::ErrorNotFound(format!(
                "Static file not found: {}",
                relative_path
            )));
        }
    };

    // Open the file using NamedFile for proper HTTP semantics
    // Use sync reads for files under 256KB (faster for typical static assets)
    // See: https://github.com/actix/actix-web/pull/3706
    let named_file = NamedFile::open_async(&file_path)
        .await
        .map_err(|_| actix_web::error::ErrorNotFound("File not found"))?
        .read_mode_threshold(256 * 1024); // 256KB threshold for sync reads

    // Convert NamedFile to HttpResponse and add CSP header if configured
    let mut response = named_file.into_response(&req);

    // Apply CSP header from Django settings (pre-built at server startup)
    if let Some(ref csp) = csp_header.as_ref() {
        response.headers_mut().insert(
            header::CONTENT_SECURITY_POLICY,
            header::HeaderValue::from_str(csp).unwrap_or_else(|_| {
                header::HeaderValue::from_static("default-src 'self'")
            }),
        );
    }

    Ok(response)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::{self, File};
    use std::io::Write;
    use tempfile::TempDir;

    #[test]
    fn test_find_in_directories() {
        let temp_dir = TempDir::new().unwrap();
        let temp_path = temp_dir.path();

        // Create a test file
        let css_dir = temp_path.join("css");
        fs::create_dir(&css_dir).unwrap();
        let mut file = File::create(css_dir.join("style.css")).unwrap();
        file.write_all(b"body { color: red; }").unwrap();

        let directories = vec![temp_path.to_string_lossy().to_string()];

        // Should find existing file
        let result = find_in_directories("css/style.css", &directories);
        assert!(result.is_some());

        // Should not find non-existent file
        let result = find_in_directories("css/missing.css", &directories);
        assert!(result.is_none());

        // Should reject directory traversal
        let result = find_in_directories("../etc/passwd", &directories);
        assert!(result.is_none());

        // Should reject absolute paths
        let result = find_in_directories("/etc/passwd", &directories);
        assert!(result.is_none());
    }

    #[test]
    fn test_find_in_multiple_directories() {
        let dir1 = TempDir::new().unwrap();
        let dir2 = TempDir::new().unwrap();

        // Create file only in dir1
        let mut file1 = File::create(dir1.path().join("file1.txt")).unwrap();
        file1.write_all(b"content1").unwrap();

        // Create file only in dir2
        let mut file2 = File::create(dir2.path().join("file2.txt")).unwrap();
        file2.write_all(b"content2").unwrap();

        let directories = vec![
            dir1.path().to_string_lossy().to_string(),
            dir2.path().to_string_lossy().to_string(),
        ];

        // Should find file1 in dir1
        let result = find_in_directories("file1.txt", &directories);
        assert!(result.is_some());
        assert!(result.unwrap().to_string_lossy().contains("file1.txt"));

        // Should find file2 in dir2
        let result = find_in_directories("file2.txt", &directories);
        assert!(result.is_some());
        assert!(result.unwrap().to_string_lossy().contains("file2.txt"));
    }

    #[test]
    fn test_directory_priority() {
        let dir1 = TempDir::new().unwrap();
        let dir2 = TempDir::new().unwrap();

        // Create same-named file in both directories
        let mut file1 = File::create(dir1.path().join("shared.txt")).unwrap();
        file1.write_all(b"from_dir1").unwrap();

        let mut file2 = File::create(dir2.path().join("shared.txt")).unwrap();
        file2.write_all(b"from_dir2").unwrap();

        // dir1 should take priority (listed first)
        let directories = vec![
            dir1.path().to_string_lossy().to_string(),
            dir2.path().to_string_lossy().to_string(),
        ];

        let result = find_in_directories("shared.txt", &directories);
        assert!(result.is_some());

        // Verify it's from dir1
        let content = fs::read_to_string(result.unwrap()).unwrap();
        assert_eq!(content, "from_dir1");
    }
}

use ahash::AHashMap;
use matchit::{Match, Router as MatchRouter};
use pyo3::prelude::*;

pub struct Route {
    pub handler: Py<PyAny>,
    pub handler_id: usize, // Store handler_id for middleware metadata lookup
}

/// Convert FastAPI-style paths like /items/{id} and /files/{path:path}
/// Matchit uses the same {param} syntax as FastAPI, but uses *path for catch-all
pub fn convert_path(path: &str) -> String {
    let mut result = String::with_capacity(path.len());
    let mut chars = path.chars().peekable();

    while let Some(ch) = chars.next() {
        if ch == '{' {
            result.push(ch);
            let mut param = String::new();

            // Collect parameter name and optional type
            while let Some(&next_ch) = chars.peek() {
                if next_ch == '}' {
                    chars.next(); // consume '}'
                    break;
                }
                param.push(chars.next().unwrap());
            }

            // Check if it has :path suffix
            if let Some(colon_pos) = param.find(':') {
                let name = &param[..colon_pos];
                let type_ = &param[colon_pos + 1..];

                if type_ == "path" {
                    // Convert {name:path} to {*name} (catch-all)
                    // matchit requires catch-all to be inside braces: {*param}
                    result.push('*');
                    result.push_str(name);
                    result.push('}');
                    continue;
                }
            }

            // Regular parameter: just keep the name
            if let Some(colon_pos) = param.find(':') {
                result.push_str(&param[..colon_pos]);
            } else {
                result.push_str(&param);
            }
            result.push('}');
        } else {
            result.push(ch);
        }
    }

    result
}

pub struct Router {
    get: MatchRouter<Route>,
    post: MatchRouter<Route>,
    put: MatchRouter<Route>,
    patch: MatchRouter<Route>,
    delete: MatchRouter<Route>,
    head: MatchRouter<Route>,
    options: MatchRouter<Route>,
}

impl Router {
    pub fn new() -> Self {
        Router {
            get: MatchRouter::new(),
            post: MatchRouter::new(),
            put: MatchRouter::new(),
            patch: MatchRouter::new(),
            delete: MatchRouter::new(),
            head: MatchRouter::new(),
            options: MatchRouter::new(),
        }
    }

    pub fn register(
        &mut self,
        method: &str,
        path: &str,
        handler_id: usize,
        handler: Py<PyAny>,
    ) -> PyResult<()> {
        // Convert path from FastAPI syntax to matchit syntax
        let converted_path = convert_path(path);

        let route = Route {
            handler,
            handler_id,
        };

        let router = match method {
            "GET" => &mut self.get,
            "POST" => &mut self.post,
            "PUT" => &mut self.put,
            "PATCH" => &mut self.patch,
            "DELETE" => &mut self.delete,
            "HEAD" => &mut self.head,
            "OPTIONS" => &mut self.options,
            _ => {
                return Err(pyo3::exceptions::PyValueError::new_err(format!(
                    "Unsupported method: {}",
                    method
                )))
            }
        };

        router.insert(&converted_path, route).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Failed to register route: {}", e))
        })?;

        Ok(())
    }

    pub fn find(
        &self,
        method: &str,
        path: &str,
    ) -> Option<(&Route, AHashMap<String, String>, usize)> {
        let router = match method {
            "GET" => &self.get,
            "POST" => &self.post,
            "PUT" => &self.put,
            "PATCH" => &self.patch,
            "DELETE" => &self.delete,
            "HEAD" => &self.head,
            "OPTIONS" => &self.options,
            _ => return None,
        };

        match router.at(path) {
            Ok(Match { value, params }) => {
                let mut path_params = AHashMap::new();
                for (key, value) in params.iter() {
                    path_params.insert(key.to_string(), value.to_string());
                }
                Some((value, path_params, value.handler_id))
            }
            Err(_) => None,
        }
    }

    /// Find all HTTP methods that have handlers registered for the given path.
    /// Used for automatic OPTIONS handling to return the Allow header.
    ///
    /// Returns a vector of method names (e.g., ["GET", "POST", "PUT"]).
    /// Always includes "OPTIONS" if any methods are found (for automatic OPTIONS support).
    pub fn find_all_methods(&self, path: &str) -> Vec<String> {
        let mut methods = Vec::new();

        // Check each method router to see if it has a handler for this path
        let method_routers = [
            ("GET", &self.get),
            ("POST", &self.post),
            ("PUT", &self.put),
            ("PATCH", &self.patch),
            ("DELETE", &self.delete),
            ("HEAD", &self.head),
            ("OPTIONS", &self.options),
        ];

        for (method_name, router) in method_routers.iter() {
            if router.at(path).is_ok() {
                methods.push(method_name.to_string());
            }
        }

        // If we found any methods and OPTIONS is not explicitly registered, add it
        // (automatic OPTIONS support for all routes)
        if !methods.is_empty() && !methods.contains(&"OPTIONS".to_string()) {
            methods.push("OPTIONS".to_string());
        }

        methods
    }
}

pub fn parse_query_string(query: &str) -> AHashMap<String, String> {
    let mut params = AHashMap::new();
    if query.is_empty() {
        return params;
    }

    for pair in query.split('&') {
        if let Some(eq_pos) = pair.find('=') {
            let key = &pair[..eq_pos];
            let value = &pair[eq_pos + 1..];
            if !key.is_empty() {
                params.insert(
                    urlencoding::decode(key)
                        .unwrap_or_else(|_| key.into())
                        .into_owned(),
                    urlencoding::decode(value)
                        .unwrap_or_else(|_| value.into())
                        .into_owned(),
                );
            }
        } else if !pair.is_empty() {
            params.insert(
                urlencoding::decode(pair)
                    .unwrap_or_else(|_| pair.into())
                    .into_owned(),
                String::new(),
            );
        }
    }

    params
}

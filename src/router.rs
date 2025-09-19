use ahash::AHashMap;
use matchit::{Match, Router as MatchRouter};
use pyo3::prelude::*;

#[derive(Clone)]
pub struct Route {
    pub handler_id: usize,
    pub handler: Py<PyAny>,
}

pub struct Router {
    get: MatchRouter<Route>,
    post: MatchRouter<Route>,
    put: MatchRouter<Route>,
    patch: MatchRouter<Route>,
    delete: MatchRouter<Route>,
}

impl Router {
    pub fn new() -> Self {
        Router {
            get: MatchRouter::new(),
            post: MatchRouter::new(),
            put: MatchRouter::new(),
            patch: MatchRouter::new(),
            delete: MatchRouter::new(),
        }
    }

    pub fn register(&mut self, method: &str, path: &str, handler_id: usize, handler: Py<PyAny>) -> PyResult<()> {
        let route = Route { handler_id, handler };
        
        let router = match method {
            "GET" => &mut self.get,
            "POST" => &mut self.post,
            "PUT" => &mut self.put,
            "PATCH" => &mut self.patch,
            "DELETE" => &mut self.delete,
            _ => return Err(pyo3::exceptions::PyValueError::new_err(format!("Unsupported method: {}", method))),
        };

        router.insert(path, route)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Failed to register route: {}", e)))?;
        
        Ok(())
    }

    pub fn find(&self, method: &str, path: &str) -> Option<(Route, AHashMap<String, String>)> {
        let router = match method {
            "GET" => &self.get,
            "POST" => &self.post,
            "PUT" => &self.put,
            "PATCH" => &self.patch,
            "DELETE" => &self.delete,
            _ => return None,
        };

        match router.at(path) {
            Ok(Match { value, params }) => {
                let mut path_params = AHashMap::new();
                for (key, value) in params.iter() {
                    path_params.insert(key.to_string(), value.to_string());
                }
                Some((value.clone(), path_params))
            }
            Err(_) => None,
        }
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
                    urlencoding::decode(key).unwrap_or_else(|_| key.into()).into_owned(),
                    urlencoding::decode(value).unwrap_or_else(|_| value.into()).into_owned(),
                );
            }
        } else if !pair.is_empty() {
            params.insert(
                urlencoding::decode(pair).unwrap_or_else(|_| pair.into()).into_owned(),
                String::new(),
            );
        }
    }
    
    params
}
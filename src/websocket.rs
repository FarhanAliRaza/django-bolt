//! WebSocket support for Django-Bolt
//!
//! This module provides WebSocket route registration and basic handling.
//! The actual WebSocket protocol handling is done via actix-web-actors.

use actix::{Actor, ActorContext, AsyncContext, StreamHandler};
use actix_web::{web, HttpRequest, HttpResponse};
use actix_web_actors::ws;
use ahash::AHashMap;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::time::{Duration, Instant};

/// How often heartbeat pings are sent
const HEARTBEAT_INTERVAL: Duration = Duration::from_secs(5);
/// How long before lack of client response causes a timeout
const CLIENT_TIMEOUT: Duration = Duration::from_secs(10);

/// WebSocket actor that handles the connection lifecycle
pub struct WebSocketActor {
    /// Client heartbeat tracking
    hb: Instant,
    /// Python handler function
    handler: Py<PyAny>,
    /// Handler ID for metadata lookup
    handler_id: usize,
    /// Path parameters from URL
    path_params: AHashMap<String, String>,
    /// Request scope data for Python
    scope: Py<PyAny>,
}

impl WebSocketActor {
    pub fn new(
        handler: Py<PyAny>,
        handler_id: usize,
        path_params: AHashMap<String, String>,
        scope: Py<PyAny>,
    ) -> Self {
        WebSocketActor {
            hb: Instant::now(),
            handler,
            handler_id,
            path_params,
            scope,
        }
    }

    /// Start heartbeat process
    fn hb(&self, ctx: &mut ws::WebsocketContext<Self>) {
        ctx.run_interval(HEARTBEAT_INTERVAL, |act, ctx| {
            if Instant::now().duration_since(act.hb) > CLIENT_TIMEOUT {
                ctx.stop();
                return;
            }
            ctx.ping(b"");
        });
    }
}

impl Actor for WebSocketActor {
    type Context = ws::WebsocketContext<Self>;

    fn started(&mut self, ctx: &mut Self::Context) {
        self.hb(ctx);
        // Note: Full Python handler integration requires additional work
        // This is a scaffold for the WebSocket actor
    }
}

impl StreamHandler<Result<ws::Message, ws::ProtocolError>> for WebSocketActor {
    fn handle(&mut self, msg: Result<ws::Message, ws::ProtocolError>, ctx: &mut Self::Context) {
        match msg {
            Ok(ws::Message::Ping(msg)) => {
                self.hb = Instant::now();
                ctx.pong(&msg);
            }
            Ok(ws::Message::Pong(_)) => {
                self.hb = Instant::now();
            }
            Ok(ws::Message::Text(text)) => {
                // Echo for now - full implementation bridges to Python
                ctx.text(text);
            }
            Ok(ws::Message::Binary(bin)) => {
                ctx.binary(bin);
            }
            Ok(ws::Message::Close(reason)) => {
                ctx.close(reason);
                ctx.stop();
            }
            Err(e) => {
                eprintln!("[django-bolt] WebSocket protocol error: {}", e);
                ctx.stop();
            }
            _ => {}
        }
    }
}

/// WebSocket route definition
pub struct WebSocketRoute {
    pub path: String,
    pub handler_id: usize,
    pub handler: Py<PyAny>,
}

/// WebSocket router for matching paths to handlers
pub struct WebSocketRouter {
    /// Static routes (no path params)
    static_routes: AHashMap<String, WebSocketRoute>,
    /// Dynamic routes (with path params)
    dynamic_router: matchit::Router<WebSocketRoute>,
    /// Track if we have any dynamic routes
    has_dynamic_routes: bool,
}

impl WebSocketRouter {
    pub fn new() -> Self {
        WebSocketRouter {
            static_routes: AHashMap::new(),
            dynamic_router: matchit::Router::new(),
            has_dynamic_routes: false,
        }
    }

    pub fn register(
        &mut self,
        path: &str,
        handler_id: usize,
        handler: Py<PyAny>,
    ) -> PyResult<()> {
        let route = WebSocketRoute {
            path: path.to_string(),
            handler_id,
            handler,
        };

        if !path.contains('{') {
            self.static_routes.insert(path.to_string(), route);
        } else {
            let converted = crate::router::convert_path(path);
            self.dynamic_router.insert(&converted, route).map_err(|e| {
                pyo3::exceptions::PyValueError::new_err(format!(
                    "Failed to register WebSocket route: {}",
                    e
                ))
            })?;
            self.has_dynamic_routes = true;
        }

        Ok(())
    }

    pub fn find(&self, path: &str) -> Option<(&WebSocketRoute, AHashMap<String, String>)> {
        if let Some(route) = self.static_routes.get(path) {
            return Some((route, AHashMap::new()));
        }

        if self.has_dynamic_routes {
            if let Ok(matched) = self.dynamic_router.at(path) {
                let mut params = AHashMap::new();
                for (key, value) in matched.params.iter() {
                    params.insert(key.to_string(), value.to_string());
                }
                return Some((matched.value, params));
            }
        }

        None
    }

    pub fn is_empty(&self) -> bool {
        self.static_routes.is_empty() && !self.has_dynamic_routes
    }
}

/// HTTP handler for WebSocket upgrade requests
pub async fn handle_websocket_upgrade(
    req: HttpRequest,
    stream: web::Payload,
    handler: Py<PyAny>,
    handler_id: usize,
    path_params: AHashMap<String, String>,
) -> actix_web::Result<HttpResponse> {
    // Build scope for Python
    let scope = Python::attach(|py| -> PyResult<Py<PyAny>> {
        let scope_dict = PyDict::new(py);
        scope_dict.set_item("path", req.path())?;
        scope_dict.set_item("query_string", req.query_string().as_bytes())?;

        let headers_dict = PyDict::new(py);
        for (key, value) in req.headers().iter() {
            if let Ok(v) = value.to_str() {
                headers_dict.set_item(key.as_str(), v)?;
            }
        }
        scope_dict.set_item("headers", headers_dict)?;

        let params_dict = PyDict::new(py);
        for (k, v) in path_params.iter() {
            params_dict.set_item(k, v)?;
        }
        scope_dict.set_item("path_params", params_dict)?;

        if let Some(peer) = req.peer_addr() {
            let client = (peer.ip().to_string(), peer.port());
            scope_dict.set_item("client", client)?;
        }

        Ok(scope_dict.into())
    })
    .map_err(|e| actix_web::error::ErrorInternalServerError(format!("Scope error: {}", e)))?;

    let actor = WebSocketActor::new(handler, handler_id, path_params, scope);
    ws::start(actor, &req, stream)
}

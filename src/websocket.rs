//! WebSocket support for Django-Bolt
//!
//! This module provides WebSocket support with proper Python handler integration.
//! Uses tokio channels to bridge Actix's actor-based WebSocket with Python's
//! ASGI-style async interface.

use actix::{Actor, ActorContext, Addr, AsyncContext, Handler, Message, StreamHandler};
use actix_web::{web, HttpRequest, HttpResponse};
use actix_web_actors::ws;
use ahash::AHashMap;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyTuple};
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::mpsc;

use crate::state::ROUTE_METADATA;
use crate::validation::{validate_auth_and_guards, AuthGuardResult};

/// Get WebSocket channel buffer size from settings
fn get_channel_buffer_size() -> usize {
    // 1. Check environment variable
    if let Ok(val) = std::env::var("DJANGO_BOLT_WS_CHANNEL_SIZE") {
        if let Ok(size) = val.parse::<usize>() {
            return size;
        }
    }

    // 2. Check Django settings
    Python::attach(|py| {
        if let Ok(django_conf) = py.import("django.conf") {
            if let Ok(settings) = django_conf.getattr("settings") {
                if let Ok(size) = settings.getattr("BOLT_WS_CHANNEL_SIZE") {
                    if let Ok(val) = size.extract::<usize>() {
                        return val;
                    }
                }
            }
        }
        100 // Default
    })
}

/// Get WebSocket heartbeat interval from settings
fn get_heartbeat_interval() -> Duration {
    // 1. Check environment variable
    if let Ok(val) = std::env::var("DJANGO_BOLT_WS_HEARTBEAT_INTERVAL") {
        if let Ok(secs) = val.parse::<u64>() {
            return Duration::from_secs(secs);
        }
    }

    // 2. Check Django settings
    Python::attach(|py| {
        if let Ok(django_conf) = py.import("django.conf") {
            if let Ok(settings) = django_conf.getattr("settings") {
                if let Ok(interval) = settings.getattr("BOLT_WS_HEARTBEAT_INTERVAL") {
                    if let Ok(secs) = interval.extract::<u64>() {
                        return Duration::from_secs(secs);
                    }
                }
            }
        }
        Duration::from_secs(5) // Default
    })
}

/// Get WebSocket client timeout from settings
fn get_client_timeout() -> Duration {
    // 1. Check environment variable
    if let Ok(val) = std::env::var("DJANGO_BOLT_WS_CLIENT_TIMEOUT") {
        if let Ok(secs) = val.parse::<u64>() {
            return Duration::from_secs(secs);
        }
    }

    // 2. Check Django settings
    Python::attach(|py| {
        if let Ok(django_conf) = py.import("django.conf") {
            if let Ok(settings) = django_conf.getattr("settings") {
                if let Ok(timeout) = settings.getattr("BOLT_WS_CLIENT_TIMEOUT") {
                    if let Ok(secs) = timeout.extract::<u64>() {
                        return Duration::from_secs(secs);
                    }
                }
            }
        }
        Duration::from_secs(10) // Default
    })
}

/// Get allowed WebSocket origins from settings (for CORS-like protection)
fn get_allowed_origins() -> Option<Vec<String>> {
    // 1. Check environment variable (comma-separated)
    if let Ok(val) = std::env::var("DJANGO_BOLT_WS_ALLOWED_ORIGINS") {
        if val == "*" {
            return None; // Allow all
        }
        return Some(val.split(',').map(|s| s.trim().to_string()).collect());
    }

    // 2. Check Django settings
    Python::attach(|py| {
        if let Ok(django_conf) = py.import("django.conf") {
            if let Ok(settings) = django_conf.getattr("settings") {
                // Check BOLT_WS_ALLOWED_ORIGINS first
                if let Ok(origins) = settings.getattr("BOLT_WS_ALLOWED_ORIGINS") {
                    if let Ok(list) = origins.extract::<Vec<String>>() {
                        if list.iter().any(|o| o == "*") {
                            return None;
                        }
                        return Some(list);
                    }
                }
                // Fall back to CORS_ALLOWED_ORIGINS if available
                if let Ok(origins) = settings.getattr("CORS_ALLOWED_ORIGINS") {
                    if let Ok(list) = origins.extract::<Vec<String>>() {
                        return Some(list);
                    }
                }
            }
        }
        None // Default: allow all (for backward compatibility)
    })
}

/// Maximum WebSocket message size (1MB default)
const MAX_MESSAGE_SIZE: usize = 1024 * 1024;

/// Message types for communication between Actix actor and Python handler
#[derive(Debug)]
pub enum WsMessage {
    /// Text message from client
    Text(String),
    /// Binary message from client
    Binary(Vec<u8>),
    /// Client disconnected
    Disconnect { code: u16 },
    /// Connection accepted by Python handler
    Accept { subprotocol: Option<String> },
    /// Send text to client (from Python)
    SendText(String),
    /// Send binary to client (from Python)
    SendBinary(Vec<u8>),
    /// Close connection (from Python)
    Close { code: u16, reason: String },
}

/// Actix message for sending data to client
#[derive(Message)]
#[rtype(result = "()")]
pub struct SendToClient(pub WsMessage);

/// WebSocket actor that bridges Actix and Python
pub struct WebSocketActor {
    /// Client heartbeat tracking
    hb: Instant,
    /// Channel to send received messages to Python handler
    to_python_tx: mpsc::Sender<WsMessage>,
    /// Whether connection has been accepted
    accepted: bool,
    /// Close code if connection was closed
    close_code: Option<u16>,
    /// Heartbeat interval (configurable)
    heartbeat_interval: Duration,
    /// Client timeout (configurable)
    client_timeout: Duration,
}

impl WebSocketActor {
    pub fn new(to_python_tx: mpsc::Sender<WsMessage>) -> Self {
        WebSocketActor {
            hb: Instant::now(),
            to_python_tx,
            accepted: false,
            close_code: None,
            heartbeat_interval: get_heartbeat_interval(),
            client_timeout: get_client_timeout(),
        }
    }

    /// Start heartbeat process
    fn start_heartbeat(&self, ctx: &mut ws::WebsocketContext<Self>) {
        let timeout = self.client_timeout;
        ctx.run_interval(self.heartbeat_interval, move |act, ctx| {
            if Instant::now().duration_since(act.hb) > timeout {
                // Send disconnect to Python
                let _ = act.to_python_tx.try_send(WsMessage::Disconnect { code: 1001 });
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
        self.start_heartbeat(ctx);
    }

    fn stopped(&mut self, _ctx: &mut Self::Context) {
        // Notify Python handler that connection is closed
        let code = self.close_code.unwrap_or(1000);
        let _ = self.to_python_tx.try_send(WsMessage::Disconnect { code });
    }
}

/// Handle messages from Python to send to client
impl Handler<SendToClient> for WebSocketActor {
    type Result = ();

    fn handle(&mut self, msg: SendToClient, ctx: &mut Self::Context) {
        match msg.0 {
            WsMessage::Accept { subprotocol: _ } => {
                self.accepted = true;
                // Accept is implicit in Actix - connection is already open
            }
            WsMessage::SendText(text) => {
                if self.accepted {
                    ctx.text(text);
                }
            }
            WsMessage::SendBinary(data) => {
                if self.accepted {
                    ctx.binary(data);
                }
            }
            WsMessage::Close { code, reason } => {
                self.close_code = Some(code);
                ctx.close(Some(ws::CloseReason {
                    code: ws::CloseCode::Other(code),
                    description: if reason.is_empty() {
                        None
                    } else {
                        Some(reason)
                    },
                }));
                ctx.stop();
            }
            _ => {}
        }
    }
}

/// Handle incoming WebSocket messages from client
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
                self.hb = Instant::now();
                // Validate message size
                if text.len() > MAX_MESSAGE_SIZE {
                    eprintln!(
                        "[django-bolt] WebSocket message too large: {} bytes (max {})",
                        text.len(),
                        MAX_MESSAGE_SIZE
                    );
                    self.close_code = Some(1009); // Message too big
                    ctx.close(Some(ws::CloseReason {
                        code: ws::CloseCode::Size,
                        description: Some("Message too large".to_string()),
                    }));
                    ctx.stop();
                    return;
                }
                // Forward to Python handler
                if let Err(e) = self.to_python_tx.try_send(WsMessage::Text(text.to_string())) {
                    eprintln!("[django-bolt] Failed to forward message to Python: {}", e);
                }
            }
            Ok(ws::Message::Binary(bin)) => {
                self.hb = Instant::now();
                // Validate message size
                if bin.len() > MAX_MESSAGE_SIZE {
                    eprintln!(
                        "[django-bolt] WebSocket binary message too large: {} bytes (max {})",
                        bin.len(),
                        MAX_MESSAGE_SIZE
                    );
                    self.close_code = Some(1009);
                    ctx.close(Some(ws::CloseReason {
                        code: ws::CloseCode::Size,
                        description: Some("Message too large".to_string()),
                    }));
                    ctx.stop();
                    return;
                }
                if let Err(e) = self.to_python_tx.try_send(WsMessage::Binary(bin.to_vec())) {
                    eprintln!("[django-bolt] Failed to forward binary to Python: {}", e);
                }
            }
            Ok(ws::Message::Close(reason)) => {
                let code = reason
                    .as_ref()
                    .map(|r| match r.code {
                        ws::CloseCode::Normal => 1000,
                        ws::CloseCode::Away => 1001,
                        ws::CloseCode::Protocol => 1002,
                        ws::CloseCode::Unsupported => 1003,
                        ws::CloseCode::Abnormal => 1006,
                        ws::CloseCode::Invalid => 1007,
                        ws::CloseCode::Policy => 1008,
                        ws::CloseCode::Size => 1009,
                        ws::CloseCode::Extension => 1010,
                        ws::CloseCode::Error => 1011,
                        ws::CloseCode::Restart => 1012,
                        ws::CloseCode::Again => 1013,
                        ws::CloseCode::Other(c) => c,
                        _ => 1000, // Unknown close codes default to normal
                    })
                    .unwrap_or(1000);
                self.close_code = Some(code);
                let _ = self.to_python_tx.try_send(WsMessage::Disconnect { code });
                ctx.close(reason);
                ctx.stop();
            }
            Err(e) => {
                eprintln!("[django-bolt] WebSocket protocol error: {}", e);
                self.close_code = Some(1002); // Protocol error
                let _ = self.to_python_tx.try_send(WsMessage::Disconnect { code: 1002 });
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
    /// Static routes (no path params) - O(1) lookup
    static_routes: AHashMap<String, WebSocketRoute>,
    /// Dynamic routes (with path params) - radix tree
    dynamic_router: matchit::Router<WebSocketRoute>,
    /// Track if we have any dynamic routes
    has_dynamic_routes: bool,
    /// Store dynamic route paths for Actix registration
    dynamic_paths: Vec<String>,
}

impl WebSocketRouter {
    pub fn new() -> Self {
        WebSocketRouter {
            static_routes: AHashMap::new(),
            dynamic_router: matchit::Router::new(),
            has_dynamic_routes: false,
            dynamic_paths: Vec::new(),
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
            self.dynamic_paths.push(path.to_string());
        }

        Ok(())
    }

    pub fn find(&self, path: &str) -> Option<(&WebSocketRoute, AHashMap<String, String>)> {
        // O(1) static route lookup first
        if let Some(route) = self.static_routes.get(path) {
            return Some((route, AHashMap::new()));
        }

        // Radix tree lookup only if we have dynamic routes
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

    #[allow(dead_code)]
    pub fn is_empty(&self) -> bool {
        self.static_routes.is_empty() && !self.has_dynamic_routes
    }

    /// Get all registered WebSocket paths for Actix route registration
    pub fn get_all_paths(&self) -> Vec<String> {
        let mut paths: Vec<String> = self.static_routes.keys().cloned().collect();
        paths.extend(self.dynamic_paths.iter().cloned());
        paths
    }
}

/// Check if a request is a WebSocket upgrade request
#[inline]
pub fn is_websocket_upgrade(req: &HttpRequest) -> bool {
    let has_upgrade_connection = req
        .headers()
        .get("connection")
        .and_then(|v| v.to_str().ok())
        .map(|v| v.to_lowercase().contains("upgrade"))
        .unwrap_or(false);

    if !has_upgrade_connection {
        return false;
    }

    req.headers()
        .get("upgrade")
        .and_then(|v| v.to_str().ok())
        .map(|v| v.eq_ignore_ascii_case("websocket"))
        .unwrap_or(false)
}

/// Build scope dict for Python WebSocket handler
fn build_scope(
    py: Python<'_>,
    req: &HttpRequest,
    path_params: &AHashMap<String, String>,
) -> PyResult<Py<PyAny>> {
    let scope_dict = PyDict::new(py);
    scope_dict.set_item("type", "websocket")?;
    scope_dict.set_item("path", req.path())?;
    scope_dict.set_item("query_string", req.query_string().as_bytes())?;

    // Add headers as dict (FastAPI style)
    let headers_dict = PyDict::new(py);
    for (key, value) in req.headers().iter() {
        if let Ok(v) = value.to_str() {
            headers_dict.set_item(key.as_str().to_lowercase(), v)?;
        }
    }
    scope_dict.set_item("headers", headers_dict)?;

    // Add path params
    let params_dict = PyDict::new(py);
    for (k, v) in path_params.iter() {
        params_dict.set_item(k.as_str(), v.as_str())?;
    }
    scope_dict.set_item("path_params", params_dict)?;

    // Add cookies
    let cookies_dict = PyDict::new(py);
    if let Some(cookie_header) = req.headers().get("cookie") {
        if let Ok(cookie_str) = cookie_header.to_str() {
            for pair in cookie_str.split(';') {
                let pair = pair.trim();
                if let Some(eq_pos) = pair.find('=') {
                    let key = &pair[..eq_pos];
                    let value = &pair[eq_pos + 1..];
                    cookies_dict.set_item(key, value)?;
                }
            }
        }
    }
    scope_dict.set_item("cookies", cookies_dict)?;

    // Add client info
    if let Some(peer) = req.peer_addr() {
        let client = PyTuple::new(py, &[peer.ip().to_string(), peer.port().to_string()])?;
        scope_dict.set_item("client", client)?;
    }

    Ok(scope_dict.into())
}

/// Shared state for WebSocket connection - passed to Python receive/send functions
struct WsConnectionState {
    /// Channel to receive messages from Actix actor
    from_actor_rx: tokio::sync::Mutex<mpsc::Receiver<WsMessage>>,
    /// Actor address to send messages to client
    actor_addr: Addr<WebSocketActor>,
}

/// Create Python receive function that reads from channel
fn create_receive_fn(py: Python<'_>, state: Arc<WsConnectionState>) -> PyResult<Py<PyAny>> {
    // Wrap in a Python callable
    #[pyclass]
    struct ReceiveFn {
        state: Arc<WsConnectionState>,
    }

    #[pymethods]
    impl ReceiveFn {
        fn __call__(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
            let state = self.state.clone();
            let future = pyo3_async_runtimes::tokio::future_into_py(py, async move {
                let mut rx = state.from_actor_rx.lock().await;
                match rx.recv().await {
                    Some(WsMessage::Text(text)) => Python::attach(|py| {
                        let dict = PyDict::new(py);
                        dict.set_item("type", "websocket.receive")?;
                        dict.set_item("text", text)?;
                        Ok(dict.unbind())
                    }),
                    Some(WsMessage::Binary(data)) => Python::attach(|py| {
                        let dict = PyDict::new(py);
                        dict.set_item("type", "websocket.receive")?;
                        dict.set_item("bytes", pyo3::types::PyBytes::new(py, &data))?;
                        Ok(dict.unbind())
                    }),
                    Some(WsMessage::Disconnect { code }) => Python::attach(|py| {
                        let dict = PyDict::new(py);
                        dict.set_item("type", "websocket.disconnect")?;
                        dict.set_item("code", code)?;
                        Ok(dict.unbind())
                    }),
                    None => Python::attach(|py| {
                        let dict = PyDict::new(py);
                        dict.set_item("type", "websocket.disconnect")?;
                        dict.set_item("code", 1000)?;
                        Ok(dict.unbind())
                    }),
                    _ => Python::attach(|py| {
                        let dict = PyDict::new(py);
                        dict.set_item("type", "websocket.receive")?;
                        Ok(dict.unbind())
                    }),
                }
            })?;
            Ok(future.into())
        }
    }

    let receive_fn = ReceiveFn { state };
    Ok(Py::new(py, receive_fn)?.into_any().into())
}

/// Create Python send function that sends to actor
fn create_send_fn(py: Python<'_>, state: Arc<WsConnectionState>) -> PyResult<Py<PyAny>> {
    #[pyclass]
    struct SendFn {
        state: Arc<WsConnectionState>,
    }

    #[pymethods]
    impl SendFn {
        fn __call__(&self, py: Python<'_>, message: &Bound<'_, PyDict>) -> PyResult<Py<PyAny>> {
            let msg_type: String = message
                .get_item("type")?
                .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("Missing 'type' key"))?
                .extract()?;

            let state = self.state.clone();

            match msg_type.as_str() {
                "websocket.accept" => {
                    let subprotocol: Option<String> = message
                        .get_item("subprotocol")?
                        .map(|v| v.extract())
                        .transpose()?;
                    let state = state.clone();
                    let future = pyo3_async_runtimes::tokio::future_into_py(py, async move {
                        state
                            .actor_addr
                            .send(SendToClient(WsMessage::Accept { subprotocol }))
                            .await
                            .map_err(|e| {
                                pyo3::exceptions::PyRuntimeError::new_err(format!(
                                    "Failed to send accept: {}",
                                    e
                                ))
                            })?;
                        Ok(Python::attach(|py| py.None().into_pyobject(py).unwrap().unbind()))
                    })?;
                    Ok(future.into())
                }
                "websocket.send" => {
                    if let Some(text) = message.get_item("text")? {
                        let text: String = text.extract()?;
                        let state = state.clone();
                        let future = pyo3_async_runtimes::tokio::future_into_py(py, async move {
                            state
                                .actor_addr
                                .send(SendToClient(WsMessage::SendText(text)))
                                .await
                                .map_err(|e| {
                                    pyo3::exceptions::PyRuntimeError::new_err(format!(
                                        "Failed to send text: {}",
                                        e
                                    ))
                                })?;
                            Ok(Python::attach(|py| py.None().into_pyobject(py).unwrap().unbind()))
                        })?;
                        Ok(future.into())
                    } else if let Some(bytes) = message.get_item("bytes")? {
                        let data: Vec<u8> = bytes.extract()?;
                        let state = state.clone();
                        let future = pyo3_async_runtimes::tokio::future_into_py(py, async move {
                            state
                                .actor_addr
                                .send(SendToClient(WsMessage::SendBinary(data)))
                                .await
                                .map_err(|e| {
                                    pyo3::exceptions::PyRuntimeError::new_err(format!(
                                        "Failed to send binary: {}",
                                        e
                                    ))
                                })?;
                            Ok(Python::attach(|py| py.None().into_pyobject(py).unwrap().unbind()))
                        })?;
                        Ok(future.into())
                    } else {
                        Err(pyo3::exceptions::PyValueError::new_err(
                            "websocket.send requires 'text' or 'bytes'",
                        ))
                    }
                }
                "websocket.close" => {
                    let code: u16 = message
                        .get_item("code")?
                        .map(|v| v.extract())
                        .transpose()?
                        .unwrap_or(1000);
                    let reason: String = message
                        .get_item("reason")?
                        .map(|v| v.extract())
                        .transpose()?
                        .unwrap_or_default();
                    let state = state.clone();
                    let future = pyo3_async_runtimes::tokio::future_into_py(py, async move {
                        state
                            .actor_addr
                            .send(SendToClient(WsMessage::Close { code, reason }))
                            .await
                            .map_err(|e| {
                                pyo3::exceptions::PyRuntimeError::new_err(format!(
                                    "Failed to send close: {}",
                                    e
                                ))
                            })?;
                        Ok(Python::attach(|py| py.None().into_pyobject(py).unwrap().unbind()))
                    })?;
                    Ok(future.into())
                }
                _ => Err(pyo3::exceptions::PyValueError::new_err(format!(
                    "Unknown message type: {}",
                    msg_type
                ))),
            }
        }
    }

    let send_fn = SendFn { state };
    Ok(Py::new(py, send_fn)?.into_any().into())
}

/// HTTP handler for WebSocket upgrade requests
pub async fn handle_websocket_upgrade(
    req: HttpRequest,
    stream: web::Payload,
    handler: Py<PyAny>,
    _handler_id: usize,
    path_params: AHashMap<String, String>,
) -> actix_web::Result<HttpResponse> {
    // Create channel for messages from Actix to Python (client messages)
    let (to_python_tx, to_python_rx) = mpsc::channel::<WsMessage>(100);

    // Start WebSocket actor and get its address
    let actor = WebSocketActor::new(to_python_tx);

    // Start the actor with the WebSocket stream
    let resp = ws::start(actor, &req, stream)?;

    // We need to get the actor address to send messages to it
    // Unfortunately, ws::start doesn't return the address directly
    // We need a different approach - use ws::WsResponseBuilder

    Ok(resp)
}

/// Validate WebSocket origin header against allowed origins
fn validate_origin(req: &HttpRequest) -> bool {
    let allowed_origins = get_allowed_origins();

    // If no allowed origins configured, allow all (backward compatibility)
    let allowed = match allowed_origins {
        None => return true,
        Some(origins) => origins,
    };

    // Get origin header from request
    let origin = match req.headers().get("origin") {
        Some(v) => match v.to_str() {
            Ok(s) => s,
            Err(_) => return false,
        },
        None => {
            // No origin header - allow for same-origin requests
            // (browsers don't send Origin for same-origin WebSocket)
            return true;
        }
    };

    // Check if origin is in allowed list
    allowed.iter().any(|allowed_origin| {
        if allowed_origin == "*" {
            true
        } else {
            origin == allowed_origin || origin.starts_with(&format!("{}:", allowed_origin))
        }
    })
}

/// HTTP handler for WebSocket upgrade with full Python integration
pub async fn handle_websocket_upgrade_with_handler(
    req: HttpRequest,
    stream: web::Payload,
    handler: Py<PyAny>,
    handler_id: usize,
    path_params: AHashMap<String, String>,
) -> actix_web::Result<HttpResponse> {
    // Validate request is actually a WebSocket upgrade
    if !is_websocket_upgrade(&req) {
        return Ok(HttpResponse::BadRequest().body("Expected WebSocket upgrade request"));
    }

    // Validate origin header (CORS-like protection for WebSocket)
    if !validate_origin(&req) {
        return Ok(HttpResponse::Forbidden()
            .content_type("application/json")
            .body(r#"{"detail":"Origin not allowed"}"#));
    }

    // Extract headers for auth/guard evaluation
    let mut headers: AHashMap<String, String> = AHashMap::new();
    for (key, value) in req.headers().iter() {
        if let Ok(v) = value.to_str() {
            headers.insert(key.as_str().to_lowercase(), v.to_string());
        }
    }

    // Evaluate authentication and guards before upgrading
    if let Some(route_metadata) = ROUTE_METADATA.get() {
        if let Some(route_meta) = route_metadata.get(&handler_id) {
            match validate_auth_and_guards(&headers, &route_meta.auth_backends, &route_meta.guards) {
                AuthGuardResult::Allow(_ctx) => {
                    // Guards passed, continue with WebSocket upgrade
                }
                AuthGuardResult::Unauthorized => {
                    return Ok(HttpResponse::Unauthorized()
                        .content_type("application/json")
                        .body(r#"{"detail":"Authentication required"}"#));
                }
                AuthGuardResult::Forbidden => {
                    return Ok(HttpResponse::Forbidden()
                        .content_type("application/json")
                        .body(r#"{"detail":"Permission denied"}"#));
                }
            }
        }
    }

    // Create channels for bidirectional communication (configurable size)
    let channel_size = get_channel_buffer_size();
    let (to_python_tx, to_python_rx) = mpsc::channel::<WsMessage>(channel_size);

    // Build scope for Python
    let scope = Python::attach(|py| build_scope(py, &req, &path_params))
        .map_err(|e| actix_web::error::ErrorBadRequest(format!("Invalid request: {}", e)))?;

    // Start the WebSocket actor
    let actor = WebSocketActor::new(to_python_tx);

    // Use WsResponseBuilder to start actor and get address
    let (addr, resp) = ws::WsResponseBuilder::new(actor, &req, stream)
        .frame_size(MAX_MESSAGE_SIZE)
        .start_with_addr()
        .map_err(|e| actix_web::error::ErrorInternalServerError(format!("WebSocket error: {}", e)))?;

    // Create shared state for Python functions
    let state = Arc::new(WsConnectionState {
        from_actor_rx: tokio::sync::Mutex::new(to_python_rx),
        actor_addr: addr.clone(),
    });

    // Spawn task to run Python handler using proper async integration
    let state_clone = state.clone();
    actix_web::rt::spawn(async move {
        // Create WebSocket instance and get the coroutine
        let future_result = Python::attach(|py| -> PyResult<_> {
            // Import the WebSocket class
            let ws_module = py.import("django_bolt.websocket")?;
            let ws_class = ws_module.getattr("WebSocket")?;

            // Create receive and send functions
            let receive_fn = create_receive_fn(py, state_clone.clone())?;
            let send_fn = create_send_fn(py, state_clone.clone())?;

            // Create WebSocket instance
            let websocket = ws_class.call1((scope, receive_fn, send_fn))?;

            // Call the handler with the WebSocket instance
            let coro = handler.call1(py, (websocket,))?;

            // Convert Python coroutine to Rust future using pyo3_async_runtimes
            pyo3_async_runtimes::tokio::into_future(coro.bind(py).clone())
        });

        match future_result {
            Ok(future) => {
                if let Err(e) = future.await {
                    eprintln!("[django-bolt] WebSocket handler error: {}", e);
                    // Close the connection on error
                    let _ = addr.send(SendToClient(WsMessage::Close {
                        code: 1011,
                        reason: "Internal error".to_string(),
                    })).await;
                }
            }
            Err(e) => {
                eprintln!("[django-bolt] WebSocket handler setup error: {}", e);
                let _ = addr.send(SendToClient(WsMessage::Close {
                    code: 1011,
                    reason: "Handler setup failed".to_string(),
                })).await;
            }
        }
    });

    Ok(resp)
}

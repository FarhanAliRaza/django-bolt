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
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::mpsc;

use crate::metadata::CorsConfig;
use crate::middleware::rate_limit::check_rate_limit;
use crate::state::{AppState, ROUTE_METADATA, TASK_LOCALS};
use crate::validation::{validate_auth_and_guards, AuthGuardResult};

/// Global counter for active WebSocket connections
pub static ACTIVE_WS_CONNECTIONS: AtomicUsize = AtomicUsize::new(0);

/// Get maximum allowed WebSocket connections from settings
fn get_max_connections() -> usize {
    // 1. Check environment variable
    if let Ok(val) = std::env::var("DJANGO_BOLT_WS_MAX_CONNECTIONS") {
        if let Ok(max) = val.parse::<usize>() {
            return max;
        }
    }

    // 2. Check Django settings
    Python::attach(|py| {
        if let Ok(django_conf) = py.import("django.conf") {
            if let Ok(settings) = django_conf.getattr("settings") {
                if let Ok(max) = settings.getattr("BOLT_WS_MAX_CONNECTIONS") {
                    if let Ok(val) = max.extract::<usize>() {
                        return val;
                    }
                }
            }
        }
        10000 // Default: 10k connections
    })
}

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

        // Decrement active connection counter
        ACTIVE_WS_CONNECTIONS.fetch_sub(1, Ordering::Relaxed);
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

/// Validate WebSocket origin header against CORS allowed origins
/// Uses the same CORS configuration as HTTP requests (like FastAPI)
///
/// Security behavior:
/// - If CORS is configured with allow_all_origins=true: allow all origins
/// - If CORS is configured with specific origins: only allow those origins
/// - If NO CORS is configured: DENY all cross-origin requests (fail-secure)
/// - Same-origin requests (no Origin header) are always allowed
fn validate_origin(req: &HttpRequest, state: &AppState) -> bool {
    // Get origin header from request
    let origin = match req.headers().get("origin") {
        Some(v) => match v.to_str() {
            Ok(s) => s,
            Err(_) => {
                eprintln!("[django-bolt] WebSocket: Invalid Origin header encoding");
                return false;
            }
        },
        None => {
            // No origin header - allow for same-origin requests
            // (browsers don't send Origin for same-origin WebSocket connections)
            return true;
        }
    };

    // Check global CORS config (same as HTTP)
    if let Some(ref cors_config) = state.global_cors_config {
        return is_origin_allowed(origin, cors_config, &state.cors_origin_regexes);
    }

    // SECURITY: No CORS configured = deny all cross-origin requests
    // This is a fail-secure default (unlike the old allow-all default)
    eprintln!(
        "[django-bolt] WebSocket: Rejecting cross-origin request from '{}' - no CORS configured. \
        Set CORS_ALLOWED_ORIGINS in Django settings to allow WebSocket connections.",
        origin
    );
    false
}

/// Check if an origin is allowed by the CORS configuration
/// Reuses the same logic as HTTP CORS validation
fn is_origin_allowed(origin: &str, cors_config: &CorsConfig, global_regexes: &[regex::Regex]) -> bool {
    // Allow all origins if configured
    if cors_config.allow_all_origins {
        return true;
    }

    // O(1) exact match using HashSet
    if cors_config.origin_set.contains(origin) {
        return true;
    }

    // Check route-level regex patterns
    if cors_config
        .compiled_origin_regexes
        .iter()
        .any(|re| re.is_match(origin))
    {
        return true;
    }

    // Check global regex patterns
    if global_regexes.iter().any(|re| re.is_match(origin)) {
        return true;
    }

    false
}

/// HTTP handler for WebSocket upgrade with full Python integration
pub async fn handle_websocket_upgrade_with_handler(
    req: HttpRequest,
    stream: web::Payload,
    handler: Py<PyAny>,
    handler_id: usize,
    path_params: AHashMap<String, String>,
    state: Arc<AppState>,
) -> actix_web::Result<HttpResponse> {
    // Validate request is actually a WebSocket upgrade
    if !is_websocket_upgrade(&req) {
        return Ok(HttpResponse::BadRequest().body("Expected WebSocket upgrade request"));
    }

    // Check connection limit FIRST (before any processing)
    let max_connections = get_max_connections();
    let current_connections = ACTIVE_WS_CONNECTIONS.load(Ordering::Relaxed);
    if current_connections >= max_connections {
        eprintln!(
            "[django-bolt] WebSocket: Connection limit reached ({}/{})",
            current_connections, max_connections
        );
        return Ok(HttpResponse::ServiceUnavailable()
            .content_type("application/json")
            .body(r#"{"detail":"Too many WebSocket connections"}"#));
    }

    // Extract headers for rate limiting and auth
    let mut headers: AHashMap<String, String> = AHashMap::new();
    for (key, value) in req.headers().iter() {
        if let Ok(v) = value.to_str() {
            headers.insert(key.as_str().to_lowercase(), v.to_string());
        }
    }

    // Get peer address for rate limiting
    let peer_addr = req.peer_addr().map(|addr| addr.ip().to_string());

    // Check rate limiting BEFORE origin validation (reuse HTTP rate limit)
    if let Some(route_metadata) = ROUTE_METADATA.get() {
        if let Some(route_meta) = route_metadata.get(&handler_id) {
            if let Some(ref rate_config) = route_meta.rate_limit_config {
                if let Some(response) = check_rate_limit(
                    handler_id,
                    &headers,
                    peer_addr.as_deref(),
                    rate_config,
                ) {
                    return Ok(response);
                }
            }
        }
    }

    // Validate origin header (CORS-like protection for WebSocket)
    // Uses same CORS config as HTTP requests
    if !validate_origin(&req, &state) {
        return Ok(HttpResponse::Forbidden()
            .content_type("application/json")
            .body(r#"{"detail":"Origin not allowed"}"#));
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

    // Increment connection counter (will be decremented when actor stops)
    ACTIVE_WS_CONNECTIONS.fetch_add(1, Ordering::Relaxed);

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

            // Reuse the global event loop locals initialized at server startup (same as HTTP handlers)
            let locals = TASK_LOCALS.get().ok_or_else(|| {
                pyo3::exceptions::PyRuntimeError::new_err("Asyncio loop not initialized")
            })?;

            // Convert Python coroutine to Rust future using the shared event loop
            pyo3_async_runtimes::into_future_with_locals(locals, coro.bind(py).clone())
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

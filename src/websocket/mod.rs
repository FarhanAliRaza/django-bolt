//! WebSocket support for Django-Bolt
//!
//! This module provides WebSocket support with proper Python handler integration.
//! Uses tokio channels to bridge Actix's actor-based WebSocket with Python's
//! ASGI-style async interface.
//!
//! ## Module Structure
//!
//! - `config` - Cached configuration (read once at startup)
//! - `messages` - Message types for actor/Python communication
//! - `actor` - Actix WebSocket actor implementation
//! - `router` - WebSocket route matching
//! - `handler` - HTTP upgrade handler

mod actor;
mod config;
mod handler;
mod messages;
mod router;

use std::sync::atomic::AtomicUsize;

// Re-export public API
#[allow(unused_imports)] // Re-exported for external use
pub use actor::WebSocketActor;
#[allow(unused_imports)] // Re-exported for external use
pub use config::WS_CONFIG;
pub use handler::{handle_websocket_upgrade_with_handler, is_websocket_upgrade};
#[allow(unused_imports)] // Re-exported for external use
pub use messages::{SendToClient, WsMessage};
pub use router::WebSocketRouter;
#[allow(unused_imports)] // Re-exported for external use
pub use router::WebSocketRoute;

/// Global counter for active WebSocket connections
pub static ACTIVE_WS_CONNECTIONS: AtomicUsize = AtomicUsize::new(0);

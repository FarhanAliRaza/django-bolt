"""WebSocket-specific exceptions."""

from __future__ import annotations

from .close_codes import CloseCode


class WebSocketException(Exception):
    """Base exception for WebSocket errors."""

    def __init__(self, code: int = CloseCode.INTERNAL_ERROR, reason: str = "") -> None:
        self.code = code
        self.reason = reason
        super().__init__(f"WebSocket error {code}: {reason}")


class WebSocketDisconnect(WebSocketException):
    """Raised when a WebSocket connection is closed."""

    def __init__(self, code: int = CloseCode.NORMAL, reason: str = "") -> None:
        super().__init__(code, reason)


class WebSocketClose(WebSocketException):
    """Raised to intentionally close a WebSocket connection."""

    def __init__(self, code: int = CloseCode.NORMAL, reason: str = "") -> None:
        super().__init__(code, reason)

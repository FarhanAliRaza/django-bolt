"""WebSocket testing utilities for django-bolt.

Provides test client for WebSocket endpoints without subprocess/network overhead.
Uses mock ASGI interface to call handlers directly.

Usage:
    api = BoltAPI()

    @api.websocket("/ws/echo")
    async def echo(websocket: WebSocket):
        await websocket.accept()
        async for msg in websocket.iter_text():
            await websocket.send_text(f"Echo: {msg}")

    async with WebSocketTestClient(api, "/ws/echo") as ws:
        await ws.send_text("hello")
        response = await ws.receive_text()
        assert response == "Echo: hello"
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncIterator, Callable, Optional
from collections import deque

from django_bolt import BoltAPI
from django_bolt.websocket import WebSocket, WebSocketState, CloseCode
from django_bolt.websocket.handlers import get_websocket_param_name


class WebSocketTestClient:
    """Async WebSocket test client for django-bolt.

    This client simulates a WebSocket connection by calling the handler
    directly with mock receive/send functions. No actual network connection
    is made.

    Usage:
        async with WebSocketTestClient(api, "/ws/echo") as ws:
            await ws.send_text("hello")
            response = await ws.receive_text()
    """

    __test__ = False  # Tell pytest this is not a test class

    def __init__(
        self,
        api: BoltAPI,
        path: str,
        headers: dict[str, str] | None = None,
        query_string: str = "",
        subprotocols: list[str] | None = None,
    ):
        """Initialize WebSocket test client.

        Args:
            api: BoltAPI instance with WebSocket routes
            path: WebSocket endpoint path (e.g., "/ws/echo")
            headers: Optional request headers
            query_string: Optional query string (without ?)
            subprotocols: Optional list of subprotocols to request
        """
        self.api = api
        self.path = path
        self.headers = headers or {}
        self.query_string = query_string
        self.subprotocols = subprotocols or []

        # Message queues for bidirectional communication
        self._client_to_server: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._server_to_client: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

        # Connection state
        self._accepted = False
        self._closed = False
        self._close_code: int | None = None
        self._accepted_subprotocol: str | None = None
        self._handler_task: asyncio.Task | None = None
        self._handler_exception: Exception | None = None

    def _find_handler(self) -> tuple[Callable, dict[str, str]] | None:
        """Find the WebSocket handler for the path."""
        for route_path, handler_id, handler in self.api._websocket_routes:
            # Simple path matching (exact or with path params)
            path_params = self._match_path(route_path, self.path)
            if path_params is not None:
                return handler, path_params
        return None

    def _match_path(self, pattern: str, path: str) -> dict[str, str] | None:
        """Match a path pattern against an actual path.

        Args:
            pattern: Route pattern like "/ws/chat/{room_id}"
            path: Actual path like "/ws/chat/general"

        Returns:
            Dict of path params if matched, None otherwise
        """
        pattern_parts = pattern.strip("/").split("/")
        path_parts = path.strip("/").split("/")

        if len(pattern_parts) != len(path_parts):
            return None

        params = {}
        for pattern_part, path_part in zip(pattern_parts, path_parts):
            if pattern_part.startswith("{") and pattern_part.endswith("}"):
                param_name = pattern_part[1:-1]
                params[param_name] = path_part
            elif pattern_part != path_part:
                return None

        return params

    def _build_scope(self, path_params: dict[str, str]) -> dict[str, Any]:
        """Build ASGI-style scope for WebSocket."""
        # Convert headers to ASGI format
        headers_dict = {k.lower(): v for k, v in self.headers.items()}

        return {
            "type": "websocket",
            "path": self.path,
            "query_string": self.query_string.encode("utf-8"),
            "headers": headers_dict,
            "path_params": path_params,
            "cookies": self._parse_cookies(headers_dict.get("cookie", "")),
            "client": ("127.0.0.1", 12345),  # Mock client address
            "subprotocols": self.subprotocols,
        }

    def _parse_cookies(self, cookie_header: str) -> dict[str, str]:
        """Parse cookie header into dict."""
        cookies = {}
        if cookie_header:
            for pair in cookie_header.split(";"):
                pair = pair.strip()
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    cookies[key.strip()] = value.strip()
        return cookies

    async def _receive(self) -> dict[str, Any]:
        """ASGI receive callable - gets messages from client queue."""
        return await self._client_to_server.get()

    async def _send(self, message: dict[str, Any]) -> None:
        """ASGI send callable - puts messages to server queue."""
        msg_type = message.get("type", "")

        if msg_type == "websocket.accept":
            self._accepted = True
            self._accepted_subprotocol = message.get("subprotocol")

        elif msg_type == "websocket.close":
            self._closed = True
            self._close_code = message.get("code", CloseCode.NORMAL)

        # Put all messages in queue for client to receive
        await self._server_to_client.put(message)

    async def __aenter__(self) -> "WebSocketTestClient":
        """Enter async context - start the WebSocket handler."""
        result = self._find_handler()
        if result is None:
            raise ValueError(f"No WebSocket handler found for path: {self.path}")

        handler, path_params = result
        scope = self._build_scope(path_params)

        # Create WebSocket instance
        ws = WebSocket(scope, self._receive, self._send)

        # Get the parameter name for the WebSocket argument
        ws_param_name = get_websocket_param_name(handler)

        # Build kwargs for the handler
        kwargs = {ws_param_name: ws}

        # Add path params as kwargs
        import inspect
        sig = inspect.signature(handler)
        for name, value in path_params.items():
            if name in sig.parameters and name != ws_param_name:
                # Type coerce if needed
                param = sig.parameters[name]
                if param.annotation != inspect.Parameter.empty:
                    try:
                        if param.annotation == int:
                            value = int(value)
                        elif param.annotation == float:
                            value = float(value)
                        elif param.annotation == bool:
                            value = value.lower() in ("true", "1", "yes")
                    except (ValueError, TypeError):
                        pass  # Keep as string if conversion fails
                kwargs[name] = value

        # Start handler in background task
        async def run_handler():
            try:
                await handler(**kwargs)
            except Exception as e:
                self._handler_exception = e
                # Send disconnect on error
                if not self._closed:
                    await self._server_to_client.put({
                        "type": "websocket.close",
                        "code": CloseCode.INTERNAL_ERROR,
                    })
                    self._closed = True
                    self._close_code = CloseCode.INTERNAL_ERROR

        self._handler_task = asyncio.create_task(run_handler())

        # Give handler a chance to start
        await asyncio.sleep(0)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context - close connection and cleanup."""
        if not self._closed:
            # Send disconnect to handler
            await self._client_to_server.put({
                "type": "websocket.disconnect",
                "code": CloseCode.NORMAL,
            })
            self._closed = True

        # Cancel handler task if still running
        if self._handler_task and not self._handler_task.done():
            self._handler_task.cancel()
            try:
                await self._handler_task
            except asyncio.CancelledError:
                pass

        # Re-raise handler exception if any
        if self._handler_exception and exc_type is None:
            raise self._handler_exception

    @property
    def accepted(self) -> bool:
        """Whether the connection has been accepted."""
        return self._accepted

    @property
    def closed(self) -> bool:
        """Whether the connection has been closed."""
        return self._closed

    @property
    def close_code(self) -> int | None:
        """Close code if connection was closed."""
        return self._close_code

    @property
    def accepted_subprotocol(self) -> str | None:
        """Subprotocol accepted by server."""
        return self._accepted_subprotocol

    async def send_text(self, data: str) -> None:
        """Send a text message to the server."""
        if self._closed:
            raise RuntimeError("WebSocket is closed")
        await self._client_to_server.put({
            "type": "websocket.receive",
            "text": data,
        })
        # Give handler time to process
        await asyncio.sleep(0)

    async def send_bytes(self, data: bytes) -> None:
        """Send a binary message to the server."""
        if self._closed:
            raise RuntimeError("WebSocket is closed")
        await self._client_to_server.put({
            "type": "websocket.receive",
            "bytes": data,
        })
        await asyncio.sleep(0)

    async def send_json(self, data: Any, mode: str = "text") -> None:
        """Send JSON data to the server."""
        text = json.dumps(data, separators=(",", ":"))
        if mode == "text":
            await self.send_text(text)
        else:
            await self.send_bytes(text.encode("utf-8"))

    async def receive(self, timeout: float = 5.0) -> dict[str, Any]:
        """Receive a raw message from the server."""
        try:
            return await asyncio.wait_for(
                self._server_to_client.get(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"No message received within {timeout}s")

    async def receive_text(self, timeout: float = 5.0) -> str:
        """Receive a text message from the server."""
        while True:
            msg = await self.receive(timeout=timeout)
            msg_type = msg.get("type", "")

            if msg_type == "websocket.send":
                if "text" in msg:
                    return msg["text"]
                elif "bytes" in msg:
                    return msg["bytes"].decode("utf-8")
            elif msg_type == "websocket.close":
                self._closed = True
                self._close_code = msg.get("code", CloseCode.NORMAL)
                raise ConnectionClosed(self._close_code)
            elif msg_type == "websocket.accept":
                # Skip accept messages
                continue
            else:
                # Unknown message type, skip
                continue

    async def receive_bytes(self, timeout: float = 5.0) -> bytes:
        """Receive a binary message from the server."""
        while True:
            msg = await self.receive(timeout=timeout)
            msg_type = msg.get("type", "")

            if msg_type == "websocket.send":
                if "bytes" in msg:
                    return msg["bytes"]
                elif "text" in msg:
                    return msg["text"].encode("utf-8")
            elif msg_type == "websocket.close":
                self._closed = True
                self._close_code = msg.get("code", CloseCode.NORMAL)
                raise ConnectionClosed(self._close_code)
            elif msg_type == "websocket.accept":
                continue
            else:
                continue

    async def receive_json(self, timeout: float = 5.0, mode: str = "text") -> Any:
        """Receive and parse JSON from the server."""
        if mode == "text":
            data = await self.receive_text(timeout=timeout)
        else:
            data = await self.receive_bytes(timeout=timeout)
            data = data.decode("utf-8")
        return json.loads(data)

    async def close(self, code: int = CloseCode.NORMAL) -> None:
        """Close the WebSocket connection."""
        if not self._closed:
            await self._client_to_server.put({
                "type": "websocket.disconnect",
                "code": code,
            })
            self._closed = True
            self._close_code = code

    async def iter_text(self, timeout: float = 5.0) -> AsyncIterator[str]:
        """Async iterator for text messages."""
        while not self._closed:
            try:
                yield await self.receive_text(timeout=timeout)
            except (ConnectionClosed, TimeoutError):
                break

    async def iter_bytes(self, timeout: float = 5.0) -> AsyncIterator[bytes]:
        """Async iterator for binary messages."""
        while not self._closed:
            try:
                yield await self.receive_bytes(timeout=timeout)
            except (ConnectionClosed, TimeoutError):
                break

    async def iter_json(self, timeout: float = 5.0) -> AsyncIterator[Any]:
        """Async iterator for JSON messages."""
        while not self._closed:
            try:
                yield await self.receive_json(timeout=timeout)
            except (ConnectionClosed, TimeoutError):
                break


class ConnectionClosed(Exception):
    """Raised when WebSocket connection is closed."""

    def __init__(self, code: int = CloseCode.NORMAL, reason: str = ""):
        self.code = code
        self.reason = reason
        super().__init__(f"WebSocket closed with code {code}: {reason}")


# For backwards compatibility and convenience
WebSocketClient = WebSocketTestClient

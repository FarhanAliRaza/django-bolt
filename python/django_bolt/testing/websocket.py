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
        auth_context: Any = None,
    ):
        """Initialize WebSocket test client.

        Args:
            api: BoltAPI instance with WebSocket routes
            path: WebSocket endpoint path (e.g., "/ws/echo")
            headers: Optional request headers
            query_string: Optional query string (without ?)
            subprotocols: Optional list of subprotocols to request
            auth_context: Optional authentication context for guard evaluation.
                         Should have user_id, is_superuser, is_staff, permissions attributes.
        """
        self.api = api
        self.path = path
        self.headers = headers or {}
        self.query_string = query_string
        self.subprotocols = subprotocols or []
        self.auth_context = auth_context

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

    def _find_handler(self) -> tuple[Callable, int, dict[str, str]] | None:
        """Find the WebSocket handler for the path.

        Returns:
            Tuple of (handler, handler_id, path_params) if found, None otherwise
        """
        for route_path, handler_id, handler in self.api._websocket_routes:
            # Simple path matching (exact or with path params)
            path_params = self._match_path(route_path, self.path)
            if path_params is not None:
                return handler, handler_id, path_params
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

        scope = {
            "type": "websocket",
            "path": self.path,
            "query_string": self.query_string.encode("utf-8"),
            "headers": headers_dict,
            "path_params": path_params,
            "cookies": self._parse_cookies(headers_dict.get("cookie", "")),
            "client": ("127.0.0.1", 12345),  # Mock client address
            "subprotocols": self.subprotocols,
        }

        # Add auth context if provided (for guard evaluation)
        if self.auth_context is not None:
            scope["auth_context"] = self.auth_context

        return scope

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

    def _evaluate_guards(self, handler_id: int, scope: dict[str, Any]) -> tuple[bool, int, str]:
        """Evaluate guards for WebSocket connection.

        Args:
            handler_id: Handler ID to look up guards
            scope: WebSocket scope with auth context

        Returns:
            Tuple of (allowed, status_code, message)
            - allowed: True if guards pass
            - status_code: HTTP status code if denied (401 or 403)
            - message: Error message if denied
        """
        # Get guards from handler middleware metadata
        middleware_meta = self.api._handler_middleware.get(handler_id)
        if not middleware_meta:
            return (True, 200, "")

        guards = middleware_meta.get("guards", [])
        if not guards:
            return (True, 200, "")

        # Build mock auth context from scope
        # In real usage, auth would be evaluated from headers/cookies
        auth_context = scope.get("auth_context")

        # Evaluate each guard
        for guard_meta in guards:
            guard_type = guard_meta.get("type", "")

            if guard_type == "allow_any":
                return (True, 200, "")

            if guard_type == "is_authenticated":
                if auth_context is None:
                    return (False, 401, "Authentication required")
                if not hasattr(auth_context, "user_id") or auth_context.user_id is None:
                    return (False, 401, "Authentication required")

            elif guard_type == "is_superuser":
                if auth_context is None:
                    return (False, 401, "Authentication required")
                if not getattr(auth_context, "is_superuser", False):
                    return (False, 403, "Superuser access required")

            elif guard_type == "is_staff":
                if auth_context is None:
                    return (False, 401, "Authentication required")
                if not getattr(auth_context, "is_staff", False):
                    return (False, 403, "Staff access required")

            elif guard_type == "has_permission":
                perm = guard_meta.get("permission", "")
                if auth_context is None:
                    return (False, 401, "Authentication required")
                permissions = getattr(auth_context, "permissions", set())
                if perm not in permissions:
                    return (False, 403, f"Permission '{perm}' required")

            elif guard_type == "has_any_permission":
                perms = guard_meta.get("permissions", [])
                if auth_context is None:
                    return (False, 401, "Authentication required")
                permissions = getattr(auth_context, "permissions", set())
                if not any(p in permissions for p in perms):
                    return (False, 403, "Required permission not found")

            elif guard_type == "has_all_permissions":
                perms = guard_meta.get("permissions", [])
                if auth_context is None:
                    return (False, 401, "Authentication required")
                permissions = getattr(auth_context, "permissions", set())
                if not all(p in permissions for p in perms):
                    return (False, 403, "Missing required permissions")

        return (True, 200, "")

    async def __aenter__(self) -> "WebSocketTestClient":
        """Enter async context - start the WebSocket handler."""
        result = self._find_handler()
        if result is None:
            raise ValueError(f"No WebSocket handler found for path: {self.path}")

        handler, handler_id, path_params = result
        scope = self._build_scope(path_params)

        # Evaluate guards before starting connection
        allowed, status_code, message = self._evaluate_guards(handler_id, scope)
        if not allowed:
            if status_code == 401:
                raise PermissionError(f"WebSocket connection denied: {message}")
            else:
                raise PermissionError(f"WebSocket connection forbidden: {message}")

        # Create WebSocket instance
        ws = WebSocket(scope, self._receive, self._send)

        # Get the parameter name for the WebSocket argument
        ws_param_name = get_websocket_param_name(handler)

        # Build kwargs for the handler
        kwargs = {ws_param_name: ws}

        # Add path params as kwargs with type coercion
        import inspect
        import typing
        import re
        sig = inspect.signature(handler)

        # Get resolved type hints (handles PEP 563 stringified annotations)
        try:
            type_hints = typing.get_type_hints(handler, include_extras=True)
        except Exception:
            type_hints = {}

        def parse_string_annotation(ann_str: str) -> Any:
            """Try to parse a string annotation to extract the base type.

            Handles patterns like:
            - "int" -> int
            - "Annotated[int, 'metadata']" -> int
            """
            ann_str = ann_str.strip()

            # Check for Annotated pattern
            annotated_match = re.match(r"Annotated\[([^,\]]+)", ann_str)
            if annotated_match:
                inner_type = annotated_match.group(1).strip()
                return inner_type

            return ann_str

        def get_base_type(annotation: Any) -> Any:
            """Extract base type from Annotated or return as-is."""
            # Handle string annotations (PEP 563)
            if isinstance(annotation, str):
                return parse_string_annotation(annotation)

            # Handle typing.Annotated[T, ...] -> T
            origin = typing.get_origin(annotation)

            # Check for Annotated (handle both typing and typing_extensions)
            try:
                from typing import Annotated as TypingAnnotated
            except ImportError:
                TypingAnnotated = None  # type: ignore

            try:
                from typing_extensions import Annotated as ExtAnnotated
            except ImportError:
                ExtAnnotated = None  # type: ignore

            is_annotated = (
                origin is not None and (
                    (TypingAnnotated is not None and origin is TypingAnnotated)
                    or (ExtAnnotated is not None and origin is ExtAnnotated)
                    or getattr(origin, "__name__", "") == "Annotated"
                )
            )

            if is_annotated:
                args = typing.get_args(annotation)
                if args:
                    return args[0]  # First arg is the actual type
            return annotation

        for name, value in path_params.items():
            if name in sig.parameters and name != ws_param_name:
                # Get annotation from resolved hints or fallback to signature
                annotation = type_hints.get(name) or sig.parameters[name].annotation

                # Type coerce if needed
                if annotation != inspect.Parameter.empty:
                    # Unwrap Annotated types
                    base_type = get_base_type(annotation)

                    try:
                        # Handle both actual types and string annotations
                        ann_name = getattr(base_type, "__name__", str(base_type))
                        if base_type is int or ann_name == "int":
                            value = int(value)
                        elif base_type is float or ann_name == "float":
                            value = float(value)
                        elif base_type is bool or ann_name == "bool":
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

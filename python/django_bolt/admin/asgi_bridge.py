"""
ASGI bridge for Django admin integration.

Converts django-bolt's PyRequest to ASGI scope and channels,
allowing Django's ASGI application (with full middleware stack)
to handle requests for admin routes.
"""

import asyncio
import logging
import traceback
from typing import Any
from urllib.parse import urlencode

from django.core.asgi import get_asgi_application

from ..bootstrap import ensure_django_ready

logger = logging.getLogger(__name__)


def actix_to_asgi_scope(request: dict[str, Any], server_host: str = "localhost", server_port: int = 8000) -> dict[str, Any]:
    """
    Convert django-bolt PyRequest dict to ASGI3 scope dict.

    Args:
        request: PyRequest dict with method, path, headers, body, etc.
        server_host: Server hostname (from settings or command args)
        server_port: Server port (from command args)

    Returns:
        ASGI3 scope dict compatible with Django's ASGI application
    """
    method = request.get("method", "GET")
    path = request.get("path", "/")
    query_params = request.get("query", {})

    # Django admin expects trailing slashes on URLs (it will redirect without them).
    # Since NormalizePath::trim() in Rust strips trailing slashes from incoming requests,
    # we need to restore the trailing slash for Django to avoid redirect loops.
    # Only add if path doesn't already end with / and is not just "/"
    if path != "/" and not path.endswith("/"):
        path = path + "/"
    headers_dict = request.get("headers", {})

    # Build query string from query params dict
    query_string = ""
    if query_params:
        # Convert dict to URL-encoded query string
        query_string = urlencode(sorted(query_params.items()))

    # Convert headers dict to ASGI headers format: [(b"name", b"value")]
    headers = []
    for name, value in headers_dict.items():
        # Headers are already lowercase from Rust
        headers.append((name.encode("latin1"), value.encode("latin1")))

    # Add host header if not present
    has_host = any(name == b"host" for name, _ in headers)
    if not has_host:
        headers.append((b"host", f"{server_host}:{server_port}".encode("latin1")))

    # Determine scheme (http/https) from headers
    scheme = "http"
    forwarded_proto = headers_dict.get("x-forwarded-proto", "")
    if forwarded_proto == "https":
        scheme = "https"

    # Get client address from headers or use placeholder
    client_host = headers_dict.get("x-forwarded-for", "127.0.0.1")
    if "," in client_host:
        client_host = client_host.split(",")[0].strip()
    client_port = 0  # Unknown client port

    # Build ASGI3 scope
    scope = {
        "type": "http",
        "asgi": {
            "version": "3.0",
            "spec_version": "2.3",
        },
        "http_version": "1.1",
        "method": method.upper(),
        "scheme": scheme,
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": query_string.encode("latin1"),
        "root_path": "",
        "headers": headers,
        "server": (server_host, server_port),
        "client": (client_host, client_port),
        "extensions": {},
    }

    return scope


def create_receive_callable(body: bytes):
    """
    Create ASGI3 receive callable that sends request body.

    Args:
        body: Request body bytes

    Returns:
        Async callable that implements ASGI receive channel
    """
    sent = False

    async def receive():
        nonlocal sent
        if not sent:
            sent = True
            return {
                "type": "http.request",
                "body": body,
                "more_body": False,
            }
        # After body is sent, wait forever (never disconnect)
        # This allows Django's ASGI handler to complete the response
        # Django uses asyncio.wait() with FIRST_COMPLETED, racing between
        # listen_for_disconnect() and process_request(). If we return
        # disconnect immediately, it aborts the request.
        await asyncio.Event().wait()  # Wait forever
        return {"type": "http.disconnect"}

    return receive


def create_send_callable(response_holder: dict[str, Any]):
    """
    Create ASGI3 send callable that collects response.

    Args:
        response_holder: Dict to populate with status, headers, body

    Returns:
        Async callable that implements ASGI send channel
    """
    async def send(message: dict[str, Any]):
        msg_type = message.get("type")

        if msg_type == "http.response.start":
            # Collect status and headers
            response_holder["status"] = message.get("status", 200)

            # Convert headers from bytes tuples to string tuples
            headers = []
            for name, value in message.get("headers", []):
                if isinstance(name, bytes):
                    name = name.decode("latin1")
                if isinstance(value, bytes):
                    value = value.decode("latin1")
                headers.append((name, value))

            response_holder["headers"] = headers

        elif msg_type == "http.response.body":
            # Collect body (may be sent in chunks)
            body_chunk = message.get("body", b"")

            if isinstance(body_chunk, memoryview):
                body_chunk = body_chunk.tobytes()
            elif isinstance(body_chunk, bytearray):
                body_chunk = bytes(body_chunk)

            if (not body_chunk) and "text" in message:
                text_chunk = message.get("text", "")
                if text_chunk:
                    body_chunk = text_chunk.encode("utf-8")

            if "body" not in response_holder:
                response_holder["body"] = body_chunk
            else:
                response_holder["body"] += body_chunk

            # Check if more body is coming
            more_body = message.get("more_body", False)
            response_holder["more_body"] = more_body

    return send


class ASGIFallbackHandler:
    """
    Handler that bridges django-bolt requests to Django's ASGI application.

    This allows Django admin and other Django views to work with django-bolt
    by converting the request format and applying Django's middleware stack.
    """

    def __init__(self, server_host: str = "localhost", server_port: int = 8000):
        """
        Initialize ASGI handler.

        Args:
            server_host: Server hostname for ASGI scope
            server_port: Server port for ASGI scope
        """
        self.server_host = server_host
        self.server_port = server_port
        self._asgi_app = None

    def _get_asgi_app(self):
        """Lazy-load Django ASGI application with middleware."""
        if self._asgi_app is None:
            # Ensure Django is configured
            ensure_django_ready()

            try:
                self._asgi_app = get_asgi_application()
            except Exception:
                raise

        return self._asgi_app

    async def handle_request(self, request: dict[str, Any]) -> tuple[int, list[tuple[str, str]], bytes]:
        """
        Handle request by converting to ASGI and calling Django app.

        Args:
            request: PyRequest dict from django-bolt

        Returns:
            Response tuple: (status_code, headers, body)
        """
        # Get Django ASGI app
        asgi_app = self._get_asgi_app()

        # Convert request to ASGI scope
        scope = actix_to_asgi_scope(request, self.server_host, self.server_port)

        # Create ASGI receive channel with request body
        body = request.get("body", b"")
        if isinstance(body, list):
            # Body is already bytes from PyRequest
            body = bytes(body)
        receive = create_receive_callable(body)

        # Create ASGI send channel to collect response
        response_holder = {
            "status": 200,
            "headers": [],
            "body": b"",
            "more_body": False,
        }
        send = create_send_callable(response_holder)

        # Call Django ASGI application
        try:
            await asgi_app(scope, receive, send)
        except Exception as e:
            # Handle errors by returning 500 response
            error_body = f"ASGI Handler Error: {str(e)}\n\n{traceback.format_exc()}"
            return (
                500,
                [("content-type", "text/plain; charset=utf-8")],
                error_body.encode("utf-8")
            )

        # Wait for response body if streaming
        # (In case more_body was True, though Django admin typically doesn't stream)
        max_wait = 100  # Max iterations to wait for body completion
        wait_count = 0
        while response_holder.get("more_body", False) and wait_count < max_wait:
            await asyncio.sleep(0.001)  # Small delay to allow body completion
            wait_count += 1

        # Extract response
        status = response_holder.get("status", 200)
        headers = response_holder.get("headers", [])
        body = response_holder.get("body", b"")

        return (status, headers, body)

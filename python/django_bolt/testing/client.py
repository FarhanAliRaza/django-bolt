"""Test clients for django-bolt using per-instance test state.

This version uses the test_state.rs infrastructure which provides:
- Per-instance routers (no global state conflicts)
- Per-instance event loops (proper async handling)
"""
from __future__ import annotations

from typing import Any

import httpx
from httpx import Response

from django_bolt import BoltAPI


class BoltTestTransport(httpx.BaseTransport):
    """HTTP transport that routes requests through django-bolt's per-instance test handler.

    Args:
        app_id: Test app instance ID
        raise_server_exceptions: If True, raise exceptions from handlers
        use_http_layer: If True, route through Actix HTTP layer (enables testing of
                        middleware like CORS, rate limiting, compression). If False (default),
                        use fast direct dispatch for unit tests.
    """

    def __init__(self, app_id: int, raise_server_exceptions: bool = True, use_http_layer: bool = False):
        self.app_id = app_id
        self.raise_server_exceptions = raise_server_exceptions
        self.use_http_layer = use_http_layer

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        """Handle a request by routing it through Rust."""
        from django_bolt import _core

        # Parse URL
        url = request.url
        path = url.path
        query_string = url.query.decode('utf-8') if url.query else None

        # Extract headers
        headers = [(k.decode('utf-8'), v.decode('utf-8')) for k, v in request.headers.raw]

        # Get body
        # Check if content has been read already
        if hasattr(request, "_content"):
            body_bytes = request.content
        else:
            # For streaming/multipart requests, need to read the content first
            try:
                # Try to read the request stream
                if hasattr(request.stream, 'read'):
                    body_bytes = request.stream.read()
                else:
                    # Fall back to iterating the stream
                    body_bytes = b''.join(request.stream)
            except Exception:
                # Last resort: try to get content directly
                body_bytes = request.content if hasattr(request, "_content") else b''

        # Get method
        method = request.method

        try:
            # Choose handler based on mode
            if self.use_http_layer:
                # Route through Actix HTTP layer (for middleware testing)
                status_code, resp_headers, resp_body = _core.handle_actix_http_request(
                    app_id=self.app_id,
                    method=method,
                    path=path,
                    headers=headers,
                    body=body_bytes,
                    query_string=query_string,
                )
            else:
                # Fast direct dispatch (for unit tests)
                status_code, resp_headers, resp_body = _core.handle_test_request_for(
                    app_id=self.app_id,
                    method=method,
                    path=path,
                    headers=headers,
                    body=body_bytes,
                    query_string=query_string,
                )

            # Build httpx Response
            return Response(
                status_code=status_code,
                headers=resp_headers,
                content=resp_body,
                request=request,
            )

        except Exception as e:
            if self.raise_server_exceptions:
                raise
            # Return 500 error
            return Response(
                status_code=500,
                headers=[('content-type', 'text/plain')],
                content=f"Test client error: {e}".encode('utf-8'),
                request=request,
            )


class TestClient(httpx.Client):
    """Synchronous test client for django-bolt using per-instance test state.

    This client:
    - Creates an isolated test app instance (no global state conflicts)
    - Manages its own event loop for async handlers
    - Routes through full Rust pipeline (auth, middleware, compression)
    - Can run multiple tests in parallel without conflicts

    Usage:
        api = BoltAPI()

        @api.get("/hello")
        async def hello():
            return {"message": "world"}

        with TestClient(api) as client:
            response = client.get("/hello")
            assert response.status_code == 200
            assert response.json() == {"message": "world"}
    """

    __test__ = False  # Tell pytest this is not a test class

    def __init__(
        self,
        api: BoltAPI,
        base_url: str = "http://testserver.local",
        raise_server_exceptions: bool = True,
        use_http_layer: bool = False,
        **kwargs: Any,
    ):
        """Initialize test client.

        Args:
            api: BoltAPI instance to test
            base_url: Base URL for requests
            raise_server_exceptions: If True, raise exceptions from handlers
            use_http_layer: If True, route through Actix HTTP layer (enables testing
                           CORS, rate limiting, compression). Default False for fast tests.
            **kwargs: Additional arguments passed to httpx.Client
        """
        from django_bolt import _core

        # Create test app instance
        self.app_id = _core.create_test_app(api._dispatch, False)

        # Register routes
        rust_routes = [
            (method, path, handler_id, handler)
            for method, path, handler_id, handler in api._routes
        ]
        _core.register_test_routes(self.app_id, rust_routes)

        # Register middleware metadata if any exists
        if api._handler_middleware:
            middleware_data = [
                (handler_id, meta)
                for handler_id, meta in api._handler_middleware.items()
            ]
            _core.register_test_middleware_metadata(self.app_id, middleware_data)

        # Ensure runtime is ready
        _core.ensure_test_runtime(self.app_id)

        super().__init__(
            base_url=base_url,
            transport=BoltTestTransport(self.app_id, raise_server_exceptions, use_http_layer),
            follow_redirects=True,
            **kwargs,
        )
        self.api = api

    def __enter__(self):
        """Enter context manager."""
        return super().__enter__()

    def __exit__(self, *args):
        """Exit context manager and cleanup test app."""
        from django_bolt import _core

        try:
            _core.destroy_test_app(self.app_id)
        except:
            pass
        return super().__exit__(*args)


class AsyncTestClient(httpx.AsyncClient):
    """Asynchronous test client for django-bolt using per-instance test state."""

    __test__ = False  # Tell pytest this is not a test class

    def __init__(
        self,
        api: BoltAPI,
        base_url: str = "http://testserver.local",
        raise_server_exceptions: bool = True,
        use_http_layer: bool = False,
        **kwargs: Any,
    ):
        """Initialize async test client.

        Args:
            api: BoltAPI instance to test
            base_url: Base URL for requests
            raise_server_exceptions: If True, raise exceptions from handlers
            use_http_layer: If True, route through Actix HTTP layer (enables testing
                           CORS, rate limiting, compression). Default False for fast tests.
            **kwargs: Additional arguments passed to httpx.AsyncClient
        """
        from django_bolt import _core

        # Create test app instance
        self.app_id = _core.create_test_app(api._dispatch, False)

        # Register routes
        rust_routes = [
            (method, path, handler_id, handler)
            for method, path, handler_id, handler in api._routes
        ]
        _core.register_test_routes(self.app_id, rust_routes)

        # Register middleware metadata if any exists
        if api._handler_middleware:
            middleware_data = [
                (handler_id, meta)
                for handler_id, meta in api._handler_middleware.items()
            ]
            _core.register_test_middleware_metadata(self.app_id, middleware_data)

        # Ensure runtime is ready
        _core.ensure_test_runtime(self.app_id)

        # Create async transport
        class AsyncTransport(httpx.AsyncBaseTransport):
            def __init__(self, app_id: int, raise_exceptions: bool, use_http_layer: bool):
                self._sync_transport = BoltTestTransport(app_id, raise_exceptions, use_http_layer)

            async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
                return self._sync_transport.handle_request(request)

        super().__init__(
            base_url=base_url,
            transport=AsyncTransport(self.app_id, raise_server_exceptions, use_http_layer),
            follow_redirects=True,
            **kwargs,
        )
        self.api = api

    async def __aenter__(self):
        """Enter async context manager."""
        return await super().__aenter__()

    async def __aexit__(self, *args):
        """Exit async context manager and cleanup test app."""
        from django_bolt import _core

        try:
            _core.destroy_test_app(self.app_id)
        except:
            pass
        return await super().__aexit__(*args)

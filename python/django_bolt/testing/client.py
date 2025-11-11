"""Test clients for django-bolt using per-instance test state.

This version uses the test_state.rs infrastructure which provides:
- Per-instance routers (no global state conflicts)
- Per-instance event loops (proper async handling)
- Streaming response support via stream=True parameter
"""
from __future__ import annotations

from typing import Any, Iterator

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

    @staticmethod
    def _read_cors_settings_from_django() -> list[str] | None:
        """Read CORS_ALLOWED_ORIGINS from Django settings (same as production server).

        Returns:
            List of allowed origins from Django settings, or None if not configured
        """
        try:
            from django.conf import settings

            # Check if CORS_ALLOWED_ORIGINS is defined
            if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
                origins = settings.CORS_ALLOWED_ORIGINS
                if isinstance(origins, (list, tuple)):
                    return list(origins)

            # Check for CORS_ALLOW_ALL_ORIGINS (wildcard)
            if hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS') and settings.CORS_ALLOW_ALL_ORIGINS:
                return ["*"]

            return None
        except (ImportError, AttributeError):
            # Django not configured or settings not available
            return None

    def __init__(
        self,
        api: BoltAPI,
        base_url: str = "http://testserver.local",
        raise_server_exceptions: bool = True,
        use_http_layer: bool = True,
        cors_allowed_origins: list[str] | None = None,
        read_django_settings: bool = True,
        **kwargs: Any,
    ):
        """Initialize test client.

        Args:
            api: BoltAPI instance to test
            base_url: Base URL for requests
            raise_server_exceptions: If True, raise exceptions from handlers
            use_http_layer: If True, route through Actix HTTP layer (enables testing
                           CORS, rate limiting, compression). Default False for fast tests.
            cors_allowed_origins: Global CORS allowed origins for testing.
                                  If None and read_django_settings=True, reads from Django settings.
            read_django_settings: If True, read CORS_ALLOWED_ORIGINS from Django settings
                                 when cors_allowed_origins is None. Default True.
            **kwargs: Additional arguments passed to httpx.Client
        """
        from django_bolt import _core

        # If cors_allowed_origins not provided and read_django_settings=True,
        # read from Django settings (same as production server does)
        if cors_allowed_origins is None and read_django_settings:
            cors_allowed_origins = self._read_cors_settings_from_django()

        # Create test app instance
        self.app_id = _core.create_test_app(api._dispatch, False, cors_allowed_origins)

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

        # Register authentication backends for user resolution (lazy loading in request.user)
        api._register_auth_backends()

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

    # Override HTTP methods to support stream=True
    def _add_streaming_methods(self, response: Response) -> Response:
        """Add iter_content() and iter_lines() methods to response."""
        response._iter_content = lambda chunk_size=1024, decode_unicode=False: self._iter_response_content(
            response.content, chunk_size, decode_unicode
        )
        response.iter_content = response._iter_content  # type: ignore

        response._iter_lines = lambda decode_unicode=True: self._iter_response_lines(
            response.content, decode_unicode
        )
        response.iter_lines = response._iter_lines  # type: ignore

        return response

    def get(self, url: str | httpx.URL, *, stream: bool = False, **kwargs: Any) -> Response:
        """GET request with optional streaming support."""
        response = super().get(url, **kwargs)
        if stream:
            response = self._add_streaming_methods(response)
        return response

    def post(self, url: str | httpx.URL, *, stream: bool = False, **kwargs: Any) -> Response:
        """POST request with optional streaming support."""
        response = super().post(url, **kwargs)
        if stream:
            response = self._add_streaming_methods(response)
        return response

    def put(self, url: str | httpx.URL, *, stream: bool = False, **kwargs: Any) -> Response:
        """PUT request with optional streaming support."""
        response = super().put(url, **kwargs)
        if stream:
            response = self._add_streaming_methods(response)
        return response

    def patch(self, url: str | httpx.URL, *, stream: bool = False, **kwargs: Any) -> Response:
        """PATCH request with optional streaming support."""
        response = super().patch(url, **kwargs)
        if stream:
            response = self._add_streaming_methods(response)
        return response

    def delete(self, url: str | httpx.URL, *, stream: bool = False, **kwargs: Any) -> Response:
        """DELETE request with optional streaming support."""
        response = super().delete(url, **kwargs)
        if stream:
            response = self._add_streaming_methods(response)
        return response

    def head(self, url: str | httpx.URL, *, stream: bool = False, **kwargs: Any) -> Response:
        """HEAD request with optional streaming support."""
        response = super().head(url, **kwargs)
        if stream:
            response = self._add_streaming_methods(response)
        return response

    def options(self, url: str | httpx.URL, *, stream: bool = False, **kwargs: Any) -> Response:
        """OPTIONS request with optional streaming support."""
        response = super().options(url, **kwargs)
        if stream:
            response = self._add_streaming_methods(response)
        return response

    @staticmethod
    def _iter_response_content(
        content: bytes, chunk_size: int = 1024, decode_unicode: bool = False
    ) -> Iterator[str | bytes]:
        """Iterate over response content in chunks.

        Args:
            content: Full response content
            chunk_size: Size of each chunk in bytes
            decode_unicode: If True, decode bytes to string using utf-8

        Yields:
            Chunks of response content
        """
        pos = 0
        while pos < len(content):
            chunk = content[pos : pos + chunk_size]
            pos += chunk_size

            if decode_unicode:
                yield chunk.decode("utf-8")
            else:
                yield chunk

    @staticmethod
    def _iter_response_lines(content: bytes, decode_unicode: bool = True) -> Iterator[str]:
        """Iterate over response content line by line.

        Args:
            content: Full response content
            decode_unicode: If True, decode bytes to string (default True)

        Yields:
            Lines from the response
        """
        buffer = b"" if not decode_unicode else ""

        for chunk in TestClient._iter_response_content(content, chunk_size=8192, decode_unicode=decode_unicode):
            if chunk:
                buffer += chunk

                # Split on newlines
                if isinstance(buffer, bytes):
                    lines = buffer.split(b"\n")
                else:
                    lines = buffer.split("\n")

                # Yield all complete lines, keep incomplete line in buffer
                for line in lines[:-1]:
                    yield line if isinstance(line, str) else line.decode("utf-8")

                buffer = lines[-1]

        # Yield any remaining data in buffer
        if buffer:
            yield buffer if isinstance(buffer, str) else buffer.decode("utf-8")

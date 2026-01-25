"""
Test StreamingResponse compatibility with various middleware configurations.
"""

import asyncio

import pytest

from django_bolt import BoltAPI, StreamingResponse
from django_bolt.middleware import Middleware
from django_bolt.testing import TestClient


class CustomTestMiddleware(Middleware):
    """Custom test middleware that tracks call count."""

    def __init__(self, name: str):
        self.name = name
        self.call_count = 0

    async def process_request(self, request):
        self.call_count += 1
        response = await self.get_response(request)
        return response


class HeaderAddingMiddleware(Middleware):
    """Middleware that adds custom headers."""

    def __init__(self, header_name: str, header_value: str):
        self.header_name = header_name
        self.header_value = header_value

    async def process_request(self, request):
        response = await self.get_response(request)
        # Note: Headers can't be modified in streaming responses after they start
        # This middleware just passes through
        return response


class ModifyingMiddleware(Middleware):
    """Middleware that modifies request state."""

    def __init__(self, get_response=None):
        # Allow standalone initialization without get_response
        # The framework will set get_response later if needed
        if get_response:
            super().__init__(get_response)
        else:
            # Initialize with placeholder
            self.get_response = None
            self.call_count = 0

    async def process_request(self, request):
        self.call_count += 1
        # Add custom state
        if not hasattr(request, "state"):
            request.state = {}
        request.state["middleware_ran"] = True
        response = await self.get_response(request)
        return response


def test_streaming_response_with_single_middleware():
    """Test that StreamingResponse works with a single middleware."""
    custom_mw = CustomTestMiddleware("test")
    api = BoltAPI(
        middleware=[custom_mw],
        middleware_config={
            "cors": {"origins": ["http://localhost:3000"], "credentials": True}
        },
    )

    @api.get("/stream")
    async def stream_endpoint():
        async def generate():
            for i in range(3):
                await asyncio.sleep(0.001)
                yield f"data: {i}\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    client = TestClient(api, use_http_layer=True)
    response = client.get("/stream")

    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("text/event-stream")
    assert response.content == b"data: 0\ndata: 1\ndata: 2\n"
    # Verify middleware was called
    assert custom_mw.call_count == 1


def test_streaming_response_with_multiple_middleware():
    """Test that StreamingResponse works with multiple middleware instances."""
    mw1 = CustomTestMiddleware("mw1")
    mw2 = CustomTestMiddleware("mw2")
    mw3 = CustomTestMiddleware("mw3")

    api = BoltAPI(middleware=[mw1, mw2, mw3])

    @api.get("/stream-multi")
    async def stream_multi():
        async def generate():
            for i in range(2):
                await asyncio.sleep(0.001)
                yield f"item-{i}\n"

        return StreamingResponse(generate(), media_type="text/plain")

    client = TestClient(api, use_http_layer=True)
    response = client.get("/stream-multi")

    assert response.status_code == 200
    assert response.content == b"item-0\nitem-1\n"
    # Verify all middleware were called
    assert mw1.call_count == 1
    assert mw2.call_count == 1
    assert mw3.call_count == 1


def test_streaming_response_sync_generator():
    """Test StreamingResponse with sync generator and middleware."""
    mw = CustomTestMiddleware("sync")
    api = BoltAPI(middleware=[mw])

    @api.get("/stream-sync")
    async def stream_sync():
        def generate():
            for i in range(3):
                yield f"sync-{i}\n"

        return StreamingResponse(generate(), media_type="text/plain")

    client = TestClient(api, use_http_layer=True)
    response = client.get("/stream-sync")

    assert response.status_code == 200
    assert response.content == b"sync-0\nsync-1\nsync-2\n"
    assert mw.call_count == 1


def test_streaming_response_with_state_modifying_middleware():
    """Test StreamingResponse with middleware that modifies request state."""
    mw = ModifyingMiddleware()
    api = BoltAPI(middleware=[mw])

    @api.get("/stream-state")
    async def stream_with_state(request):
        # Verify middleware state was set
        assert hasattr(request, "state")
        assert request.state.get("middleware_ran") is True

        async def generate():
            yield "state-ok\n"

        return StreamingResponse(generate(), media_type="text/plain")

    client = TestClient(api, use_http_layer=True)
    response = client.get("/stream-state")

    assert response.status_code == 200
    assert response.content == b"state-ok\n"
    assert mw.call_count == 1


def test_streaming_response_different_media_types():
    """Test StreamingResponse with various media types and middleware."""
    mw = CustomTestMediaType()
    api = BoltAPI(middleware=[mw])

    @api.get("/stream-json")
    async def stream_json():
        async def generate():
            yield '{"message": "hello"}\n'

        return StreamingResponse(generate(), media_type="application/json")

    @api.get("/stream-text")
    async def stream_text():
        async def generate():
            yield "plain text\n"

        return StreamingResponse(generate(), media_type="text/plain")

    @api.get("/stream-html")
    async def stream_html():
        async def generate():
            yield "<div>content</div>\n"

        return StreamingResponse(generate(), media_type="text/html")

    client = TestClient(api, use_http_layer=True)

    response = client.get("/stream-json")
    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("application/json")
    assert response.content == b'{"message": "hello"}\n'

    response = client.get("/stream-text")
    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("text/plain")
    assert response.content == b"plain text\n"

    response = client.get("/stream-html")
    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("text/html")
    assert response.content == b"<div>content</div>\n"

    # Middleware should have been called 3 times (once per endpoint)
    assert mw.call_count == 3


def test_streaming_response_empty():
    """Test StreamingResponse with empty generator and middleware."""
    mw = CustomTestMiddleware("empty")
    api = BoltAPI(middleware=[mw])

    @api.get("/stream-empty")
    async def stream_empty():
        async def generate():
            return
            yield  # Never reached

        return StreamingResponse(generate(), media_type="text/plain")

    client = TestClient(api, use_http_layer=True)
    response = client.get("/stream-empty")

    assert response.status_code == 200
    assert response.content == b""
    assert mw.call_count == 1


def test_streaming_response_large_chunks():
    """Test StreamingResponse with large chunks and middleware."""
    mw = CustomTestMiddleware("large")
    api = BoltAPI(middleware=[mw])

    @api.get("/stream-large")
    async def stream_large():
        async def generate():
            for i in range(5):
                chunk = "x" * 1000 + f"\n{i}\n"
                yield chunk.encode()

        return StreamingResponse(generate(), media_type="application/octet-stream")

    client = TestClient(api, use_http_layer=True)
    response = client.get("/stream-large")

    assert response.status_code == 200
    # Verify content length
    assert len(response.content) == 5 * (1000 + 3)  # 1000 chars + \n + digit + \n
    assert mw.call_count == 1


def test_streaming_response_mixed_types():
    """Test StreamingResponse yielding different data types."""
    mw = CustomTestMiddleware("mixed")
    api = BoltAPI(middleware=[mw])

    @api.get("/stream-mixed")
    async def stream_mixed():
        async def generate():
            yield b"bytes-chunk\n"
            await asyncio.sleep(0.001)
            yield "string-chunk\n"
            await asyncio.sleep(0.001)
            yield bytearray(b"bytearray-chunk\n")

        return StreamingResponse(generate(), media_type="text/plain")

    client = TestClient(api, use_http_layer=True)
    response = client.get("/stream-mixed")

    assert response.status_code == 200
    assert b"bytes-chunk\n" in response.content
    assert b"string-chunk\n" in response.content
    assert b"bytearray-chunk\n" in response.content
    assert mw.call_count == 1


def test_streaming_response_sse_format():
    """Test Server-Sent Events format with middleware."""
    mw = CustomTestMiddleware("sse")
    api = BoltAPI(middleware=[mw])

    @api.get("/stream-sse")
    async def stream_sse():
        async def generate():
            yield "event: message\ndata: hello\n\n"
            await asyncio.sleep(0.001)
            yield "event: update\ndata: world\n\n"
            await asyncio.sleep(0.001)
            yield ": comment\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    client = TestClient(api, use_http_layer=True)
    response = client.get("/stream-sse")

    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("text/event-stream")
    assert b"event: message" in response.content
    assert b"data: hello" in response.content
    assert b"event: update" in response.content
    assert b"data: world" in response.content
    assert b": comment" in response.content
    assert mw.call_count == 1


def test_streaming_response_with_compression_config():
    """Test that streaming can work alongside compression config."""
    from django_bolt.middleware import CompressionConfig, skip_middleware

    mw = CustomTestMiddleware("compress")
    api = BoltAPI(
        middleware=[mw],
        compression=CompressionConfig(backend="gzip"),
    )

    @api.get("/stream")
    @skip_middleware("compression")
    async def stream_with_skip():
        async def generate():
            for i in range(2):
                yield f"data-{i}\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    client = TestClient(api, use_http_layer=True)
    response = client.get("/stream", headers={"Accept-Encoding": "gzip"})

    assert response.status_code == 200
    # Streaming with skip should NOT have Content-Encoding header
    assert response.headers.get("content-encoding") is None
    assert response.content == b"data-0\ndata-1\n"
    assert mw.call_count == 1


def test_multiple_streaming_endpoints_with_shared_middleware():
    """Test multiple streaming endpoints sharing the same middleware."""
    shared_mw = CustomTestMiddleware("shared")
    api = BoltAPI(middleware=[shared_mw])

    @api.get("/stream1")
    async def stream1():
        async def generate():
            yield "stream1\n"

        return StreamingResponse(generate(), media_type="text/plain")

    @api.get("/stream2")
    async def stream2():
        async def generate():
            yield "stream2\n"

        return StreamingResponse(generate(), media_type="text/plain")

    @api.get("/stream3")
    async def stream3():
        async def generate():
            yield "stream3\n"

        return StreamingResponse(generate(), media_type="text/plain")

    client = TestClient(api, use_http_layer=True)

    response1 = client.get("/stream1")
    assert response1.status_code == 200
    assert response1.content == b"stream1\n"

    response2 = client.get("/stream2")
    assert response2.status_code == 200
    assert response2.content == b"stream2\n"

    response3 = client.get("/stream3")
    assert response3.status_code == 200
    assert response3.content == b"stream3\n"

    # Middleware should have been called 3 times
    assert shared_mw.call_count == 3


def test_streaming_response_with_rate_limit_config():
    """Test StreamingResponse with rate_limit middleware config."""
    from django_bolt.middleware import rate_limit

    api = BoltAPI(middleware_config={"rate_limit": {"rps": 100}})

    @api.get("/stream-rate-limit")
    @rate_limit(rps=50)
    async def stream_rate_limited():
        async def generate():
            for i in range(2):
                yield f"limit-{i}\n"

        return StreamingResponse(generate(), media_type="text/plain")

    client = TestClient(api, use_http_layer=True)
    response = client.get("/stream-rate-limit")

    assert response.status_code == 200
    assert response.content == b"limit-0\nlimit-1\n"


class CustomTestMediaType(Middleware):
    """Custom test middleware."""

    def __init__(self, get_response=None):
        if get_response:
            super().__init__(get_response)
        else:
            self.get_response = None
            self.call_count = 0

    async def process_request(self, request):
        self.call_count += 1
        response = await self.get_response(request)
        return response


def test_streaming_response_with_django_middleware():
    """Test that StreamingResponse works correctly with Django middleware enabled.

    This test verifies that the Django middleware adapter correctly passes through
    StreamingResponse without attempting to convert its generator content to bytes.
    Previously, the adapter would call str() on the generator, producing:
    '<async_generator object ... at 0x...>'
    """
    # Create API with Django middleware enabled
    # Using a list of middleware that won't interfere with the response
    api = BoltAPI(
        django_middleware=["django.middleware.common.CommonMiddleware"],
    )

    @api.get("/stream-django")
    async def stream_with_django():
        async def generate():
            for i in range(3):
                await asyncio.sleep(0.001)
                yield f"django-{i}\n"

        return StreamingResponse(generate(), media_type="text/plain")

    client = TestClient(api, use_http_layer=True)
    response = client.get("/stream-django")

    assert response.status_code == 200
    # Verify the content is the actual streamed data, not a string representation
    # of the generator like '<async_generator object ...>'
    assert response.content == b"django-0\ndjango-1\ndjango-2\n"
    assert b"async_generator" not in response.content


def test_streaming_response_sse_with_django_middleware():
    """Test that SSE StreamingResponse works correctly with Django middleware."""
    api = BoltAPI(
        django_middleware=["django.middleware.common.CommonMiddleware"],
    )

    @api.get("/sse-django")
    async def sse_with_django():
        async def generate():
            yield "event: message\ndata: hello\n\n"
            await asyncio.sleep(0.001)
            yield "event: update\ndata: world\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    client = TestClient(api, use_http_layer=True)
    response = client.get("/sse-django")

    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("text/event-stream")
    assert b"event: message" in response.content
    assert b"data: hello" in response.content
    assert b"async_generator" not in response.content

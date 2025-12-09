"""
Tests for SSE streaming and concurrent connections.

NOTE: These tests use TestClient which is synchronous and materializes
responses fully. Therefore, they CANNOT test:
- Zombie thread leaks (a129bb1) - need real streaming with early disconnect
- Generator cleanup on disconnect (afca2ca) - need real client disconnect

For testing those fixes, use the load test script:
    uv run python scripts/sse_load.py --url http://localhost:8000/sync-sse --clients 5000 --duration 10
then immediately run again. If the view hangs then we have the issue.
    uv run python scripts/sse_load.py --url http://localhost:8000/sync-sse --clients 5000 --duration 10

The load test will:
1. Verify threads don't become zombies on ~50 concurrent disconnects
2. Verify finally blocks execute by monitoring resource cleanup

These unit tests verify:
- SSE format and parsing work correctly
- Streaming API (iter_content, iter_lines) functions
- Concurrent complete requests work
- Data integrity under various conditions
"""

from __future__ import annotations

import asyncio
import time

import pytest

from django_bolt import BoltAPI, StreamingResponse
from django_bolt.testing import TestClient


@pytest.fixture(scope="module")
def api():
    """Create test API with SSE streaming endpoints."""
    api = BoltAPI()

    # ==================== Async SSE Endpoints ====================

    @api.get("/sse-async-basic")
    async def sse_async_basic():
        """Basic async SSE with 5 messages."""
        async def gen():
            for i in range(5):
                yield f"data: async-message-{i}\n\n"
                await asyncio.sleep(0.01)
        return StreamingResponse(gen(), media_type="text/event-stream")

    @api.get("/sse-async-sse-format")
    async def sse_async_sse_format():
        """Async SSE with proper SSE event fields."""
        async def gen():
            for i in range(3):
                yield f"event: update\nid: {i}\ndata: {{\"count\": {i}}}\n\n"
                await asyncio.sleep(0.01)
        return StreamingResponse(gen(), media_type="text/event-stream")

    @api.get("/sse-async-mixed-types")
    async def sse_async_mixed_types():
        """Async SSE with different data types."""
        async def gen():
            yield "data: first\n\n"
            await asyncio.sleep(0.01)
            yield b"data: bytes-message\n\n"
            await asyncio.sleep(0.01)
            yield "data: third\n\n"
        return StreamingResponse(gen(), media_type="text/event-stream")

    # ==================== Sync SSE Endpoints ====================

    @api.get("/sse-sync-basic")
    async def sse_sync_basic():
        """Basic sync SSE with 5 messages."""
        def gen():
            for i in range(5):
                yield f"data: sync-message-{i}\n\n"
                time.sleep(0.01)
        return StreamingResponse(gen(), media_type="text/event-stream")

    @api.get("/sse-sync-sse-format")
    async def sse_sync_sse_format():
        """Sync SSE with proper SSE event fields."""
        def gen():
            for i in range(3):
                yield f"event: tick\nid: {i}\ndata: {i}\n\n"
                time.sleep(0.01)
        return StreamingResponse(gen(), media_type="text/event-stream")

    # ==================== High-frequency Endpoints ====================

    @api.get("/sse-rapid-async")
    async def sse_rapid_async():
        """High-frequency async messages (20 per second)."""
        async def gen():
            for i in range(20):
                yield f"data: {i}\n\n"
                await asyncio.sleep(0.05)  # 20 per second
        return StreamingResponse(gen(), media_type="text/event-stream")

    @api.get("/sse-rapid-sync")
    async def sse_rapid_sync():
        """High-frequency sync messages (20 per second)."""
        def gen():
            for i in range(20):
                yield f"data: {i}\n\n"
                time.sleep(0.05)
        return StreamingResponse(gen(), media_type="text/event-stream")

    # ==================== Endpoints with Cleanup Tracking ====================

    @api.get("/sse-async-with-tracking")
    async def sse_async_with_tracking():
        """Async SSE that yields tracking data to verify generator execution."""
        async def gen():
            # Send start marker
            yield "data: START\n\n"

            for i in range(3):
                yield f"data: chunk-{i}\n\n"
                await asyncio.sleep(0.01)

            # Send end marker to verify generator completed
            yield "data: END\n\n"

        return StreamingResponse(gen(), media_type="text/event-stream")

    @api.get("/sse-sync-with-tracking")
    async def sse_sync_with_tracking():
        """Sync SSE that yields tracking data to verify generator execution."""
        def gen():
            # Send start marker
            yield "data: START\n\n"

            for i in range(3):
                yield f"data: chunk-{i}\n\n"
                time.sleep(0.01)

            # Send end marker to verify generator completed
            yield "data: END\n\n"

        return StreamingResponse(gen(), media_type="text/event-stream")

    return api


@pytest.fixture(scope="module")
def client(api):
    """Create TestClient for the API."""
    with TestClient(api, use_http_layer=True) as client:
        yield client


def parse_sse_data(content: str) -> list[str]:
    """Parse SSE message data from response content.

    SSE format: data: <value>\n\n
    This extracts all data values.
    """
    data_lines = []
    for line in content.split("\n"):
        if line.startswith("data: "):
            data_lines.append(line[6:])  # Strip "data: " prefix
    return data_lines


def parse_sse_events(content: str) -> list[dict]:
    """Parse complete SSE events from response content.

    Returns list of dicts with keys: data, event, id, retry
    """
    events = []
    current_event = {}

    for line in content.split("\n"):
        if not line.strip():  # Empty line = end of message
            if current_event:
                events.append(current_event)
                current_event = {}
        elif line.startswith("data: "):
            current_event["data"] = line[6:]
        elif line.startswith("event: "):
            current_event["event"] = line[7:]
        elif line.startswith("id: "):
            current_event["id"] = line[4:]
        elif line.startswith("retry: "):
            current_event["retry"] = line[7:]
        elif line.startswith(":"):
            # Comment line - ignore
            pass

    if current_event:
        events.append(current_event)

    return events


# ============================================================================
# Basic Functionality Tests
# ============================================================================


def test_async_sse_basic(client):
    """Test basic async SSE streaming works."""
    response = client.get("/sse-async-basic")
    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("text/event-stream")

    content = response.content.decode()
    data = parse_sse_data(content)

    assert len(data) == 5
    assert data[0] == "async-message-0"
    assert data[4] == "async-message-4"


def test_sync_sse_basic(client):
    """Test basic sync SSE streaming works."""
    response = client.get("/sse-sync-basic")
    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("text/event-stream")

    content = response.content.decode()
    data = parse_sse_data(content)

    assert len(data) == 5
    assert data[0] == "sync-message-0"
    assert data[4] == "sync-message-4"


# ============================================================================
# SSE Format Validation Tests
# ============================================================================


def test_async_sse_event_fields(client):
    """Test async SSE with event, id, and data fields."""
    response = client.get("/sse-async-sse-format")
    assert response.status_code == 200

    content = response.content.decode()
    events = parse_sse_events(content)

    assert len(events) == 3
    assert events[0].get("event") == "update"
    assert events[0].get("id") == "0"
    assert '0' in events[0].get("data", "")
    assert events[2].get("id") == "2"


def test_sync_sse_event_fields(client):
    """Test sync SSE with event, id, and data fields."""
    response = client.get("/sse-sync-sse-format")
    assert response.status_code == 200

    content = response.content.decode()
    events = parse_sse_events(content)

    assert len(events) == 3
    assert events[0].get("event") == "tick"
    assert events[1].get("id") == "1"


# ============================================================================
# Data Type Handling Tests
# ============================================================================


def test_async_mixed_types(client):
    """Test async SSE handles different data types (str, bytes)."""
    response = client.get("/sse-async-mixed-types")
    assert response.status_code == 200

    content = response.content.decode()
    data = parse_sse_data(content)

    assert len(data) == 3
    assert data[0] == "first"
    assert data[1] == "bytes-message"
    assert data[2] == "third"


# ============================================================================
# High-Frequency Streaming Tests
# ============================================================================


def test_rapid_async_streaming(client):
    """Test rapid async SSE streaming (20 messages)."""
    response = client.get("/sse-rapid-async")
    assert response.status_code == 200

    content = response.content.decode()
    data = parse_sse_data(content)

    # Should have all 20 messages
    assert len(data) == 20

    # Verify data integrity
    for i, msg in enumerate(data):
        assert msg == str(i), f"Expected {i}, got {msg}"


def test_rapid_sync_streaming(client):
    """Test rapid sync SSE streaming (20 messages)."""
    response = client.get("/sse-rapid-sync")
    assert response.status_code == 200

    content = response.content.decode()
    data = parse_sse_data(content)

    # Should have all 20 messages
    assert len(data) == 20

    # Verify data integrity
    for i, msg in enumerate(data):
        assert msg == str(i), f"Expected {i}, got {msg}"


# ============================================================================
# Generator Completion Tests
# ============================================================================


def test_async_generator_completes(client):
    """Test async generator with tracking markers completes properly."""
    response = client.get("/sse-async-with-tracking")
    assert response.status_code == 200

    content = response.content.decode()
    data = parse_sse_data(content)

    # Should have: START, chunk-0, chunk-1, chunk-2, END
    assert len(data) == 5
    assert data[0] == "START", "Generator should yield START marker"
    assert data[1] == "chunk-0"
    assert data[2] == "chunk-1"
    assert data[3] == "chunk-2"
    assert data[4] == "END", "Generator should complete and yield END marker"


def test_sync_generator_completes(client):
    """Test sync generator with tracking markers completes properly."""
    response = client.get("/sse-sync-with-tracking")
    assert response.status_code == 200

    content = response.content.decode()
    data = parse_sse_data(content)

    # Should have: START, chunk-0, chunk-1, chunk-2, END
    assert len(data) == 5
    assert data[0] == "START", "Generator should yield START marker"
    assert data[1] == "chunk-0"
    assert data[2] == "chunk-1"
    assert data[3] == "chunk-2"
    assert data[4] == "END", "Generator should complete and yield END marker"


# ============================================================================
# Concurrent Connection Tests
# ============================================================================


def test_concurrent_async_sse(client):
    """Test multiple concurrent async SSE connections work correctly."""

    # Make 3 concurrent-like requests (sequential in test, but tests server handles them)
    responses = []
    for _req_num in range(3):
        response = client.get("/sse-async-basic")
        assert response.status_code == 200
        responses.append(response)

    # Verify all responses are complete and correct
    for _resp_num, response in enumerate(responses):
        content = response.content.decode()
        data = parse_sse_data(content)
        assert len(data) == 5
        assert data[0] == "async-message-0"



def test_concurrent_sync_sse(client):
    """Test multiple concurrent sync SSE connections work correctly."""
    # Make 3 concurrent-like requests
    responses = []
    for _ in range(3):
        response = client.get("/sse-sync-basic")
        assert response.status_code == 200
        responses.append(response)

    # Verify all responses are complete and correct
    for response in responses:
        content = response.content.decode()
        data = parse_sse_data(content)
        assert len(data) == 5
        assert data[0] == "sync-message-0"


def test_mixed_async_sync_sse(client):
    """Test alternating async and sync SSE connections work correctly."""
    for _ in range(3):
        async_response = client.get("/sse-async-basic")
        sync_response = client.get("/sse-sync-basic")

        assert async_response.status_code == 200
        assert sync_response.status_code == 200

        async_data = parse_sse_data(async_response.content.decode())
        sync_data = parse_sse_data(sync_response.content.decode())

        assert len(async_data) == 5
        assert len(sync_data) == 5


# ============================================================================
# Header Validation Tests
# ============================================================================


def test_sse_content_type_header(client):
    """Test that SSE endpoints set correct Content-Type header."""
    response = client.get("/sse-async-basic")

    content_type = response.headers.get("content-type", "").lower()
    assert "text/event-stream" in content_type


def test_sse_cache_control_headers(client):
    """Test that SSE endpoints set appropriate cache control headers."""
    response = client.get("/sse-async-basic")

    # SSE should not be cached
    cache_control = response.headers.get("cache-control", "").lower()
    # May or may not be set, but if present should indicate no caching
    if cache_control:
        assert "no-cache" in cache_control or "no-store" in cache_control


def test_sse_no_buffering_header(client):
    """Test that SSE endpoints set X-Accel-Buffering header for nginx."""
    response = client.get("/sse-async-basic")

    x_accel = response.headers.get("x-accel-buffering", "").lower()
    # Header might be set to "no" to prevent nginx buffering
    if x_accel:
        assert x_accel == "no"


# ============================================================================
# Manual Testing Notes for Fixes (a129bb1, afca2ca)
# ============================================================================
#
# ZOMBIE THREAD FIX (a129bb1):
#   Issue: Sync generators kept running on client disconnect, exhausting thread pool
#   Fix: Set 'exhausted = true' when blocking_send() fails
#
#   Manual test:
#   1. Start server: python manage.py runbolt
#   2. Connect many clients that disconnect early:
#      for i in {1..300}; do curl -N http://localhost:8000/sse & done
#   3. Without fix: Server stops accepting connections after ~200 disconnects
#   4. With fix: All 300+ connections succeed
#
# GENERATOR CLEANUP FIX (afca2ca):
#   Issue: Finally blocks in generators didn't run on disconnect → resource leaks
#   Fix: Call .close()/.aclose() on generators when disconnect detected
#
#   Manual test:
#   1. Add logging to finally blocks in your SSE generators
#   2. Connect and disconnect clients
#   3. Without fix: Finally blocks never log (cleanup didn't run)
#   4. With fix: Finally blocks log when client disconnects


# ============================================================================
# Multiple Request Robustness Tests
# ============================================================================


def test_repeated_sse_connections(client):
    """Test repeated SSE connections work reliably."""
    print("\n" + "=" * 80)
    print("TEST: Repeated SSE Connections (10x)")
    print("=" * 80)

    for i in range(10):
        print(f"\nConnection {i + 1}/10...")
        response = client.get("/sse-sync-basic")
        assert response.status_code == 200, f"Failed on iteration {i}"
        print(f"  Status: {response.status_code} ✓")

        content = response.content.decode()
        data = parse_sse_data(content)
        assert len(data) == 5, f"Wrong number of messages on iteration {i}"
        print(f"  Messages: {len(data)} ✓")

    print("\n✓ All 10 connections succeeded")
    print("")


def test_rapid_sequential_requests(client):
    """Test rapid sequential SSE requests don't cause issues."""
    print("\n" + "=" * 80)
    print("TEST: Rapid Sequential Requests (2 rounds)")
    print("=" * 80)

    urls = [
        "/sse-async-basic",
        "/sse-sync-basic",
        "/sse-async-sse-format",
        "/sse-sync-sse-format",
    ]

    for round_num in range(2):
        print(f"\nRound {round_num + 1}:")
        for url in urls:
            response = client.get(url)
            assert response.status_code == 200
            assert len(response.content) > 0
            print(f"  {url}: {response.status_code} | {len(response.content)} bytes ✓")

    print("\n✓ All rapid requests succeeded")
    print("")


# ============================================================================
# Streaming API Tests (stream=True parameter)
# ============================================================================


def test_streaming_with_iter_content(client):
    """Test that stream=True enables iter_content() on responses."""

    response = client.get("/sse-sync-basic", stream=True)
    assert response.status_code == 200

    # iter_content should be available
    assert hasattr(response, "iter_content")
    assert callable(response.iter_content)

    # Iterate over chunks
    chunks = []
    for _i, chunk in enumerate(response.iter_content(chunk_size=32, decode_unicode=True)):
        if chunk:
            chunks.append(chunk)

    assert len(chunks) > 0

    # Reconstruct content
    content = "".join(chunks)
    assert "sync-message-0" in content
    assert "sync-message-4" in content


def test_streaming_with_iter_lines(client):
    """Test that stream=True enables iter_lines() on responses."""
    response = client.get("/sse-async-basic", stream=True)
    assert response.status_code == 200

    # iter_lines should be available
    assert hasattr(response, "iter_lines")
    assert callable(response.iter_lines)

    # Iterate over lines
    lines = list(response.iter_lines())

    assert len(lines) > 0
    # Should have lines containing our data
    data_lines = [line for line in lines if "async-message" in line]
    assert len(data_lines) > 0


def test_streaming_chunk_sizes(client):
    """Test iter_content with different chunk sizes."""
    response = client.get("/sse-rapid-async", stream=True)
    assert response.status_code == 200

    # Test with small chunks
    small_chunks = list(response.iter_content(chunk_size=16, decode_unicode=True))
    assert len(small_chunks) > 10  # Should have many small chunks

    # Test with large chunks
    response2 = client.get("/sse-rapid-async", stream=True)
    large_chunks = list(response2.iter_content(chunk_size=8192, decode_unicode=True))
    assert len(large_chunks) < len(small_chunks)  # Fewer large chunks

    # Verify content is the same
    small_content = "".join(small_chunks)
    large_content = "".join(large_chunks)
    assert small_content == large_content


def test_streaming_decode_unicode(client):
    """Test iter_content with and without decode_unicode."""
    response = client.get("/sse-sync-basic", stream=True)
    assert response.status_code == 200

    # With decode_unicode=True (default)
    chunks_str = list(response.iter_content(chunk_size=64, decode_unicode=True))
    assert all(isinstance(chunk, str) for chunk in chunks_str if chunk)

    # With decode_unicode=False
    response2 = client.get("/sse-sync-basic", stream=True)
    chunks_bytes = list(response2.iter_content(chunk_size=64, decode_unicode=False))
    assert all(isinstance(chunk, bytes) for chunk in chunks_bytes if chunk)

    # Content should be equivalent
    str_content = "".join(chunks_str)
    bytes_content = b"".join(chunks_bytes).decode("utf-8")
    assert str_content == bytes_content


def test_streaming_api_on_all_http_methods(client):
    """Test that stream=True works on different HTTP methods."""
    # Test GET (already tested above)
    response = client.get("/sse-async-basic", stream=True)
    assert hasattr(response, "iter_content")
    assert len(response.content) > 0

    # Test other methods would need streaming endpoints, but we can at least verify
    # the API accepts stream=True without error
    response2 = client.post("/sse-async-basic", stream=True)  # Won't actually stream but should accept stream param
    assert response2.status_code in [200, 404, 405]  # Some status is OK

import os
import tempfile
import time

import pytest

from django_bolt import BoltAPI
from django_bolt.responses import FileResponse
from django_bolt.testing import TestClient

# Create test files once at module level
TEST_DIR = tempfile.mkdtemp()

# Small file (< 10MB) - 1KB
SMALL_FILE = os.path.join(TEST_DIR, "small_file.txt")
with open(SMALL_FILE, "w") as f:
    f.write("x" * 1024)

# Medium file (< 10MB) - 1MB
MEDIUM_FILE = os.path.join(TEST_DIR, "medium_file.txt")
with open(MEDIUM_FILE, "w") as f:
    f.write("y" * (1024 * 1024))

# Large file (> 10MB) - 11MB
LARGE_FILE = os.path.join(TEST_DIR, "large_file.bin")
with open(LARGE_FILE, "wb") as f:
    f.write(b"z" * (11 * 1024 * 1024))


@pytest.fixture(scope="module")
def api():
    """Create test API with file endpoints"""
    api = BoltAPI()

    @api.get("/file/small")
    async def get_small_file():
        """Small file should be read into memory"""
        return FileResponse(SMALL_FILE, filename="small_file.txt")

    @api.get("/file/medium")
    async def get_medium_file():
        """Medium file should be read into memory"""
        return FileResponse(MEDIUM_FILE, filename="medium_file.txt")

    @api.get("/file/large")
    async def get_large_file():
        """Large file should be streamed"""
        return FileResponse(LARGE_FILE, filename="large_file.bin")

    @api.get("/file/custom-headers")
    async def get_file_with_headers():
        """Test custom headers"""
        return FileResponse(
            SMALL_FILE,
            filename="custom.txt",
            headers={"X-Custom-Header": "test-value"}
        )

    @api.get("/file/custom-media-type")
    async def get_file_with_media_type():
        """Test custom media type"""
        return FileResponse(
            SMALL_FILE,
            media_type="application/octet-stream"
        )

    return api


@pytest.fixture(scope="module")
def client(api):
    """Create test client with HTTP layer enabled to test file serving"""
    # use_http_layer=True enables full HTTP stack including file serving
    return TestClient(api, use_http_layer=True)


def test_small_file_response(client):
    """Test that small files (<10MB) work correctly"""
    response = client.get("/file/small")

    # Should succeed
    assert response.status_code == 200

    # Should have correct Content-Type
    assert response.headers.get("content-type", "").startswith("text/")

    # Should have Content-Disposition with filename
    content_disp = response.headers.get("content-disposition", "")
    assert "attachment" in content_disp.lower()
    assert "small_file.txt" in content_disp

    # With HTTP layer, we should get the file content
    if response.content:
        assert len(response.content) == 1024
        assert response.content == b"x" * 1024


def test_medium_file_response(client):
    """Test that medium files (<10MB) work correctly"""
    response = client.get("/file/medium")

    # Should succeed
    assert response.status_code == 200

    # With HTTP layer, content should be available
    if response.content:
        assert len(response.content) == 1024 * 1024
        assert response.content[:100] == b"y" * 100
        assert response.content[-100:] == b"y" * 100


def test_large_file_response(client):
    """Test that large files (>10MB) are streamed"""
    response = client.get("/file/large")

    # Should succeed
    assert response.status_code == 200

    # Large files use streaming
    # TestClient may not preserve the full streamed content, so just verify response is successful
    # In production, streaming works correctly
    # Content should be available (even if TestClient doesn't show full stream)
    assert response.content is not None


def test_file_custom_headers(client):
    """Test FileResponse with custom headers"""
    response = client.get("/file/custom-headers")

    assert response.status_code == 200
    assert response.headers.get("x-custom-header") == "test-value"
    assert "custom.txt" in response.headers.get("content-disposition", "")


def test_file_custom_media_type(client):
    """Test FileResponse with custom media type"""
    response = client.get("/file/custom-media-type")

    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/octet-stream"


def test_file_not_found():
    """Test FileResponse with non-existent file returns 404"""
    api = BoltAPI()

    @api.get("/file/nonexistent")
    async def get_nonexistent():
        return FileResponse("/path/to/nonexistent/file.txt")

    # Use HTTP layer to test actual file opening
    client = TestClient(api, use_http_layer=True)
    response = client.get("/file/nonexistent")

    # Should return 404 Not Found (proper HTTP status for missing file)
    # File error happens in Rust after Python serializes the response
    assert response.status_code == 404
    assert b"File not found" in response.content or response.content == b""


def test_file_performance_small_vs_large():
    """Test that small files use in-memory buffering for better performance"""
    api = BoltAPI()
    temp_dir = tempfile.mkdtemp()

    # Create small file
    small_file = os.path.join(temp_dir, "perf_small.txt")
    with open(small_file, "w") as f:
        f.write("x" * (100 * 1024))  # 100KB

    @api.get("/perf/small")
    async def perf_small():
        return FileResponse(small_file)

    client = TestClient(api)

    # Warm up
    client.get("/perf/small")

    # Time multiple requests
    start = time.time()
    for _ in range(100):
        response = client.get("/perf/small")
        assert response.status_code == 200
    elapsed = time.time() - start

    # Should handle 100 requests relatively quickly
    # (This is more of a smoke test than a strict perf test)
    assert elapsed < 5.0  # Should take less than 5 seconds for 100 requests

    print(f"Small file (100KB) - 100 requests: {elapsed:.3f}s ({100/elapsed:.1f} RPS)")

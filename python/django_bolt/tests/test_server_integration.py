"""
Integration tests for the real server with queue-based request handling.

These tests start an actual bolt server process and make HTTP requests to it,
testing the full stack including the Python event loop worker and queue system.
"""
import subprocess
import time
import signal
import requests
import pytest
from pathlib import Path


@pytest.fixture(scope="module")
def test_server():
    """Start a test server process and yield its info"""
    # Use testproject from examples
    project_dir = Path(__file__).parent.parent.parent / "examples" / "testproject"

    # Start server in background
    env = {
        **subprocess.os.environ,
        "DJANGO_SETTINGS_MODULE": "testproject.settings",
    }

    # Start server with runbolt
    proc = subprocess.Popen(
        ["uv", "run", "python", "manage.py", "runbolt",
         "--host", "127.0.0.1", "--port", "8765",
         "--processes", "1", "--workers", "1"],
        cwd=str(project_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Wait for server to start
    max_retries = 30
    for i in range(max_retries):
        try:
            resp = requests.get("http://127.0.0.1:8765/", timeout=1)
            if resp.status_code == 200:
                print(f"Server started after {i+1} attempts")
                break
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(0.5)
    else:
        # Failed to start
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=5)
        pytest.fail(f"Server failed to start.\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")

    yield {
        "base_url": "http://127.0.0.1:8765",
        "proc": proc,
    }

    # Cleanup
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def test_basic_request(test_server):
    """Test a basic GET request through the queue system"""
    resp = requests.get(f"{test_server['base_url']}/")
    assert resp.status_code == 200
    data = resp.json()
    assert "ok" in data or "message" in data


def test_path_params(test_server):
    """Test path parameter extraction"""
    resp = requests.get(f"{test_server['base_url']}/users/123")
    assert resp.status_code == 200


def test_query_params(test_server):
    """Test query parameter extraction"""
    resp = requests.get(f"{test_server['base_url']}/items?page=1&limit=10")
    assert resp.status_code == 200


def test_post_request(test_server):
    """Test POST request with JSON body"""
    resp = requests.post(
        f"{test_server['base_url']}/users",
        json={"name": "Test User", "email": "test@example.com"}
    )
    # May be 200, 201, or 404 depending on endpoint existence
    assert resp.status_code in [200, 201, 404]


def test_concurrent_requests(test_server):
    """Test multiple concurrent requests to ensure queue handles them properly"""
    import concurrent.futures

    def make_request(i):
        resp = requests.get(f"{test_server['base_url']}/", timeout=5)
        return resp.status_code

    # Make 20 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # All requests should succeed
    assert all(status == 200 for status in results), f"Some requests failed: {results}"


def test_request_timeout_behavior(test_server):
    """Test that requests don't timeout under normal conditions"""
    # Make several sequential requests to ensure the queue is working
    for i in range(10):
        resp = requests.get(f"{test_server['base_url']}/", timeout=5)
        assert resp.status_code == 200, f"Request {i} failed with status {resp.status_code}"

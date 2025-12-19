"""
Integration test for SSE CORS headers using production handler.rs code path.

This test starts a REAL server using subprocess and makes actual HTTP requests
to verify that CORS headers are correctly added to SSE streaming responses.

This test would FAIL if the fix in handler.rs (adding CORS headers to SSE responses)
is reverted, because it exercises the actual production code path.

TestClient with use_http_layer=True does NOT exercise handler.rs for streaming
responses - it uses test_state.rs instead. This integration test is the only
way to verify the production SSE CORS fix works.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time

import httpx
import pytest

# Server startup configuration
HOST = "127.0.0.1"
PORT = 19876  # Use unusual port to avoid conflicts
TIMEOUT = 15


def wait_for_server(host: str, port: int, timeout: float = 15) -> bool:
    """Wait for server to be reachable."""
    import socket

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.create_connection((host, port), timeout=2)
            sock.close()
            return True
        except Exception:
            time.sleep(0.3)
    return False


@pytest.fixture(scope="module")
def sse_cors_server():
    """
    Start a real server with SSE + CORS endpoints.

    This fixture creates a temporary Django project with SSE endpoints
    that have CORS configured, starts the server, and yields the base URL.
    """
    # Create temporary directory for test project
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create minimal Django project structure
        project_dir = os.path.join(tmpdir, "testproj")
        os.makedirs(project_dir)

        # Create settings.py
        settings_content = '''
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY = "test-secret-key-for-sse-cors"
DEBUG = True
ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django_bolt",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
USE_TZ = True
ROOT_URLCONF = "testproj.urls"
'''
        with open(os.path.join(project_dir, "settings.py"), "w") as f:
            f.write(settings_content)

        # Create urls.py
        urls_content = '''
urlpatterns = []
'''
        with open(os.path.join(project_dir, "urls.py"), "w") as f:
            f.write(urls_content)

        # Create __init__.py
        with open(os.path.join(project_dir, "__init__.py"), "w") as f:
            f.write("")

        # Create api.py with SSE + CORS endpoints
        api_content = '''
import asyncio
import time

from django_bolt import BoltAPI, StreamingResponse
from django_bolt.middleware import cors

api = BoltAPI()


@api.get("/sse-cors-async")
@cors(origins=["https://example.com", "https://trusted.com"])
async def sse_cors_async():
    """Async SSE endpoint with CORS configured."""
    async def gen():
        for i in range(3):
            yield f"data: message-{i}\\n\\n"
            await asyncio.sleep(0.01)
    return StreamingResponse(gen(), media_type="text/event-stream")


@api.get("/sse-cors-sync")
@cors(origins=["https://sync-app.com"])
async def sse_cors_sync():
    """Sync SSE endpoint with CORS configured."""
    def gen():
        for i in range(3):
            yield f"data: sync-{i}\\n\\n"
            time.sleep(0.01)
    return StreamingResponse(gen(), media_type="text/event-stream")


@api.get("/sse-cors-credentials")
@cors(origins=["https://secure.com"], credentials=True)
async def sse_cors_credentials():
    """SSE endpoint with CORS credentials enabled."""
    async def gen():
        yield "data: secure\\n\\n"
    return StreamingResponse(gen(), media_type="text/event-stream")


@api.get("/sse-cors-wildcard")
@cors(origins=["*"])
async def sse_cors_wildcard():
    """SSE endpoint with wildcard CORS."""
    async def gen():
        yield "data: public\\n\\n"
    return StreamingResponse(gen(), media_type="text/event-stream")


@api.get("/sse-no-cors")
async def sse_no_cors():
    """SSE endpoint without CORS (control test)."""
    async def gen():
        yield "data: no-cors\\n\\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
'''
        with open(os.path.join(project_dir, "api.py"), "w") as f:
            f.write(api_content)

        # Create manage.py
        manage_content = '''#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testproj.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
'''
        manage_path = os.path.join(tmpdir, "manage.py")
        with open(manage_path, "w") as f:
            f.write(manage_content)
        os.chmod(manage_path, 0o755)

        # Add tmpdir to Python path so imports work
        env = os.environ.copy()
        env["PYTHONPATH"] = tmpdir + ":" + env.get("PYTHONPATH", "")

        # Start the server
        cmd = [
            sys.executable, manage_path,
            "runbolt",
            "--host", HOST,
            "--port", str(PORT),
        ]

        process = subprocess.Popen(
            cmd,
            cwd=tmpdir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            # Wait for server to start
            if not wait_for_server(HOST, PORT, timeout=TIMEOUT):
                stdout, stderr = process.communicate(timeout=5)
                pytest.fail(
                    f"Server failed to start within {TIMEOUT}s.\n"
                    f"stdout: {stdout.decode()}\n"
                    f"stderr: {stderr.decode()}"
                )

            base_url = f"http://{HOST}:{PORT}"
            yield base_url

        finally:
            # Clean up: kill the server
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


class TestSSECorsProduction:
    """
    Integration tests for SSE CORS using real production server.

    These tests exercise the actual handler.rs code path, NOT test_state.rs.
    They would FAIL if the SSE CORS fix in handler.rs is reverted.
    """

    def test_async_sse_has_cors_headers(self, sse_cors_server):
        """
        Test that async SSE responses include CORS headers.

        CRITICAL: This test verifies the production handler.rs fix.
        Without the fix, browsers would block EventSource connections.
        """
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{sse_cors_server}/sse-cors-async",
                headers={"Origin": "https://example.com"}
            )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

        # CRITICAL: Must have CORS headers from production handler.rs
        assert response.headers.get("access-control-allow-origin") == "https://example.com", \
            "Production SSE response missing Access-Control-Allow-Origin header"

        # Must have Vary: Origin when reflecting origin
        # httpx may return multiple Vary headers as separate entries, so check all
        vary_headers = response.headers.get_list("vary")
        all_vary = ", ".join(vary_headers).lower()
        assert "origin" in all_vary, \
            f"Production SSE response missing Vary: Origin header. Got: {vary_headers}"

    def test_sync_sse_has_cors_headers(self, sse_cors_server):
        """Test that sync SSE responses include CORS headers."""
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{sse_cors_server}/sse-cors-sync",
                headers={"Origin": "https://sync-app.com"}
            )

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "https://sync-app.com"

    def test_sse_cors_credentials(self, sse_cors_server):
        """Test that SSE responses include credentials header when configured."""
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{sse_cors_server}/sse-cors-credentials",
                headers={"Origin": "https://secure.com"}
            )

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "https://secure.com"
        assert response.headers.get("access-control-allow-credentials") == "true"

    def test_sse_cors_wildcard(self, sse_cors_server):
        """Test that SSE responses with wildcard CORS return '*'."""
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{sse_cors_server}/sse-cors-wildcard",
                headers={"Origin": "https://any-domain.com"}
            )

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "*"

    def test_sse_rejects_disallowed_origin(self, sse_cors_server):
        """Test that SSE responses reject disallowed origins."""
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{sse_cors_server}/sse-cors-async",
                headers={"Origin": "https://evil.com"}
            )

        assert response.status_code == 200
        # Must NOT have CORS headers for disallowed origin
        assert response.headers.get("access-control-allow-origin") is None

    def test_sse_without_cors_decorator(self, sse_cors_server):
        """Test that SSE without CORS decorator has no CORS headers."""
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{sse_cors_server}/sse-no-cors",
                headers={"Origin": "https://example.com"}
            )

        assert response.status_code == 200
        # No CORS decorator = no CORS headers
        assert response.headers.get("access-control-allow-origin") is None

    def test_sse_content_is_correct(self, sse_cors_server):
        """Test that SSE content is correctly streamed with CORS headers."""
        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{sse_cors_server}/sse-cors-async",
                headers={"Origin": "https://example.com"}
            )

        assert response.status_code == 200

        # Verify CORS headers present
        assert response.headers.get("access-control-allow-origin") == "https://example.com"

        # Verify SSE content
        content = response.content.decode()
        assert "data: message-0" in content
        assert "data: message-1" in content
        assert "data: message-2" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

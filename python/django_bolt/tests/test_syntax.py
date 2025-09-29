import asyncio
import threading
import time
import socket
import http.client
import json

import msgspec
import pytest

from django_bolt import BoltAPI, JSON, StreamingResponse
from django_bolt.param_functions import Query, Path, Header, Cookie, Depends, Form, File as FileParam
from django_bolt.responses import PlainText, HTML, Redirect, File, FileResponse
from django_bolt.exceptions import HTTPException
from django_bolt import _core as core


# Removed: run_server function no longer needed
# Server runs in subprocess via syntax_test_server.py


def http_request(method: str, host: str, port: int, path: str, body: bytes | None = None, headers: dict | None = None, timeout: int = None):
    conn = http.client.HTTPConnection(host, port, timeout=timeout or 2)
    try:
        conn.request(method, path, body=body, headers=headers or {})
        resp = conn.getresponse()
        data = resp.read()
        return resp.status, dict(resp.getheaders()), data
    finally:
        conn.close()


def http_get(host: str, port: int, path: str, timeout: int = None):
    return http_request("GET", host, port, path, timeout=timeout)


def http_put_json(host: str, port: int, path: str, data: dict):
    payload = json.dumps(data).encode()
    return http_request("PUT", host, port, path, body=payload, headers={"Content-Type": "application/json"})


def http_post(host: str, port: int, path: str):
    return http_request("POST", host, port, path)

def http_post_form(host: str, port: int, path: str, data: dict):
    from urllib.parse import urlencode
    payload = urlencode(data).encode()
    return http_request("POST", host, port, path, body=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})

def http_post_multipart(host: str, port: int, path: str, fields: dict, files: list[tuple[str, bytes, str]]):
    import uuid
    boundary = f"----bolt{uuid.uuid4().hex}"
    lines: list[bytes] = []
    for k, v in fields.items():
        lines.append(f"--{boundary}\r\n".encode())
        lines.append(f"Content-Disposition: form-data; name=\"{k}\"\r\n\r\n".encode())
        lines.append(str(v).encode())
        lines.append(b"\r\n")
    for name, content, filename in files:
        lines.append(f"--{boundary}\r\n".encode())
        lines.append(f"Content-Disposition: form-data; name=\"{name}\"; filename=\"{filename}\"\r\n".encode())
        lines.append(b"Content-Type: application/octet-stream\r\n\r\n")
        lines.append(content)
        lines.append(b"\r\n")
    lines.append(f"--{boundary}--\r\n".encode())
    body = b"".join(lines)
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    return http_request("POST", host, port, path, body=body, headers=headers)


def http_patch(host: str, port: int, path: str):
    return http_request("PATCH", host, port, path)


def http_delete(host: str, port: int, path: str):
    return http_request("DELETE", host, port, path)


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="module")
def server():
    """Start syntax test server in subprocess"""
    import sys
    import os
    from conftest import spawn_process, kill_process, wait_for_server

    host = "127.0.0.1"
    port = free_port()

    # Path to the standalone server script
    current_dir = os.path.dirname(__file__)
    server_script = os.path.join(current_dir, "syntax_test_server.py")

    # Start server in subprocess
    python_exec = sys.executable
    command = [python_exec, server_script, str(port)]

    print(f"\nStarting syntax test server on {host}:{port} in subprocess")
    process = spawn_process(command)

    # Wait for server to be ready
    if wait_for_server(host, port, timeout=15):
        print(f"✓ Syntax test server ready on {host}:{port}")
    else:
        print(f"⚠ Syntax test server may not have started properly")
        # Try to get error output
        try:
            stdout, stderr = process.communicate(timeout=1)
            if stderr:
                print(f"Server stderr: {stderr.decode()[:500]}")
        except:
            pass

    yield host, port

    # Cleanup: kill the server process
    print("\nStopping syntax test server")
    kill_process(process)
    try:
        process.wait(timeout=2)
    except:
        pass


def test_root(server):
    host, port = server
    status, headers, body = http_get(host, port, "/")
    assert status == 200
    assert json.loads(body) == {"ok": True}


def test_path_and_query_binding(server):
    host, port = server
    status, headers, body = http_get(host, port, "/items/42?q=hello")
    assert status == 200
    assert json.loads(body) == {"item_id": 42, "q": "hello"}


def test_bool_and_float_binding(server):
    host, port = server
    status, headers, body = http_get(host, port, "/types?b=true&f=1.25")
    assert status == 200
    assert json.loads(body) == {"b": True, "f": 1.25}


def test_body_decoding(server):
    host, port = server
    status, headers, body = http_put_json(host, port, "/items/5", {"name": "x", "price": 1.5, "is_offer": True})
    assert status == 200
    assert json.loads(body) == {"item_id": 5, "item_name": "x", "is_offer": True}


def test_response_types(server):
    host, port = server
    # str
    status, headers, body = http_get(host, port, "/str")
    assert status == 200
    assert body == b"hello"
    assert headers.get("content-type", "").startswith("text/plain")
    # bytes
    status, headers, body = http_get(host, port, "/bytes")
    assert status == 200
    assert body == b"abc"
    assert headers.get("content-type", "").startswith("application/octet-stream")


def test_json_response_status_and_headers(server):
    host, port = server
    status, headers, body = http_get(host, port, "/json")
    assert status == 201
    assert headers.get("x-test") == "1"
    assert json.loads(body) == {"x": 1}


def test_request_only_handler(server):
    host, port = server
    status, headers, body = http_get(host, port, "/req/9?y=z")
    assert status == 200
    assert json.loads(body) == {"p": "9", "q": "z"}


def test_methods(server):
    host, port = server
    status, headers, body = http_post(host, port, "/m")
    assert status == 200 and json.loads(body) == {"m": "post"}
    status, headers, body = http_patch(host, port, "/m")
    assert status == 200 and json.loads(body) == {"m": "patch"}
    status, headers, body = http_delete(host, port, "/m")
    assert status == 200 and json.loads(body) == {"m": "delete"}


def test_response_model_validation_ok(server):
    host, port = server
    status, headers, body = http_get(host, port, "/ok-list")
    assert status == 200
    data = json.loads(body)
    assert isinstance(data, list) and len(data) == 2
    assert data[0]["name"] == "a" and data[0]["price"] == 1.0


def test_response_model_validation_error(server):
    host, port = server
    status, headers, body = http_get(host, port, "/bad-list")
    # We currently surface server error (500) on validation problems
    assert status == 500
    assert b"Response validation error" in body


def test_return_annotation_validation_ok(server):
    host, port = server
    status, headers, body = http_get(host, port, "/anno-list")
    assert status == 200
    data = json.loads(body)
    assert isinstance(data, list) and data[0]["name"] == "c"


def test_return_annotation_validation_error(server):
    host, port = server
    status, headers, body = http_get(host, port, "/anno-bad")
    assert status == 500
    assert b"Response validation error" in body


def test_response_coercion_from_objects(server):
    host, port = server
    status, headers, body = http_get(host, port, "/coerce/mini")
    assert status == 200
    data = json.loads(body)
    assert data == [{"id": 1, "username": "a"}, {"id": 2, "username": "b"}]


def test_response_coercion_error_from_objects(server):
    host, port = server
    status, headers, body = http_get(host, port, "/coerce/mini-bad")
    assert status == 500
    assert b"Response validation error" in body


def test_response_model_overrides_return_annotation(server):
    host, port = server
    status, headers, body = http_get(host, port, "/both-override")
    assert status == 200
    data = json.loads(body)
    assert isinstance(data, list) and data[0]["name"] == "o"


def test_no_validation_without_types(server):
    host, port = server
    status, headers, body = http_get(host, port, "/no-validate")
    assert status == 200
    data = json.loads(body)
    # Should return as-is since neither annotation nor response_model provided
    assert data == [{"anything": 1, "extra": "ok"}]


def test_status_code_default(server):
    host, port = server
    status, headers, body = http_get(host, port, "/status-default")
    assert status == 201


def test_header_and_cookie(server):
    host, port = server
    status, headers, body = http_request("GET", host, port, "/header", headers={"x-test": "val"})
    assert status == 200 and body == b"val"
    # set cookie via header
    status, headers, body = http_request("GET", host, port, "/cookie", headers={"Cookie": "session=abc"})
    assert status == 200 and body == b"abc"


def test_http_exception(server):
    host, port = server
    status, headers, body = http_get(host, port, "/exc")
    assert status == 418
    assert headers.get("x-err") == "1"


def test_response_helpers(server):
    host, port = server
    status, headers, body = http_get(host, port, "/html")
    assert status == 200 and headers.get("content-type", "").startswith("text/html")
    status, headers, body = http_get(host, port, "/redirect")
    assert status == 302 and headers.get("location") == "/"
    status, headers, body = http_get(host, port, "/file")
    assert status == 200 and headers.get("content-type", "").startswith("text/")
    # FileResponse should also succeed and set content-disposition
    status, headers, body = http_get(host, port, "/fileresponse")
    assert status == 200
    assert headers.get("content-type", "").startswith("text/")
    assert "attachment;" in (headers.get("content-disposition", "").lower())


def test_streaming_plain(server):
    host, port = server
    status, headers, body = http_get(host, port, "/stream-plain")
    assert status == 200
    assert headers.get("content-type", "").startswith("text/plain")
    assert body == b"p0,p1,p2,"


def test_streaming_bytes_default_content_type(server):
    host, port = server
    status, headers, body = http_get(host, port, "/stream-bytes")
    assert status == 200
    assert headers.get("content-type", "").startswith("application/octet-stream")
    assert body == b"01"


def test_streaming_sse_headers(server):
    host, port = server
    status, headers, body = http_get(host, port, "/sse")
    assert status == 200
    assert headers.get("content-type", "").startswith("text/event-stream")
    # SSE-friendly headers are set by the server
    # Note: Connection header may be managed by the HTTP server automatically
    assert headers.get("x-accel-buffering", "").lower() == "no"
    # Body should contain multiple well-formed SSE lines
    text = body.decode()
    assert "event: message" in text
    assert "data: hello" in text
    assert "data: 1" in text
    assert ": comment" in text


def test_streaming_async_large(server):
    """Test async streaming with larger payloads."""
    host, port = server
    status, headers, body = http_get(host, port, "/stream-async-large")
    assert status == 200
    assert headers.get("content-type", "").startswith("application/octet-stream")
    
    # Should have 10 chunks
    lines = body.decode().strip().split('\n')
    assert len(lines) == 10
    
    # Check format of chunks
    for i, line in enumerate(lines):
        expected_prefix = f"chunk-{i:02d}-"
        assert line.startswith(expected_prefix)
        assert len(line) >= 109  # ~109 bytes per line (110 bytes per chunk with \n)
        assert line.endswith('x' * 100)


def test_streaming_async_mixed_types(server):
    """Test async streaming with different data types."""
    host, port = server
    status, headers, body = http_get(host, port, "/stream-async-mixed-types")
    assert status == 200
    assert headers.get("content-type", "").startswith("text/plain")
    
    # Check all data types are properly converted
    text = body.decode()
    expected_chunks = [
        "bytes-chunk\n",
        "string-chunk\n", 
        "bytearray-chunk\n",
        "memoryview-chunk\n"
    ]
    
    for expected in expected_chunks:
        assert expected in text


def test_streaming_async_vs_sync_compatibility(server):
    """Test that async and sync streaming produce the same results for equivalent data."""
    host, port = server
    
    # Get sync streaming result  
    sync_status, sync_headers, sync_body = http_get(host, port, "/stream-plain")
    
    # Get async streaming result
    async_status, async_headers, async_body = http_get(host, port, "/stream-async")
    
    # Both should succeed
    assert sync_status == 200
    assert async_status == 200
    
    # Both should be text/plain
    assert sync_headers.get("content-type", "").startswith("text/plain")
    assert async_headers.get("content-type", "").startswith("text/plain")
    
    # Content should be similar format (both have 3 items)
    sync_text = sync_body.decode()
    async_text = async_body.decode()
    
    # Both should have 3 comma-separated items
    assert len(sync_text.split(',')) == 4  # "p0,p1,p2," = 4 parts
    assert len(async_text.split(',')) == 4  # "async-0,async-1,async-2," = 4 parts


def test_async_bridge_endpoints_work(server):
    """Test that async SSE streaming works correctly."""
    host, port = server
    
    # Test the async SSE endpoint - this should expose the real bug
    status, headers, body = http_get(host, port, "/sse-async-test", timeout=5)
    assert status == 200, f"Async SSE endpoint failed with status {status}"
    assert len(body) > 0, f"Async SSE endpoint returned empty body, got {len(body)} bytes"
    # Check that we actually get SSE formatted data
    text = body.decode()
    assert "data: 0" in text, f"Expected SSE data not found in response: {text[:100]}"
    assert "data: 1" in text, f"Expected SSE data not found in response: {text[:100]}"


def test_form_and_file(server):
    host, port = server
    status, headers, body = http_post_form(host, port, "/form-urlencoded", {"a": "x", "b": 3})
    assert status == 200 and json.loads(body) == {"a": "x", "b": 3}
    status, headers, body = http_post_multipart(host, port, "/upload", {"note": "hi"}, [("file", b"abc", "a.txt"), ("file", b"def", "b.txt")])
    data = json.loads(body)
    assert status == 200 and data["count"] == 2 and set(data["names"]) == {"a.txt", "b.txt"}



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


def run_server(api: BoltAPI, host: str, port: int):
    # The routes in api._routes are already converted to matchit style,
    # so we shouldn't convert them again
    routes = []
    for m, p, hid, h in api._routes:
        routes.append((m, p, hid, h))
    core.register_routes(routes)
    core.start_server_async(api._dispatch, host, port)


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
    api = BoltAPI()

    class Item(msgspec.Struct):
        name: str
        price: float
        is_offer: bool | None = None

    @api.get("/")
    async def root():
        return {"ok": True}

    @api.get("/items/{item_id}")
    async def get_item(item_id: int, q: str | None = None):
        return {"item_id": item_id, "q": q}

    @api.get("/types")
    async def get_types(b: bool | None = None, f: float | None = None):
        return {"b": b, "f": f}

    @api.put("/items/{item_id}")
    async def put_item(item_id: int, item: Item):
        return {"item_id": item_id, "item_name": item.name, "is_offer": item.is_offer}

    @api.get("/str")
    async def ret_str():
        return "hello"

    @api.get("/bytes")
    async def ret_bytes():
        return b"abc"

    @api.get("/json")
    async def ret_json():
        return JSON({"x": 1}, status_code=201, headers={"X-Test": "1"})

    @api.get("/req/{x}")
    async def req_only(req):
        return {"p": req["params"].get("x"), "q": req["query"].get("y")}

    @api.post("/m")
    async def post_m():
        return {"m": "post"}

    @api.patch("/m")
    async def patch_m():
        return {"m": "patch"}

    @api.delete("/m")
    async def delete_m():
        return {"m": "delete"}

    # ----- Response coercion from objects to msgspec.Struct -----
    class Mini(msgspec.Struct):
        id: int
        username: str

    class Model:
        def __init__(self, id: int, username: str | None):
            self.id = id
            self.username = username

    @api.get("/coerce/mini", response_model=list[Mini])
    async def coerce_mini() -> list[Mini]:
        return [Model(1, "a"), Model(2, "b")]

    @api.get("/coerce/mini-bad", response_model=list[Mini])
    async def coerce_mini_bad() -> list[Mini]:
        # username None should fail str requirement
        return [Model(1, None)]

    # Response model validation via decorator
    @api.get("/ok-list", response_model=list[Item])
    async def ok_list():
        return [
            {"name": "a", "price": 1.0, "is_offer": True},
            {"name": "b", "price": 2.0, "is_offer": False},
        ]

    @api.get("/bad-list", response_model=list[Item])
    async def bad_list():
        # Missing required field 'price' to trigger validation error
        return [
            {"name": "x", "is_offer": True},
        ]

    # Response type via return annotation
    @api.get("/anno-list")
    async def anno_list() -> list[Item]:
        return [Item(name="c", price=3.0, is_offer=None)]

    @api.get("/anno-bad")
    async def anno_bad() -> list[Item]:
        # Wrong shape; missing required 'price'
        return [{"name": "d"}]

    # response_model should override return annotation
    @api.get("/both-override", response_model=list[Item])
    async def both_override() -> list[str]:  # intentionally wrong annotation, should be ignored
        return [{"name": "o", "price": 1.0, "is_offer": False}]

    # No types at all -> no validation, return as-is
    @api.get("/no-validate")
    async def no_validate():
        return [{"anything": 1, "extra": "ok"}]

    # ---- New syntax parity endpoints ----
    # Decorator status_code default
    @api.get("/status-default", status_code=201)
    async def status_default():
        return {"ok": True}

    # Header and Cookie extraction
    @api.get("/headers-cookies")
    async def headers_cookies(
        agent: str = Depends(lambda user_agent: user_agent),
    ):
        return {"ok": True}

    # Explicit Header/Cookie parameters using Annotated
    from typing import Annotated

    @api.get("/header")
    async def get_header(x: Annotated[str, Header(alias="x-test")]):
        return PlainText(x)

    @api.get("/cookie")
    async def get_cookie(val: Annotated[str, Cookie(alias="session")]):
        return PlainText(val)

    # HTTPException
    @api.get("/exc")
    async def raise_exc():
        raise HTTPException(418, {"detail": "teapot"}, headers={"X-Err": "1"})

    # Response helpers
    @api.get("/html")
    async def get_html():
        return HTML("<h1>Hi</h1>")

    @api.get("/redirect")
    async def get_redirect():
        return Redirect("/", status_code=302)

    # File response (serve this test file itself)
    import os
    THIS_FILE = os.path.abspath(__file__)

    @api.get("/file")
    async def get_file():
        return File(THIS_FILE, filename="test_syntax.py")

    # FileResponse streamed by Actix NamedFile
    @api.get("/fileresponse")
    async def get_fileresponse():
        return FileResponse(THIS_FILE, filename="test_syntax.py")

    # Streaming endpoints
    @api.get("/stream-plain")
    async def stream_plain():
        def gen():
            for i in range(3):
                yield f"p{i},"
        return StreamingResponse(gen, media_type="text/plain")

    @api.get("/stream-bytes")
    async def stream_bytes():
        def gen():
            for i in range(2):
                yield str(i).encode()
        return StreamingResponse(gen)

    @api.get("/sse")
    async def stream_sse():
        def gen():
            yield "event: message\ndata: hello\n\n"
            yield "data: 1\n\n"
            yield ": comment\n\n"
        return StreamingResponse(gen, media_type="text/event-stream")

    # Async streaming endpoints to test the new async channel bridge
    @api.get("/stream-async")
    async def stream_async():
        async def async_gen():
            for i in range(3):
                await asyncio.sleep(0.001)  # Small delay to simulate async work
                yield f"async-{i},".encode()
        return StreamingResponse(async_gen(), media_type="text/plain")

    @api.get("/stream-async-sse")
    async def stream_async_sse():
        async def async_gen():
            yield "event: start\ndata: beginning\n\n"
            await asyncio.sleep(0.001)
            yield "event: message\ndata: async data\n\n"
            await asyncio.sleep(0.001)
            yield "event: end\ndata: finished\n\n"
        return StreamingResponse(async_gen(), media_type="text/event-stream")

    @api.get("/stream-async-large")
    async def stream_async_large():
        """Test async streaming with larger payload to test channel efficiency."""
        async def async_gen():
            for i in range(10):
                await asyncio.sleep(0.001)
                chunk = f"chunk-{i:02d}-{'x' * 100}\n".encode()  # ~110 bytes per chunk
                yield chunk
        return StreamingResponse(async_gen(), media_type="application/octet-stream")

    @api.get("/stream-async-mixed-types")
    async def stream_async_mixed_types():
        """Test async streaming with different data types."""
        async def async_gen():
            yield b"bytes-chunk\n"
            await asyncio.sleep(0.001)
            yield "string-chunk\n"
            await asyncio.sleep(0.001)
            yield bytearray(b"bytearray-chunk\n")
            await asyncio.sleep(0.001)
            yield memoryview(b"memoryview-chunk\n")
        return StreamingResponse(async_gen(), media_type="text/plain")

    @api.get("/stream-async-error")
    async def stream_async_error():
        """Test async streaming error handling."""
        async def async_gen():
            yield b"chunk1\n"
            await asyncio.sleep(0.001)
            yield b"chunk2\n"
            await asyncio.sleep(0.001)
            raise ValueError("Simulated async error")
        return StreamingResponse(async_gen(), media_type="text/plain")

    # Additional endpoints for forms and file upload
    from typing import Annotated
    @api.post("/form-urlencoded")
    async def form_urlencoded(a: Annotated[str, Form()], b: Annotated[int, Form()]):
        return {"a": a, "b": b}

    @api.post("/upload")
    async def upload(files: Annotated[list[dict], FileParam(alias="file")]):
        # return only metadata
        return {"count": len(files), "names": [f.get("filename") for f in files]}

    # Add the real problematic async streaming endpoints from the actual server
    @api.get("/sse-async-test")
    async def sse_async_test():
        async def agen():
            for i in range(3):
                yield f"data: {i}\n\n"
                await asyncio.sleep(0)
        return StreamingResponse(agen(), media_type="text/event-stream")

    @api.post("/v1/chat/completions-async-test")
    async def chat_completions_async_test(payload: dict):
        if payload.get("stream", True):
            async def agen():
                for i in range(payload.get("n_chunks", 2)):
                    data = {"chunk": i, "content": " hello"}
                    yield f"data: {json.dumps(data)}\n\n"
                    await asyncio.sleep(0)
                yield "data: [DONE]\n\n"
            return StreamingResponse(agen(), media_type="text/event-stream")
        return {"non_streaming": True}

    host, port = "127.0.0.1", free_port()
    t = threading.Thread(target=run_server, args=(api, host, port), daemon=True)
    t.start()
    time.sleep(0.5)
    return host, port


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



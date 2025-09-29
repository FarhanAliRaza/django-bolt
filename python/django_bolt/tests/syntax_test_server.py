#!/usr/bin/env python3
"""
Standalone server for syntax/core integration tests.
Runs in a subprocess to avoid router initialization conflicts.
"""
import sys
import os
import asyncio
import json

# Ensure we can import from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Configure Django before importing anything else
from django.conf import settings
if not settings.configured:
    settings.configure(
        SECRET_KEY='test-secret-key-for-syntax-tests',
        DEBUG=True,
        INSTALLED_APPS=['django_bolt'],
    )

def create_test_api():
    """Create the test API with all routes"""
    import msgspec
    from django_bolt import BoltAPI, JSON, StreamingResponse
    from django_bolt.param_functions import Query, Path, Header, Cookie, Depends, Form, File as FileParam
    from django_bolt.responses import PlainText, HTML, Redirect, File, FileResponse
    from django_bolt.exceptions import HTTPException
    from typing import Annotated

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

    # Response coercion from objects to msgspec.Struct
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
        return [Model(1, None)]

    @api.get("/ok-list", response_model=list[Item])
    async def ok_list():
        return [
            {"name": "a", "price": 1.0, "is_offer": True},
            {"name": "b", "price": 2.0, "is_offer": False},
        ]

    @api.get("/bad-list", response_model=list[Item])
    async def bad_list():
        return [{"name": "x", "is_offer": True}]

    @api.get("/anno-list")
    async def anno_list() -> list[Item]:
        return [Item(name="c", price=3.0, is_offer=None)]

    @api.get("/anno-bad")
    async def anno_bad() -> list[Item]:
        return [{"name": "d"}]

    @api.get("/both-override", response_model=list[Item])
    async def both_override() -> list[str]:
        return [{"name": "o", "price": 1.0, "is_offer": False}]

    @api.get("/no-validate")
    async def no_validate():
        return [{"anything": 1, "extra": "ok"}]

    @api.get("/status-default", status_code=201)
    async def status_default():
        return {"ok": True}

    @api.get("/headers-cookies")
    async def headers_cookies(agent: str = Depends(lambda user_agent: user_agent)):
        return {"ok": True}

    @api.get("/header")
    async def get_header(x: Annotated[str, Header(alias="x-test")]):
        return PlainText(x)

    @api.get("/cookie")
    async def get_cookie(val: Annotated[str, Cookie(alias="session")]):
        return PlainText(val)

    @api.get("/exc")
    async def raise_exc():
        raise HTTPException(418, {"detail": "teapot"}, headers={"X-Err": "1"})

    @api.get("/html")
    async def get_html():
        return HTML("<h1>Hi</h1>")

    @api.get("/redirect")
    async def get_redirect():
        return Redirect("/", status_code=302)

    THIS_FILE = os.path.abspath(__file__)

    @api.get("/file")
    async def get_file():
        return File(THIS_FILE, filename="syntax_test_server.py")

    @api.get("/fileresponse")
    async def get_fileresponse():
        return FileResponse(THIS_FILE, filename="syntax_test_server.py")

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

    @api.get("/stream-async")
    async def stream_async():
        async def async_gen():
            for i in range(3):
                await asyncio.sleep(0.001)
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
        async def async_gen():
            for i in range(10):
                await asyncio.sleep(0.001)
                chunk = f"chunk-{i:02d}-{'x' * 100}\n".encode()
                yield chunk
        return StreamingResponse(async_gen(), media_type="application/octet-stream")

    @api.get("/stream-async-mixed-types")
    async def stream_async_mixed_types():
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
        async def async_gen():
            yield b"chunk1\n"
            await asyncio.sleep(0.001)
            yield b"chunk2\n"
            await asyncio.sleep(0.001)
            raise ValueError("Simulated async error")
        return StreamingResponse(async_gen(), media_type="text/plain")

    @api.post("/form-urlencoded")
    async def form_urlencoded(a: Annotated[str, Form()], b: Annotated[int, Form()]):
        return {"a": a, "b": b}

    @api.post("/upload")
    async def upload(files: Annotated[list[dict], FileParam(alias="file")]):
        return {"count": len(files), "names": [f.get("filename") for f in files]}

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

    return api


if __name__ == "__main__":
    # Get port from command line or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    host = "127.0.0.1"

    # Create and serve API
    api = create_test_api()
    print(f"Starting syntax test server on {host}:{port}", flush=True)
    api.serve(host=host, port=port)
import threading
import time
import socket
import http.client
import json

import msgspec
import pytest

from django_bolt import BoltAPI, JSON
from django_bolt import _core as core


def run_server(api: BoltAPI, host: str, port: int):
    core.register_routes([(m, p, hid, h) for (m, p, hid, h) in api._routes])
    core.start_server_async(api._dispatch, host, port)


def http_request(method: str, host: str, port: int, path: str, body: bytes | None = None, headers: dict | None = None):
    conn = http.client.HTTPConnection(host, port, timeout=2)
    try:
        conn.request(method, path, body=body, headers=headers or {})
        resp = conn.getresponse()
        data = resp.read()
        return resp.status, dict(resp.getheaders()), data
    finally:
        conn.close()


def http_get(host: str, port: int, path: str):
    return http_request("GET", host, port, path)


def http_put_json(host: str, port: int, path: str, data: dict):
    payload = json.dumps(data).encode()
    return http_request("PUT", host, port, path, body=payload, headers={"Content-Type": "application/json"})


def http_post(host: str, port: int, path: str):
    return http_request("POST", host, port, path)


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



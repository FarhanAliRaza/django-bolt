"""CodSpeed benchmarks of the production request path.

Each case sends one request of `scripts/benchmark.sh` to the real `runbolt`
server. The server is the example project, so the routes are the same as in
BENCHMARK.md. The request bytes are built outside the measured region.

One measured round sends REQUESTS_PER_ROUND requests, so a count is for the
round. Background work of the server, for example the timer that updates the
Date header, then has a small share of the count. With one request per round,
one timer tick changes it by 5-15%.

Each response of a round must have the expected status. The body of the last
response must pass the check of its case. A broken route then fails, and does
not show as a faster one.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass

import pytest
from conftest import Connection, build_request
from pytest_codspeed.plugin import BenchmarkFixture

WARMUP_REQUESTS = 20
REQUESTS_PER_ROUND = 100

JSON = (("Content-Type", "application/json"),)
FORM = (("Content-Type", "application/x-www-form-urlencoded"),)
BOUNDARY = "----BoltBenchmark"
MULTIPART = (("Content-Type", f"multipart/form-data; boundary={BOUNDARY}"),)


def multipart(*parts: tuple[str, str, str | None]) -> bytes:
    """Encode (field name, value, file name) parts with CRLF line endings."""
    out = []
    for name, value, filename in parts:
        out.append(f"--{BOUNDARY}\r\n")
        if filename is None:
            out.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n')
        else:
            out.append(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n')
            out.append("Content-Type: text/plain\r\n\r\n")
        out.append(f"{value}\r\n")
    out.append(f"--{BOUNDARY}--\r\n")
    return "".join(out).encode()


def json_equals(expected: object) -> Callable[[bytes], bool]:
    return lambda body: json.loads(body) == expected


def users(fields: set[str]) -> Callable[[bytes], bool]:
    """Ten seeded users, each with exactly these fields."""
    return lambda body: (
        len(rows := json.loads(body)) == 10
        and all(row.keys() == fields and row["username"].startswith("user") for row in rows)
    )


def has_length(length: int) -> Callable[[bytes], bool]:
    return lambda body: len(body) == length


def empty(body: bytes) -> bool:
    return body == b""


def ten_kb_json(body: bytes) -> bool:
    rows = json.loads(body)
    return len(body) > 10_000 and all("_id" in row for row in rows)


def bench_user(body: bytes) -> bool:
    return json.loads(body)["username"] == "benchuser"


def jwt_context(body: bytes) -> bool:
    context = json.loads(body)
    return context["auth_backend"] == "jwt" and context["auth_claims"]["sub"] == context["user_id"]


def union_feed(body: bytes) -> bool:
    items = json.loads(body)
    return len(items) == 100 and {item["type"] for item in items} == {"post", "comment", "like"}


FULL_USER = {"id", "username", "email", "first_name", "last_name", "is_active"}
FORM_LIST = json_equals({"name": "Bench", "tag_count": 4, "count_sum": 6})


@dataclass(frozen=True)
class Case:
    id: str
    method: str
    path: str
    expect: Callable[[bytes], bool]
    headers: tuple[tuple[str, str], ...] = ()
    body: bytes = b""
    status: int = 200
    auth: bool = False


CASES = (
    Case("root", "GET", "/", json_equals({"message": "Hello World"})),
    Case("10k-json-async", "GET", "/10k-json", ten_kb_json),
    Case("10k-json-sync", "GET", "/sync-10k-json", ten_kb_json),
    Case("header", "GET", "/header", lambda body: body == b"val", (("x-test", "val"),)),
    Case("cookie", "GET", "/cookie", lambda body: body == b"abc", (("Cookie", "session=abc"),)),
    Case("exception", "GET", "/exc", json_equals({"detail": "Not found"}), status=404),
    # Errors that the Rust core builds, with no Python call: a route miss and a guard 401.
    Case("route-miss", "GET", "/no-such-route", json_equals({"detail": "Not Found"}), status=404),
    Case("auth-401", "GET", "/auth/me", json_equals({"detail": "Authentication required"}), status=401),
    Case("html", "GET", "/html", lambda body: body == b"<h1>Hello</h1>"),
    Case("redirect", "GET", "/redirect", empty, status=302),
    Case("file-static", "GET", "/file-static", lambda body: body.startswith(b"from __future__ import annotations")),
    Case("static-1k", "GET", "/static/bench/asset_1k.css", has_length(1024)),
    Case("static-1k-head", "HEAD", "/static/bench/asset_1k.css", empty),
    Case("static-100k", "GET", "/static/bench/asset_100k.js", has_length(102_400)),
    Case("static-miss", "GET", "/static/bench/missing.css", lambda body: body == b"File not found", status=404),
    Case("media-1k", "GET", "/media/bench/upload_1k.bin", has_length(1024)),
    Case("media-100k", "GET", "/media/bench/upload_100k.bin", has_length(102_400)),
    Case("auth-me", "GET", "/auth/me", bench_user, auth=True),
    Case("auth-context", "GET", "/auth/context", jwt_context, auth=True),
    Case("path-int", "GET", "/items/12345", json_equals({"item_id": 12345, "q": None})),
    Case("path-query", "GET", "/items/1?q=hello", json_equals({"item_id": 1, "q": "hello"})),
    Case(
        "put-json",
        "PUT",
        "/items/1",
        json_equals({"item_name": "bench", "item_id": 1}),
        JSON,
        b'{"name":"bench","price":1.23,"is_offer":true}',
    ),
    Case("users-full10-async", "GET", "/users/full10", users(FULL_USER)),
    Case("users-full10-sync", "GET", "/users/sync-full10", users(FULL_USER)),
    Case("users-mini10-async", "GET", "/users/mini10", users({"id", "username"})),
    Case("cbv-get", "GET", "/cbv-simple", json_equals({"message": "Hello from APIView"})),
    Case(
        "cbv-post",
        "POST",
        "/cbv-simple",
        json_equals({"name": "bench", "price": 1.23, "cbv": True}),
        JSON,
        b'{"name":"bench","price":1.23,"is_offer":true}',
    ),
    Case("cbv-items-get", "GET", "/cbv-items/1?q=test", json_equals({"item_id": 1, "q": "test", "cbv": True})),
    Case(
        "cbv-items-put",
        "PUT",
        "/cbv-items/1",
        json_equals({"item_name": "updated-item", "item_id": 1, "cbv": True}),
        JSON,
        b'{"name":"updated-item","price":79.99,"is_offer":true}',
    ),
    Case(
        "form",
        "POST",
        "/form",
        json_equals({"name": "TestUser", "age": 25, "email": "test@example.com"}),
        FORM,
        b"name=TestUser&age=25&email=test%40example.com",
    ),
    Case(
        "upload",
        "POST",
        "/upload",
        json_equals({"uploaded": 2, "files": [{"name": "test1.txt", "size": 27}, {"name": "test2.txt", "size": 27}]}),
        MULTIPART,
        multipart(
            ("file", "This is test file content 1", "test1.txt"),
            ("file", "This is test file content 2", "test2.txt"),
        ),
    ),
    Case(
        "form-list-urlencoded",
        "POST",
        "/form-list",
        FORM_LIST,
        FORM,
        b"name=Bench&tags=red&tags=green&tags=blue&tags=yellow&counts=1&counts=2&counts=3",
    ),
    Case(
        "form-list-multipart",
        "POST",
        "/form-list",
        FORM_LIST,
        MULTIPART,
        multipart(
            ("name", "Bench", None),
            *(("tags", tag, None) for tag in ("red", "green", "blue", "yellow")),
            *(("counts", count, None) for count in ("1", "2", "3")),
        ),
    ),
    Case("django-middleware", "GET", "/middleware/demo", lambda body: b"Middleware &amp; Messages Demo" in body),
    Case(
        "json-parse",
        "POST",
        "/bench/parse",
        json_equals({"ok": True, "n": 1, "count": 100}),
        JSON,
        b'{"title":"bench","count":100,"items":[{"name":"a","price":1.0,"is_offer":true}]}',
    ),
    Case("union-feed", "GET", "/feed", union_feed),
)


def send_round(conn: Connection, raw: bytes, head: bool, status: int) -> bytes:
    """Send the request REQUESTS_PER_ROUND times. Return the last body.

    Each response must have the expected status.
    """
    for _ in range(REQUESTS_PER_ROUND - 1):
        got, body = conn.send(raw, head=head)
        if got != status:
            raise AssertionError(f"Expected status {status}, got {got}: {body[:200]!r}")
    got, body = conn.send(raw, head=head)
    if got != status:
        raise AssertionError(f"Expected status {status}, got {got}: {body[:200]!r}")
    return body


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_http(bench_server: Connection, auth_token: str, benchmark: BenchmarkFixture, case: Case) -> None:
    headers = case.headers + ((("Authorization", f"Bearer {auth_token}"),) if case.auth else ())
    raw = build_request(case.method, case.path, headers, case.body)
    head = case.method == "HEAD"
    # Warm the route, so the measured run does not count lazy setup and
    # interpreter specialization.
    for _ in range(WARMUP_REQUESTS):
        bench_server.send(raw, head=head)

    body = benchmark(send_round, bench_server, raw, head, case.status)

    assert case.expect(body), body[:500]

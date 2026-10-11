"""CodSpeed benchmarks of the production request path.

Each case sends one request of `scripts/benchmark.sh` to the real `runbolt`
server. The server is the example project, so the routes are the same as in
BENCHMARK.md. The request bytes are built outside the measured region.

One measured round sends many requests. Background work of the server, for
example the timer that updates the Date header, then has a small share of
the count. With one request per round, one timer tick changes it by 5-15%.
"""

from __future__ import annotations

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


@dataclass(frozen=True)
class Case:
    id: str
    method: str
    path: str
    headers: tuple[tuple[str, str], ...] = ()
    body: bytes = b""
    status: int = 200
    auth: bool = False


CASES = (
    Case("root", "GET", "/"),
    Case("10k-json-async", "GET", "/10k-json"),
    Case("10k-json-sync", "GET", "/sync-10k-json"),
    Case("header", "GET", "/header", (("x-test", "val"),)),
    Case("cookie", "GET", "/cookie", (("Cookie", "session=abc"),)),
    Case("exception", "GET", "/exc", status=404),
    Case("html", "GET", "/html"),
    Case("redirect", "GET", "/redirect", status=302),
    Case("file-static", "GET", "/file-static"),
    Case("static-1k", "GET", "/static/bench/asset_1k.css"),
    Case("static-1k-head", "HEAD", "/static/bench/asset_1k.css"),
    Case("static-100k", "GET", "/static/bench/asset_100k.js"),
    Case("static-miss", "GET", "/static/bench/missing.css", status=404),
    Case("media-1k", "GET", "/media/bench/upload_1k.bin"),
    Case("media-100k", "GET", "/media/bench/upload_100k.bin"),
    Case("auth-me", "GET", "/auth/me", auth=True),
    Case("auth-context", "GET", "/auth/context", auth=True),
    Case("path-int", "GET", "/items/12345"),
    Case("path-query", "GET", "/items/1?q=hello"),
    Case("put-json", "PUT", "/items/1", JSON, b'{"name":"bench","price":1.23,"is_offer":true}'),
    Case("users-full10-async", "GET", "/users/full10"),
    Case("users-full10-sync", "GET", "/users/sync-full10"),
    Case("users-mini10-async", "GET", "/users/mini10"),
    Case("cbv-get", "GET", "/cbv-simple"),
    Case("cbv-post", "POST", "/cbv-simple", JSON, b'{"name":"bench","price":1.23,"is_offer":true}'),
    Case("cbv-items-get", "GET", "/cbv-items/1?q=test"),
    Case("cbv-items-put", "PUT", "/cbv-items/1", JSON, b'{"name":"updated-item","price":79.99,"is_offer":true}'),
    Case("form", "POST", "/form", FORM, b"name=TestUser&age=25&email=test%40example.com"),
    Case(
        "upload",
        "POST",
        "/upload",
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
        FORM,
        b"name=Bench&tags=red&tags=green&tags=blue&tags=yellow&counts=1&counts=2&counts=3",
    ),
    Case(
        "form-list-multipart",
        "POST",
        "/form-list",
        MULTIPART,
        multipart(
            ("name", "Bench", None),
            *(("tags", tag, None) for tag in ("red", "green", "blue", "yellow")),
            *(("counts", count, None) for count in ("1", "2", "3")),
        ),
    ),
    Case("django-middleware", "GET", "/middleware/demo"),
    Case(
        "json-parse",
        "POST",
        "/bench/parse",
        JSON,
        b'{"title":"bench","count":100,"items":[{"name":"a","price":1.0,"is_offer":true}]}',
    ),
    Case("union-feed", "GET", "/feed"),
)


def send_round(conn: Connection, raw: bytes, head: bool) -> tuple[int, bytes]:
    """Send the request REQUESTS_PER_ROUND times. Return the last response."""
    for _ in range(REQUESTS_PER_ROUND - 1):
        conn.send(raw, head=head)
    return conn.send(raw, head=head)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_http(bench_server: Connection, auth_token: str, benchmark: BenchmarkFixture, case: Case) -> None:
    headers = case.headers + ((("Authorization", f"Bearer {auth_token}"),) if case.auth else ())
    raw = build_request(case.method, case.path, headers, case.body)
    head = case.method == "HEAD"
    # Warm the route, so the measured run does not count lazy setup and
    # interpreter specialization.
    for _ in range(WARMUP_REQUESTS):
        bench_server.send(raw, head=head)

    status, body = benchmark(send_round, bench_server, raw, head)

    assert status == case.status, body

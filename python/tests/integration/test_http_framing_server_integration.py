"""A real server rejects HTTP/1 requests whose framing is ambiguous.

TestClient does not parse HTTP, so these tests send raw bytes to runbolt. A
front proxy and Bolt must find the same request boundaries. If two parsers can
split one byte stream in two ways, an attacker can smuggle a request.
"""

from __future__ import annotations

import socket

import pytest

from .apps import app_module

pytestmark = pytest.mark.server_integration

_BODY = b'{"data":"x"}'
_CHUNKED_BODY = b"%x\r\n%s\r\n0\r\n\r\n" % (len(_BODY), _BODY)


def _send(server, raw: bytes) -> bytes:
    """Send the raw request on a new connection and return the reply up to EOF."""
    with socket.create_connection((server.host, server.port), timeout=5) as sock:
        sock.sendall(raw)
        chunks = []
        while chunk := sock.recv(65536):
            chunks.append(chunk)
    return b"".join(chunks)


def _status_line(reply: bytes) -> bytes:
    return reply.split(b"\r\n", 1)[0]


def test_content_length_with_chunked_gets_400(make_server_project):
    """Content-Length and Transfer-Encoding: chunked together give 400."""
    project = make_server_project(api_module=app_module("payload_sink"))
    with project.start() as server:
        host = server.host.encode()
        chunked = _send(
            server,
            b"POST /sink HTTP/1.1\r\nHost: %s\r\nContent-Type: application/json\r\n"
            b"Transfer-Encoding: chunked\r\nConnection: close\r\n\r\n%s" % (host, _CHUNKED_BODY),
        )
        ambiguous = _send(
            server,
            b"POST /sink HTTP/1.1\r\nHost: %s\r\nContent-Type: application/json\r\n"
            b"Content-Length: %d\r\nTransfer-Encoding: chunked\r\nConnection: close\r\n\r\n%s"
            % (host, len(_CHUNKED_BODY), _CHUNKED_BODY),
        )
    assert _status_line(chunked) == b"HTTP/1.1 200 OK", chunked[:200]
    assert _status_line(ambiguous) == b"HTTP/1.1 400 Bad Request", ambiguous[:200]


@pytest.mark.parametrize(
    "host_lines",
    [b"", b"Host: a.example\r\nHost: b.example\r\n"],
    ids=["missing", "duplicate"],
)
def test_http11_request_needs_one_host_header(make_server_project, host_lines):
    """HTTP/1.1 needs exactly one Host header. HTTP/1.0 needs none."""
    project = make_server_project(api_module=app_module("payload_sink"))
    with project.start() as server:
        http10 = _send(server, b"GET /health HTTP/1.0\r\n\r\n")
        http11 = _send(server, b"GET /health HTTP/1.1\r\n%sConnection: close\r\n\r\n" % host_lines)
    assert _status_line(http10).endswith(b" 200 OK"), http10[:200]
    assert _status_line(http11) == b"HTTP/1.1 400 Bad Request", http11[:200]

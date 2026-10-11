"""CodSpeed harness: the production server of the example project, in this process.

`runbolt` starts the Actix server in a background thread. CodSpeed simulation
counts the CPU instructions of all threads in the measured region. Thus each
benchmark measures the server work, and the small cost of the raw socket client.
Simulation does not count the time in system calls, for example socket I/O.

The server keeps global state, so one server serves the whole session. The
database and the static root are in a temporary directory (bench_settings.py).
"""

from __future__ import annotations

import os
import signal
import socket
import sys
import tempfile
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "example"
STARTUP_TIMEOUT = 300  # seconds; startup under valgrind is slow
SHUTDOWN_TIMEOUT = 60
# A blocked socket call fails after this time, so a deadlocked server cannot
# hang the run. It is long, because a request under valgrind is slow.
SOCKET_TIMEOUT = float(os.environ.get("BOLT_BENCH_SOCKET_TIMEOUT", "120"))


class Connection:
    """A keep-alive HTTP/1.1 client on a raw socket.

    http.client costs more instructions than the server work for a small
    response, so the benchmarks use this client.
    """

    def __init__(self, port: int) -> None:
        self.port = port
        self.sock = socket.create_connection(("127.0.0.1", port), timeout=SOCKET_TIMEOUT)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.buffer = b""

    def send(self, raw: bytes, *, head: bool = False) -> tuple[int, bytes]:
        """Send one prebuilt request. Return the status and the body."""
        self.sock.sendall(raw)
        while b"\r\n\r\n" not in self.buffer:
            self._recv()
        header_block, self.buffer = self.buffer.split(b"\r\n\r\n", 1)
        lines = header_block.split(b"\r\n")
        status = int(lines[0].split(b" ", 2)[1])
        length = None
        for line in lines[1:]:
            name, _, value = line.partition(b":")
            if name.lower() == b"content-length":
                length = int(value)
        if head:
            return status, b""
        if length is None:
            raise AssertionError(f"Response has no Content-Length: {header_block!r}")
        if len(self.buffer) >= length:
            body, self.buffer = self.buffer[:length], self.buffer[length:]
            return status, body
        # Receive the rest into one buffer of the body size. The kernel splits
        # a large body differently on each run, and a join of the parts would
        # copy a different number of bytes.
        body = bytearray(length)
        view = memoryview(body)
        filled = len(self.buffer)
        view[:filled] = self.buffer
        self.buffer = b""
        while filled < length:
            count = self.sock.recv_into(view[filled:])
            if not count:
                raise ConnectionError("The server closed the connection")
            filled += count
        return status, bytes(body)

    def _recv(self) -> None:
        chunk = self.sock.recv(65536)
        if not chunk:
            raise ConnectionError("The server closed the connection")
        self.buffer += chunk

    def close(self) -> None:
        self.sock.close()


def build_request(method: str, path: str, headers: tuple[tuple[str, str], ...] = (), body: bytes = b"") -> bytes:
    """Encode a request one time, outside the measured region."""
    lines = [f"{method} {path} HTTP/1.1", "Host: 127.0.0.1"]
    lines += [f"{name}: {value}" for name, value in headers]
    if body:
        lines.append(f"Content-Length: {len(body)}")
    return ("\r\n".join(lines) + "\r\n\r\n").encode() + body


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _run_server(port: int, errors: list[BaseException]) -> None:
    from django.core.management import call_command  # noqa: PLC0415

    try:
        call_command("runbolt", "--host", "127.0.0.1", "--port", str(port), "--processes", "1", "--workers", "1")
    except BaseException as exc:
        errors.append(exc)
        raise


def _wait_until_ready(port: int, thread: threading.Thread, errors: list[BaseException]) -> Connection:
    deadline = time.monotonic() + STARTUP_TIMEOUT
    while time.monotonic() < deadline:
        if not thread.is_alive():
            raise RuntimeError("runbolt stopped during startup") from (errors[0] if errors else None)
        try:
            conn = Connection(port)
        except OSError:
            time.sleep(0.1)
            continue
        status, _ = conn.send(build_request("GET", "/"))
        if status == 200:
            return conn
        conn.close()
        raise RuntimeError(f"GET / returned {status} at startup")
    raise RuntimeError(f"runbolt did not accept connections within {STARTUP_TIMEOUT} s")


def _stop_server(thread: threading.Thread) -> None:
    """Stop runbolt with SIGTERM, as in production.

    A running server keeps the executor threads busy, and the interpreter
    waits for them at exit.
    """
    if not thread.is_alive():
        return
    os.kill(os.getpid(), signal.SIGTERM)
    thread.join(SHUTDOWN_TIMEOUT)
    if thread.is_alive():
        raise RuntimeError(f"runbolt did not stop within {SHUTDOWN_TIMEOUT} s of SIGTERM")


@pytest.fixture(scope="session")
def bench_server() -> Iterator[Connection]:
    """Prepare the example project like `just save-bench`, then start runbolt."""
    with tempfile.TemporaryDirectory(prefix="bolt_bench_") as bench_dir:
        sys.path.insert(0, str(EXAMPLE_DIR))
        os.environ["BOLT_BENCH_DIR"] = bench_dir
        os.environ["DJANGO_SETTINGS_MODULE"] = "bench_settings"

        import django  # noqa: PLC0415
        from django.core.management import call_command  # noqa: PLC0415

        django.setup()
        call_command("migrate", "--noinput", verbosity=0)
        call_command("collectstatic", "--noinput", verbosity=0)

        port = _free_port()
        errors: list[BaseException] = []
        thread = threading.Thread(target=_run_server, args=(port, errors), name="runbolt", daemon=True)
        thread.start()
        try:
            conn = _wait_until_ready(port, thread, errors)
            try:
                # The ORM benchmarks read 10 of these users.
                status, body = conn.send(build_request("GET", "/users/seed?count=1000"))
                assert status == 200, body
                yield conn
            finally:
                conn.close()
        finally:
            _stop_server(thread)


@pytest.fixture(scope="session")
def auth_token(bench_server: Connection) -> str:
    """Make a JWT for the benchmark user with the shipped helper."""
    from django.contrib.auth.models import User  # noqa: PLC0415

    from django_bolt.auth import create_jwt_for_user  # noqa: PLC0415

    user, _ = User.objects.get_or_create(username="benchuser", defaults={"email": "bench@example.com"})
    return create_jwt_for_user(user)

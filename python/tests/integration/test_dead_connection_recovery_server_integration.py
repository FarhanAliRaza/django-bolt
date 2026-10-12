"""Recovery from dead PostgreSQL connections on a real ``runbolt`` server.

Bolt keeps Django connections open across requests and does not run
``close_old_connections``. The connection that loads ``request.user`` is
parked on an ORM pool thread between requests. Before 0.12, when PostgreSQL
closed that connection, every authenticated request on that thread failed with
``OperationalError: the connection is closed`` until the process restarted.

The connection has to survive between requests on a thread the framework
owns, so this needs a real server: ``TestClient`` runs the load in-process.
The in-process suite in ``test_broken_connection_recovery.py`` pins the same
code path against SQLite and covers the ``_check_before_call`` gate.

Set ``DJANGO_BOLT_TEST_POSTGRES_DSN`` to a PostgreSQL DSN whose role can
create databases, for example
``postgresql://postgres:postgres@127.0.0.1:5432/postgres``. ``just test-pg``
starts a throwaway server with Docker and runs these tests. Without the
variable, they skip.
"""

from __future__ import annotations

import secrets
import socket
import threading
import time
from typing import Any

import httpx
import jwt
import psycopg
import pytest

from .apps import app_module
from .apps.dead_connection_recovery import SECRET, USERNAME
from .helpers import postgres_settings

pytestmark = [pytest.mark.server_integration, pytest.mark.postgres]


def make_token(user_id: int) -> str:
    now = int(time.time())
    return jwt.encode({"sub": str(user_id), "iat": now, "exp": now + 3600}, SECRET, algorithm="HS256")


def terminate_backends(params: dict[str, Any], application_name: str, timeout: float = 10.0) -> int:
    """Kill every backend of the server with this ``application_name``.

    Returns the number of backends killed, after they are gone from
    ``pg_stat_activity``. ``pg_terminate_backend`` returns before the backend
    exits, and a request that arrives first would still be served.
    """
    with psycopg.connect(**params, autocommit=True) as conn:
        killed = conn.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity"
            " WHERE application_name = %s AND pid <> pg_backend_pid()",
            (application_name,),
        ).fetchall()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            (remaining,) = conn.execute(
                "SELECT count(*) FROM pg_stat_activity WHERE application_name = %s AND pid <> pg_backend_pid()",
                (application_name,),
            ).fetchone()
            if remaining == 0:
                return len(killed)
            time.sleep(0.05)
    raise AssertionError(f"{remaining} backend(s) of {application_name!r} still alive after {timeout}s")


def start_server(
    make_server_project,
    params: dict[str, Any],
    *,
    orm_threads: int = 1,
    settings_extra: str = "",
    **database_options: Any,
):
    """Start ``runbolt`` on the given database, with a unique ``application_name``.

    ``PGAPPNAME`` is read by libpq, so the kill can be scoped to the
    connections of this server. One ORM thread keeps one connection parked
    between requests, so the shape of the failure is deterministic.
    """
    application_name = f"bolt-recovery-{secrets.token_hex(4)}"
    project = make_server_project(
        api_module=app_module("dead_connection_recovery"),
        settings_extra=postgres_settings(params, **database_options) + settings_extra,
    )
    server = project.start(env={"PGAPPNAME": application_name, "DJANGO_BOLT_ORM_THREADS": str(orm_threads)})
    return server, application_name


def seed_and_authenticate(server) -> dict[str, str]:
    seeded = server.request("POST", "/seed")
    assert seeded.status_code == 200, seeded.text
    headers = {"Authorization": f"Bearer {make_token(seeded.json()['user_id'])}"}
    before = server.get("/me", headers=headers)
    assert before.status_code == 200, before.text
    assert before.json() == {"username": USERNAME}
    return headers


def test_authenticated_requests_recover_after_postgres_closes_the_connection(make_server_project, postgres_database):
    """Default settings: neither ``CONN_MAX_AGE`` nor ``CONN_HEALTH_CHECKS``.

    Nothing checks the connection before the query, so the first request
    after the kill may fail: the connection looks fine until it is used. Bolt
    drops it on that error, and the request after it reconnects. Without the
    drop, every request on the thread fails until the process restarts.
    """
    server, application_name = start_server(make_server_project, postgres_database)
    with server:
        headers = seed_and_authenticate(server)

        killed = terminate_backends(postgres_database, application_name)
        assert killed >= 1, "the server kept no connection open between requests"

        statuses = [server.get("/me", headers=headers).status_code for _ in range(5)]
        assert 200 in statuses[:2], f"no recovery within two requests: {statuses}"
        assert statuses[2:] == [200, 200, 200], f"recovery did not hold: {statuses}"

        recovered = server.get("/me", headers=headers)
        assert recovered.json() == {"username": USERNAME}


def test_health_checks_replace_the_dead_connection_before_the_query(make_server_project, postgres_database):
    """``CONN_HEALTH_CHECKS`` turns on the check before each pool call.

    Django runs its health check one time after ``close_if_unusable_or_obsolete``
    re-arms it. Bolt runs that on the pool thread before each call, so the dead
    connection is found and replaced before the query, and no request fails.
    """
    server, application_name = start_server(
        make_server_project, postgres_database, CONN_MAX_AGE=600, CONN_HEALTH_CHECKS=True
    )
    with server:
        headers = seed_and_authenticate(server)

        killed = terminate_backends(postgres_database, application_name)
        assert killed >= 1, "the server kept no connection open between requests"

        first = server.get("/me", headers=headers)
        assert first.status_code == 200, first.text
        assert first.json() == {"username": USERNAME}
        assert server.get("/me", headers=headers).status_code == 200


# The pool keeps more connections than the threads hold, so the kill also
# ends idle connections of the pool.
POOL = """
DATABASES["default"]["OPTIONS"] = {"pool": {"min_size": 8, "max_size": 12}}
"""
# After the second failed check in one checkout, the pool sleeps 0.9 s or more.
RECONNECT_BUDGET = 0.5


def query_each_orm_thread(server, count: int) -> list[str]:
    response = server.get(f"/orm-threads?count={count}")
    assert response.status_code == 200, response.text
    return response.json()["results"]


@pytest.mark.parametrize(
    "settings_extra",
    [
        pytest.param("", id="persistent"),
        pytest.param(POOL, id="pool"),
    ],
)
def test_one_dead_connection_retires_the_connections_of_every_thread(
    make_server_project, postgres_database, settings_extra
):
    """A restart of PostgreSQL kills the connection of each thread at once.

    The first call that meets a dead connection fails. Every thread then
    reconnects before its next call, so no other call fails. Before, each
    thread failed one call of its own: here, three ORM threads and the thread
    that loads ``request.user``. With a pool, the reconnects must not meet the
    dead connections of the pool, or the pool sleeps before each next one.
    """
    orm_threads = 4
    server, application_name = start_server(
        make_server_project, postgres_database, orm_threads=orm_threads, settings_extra=settings_extra
    )
    with server:
        headers = seed_and_authenticate(server)
        assert query_each_orm_thread(server, orm_threads) == ["ok"] * orm_threads

        killed = terminate_backends(postgres_database, application_name)
        assert killed > orm_threads, "the server did not keep a connection on each thread"

        assert query_each_orm_thread(server, 1) == ["OperationalError"]
        started = time.monotonic()
        assert query_each_orm_thread(server, 1) == ["ok"]
        assert query_each_orm_thread(server, orm_threads) == ["ok"] * orm_threads
        took = time.monotonic() - started
        assert took < RECONNECT_BUDGET, f"the calls after the failure took {took:.1f} s: the pool slept"
        recovered = server.get("/me", headers=headers)
        assert recovered.status_code == 200, recovered.text
        assert recovered.json() == {"username": USERNAME}


class FreezableProxy:
    """A TCP proxy to PostgreSQL that can stop forwarding without closing a connection.

    A frozen connection takes the bytes of a query and never answers, as a
    connection behind a network partition does. Thaw forwards the held bytes.
    """

    def __init__(self, host: str, port: int) -> None:
        self._target = (host, port)
        self._frozen = threading.Event()
        self._sockets: list[socket.socket] = []
        self._listener = socket.create_server(("127.0.0.1", 0))
        self.port = self._listener.getsockname()[1]
        threading.Thread(target=self._accept, daemon=True).start()

    def freeze(self) -> None:
        self._frozen.set()

    def thaw(self) -> None:
        self._frozen.clear()

    def close(self) -> None:
        self.thaw()
        for sock in [self._listener, *self._sockets]:
            sock.close()

    def _accept(self) -> None:
        while True:
            try:
                client, _ = self._listener.accept()
            except OSError:
                return
            upstream = socket.create_connection(self._target)
            self._sockets += [client, upstream]
            for source, target in ((client, upstream), (upstream, client)):
                threading.Thread(target=self._forward, args=(source, target), daemon=True).start()

    def _forward(self, source: socket.socket, target: socket.socket) -> None:
        try:
            while data := source.recv(65536):
                while self._frozen.is_set():
                    time.sleep(0.02)
                target.sendall(data)
        except OSError:
            return


def test_a_dead_connection_does_not_wait_for_the_idle_connections_of_its_pool(make_server_project, postgres_database):
    """A partition can leave the idle connections of the pool unable to answer.

    The thread that finds a dead connection must not send anything on them:
    it would wait until TCP gives up, and that thread can be an event loop.
    """
    proxy = FreezableProxy(postgres_database["host"], int(postgres_database["port"]))
    params = {**postgres_database, "host": "127.0.0.1", "port": proxy.port}
    server, _ = start_server(make_server_project, params, settings_extra=POOL)
    try:
        with server:
            assert query_each_orm_thread(server, 1) == ["ok"]
            proxy.freeze()
            started = time.monotonic()
            try:
                response = server.get("/break-own-connection", timeout=10)
            except httpx.TimeoutException:
                pytest.fail("the request that met the dead connection waited on the frozen idle connections")
            took = time.monotonic() - started
            proxy.thaw()
            assert response.status_code == 500, response.text
            assert took < RECONNECT_BUDGET, f"the failed request took {took:.1f} s"
    finally:
        proxy.close()

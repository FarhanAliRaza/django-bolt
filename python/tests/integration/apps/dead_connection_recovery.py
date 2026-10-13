"""App under test for recovery from a database connection that died.

``/me`` is the path that failed in production: an async handler behind the
default ``JWTAuthentication`` reads ``request.user``. The lazy load runs
``get_user_sync`` on the bounded ORM pool through ``run_orm_blocking``. The
Django connection it uses is parked on a pool thread between requests. When
the database server closes that connection, the next load must fail once at
most, and the request after it must reconnect.

``/orm-threads`` runs one query on each of ``count`` ORM pool threads, so a
test can park a connection on every thread and see which threads reconnect.

``/seed`` migrates the database of the subprocess and creates the test user,
since server projects start with an unmigrated database. ``SECRET`` and
``USERNAME`` are exported so tests can mint matching tokens.

``/me-inline`` is ``/me`` with no await, so Bolt dispatches it synchronously
on the worker thread.

``/echo`` sends a token through a query and returns what the database sent
back, with the process that served it. Two processes that share a socket read
each other's results, so a token that comes back wrong shows the sharing.

``/stream`` returns a sync streaming body that queries on the thread that
iterates it.

``/orm-threads-both-databases`` is ``/orm-threads`` with one query on the
``other`` alias before the query on ``default``.
"""

from __future__ import annotations

import asyncio
import os
import threading

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection, connections

from django_bolt import BoltAPI
from django_bolt.auth import IsAuthenticated, JWTAuthentication
from django_bolt.concurrency import run_in_orm_executor
from django_bolt.responses import StreamingResponse

SECRET = "dead-connection-recovery-secret-key-32-bytes"
USERNAME = "recovered"

api = BoltAPI()


@api.get("/health")
async def health():
    return {"status": "ok"}


@api.post("/seed")
def seed():
    call_command("migrate", interactive=False, verbosity=0)
    user, _ = User.objects.get_or_create(username=USERNAME)
    return {"user_id": user.id}


@api.get("/me", auth=[JWTAuthentication(secret=SECRET)], guards=[IsAuthenticated()])
async def me(request):
    # Forces the lazy load: load_via_sync -> run_orm_blocking -> get_user_sync.
    return {"username": request.user.username}


@api.get("/me-inline", auth=[JWTAuthentication(secret=SECRET)], guards=[IsAuthenticated()])
async def me_inline(request):
    # No await: Bolt runs this handler on the worker thread with no event
    # loop step, and the lazy user load blocks the loop of that thread.
    return {"username": request.user.username}


@api.get("/orm-threads")
async def orm_threads(count: int):
    """Run ``SELECT 1`` on ``count`` ORM pool threads at the same time.

    The barrier holds each call until all of them run, so each call has a
    thread of its own. Each result is ``"ok"`` or the name of the error.
    """
    barrier = threading.Barrier(count, timeout=5)

    def select_one() -> str:
        barrier.wait()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return "ok"

    results = await asyncio.gather(*(run_in_orm_executor(select_one) for _ in range(count)), return_exceptions=True)
    return {"results": [result if isinstance(result, str) else type(result).__name__ for result in results]}


@api.get("/break-own-connection")
async def break_own_connection():
    """Close the raw connection of an ORM pool thread, then query on it.

    The query fails with no network I/O, so the thread finds a dead connection
    while the network to the database stays as it is.
    """

    def close_then_query() -> None:
        connection.ensure_connection()
        connection.connection.close()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

    await run_in_orm_executor(close_then_query)
    return {"ok": True}


@api.get("/echo")
def echo(token: str):
    with connection.cursor() as cursor:
        # The sleep keeps the query on the socket long enough for another
        # process that shares it to write its own query.
        cursor.execute("SELECT %s::text, pg_sleep(0.002)", [token])
        (echoed, _) = cursor.fetchone()
    return {"token": echoed, "pid": os.getpid()}


@api.get("/stream")
def stream(rows: int):
    def body():
        with connection.cursor() as cursor:
            cursor.execute("SELECT generate_series(1, %s)", [rows])
            for (value,) in cursor.fetchall():
                yield f"{value}\n"

    return StreamingResponse(body(), media_type="text/plain")


@api.get("/orm-threads-both-databases")
async def orm_threads_both_databases(count: int):
    """Run one query on ``other`` and then one on ``default``, on ``count`` ORM pool threads at once."""
    barrier = threading.Barrier(count, timeout=5)

    def select_on_both() -> str:
        barrier.wait()
        for alias in ("other", "default"):
            with connections[alias].cursor() as cursor:
                cursor.execute("SELECT 1")
        return "ok"

    results = await asyncio.gather(*(run_in_orm_executor(select_on_both) for _ in range(count)), return_exceptions=True)
    return {"results": [result if isinstance(result, str) else type(result).__name__ for result in results]}

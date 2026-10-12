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
"""

from __future__ import annotations

import asyncio
import threading

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection

from django_bolt import BoltAPI
from django_bolt.auth import IsAuthenticated, JWTAuthentication
from django_bolt.concurrency import run_in_orm_executor

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

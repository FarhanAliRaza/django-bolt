"""An API with Django middleware and mostly async routes.

An async route does not use lane dispatch. The connection checks of a lane
must work with the async flow alone, so most tests here request only async
routes. The sync routes run their whole request on the lane.

``/pool-checkouts`` runs three ORM calls on the lane of its request. It
returns the number of connections that they opened or checked out of a pool.

``/pool-checkouts-after-an-error`` does the same, but its second call raises an
error that is not a database error, and the handler catches it.

``/lose-the-pool-on-a-sync-lane`` is a sync handler, so its whole request runs
on the lane. It makes the return of its pooled connection fail.
``/query-on-a-sync-lane`` runs one query on the lane.

``/lose-the-pool-after-an-error-on-a-sync-lane`` needs a second pooled database,
``second``. A query on ``default`` fails, and the handler catches the error.
Then the close of the ``default`` connection fails at the end of the request.
``/pool-stats`` returns the statistics of the pool of ``alias``.

``/lose-the-pool-of-one-database-on-a-sync-lane`` needs two more pooled
databases, ``a`` and ``b``. It queries both on the lane, then makes the return
of the connection of ``alias`` fail.
"""

from __future__ import annotations

import contextlib
import threading

from django.db import ProgrammingError, connection, connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.signals import connection_created
from django.utils.deprecation import MiddlewareMixin

from django_bolt import BoltAPI
from django_bolt.concurrency import sync_to_thread
from django_bolt.middleware import DjangoMiddlewareStack

_health_checks = []

# Each backend has its own is_usable, so count at the point where Django calls it.
_close_if_health_check_failed = BaseDatabaseWrapper.close_if_health_check_failed


def _counted_close_if_health_check_failed(self):
    if self.connection is not None and self.health_check_enabled and not self.health_check_done:
        _health_checks.append(self)
    return _close_if_health_check_failed(self)


BaseDatabaseWrapper.close_if_health_check_failed = _counted_close_if_health_check_failed

# Django sends connection_created for each new connection and for each checkout from a pool.
_checkouts = [0]
_checkouts_lock = threading.Lock()


def _count_checkout(sender, connection, **kwargs) -> None:
    with _checkouts_lock:
        _checkouts[0] += 1


connection_created.connect(_count_checkout, dispatch_uid="request_lanes_async.count_checkout")


def _select_one() -> int:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        return cursor.fetchone()[0]


class QueryMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _select_one()


api = BoltAPI(middleware=[DjangoMiddlewareStack([QueryMiddleware])])


@api.get("/health")
async def health():
    return {"status": "ok"}


@api.get("/health-checks")
async def health_checks():
    before = len(_health_checks)
    await sync_to_thread(_select_one)
    await sync_to_thread(_select_one)
    return {"checks": len(_health_checks) - before}


@api.get("/pool-checkouts")
async def pool_checkouts():
    before = _checkouts[0]
    for _ in range(3):
        await sync_to_thread(_select_one)
    return {"checkouts": _checkouts[0] - before}


def _select_one_then_fail() -> None:
    _select_one()
    raise LookupError("an error of user code, not of the database")


@api.get("/pool-checkouts-after-an-error")
async def pool_checkouts_after_an_error():
    before = _checkouts[0]
    await sync_to_thread(_select_one)
    with contextlib.suppress(LookupError):
        await sync_to_thread(_select_one_then_fail)
    await sync_to_thread(_select_one)
    return {"checkouts": _checkouts[0] - before}


@api.get("/lose-the-pool-on-a-sync-lane")
def lose_the_pool_on_a_sync_lane():
    _select_one()
    # psycopg_pool clears this reference when it closes a connection. Django
    # then cannot give the connection back, and its close() raises.
    connection.connection._pool = None
    return {"result": "ok"}


@api.get("/query-on-a-sync-lane")
def query_on_a_sync_lane():
    return {"result": _select_one()}


@api.get("/lose-the-pool-after-an-error-on-a-sync-lane")
def lose_the_pool_after_an_error_on_a_sync_lane():
    # The error sets errors_occurred, so the lane closes this connection when
    # the request ends. That close fails, before the lane gives ``second`` back.
    # A DataError or an IntegrityError does not set errors_occurred.
    with contextlib.suppress(ProgrammingError), connection.cursor() as cursor:
        cursor.execute("SELECT * FROM a_table_that_does_not_exist")
    with connections["second"].cursor() as cursor:
        cursor.execute("SELECT 1")
    connection.connection._pool = None
    return {"result": "ok"}


@api.get("/pool-stats")
async def pool_stats(alias: str):
    return connections[alias].pool.get_stats()


@api.get("/lose-the-pool-of-one-database-on-a-sync-lane")
def lose_the_pool_of_one_database_on_a_sync_lane(alias: str):
    for name in ("a", "b"):
        with connections[name].cursor() as cursor:
            cursor.execute("SELECT 1")
    connections[alias].connection._pool = None
    return {"result": "ok"}

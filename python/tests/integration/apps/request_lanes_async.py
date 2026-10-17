"""An API with Django middleware and async routes only.

No sync route is here, so no route uses lane dispatch. The connection checks
of a lane must work with the async flow alone.

``/pool-checkouts`` runs three ORM calls on the lane of its request. It
returns the number of connections that they opened or checked out of a pool.
"""

from __future__ import annotations

import threading

from django.db import connection
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

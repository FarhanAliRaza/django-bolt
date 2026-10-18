"""A QuerySet that a handler gets from a helper loads on the ORM pool.

The analysis of a handler finds the ORM calls in the handler itself. It cannot
see the ORM calls of a helper, so such a handler takes a fast path that does
not expect a QuerySet. Each fast path must still load the rows on the ORM
pool: not on the server worker thread, and not on the event loop, where Django
raises ``SynchronousOnlyOperation``.
"""

from __future__ import annotations

import msgspec
import pytest

from django_bolt import BoltAPI
from django_bolt.middleware import middleware
from django_bolt.testing import TestClient

from .test_models import Article
from .test_request_only_dispatch import ThreadRecordingQuerySet, articles


class Row(msgspec.Struct):
    title: str


async def passthrough(request, call_next):
    return await call_next(request)


def sync_typed(api: BoltAPI) -> None:
    @api.get("/articles")
    def listing(n: int = 0):
        return articles()


def async_typed(api: BoltAPI) -> None:
    @api.get("/articles")
    async def listing(n: int = 0):
        return articles()


def sync_no_params(api: BoltAPI) -> None:
    @api.get("/articles")
    def listing():
        return articles()


def async_no_params(api: BoltAPI) -> None:
    @api.get("/articles")
    async def listing():
        return articles()


def sync_typed_validated(api: BoltAPI) -> None:
    @api.get("/articles")
    def listing(n: int = 0) -> list[Row]:
        return articles()


def async_typed_validated(api: BoltAPI) -> None:
    @api.get("/articles")
    async def listing(n: int = 0) -> list[Row]:
        return articles()


def sync_typed_with_middleware(api: BoltAPI) -> None:
    @api.get("/articles")
    @middleware(passthrough)
    def listing(n: int = 0):
        return articles()


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "register",
    [
        sync_typed,
        async_typed,
        sync_no_params,
        async_no_params,
        sync_typed_validated,
        async_typed_validated,
        sync_typed_with_middleware,
    ],
)
def test_a_queryset_from_a_helper_loads_on_the_orm_pool(register):
    api = BoltAPI()
    register(api)
    Article.objects.create(title="One", content="First", author="A")
    ThreadRecordingQuerySet.threads.clear()
    with TestClient(api) as client:
        response = client.get("/articles")

    assert response.status_code == 200, response.text
    assert [row["title"] for row in response.json()] == ["One"]
    assert ThreadRecordingQuerySet.threads
    assert all(name.startswith("bolt_orm") for name in ThreadRecordingQuerySet.threads), ThreadRecordingQuerySet.threads

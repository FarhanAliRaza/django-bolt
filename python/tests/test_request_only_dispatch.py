"""A handler whose only parameter is the request takes the sync dispatch.

The sync dispatch calls the handler from Rust with no asyncio task. The async
dispatch runs it in a task on the worker loop, which costs about 15 us more for
each request. Each test reads ``asyncio.current_task()`` in the handler to see
which dispatch ran.
"""

from __future__ import annotations

import asyncio
import threading

import pytest

from django_bolt import BoltAPI, Request
from django_bolt.responses import PlainText
from django_bolt.testing import TestClient

from .test_models import Article


def in_task() -> bool:
    try:
        return asyncio.current_task() is not None
    except RuntimeError:
        return False


def test_an_async_request_handler_with_no_await_runs_with_no_task():
    api = BoltAPI()

    @api.get("/items")
    async def items(request: Request):
        return {"in_task": in_task(), "q": request.query.get("q")}

    with TestClient(api) as client:
        response = client.get("/items?q=bolt")

    assert response.json() == {"in_task": False, "q": "bolt"}


def test_a_sync_request_handler_runs_with_no_task():
    api = BoltAPI()

    @api.get("/items")
    def items(request: Request):
        return {"in_task": in_task(), "token": request.headers.get("x-token")}

    with TestClient(api) as client:
        response = client.get("/items", headers={"x-token": "secret"})

    assert response.json() == {"in_task": False, "token": "secret"}


def test_an_async_request_handler_that_awaits_runs_in_a_task():
    api = BoltAPI()

    @api.get("/items")
    async def items(request: Request):
        await asyncio.sleep(0)
        return {"in_task": in_task()}

    with TestClient(api) as client:
        response = client.get("/items")

    assert response.json() == {"in_task": True}


def test_a_request_handler_on_the_sync_dispatch_keeps_its_status_and_response_class():
    api = BoltAPI()

    @api.post("/created", status_code=201)
    async def created(request: Request):
        return {"created": True}

    @api.get("/text")
    def text(request: Request):
        return PlainText("hello")

    @api.get("/list")
    def listing(request: Request):
        return [1, 2, 3]

    with TestClient(api) as client:
        created_response = client.post("/created")
        text_response = client.get("/text")
        list_response = client.get("/list")

    assert (created_response.status_code, created_response.json()) == (201, {"created": True})
    assert text_response.text == "hello"
    assert text_response.headers["content-type"].startswith("text/plain")
    assert list_response.json() == [1, 2, 3]


@pytest.mark.django_db(transaction=True)
def test_a_sync_request_handler_that_uses_the_orm_still_runs_in_the_thread_pool():
    api = BoltAPI()

    @api.get("/count")
    def count(request: Request):
        return {"count": Article.objects.count(), "thread": threading.current_thread().name}

    with TestClient(api) as client:
        response = client.get("/count")

    assert response.json()["count"] == 0
    assert response.json()["thread"].startswith("bolt_default")

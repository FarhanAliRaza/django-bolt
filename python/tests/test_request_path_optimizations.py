"""Behavior at the optimized request boundaries."""

from __future__ import annotations

import pytest

from django_bolt import BoltAPI
from django_bolt.testing import TestClient


@pytest.fixture(scope="module")
def client():
    api = BoltAPI()

    @api.get("/raw")
    def raw(request):
        return request.raw_cookies

    @api.get("/bound")
    def bound(request):
        getter = request.get
        return getter("cookies")

    @api.get("/dynamic")
    def dynamic(request):
        return request.__getattribute__("cookies")

    @api.get("/path/{value}")
    def path(request):
        return {"value": request.params["value"], "query": request.query["q"]}

    with TestClient(api) as client:
        yield client


@pytest.mark.parametrize("path", ["/raw", "/bound", "/dynamic"])
def test_indirect_cookie_reads_keep_values(client, path):
    assert client.get(path, headers={"cookie": "a=value"}).json() == {"a": "value"}


@pytest.mark.parametrize("path", ["/path/hello", "/path//hello", "/path///hello"])
def test_normalization_preserves_query_slashes(client, path):
    response = client.get(path + "?q=https%3A%2F%2Fexample.org%2F%2F")
    assert response.status_code == 200
    assert response.json() == {"value": "hello", "query": "https://example.org//"}


def test_normalization_preserves_encoded_path_slashes(client):
    response = client.get("/path//a%2Fb?q=x")
    assert response.status_code == 200
    assert response.json() == {"value": "a/b", "query": "x"}

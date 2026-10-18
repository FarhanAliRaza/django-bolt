"""A URL-encoded form body has at most 1000 fields, as in Django.

Multipart bodies already stop at 100 parts. A URL-encoded body had no limit,
so a 1 MB body of empty fields gave about 330000 values to convert to Python.
"""

from __future__ import annotations

from typing import Annotated

from django_bolt import BoltAPI
from django_bolt.param_functions import Form
from django_bolt.testing import TestClient

FORM = {"content-type": "application/x-www-form-urlencoded"}


def form_api() -> BoltAPI:
    api = BoltAPI()

    @api.post("/form")
    async def form(name: Annotated[str, Form()] = ""):
        return {"name": name}

    return api


def test_a_form_of_1000_fields_is_accepted():
    body = "&".join(["name=bolt", *(f"f{i}=" for i in range(999))])
    with TestClient(form_api()) as client:
        response = client.post("/form", content=body, headers=FORM)

    assert (response.status_code, response.json()) == (200, {"name": "bolt"})


def test_a_form_of_1001_fields_is_rejected_with_422():
    body = "&".join(["name=bolt", *("f=" for _ in range(1000))])
    with TestClient(form_api()) as client:
        response = client.post("/form", content=body, headers=FORM)

    assert response.status_code == 422, response.text
    assert response.json()["detail"][0]["type"] == "too_many_fields"
    assert response.json()["detail"][0]["msg"] == "Too many form fields (max 1000)"

"""BoltAPI(error_formatter=...): one hook formats every error that the framework builds.

The errors come from the Rust core (guards, routing, parameter coercion, rate
limits, payload limits) and from Python (validation, HTTPException, unhandled
exceptions). Each test checks the HTTP response that a client gets.
"""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

import msgspec
import pytest
from django.core.management.base import CommandError
from msgspec import Meta

from django_bolt import BoltAPI
from django_bolt.auth import AllowAny, IsAuthenticated
from django_bolt.error_handlers import BoltError, problem_details
from django_bolt.exceptions import HTTPException
from django_bolt.management.commands.runbolt import Command
from django_bolt.middleware import rate_limit
from django_bolt.param_functions import Form
from django_bolt.responses import JSON, FileResponse, PlainText, Response
from django_bolt.serializers import Serializer
from django_bolt.testing import TestClient


class Body(Serializer):
    n: Annotated[int, Meta(ge=1)]


class Item(msgspec.Struct):
    id: int


def _record(error: BoltError, request) -> JSON:
    """Return every field of the error, so a test can check what the hook gets."""
    return JSON(
        {
            "status": error.status,
            "kind": error.kind,
            "detail": error.detail,
            "errors": error.errors,
            "headers": error.headers,
            "extra": error.extra,
            "exception": type(error.exception).__name__ if error.exception is not None else None,
            "method": request.method,
            "path": request.path,
            "probe": request.headers.get("x-probe"),
        },
        status_code=error.status,
    )


def _routes(api: BoltAPI) -> BoltAPI:
    @api.get("/items/{item_id}", guards=[AllowAny()])
    async def item(item_id: UUID) -> dict:
        return {}

    @api.get("/search", guards=[AllowAny()])
    async def search(limit: int) -> dict:
        return {}

    @api.get("/private", guards=[IsAuthenticated()])
    async def private() -> dict:
        return {}

    @api.get("/limited", guards=[AllowAny()])
    @rate_limit(rps=1, burst=1)
    async def limited() -> dict:
        return {}

    @api.post("/body", guards=[AllowAny()])
    async def body(body: Body) -> dict:
        return {}

    @api.post("/form", guards=[AllowAny()])
    async def form(age: Annotated[int, Form()]) -> dict:
        return {}

    @api.get("/conflict")
    async def conflict() -> dict:
        raise HTTPException(409, "Already exists", headers={"X-Reason": "dup"}, extra={"id": 3})

    @api.get("/crash")
    async def crash() -> dict:
        raise RuntimeError("boom")

    @api.get("/crash-sync")
    def crash_sync() -> dict:
        raise RuntimeError("boom")

    @api.get("/bad-response")
    async def bad_response() -> Item:
        return {"id": "not-an-int"}

    return api


@pytest.fixture
def recorded():
    with TestClient(_routes(BoltAPI(error_formatter=_record))) as client:
        yield client


@pytest.fixture
def problems():
    with TestClient(_routes(BoltAPI(error_formatter=problem_details))) as client:
        yield client


# --- Errors that the Rust core builds -------------------------------------


def test_guard_401_reaches_the_formatter_with_its_challenge(recorded):
    response = recorded.get("/private", headers={"X-Probe": "p1"})
    assert response.status_code == 401
    data = response.json()
    assert data["kind"] == "not_authenticated"
    assert data["detail"] == "Authentication required"
    assert data["headers"] == {"www-authenticate": "Bearer"}
    assert data["method"] == "GET"
    assert data["path"] == "/private"
    assert data["probe"] == "p1"
    assert data["exception"] is None
    # The error headers stay on the response that the formatter returns.
    assert response.headers["www-authenticate"] == "Bearer"


def test_route_miss_404_reaches_the_formatter(recorded):
    response = recorded.get("/nowhere")
    assert response.status_code == 404
    data = response.json()
    assert (data["kind"], data["detail"], data["path"]) == ("not_found", "Not Found", "/nowhere")


def test_path_coercion_422_gives_structured_errors(recorded):
    response = recorded.get("/items/not-a-uuid")
    assert response.status_code == 422
    data = response.json()
    assert data["kind"] == "validation"
    assert data["detail"] == "Request validation failed"
    [error] = data["errors"]
    assert error["loc"] == ["path", "item_id"]
    assert error["type"] == "validation_error"
    assert "UUID" in error["msg"]


def test_query_coercion_422_gives_structured_errors(recorded):
    response = recorded.get("/search?limit=abc")
    assert response.status_code == 422
    [error] = response.json()["errors"]
    assert error["loc"] == ["query", "limit"]


def test_form_coercion_422_gives_structured_errors(recorded):
    response = recorded.post("/form", data={"age": "old"})
    assert response.status_code == 422
    data = response.json()
    assert data["kind"] == "validation"
    [error] = data["errors"]
    assert error["loc"] == ["body", "age"]


def test_rate_limit_429_keeps_retry_after(recorded):
    assert recorded.get("/limited").status_code == 200
    response = recorded.get("/limited")
    assert response.status_code == 429
    data = response.json()
    assert data["kind"] == "rate_limited"
    assert data["extra"] == {"retry_after": 1}
    assert data["headers"]["retry-after"] == "1"
    assert response.headers["retry-after"] == "1"
    assert response.headers["x-ratelimit-limit"] == "1"


def test_payload_too_large_413_reaches_the_formatter(settings):
    settings.BOLT_MAX_UPLOAD_SIZE = 16
    with TestClient(_routes(BoltAPI(error_formatter=_record))) as client:
        response = client.post("/body", content=b'{"n": 1' + b" " * 64 + b"}")
    assert response.status_code == 413
    assert response.json()["kind"] == "payload_too_large"


# --- Errors that Python builds -------------------------------------------


def test_body_validation_422_reaches_the_formatter(recorded):
    response = recorded.post("/body", json={"n": 0})
    assert response.status_code == 422
    data = response.json()
    assert data["kind"] == "validation"
    assert data["exception"] is not None
    [error] = data["errors"]
    assert error["loc"] == ["body", "n"]


def test_http_exception_reaches_the_formatter(recorded):
    response = recorded.get("/conflict")
    assert response.status_code == 409
    data = response.json()
    assert data["kind"] == "conflict"
    assert data["detail"] == "Already exists"
    assert data["extra"] == {"id": 3}
    assert data["exception"] == "HTTPException"
    assert response.headers["x-reason"] == "dup"


@pytest.mark.parametrize("path", ["/crash", "/crash-sync"])
def test_unhandled_exception_reaches_the_formatter(recorded, path, caplog):
    with caplog.at_level(logging.ERROR, logger="django_bolt.error_handlers"):
        response = recorded.get(path)
    assert response.status_code == 500
    data = response.json()
    assert data["kind"] == "internal_error"
    assert data["detail"] == "Internal Server Error"
    assert data["exception"] == "RuntimeError"
    # The formatter does not stop the log of the server error.
    assert any("boom" in record.getMessage() for record in caplog.records)


def test_response_validation_500_reaches_the_formatter(recorded):
    response = recorded.get("/bad-response")
    assert response.status_code == 500
    data = response.json()
    assert data["kind"] == "response_validation"
    assert data["errors"]


# --- The built-in RFC 9457 formatter ---------------------------------------


def test_problem_details_for_a_rust_error(problems):
    response = problems.get("/private")
    assert response.status_code == 401
    assert response.headers["content-type"] == "application/problem+json"
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {
        "type": "about:blank",
        "title": "Unauthorized",
        "status": 401,
        "detail": "Authentication required",
        "instance": "/private",
    }


def test_problem_details_for_field_errors(problems):
    response = problems.get("/items/not-a-uuid")
    assert response.headers["content-type"] == "application/problem+json"
    data = response.json()
    assert data["status"] == 422
    assert data["title"] == HTTPStatus(422).phrase
    assert data["errors"][0]["loc"] == ["path", "item_id"]


def test_problem_details_for_a_python_error(problems):
    response = problems.post("/body", json={"n": 0})
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["errors"][0]["loc"] == ["body", "n"]


# --- Formatter results ------------------------------------------------------


def test_formatter_header_wins_over_the_error_header():
    def formatter(error: BoltError, request) -> Response:
        return Response(
            {"kind": error.kind},
            status_code=error.status,
            headers={"WWW-Authenticate": 'Bearer realm="api"'},
            media_type="application/vnd.error+json",
        )

    with TestClient(_routes(BoltAPI(error_formatter=formatter))) as client:
        response = client.get("/private")
    assert response.status_code == 401
    assert response.headers["content-type"] == "application/vnd.error+json"
    assert response.headers.get_list("www-authenticate") == ['Bearer realm="api"']
    assert response.json() == {"kind": "not_authenticated"}


def test_formatter_can_return_plain_text():
    def formatter(error: BoltError, request) -> PlainText:
        return PlainText(f"{error.status} {error.kind}", status_code=error.status)

    with TestClient(_routes(BoltAPI(error_formatter=formatter))) as client:
        rust_error = client.get("/nowhere")
        python_error = client.get("/conflict")
    assert rust_error.text == "404 not_found"
    assert rust_error.headers["content-type"].startswith("text/plain")
    assert python_error.text == "409 conflict"


@pytest.mark.parametrize(
    "formatter",
    [
        pytest.param(lambda _error, _request: 1 / 0, id="raises"),
        pytest.param(lambda _error, _request: {"not": "a response"}, id="wrong-type"),
    ],
)
def test_broken_formatter_logs_and_sends_the_default_error(formatter, caplog):
    with (
        caplog.at_level(logging.ERROR, logger="django_bolt.error_handlers"),
        TestClient(_routes(BoltAPI(error_formatter=formatter))) as client,
    ):
        rust_error = client.get("/nowhere")
        python_error = client.get("/conflict")
    assert rust_error.status_code == 404
    assert rust_error.json() == {"detail": "Not Found"}
    assert python_error.status_code == 409
    assert python_error.json() == {"detail": "Already exists", "extra": {"id": 3}}
    failures = [record for record in caplog.records if "error_formatter failed" in record.getMessage()]
    assert len(failures) == 2


def test_file_response_errors_reach_the_formatter(tmp_path):
    """FileResponse checks its file when the handler makes it, and Rust opens the file again to send it.

    A file that is missing at the first check gives a Python error. A file
    that goes away before Rust opens it gives a Rust error. Both reach the
    formatter.
    """
    path = tmp_path / "report.txt"
    api = BoltAPI(error_formatter=_record)

    @api.get("/missing")
    async def missing():
        return FileResponse(str(tmp_path / "absent.txt"))

    @api.get("/gone")
    async def gone():
        path.write_text("data")
        response = FileResponse(str(path))
        path.unlink()
        return response

    with TestClient(api) as client:
        missing_response = client.get("/missing")
        gone_response = client.get("/gone")

    assert missing_response.status_code == 404
    assert missing_response.json()["kind"] == "not_found"
    assert missing_response.json()["exception"] == "FileNotFoundError"
    assert gone_response.status_code == 404
    assert gone_response.headers["content-type"] == "application/json"
    assert gone_response.json()["kind"] == "not_found"
    assert gone_response.json()["exception"] is None


def test_without_formatter_the_errors_keep_the_detail_shape():
    with TestClient(_routes(BoltAPI())) as client:
        assert client.get("/private").json() == {"detail": "Authentication required"}
        assert client.get("/nowhere").json() == {"detail": "Not Found"}
        assert client.get("/conflict").json() == {"detail": "Already exists", "extra": {"id": 3}}


def test_error_formatter_must_be_callable():
    with pytest.raises(TypeError, match="error_formatter"):
        BoltAPI(error_formatter="problem_details")


# --- runbolt merges the APIs of a project -----------------------------------


def _api_with_route(path: str, formatter=None) -> BoltAPI:
    api = BoltAPI(error_formatter=formatter)

    @api.get(path)
    async def view() -> dict:
        return {}

    return api


def test_merge_keeps_the_one_formatter_of_the_project():
    merged = Command().merge_apis([("a.api", _api_with_route("/a", problem_details)), ("b.api", _api_with_route("/b"))])
    assert merged._error_formatter is problem_details


def test_merge_rejects_two_different_formatters():
    with pytest.raises(CommandError, match="error_formatter"):
        Command().merge_apis(
            [
                ("a.api", _api_with_route("/a", problem_details)),
                ("b.api", _api_with_route("/b", _record)),
            ]
        )

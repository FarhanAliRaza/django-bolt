"""The OpenAPI schema describes the error body of BoltAPI(error_formatter=...).

Each test reads the schema from the docs route, as a client generator does,
and compares it with the error response that a client gets.
"""

from __future__ import annotations

import msgspec
import pytest
from openapi_spec_validator import validate

from django_bolt import BoltAPI
from django_bolt.error_handlers import BoltError, ProblemDetails, error_schema, problem_details
from django_bolt.exceptions import HTTPException
from django_bolt.openapi import OpenAPIConfig
from django_bolt.openapi.schema_generator import OpenAPIStrictError, SchemaGenerator
from django_bolt.responses import PlainText, Response
from django_bolt.testing import TestClient


class ItemIn(msgspec.Struct):
    name: str


class Item(msgspec.Struct):
    id: int
    name: str


class Conflict(msgspec.Struct):
    reason: str


class ErrorBody(msgspec.Struct):
    """The body of a vendor error."""

    code: str
    message: str


@error_schema(ErrorBody, media_type="application/vnd.error+json")
def vendor_error(error: BoltError, request) -> Response:
    body = {"code": error.kind, "message": error.detail}
    return Response(body, status_code=error.status, media_type="application/vnd.error+json")


def plain_error(error: BoltError, request) -> PlainText:
    return PlainText(error.detail, status_code=error.status)


def _api(formatter=None, *, strict: bool = False) -> BoltAPI:
    api = BoltAPI(
        error_formatter=formatter,
        openapi_config=OpenAPIConfig(title="Errors", version="1.0.0", strict=strict),
    )

    @api.post("/items", response_model={200: Item, 409: Conflict})
    async def create_item(data: ItemIn):
        if data.name == "taken":
            raise HTTPException(409, body=Conflict(reason="taken"))
        return Item(id=1, name=data.name)

    api._register_openapi_routes()
    return api


def _spec(api: BoltAPI) -> dict:
    with TestClient(api) as client:
        response = client.get("/docs/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    validate(spec)
    return spec


def _responses(spec: dict) -> dict:
    return spec["paths"]["/items"]["post"]["responses"]


def test_without_formatter_the_422_keeps_the_detail_schema():
    assert _responses(_spec(_api()))["422"] == {
        "description": "Validation Error - Request data failed validation",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "array",
                            "description": "List of validation errors",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "description": "Error type",
                                        "example": "validation_error",
                                    },
                                    "loc": {
                                        "type": "array",
                                        "description": "Location of the error (field path)",
                                        "items": {"oneOf": [{"type": "string"}, {"type": "integer"}]},
                                        "example": ["body", "is_active"],
                                    },
                                    "msg": {
                                        "type": "string",
                                        "description": "Error message",
                                        "example": "Expected `bool`, got `int`",
                                    },
                                    "input": {"description": "The input value that caused the error (optional)"},
                                },
                                "required": ["type", "loc", "msg"],
                            },
                        }
                    },
                    "required": ["detail"],
                }
            }
        },
    }


def test_problem_details_documents_the_422_that_the_client_gets():
    api = _api(problem_details, strict=True)
    spec = _spec(api)
    responses = _responses(spec)

    assert responses["422"]["content"] == {
        "application/problem+json": {"schema": {"$ref": "#/components/schemas/ProblemDetails"}}
    }
    problem = spec["components"]["schemas"]["ProblemDetails"]
    assert problem["required"] == ["type", "title", "status", "detail", "instance"]
    assert problem["properties"]["errors"]["items"] == {"$ref": "#/components/schemas/ProblemFieldError"}
    assert spec["components"]["schemas"]["ProblemFieldError"]["required"] == ["loc", "msg", "type"]
    # An error model that the route declares keeps its entry: its typed body skips the formatter.
    assert responses["409"]["content"] == {"application/json": {"schema": {"$ref": "#/components/schemas/Conflict"}}}

    with TestClient(api) as client:
        invalid = client.post("/items", json={"name": 1})
        taken = client.post("/items", json={"name": "taken"})

    assert invalid.status_code == 422
    assert invalid.headers["content-type"] == "application/problem+json"
    body = msgspec.convert(invalid.json(), ProblemDetails)
    assert body.status == 422
    assert [error.loc for error in body.errors] == [["body", "name"]]
    assert taken.status_code == 409
    assert taken.headers["content-type"] == "application/json"
    assert taken.json() == {"reason": "taken"}


def test_declared_error_schema_documents_the_422():
    api = _api(vendor_error, strict=True)
    spec = _spec(api)

    assert _responses(spec)["422"]["content"] == {
        "application/vnd.error+json": {"schema": {"$ref": "#/components/schemas/ErrorBody"}}
    }
    assert spec["components"]["schemas"]["ErrorBody"]["required"] == ["code", "message"]

    with TestClient(api) as client:
        invalid = client.post("/items", json={})

    assert invalid.headers["content-type"] == "application/vnd.error+json"
    msgspec.convert(invalid.json(), ErrorBody)


def test_formatter_without_error_schema_documents_no_422_body():
    """Bolt cannot know the body of the formatter, so it does not guess one."""
    assert _responses(_spec(_api(plain_error)))["422"] == {
        "description": "Validation Error - Request data failed validation",
    }


def test_strict_mode_reports_a_formatter_without_error_schema():
    api = _api(plain_error, strict=True)
    with pytest.raises(OpenAPIStrictError, match=r"error_formatter plain_error has no error_schema"):
        SchemaGenerator(api, api._openapi_config).generate()

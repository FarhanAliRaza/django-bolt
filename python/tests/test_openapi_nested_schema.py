"""
Tests for OpenAPI schema generation with nested msgspec Structs.

Regression test for: nested serializers showing as empty objects {} in OpenAPI
schema instead of expanding their fields.
"""

from __future__ import annotations

import msgspec

from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig
from django_bolt.testing import TestClient


class Address(msgspec.Struct):
    street: str
    city: str


class Child(msgspec.Struct):
    id: str
    name: str


class ChildWithAddress(msgspec.Struct):
    id: str
    name: str
    address: Address


class Parent(msgspec.Struct):
    id: str
    child: Child


class ParentWithList(msgspec.Struct):
    id: str
    children: list[Child]


class ParentWithOptional(msgspec.Struct):
    id: str
    maybe_child: Child | None = None


class ParentDeepNested(msgspec.Struct):
    id: str
    child: ChildWithAddress


def _get_schema(api: BoltAPI) -> dict:
    """Helper to get OpenAPI schema dict from an API instance."""
    api._register_openapi_routes()
    with TestClient(api) as client:
        response = client.get("/docs/openapi.json")
        assert response.status_code == 200
        return response.json()


def test_nested_struct_has_properties():
    """Nested struct fields must include their properties in the schema."""
    api = BoltAPI(openapi_config=OpenAPIConfig(title="Test", version="1.0.0"))

    @api.get("/parent")
    async def get_parent() -> Parent:
        pass

    schema = _get_schema(api)
    schemas = schema["components"]["schemas"]

    # Child schema must exist and have its fields
    assert "Child" in schemas, f"Child schema missing from components. Got: {list(schemas.keys())}"
    child_schema = schemas["Child"]
    assert "properties" in child_schema, f"Child schema has no properties: {child_schema}"
    assert "id" in child_schema["properties"], "Child.id missing"
    assert "name" in child_schema["properties"], "Child.name missing"
    assert child_schema["properties"]["id"]["type"] == "string"
    assert child_schema["properties"]["name"]["type"] == "string"

    # Parent.child should reference the Child component
    parent_schema = schemas["Parent"]
    child_field = parent_schema["properties"]["child"]
    assert "$ref" in child_field, f"Parent.child should be a $ref, got: {child_field}"
    assert child_field["$ref"] == "#/components/schemas/Child"


def test_list_of_nested_structs_has_properties():
    """list[Struct] fields must reference the struct schema with full properties."""
    api = BoltAPI(openapi_config=OpenAPIConfig(title="Test", version="1.0.0"))

    @api.get("/parents")
    async def get_parents() -> ParentWithList:
        pass

    schema = _get_schema(api)
    schemas = schema["components"]["schemas"]

    # Child schema must exist with fields
    assert "Child" in schemas
    assert "id" in schemas["Child"]["properties"]
    assert "name" in schemas["Child"]["properties"]

    # ParentWithList.children should be array of $ref
    parent_schema = schemas["ParentWithList"]
    children_field = parent_schema["properties"]["children"]
    assert children_field["type"] == "array"
    assert "$ref" in children_field["items"], f"List items should be $ref, got: {children_field['items']}"
    assert children_field["items"]["$ref"] == "#/components/schemas/Child"


def test_optional_nested_struct_has_properties():
    """Optional[Struct] fields must reference the struct schema with full properties."""
    api = BoltAPI(openapi_config=OpenAPIConfig(title="Test", version="1.0.0"))

    @api.get("/parent")
    async def get_parent() -> ParentWithOptional:
        pass

    schema = _get_schema(api)
    schemas = schema["components"]["schemas"]

    # Child schema must exist with fields
    assert "Child" in schemas
    assert "id" in schemas["Child"]["properties"]
    assert "name" in schemas["Child"]["properties"]


def test_deeply_nested_structs_have_properties():
    """Structs nested multiple levels deep must all have their properties."""
    api = BoltAPI(openapi_config=OpenAPIConfig(title="Test", version="1.0.0"))

    @api.get("/parent")
    async def get_parent() -> ParentDeepNested:
        pass

    schema = _get_schema(api)
    schemas = schema["components"]["schemas"]

    # Address (2 levels deep) must exist with fields
    assert "Address" in schemas, f"Address schema missing. Got: {list(schemas.keys())}"
    address_schema = schemas["Address"]
    assert "street" in address_schema["properties"], "Address.street missing"
    assert "city" in address_schema["properties"], "Address.city missing"

    # ChildWithAddress.address should reference Address
    child_schema = schemas["ChildWithAddress"]
    assert child_schema["properties"]["address"]["$ref"] == "#/components/schemas/Address"

    # ParentDeepNested.child should reference ChildWithAddress
    parent_schema = schemas["ParentDeepNested"]
    assert parent_schema["properties"]["child"]["$ref"] == "#/components/schemas/ChildWithAddress"


def test_nested_struct_as_request_body():
    """Nested structs in request bodies must also have their properties expanded."""
    api = BoltAPI(openapi_config=OpenAPIConfig(title="Test", version="1.0.0"))

    @api.post("/parent")
    async def create_parent(data: Parent) -> Parent:
        pass

    schema = _get_schema(api)
    schemas = schema["components"]["schemas"]

    # Child schema must exist with fields for both request and response
    assert "Child" in schemas
    assert "id" in schemas["Child"]["properties"]
    assert "name" in schemas["Child"]["properties"]

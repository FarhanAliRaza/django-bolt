#!/usr/bin/env python3
"""
Quick verification script for OpenAPI metadata feature.
Tests the Python-side implementation without requiring Rust build.
"""
import sys
sys.path.insert(0, 'python')

from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig
from django_bolt.openapi.schema_generator import SchemaGenerator
from django_bolt.openapi.spec import Tag
from django_bolt.decorators import action


def test_route_decorator_metadata():
    """Test that route decorators accept and store metadata."""
    print("Testing route decorator with tags, summary, description...")

    api = BoltAPI()

    @api.get(
        "/items",
        tags=["Items", "Inventory"],
        summary="Get all items",
        description="Returns a list of all items in the inventory."
    )
    async def get_items():
        """Docstring summary.

        Docstring description.
        """
        return []

    # Verify metadata is stored
    meta = api._handler_meta.get(get_items)
    assert meta is not None, "Handler metadata not found"
    assert meta.get("openapi_tags") == ["Items", "Inventory"], f"Tags mismatch: {meta.get('openapi_tags')}"
    assert meta.get("openapi_summary") == "Get all items", f"Summary mismatch: {meta.get('openapi_summary')}"
    assert meta.get("openapi_description") == "Returns a list of all items in the inventory.", f"Description mismatch: {meta.get('openapi_description')}"

    print("✓ Route decorator metadata stored correctly")
    return True


def test_schema_generation():
    """Test that schema generator uses custom metadata."""
    print("\nTesting schema generation with custom metadata...")

    api = BoltAPI()

    @api.get(
        "/items",
        tags=["CustomTag"],
        summary="Custom Summary",
        description="Custom Description"
    )
    async def get_items():
        """Docstring summary.

        Docstring description.
        """
        return []

    @api.post("/orders", tags=["Orders"])
    async def create_order():
        return {}

    config = OpenAPIConfig(title="Test API", version="1.0.0", use_handler_docstrings=True)
    generator = SchemaGenerator(api, config)
    schema = generator.generate()

    # Check operation metadata
    operation = schema.paths["/items"].get
    assert operation.tags == ["CustomTag"], f"Operation tags mismatch: {operation.tags}"
    assert operation.summary == "Custom Summary", f"Operation summary mismatch: {operation.summary}"
    assert operation.description == "Custom Description", f"Operation description mismatch: {operation.description}"

    print("✓ Schema generation uses custom metadata")

    # Check tag collection
    assert schema.tags is not None, "Tags not collected"
    tag_names = {tag.name for tag in schema.tags}
    assert "CustomTag" in tag_names, f"CustomTag not in collected tags: {tag_names}"
    assert "Orders" in tag_names, f"Orders not in collected tags: {tag_names}"

    print("✓ Tags collected correctly")
    return True


def test_fallback_to_docstring():
    """Test that schema generator falls back to docstring when metadata not provided."""
    print("\nTesting fallback to docstring...")

    api = BoltAPI()

    @api.get("/items")
    async def get_items():
        """Docstring summary line.

        Docstring description paragraph.
        """
        return []

    config = OpenAPIConfig(title="Test API", version="1.0.0", use_handler_docstrings=True)
    generator = SchemaGenerator(api, config)
    schema = generator.generate()

    operation = schema.paths["/items"].get
    assert operation.summary == "Docstring summary line.", f"Summary should use docstring: {operation.summary}"
    assert operation.description == "Docstring description paragraph.", f"Description should use docstring: {operation.description}"

    print("✓ Fallback to docstring works")
    return True


def test_partial_override():
    """Test that partial metadata override works."""
    print("\nTesting partial metadata override...")

    api = BoltAPI()

    @api.get("/items", summary="Custom Summary Only")
    async def get_items():
        """Docstring summary.

        Docstring description that should be used.
        """
        return []

    config = OpenAPIConfig(title="Test API", version="1.0.0", use_handler_docstrings=True)
    generator = SchemaGenerator(api, config)
    schema = generator.generate()

    operation = schema.paths["/items"].get
    assert operation.summary == "Custom Summary Only", f"Summary should be custom: {operation.summary}"
    assert operation.description == "Docstring description that should be used.", f"Description should use docstring: {operation.description}"

    print("✓ Partial override works correctly")
    return True


def test_action_decorator_metadata():
    """Test that action decorator accepts metadata."""
    print("\nTesting action decorator with metadata...")

    from django_bolt.decorators import ActionHandler

    @action(
        methods=["POST"],
        detail=True,
        tags=["UserActions"],
        summary="Activate user",
        description="Activates the user account."
    )
    async def activate(self, id: int):
        return {}

    assert isinstance(activate, ActionHandler), "Should be ActionHandler instance"
    assert activate.tags == ["UserActions"], f"Tags mismatch: {activate.tags}"
    assert activate.summary == "Activate user", f"Summary mismatch: {activate.summary}"
    assert activate.description == "Activates the user account.", f"Description mismatch: {activate.description}"

    print("✓ Action decorator metadata stored correctly")
    return True


def test_all_http_methods():
    """Test that all HTTP methods support metadata."""
    print("\nTesting all HTTP methods...")

    api = BoltAPI()

    @api.get("/test", tags=["Test"], summary="GET test")
    async def get_test():
        return {}

    @api.post("/test", tags=["Test"], summary="POST test")
    async def post_test():
        return {}

    @api.put("/test", tags=["Test"], summary="PUT test")
    async def put_test():
        return {}

    @api.patch("/test", tags=["Test"], summary="PATCH test")
    async def patch_test():
        return {}

    @api.delete("/test", tags=["Test"], summary="DELETE test")
    async def delete_test():
        return {}

    @api.head("/test", tags=["Test"], summary="HEAD test")
    async def head_test():
        return {}

    @api.options("/test", tags=["Test"], summary="OPTIONS test")
    async def options_test():
        return {}

    for handler, method_name in [
        (get_test, "GET"),
        (post_test, "POST"),
        (put_test, "PUT"),
        (patch_test, "PATCH"),
        (delete_test, "DELETE"),
        (head_test, "HEAD"),
        (options_test, "OPTIONS"),
    ]:
        meta = api._handler_meta.get(handler)
        assert meta is not None, f"{method_name} handler metadata not found"
        assert meta.get("openapi_tags") == ["Test"], f"{method_name} tags mismatch"
        assert method_name in meta.get("openapi_summary", ""), f"{method_name} summary mismatch"

    print("✓ All HTTP methods support metadata")
    return True


def test_config_tags_merge():
    """Test that config tags merge with collected tags."""
    print("\nTesting config tags merge...")

    api = BoltAPI()

    @api.get("/items", tags=["Items"])
    async def get_items():
        return []

    @api.get("/orders", tags=["Orders"])
    async def get_orders():
        return []

    # Pre-define Items tag with description
    config = OpenAPIConfig(
        title="Test API",
        version="1.0.0",
        tags=[Tag(name="Items", description="Inventory items")]
    )
    generator = SchemaGenerator(api, config)
    schema = generator.generate()

    # Check that Items tag has description from config
    items_tag = next((tag for tag in schema.tags if tag.name == "Items"), None)
    assert items_tag is not None, "Items tag not found"
    assert items_tag.description == "Inventory items", f"Items tag description mismatch: {items_tag.description}"

    # Check that Orders tag was created without description
    orders_tag = next((tag for tag in schema.tags if tag.name == "Orders"), None)
    assert orders_tag is not None, "Orders tag not found"
    assert orders_tag.description is None, f"Orders tag should have no description: {orders_tag.description}"

    print("✓ Config tags merged correctly")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("OpenAPI Metadata Feature Verification")
    print("=" * 60)

    tests = [
        test_route_decorator_metadata,
        test_schema_generation,
        test_fallback_to_docstring,
        test_partial_override,
        test_action_decorator_metadata,
        test_all_http_methods,
        test_config_tags_merge,
    ]

    failed = []
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed.append((test.__name__, e))

    print("\n" + "=" * 60)
    if not failed:
        print("✓ All tests passed!")
        print("=" * 60)
        sys.exit(0)
    else:
        print(f"✗ {len(failed)} tests failed:")
        for name, error in failed:
            print(f"  - {name}: {error}")
        print("=" * 60)
        sys.exit(1)

"""
Tests for OpenAPI documentation generation and rendering.

These tests verify that the OpenAPI/Swagger documentation endpoints
are working correctly and not throwing internal errors.
"""
import msgspec
from typing import Optional
from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig, SwaggerRenderPlugin
from django_bolt.testing import TestClient


class Item(msgspec.Struct):
    """Model for OpenAPI schema generation."""
    id: int
    name: str
    price: float
    is_active: Optional[bool] = None


def test_openapi_json_endpoint():
    """Test that /schema/openapi.json returns valid JSON without errors."""
    # Create API with OpenAPI enabled (default path is /schema)
    api = BoltAPI(
        openapi_config=OpenAPIConfig(
            title="Test API",
            version="1.0.0",
            description="Test API for OpenAPI docs"
        )
    )

    # Add some test routes with various parameter types
    @api.get("/items/{item_id}")
    async def get_item(item_id: int, q: Optional[str] = None):
        """Get an item by ID."""
        return {"item_id": item_id, "q": q}

    @api.post("/items", response_model=Item)
    async def create_item(item: Item) -> Item:
        """Create a new item."""
        return item

    # Test the OpenAPI JSON endpoint
    # Note: Must register OpenAPI routes BEFORE creating TestClient
    api._register_openapi_routes()

    with TestClient(api) as client:
        response = client.get("/schema/openapi.json")

        # Should return 200 OK (not 500 Internal Server Error)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        # Should return valid JSON
        data = response.json()
        assert data is not None

        # Verify basic OpenAPI structure
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Test API"
        assert data["info"]["version"] == "1.0.0"
        assert "paths" in data

        # Verify our routes are in the schema
        assert "/items/{item_id}" in data["paths"]
        assert "/items" in data["paths"]


def test_swagger_ui_endpoint():
    """Test that /schema/swagger (Swagger UI) loads without internal errors."""
    # Create API with Swagger UI enabled (default path is /schema)
    api = BoltAPI(
        openapi_config=OpenAPIConfig(
            title="Test API",
            version="1.0.0",
            render_plugins=[SwaggerRenderPlugin()]
        )
    )

    # Add a simple route
    @api.get("/test")
    async def test_endpoint():
        """Test endpoint."""
        return {"status": "ok"}

    # Test the Swagger UI endpoint
    # Note: Must register OpenAPI routes BEFORE creating TestClient
    api._register_openapi_routes()

    with TestClient(api) as client:
        response = client.get("/schema/swagger")

        # Should return 200 OK (not 500 Internal Server Error)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        # Should return HTML content
        assert response.headers.get("content-type", "").startswith("text/html")

        # Should contain Swagger UI indicators
        html = response.text
        assert "swagger" in html.lower() or "openapi" in html.lower()


def test_openapi_root_path_serves_ui_directly():
    """Test that /docs serves default UI directly without redirect loop.

    This test catches the bug where:
    - /docs redirected to /docs/
    - NormalizePath::trim() stripped trailing slash back to /docs
    - Infinite redirect loop

    The fix serves the default UI directly at /docs instead of redirecting.

    We verify this by checking that response.history is empty (no redirects occurred).
    """
    api = BoltAPI(
        openapi_config=OpenAPIConfig(
            title="Test API",
            version="1.0.0",
            path="/docs",
            render_plugins=[SwaggerRenderPlugin(path="/")]
        )
    )

    @api.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    api._register_openapi_routes()

    with TestClient(api) as client:
        response = client.get("/docs")

        # CRITICAL: Must NOT redirect - this is what causes the infinite loop
        # in production with NormalizePath::trim() middleware.
        # TestClient doesn't have NormalizePath, so redirect would "work" here,
        # but in production: /docs -> redirect /docs/ -> trim to /docs -> loop
        assert len(response.history) == 0, \
            f"/docs should serve UI directly without redirect, but got redirects: {response.history}"

        # Should return 200 with HTML content directly
        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}"

        # Should be HTML content (Swagger UI)
        content_type = response.headers.get("content-type", "")
        assert "text/html" in content_type, f"Expected HTML, got {content_type}"

        # Should contain Swagger UI content
        html = response.text
        assert "swagger" in html.lower(), "Response should contain Swagger UI"

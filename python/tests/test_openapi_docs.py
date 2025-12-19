"""
Tests for OpenAPI documentation generation and rendering.

These tests verify that the OpenAPI/Swagger documentation endpoints
are working correctly and not throwing internal errors.
"""

import msgspec

from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig, SwaggerRenderPlugin
from django_bolt.testing import TestClient


class Item(msgspec.Struct):
    """Model for OpenAPI schema generation."""
    id: int
    name: str
    price: float
    is_active: bool | None = None


def test_openapi_json_endpoint():
    """Test that /docs/openapi.json returns valid JSON without errors."""
    # Create API with OpenAPI enabled (default path is /docs)
    api = BoltAPI(
        openapi_config=OpenAPIConfig(
            title="Test API",
            version="1.0.0",
            description="Test API for OpenAPI docs"
        )
    )

    # Add some test routes with various parameter types
    @api.get("/items/{item_id}")
    async def get_item(item_id: int, q: str | None = None):
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
        response = client.get("/docs/openapi.json")

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
    """Test that /docs/swagger (Swagger UI) loads without internal errors."""
    # Create API with Swagger UI enabled (default path is /docs)
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
        response = client.get("/docs/swagger")

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


def test_openapi_disabled_returns_404():
    """Test that disabled OpenAPI docs return 404."""
    api = BoltAPI(
        openapi_config=OpenAPIConfig(
            title="Test API",
            version="1.0.0",
            enabled=False  # Explicitly disabled
        )
    )

    @api.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    # Register routes (should skip OpenAPI routes due to enabled=False)
    api._register_openapi_routes()

    with TestClient(api) as client:
        # All doc routes should return 404
        response = client.get("/docs/openapi.json")
        assert response.status_code == 404, \
            f"Disabled docs should return 404, got {response.status_code}"

        response = client.get("/docs")
        assert response.status_code == 404, \
            f"Disabled docs UI should return 404, got {response.status_code}"


def test_openapi_protected_without_auth_returns_401():
    """Test that protected docs without authentication return 401."""
    from django_bolt.auth import IsAuthenticated, JWTAuthentication

    api = BoltAPI(
        openapi_config=OpenAPIConfig(
            title="Test API",
            version="1.0.0",
            auth=[JWTAuthentication(secret="test-secret")],
            guards=[IsAuthenticated()]
        )
    )

    @api.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    api._register_openapi_routes()

    with TestClient(api) as client:
        # Without token, should get 401
        response = client.get("/docs/openapi.json")
        assert response.status_code == 401, \
            f"Protected docs without auth should return 401, got {response.status_code}"

        response = client.get("/docs")
        assert response.status_code == 401, \
            f"Protected docs UI without auth should return 401, got {response.status_code}"


def test_openapi_protected_with_valid_auth():
    """Test that protected docs with valid authentication work."""
    import time

    import jwt

    from django_bolt.auth import IsAuthenticated, JWTAuthentication

    api = BoltAPI(
        openapi_config=OpenAPIConfig(
            title="Test API",
            version="1.0.0",
            auth=[JWTAuthentication(secret="test-secret")],
            guards=[IsAuthenticated()]
        )
    )

    @api.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    api._register_openapi_routes()

    # Create valid token
    token = jwt.encode(
        {"sub": "user123", "exp": int(time.time()) + 3600},
        "test-secret",
        algorithm="HS256"
    )

    with TestClient(api) as client:
        headers = {"Authorization": f"Bearer {token}"}

        # With valid token, should get 200
        response = client.get("/docs/openapi.json", headers=headers)
        assert response.status_code == 200, \
            f"Protected docs with valid auth should return 200, got {response.status_code}"

        # Verify it returns valid JSON schema
        data = response.json()
        assert "openapi" in data
        assert data["info"]["title"] == "Test API"

        # UI should also work
        response = client.get("/docs", headers=headers)
        assert response.status_code == 200, \
            f"Protected docs UI with valid auth should return 200, got {response.status_code}"


def test_openapi_all_routes_protected():
    """Test that all OpenAPI routes are protected when guards are set."""
    from django_bolt.auth import IsAuthenticated, JWTAuthentication

    api = BoltAPI(
        openapi_config=OpenAPIConfig(
            title="Test API",
            version="1.0.0",
            path="/docs",
            auth=[JWTAuthentication(secret="test-secret")],
            guards=[IsAuthenticated()],
            render_plugins=[SwaggerRenderPlugin()]
        )
    )

    @api.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    api._register_openapi_routes()

    with TestClient(api) as client:
        # All routes should return 401 without auth
        routes_to_test = [
            "/docs/openapi.json",
            "/docs/openapi.yaml",
            "/docs/openapi.yml",
            "/docs",  # Root UI
            "/docs/swagger",  # Swagger UI
        ]

        for route in routes_to_test:
            response = client.get(route)
            assert response.status_code == 401, \
                f"Route {route} should be protected (401), got {response.status_code}"


def test_openapi_django_auth_redirects_to_login():
    """Test that django_auth=True redirects unauthenticated users to login."""

    api = BoltAPI(
        openapi_config=OpenAPIConfig(
            title="Test API",
            version="1.0.0",
            django_auth=True
        )
    )

    @api.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    api._register_openapi_routes()

    with TestClient(api) as client:
        # Without authentication, should redirect to login
        response = client.get("/docs", follow_redirects=False)

        # Django's login_required returns 302 redirect to login page
        assert response.status_code == 302, \
            f"Expected 302 redirect, got {response.status_code}"

        # Should redirect to login URL (contains 'login' or 'accounts/login')
        location = response.headers.get("location", "")
        assert "login" in location.lower(), \
            f"Should redirect to login page, got: {location}"


def test_openapi_django_auth_with_staff_member_required():
    """Test that staff_member_required decorator redirects non-staff to admin login."""
    from django.contrib.admin.views.decorators import staff_member_required

    api = BoltAPI(
        openapi_config=OpenAPIConfig(
            title="Test API",
            version="1.0.0",
            django_auth=staff_member_required
        )
    )

    @api.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    api._register_openapi_routes()

    with TestClient(api) as client:
        # staff_member_required redirects to admin login
        response = client.get("/docs", follow_redirects=False)
        assert response.status_code == 302, \
            f"Expected 302 redirect, got {response.status_code}"

        # Should redirect to admin login
        location = response.headers.get("location", "")
        assert "admin" in location.lower() or "login" in location.lower(), \
            f"Should redirect to admin login, got: {location}"


def test_openapi_django_auth_all_routes_protected():
    """Test that all OpenAPI routes are protected when django_auth is set."""
    api = BoltAPI(
        openapi_config=OpenAPIConfig(
            title="Test API",
            version="1.0.0",
            path="/docs",
            django_auth=True,
            render_plugins=[SwaggerRenderPlugin()]
        )
    )

    @api.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    api._register_openapi_routes()

    with TestClient(api) as client:
        # All doc routes should redirect to login (302)
        routes_to_test = [
            "/docs/openapi.json",
            "/docs/openapi.yaml",
            "/docs/openapi.yml",
            "/docs",
            "/docs/swagger",
        ]

        for route in routes_to_test:
            response = client.get(route, follow_redirects=False)
            assert response.status_code == 302, \
                f"Route {route} should redirect to login (302), got {response.status_code}"

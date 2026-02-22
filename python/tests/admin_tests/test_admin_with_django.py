"""
Tests for Django admin integration that actually use a Django project.

These tests configure Django properly and validate admin via ASGI mounts.
"""

import pytest

from django_bolt.api import BoltAPI
from django_bolt.testing import TestClient


@pytest.mark.django_db(transaction=True)
def test_admin_root_redirect():
    """Test /admin/ returns content (redirect or login page) via TestClient."""
    from django_bolt.admin.admin_detection import should_enable_admin  # noqa: PLC0415

    if not should_enable_admin():
        pytest.skip("Django admin not enabled")

    api = BoltAPI()
    api._register_admin_routes("127.0.0.1", 8000)

    @api.get("/test")
    async def test_route():
        return {"test": "ok"}

    # Check if admin mount was registered
    if not api._admin_routes_registered:
        pytest.skip("Admin mount was not registered")

    with TestClient(api, use_http_layer=True) as client:
        response = client.get("/admin/")

        print("\n[Admin Root Test]")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body length: {len(response.content)}")
        print(f"Body preview: {response.text[:300] if response.text else 'N/A'}")

        # Should return a valid response (redirect or login page)
        assert response.status_code in (200, 301, 302), f"Expected valid response, got {response.status_code}"

        # CRITICAL: Body should NOT be empty
        assert len(response.content) > 0, (
            f"Response body is EMPTY! Got {len(response.content)} bytes. Admin mount path is broken."
        )


@pytest.mark.django_db(transaction=True)
def test_admin_login_page():
    """Test /admin/login/ returns HTML page (not empty body) via TestClient."""
    from django_bolt.admin.admin_detection import should_enable_admin  # noqa: PLC0415

    if not should_enable_admin():
        pytest.skip("Django admin not enabled")

    api = BoltAPI()
    api._register_admin_routes("127.0.0.1", 8000)

    @api.get("/test")
    async def test_route():
        return {"test": "ok"}

    # Check if admin mount was registered
    if not api._admin_routes_registered:
        pytest.skip("Admin mount was not registered")

    with TestClient(api, use_http_layer=True) as client:
        response = client.get("/admin/login/")

        print("\n[Admin Login Test]")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body length: {len(response.content)}")
        print(f"Body preview: {response.text[:300]}")

        # Should return 200 OK
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # CRITICAL: Body should NOT be empty - THIS IS THE BUG
        assert len(response.content) > 0, (
            f"Admin login page body is EMPTY! Got {len(response.content)} bytes. Admin mount path is broken."
        )

        # Should be HTML
        content_type = response.headers.get("content-type", "")
        assert "html" in content_type.lower(), f"Expected HTML, got {content_type}"

        # Should contain login form
        body_text = response.text.lower()
        assert "login" in body_text or "django" in body_text, f"Expected login content, got: {body_text[:200]}"


class TestStaticRouteMetadata:
    """Tests for static route registration metadata.

    These tests verify that the static route registrar properly creates
    handler metadata with injectors, which is required by the dispatch system.
    """

    def test_static_route_has_injector(self):
        """Test that static routes are registered with an injector in metadata.

        This test verifies the fix for KeyError: 'injector' when accessing
        static files. The _dispatch method requires an injector for non-request-only
        handlers.
        """
        api = BoltAPI()
        # First register admin routes (required before static routes)
        api._register_admin_routes("127.0.0.1", 8000)
        # Then register static routes
        api._register_static_routes()

        # Find the static handler
        static_handler = None
        for _method, path, _handler_id, handler in api._routes:
            if "/static/" in path and "{path:path}" in path:
                static_handler = handler
                break

        assert static_handler is not None, "Static route should be registered"

        # Get metadata for the static handler (find handler_id from routes)
        handler_id = None
        for _method, path, hid, handler in api._routes:
            if handler == static_handler:
                handler_id = hid
                break
        assert handler_id is not None, "Static handler should be in routes"
        meta = api._handler_meta.get(handler_id)
        assert meta is not None, "Static handler should have metadata"

        # Verify injector exists (this is the key fix)
        assert "injector" in meta, "Static handler metadata must have 'injector' key"
        assert callable(meta["injector"]), "Injector must be callable"
        assert "injector_is_async" in meta, "Static handler metadata must have 'injector_is_async' key"
        assert meta["injector_is_async"] is False, "Static injector should be synchronous"

        # Verify other required metadata
        assert meta.get("mode") == "mixed", "Static handler should be in 'mixed' mode"
        assert meta.get("is_async") is True, "Static handler should be marked as async"
        assert "path" in meta.get("path_params", set()), "Static handler should have 'path' as path param"

    def test_static_injector_extracts_path(self):
        """Test that the static injector correctly extracts the path parameter."""
        api = BoltAPI()
        api._register_admin_routes("127.0.0.1", 8000)
        api._register_static_routes()

        # Find the static handler
        static_handler = None
        for _method, path, _handler_id, handler in api._routes:
            if "/static/" in path and "{path:path}" in path:
                static_handler = handler
                break

        assert static_handler is not None, "Static route should be registered"

        # Get metadata using handler_id from routes
        handler_id = None
        for _method, path, hid, handler in api._routes:
            if handler == static_handler:
                handler_id = hid
                break
        assert handler_id is not None, "Static handler should be in routes"
        meta = api._handler_meta[handler_id]
        injector = meta["injector"]

        # Test the injector with a mock request
        mock_request = {
            "params": {"path": "admin/css/base.css"},
            "query": {},
            "headers": {},
            "cookies": {},
        }

        args, kwargs = injector(mock_request)

        assert args == ["admin/css/base.css"], f"Injector should extract path, got {args}"
        assert kwargs == {}, f"Injector should return empty kwargs, got {kwargs}"

    def test_static_injector_handles_empty_path(self):
        """Test that the static injector handles missing path gracefully."""
        api = BoltAPI()
        api._register_admin_routes("127.0.0.1", 8000)
        api._register_static_routes()

        # Find the static handler
        static_handler = None
        for _method, path, _handler_id, handler in api._routes:
            if "/static/" in path and "{path:path}" in path:
                static_handler = handler
                break

        assert static_handler is not None, "Static route should be registered"

        # Get metadata using handler_id from routes
        handler_id = None
        for _method, path, hid, handler in api._routes:
            if handler == static_handler:
                handler_id = hid
                break
        assert handler_id is not None, "Static handler should be in routes"
        meta = api._handler_meta[handler_id]
        injector = meta["injector"]

        # Test with missing path param
        mock_request = {
            "params": {},
            "query": {},
            "headers": {},
            "cookies": {},
        }

        args, kwargs = injector(mock_request)

        assert args == [""], f"Injector should return empty string for missing path, got {args}"
        assert kwargs == {}, f"Injector should return empty kwargs, got {kwargs}"

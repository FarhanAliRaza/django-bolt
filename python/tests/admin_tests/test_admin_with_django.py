"""
Tests for Django admin integration that actually use a Django project.

These tests configure Django properly and will FAIL if ASGI bridge is broken.
"""

import asyncio

import pytest

from django_bolt.admin.asgi_bridge import ASGIFallbackHandler
from django_bolt.api import BoltAPI
from django_bolt.testing import TestClient


@pytest.mark.django_db(transaction=True)
def test_admin_root_redirect():
    """Test /admin/ returns content (redirect or login page) via TestClient."""
    from django_bolt.admin.admin_detection import should_enable_admin  # noqa: PLC0415
    if not should_enable_admin():
        pytest.skip("Django admin not enabled")

    api = BoltAPI()
    api._register_admin_routes('127.0.0.1', 8000)

    @api.get("/test")
    async def test_route():
        return {"test": "ok"}

    # Check if admin routes were registered
    admin_routes = [r for r in api._routes if '/admin' in r[1]]
    if not admin_routes:
        pytest.skip("Admin routes were not registered")

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
        assert len(response.content) > 0, f"Response body is EMPTY! Got {len(response.content)} bytes. ASGI bridge is BROKEN!"


@pytest.mark.django_db(transaction=True)
def test_admin_login_page():
    """Test /admin/login/ returns HTML page (not empty body) via TestClient."""
    from django_bolt.admin.admin_detection import should_enable_admin  # noqa: PLC0415
    if not should_enable_admin():
        pytest.skip("Django admin not enabled")

    api = BoltAPI()
    api._register_admin_routes('127.0.0.1', 8000)

    @api.get("/test")
    async def test_route():
        return {"test": "ok"}

    # Check if admin routes were registered
    admin_routes = [r for r in api._routes if '/admin' in r[1]]
    if not admin_routes:
        pytest.skip("Admin routes were not registered")

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
        assert len(response.content) > 0, f"Admin login page body is EMPTY! Got {len(response.content)} bytes. ASGI bridge is BROKEN!"

        # Should be HTML
        content_type = response.headers.get('content-type', '')
        assert 'html' in content_type.lower(), f"Expected HTML, got {content_type}"

        # Should contain login form
        body_text = response.text.lower()
        assert 'login' in body_text or 'django' in body_text, f"Expected login content, got: {body_text[:200]}"


@pytest.mark.django_db
def test_asgi_bridge_direct_with_real_django():
    """Test ASGI bridge directly with real Django configuration."""
    # Database is already set up by pytest-django
    handler = ASGIFallbackHandler(server_host="127.0.0.1", server_port=8000)

    request = {
        "method": "GET",
        "path": "/admin/login/",
        "body": b"",
        "params": {},
        "query": {},
        "headers": {"host": "127.0.0.1:8000"},
        "cookies": {},
        "context": None,
    }

    status, headers, body = asyncio.run(handler.handle_request(request))

    print("\n[ASGI Bridge Direct Test]")
    print(f"Status: {status}")
    print(f"Headers: {dict(headers)}")
    print(f"Body length: {len(body)}")
    print(f"Body preview: {body[:300]}")

    # Validate structure
    assert isinstance(status, int), f"Status should be int, got {type(status)}"
    assert isinstance(headers, list), f"Headers should be list, got {type(headers)}"
    assert isinstance(body, bytes), f"Body should be bytes, got {type(body)}"

    # Should return 200 OK
    assert status == 200, f"Expected 200, got {status}"

    # CRITICAL TEST: Body should NOT be empty - THIS WILL FAIL IF BUG EXISTS
    assert len(body) > 0, f"ASGI bridge returned EMPTY body! Expected HTML content. Body length: {len(body)}"

    # Should be HTML content
    body_text = body.decode('utf-8', errors='ignore')
    assert 'html' in body_text.lower(), f"Expected HTML content, got: {body_text[:100]}"
    assert 'django' in body_text.lower() or 'login' in body_text.lower(), "Expected Django admin content"


@pytest.mark.django_db
def test_asgi_bridge_admin_root():
    """Test ASGI bridge handles /admin/ root correctly."""
    handler = ASGIFallbackHandler(server_host="127.0.0.1", server_port=8000)

    request = {
        "method": "GET",
        "path": "/admin/",
        "body": b"",
        "params": {},
        "query": {},
        "headers": {"host": "127.0.0.1:8000"},
        "cookies": {},
        "context": None,
    }

    status, headers, body = asyncio.run(handler.handle_request(request))

    # Should redirect to login
    assert status in (301, 302), f"Expected redirect, got {status}"

    # Should have location header
    location = None
    for name, value in headers:
        if name.lower() == 'location':
            location = value
            break

    assert location is not None, "Redirect should have Location header"
    assert '/admin/login/' in location, f"Should redirect to login, got {location}"


@pytest.mark.django_db
def test_asgi_bridge_with_query_params():
    """Test ASGI bridge handles query parameters correctly."""
    handler = ASGIFallbackHandler(server_host="127.0.0.1", server_port=8000)

    request = {
        "method": "GET",
        "path": "/admin/login/",
        "body": b"",
        "params": {},
        "query": {"next": "/admin/"},
        "headers": {"host": "127.0.0.1:8000"},
        "cookies": {},
        "context": None,
    }

    status, headers, body = asyncio.run(handler.handle_request(request))

    # Should return 200 OK
    assert status == 200, f"Expected 200, got {status}"
    assert len(body) > 0, "Body should not be empty"


@pytest.mark.django_db
def test_asgi_bridge_post_request():
    """Test ASGI bridge handles POST requests correctly."""
    handler = ASGIFallbackHandler(server_host="127.0.0.1", server_port=8000)

    # POST request with form data
    form_data = b"username=admin&password=test123"

    request = {
        "method": "POST",
        "path": "/admin/login/",
        "body": form_data,
        "params": {},
        "query": {},
        "headers": {
            "host": "127.0.0.1:8000",
            "content-type": "application/x-www-form-urlencoded",
            "content-length": str(len(form_data)),
        },
        "cookies": {},
        "context": None,
    }

    status, headers, body = asyncio.run(handler.handle_request(request))

    # Should return response (even if login fails, it should process the request)
    assert isinstance(status, int), f"Status should be int, got {type(status)}"
    assert len(body) > 0, "Body should not be empty"


@pytest.mark.django_db
def test_asgi_bridge_404_path():
    """Test ASGI bridge handles non-existent admin paths correctly."""
    handler = ASGIFallbackHandler(server_host="127.0.0.1", server_port=8000)

    request = {
        "method": "GET",
        "path": "/admin/nonexistent/path/",
        "body": b"",
        "params": {},
        "query": {},
        "headers": {"host": "127.0.0.1:8000"},
        "cookies": {},
        "context": None,
    }

    status, headers, body = asyncio.run(handler.handle_request(request))

    # Django redirects unauthenticated users to login for non-existent admin paths
    # This is expected Django admin behavior
    assert status in (302, 404), f"Expected redirect or 404, got {status}"
    assert len(body) >= 0, "Response should have structure"


@pytest.mark.django_db
def test_asgi_bridge_with_cookies():
    """Test ASGI bridge handles cookies correctly."""
    handler = ASGIFallbackHandler(server_host="127.0.0.1", server_port=8000)

    request = {
        "method": "GET",
        "path": "/admin/login/",
        "body": b"",
        "params": {},
        "query": {},
        "headers": {
            "host": "127.0.0.1:8000",
            "cookie": "sessionid=abc123; csrftoken=xyz789",
        },
        "cookies": {
            "sessionid": "abc123",
            "csrftoken": "xyz789",
        },
        "context": None,
    }

    status, headers, body = asyncio.run(handler.handle_request(request))

    # Should return 200 OK
    assert status == 200, f"Expected 200, got {status}"
    assert len(body) > 0, "Body should not be empty"

    # Should set CSRF token cookie
    has_csrf = False
    for name, value in headers:
        if name.lower() == 'set-cookie' and 'csrftoken' in value:
            has_csrf = True
            break

    assert has_csrf, "Response should include CSRF token cookie"


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
        api._register_admin_routes('127.0.0.1', 8000)
        # Then register static routes
        api._register_static_routes()

        # Find the static handler
        static_handler = None
        for _method, path, _handler_id, handler in api._routes:
            if '/static/' in path and '{path:path}' in path:
                static_handler = handler
                break

        assert static_handler is not None, "Static route should be registered"

        # Get metadata for the static handler (find handler_id from routes)
        handler_id = None
        for method, path, hid, handler in api._routes:
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
        api._register_admin_routes('127.0.0.1', 8000)
        api._register_static_routes()

        # Find the static handler
        static_handler = None
        for _method, path, _handler_id, handler in api._routes:
            if '/static/' in path and '{path:path}' in path:
                static_handler = handler
                break

        assert static_handler is not None, "Static route should be registered"

        # Get metadata using handler_id from routes
        handler_id = None
        for method, path, hid, handler in api._routes:
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
        api._register_admin_routes('127.0.0.1', 8000)
        api._register_static_routes()

        # Find the static handler
        static_handler = None
        for _method, path, _handler_id, handler in api._routes:
            if '/static/' in path and '{path:path}' in path:
                static_handler = handler
                break

        assert static_handler is not None, "Static route should be registered"

        # Get metadata using handler_id from routes
        handler_id = None
        for method, path, hid, handler in api._routes:
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

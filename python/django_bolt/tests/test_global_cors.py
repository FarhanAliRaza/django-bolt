"""Tests for global CORS origins fallback functionality."""

import pytest
from django_bolt import BoltAPI
from django_bolt.middleware import cors
from django_bolt.testing import TestClient


def test_cors_uses_global_origins_when_no_route_config():
    """Test that global CORS origins are used when route has no specific config."""
    api = BoltAPI()

    # Route without CORS config (should use global) but with middleware enabled
    @api.get("/no-cors-config")
    @cors()  # Empty CORS config - should use global
    async def no_cors_endpoint():
        return {"message": "hello"}

    # Configure global CORS origins
    global_origins = ["https://example.com", "https://trusted.com"]

    with TestClient(api, use_http_layer=True, cors_allowed_origins=global_origins) as client:
        response = client.get(
            "/no-cors-config",
            headers={"Origin": "https://example.com"}
        )
        assert response.status_code == 200
        assert response.headers.get("Access-Control-Allow-Origin") == "https://example.com"


def test_cors_route_config_overrides_global():
    """Test that route-specific CORS config takes precedence over global."""
    api = BoltAPI()

    # Route with specific CORS config (should override global)
    @api.get("/with-cors-config")
    @cors(origins=["https://custom.com", "https://other.com"])
    async def with_cors_endpoint():
        return {"message": "hello"}

    # Global config has different origins
    global_origins = ["https://example.com", "https://trusted.com"]

    with TestClient(api, use_http_layer=True, cors_allowed_origins=global_origins) as client:
        response = client.get(
            "/with-cors-config",
            headers={"Origin": "https://custom.com"}
        )
        assert response.status_code == 200
        assert response.headers.get("Access-Control-Allow-Origin") == "https://custom.com"


def test_cors_rejects_unlisted_origin_with_global_config():
    """Test that unlisted origins are rejected even with global config."""
    api = BoltAPI()

    @api.get("/no-cors-config")
    @cors()  # Empty CORS config - should use global
    async def endpoint():
        return {"message": "hello"}

    global_origins = ["https://example.com", "https://trusted.com"]

    with TestClient(api, use_http_layer=True, cors_allowed_origins=global_origins) as client:
        response = client.get(
            "/no-cors-config",
            headers={"Origin": "https://evil.com"}
        )
        # Should not have CORS headers for unlisted origin
        assert "Access-Control-Allow-Origin" not in response.headers


def test_cors_allows_wildcard_in_global_config():
    """Test that wildcard in global config allows any origin."""
    api = BoltAPI()

    @api.get("/no-cors-config")
    @cors()  # Empty CORS config - should use global
    async def endpoint():
        return {"message": "hello"}

    # Wildcard in global config
    global_origins = ["*"]

    with TestClient(api, use_http_layer=True, cors_allowed_origins=global_origins) as client:
        response = client.get(
            "/no-cors-config",
            headers={"Origin": "https://any-domain.com"}
        )
        assert response.status_code == 200
        assert response.headers.get("Access-Control-Allow-Origin") == "*"


def test_cors_empty_global_config_no_headers():
    """Test that no CORS headers are added when global config is empty and no route config."""
    api = BoltAPI()

    @api.get("/no-cors-config")
    async def endpoint():
        return {"message": "hello"}

    # Empty global origins, no route middleware
    with TestClient(api, use_http_layer=True, cors_allowed_origins=[]) as client:
        response = client.get(
            "/no-cors-config",
            headers={"Origin": "https://example.com"}
        )
        assert "Access-Control-Allow-Origin" not in response.headers


def test_cors_middleware_enabled_but_no_origins_configured():
    """Test that when CORS middleware is enabled but no origins configured, requests succeed but have no headers."""
    api = BoltAPI()

    @api.get("/cors-no-origins")
    @cors()  # CORS enabled but no origins in decorator and no global
    async def endpoint():
        return {"message": "hello"}

    # No global origins
    with TestClient(api, use_http_layer=True, cors_allowed_origins=[]) as client:
        # Regular request with Origin header
        response = client.get(
            "/cors-no-origins",
            headers={"Origin": "https://example.com"}
        )
        # Request succeeds but no CORS headers
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" not in response.headers

        # Preflight should be rejected
        preflight = client.options(
            "/cors-no-origins",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            }
        )
        # Preflight is rejected with 403
        assert preflight.status_code == 403


def test_preflight_uses_global_origins():
    """Test that preflight requests use global origins."""
    api = BoltAPI()

    @api.post("/no-cors-config")
    @cors()  # Empty CORS config - should use global
    async def endpoint():
        return {"message": "hello"}

    # Also need to register OPTIONS handler or it will be auto-generated
    @api.options("/no-cors-config")
    @cors()  # Empty CORS config - should use global
    async def options_endpoint():
        return {"message": "options"}

    global_origins = ["https://example.com", "https://trusted.com"]

    with TestClient(api, use_http_layer=True, cors_allowed_origins=global_origins) as client:
        response = client.options(
            "/no-cors-config",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        # Preflight is intercepted by CORS middleware and returns 204
        assert response.status_code == 204
        assert response.headers.get("Access-Control-Allow-Origin") == "https://example.com"
        assert "POST" in response.headers.get("Access-Control-Allow-Methods", "")

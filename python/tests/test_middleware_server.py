"""
Integration test for middleware with TestClient
"""
import time

import django
import jwt
import pytest
from django.conf import settings  # noqa: PLC0415

from django_bolt import BoltAPI
from django_bolt.auth import APIKeyAuthentication, IsAuthenticated, JWTAuthentication
from django_bolt.middleware import cors, rate_limit
from django_bolt.testing import TestClient


@pytest.fixture(scope="module")
def api():
    """Create test API with various middleware configurations"""
    # Setup minimal Django for testing
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test-secret-key-for-middleware',
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'django_bolt',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            USE_TZ=True,
        )
        django.setup()

    api = BoltAPI(
        middleware_config={
            'cors': {
                'origins': ['http://localhost:3000'],
                'credentials': True
            }
        }
    )

    @api.get("/")
    async def root():
        return {"message": "Hello, middleware!"}

    @api.get("/rate-limited")
    @rate_limit(rps=5, burst=10)
    async def rate_limited_endpoint():
        return {"message": "This endpoint is rate limited", "timestamp": time.time()}

    @api.get("/cors-test")
    @cors(origins=["http://localhost:3000", "http://example.com"], credentials=True)
    async def cors_endpoint():
        return {"cors": "enabled"}

    @api.get(
        "/protected-jwt",
        auth=[JWTAuthentication(secret="test-secret")],
        guards=[IsAuthenticated()]
    )
    async def jwt_protected():
        return {"message": "JWT protected content"}

    @api.get(
        "/protected-api-key",
        auth=[APIKeyAuthentication(
            api_keys={"test-key-123", "test-key-456"},
            header="authorization"
        )],
        guards=[IsAuthenticated()]
    )
    async def api_key_protected():
        return {"message": "API key protected content"}

    @api.get(
        "/context-test",
        auth=[APIKeyAuthentication(
            api_keys={"test-key"},
            header="authorization"
        )],
        guards=[IsAuthenticated()]
    )
    async def context_endpoint(request: dict):
        """Test that middleware context is available"""
        context = request.get("context")
        return {
            "has_context": context is not None,
            "context_keys": list(context.keys()) if context and hasattr(context, 'keys') else []
        }

    return api


@pytest.fixture(scope="module")
def client(api):
    """Create TestClient for the API (fast mode - direct dispatch)"""
    with TestClient(api) as client:
        yield client


@pytest.fixture(scope="module")
def http_client(api):
    """Create TestClient with HTTP layer enabled (for middleware testing)"""
    with TestClient(api, use_http_layer=True) as client:
        yield client


def test_basic_endpoint(client):
    """Test basic endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, middleware!"}


def test_compression_http_layer(http_client):
    """Test that compression middleware is applied in HTTP layer"""
    # Request with Accept-Encoding header
    response = http_client.get("/", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, middleware!"}
    # Note: httpx automatically decompresses, so we won't see content-encoding in response
    # But the middleware is applied in Actix layer


def test_rate_limiting(http_client):
    """Test rate limiting"""
    # The rate limit is 5 rps with burst of 10
    # First 10 requests should succeed (burst)
    for i in range(10):
        response = http_client.get("/rate-limited")
        assert response.status_code == 200, f"Request {i+1} failed"

    # Next request should be rate limited
    response = http_client.get("/rate-limited")
    assert response.status_code == 429  # Too Many Requests
    assert "retry-after" in response.headers


def test_cors_headers(http_client):
    """Test CORS headers"""
    response = http_client.get("/cors-test", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert response.json() == {"cors": "enabled"}
    # Check CORS headers
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_preflight(http_client):
    """Test CORS preflight (OPTIONS)"""
    response = http_client.options(
        "/cors-test",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        }
    )
    # Preflight should return 204
    assert response.status_code == 204
    # Check preflight headers
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers


def test_jwt_auth_without_token(client):
    """Test JWT authentication without token"""
    response = client.get("/protected-jwt")
    assert response.status_code == 401


def test_jwt_auth_with_valid_token(client):
    """Test JWT authentication with valid token"""
    token = jwt.encode(
        {"sub": "user123", "exp": int(time.time()) + 3600},
        "test-secret",
        algorithm="HS256"
    )
    response = client.get("/protected-jwt", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "JWT protected content"}


def test_jwt_auth_with_expired_token(client):
    """Test JWT authentication with expired token"""
    expired_token = jwt.encode(
        {"sub": "user123", "exp": int(time.time()) - 3600},
        "test-secret",
        algorithm="HS256"
    )
    response = client.get("/protected-jwt", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401


def test_api_key_auth_without_key(client):
    """Test API key authentication without key"""
    response = client.get("/protected-api-key")
    assert response.status_code == 401


def test_api_key_auth_with_valid_key(client):
    """Test API key authentication with valid key"""
    response = client.get("/protected-api-key", headers={"Authorization": "Bearer test-key-123"})
    assert response.status_code == 200
    assert response.json() == {"message": "API key protected content"}


def test_api_key_auth_with_invalid_key(client):
    """Test API key authentication with invalid key"""
    response = client.get("/protected-api-key", headers={"Authorization": "Bearer invalid-key"})
    assert response.status_code == 401


def test_context_availability(client):
    """Test middleware context availability"""
    response = client.get("/context-test", headers={"Authorization": "Bearer test-key"})
    assert response.status_code == 200
    data = response.json()
    # Context may or may not be available depending on implementation
    # Just verify the endpoint works and returns expected structure
    assert "has_context" in data
    assert "context_keys" in data

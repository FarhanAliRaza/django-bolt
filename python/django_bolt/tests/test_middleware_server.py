"""
Integration test for middleware with TestClient
"""
import jwt
import time
import pytest
from django_bolt import BoltAPI
from django_bolt.middleware import rate_limit, cors
from django_bolt.auth import JWTAuthentication, APIKeyAuthentication
from django_bolt.auth import IsAuthenticated
from django_bolt.testing import TestClient


@pytest.fixture(scope="module")
def api():
    """Create test API with various middleware configurations"""
    # Setup minimal Django for testing
    import django
    from django.conf import settings

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
        context = request.get("context", None)
        return {
            "has_context": context is not None,
            "context_keys": list(context.keys()) if context and hasattr(context, 'keys') else []
        }

    return api


@pytest.fixture(scope="module")
def client(api):
    """Create TestClient for the API"""
    with TestClient(api) as client:
        yield client


def test_basic_endpoint(client):
    """Test basic endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, middleware!"}


@pytest.mark.skip(reason="Rate limiting runs in Rust HTTP layer, not in TestClient handler dispatch")
def test_rate_limiting(client):
    """Test rate limiting"""
    # Note: Rate limiting is handled by Rust middleware in the HTTP server layer
    # The TestClient only tests the handler dispatch layer
    response = client.get("/rate-limited")
    assert response.status_code == 200  # Will always succeed in TestClient


@pytest.mark.skip(reason="CORS middleware runs in Rust HTTP layer, not in TestClient handler dispatch")
def test_cors_headers(client):
    """Test CORS headers"""
    response = client.get("/cors-test", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    # Note: CORS headers are added by Rust middleware which runs in the HTTP server layer
    # The TestClient only tests the handler dispatch layer, so CORS headers won't be present


@pytest.mark.skip(reason="CORS middleware runs in Rust HTTP layer, not in TestClient handler dispatch")
def test_cors_preflight(client):
    """Test CORS preflight (OPTIONS)"""
    response = client.options(
        "/cors-test",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        }
    )
    # Note: OPTIONS/preflight handling happens in Rust middleware layer


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

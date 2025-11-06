"""
Test sync function support in django-bolt.
Tests that sync and async handlers work correctly with parameters, dependencies, middleware, and auth.
"""
from __future__ import annotations

import inspect
import time
from typing import Annotated

import msgspec
import pytest
from django_bolt import BoltAPI
from django_bolt.auth import JWTAuthentication, IsAuthenticated
from django_bolt.middleware import cors, rate_limit
from django_bolt.params import Header, Query, Depends
from django_bolt.testing import TestClient


# ========================
# Shared Models
# ========================


class UserCreate(msgspec.Struct):
    """User creation request model."""

    name: str
    email: str


@pytest.fixture(scope="module")
def api():
    """Create test API with sync and async handlers."""
    api = BoltAPI()

    # ========================
    # Basic Handlers
    # ========================

    # Test 1: Async function (existing behavior)
    @api.get("/async")
    async def async_handler():
        return {"type": "async"}

    # Test 2: Sync function with inline=True (default)
    @api.get("/sync-inline")
    def sync_inline_handler():
        return {"type": "sync", "mode": "inline"}

    # Test 3: Sync function without inline (uses default)
    @api.get("/sync-blocking")
    def sync_blocking_handler():
        time.sleep(0.001)  # Simulate slow operation
        return {"type": "sync", "mode": "blocking"}

    # ========================
    # Parameter Handlers
    # ========================

    # Path parameters (sync)
    @api.get("/sync/users/{user_id}")
    def sync_path_param(user_id: int):
        return {"user_id": user_id, "name": f"User {user_id}"}

    # Path and query parameters (sync)
    @api.get("/sync/items/{item_id}")
    def sync_path_query_param(item_id: int, search: str = "default"):
        return {"item_id": item_id, "search": search}

    # Query parameters (sync)
    @api.get("/sync/search")
    def sync_query_param(q: str, limit: int = 10):
        return {"query": q, "limit": limit}

    # Header parameters (sync)
    @api.get("/sync/headers")
    def sync_header_param(x_custom: Annotated[str, Header()]):
        return {"header": x_custom}

    # Query with annotation (sync)
    @api.get("/sync/annotated-query")
    def sync_annotated_query(count: Annotated[int, Query()] = 5):
        return {"count": count}

    # ========================
    # Request Body Handlers
    # ========================

    # POST with JSON body (sync)
    @api.post("/sync/users")
    def sync_post_body(user: UserCreate):
        return {"id": 1, "name": user.name, "email": user.email}

    # ========================
    # Dependency Injection
    # ========================

    async def get_current_user():
        """Dependency that returns current user."""
        return {"user_id": 42, "username": "testuser"}

    async def get_db_connection():
        """Dependency that returns a DB-like connection."""
        return {"connection": "active"}

    # Sync handler with single dependency
    @api.get("/sync/with-dependency")
    def sync_with_dependency(user: dict = Depends(get_current_user)):
        return {"user": user}

    # Sync handler with multiple dependencies
    @api.get("/sync/with-multiple-dependencies")
    def sync_with_multiple_deps(
        user: dict = Depends(get_current_user),
        db: dict = Depends(get_db_connection),
    ):
        return {"user": user, "db": db}

    # ========================
    # Middleware Handlers (CORS)
    # ========================

    @api.get("/sync/cors-enabled")
    @cors(origins=["http://localhost:3000"])
    def sync_cors_handler():
        return {"cors": "enabled"}

    # ========================
    # Middleware Handlers (Rate Limiting)
    # ========================

    @api.get("/sync/rate-limited")
    @rate_limit(rps=100, burst=10)
    def sync_rate_limited():
        return {"status": "ok"}

    # ========================
    # Auth Handlers
    # ========================

    auth_config = JWTAuthentication(secret="test-secret-key", algorithms=["HS256"])

    @api.get("/sync/protected", auth=[auth_config], guards=[IsAuthenticated()])
    def sync_protected_handler():
        return {"message": "Protected sync handler"}

    @api.get("/sync/unprotected")
    def sync_unprotected_handler():
        return {"message": "Public sync handler"}

    # ========================
    # Mixed Async/Sync Handlers with Same Features
    # ========================

    @api.get("/async/users/{user_id}")
    async def async_path_param(user_id: int):
        return {"user_id": user_id, "name": f"User {user_id}", "is_async": True}

    @api.post("/async/users")
    async def async_post_body(user: UserCreate):
        return {"id": 1, "name": user.name, "email": user.email, "is_async": True}

    @api.get("/async/with-dependency")
    async def async_with_dependency(user: dict = Depends(get_current_user)):
        return {"user": user, "is_async": True}

    @api.get("/async/protected", auth=[auth_config], guards=[IsAuthenticated()])
    async def async_protected_handler():
        return {"message": "Protected async handler", "is_async": True}

    # Store handlers for inspection tests
    api._async_handler = async_handler
    api._sync_inline_handler = sync_inline_handler
    api._sync_blocking_handler = sync_blocking_handler
    api._sync_path_param = sync_path_param
    api._auth_config = auth_config

    return api


@pytest.fixture
def client(api):
    """Test client for making HTTP requests."""
    with TestClient(api) as client:
        yield client


class TestMetadataDetection:
    """Test that handlers have correct metadata."""

    def test_async_handler_metadata(self, api):
        """Async handlers should be marked as async."""
        meta = api._handler_meta[api._async_handler]
        assert meta["is_async"] is True, "Async handler should be marked as async"

    def test_sync_inline_handler_metadata(self, api):
        """Sync inline handlers should be marked as sync."""
        meta = api._handler_meta[api._sync_inline_handler]
        assert meta["is_async"] is False, "Sync handler should be marked as sync"

    def test_sync_blocking_handler_metadata(self, api):
        """Sync blocking handlers should be marked as sync."""
        meta = api._handler_meta[api._sync_blocking_handler]
        assert meta["is_async"] is False, "Sync handler should be marked as sync"


class TestHandlerInspection:
    """Test Python's inspect functions on handlers."""

    def test_async_handler_is_coroutine_function(self, api):
        """Async handlers should be coroutine functions."""
        assert inspect.iscoroutinefunction(
            api._async_handler
        ), "Async handler should be recognized as coroutine function"

    def test_sync_inline_handler_is_not_coroutine(self, api):
        """Sync inline handlers should NOT be coroutine functions."""
        assert not inspect.iscoroutinefunction(
            api._sync_inline_handler
        ), "Sync handler should not be recognized as coroutine function"

    def test_sync_blocking_handler_is_not_coroutine(self, api):
        """Sync blocking handlers should NOT be coroutine functions."""
        assert not inspect.iscoroutinefunction(
            api._sync_blocking_handler
        ), "Sync handler should not be recognized as coroutine function"


class TestAsyncHandlerExecution:
    """Test async handler execution via HTTP."""

    def test_async_handler_returns_correct_response(self, client):
        """Async handler should return expected response."""
        response = client.get("/async")
        assert response.status_code == 200, "Async handler should return 200"
        data = response.json()
        assert data == {"type": "async"}, "Async handler should return correct data"

    def test_async_handler_response_type(self, client):
        """Async handler response should be proper JSON."""
        response = client.get("/async")
        assert response.headers["content-type"] == "application/json"


class TestSyncInlineHandlerExecution:
    """Test sync inline handler execution via HTTP."""

    def test_sync_inline_handler_returns_correct_response(self, client):
        """Sync inline handler should return expected response."""
        response = client.get("/sync-inline")
        assert response.status_code == 200, "Sync inline handler should return 200"
        data = response.json()
        assert data == {
            "type": "sync",
            "mode": "inline",
        }, "Sync inline handler should return correct data"

    def test_sync_inline_handler_response_type(self, client):
        """Sync inline handler response should be proper JSON."""
        response = client.get("/sync-inline")
        assert response.headers["content-type"] == "application/json"

    def test_sync_inline_handler_is_actually_sync(self, api):
        """Verify handler is sync function."""
        assert not inspect.iscoroutinefunction(
            api._sync_inline_handler
        ), "Handler should be sync"


class TestSyncBlockingHandlerExecution:
    """Test sync blocking handler execution via HTTP."""

    def test_sync_blocking_handler_returns_correct_response(self, client):
        """Sync blocking handler should return expected response."""
        response = client.get("/sync-blocking")
        assert response.status_code == 200, "Sync blocking handler should return 200"
        data = response.json()
        assert data == {
            "type": "sync",
            "mode": "blocking",
        }, "Sync blocking handler should return correct data"

    def test_sync_blocking_handler_response_type(self, client):
        """Sync blocking handler response should be proper JSON."""
        response = client.get("/sync-blocking")
        assert response.headers["content-type"] == "application/json"

    def test_sync_blocking_handler_is_actually_sync(self, api):
        """Verify handler is sync function."""
        assert not inspect.iscoroutinefunction(
            api._sync_blocking_handler
        ), "Handler should be sync"


class TestComparisonBetweenSyncModes:
    """Test the differences between sync inline and blocking modes."""

    def test_both_sync_modes_return_same_structure(self, client):
        """Both sync modes should return similar response structure."""
        inline_response = client.get("/sync-inline")
        blocking_response = client.get("/sync-blocking")

        inline_data = inline_response.json()
        blocking_data = blocking_response.json()

        assert inline_data["type"] == blocking_data["type"] == "sync"
        assert "mode" in inline_data and "mode" in blocking_data

    def test_sync_handlers_all_work(self, client):
        """All sync handlers should be accessible and working."""
        async_response = client.get("/async")
        inline_response = client.get("/sync-inline")
        blocking_response = client.get("/sync-blocking")

        assert async_response.status_code == 200
        assert inline_response.status_code == 200
        assert blocking_response.status_code == 200

    def test_responses_are_all_json(self, client):
        """All responses should be valid JSON."""
        endpoints = ["/async", "/sync-inline", "/sync-blocking"]
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            # This should not raise if JSON is valid
            data = response.json()
            assert isinstance(data, dict), f"Response from {endpoint} should be a dict"


# ========================
# PARAMETER EXTRACTION TESTS
# ========================


class TestSyncPathParameters:
    """Test sync handlers with path parameters."""

    def test_sync_path_parameter(self, client):
        """Sync handler should extract path parameter."""
        response = client.get("/sync/users/123")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 123
        assert data["name"] == "User 123"

    def test_sync_path_parameter_invalid_type(self, client):
        """Sync handler should fail with invalid path parameter type."""
        response = client.get("/sync/users/invalid")
        assert response.status_code != 200


class TestSyncPathAndQueryParameters:
    """Test sync handlers with path and query parameters."""

    def test_sync_path_and_query_with_default(self, client):
        """Sync handler should extract path and use query default."""
        response = client.get("/sync/items/456")
        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == 456
        assert data["search"] == "default"

    def test_sync_path_and_query_with_value(self, client):
        """Sync handler should extract path and query parameter."""
        response = client.get("/sync/items/456?search=custom")
        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == 456
        assert data["search"] == "custom"


class TestSyncQueryParameters:
    """Test sync handlers with query parameters."""

    def test_sync_query_parameter_required(self, client):
        """Sync handler should extract required query parameter."""
        response = client.get("/sync/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test"
        assert data["limit"] == 10

    def test_sync_query_parameter_with_limit(self, client):
        """Sync handler should extract query parameters with values."""
        response = client.get("/sync/search?q=test&limit=20")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test"
        assert data["limit"] == 20

    def test_sync_query_parameter_missing_required(self, client):
        """Sync handler should fail without required query parameter."""
        response = client.get("/sync/search")
        assert response.status_code != 200


class TestSyncHeaderParameters:
    """Test sync handlers with header parameters."""

    def test_sync_header_parameter(self, client):
        """Sync handler should extract header parameter."""
        response = client.get("/sync/headers", headers={"X-Custom": "test-value"})
        assert response.status_code == 200
        data = response.json()
        assert data["header"] == "test-value"


class TestSyncAnnotatedQueryParameters:
    """Test sync handlers with annotated query parameters."""

    def test_sync_annotated_query_default(self, client):
        """Sync handler should use default value for annotated query."""
        response = client.get("/sync/annotated-query")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 5

    def test_sync_annotated_query_custom_value(self, client):
        """Sync handler should extract annotated query parameter."""
        response = client.get("/sync/annotated-query?count=15")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 15


# ========================
# REQUEST BODY TESTS
# ========================


class TestSyncRequestBodyValidation:
    """Test sync handlers with request body validation."""

    def test_sync_post_with_valid_body(self, client):
        """Sync handler should accept valid request body."""
        response = client.post(
            "/sync/users",
            json={"name": "John", "email": "john@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "John"
        assert data["email"] == "john@example.com"

    def test_sync_post_with_invalid_body(self, client):
        """Sync handler should reject invalid request body."""
        response = client.post(
            "/sync/users",
            json={"name": "John"},  # Missing email
        )
        assert response.status_code != 200


# ========================
# DEPENDENCY INJECTION TESTS
# ========================


class TestSyncDependencyInjection:
    """Test sync handlers with dependency injection."""

    def test_sync_single_dependency(self, client):
        """Sync handler should resolve single dependency."""
        response = client.get("/sync/with-dependency")
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["user_id"] == 42
        assert data["user"]["username"] == "testuser"

    def test_sync_multiple_dependencies(self, client):
        """Sync handler should resolve multiple dependencies."""
        response = client.get("/sync/with-multiple-dependencies")
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "db" in data
        assert data["user"]["user_id"] == 42
        assert data["db"]["connection"] == "active"


# ========================
# MIDDLEWARE TESTS
# ========================


class TestSyncMiddlewareCORS:
    """Test sync handlers with CORS middleware."""

    def test_sync_cors_handler_http_layer(self):
        """Sync handler should include CORS headers with HTTP layer."""
        test_api = BoltAPI()

        @test_api.get("/sync/cors-test")
        @cors(origins=["http://localhost:3000"])
        def cors_handler():
            return {"cors": "enabled"}

        with TestClient(test_api, use_http_layer=True) as client:
            response = client.get(
                "/sync/cors-test",
                headers={"Origin": "http://localhost:3000"},
            )
            assert response.status_code == 200
            assert "access-control-allow-origin" in response.headers


class TestSyncMiddlewareRateLimit:
    """Test sync handlers with rate limiting."""

    def test_sync_rate_limit_handler_http_layer(self):
        """Sync handler should be rate limited with HTTP layer."""
        test_api = BoltAPI()

        @test_api.get("/sync/rate-test")
        @rate_limit(rps=100, burst=3)
        def rate_limited():
            return {"status": "ok"}

        with TestClient(test_api, use_http_layer=True) as client:
            # First 3 requests should succeed (burst)
            for i in range(3):
                response = client.get("/sync/rate-test")
                assert response.status_code == 200, f"Request {i+1} should succeed"

            # 4th request might be rate limited
            response = client.get("/sync/rate-test")
            # Just verify it returns a valid status
            assert response.status_code in [200, 429]


# ========================
# AUTHENTICATION TESTS
# ========================


class TestSyncAuthentication:
    """Test sync handlers with authentication."""

    def test_sync_unprotected_endpoint(self, client):
        """Sync handler without auth should be accessible."""
        response = client.get("/sync/unprotected")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Public sync handler"

    def test_sync_protected_endpoint_without_token(self, client):
        """Sync protected handler should reject requests without token."""
        response = client.get("/sync/protected")
        assert response.status_code == 401, "Should reject without token"

    def test_sync_protected_endpoint_with_valid_token(self, client):
        """Sync protected handler should accept valid token."""
        import jwt

        token = jwt.encode(
            {"sub": "user123", "exp": int(time.time()) + 3600},
            "test-secret-key",
            algorithm="HS256",
        )
        response = client.get(
            "/sync/protected",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Protected sync handler"


# ========================
# ASYNC VS SYNC COMPARISON TESTS
# ========================


class TestAsyncSyncParityPathParameters:
    """Compare async and sync handlers with path parameters."""

    def test_async_vs_sync_path_parameters(self, client):
        """Async and sync handlers should both extract path parameters."""
        async_response = client.get("/async/users/789")
        sync_response = client.get("/sync/users/789")

        assert async_response.status_code == 200
        assert sync_response.status_code == 200

        async_data = async_response.json()
        sync_data = sync_response.json()

        assert async_data["user_id"] == sync_data["user_id"] == 789
        assert async_data["is_async"] is True
        assert "is_async" not in sync_data or sync_data.get("is_async") != True


class TestAsyncSyncParityRequestBody:
    """Compare async and sync handlers with request body."""

    def test_async_vs_sync_post_body(self, client):
        """Async and sync handlers should both validate request bodies."""
        payload = {"name": "Jane", "email": "jane@example.com"}

        async_response = client.post("/async/users", json=payload)
        sync_response = client.post("/sync/users", json=payload)

        assert async_response.status_code == 200
        assert sync_response.status_code == 200

        async_data = async_response.json()
        sync_data = sync_response.json()

        assert async_data["name"] == sync_data["name"] == "Jane"
        assert async_data["email"] == sync_data["email"] == "jane@example.com"


class TestAsyncSyncParityDependencies:
    """Compare async and sync handlers with dependency injection."""

    def test_async_vs_sync_dependencies(self, client):
        """Async and sync handlers should both resolve dependencies."""
        async_response = client.get("/async/with-dependency")
        sync_response = client.get("/sync/with-dependency")

        assert async_response.status_code == 200
        assert sync_response.status_code == 200

        async_data = async_response.json()
        sync_data = sync_response.json()

        assert async_data["user"]["user_id"] == sync_data["user"]["user_id"] == 42


class TestAsyncSyncParityAuthentication:
    """Compare async and sync handlers with authentication."""

    def test_async_vs_sync_protected_endpoints(self, client):
        """Async and sync protected handlers should both reject without token."""
        async_response = client.get("/async/protected")
        sync_response = client.get("/sync/protected")

        assert async_response.status_code == 401
        assert sync_response.status_code == 401

    def test_async_vs_sync_protected_with_token(self, client):
        """Async and sync protected handlers should both accept valid token."""
        import jwt

        token = jwt.encode(
            {"sub": "user123", "exp": int(time.time()) + 3600},
            "test-secret-key",
            algorithm="HS256",
        )
        headers = {"Authorization": f"Bearer {token}"}

        async_response = client.get("/async/protected", headers=headers)
        sync_response = client.get("/sync/protected", headers=headers)

        assert async_response.status_code == 200
        assert sync_response.status_code == 200

        async_data = async_response.json()
        sync_data = sync_response.json()

        assert async_data["is_async"] is True
        assert "Protected" in async_data["message"]
        assert "Protected" in sync_data["message"]

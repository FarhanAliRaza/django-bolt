"""
Test request.get() method default parameter behavior.
"""
import time

import jwt

from django_bolt import BoltAPI
from django_bolt.auth import JWTAuthentication  # noqa: PLC0415
from django_bolt.auth.guards import IsAuthenticated  # noqa: PLC0415
from django_bolt.testing import TestClient


def test_request_get_default_behavior():
    """
    Test that request.get() properly handles default parameter:
    - Default parameter is optional
    - Returns default value when key doesn't exist
    - Returns default value for 'auth'/'context' when None
    - Returns actual values for known keys
    """
    api = BoltAPI()

    @api.get("/test-request-get")
    async def test_handler(request):
        # Test 1: Default parameter is optional (no default provided)
        non_existent_no_default = request.get("non_existent_key")

        # Test 2: Default value is returned when key doesn't exist
        non_existent_with_default = request.get("non_existent_key", "my_default")

        # Test 3: Default value for auth/context when None
        auth_no_default = request.get("auth")
        auth_with_default = request.get("auth", {"default": "auth"})
        context_no_default = request.get("context")
        context_with_default = request.get("context", {"default": "context"})

        # Test 4: Known keys return actual values
        method = request.get("method")
        path = request.get("path")

        # Test 5: Known keys ignore default parameter
        method_with_default = request.get("method", "ignored_default")

        return {
            "non_existent_no_default": non_existent_no_default,
            "non_existent_with_default": non_existent_with_default,
            "auth_no_default": auth_no_default,
            "auth_with_default": auth_with_default,
            "context_no_default": context_no_default,
            "context_with_default": context_with_default,
            "method": method,
            "path": path,
            "method_with_default": method_with_default,
        }

    with TestClient(api) as client:
        response = client.get("/test-request-get")
        assert response.status_code == 200

        data = response.json()

        # Debug: Print what we actually got
        print(f"\nDEBUG - auth_no_default: {data['auth_no_default']!r} (type: {type(data['auth_no_default'])})")
        print(f"DEBUG - auth_with_default: {data['auth_with_default']!r}")

        # Assertion 1: Default parameter is optional, returns None
        assert data["non_existent_no_default"] is None, \
            "request.get() without default should return None for non-existent key"

        # Assertion 2: Default value is returned when key doesn't exist
        assert data["non_existent_with_default"] == "my_default", \
            "request.get() should return provided default value for non-existent key"

        # Assertion 3: Default value for auth/context when None
        assert data["auth_no_default"] is None, \
            "request.get('auth') should return None when no auth context exists"
        assert data["auth_with_default"] == {"default": "auth"}, \
            "request.get('auth', default) should return default when no auth context exists"
        assert data["context_no_default"] is None, \
            "request.get('context') should return None when no context exists"
        assert data["context_with_default"] == {"default": "context"}, \
            "request.get('context', default) should return default when no context exists"

        # Assertion 4: Known keys return actual values
        assert data["method"] == "GET", \
            "request.get('method') should return actual HTTP method"
        assert data["path"] == "/test-request-get", \
            "request.get('path') should return actual request path"

        # Assertion 5: Known keys ignore default parameter
        assert data["method_with_default"] == "GET", \
            "request.get('method', default) should return actual method, not default"


def test_request_get_with_auth_context():
    """
    Test that request.get() returns actual auth context when present.
    """
    api = BoltAPI()

    @api.get(
        "/test-auth-context",
        auth=[JWTAuthentication(secret="test-secret")],
        guards=[IsAuthenticated()]
    )
    async def test_handler(request):
        # When auth is present, should return actual auth object, not default
        auth_no_default = request.get("auth")
        auth_with_default = request.get("auth", {"default": "should_be_ignored"})

        return {
            "auth_no_default": auth_no_default,
            "auth_with_default": auth_with_default,
        }

    with TestClient(api) as client:
        # Create a valid JWT token
        payload = {
            "sub": "123",
            "user_id": 123,
            "exp": int(time.time()) + 3600,
            "iat": int(time.time())
        }
        token = jwt.encode(payload, "test-secret", algorithm="HS256")

        response = client.get(
            "/test-auth-context",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        data = response.json()

        # Assertion: When auth exists, should return actual auth object, not default
        assert data["auth_no_default"] is not None, \
            "request.get('auth') should return auth object when present"
        assert "user_id" in data["auth_no_default"], \
            "Auth object should contain user_id"
        assert data["auth_no_default"]["user_id"] == "123", \
            "Auth object should have correct user_id (as string from JWT sub claim)"

        assert data["auth_with_default"] is not None, \
            "request.get('auth', default) should return auth object when present, not default"
        assert data["auth_with_default"]["user_id"] == "123", \
            "Auth object should be returned even when default is provided"

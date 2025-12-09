"""
Test type definitions and protocols.
"""
import time

import jwt
import msgspec

from django_bolt import BoltAPI, Request
from django_bolt.auth import IsAuthenticated, JWTAuthentication
from django_bolt.testing import TestClient


class UserCreate(msgspec.Struct):
    name: str
    email: str
    age: int


def test_request_protocol_has_expected_attributes():
    """Test that Request protocol has expected methods and properties."""
    # Verify protocol has expected attributes
    # Note: Protocol defines the interface, PyRequest (Rust) implements it
    assert hasattr(Request, "method")
    assert hasattr(Request, "path")
    assert hasattr(Request, "body")
    assert hasattr(Request, "context")
    assert hasattr(Request, "user")
    assert hasattr(Request, "state")
    assert hasattr(Request, "headers")
    assert hasattr(Request, "cookies")
    assert hasattr(Request, "query")


def test_request_type_in_handler():
    """Test that Request type can be used in handler signatures."""
    api = BoltAPI()

    @api.get("/test")
    async def handler(request: Request):
        # Test that request object works with type hints
        method = request.method
        path = request.path
        auth = request.get("auth")
        headers = request.get("headers", {})

        return {
            "method": method,
            "path": path,
            "has_auth": auth is not None,
            "headers_count": len(headers)
        }

    with TestClient(api) as client:
        response = client.get("/test")
        assert response.status_code == 200

        data = response.json()
        assert data["method"] == "GET"
        assert data["path"] == "/test"
        assert data["has_auth"] is False
        assert data["headers_count"] > 0


def test_request_with_validated_body():
    """Test Request type with msgspec validated body parameter."""
    api = BoltAPI()

    @api.post("/users")
    async def create_user(request: Request, user: UserCreate):
        # Both request and validated body should work
        method = request.method
        auth = request.get("auth")

        # Validated body has full type safety
        return {
            "method": method,
            "has_auth": auth is not None,
            "user_name": user.name,
            "user_email": user.email,
            "user_age": user.age
        }

    with TestClient(api) as client:
        response = client.post(
            "/users",
            json={"name": "John", "email": "john@example.com", "age": 30}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["method"] == "POST"
        assert data["has_auth"] is False
        assert data["user_name"] == "John"
        assert data["user_email"] == "john@example.com"
        assert data["user_age"] == 30


def test_request_with_auth_context():
    """Test Request type with authentication context."""
    api = BoltAPI()

    @api.get(
        "/protected",
        auth=[JWTAuthentication(secret="test-secret")],
        guards=[IsAuthenticated()]
    )
    async def protected_route(request: Request):
        # Type-safe access to auth context
        auth = request.get("auth", {})
        user_id = auth.get("user_id")
        is_staff = auth.get("is_staff", False)
        backend = auth.get("auth_backend")

        return {
            "user_id": user_id,
            "is_staff": is_staff,
            "backend": backend
        }

    with TestClient(api) as client:
        # Create valid JWT token
        payload = {
            "sub": "123",
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
            "is_staff": True
        }
        token = jwt.encode(payload, "test-secret", algorithm="HS256")

        response = client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["user_id"] == "123"
        assert data["is_staff"] is True
        assert data["backend"] == "jwt"


def test_request_dict_style_access():
    """Test Request supports dict-style access."""
    api = BoltAPI()

    @api.get("/test")
    async def handler(request: Request):
        # Dict-style access should work
        method = request["method"]
        path = request["path"]
        headers = request["headers"]

        return {
            "method": method,
            "path": path,
            "has_headers": len(headers) > 0
        }

    with TestClient(api) as client:
        response = client.get("/test")
        assert response.status_code == 200

        data = response.json()
        assert data["method"] == "GET"
        assert data["path"] == "/test"
        assert data["has_headers"] is True


def test_request_get_with_defaults():
    """Test Request.get() with default values."""
    api = BoltAPI()

    @api.get("/test")
    async def handler(request: Request):
        # Test default values
        auth = request.get("auth")  # Should be None
        auth_with_default = request.get("auth", {"default": "value"})
        context = request.get("context")  # Should be None
        context_with_default = request.get("context", {"default": "ctx"})

        # Method should never be None
        method = request.get("method")

        return {
            "auth": auth,
            "auth_with_default": auth_with_default,
            "context": context,
            "context_with_default": context_with_default,
            "method": method
        }

    with TestClient(api) as client:
        response = client.get("/test")
        assert response.status_code == 200

        data = response.json()
        assert data["auth"] is None
        assert data["auth_with_default"] == {"default": "value"}
        assert data["context"] is None
        assert data["context_with_default"] == {"default": "ctx"}
        assert data["method"] == "GET"


def test_request_property_access():
    """Test Request property access."""
    api = BoltAPI()

    @api.get("/test")
    async def handler(request: Request):
        # Property access should work
        method_prop = request.method
        path_prop = request.path
        body_prop = request.body
        context_prop = request.context

        return {
            "method": method_prop,
            "path": path_prop,
            "body_length": len(body_prop),
            "has_context": context_prop is not None
        }

    with TestClient(api) as client:
        response = client.get("/test")
        assert response.status_code == 200

        data = response.json()
        assert data["method"] == "GET"
        assert data["path"] == "/test"
        assert data["body_length"] == 0  # GET has empty body
        assert data["has_context"] is False


def test_request_import_from_main_module():
    """Test that Request can be imported from django_bolt.

    This test intentionally uses a local import to verify the import mechanism works.
    """
    from django_bolt import Request as ImportedRequest  # noqa: PLC0415 - testing import mechanism

    # Should be the same class (ImportedRequest is the same as the module-level Request)
    # This test verifies the import works, even though we compare with module-level Request
    assert ImportedRequest is Request

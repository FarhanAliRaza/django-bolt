"""
Tests for type-safe dependency injection.
"""
from __future__ import annotations

import pytest
import msgspec
from typing import Annotated
from django_bolt import BoltAPI, Depends, Header, Query
from django_bolt.testing import TestClient


class User(msgspec.Struct):
    """User model."""
    id: int
    username: str
    email: str


class Config(msgspec.Struct):
    """App configuration."""
    max_items: int
    timeout: int


# Module-level dependency functions (required for type resolution)

async def get_current_user_from_token(token: Annotated[str, Header(alias="Authorization")]) -> User:
    """
    Dependency that extracts user from authorization token.

    Returns properly typed User object for IDE autocomplete and type checking.
    """
    # In real app, would validate token and fetch from database
    if token == "valid-token":
        return User(id=1, username="john", email="john@example.com")
    raise ValueError("Invalid token")


async def get_admin_user(token: Annotated[str, Header(alias="Authorization")]) -> User:
    """Dependency that requires admin token."""
    if token == "admin-token":
        return User(id=2, username="admin", email="admin@example.com")
    raise ValueError("Not an admin")


async def get_page_size(limit: int = Query(10, ge=1, le=100)) -> int:
    """Dependency that validates and returns page size."""
    return limit


async def require_admin(user: Annotated[User, Depends(get_current_user_from_token)]) -> User:
    """Nested dependency that checks if user is admin."""
    if user.username != "admin":
        raise ValueError("Admin required")
    return user


# Global counter for testing caching
_call_counts = {}


async def expensive_dependency() -> dict:
    """Simulates expensive operation that should be cached."""
    _call_counts.setdefault("expensive", 0)
    _call_counts["expensive"] += 1
    return {"value": _call_counts["expensive"]}


async def non_cached_dependency() -> int:
    """Dependency that shouldn't be cached."""
    _call_counts.setdefault("non_cached", 0)
    _call_counts["non_cached"] += 1
    return _call_counts["non_cached"]


async def get_request_info(request) -> dict:
    """Dependency that extracts info from request."""
    return {
        "method": request.get("method"),
        "path": request.get("path"),
    }


async def get_optional_user(
    token: str | None = Header(None, alias="Authorization")
) -> User | None:
    """Optional dependency that returns None if no token provided."""
    if token == "valid-token":
        return User(id=1, username="john", email="john@example.com")
    return None


async def get_config() -> Config:
    """Dependency that returns configuration."""
    return Config(max_items=100, timeout=30)


def test_basic_dependency_injection():
    """Test basic dependency injection with type safety."""
    api = BoltAPI()

    @api.get("/profile")
    async def get_profile(user: Annotated[User, Depends(get_current_user_from_token)]):
        # Type checker knows user is User, so we get autocomplete for .username, .email, etc.
        return {"username": user.username, "email": user.email}

    client = TestClient(api)

    # Valid token
    response = client.get("/profile", headers={"Authorization": "valid-token"})
    assert response.status_code == 200
    assert response.json() == {"username": "john", "email": "john@example.com"}

    # Missing token (dependencies raise 500 on missing required params)
    response = client.get("/profile")
    assert response.status_code == 500


def test_multiple_dependencies():
    """Test using multiple dependencies in the same handler."""
    api = BoltAPI()

    @api.get("/users")
    async def list_users(
        current_user: Annotated[User, Depends(get_current_user_from_token)],
        page_size: Annotated[int, Depends(get_page_size)]
    ):
        # Both dependencies are properly typed
        return {
            "requester": current_user.username,
            "page_size": page_size,
            "users": []
        }

    client = TestClient(api)

    response = client.get("/users?limit=20", headers={"Authorization": "valid-token"})
    assert response.status_code == 200
    assert response.json() == {
        "requester": "john",
        "page_size": 20,
        "users": []
    }


def test_nested_dependencies():
    """Test dependencies that depend on other dependencies."""
    api = BoltAPI()

    @api.delete("/users/{user_id}")
    async def delete_user(
        user_id: int,
        admin: Annotated[User, Depends(require_admin)]
    ):
        # admin is properly typed as User
        return {"deleted_by": admin.username, "user_id": user_id}

    client = TestClient(api)

    # This will fail because 'john' is not admin
    response = client.delete("/users/123", headers={"Authorization": "valid-token"})
    assert response.status_code == 500  # ValueError is caught


def test_dependency_caching():
    """Test that dependencies are cached per request."""
    api = BoltAPI()

    # Reset counter
    _call_counts["expensive"] = 0

    @api.get("/test")
    async def test_endpoint(
        dep1: Annotated[dict, Depends(expensive_dependency)],
        dep2: Annotated[dict, Depends(expensive_dependency)],
    ):
        # Both should return same cached value
        return {"dep1": dep1, "dep2": dep2}

    client = TestClient(api)

    response = client.get("/test")
    assert response.status_code == 200
    result = response.json()
    # Both deps should have the same value (cached)
    assert result["dep1"]["value"] == result["dep2"]["value"] == 1
    # Function was only called once
    assert _call_counts["expensive"] == 1


def test_dependency_no_caching():
    """Test dependencies with use_cache=False."""
    api = BoltAPI()

    # Reset counter
    _call_counts["non_cached"] = 0

    @api.get("/test")
    async def test_endpoint(
        dep1: Annotated[int, Depends(non_cached_dependency, use_cache=False)],
        dep2: Annotated[int, Depends(non_cached_dependency, use_cache=False)],
    ):
        return {"dep1": dep1, "dep2": dep2}

    client = TestClient(api)

    response = client.get("/test")
    assert response.status_code == 200
    result = response.json()
    # Different values because not cached
    assert result["dep1"] == 1
    assert result["dep2"] == 2
    assert _call_counts["non_cached"] == 2


def test_dependency_with_request_parameter():
    """Test dependency that receives the raw request object."""
    api = BoltAPI()

    @api.get("/info")
    async def get_info(info: Annotated[dict, Depends(get_request_info)]):
        return info

    client = TestClient(api)

    response = client.get("/info")
    assert response.status_code == 200
    result = response.json()
    assert result["method"] == "GET"
    assert result["path"] == "/info"


def test_optional_dependency():
    """Test optional dependencies with default values."""
    api = BoltAPI()

    @api.get("/optional")
    async def optional_endpoint(
        user: Annotated[User | None, Depends(get_optional_user)]
    ):
        if user:
            return {"username": user.username}
        return {"username": "guest"}

    client = TestClient(api)

    # With token
    response = client.get("/optional", headers={"Authorization": "valid-token"})
    assert response.status_code == 200
    assert response.json() == {"username": "john"}

    # Without token
    response = client.get("/optional")
    assert response.status_code == 200
    assert response.json() == {"username": "guest"}


def test_dependency_with_struct_return():
    """Test that dependencies returning msgspec.Struct work correctly."""
    api = BoltAPI()

    @api.get("/config")
    async def get_config_endpoint(config: Annotated[Config, Depends(get_config)]):
        # config is properly typed as Config
        return {"max_items": config.max_items, "timeout": config.timeout}

    client = TestClient(api)

    response = client.get("/config")
    assert response.status_code == 200
    assert response.json() == {"max_items": 100, "timeout": 30}


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

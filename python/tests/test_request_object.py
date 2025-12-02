"""
Tests for the type-safe Request[UserT, AuthT, StateT] class.
"""
from __future__ import annotations

import pytest
from typing import TypedDict

from django_bolt.request import Request, State


class MyState(TypedDict, total=False):
    """Custom state type for testing."""
    request_id: str
    start_time: float
    custom_data: dict


class TestRequestClass:
    """Tests for the Request class."""

    def test_request_creation(self):
        """Test basic request creation."""
        req = Request(
            method="GET",
            path="/test",
            headers={"content-type": "application/json"},
            query={"page": "1"},
        )

        assert req.method == "GET"
        assert req.path == "/test"
        assert req.headers["content-type"] == "application/json"
        assert req.query["page"] == "1"

    def test_request_defaults(self):
        """Test request defaults."""
        req = Request()

        assert req.method == "GET"
        assert req.path == "/"
        assert req.body == b""
        assert req.headers == {}
        assert req.cookies == {}
        assert req.query == {}
        assert req.params == {}

    def test_request_dict_access(self):
        """Test dict-style access."""
        req = Request(method="POST", path="/api/users")

        # Dict-style get
        assert req["method"] == "POST"
        assert req["path"] == "/api/users"
        assert req.get("method") == "POST"
        assert req.get("nonexistent") is None
        assert req.get("nonexistent", "default") == "default"

    def test_request_user_property(self):
        """Test user property."""
        req = Request()

        # No user set - should raise AttributeError
        with pytest.raises(AttributeError, match="request.user is not available"):
            _ = req.user

        # Set user
        req.user = {"id": 1, "username": "test"}
        assert req.user == {"id": 1, "username": "test"}

        # has_user check
        assert req.has_user() is True

    def test_request_auth_property(self):
        """Test auth property."""
        req = Request()

        # No auth set - should raise AttributeError
        with pytest.raises(AttributeError, match="request.auth is not available"):
            _ = req.auth

        # Set auth
        req.auth = {"user_id": "123", "permissions": ["read", "write"]}
        assert req.auth["user_id"] == "123"

        # has_auth check
        assert req.has_auth() is True

    def test_request_state(self):
        """Test state property."""
        req = Request()

        # State starts empty
        assert len(req.state) == 0

        # Add to state using dict-style
        req.state["request_id"] = "abc123"
        assert req.state["request_id"] == "abc123"

        # Add to state using attribute-style
        req.state.start_time = 12345.0
        assert req.state.start_time == 12345.0

    def test_request_from_dict(self):
        """Test creating request from dict."""
        data = {
            "method": "POST",
            "path": "/api/create",
            "body": b'{"name": "test"}',
            "headers": {"content-type": "application/json"},
            "query": {"debug": "true"},
            "params": {"id": "123"},
        }

        req = Request.from_dict(data)

        assert req.method == "POST"
        assert req.path == "/api/create"
        assert req.body == b'{"name": "test"}'
        assert req.headers["content-type"] == "application/json"
        assert req.query["debug"] == "true"
        assert req.params["id"] == "123"

    def test_request_to_dict(self):
        """Test converting request to dict."""
        req = Request(
            method="PUT",
            path="/api/update",
            body=b'{"updated": true}',
            headers={"authorization": "Bearer token"},
        )
        req.user = {"id": 1}
        req.auth = {"token": "xxx"}

        data = req.to_dict()

        assert data["method"] == "PUT"
        assert data["path"] == "/api/update"
        assert data["body"] == b'{"updated": true}'
        assert data["user"] == {"id": 1}
        assert data["auth"] == {"token": "xxx"}

    def test_request_contains(self):
        """Test 'in' operator."""
        req = Request()

        assert "method" in req
        assert "path" in req
        assert "body" in req
        assert "headers" in req
        assert "user" in req
        assert "auth" in req
        assert "state" in req
        assert "nonexistent" not in req

    def test_request_repr(self):
        """Test string representation."""
        req = Request(method="DELETE", path="/api/item/123")
        repr_str = repr(req)

        assert "DELETE" in repr_str
        assert "/api/item/123" in repr_str
        assert "has_user=False" in repr_str


class TestStateClass:
    """Tests for the State class."""

    def test_state_creation(self):
        """Test basic state creation."""
        data = {"foo": "bar", "count": 42}
        state = State(data)

        assert state["foo"] == "bar"
        assert state["count"] == 42

    def test_state_dict_access(self):
        """Test dict-style access."""
        state = State({})

        # Set using dict-style
        state["key1"] = "value1"
        assert state["key1"] == "value1"

        # Get with default
        assert state.get("key1") == "value1"
        assert state.get("missing") is None
        assert state.get("missing", "default") == "default"

    def test_state_attribute_access(self):
        """Test attribute-style access."""
        state = State({"name": "test"})

        # Read using attribute
        assert state.name == "test"

        # Write using attribute
        state.value = 123
        assert state.value == 123
        assert state["value"] == 123

    def test_state_attribute_error(self):
        """Test AttributeError for missing attributes."""
        state = State({})

        with pytest.raises(AttributeError, match="has no attribute 'missing'"):
            _ = state.missing

    def test_state_iteration(self):
        """Test iteration over state."""
        state = State({"a": 1, "b": 2, "c": 3})

        keys = list(state)
        assert set(keys) == {"a", "b", "c"}

        assert len(state) == 3

    def test_state_contains(self):
        """Test 'in' operator."""
        state = State({"exists": True})

        assert "exists" in state
        assert "missing" not in state

    def test_state_delete(self):
        """Test deletion."""
        state = State({"key": "value"})

        # Dict-style delete
        del state["key"]
        assert "key" not in state

        # Attribute-style delete
        state["another"] = "val"
        del state.another
        assert "another" not in state

    def test_state_methods(self):
        """Test dict methods."""
        state = State({"a": 1, "b": 2})

        assert list(state.keys()) == ["a", "b"]
        assert list(state.values()) == [1, 2]
        assert list(state.items()) == [("a", 1), ("b", 2)]

        # Pop
        val = state.pop("a")
        assert val == 1
        assert "a" not in state

        # Update
        state.update({"c": 3, "d": 4})
        assert state["c"] == 3
        assert state["d"] == 4

        # Setdefault
        state.setdefault("e", 5)
        assert state["e"] == 5

        state.setdefault("e", 10)  # Shouldn't change
        assert state["e"] == 5

    def test_state_clear(self):
        """Test clear method."""
        state = State({"a": 1, "b": 2})
        state.clear()

        assert len(state) == 0

    def test_state_bool(self):
        """Test boolean evaluation."""
        empty = State({})
        filled = State({"key": "value"})

        assert not empty
        assert filled

    def test_state_repr(self):
        """Test string representation."""
        state = State({"test": "data"})
        repr_str = repr(state)

        assert "State" in repr_str
        assert "'test'" in repr_str


class TestRequestWithTyping:
    """Tests for Request with type parameters."""

    def test_typed_request_user(self):
        """Test typed user access."""
        class User:
            def __init__(self, id: int, username: str):
                self.id = id
                self.username = username

        user = User(id=1, username="testuser")
        req: Request[User, dict, dict] = Request()
        req.user = user

        # Type checker would know req.user is User
        assert req.user.id == 1
        assert req.user.username == "testuser"

    def test_typed_request_auth(self):
        """Test typed auth access."""
        class JWTClaims(TypedDict):
            sub: str
            exp: int
            permissions: list

        claims: JWTClaims = {
            "sub": "user123",
            "exp": 1234567890,
            "permissions": ["read", "write"],
        }

        req: Request[None, JWTClaims, dict] = Request()
        req.auth = claims

        # Type checker would know req.auth is JWTClaims
        assert req.auth["sub"] == "user123"
        assert req.auth["exp"] == 1234567890

    def test_typed_request_state(self):
        """Test typed state access."""
        req: Request[None, None, MyState] = Request()
        req.state["request_id"] = "abc123"
        req.state["start_time"] = 12345.0

        # Type checker would know about MyState fields
        assert req.state["request_id"] == "abc123"
        assert req.state.start_time == 12345.0


class TestMiddlewareIntegration:
    """Tests for middleware integration with Request."""

    def test_middleware_adds_to_state(self):
        """Test that middleware can add data to request state."""
        req = Request()

        # Simulate middleware adding data
        req.state["request_id"] = "12345"
        req.state["start_time"] = 1000.0

        # Verify data is accessible
        assert req.state["request_id"] == "12345"
        assert req.state.start_time == 1000.0

    def test_middleware_sets_user(self):
        """Test that middleware can set user."""
        class MockUser:
            username = "admin"
            is_authenticated = True

        req = Request()
        assert req.has_user() is False

        # Middleware sets user
        req.user = MockUser()

        assert req.has_user() is True
        assert req.user.username == "admin"

    def test_get_user_with_default(self):
        """Test get_user with default value."""
        req = Request()

        # No user set
        default_user = {"id": 0, "anonymous": True}
        user = req.get_user(default_user)
        assert user == default_user

        # User is set
        req.user = {"id": 1, "username": "test"}
        user = req.get_user(default_user)
        assert user == {"id": 1, "username": "test"}

    def test_get_auth_with_default(self):
        """Test get_auth with default value."""
        req = Request()

        # No auth set
        default_auth = {}
        auth = req.get_auth(default_auth)
        assert auth == default_auth

        # Auth is set
        req.auth = {"token": "abc"}
        auth = req.get_auth(default_auth)
        assert auth == {"token": "abc"}

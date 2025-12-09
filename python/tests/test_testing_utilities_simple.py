"""Simple test for django-bolt testing utilities.

Tests the new TestClient in a single comprehensive test to avoid
router re-initialization issues (the Rust global router can only be set once).
"""
from typing import Annotated

import msgspec

from django_bolt import BoltAPI
from django_bolt.param_functions import Header
from django_bolt.testing import TestClient


def test_test_client_comprehensive():
    """Comprehensive test of TestClient functionality."""
    api = BoltAPI()

    # Test 1: Simple GET
    @api.get("/hello")
    async def hello():
        return {"message": "world"}

    # Test 2: Path parameters
    @api.get("/users/{user_id}")
    async def get_user(user_id: int):
        return {"id": user_id, "name": f"User {user_id}"}

    # Test 3: Query parameters
    @api.get("/search")
    async def search(q: str, limit: int = 10):
        return {"query": q, "limit": limit}

    # Test 4: POST with body
    class UserCreate(msgspec.Struct):
        name: str
        email: str

    @api.post("/users")
    async def create_user(user: UserCreate):
        return {"id": 1, "name": user.name, "email": user.email}

    # Test 5: Headers
    @api.get("/with-header")
    async def with_header(x_custom: Annotated[str, Header()]):
        return {"header_value": x_custom}

    # Test 6: Custom status code
    @api.post("/created", status_code=201)
    async def create():
        return {"created": True}

    # Test 7: Different methods on same path
    @api.get("/resource")
    async def get_resource():
        return {"method": "GET"}

    @api.post("/resource")
    async def create_resource():
        return {"method": "POST"}

    # Now run all tests using one client
    with TestClient(api) as client:
        # Test 1: Simple GET
        response = client.get("/hello")
        assert response.status_code == 200
        assert response.json() == {"message": "world"}
        print("✓ Simple GET works")

        # Test 2: Path parameters
        response = client.get("/users/123")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 123
        assert data["name"] == "User 123"
        print("✓ Path parameters work")

        # Test 3: Query parameters
        response = client.get("/search?q=test&limit=20")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test"
        assert data["limit"] == 20
        print("✓ Query parameters work")

        # Test 3b: Query parameters with defaults
        response = client.get("/search?q=test2")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test2"
        assert data["limit"] == 10
        print("✓ Query parameters with defaults work")

        # Test 4: POST with JSON body
        response = client.post("/users", json={"name": "John", "email": "john@example.com"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "John"
        assert data["email"] == "john@example.com"
        print("✓ POST with JSON body works")

        # Test 5: Headers
        response = client.get("/with-header", headers={"X-Custom": "test-value"})
        assert response.status_code == 200
        assert response.json() == {"header_value": "test-value"}
        print("✓ Headers work")

        # Test 6: Custom status code
        response = client.post("/created")
        assert response.status_code == 201
        assert response.json() == {"created": True}
        print("✓ Custom status codes work")

        # Test 7: Different methods
        assert client.get("/resource").json() == {"method": "GET"}
        assert client.post("/resource").json() == {"method": "POST"}
        print("✓ Multiple HTTP methods work")

        # Test 8: 404
        response = client.get("/nonexistent")
        assert response.status_code == 404
        print("✓ 404 for non-existent routes works")

    print("\n✅ All test client features working correctly!")

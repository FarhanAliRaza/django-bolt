"""
Tests for runtime parameter validation constraints.
"""
from __future__ import annotations

import pytest
from typing import Annotated
from django_bolt import BoltAPI, Query, Path, Header
from django_bolt.testing import TestClient


def test_numeric_gt_constraint():
    """Test greater than (gt) constraint."""
    api = BoltAPI()

    @api.get("/items")
    async def get_items(limit: Annotated[int, Query(gt=0)]):
        return {"limit": limit}

    client = TestClient(api)

    # Valid: limit > 0
    response = client.get("/items?limit=10")
    assert response.status_code == 200
    assert response.json() == {"limit": 10}

    # Invalid: limit <= 0
    response = client.get("/items?limit=0")
    assert response.status_code == 422
    assert "greater than 0" in response.json()["detail"]

    response = client.get("/items?limit=-5")
    assert response.status_code == 422
    assert "greater than 0" in response.json()["detail"]


def test_numeric_ge_constraint():
    """Test greater than or equal (ge) constraint."""
    api = BoltAPI()

    @api.get("/items")
    async def get_items(limit: Annotated[int, Query(ge=1)]):
        return {"limit": limit}

    client = TestClient(api)

    # Valid: limit >= 1
    response = client.get("/items?limit=1")
    assert response.status_code == 200

    response = client.get("/items?limit=10")
    assert response.status_code == 200

    # Invalid: limit < 1
    response = client.get("/items?limit=0")
    assert response.status_code == 422


def test_numeric_lt_constraint():
    """Test less than (lt) constraint."""
    api = BoltAPI()

    @api.get("/items")
    async def get_items(limit: Annotated[int, Query(lt=100)]):
        return {"limit": limit}

    client = TestClient(api)

    # Valid: limit < 100
    response = client.get("/items?limit=50")
    assert response.status_code == 200

    # Invalid: limit >= 100
    response = client.get("/items?limit=100")
    assert response.status_code == 422

    response = client.get("/items?limit=200")
    assert response.status_code == 422


def test_numeric_le_constraint():
    """Test less than or equal (le) constraint."""
    api = BoltAPI()

    @api.get("/items")
    async def get_items(limit: Annotated[int, Query(le=100)]):
        return {"limit": limit}

    client = TestClient(api)

    # Valid: limit <= 100
    response = client.get("/items?limit=100")
    assert response.status_code == 200

    response = client.get("/items?limit=50")
    assert response.status_code == 200

    # Invalid: limit > 100
    response = client.get("/items?limit=101")
    assert response.status_code == 422


def test_numeric_range_constraint():
    """Test combined numeric constraints (ge + le)."""
    api = BoltAPI()

    @api.get("/items")
    async def get_items(page: Annotated[int, Query(ge=1, le=100)]):
        return {"page": page}

    client = TestClient(api)

    # Valid: 1 <= page <= 100
    response = client.get("/items?page=1")
    assert response.status_code == 200

    response = client.get("/items?page=50")
    assert response.status_code == 200

    response = client.get("/items?page=100")
    assert response.status_code == 200

    # Invalid: page < 1
    response = client.get("/items?page=0")
    assert response.status_code == 422

    # Invalid: page > 100
    response = client.get("/items?page=101")
    assert response.status_code == 422


def test_multiple_of_constraint():
    """Test multiple_of constraint."""
    api = BoltAPI()

    @api.get("/items")
    async def get_items(quantity: Annotated[int, Query(multiple_of=10)]):
        return {"quantity": quantity}

    client = TestClient(api)

    # Valid: multiples of 10
    response = client.get("/items?quantity=10")
    assert response.status_code == 200

    response = client.get("/items?quantity=100")
    assert response.status_code == 200

    # Invalid: not multiples of 10
    response = client.get("/items?quantity=15")
    assert response.status_code == 422

    response = client.get("/items?quantity=7")
    assert response.status_code == 422


def test_string_min_length_constraint():
    """Test min_length constraint for strings."""
    api = BoltAPI()

    @api.get("/users")
    async def get_users(username: Annotated[str, Query(min_length=3)]):
        return {"username": username}

    client = TestClient(api)

    # Valid: length >= 3
    response = client.get("/users?username=abc")
    assert response.status_code == 200

    response = client.get("/users?username=abcdef")
    assert response.status_code == 200

    # Invalid: length < 3
    response = client.get("/users?username=ab")
    assert response.status_code == 422
    assert "at least 3" in response.json()["detail"]


def test_string_max_length_constraint():
    """Test max_length constraint for strings."""
    api = BoltAPI()

    @api.get("/users")
    async def get_users(username: Annotated[str, Query(max_length=10)]):
        return {"username": username}

    client = TestClient(api)

    # Valid: length <= 10
    response = client.get("/users?username=short")
    assert response.status_code == 200

    response = client.get("/users?username=exactly10c")
    assert response.status_code == 200

    # Invalid: length > 10
    response = client.get("/users?username=thisistoolong")
    assert response.status_code == 422
    assert "at most 10" in response.json()["detail"]


def test_string_length_range_constraint():
    """Test combined min_length and max_length constraints."""
    api = BoltAPI()

    @api.get("/users")
    async def get_users(username: Annotated[str, Query(min_length=3, max_length=20)]):
        return {"username": username}

    client = TestClient(api)

    # Valid: 3 <= length <= 20
    response = client.get("/users?username=abc")
    assert response.status_code == 200

    response = client.get("/users?username=validusername")
    assert response.status_code == 200

    # Invalid: length < 3
    response = client.get("/users?username=ab")
    assert response.status_code == 422

    # Invalid: length > 20
    response = client.get("/users?username=thisusernameiswaytoolong")
    assert response.status_code == 422


def test_pattern_constraint():
    """Test regex pattern constraint."""
    api = BoltAPI()

    @api.get("/users")
    async def get_users(email: Annotated[str, Query(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")]):
        return {"email": email}

    client = TestClient(api)

    # Valid: matches pattern
    response = client.get("/users?email=user@example.com")
    assert response.status_code == 200

    response = client.get("/users?email=john.doe@company.org")
    assert response.status_code == 200

    # Invalid: doesn't match pattern
    response = client.get("/users?email=notanemail")
    assert response.status_code == 422
    assert "does not match pattern" in response.json()["detail"]

    response = client.get("/users?email=@example.com")
    assert response.status_code == 422
    assert "does not match pattern" in response.json()["detail"]


def test_path_parameter_constraints():
    """Test constraints on path parameters."""
    api = BoltAPI()

    @api.get("/users/{user_id}")
    async def get_user(user_id: Annotated[int, Path(ge=1, le=999999)]):
        return {"user_id": user_id}

    client = TestClient(api)

    # Valid
    response = client.get("/users/123")
    assert response.status_code == 200
    assert response.json() == {"user_id": 123}

    # Invalid: out of range
    response = client.get("/users/0")
    assert response.status_code == 422

    response = client.get("/users/1000000")
    assert response.status_code == 422


def test_header_constraints():
    """Test constraints on header parameters."""
    api = BoltAPI()

    @api.get("/items")
    async def get_items(
        x_request_id: Annotated[str, Header(min_length=10, max_length=36)]
    ):
        return {"request_id": x_request_id}

    client = TestClient(api)

    # Valid
    response = client.get("/items", headers={"X-Request-ID": "1234567890"})
    assert response.status_code == 200

    # Invalid: too short
    response = client.get("/items", headers={"X-Request-ID": "short"})
    assert response.status_code == 422


def test_optional_parameter_with_constraints():
    """Test that constraints are only validated when value is provided."""
    api = BoltAPI()

    @api.get("/items")
    async def get_items(limit: Annotated[int | None, Query(gt=0, le=100)] = None):
        return {"limit": limit}

    client = TestClient(api)

    # Valid: no parameter (optional)
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == {"limit": None}

    # Valid: within constraints
    response = client.get("/items?limit=50")
    assert response.status_code == 200
    assert response.json() == {"limit": 50}

    # Invalid: violates constraints
    response = client.get("/items?limit=0")
    assert response.status_code == 422

    response = client.get("/items?limit=101")
    assert response.status_code == 422


def test_multiple_constraints_on_same_parameter():
    """Test multiple constraints on the same parameter."""
    api = BoltAPI()

    @api.get("/items")
    async def get_items(
        code: Annotated[str, Query(min_length=6, max_length=6, pattern=r"^[A-Z0-9]+$")]
    ):
        return {"code": code}

    client = TestClient(api)

    # Valid: matches all constraints
    response = client.get("/items?code=ABC123")
    assert response.status_code == 200

    # Invalid: wrong length
    response = client.get("/items?code=ABC12")
    assert response.status_code == 422

    response = client.get("/items?code=ABC1234")
    assert response.status_code == 422

    # Invalid: wrong pattern (lowercase)
    response = client.get("/items?code=abc123")
    assert response.status_code == 422


def test_float_constraints():
    """Test constraints on float parameters."""
    api = BoltAPI()

    @api.get("/products")
    async def get_products(
        price_min: Annotated[float, Query(ge=0.0)],
        price_max: Annotated[float, Query(le=1000.0)]
    ):
        return {"price_min": price_min, "price_max": price_max}

    client = TestClient(api)

    # Valid
    response = client.get("/products?price_min=10.5&price_max=99.99")
    assert response.status_code == 200

    # Invalid: negative price_min
    response = client.get("/products?price_min=-5&price_max=100")
    assert response.status_code == 422

    # Invalid: price_max too high
    response = client.get("/products?price_min=0&price_max=1001")
    assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

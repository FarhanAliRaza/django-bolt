"""Helper functions for creating test clients."""
from __future__ import annotations

from typing import Any

from django_bolt import BoltAPI
from django_bolt.testing.client import TestClient


def create_test_client(
    api: BoltAPI,
    base_url: str = "http://testserver.local",
    raise_server_exceptions: bool = True,
    bootstrap_django: bool = True,
    **kwargs: Any,
) -> TestClient:
    """Create a synchronous test client.

    Args:
        api: BoltAPI instance to test
        base_url: Base URL for requests
        raise_server_exceptions: If True, raise handler exceptions instead of 500 responses
        **kwargs: Additional httpx.Client arguments

    Returns:
        TestClient instance

    Example:
        from django_bolt import BoltAPI
        from django_bolt.testing import create_test_client

        api = BoltAPI()

        @api.get("/users/{user_id}")
        async def get_user(user_id: int):
            return {"id": user_id, "name": "Test User"}

        def test_get_user():
            with create_test_client(api) as client:
                response = client.get("/users/123")
                assert response.status_code == 200
                assert response.json()["id"] == 123
    """
    return TestClient(
        api=api,
        base_url=base_url,
        raise_server_exceptions=raise_server_exceptions,
        bootstrap_django=bootstrap_django,
        **kwargs,
    )

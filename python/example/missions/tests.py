"""Tests for missions API endpoints."""
from __future__ import annotations

import pytest

from django_bolt.testing import TestClient

from missions.api import api
from missions.models import Astronaut, Mission


@pytest.fixture(autouse=True)
def clean_db(db):
    """Clean database before each test."""
    Astronaut.objects.all().delete()
    Mission.objects.all().delete()
    yield
    Astronaut.objects.all().delete()
    Mission.objects.all().delete()


@pytest.fixture(scope="class")
def client():
    """Shared TestClient for all tests in the class."""
    with TestClient(api) as c:
        yield c


@pytest.mark.django_db(transaction=True)
class TestMissionEndpoints:
    """Test mission CRUD endpoints."""

    def test_list_missions_empty(self, client):
        """GET /missions returns empty list."""
        response = client.get("/missions")
        assert response.status_code == 200
        assert response.json() == {"missions": [], "count": 0}

    def test_create_mission(self, client):
        """POST /missions creates a mission."""
        response = client.post(
            "/missions",
            json={"name": "Artemis II", "description": "Crewed mission"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Artemis II"
        assert data["status"] == "planned"
        assert "id" in data
        assert Mission.objects.filter(name="Artemis II").exists()

    def test_create_mission_validation_name_required(self, client):
        """POST /missions requires name."""
        response = client.post("/missions", json={})
        assert response.status_code == 422

    def test_create_mission_validation_name_min_length(self, client):
        """POST /missions rejects empty name."""
        response = client.post("/missions", json={"name": ""})
        assert response.status_code == 422

    def test_create_mission_validation_name_max_length(self, client):
        """POST /missions rejects name over 100 chars."""
        response = client.post("/missions", json={"name": "A" * 101})
        assert response.status_code == 422

    def test_create_mission_validation_custom_validator(self, client):
        """POST /missions rejects names starting with 'test'."""
        response = client.post("/missions", json={"name": "Test Mission"})
        assert response.status_code == 422

    def test_get_mission(self, client):
        """GET /missions/{id} returns mission details (API-based setup)."""
        # Create via API
        create_resp = client.post(
            "/missions",
            json={"name": "Apollo 11", "description": "Moon landing"},
        )
        mission_id = create_resp.json()["id"]

        # Fetch via API
        response = client.get(f"/missions/{mission_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == mission_id
        assert data["name"] == "Apollo 11"

    def test_get_mission_not_found(self, client):
        """GET /missions/{id} returns 404 for unknown id."""
        response = client.get("/missions/99999")
        assert response.status_code == 404

    def test_update_mission(self, client):
        """PUT /missions/{id} updates mission (ORM-based setup)."""
        mission = Mission.objects.create(name="Mars Rover", status="planned")

        response = client.put(
            f"/missions/{mission.id}",
            json={"status": "active"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "active"

        mission.refresh_from_db()
        assert mission.status == "active"

    def test_update_mission_invalid_status(self, client):
        """PUT /missions/{id} rejects invalid status (ORM-based setup)."""
        mission = Mission.objects.create(name="Valid Name", status="planned")

        response = client.put(
            f"/missions/{mission.id}",
            json={"status": "invalid"},
        )
        assert response.status_code == 422

    def test_delete_mission(self, client):
        """DELETE /missions/{id} removes mission (API-based setup)."""
        # Create via API
        create_resp = client.post("/missions", json={"name": "Cancelled"})
        mission_id = create_resp.json()["id"]

        # Delete via API
        response = client.delete(f"/missions/{mission_id}")
        assert response.status_code == 204

        # Verify deleted via API
        get_resp = client.get(f"/missions/{mission_id}")
        assert get_resp.status_code == 404

    def test_list_missions_with_filter(self, client):
        """GET /missions?status=active filters results (ORM-based setup)."""
        Mission.objects.create(name="Active 1", status="active")
        Mission.objects.create(name="Active 2", status="active")
        Mission.objects.create(name="Completed", status="completed")

        response = client.get("/missions?status=active")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2


@pytest.mark.django_db(transaction=True)
class TestAstronautEndpoints:
    """Test astronaut endpoints."""

    def test_add_astronaut(self, client):
        """POST /missions/{id}/astronauts adds astronaut (ORM-based setup)."""
        mission = Mission.objects.create(name="Moon Mission")

        response = client.post(
            f"/missions/{mission.id}/astronauts",
            data={"name": "Neil Armstrong", "role": "Commander"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Neil Armstrong"
        assert data["role"] == "Commander"
        assert Astronaut.objects.filter(name="Neil Armstrong").exists()

    def test_add_astronaut_invalid_role(self, client):
        """POST /missions/{id}/astronauts validates role via Form model."""
        mission = Mission.objects.create(name="Moon Mission")

        response = client.post(
            f"/missions/{mission.id}/astronauts",
            data={"name": "John Doe", "role": "Invalid Role"},
        )
        assert response.status_code == 422

    def test_list_astronauts(self, client):
        """GET /missions/{id}/astronauts lists crew (ORM-based setup)."""
        mission = Mission.objects.create(name="Apollo 11")
        Astronaut.objects.create(name="Neil Armstrong", role="Commander", mission=mission)
        Astronaut.objects.create(name="Buzz Aldrin", role="Pilot", mission=mission)

        response = client.get(f"/missions/{mission.id}/astronauts")
        assert response.status_code == 200
        data = response.json()
        assert len(data["astronauts"]) == 2

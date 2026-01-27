import pytest
from django.contrib.auth import alogin, get_user_model
from django.contrib.auth.hashers import make_password

from django_bolt import BoltAPI, IsAuthenticated, SessionAuthentication
from django_bolt.testing.client import TestClient


@pytest.fixture(autouse=False)
def api(settings):
    settings.AUTH_USER_MODEL = "django_bolt.User"

    User = get_user_model()

    User.objects.create(
        username="user",
        email="user@test.com",
        password_hash=make_password("123456"),
    )

    api = BoltAPI(
        django_middleware=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ]
    )

    @api.post("/login")
    async def login(request):
        user = await User.objects.aget(username="user")
        await alogin(request, user)
        return {
            "status": "ok",
        }

    @api.get("/protected-route", guards=[IsAuthenticated()], auth=[SessionAuthentication()])
    def protected_route(request):
        return {
            "status": "ok",
        }

    return api


@pytest.fixture
def client(api):
    """Create TestClient for the API"""
    with TestClient(api) as client:
        yield client

@pytest.mark.django_db(transaction=True)
def test_session_auth(client):
    response = client.post("/login")
    assert response.status_code == 200
    assert "sessionid" in response.cookies

    response = client.get("/protected-route")
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_session_auth_missing_cookie(client):
    response = client.post("/login")
    assert response.status_code == 200
    assert "sessionid" in response.cookies

    client.cookies.clear()

    response = client.get("/protected-route")
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]

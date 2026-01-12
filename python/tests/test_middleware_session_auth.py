import msgspec
import pytest
from django.contrib.auth import alogin, alogout, get_user_model
from django.contrib.auth.hashers import check_password, make_password

from django_bolt import BoltAPI, IsAuthenticated, JWTAuthentication, SessionAuthentication, ViewSet, create_jwt_for_user
from django_bolt.exceptions import Unauthorized
from django_bolt.middleware.django_adapter import DjangoMiddlewareStack
from django_bolt.middleware.middleware import AuthenticationMiddleware, SessionMiddleware
from django_bolt.testing.client import TestClient
from tests.test_action_decorator import ArticleSchema

from .test_models import Article

password = make_password("123456")


class LoginRequest(msgspec.Struct):
    """Request body for login endpoint."""

    username: str
    password: str


@pytest.fixture
def api_factory(settings):
    settings.AUTH_USER_MODEL = "django_bolt.User"

    def create_api(session_cookie_name: str = "sessionid"):
        """Create test API with guards and authentication"""
        settings.SESSION_COOKIE_NAME = session_cookie_name

        User = get_user_model()

        User.objects.create(
            username="user",
            email="user@test.com",
            password_hash=password,
        )

        api = BoltAPI(
            middleware=[
                DjangoMiddlewareStack(
                    [
                        SessionMiddleware,
                        AuthenticationMiddleware,
                    ]
                )
            ],
        )

        @api.post("/login")
        async def login(request, credentials: LoginRequest):
            try:
                user = await User.objects.aget(username=credentials.username)
            except User.DoesNotExist:
                raise Unauthorized(detail="Invalid username or password")

            if not check_password(credentials.password, user.password_hash):
                raise Unauthorized(detail="Invalid username or password")

            await alogin(request, user)
            print(user.id)
            return {
                "status": "ok",
            }

        @api.get("/protected-route", guards=[IsAuthenticated()], auth=[SessionAuthentication()])
        async def protected_route(request):
            return {
                "status": "ok",
            }

        @api.get("/me", guards=[IsAuthenticated()], auth=[SessionAuthentication()])
        async def me(request):
            user = await request.auser()

            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }

        @api.post("/logout", guards=[IsAuthenticated()], auth=[SessionAuthentication()])
        async def logout_user(request):
            await alogout(request)
            return {
                "status": "ok",
            }

        return api

    return create_api


@pytest.fixture
def client(api_factory):
    """Create TestClient for the API"""
    api = api_factory()
    with TestClient(api) as client:
        yield client


@pytest.mark.django_db(transaction=True)
def test_user_auth(client):
    from django.conf import settings

    settings.AUTH_USER_MODEL = "django_bolt.User"
    response = client.post("/login", json={"username": "user", "password": "123456"})
    assert response.status_code == 200
    assert "sessionid" in response.cookies

    response = client.get("/protected-route")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.django_db(transaction=True)
def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post("/login", json={"username": "user", "password": "wrong_password"})
    assert response.status_code == 401

    response = client.post("/login", json={"username": "nonexistent", "password": "123456"})
    assert response.status_code == 401

    assert "sessionid" not in response.cookies


@pytest.mark.django_db(transaction=True)
def test_login_logout_worflow(client):
    from django.conf import settings

    settings.AUTH_USER_MODEL = "django_bolt.User"
    response = client.post("/login", json={"username": "user", "password": "123456"})
    assert response.status_code == 200
    assert "sessionid" in response.cookies

    response = client.get("/me")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["username"] == "user"
    assert data["email"] == "user@test.com"
    assert data["is_staff"] is False
    assert data["is_superuser"] is False

    response = client.post("/logout")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    response = client.get("/me")
    assert response.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_session_middleware_in_viewset_unauthenticated(api_factory):
    api = api_factory()

    @api.viewset("/articles")
    class ArticleViewSet(ViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSchema
        auth = [SessionAuthentication()]
        guards = [IsAuthenticated()]

        async def list(self, request):
            """List articles."""
            articles = []
            async for article in await self.get_queryset():
                articles.append(ArticleSchema(id=article.id, title=article.title, content=article.content))
            return articles

        async def retrieve(self, request, pk: int):
            """Retrieve single article."""
            article = await self.get_object(pk)
            return ArticleSchema(id=article.id, title=article.title, content=article.content)

    # Create test article
    article = Article.objects.create(
        title="Test Article", content="Test content", author="Test Author", is_published=False
    )

    client = TestClient(api)

    # Test the custom action
    response = client.get(f"/articles/{article.id}")
    assert response.status_code == 401

    response = client.get("/articles")
    assert response.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_session_middleware_in_viewset_authenticated(api_factory):
    api = api_factory()

    @api.viewset("/articles")
    class ArticleViewSet(ViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSchema
        auth = [SessionAuthentication()]
        guards = [IsAuthenticated()]

        async def list(self, request):
            """List articles."""
            articles = []
            async for article in await self.get_queryset():
                articles.append(ArticleSchema(id=article.id, title=article.title, content=article.content))
            return articles

        async def retrieve(self, request, pk: int):
            """Retrieve single article."""
            article = await self.get_object(pk)
            return ArticleSchema(id=article.id, title=article.title, content=article.content)

    # Create test article
    article = Article.objects.create(
        title="Test Article", content="Test content", author="Test Author", is_published=False
    )

    client = TestClient(api)

    response = client.post("/login", json={"username": "user", "password": "123456"})
    assert response.status_code == 200
    assert "sessionid" in response.cookies
    assert response.json()["status"] == "ok"

    response = client.get(f"/articles/{article.id}")
    assert response.status_code == 200

    response = client.get("/articles")
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_session_middleware_in_viewset_full_flow(api_factory):
    api = api_factory()

    @api.viewset("/articles")
    class ArticleViewSet(ViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSchema
        auth = [SessionAuthentication()]
        guards = [IsAuthenticated()]

        async def list(self, request):
            """List articles."""
            articles = []
            async for article in await self.get_queryset():
                articles.append(ArticleSchema(id=article.id, title=article.title, content=article.content))
            return articles

        async def retrieve(self, request, pk: int):
            """Retrieve single article."""
            article = await self.get_object(pk)
            return ArticleSchema(id=article.id, title=article.title, content=article.content)

    # Create test article
    article = Article.objects.create(
        title="Test Article", content="Test content", author="Test Author", is_published=False
    )

    client = TestClient(api)

    response = client.post("/login", json={"username": "user", "password": "123456"})
    assert response.status_code == 200
    assert "sessionid" in response.cookies
    assert response.json()["status"] == "ok"

    # Test the custom action
    response = client.get(f"/articles/{article.id}")
    assert response.status_code == 200

    response = client.get("/articles")
    assert response.status_code == 200

    response = client.post("/logout")
    assert response.status_code == 200

    response = client.get(f"/articles/{article.id}")
    assert response.status_code == 401

    response = client.get("/articles")
    assert response.status_code == 401


@pytest.mark.django_db(transaction=True)
def test_session_middleware_with_custom_session_cookie_name(api_factory):
    # settings.SESSION_COOKIE_NAME = "custom_sessionid"
    # django.setup()
    api = api_factory(session_cookie_name="custom_sessionid")
    client = TestClient(api)

    response = client.post("/login", json={"username": "user", "password": "123456"})
    assert response.status_code == 200
    assert "custom_sessionid" in response.cookies


@pytest.mark.django_db(transaction=True)
def test_session_middleware_with_other_authentication_strategies(api_factory):
    api = api_factory()

    @api.get("/jwt", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
    async def jwt_endpoint(request):
        return {
            "status": "ok",
        }

    client = TestClient(api)

    response = client.post("/login", json={"username": "user", "password": "123456"})
    assert response.status_code == 200
    assert "sessionid" in response.cookies
    assert response.json()["status"] == "ok"

    response = client.get("/me")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["username"] == "user"
    assert data["email"] == "user@test.com"
    assert data["is_staff"] is False
    assert data["is_superuser"] is False

    User = get_user_model()
    user = User.objects.get(username="user")
    token = create_jwt_for_user(user)

    response = client.get("/jwt")
    assert response.status_code == 401

    response = client.get("/jwt", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

import django
import pytest
from django.conf import settings
from django.contrib.auth import alogin, alogout
from django.contrib.auth.hashers import make_password
from django.core.management import call_command  # noqa: PLC0415

from django_bolt import BoltAPI, IsAuthenticated, SessionAuthentication, ViewSet
from django_bolt.middleware.django_adapter import DjangoMiddlewareStack
from django_bolt.middleware.middleware import AuthenticationMiddleware, SessionMiddleware
from django_bolt.testing.client import TestClient
from tests.test_action_decorator import ArticleSchema

from .test_models import Article, User

password = make_password("123456")


@pytest.fixture()
def api_factory():
    def create_api(session_cookie_name: str = "sessionid"):
        """Create test API with guards and authentication"""

        settings.DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
        settings.SESSION_COOKIE_NAME = session_cookie_name

        django.setup()

        call_command("migrate", "--run-syncdb", verbosity=0)

        User.objects.create(
            username="user",
            email="user@test.com",
            password_hash=password,
        )

        User.objects.create(
            username="staff",
            email="staff@test.com",
            password_hash=password,
            is_staff=True,
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
        async def login(request):
            user = await User.objects.aget(username="user")
            await alogin(request, user)
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
            return {
                "status": "ok",
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
    response = client.post("/login")
    assert response.status_code == 200
    assert "sessionid" in response.cookies

    response = client.get("/protected-route")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.django_db(transaction=True)
def test_login_logout_worflow(client):
    response = client.post("/login")
    assert response.status_code == 200
    assert "sessionid" in response.cookies

    response = client.get("/me")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

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

    response = client.post("/login")
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

    response = client.post("/login")
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
    api = api_factory(session_cookie_name="custom_sessionid")
    client = TestClient(api)

    response = client.post("/login")
    assert response.status_code == 200
    assert "custom_sessionid" in response.cookies

"""
Tests for ModelViewSet and ReadOnlyModelViewSet (DRF-style usage).

This test suite verifies that ModelViewSet and ReadOnlyModelViewSet work similarly
to Django REST Framework's ModelViewSet, where you just set queryset and serializer_class.
"""
import msgspec
import pytest
from asgiref.sync import async_to_sync

from django_bolt import BoltAPI, ModelViewSet, ReadOnlyModelViewSet
from django_bolt.testing import TestClient

from .test_models import Article

# --- Schemas ---

class ArticleSchema(msgspec.Struct):
    """Full article schema."""
    id: int
    title: str
    content: str
    author: str
    is_published: bool

    @classmethod
    def from_model(cls, obj):
        return cls(
            id=obj.id,
            title=obj.title,
            content=obj.content,
            author=obj.author,
            is_published=obj.is_published,
        )


class ArticleCreateSchema(msgspec.Struct):
    """Schema for creating/updating articles."""
    title: str
    content: str
    author: str


# --- Tests ---

@pytest.mark.django_db(transaction=True)
def test_readonly_model_viewset(api):
    """Test ReadOnlyModelViewSet provides helpers for read operations."""
    # Create test data
    article1 = async_to_sync(Article.objects.acreate)(
        title="Article 1",
        content="Content 1",
        author="Author 1",
    )
    async_to_sync(Article.objects.acreate)(
        title="Article 2",
        content="Content 2",
        author="Author 2",
    )

    @api.view("/articles", methods=["GET"])
    class ArticleListViewSet(ReadOnlyModelViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSchema

        async def get(self, request):
            """List all articles."""
            articles = []
            async for article in await self.get_queryset():
                articles.append(ArticleSchema.from_model(article))
            return articles

    @api.view("/articles/{pk}", methods=["GET"])
    class ArticleDetailViewSet(ReadOnlyModelViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSchema

        async def get(self, request, pk: int):
            """Retrieve a single article."""
            article = await self.get_object(pk)
            return ArticleSchema.from_model(article)

    with TestClient(api) as client:
        # List
        response = client.get("/articles")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("id" in article and "title" in article for article in data)

        # Retrieve
        response = client.get(f"/articles/{article1.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == article1.id
        assert data["title"] == "Article 1"


@pytest.mark.django_db(transaction=True)
def test_model_viewset_with_custom_methods(api):
    """Test ModelViewSet with full CRUD implementation."""

    @api.view("/articles", methods=["GET", "POST"])
    class ArticleListViewSet(ModelViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSchema

        async def get(self, request):
            """List all articles."""
            articles = []
            async for article in await self.get_queryset():
                articles.append(ArticleSchema.from_model(article))
            return articles

        async def post(self, request, data: ArticleCreateSchema):
            """Create a new article."""
            article = await Article.objects.acreate(
                title=data.title,
                content=data.content,
                author=data.author,
            )
            return ArticleSchema.from_model(article)

    @api.view("/articles/{pk}", methods=["GET", "PUT", "PATCH", "DELETE"])
    class ArticleDetailViewSet(ModelViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSchema

        async def get(self, request, pk: int):
            """Retrieve a single article."""
            article = await self.get_object(pk)
            return ArticleSchema.from_model(article)

        async def put(self, request, pk: int, data: ArticleCreateSchema):
            """Update an article."""
            article = await self.get_object(pk)
            article.title = data.title
            article.content = data.content
            article.author = data.author
            await article.asave()
            return ArticleSchema.from_model(article)

        async def patch(self, request, pk: int, data: ArticleCreateSchema):
            """Partially update an article."""
            article = await self.get_object(pk)
            if data.title:
                article.title = data.title
            if data.content:
                article.content = data.content
            if data.author:
                article.author = data.author
            await article.asave()
            return ArticleSchema.from_model(article)

        async def delete(self, request, pk: int):
            """Delete an article."""
            article = await self.get_object(pk)
            await article.adelete()
            return {"detail": "Object deleted successfully"}

    with TestClient(api) as client:
        # List
        response = client.get("/articles")
        assert response.status_code == 200
        assert response.json() == []

        # Create
        response = client.post(
            "/articles",
            json={"title": "New Article", "content": "New Content", "author": "Test Author"},
        )
        assert response.status_code == 200
        article_id = response.json()["id"]

        # Retrieve
        response = client.get(f"/articles/{article_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "New Article"

        # Update
        response = client.put(
            f"/articles/{article_id}",
            json={"title": "Updated Title", "content": "Updated Content", "author": "Updated Author"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

        # Partial update
        response = client.patch(
            f"/articles/{article_id}",
            json={"title": "Patched Title", "content": "", "author": ""},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Patched Title"

        # Delete
        response = client.delete(f"/articles/{article_id}")
        assert response.status_code == 200

        # Verify deletion
        response = client.get(f"/articles/{article_id}")
        assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_model_viewset_queryset_reevaluation(api):
    """Test that queryset is re-evaluated on each request (like DRF)."""
    @api.view("/articles", methods=["GET"])
    class ArticleViewSet(ReadOnlyModelViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSchema

        async def get(self, request):
            """List all articles."""
            articles = []
            async for article in await self.get_queryset():
                articles.append(ArticleSchema.from_model(article))
            return articles

    with TestClient(api) as client:
        # First request - empty
        response = client.get("/articles")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Create article outside the viewset
        async_to_sync(Article.objects.acreate)(
            title="Article 1",
            content="Content 1",
            author="Author 1",
        )

        # Second request - should see the new article (queryset re-evaluated)
        response = client.get("/articles")
        assert response.status_code == 200
        assert len(response.json()) == 1


@pytest.mark.django_db(transaction=True)
def test_model_viewset_custom_queryset(api):
    """Test ModelViewSet with custom get_queryset()."""
    # Create test data
    async_to_sync(Article.objects.acreate)(
        title="Published 1",
        content="Content",
        author="Author",
        is_published=True,
    )
    async_to_sync(Article.objects.acreate)(
        title="Draft 1",
        content="Content",
        author="Author",
        is_published=False,
    )

    @api.view("/articles/published", methods=["GET"])
    class PublishedArticleViewSet(ReadOnlyModelViewSet):
        queryset = Article.objects.all()  # Base queryset
        serializer_class = ArticleSchema

        async def get_queryset(self):
            # Custom filtering
            queryset = await super().get_queryset()
            return queryset.filter(is_published=True)

        async def get(self, request):
            """List published articles."""
            articles = []
            async for article in await self.get_queryset():
                articles.append(ArticleSchema.from_model(article))
            return articles

    with TestClient(api) as client:
        response = client.get("/articles/published")
        assert response.status_code == 200
        data = response.json()
        # Should only get published articles
        assert len(data) == 1
        assert data[0]["is_published"] is True
        assert data[0]["title"] == "Published 1"


@pytest.mark.django_db(transaction=True)
def test_model_viewset_lookup_field(api):
    """Test ModelViewSet with custom lookup_field."""
    # Create article
    async_to_sync(Article.objects.acreate)(
        title="Test Article",
        content="Content",
        author="test-author",
    )

    # Use {pk} in URL pattern (will be matched to author field)
    @api.view("/articles/by-author/{pk}", methods=["GET"])
    class ArticleViewSet(ReadOnlyModelViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSchema
        lookup_field = 'author'  # Look up by author instead of pk

        async def get(self, request, pk: str):  # pk will be the author name
            """Retrieve article by author."""
            article = await self.get_object(pk)
            return ArticleSchema.from_model(article)

    with TestClient(api) as client:
        # Lookup by author
        response = client.get("/articles/by-author/test-author")
        assert response.status_code == 200
        data = response.json()
        assert data["author"] == "test-author"
        assert data["title"] == "Test Article"


@pytest.fixture
def api():
    """Create a fresh BoltAPI instance for each test."""
    return BoltAPI()

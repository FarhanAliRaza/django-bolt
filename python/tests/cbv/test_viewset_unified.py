"""
Tests for unified ViewSet pattern with api.viewset() (Litestar/DRF-inspired).

This test suite verifies that the new unified ViewSet pattern works correctly:
- Single ViewSet for both list and detail views
- DRF-style action methods (list, retrieve, create, update, partial_update, destroy)
- Automatic route generation with api.viewset()
- Different serializers for list vs detail (list_serializer_class)
- Type-driven serialization
"""
import msgspec
import pytest
from asgiref.sync import async_to_sync  # noqa: PLC0415

from django_bolt import BoltAPI, ViewSet, action
from django_bolt.testing import TestClient
from tests.test_models import Article

# --- Schemas ---

class ArticleFullSchema(msgspec.Struct):
    """Full article schema for detail views."""
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


class ArticleMiniSchema(msgspec.Struct):
    """Minimal article schema for list views."""
    id: int
    title: str

    @classmethod
    def from_model(cls, obj):
        return cls(id=obj.id, title=obj.title)


class ArticleCreateSchema(msgspec.Struct):
    """Schema for creating articles."""
    title: str
    content: str
    author: str


class ArticleUpdateSchema(msgspec.Struct):
    """Schema for updating articles."""
    title: str | None = None
    content: str | None = None
    author: str | None = None


# --- Tests ---

@pytest.mark.django_db(transaction=True)
def test_unified_viewset_basic_crud(api):
    """Test unified ViewSet with basic CRUD operations."""

    class ArticleViewSet(ViewSet):
        """Unified ViewSet for articles."""
        queryset = Article.objects.all()
        serializer_class = ArticleFullSchema
        list_serializer_class = ArticleMiniSchema
        lookup_field = 'pk'

        async def list(self, request):
            """List articles."""
            articles = []
            async for article in await self.get_queryset():
                articles.append(ArticleMiniSchema.from_model(article))
            return articles

        async def retrieve(self, request, pk: int):
            """Retrieve a single article."""
            article = await self.get_object(pk)
            return ArticleFullSchema.from_model(article)

        async def create(self, request, data: ArticleCreateSchema):
            """Create a new article."""
            article = await Article.objects.acreate(
                title=data.title,
                content=data.content,
                author=data.author,
            )
            return ArticleFullSchema.from_model(article)

        async def update(self, request, pk: int, data: ArticleUpdateSchema):
            """Update an article."""
            article = await self.get_object(pk)
            if data.title:
                article.title = data.title
            if data.content:
                article.content = data.content
            if data.author:
                article.author = data.author
            await article.asave()
            return ArticleFullSchema.from_model(article)

        async def partial_update(self, request, pk: int, data: ArticleUpdateSchema):
            """Partially update an article."""
            article = await self.get_object(pk)
            if data.title:
                article.title = data.title
            if data.content:
                article.content = data.content
            if data.author:
                article.author = data.author
            await article.asave()
            return ArticleFullSchema.from_model(article)

        async def destroy(self, request, pk: int):
            """Delete an article."""
            article = await self.get_object(pk)
            await article.adelete()
            return {"deleted": True, "id": pk}

    # Register with api.viewset() - automatic route generation
    @api.viewset("/articles")
    class ArticleViewSetRegistered(ArticleViewSet):
        pass

    with TestClient(api) as client:
        # List (empty)
        response = client.get("/articles")
        assert response.status_code == 200
        assert response.json() == []

        # Create
        response = client.post(
            "/articles",
            json={"title": "Test Article", "content": "Test Content", "author": "Test Author"},
        )
        assert response.status_code == 201  # HTTP 201 Created
        data = response.json()
        assert data["title"] == "Test Article"
        assert data["content"] == "Test Content"
        article_id = data["id"]

        # List (with data)
        response = client.get("/articles")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 1
        assert articles[0]["title"] == "Test Article"
        # List returns mini schema (id, title only)
        assert "content" not in articles[0]

        # Retrieve (detail view)
        response = client.get(f"/articles/{article_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Article"
        assert data["content"] == "Test Content"  # Detail view includes content

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
            json={"title": "Patched Title"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Patched Title"

        # Delete
        response = client.delete(f"/articles/{article_id}")
        assert response.status_code == 204  # HTTP 204 No Content
        assert response.json()["deleted"] is True

        # Verify deletion
        response = client.get(f"/articles/{article_id}")
        assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_unified_viewset_custom_lookup_field(api):
    """Test unified ViewSet with custom lookup_field."""

    # Create article
    async_to_sync(Article.objects.acreate)(
        title="Test Article",
        content="Test Content",
        author="test-author-slug",
    )

    class ArticleViewSet(ViewSet):
        """Unified ViewSet with custom lookup field."""
        queryset = Article.objects.all()
        serializer_class = ArticleFullSchema
        lookup_field = 'author'  # Use author as lookup field

        async def retrieve(self, request, author: str):
            """Retrieve article by author."""
            article = await self.get_object(author=author)
            return ArticleFullSchema.from_model(article)

    # Register with api.viewset() - uses lookup_field from class
    @api.viewset("/articles")
    class ArticleViewSetRegistered(ArticleViewSet):
        pass

    with TestClient(api) as client:
        # Lookup by author (using custom lookup_field)
        response = client.get("/articles/test-author-slug")
        assert response.status_code == 200
        data = response.json()
        assert data["author"] == "test-author-slug"
        assert data["title"] == "Test Article"


@pytest.mark.django_db(transaction=True)
def test_unified_viewset_with_custom_actions(api):
    """Test unified ViewSet with custom actions."""

    # Create test data
    async_to_sync(Article.objects.acreate)(
        title="Published Article",
        content="Content",
        author="Author",
        is_published=True,
    )
    async_to_sync(Article.objects.acreate)(
        title="Draft Article",
        content="Content",
        author="Author",
        is_published=False,
    )

    class ArticleViewSet(ViewSet):
        """Unified ViewSet with custom actions."""
        queryset = Article.objects.all()
        serializer_class = ArticleFullSchema
        list_serializer_class = ArticleMiniSchema

        async def list(self, request):
            """List all articles."""
            articles = []
            async for article in await self.get_queryset():
                articles.append(ArticleMiniSchema.from_model(article))
            return articles

        # Custom action: search (using @action decorator)
        @action(methods=["GET"], detail=False)
        async def search(self, request, query: str):
            """Search articles by title. GET /articles/search"""
            results = []
            async for article in Article.objects.filter(title__icontains=query):
                results.append(ArticleMiniSchema.from_model(article))
            return {"query": query, "results": results}

        # Custom action: published only (using @action decorator)
        @action(methods=["GET"], detail=False)
        async def published(self, request):
            """Get published articles only. GET /articles/published"""
            articles = []
            async for article in Article.objects.filter(is_published=True):
                articles.append(ArticleMiniSchema.from_model(article))
            return articles

    # Register with api.viewset() - automatically discovers custom actions
    @api.viewset("/articles")
    class ArticleViewSetRegistered(ArticleViewSet):
        pass

    with TestClient(api) as client:
        # List all articles
        response = client.get("/articles")
        assert response.status_code == 200
        assert len(response.json()) == 2

        # Search
        response = client.get("/articles/search?query=Published")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "Published"
        assert len(data["results"]) == 1
        assert data["results"][0]["title"] == "Published Article"

        # Published only
        response = client.get("/articles/published")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 1
        assert articles[0]["title"] == "Published Article"


@pytest.mark.django_db(transaction=True)
def test_unified_viewset_partial_implementation(api):
    """Test unified ViewSet with only some actions implemented."""

    class ReadOnlyArticleViewSet(ViewSet):
        """Read-only ViewSet (only list and retrieve)."""
        queryset = Article.objects.all()
        serializer_class = ArticleFullSchema

        async def list(self, request):
            """List articles."""
            articles = []
            async for article in await self.get_queryset():
                articles.append(ArticleFullSchema.from_model(article))
            return articles

        async def retrieve(self, request, pk: int):
            """Retrieve a single article."""
            article = await self.get_object(pk)
            return ArticleFullSchema.from_model(article)

        # Note: create, update, partial_update, destroy not implemented

    # Register with api.viewset() - only generates routes for implemented actions
    @api.viewset("/articles")
    class ReadOnlyArticleViewSetRegistered(ReadOnlyArticleViewSet):
        pass

    with TestClient(api) as client:
        # List works
        response = client.get("/articles")
        assert response.status_code == 200

        # POST not registered (create not implemented)
        response = client.post("/articles", json={"title": "Test", "content": "Test", "author": "Test"})
        assert response.status_code == 404


@pytest.fixture
def api():
    """Create a fresh BoltAPI instance for each test."""
    return BoltAPI()

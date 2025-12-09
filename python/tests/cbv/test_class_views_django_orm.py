"""
Django ORM Integration Tests for Class-Based Views.

This test suite verifies that ViewSets and Mixins work correctly with
real Django ORM operations (like Django REST Framework).

Tests cover:
- Real database queries with Django async ORM
- ViewSet with all CRUD operations
- ListMixin with Article.objects.all()
- RetrieveMixin with Article.objects.aget(pk=pk)
- CreateMixin with Article.objects.acreate(**data)
- UpdateMixin with obj.asave()
- PartialUpdateMixin with partial updates + asave()
- DestroyMixin with obj.adelete()
- End-to-end CRUD workflows
"""
import msgspec
import pytest

from django_bolt import BoltAPI
from django_bolt.testing import TestClient
from django_bolt.views import (
    APIView,
    DestroyMixin,
    ListMixin,
    RetrieveMixin,
    ViewSet,
)

from ..test_models import Article

# --- Fixtures ---

@pytest.fixture
def api():
    """Create a fresh BoltAPI instance for each test."""
    return BoltAPI()


@pytest.fixture
def sample_articles(db):
    """Create sample articles in the database."""
    from asgiref.sync import async_to_sync  # noqa: PLC0415

    articles = []
    for i in range(1, 4):
        article = async_to_sync(Article.objects.acreate)(
            title=f"Article {i}",
            content=f"Content {i}",
            author="Test Author",
            is_published=(i % 2 == 0),
        )
        articles.append(article)
    return articles


# --- Schemas ---

class ArticleSchema(msgspec.Struct):
    """Full article schema (without datetime fields for simplicity)."""
    id: int
    title: str
    content: str
    author: str
    is_published: bool

    @classmethod
    def from_model(cls, obj):
        """Convert Django model instance to schema."""
        return cls(
            id=obj.id,
            title=obj.title,
            content=obj.content,
            author=obj.author,
            is_published=obj.is_published,
        )


class ArticleCreateSchema(msgspec.Struct):
    """Schema for creating articles."""
    title: str
    content: str
    author: str


class ArticleUpdateSchema(msgspec.Struct):
    """Schema for updating articles (full update)."""
    title: str
    content: str
    author: str
    is_published: bool


class ArticlePartialUpdateSchema(msgspec.Struct):
    """Schema for partial updates (all fields optional)."""
    title: str | None = None
    content: str | None = None
    author: str | None = None
    is_published: bool | None = None


# --- ListMixin Tests ---

@pytest.mark.django_db(transaction=True)
def test_simple_list_without_mixin(api, sample_articles):
    """Test simple list without mixin to debug."""

    @api.view("/articles/simple")
    class ArticleListView(APIView):
        async def get(self, request) -> list:
            articles = []
            async for article in Article.objects.all():
                articles.append({
                    "id": article.id,
                    "title": article.title,
                    "content": article.content,
                    "author": article.author,
                    "is_published": article.is_published,
                })
            return articles

    with TestClient(api) as client:
        response = client.get("/articles/simple")
        if response.status_code != 200:
            print(f"Error response: {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


@pytest.mark.django_db(transaction=True)
def test_list_mixin_with_real_django_orm(api, sample_articles):
    """Test ListMixin with real Django ORM queryset."""

    @api.view("/articles")
    class ArticleListView(ListMixin, APIView):
        serializer_class = ArticleSchema

        async def get_queryset(self):
            return Article.objects.all()

    with TestClient(api) as client:
        response = client.get("/articles")
        if response.status_code != 200:
            print(f"Error response: {response.text}")
        assert response.status_code == 200
        data = response.json()

        # Verify we got all articles
        assert isinstance(data, list)
        assert len(data) == 3

        # Verify data structure
        for article_data in data:
            assert "id" in article_data
            assert "title" in article_data
            assert "content" in article_data
            assert "author" in article_data
            assert "is_published" in article_data


@pytest.mark.django_db(transaction=True)
def test_list_mixin_filtered_queryset(api, sample_articles):
    """Test ListMixin with filtered Django queryset."""

    @api.view("/articles/published")
    class PublishedArticleListView(ListMixin, APIView):
        serializer_class = ArticleSchema

        async def get_queryset(self):
            return Article.objects.filter(is_published=True)

    with TestClient(api) as client:
        response = client.get("/articles/published")
        assert response.status_code == 200
        data = response.json()

        # Should only get published articles (even numbered from fixture)
        assert isinstance(data, list)
        assert len(data) == 1  # Only Article 2 is published (2 % 2 == 0)
        assert all(article["is_published"] for article in data)


# --- RetrieveMixin Tests ---

@pytest.mark.django_db(transaction=True)
def test_retrieve_mixin_with_real_django_orm(api, sample_articles):
    """Test RetrieveMixin with real Django ORM aget()."""

    @api.view("/articles/{pk}")
    class ArticleDetailView(RetrieveMixin, ViewSet):
        serializer_class = ArticleSchema

        async def get_queryset(self):
            return Article.objects.all()

    article_id = sample_articles[0].id

    with TestClient(api) as client:
        response = client.get(f"/articles/{article_id}")
        assert response.status_code == 200
        data = response.json()

        # Verify correct article retrieved
        assert data["id"] == article_id
        assert data["title"] == "Article 1"
        assert data["content"] == "Content 1"
        assert data["author"] == "Test Author"


@pytest.mark.django_db(transaction=True)
def test_retrieve_mixin_not_found(api):
    """Test RetrieveMixin returns 404 when object doesn't exist."""

    @api.view("/articles/{pk}")
    class ArticleDetailView(RetrieveMixin, ViewSet):
        serializer_class = ArticleSchema

        async def get_queryset(self):
            return Article.objects.all()

    with TestClient(api) as client:
        response = client.get("/articles/99999")
        assert response.status_code == 404


# --- CreateMixin Tests ---

@pytest.mark.django_db(transaction=True)
def test_create_mixin_with_real_django_orm(api):
    """Test CreateMixin with real Django ORM acreate()."""

    @api.view("/articles")
    class ArticleCreateView(ViewSet):
        serializer_class = ArticleSchema

        async def get_queryset(self):
            return Article.objects.all()

        async def post(self, request, data: ArticleCreateSchema):
            """Create a new article."""
            article = await Article.objects.acreate(
                title=data.title,
                content=data.content,
                author=data.author,
            )
            return ArticleSchema.from_model(article)

    with TestClient(api) as client:
        response = client.post(
            "/articles",
            json={
                "title": "New Article",
                "content": "New Content",
                "author": "New Author",
            },
        )
        assert response.status_code == 200
        data = response.json()

        # Verify article was created
        assert data["title"] == "New Article"
        assert data["content"] == "New Content"
        assert data["author"] == "New Author"
        assert "id" in data

        # Verify it's actually in the database
        from asgiref.sync import async_to_sync  # noqa: PLC0415
        article_id = data["id"]
        article = async_to_sync(Article.objects.aget)(id=article_id)
        assert article.title == "New Article"
        assert article.content == "New Content"


# --- UpdateMixin Tests ---

@pytest.mark.django_db(transaction=True)
def test_update_mixin_with_real_django_orm(api, sample_articles):
    """Test UpdateMixin with real Django ORM asave()."""

    @api.view("/articles/{pk}")
    class ArticleUpdateView(ViewSet):
        serializer_class = ArticleSchema

        async def get_queryset(self):
            return Article.objects.all()

        async def put(self, request, pk: int, data: ArticleUpdateSchema):
            """Update an article (full update)."""
            article = await self.get_object(pk)
            article.title = data.title
            article.content = data.content
            article.author = data.author
            article.is_published = data.is_published
            await article.asave()
            return ArticleSchema.from_model(article)

    article_id = sample_articles[0].id

    with TestClient(api) as client:
        response = client.put(
            f"/articles/{article_id}",
            json={
                "title": "Updated Title",
                "content": "Updated Content",
                "author": "Updated Author",
                "is_published": True,
            },
        )
        assert response.status_code == 200
        data = response.json()

        # Verify response
        assert data["id"] == article_id
        assert data["title"] == "Updated Title"
        assert data["content"] == "Updated Content"
        assert data["is_published"] is True

        # Verify database was updated
        from asgiref.sync import async_to_sync  # noqa: PLC0415
        article = async_to_sync(Article.objects.aget)(id=article_id)
        assert article.title == "Updated Title"
        assert article.content == "Updated Content"
        assert article.is_published is True


# --- PartialUpdateMixin Tests ---

@pytest.mark.django_db(transaction=True)
def test_partial_update_mixin_with_real_django_orm(api, sample_articles):
    """Test PartialUpdateMixin with real Django ORM asave()."""

    @api.view("/articles/{pk}")
    class ArticlePartialUpdateView(ViewSet):
        serializer_class = ArticleSchema

        async def get_queryset(self):
            return Article.objects.all()

        async def patch(self, request, pk: int, data: ArticlePartialUpdateSchema):
            """Partially update an article."""
            article = await self.get_object(pk)
            if data.title is not None:
                article.title = data.title
            if data.content is not None:
                article.content = data.content
            if data.author is not None:
                article.author = data.author
            if data.is_published is not None:
                article.is_published = data.is_published
            await article.asave()
            return ArticleSchema.from_model(article)

    article_id = sample_articles[0].id
    original_content = sample_articles[0].content

    with TestClient(api) as client:
        # Only update title, leave other fields unchanged
        response = client.patch(
            f"/articles/{article_id}",
            json={"title": "Partially Updated Title"},
        )
        assert response.status_code == 200
        data = response.json()

        # Verify title was updated
        assert data["title"] == "Partially Updated Title"

        # Verify database was updated and other fields unchanged
        from asgiref.sync import async_to_sync  # noqa: PLC0415
        article = async_to_sync(Article.objects.aget)(id=article_id)
        assert article.title == "Partially Updated Title"
        assert article.content == original_content  # Unchanged


# --- DestroyMixin Tests ---

@pytest.mark.django_db(transaction=True)
def test_destroy_mixin_with_real_django_orm(api, sample_articles):
    """Test DestroyMixin with real Django ORM adelete()."""

    @api.view("/articles/{pk}")
    class ArticleDestroyView(DestroyMixin, ViewSet):
        async def get_queryset(self):
            return Article.objects.all()

    article_id = sample_articles[0].id

    # Verify article exists before deletion
    from asgiref.sync import async_to_sync  # noqa: PLC0415
    exists_before = async_to_sync(Article.objects.filter(id=article_id).aexists)()
    assert exists_before is True

    with TestClient(api) as client:
        response = client.delete(f"/articles/{article_id}")
        assert response.status_code == 200
        data = response.json()
        assert "detail" in data

        # Verify article was deleted from database
        exists_after = async_to_sync(Article.objects.filter(id=article_id).aexists)()
        assert exists_after is False


# --- Full CRUD ViewSet Tests ---

@pytest.mark.django_db(transaction=True)
def test_full_crud_viewset_with_django_orm(api):
    """
    Test a complete CRUD ViewSet with all mixins using real Django ORM.
    This verifies the ViewSet works like Django REST Framework.
    """

    class ArticleViewSet(ViewSet):
        serializer_class = ArticleSchema

        async def get_queryset(self):
            return Article.objects.all()

        async def get(self, request):
            """List all articles."""
            articles = []
            async for article in Article.objects.all():
                articles.append(ArticleSchema.from_model(article))
            return articles

        async def post(self, request, data: ArticleCreateSchema):
            """Create an article."""
            article = await Article.objects.acreate(
                title=data.title,
                content=data.content,
                author=data.author,
            )
            return ArticleSchema.from_model(article)

    class ArticleDetailViewSet(ViewSet):
        serializer_class = ArticleSchema

        async def get_queryset(self):
            return Article.objects.all()

        async def get(self, request, pk: int):
            """Retrieve an article."""
            article = await self.get_object(pk)
            return ArticleSchema.from_model(article)

        async def put(self, request, pk: int, data: ArticleUpdateSchema):
            """Update an article."""
            article = await self.get_object(pk)
            article.title = data.title
            article.content = data.content
            article.author = data.author
            article.is_published = data.is_published
            await article.asave()
            return ArticleSchema.from_model(article)

        async def patch(self, request, pk: int, data: ArticlePartialUpdateSchema):
            """Partially update an article."""
            article = await self.get_object(pk)
            if data.title is not None:
                article.title = data.title
            if data.content is not None:
                article.content = data.content
            if data.author is not None:
                article.author = data.author
            if data.is_published is not None:
                article.is_published = data.is_published
            await article.asave()
            return ArticleSchema.from_model(article)

        async def delete(self, request, pk: int):
            """Delete an article."""
            article = await self.get_object(pk)
            await article.adelete()
            return {"detail": "Object deleted successfully"}

    # Register routes with decorator syntax
    @api.view("/articles", methods=["GET", "POST"])
    class ArticleViewSetRegistered(ArticleViewSet):
        pass

    @api.view("/articles/{pk}", methods=["GET", "PUT", "PATCH", "DELETE"])
    class ArticleDetailViewSetRegistered(ArticleDetailViewSet):
        pass

    with TestClient(api) as client:
        # 1. List (should be empty initially)
        response = client.get("/articles")
        assert response.status_code == 200
        assert response.json() == []

        # 2. Create first article
        response = client.post(
            "/articles",
            json={
                "title": "First Article",
                "content": "First Content",
                "author": "Author 1",
            },
        )
        assert response.status_code == 200
        article1_id = response.json()["id"]

        # 3. Create second article
        response = client.post(
            "/articles",
            json={
                "title": "Second Article",
                "content": "Second Content",
                "author": "Author 2",
            },
        )
        assert response.status_code == 200
        article2_id = response.json()["id"]

        # 4. List (should now have 2 articles)
        response = client.get("/articles")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 2

        # 5. Retrieve single article
        response = client.get(f"/articles/{article1_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "First Article"

        # 6. Update (full)
        response = client.put(
            f"/articles/{article1_id}",
            json={
                "title": "Updated First Article",
                "content": "Updated Content",
                "author": "Updated Author",
                "is_published": True,
            },
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated First Article"

        # 7. Partial update
        response = client.patch(
            f"/articles/{article2_id}",
            json={"title": "Partially Updated Second Article"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Partially Updated Second Article"

        # 8. Delete
        response = client.delete(f"/articles/{article1_id}")
        assert response.status_code == 200

        # 9. Verify deletion
        response = client.get(f"/articles/{article1_id}")
        assert response.status_code == 404

        # 10. List (should now have 1 article)
        response = client.get("/articles")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 1
        assert articles[0]["id"] == article2_id


# --- Custom ViewSet Tests ---

@pytest.mark.django_db(transaction=True)
def test_custom_viewset_method_with_django_orm(api, sample_articles):
    """Test custom ViewSet method with Django ORM operations."""

    @api.view("/articles/{pk}")
    class ArticleViewSet(ViewSet):
        async def get_queryset(self):
            return Article.objects.all()

        async def get(self, request, pk: int) -> dict:
            """Custom retrieve with additional business logic."""
            article = await self.get_object(pk)

            # Custom logic: count total articles by same author
            author_count = await Article.objects.filter(author=article.author).acount()

            return {
                "id": article.id,
                "title": article.title,
                "content": article.content,
                "author": article.author,
                "author_article_count": author_count,
            }

    article_id = sample_articles[0].id

    with TestClient(api) as client:
        response = client.get(f"/articles/{article_id}")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == article_id
        assert data["title"] == "Article 1"
        # All 3 sample articles have same author
        assert data["author_article_count"] == 3


# --- Queryset Filtering Tests ---

@pytest.mark.django_db(transaction=True)
def test_viewset_with_filtered_queryset(api, sample_articles):
    """Test ViewSet with custom queryset filtering."""

    @api.view("/articles/published")
    class PublishedArticleViewSet(ListMixin, ViewSet):
        serializer_class = ArticleSchema

        async def get_queryset(self):
            # Override to only return published articles
            return Article.objects.filter(is_published=True).order_by("-created_at")

    with TestClient(api) as client:
        response = client.get("/articles/published")
        assert response.status_code == 200
        data = response.json()

        # Should only get published articles
        assert len(data) == 1
        assert all(article["is_published"] for article in data)


# --- Edge Cases ---

@pytest.mark.django_db(transaction=True)
def test_update_nonexistent_article(api):
    """Test updating a non-existent article returns 404."""

    @api.view("/articles/{pk}")
    class ArticleUpdateView(ViewSet):
        serializer_class = ArticleSchema

        async def get_queryset(self):
            return Article.objects.all()

        async def put(self, request, pk: int, data: ArticleUpdateSchema):
            """Update an article."""
            article = await self.get_object(pk)  # This will raise 404
            article.title = data.title
            article.content = data.content
            article.author = data.author
            article.is_published = data.is_published
            await article.asave()
            return ArticleSchema.from_model(article)

    with TestClient(api) as client:
        response = client.put(
            "/articles/99999",
            json={
                "title": "Test",
                "content": "Test",
                "author": "Test",
                "is_published": False,
            },
        )
        assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_delete_nonexistent_article(api):
    """Test deleting a non-existent article returns 404."""

    @api.view("/articles/{pk}")
    class ArticleDestroyView(DestroyMixin, ViewSet):
        async def get_queryset(self):
            return Article.objects.all()

    with TestClient(api) as client:
        response = client.delete("/articles/99999")
        assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_async_queryset_iteration(api, sample_articles):
    """Test that async queryset iteration works correctly."""

    @api.view("/articles")
    class ArticleListView(APIView):
        async def get(self, request) -> list:
            articles = []
            # Test async iteration like ListMixin does
            async for article in Article.objects.all():
                articles.append({
                    "id": article.id,
                    "title": article.title,
                })
            return articles

    with TestClient(api) as client:
        response = client.get("/articles")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in article and "title" in article for article in data)

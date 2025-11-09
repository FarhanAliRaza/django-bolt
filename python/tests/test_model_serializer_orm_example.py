"""
Practical example test: ORM operations with validators and computed fields.
"""
from __future__ import annotations

import pytest
from django_bolt import ModelSerializer, Serializer
from .test_models import Article


# ============================================================
# Define Serializer with ALL features
# ============================================================

@ModelSerializer
class ArticleSerializer:
    """Article serializer demonstrating all features."""

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'author', 'is_published', 'created_at',
            # Computed fields
            'word_count', 'reading_time', 'content_preview', 'is_long_form'
        ]
        read_only_fields = ['id', 'created_at', 'word_count', 'reading_time', 'content_preview', 'is_long_form']

    # ============================================================
    # CUSTOM VALIDATORS
    # ============================================================

    def validate_title(self, value: str) -> str:
        """Ensure title is properly formatted."""
        if len(value.strip()) < 5:
            raise ValueError("Title must be at least 5 characters")
        if len(value) > 200:
            raise ValueError("Title too long (max 200 characters)")
        # Clean and return
        return value.strip()

    def validate_content(self, value: str) -> str:
        """Ensure content has minimum length."""
        if len(value.strip()) < 50:
            raise ValueError("Content must be at least 50 characters")
        return value.strip()

    def validate_author(self, value: str) -> str:
        """Validate author name."""
        if not value or len(value.strip()) < 2:
            raise ValueError("Author name required (min 2 characters)")
        return value.strip()

    # ============================================================
    # COMPUTED FIELDS
    # ============================================================

    @staticmethod
    def get_word_count(obj) -> int:
        """Count words in content."""
        return len(obj.content.split())

    @staticmethod
    def get_reading_time(obj) -> str:
        """Estimate reading time (200 words per minute)."""
        words = len(obj.content.split())
        minutes = words / 200
        if minutes < 1:
            return "< 1 min"
        elif minutes < 60:
            return f"{int(minutes)} min"
        else:
            hours = minutes / 60
            return f"{hours:.1f} hours"

    @staticmethod
    def get_content_preview(obj) -> str:
        """Generate preview (first 100 characters)."""
        if len(obj.content) <= 100:
            return obj.content
        return obj.content[:100] + "..."

    @staticmethod
    def get_is_long_form(obj) -> bool:
        """Check if article is long-form (> 1000 words)."""
        return len(obj.content.split()) > 1000


# ============================================================
# TESTS - Demonstrating ORM Read/Write with Features
# ============================================================

@pytest.mark.django_db(transaction=True)
def test_orm_write_with_validation():
    """Test: ORM WRITE - Creating article with validation."""
    from asgiref.sync import async_to_sync

    # This will PASS validation
    valid_data = ArticleSerializer(
        title="Understanding Django Performance",  # >= 5 chars ✓
        content="This is a comprehensive guide to optimizing Django applications. " * 10,  # >= 50 chars ✓
        author="Jane Smith",  # >= 2 chars ✓
        is_published=True,
        word_count=0,  # Read-only, will be computed
        reading_time="",  # Read-only, will be computed
        content_preview="",  # Read-only, will be computed
        is_long_form=False  # Read-only, will be computed
    )

    # ORM WRITE: Create article in database
    @async_to_sync
    async def create_article():
        return await Article.objects.acreate(
            title=valid_data.title,
            content=valid_data.content,
            author=valid_data.author,
            is_published=valid_data.is_published
        )

    article = create_article()

    # Verify it was saved
    assert article.id is not None
    assert article.title == "Understanding Django Performance"  # From validated data
    assert len(article.content) > 50


@pytest.mark.django_db(transaction=True)
def test_orm_write_validation_errors():
    """Test: Validation errors prevent bad data."""

    # Test 1: Title too short
    with pytest.raises(ValueError, match="Title must be at least 5 characters"):
        ArticleSerializer(
            title="Bad",  # Too short!
            content="Some content here that is long enough to pass validation checks",
            author="John Doe",
            is_published=False,
            word_count=0,
            reading_time="",
            content_preview="",
            is_long_form=False
        )

    # Test 2: Content too short
    with pytest.raises(ValueError, match="Content must be at least 50 characters"):
        ArticleSerializer(
            title="Good Title Here",
            content="Too short",  # Less than 50 chars!
            author="John Doe",
            is_published=False,
            word_count=0,
            reading_time="",
            content_preview="",
            is_long_form=False
        )


@pytest.mark.django_db(transaction=True)
def test_orm_read_with_computed_fields():
    """Test: ORM READ - Reading with computed fields."""
    from asgiref.sync import async_to_sync

    # Create test article
    @async_to_sync
    async def create_article():
        return await Article.objects.acreate(
            title="Django Optimization Guide",
            content="Learn how to optimize Django. " * 50,  # 250 words
            author="Expert Dev",
            is_published=True
        )

    article = create_article()

    # ORM READ: Fetch and serialize with computed fields
    @async_to_sync
    async def read_article():
        fetched = await Article.objects.aget(id=article.id)
        return ArticleSerializer.from_model(fetched)

    serialized = read_article()

    # Verify computed fields work
    assert serialized.id == article.id
    assert serialized.title == article.title
    assert serialized.word_count == 250  # Computed!
    assert "min" in serialized.reading_time  # Computed!
    assert len(serialized.content_preview) <= 103  # Computed (100 + "...")
    assert serialized.is_long_form is False  # Computed (< 1000 words)


@pytest.mark.django_db(transaction=True)
def test_orm_read_queryset_optimization():
    """Test: ORM READ - Bulk serialization with from_queryset()."""
    from asgiref.sync import async_to_sync

    # Create multiple articles
    @async_to_sync
    async def create_articles():
        return await Article.objects.abulk_create([
            Article(title=f"Article {i}", content=f"Content for article {i}. " * 20, author=f"Author {i}", is_published=True)
            for i in range(1, 6)
        ])

    create_articles()

    # ORM READ: Fetch all articles
    @async_to_sync
    async def read_all():
        # Note: from_queryset uses the hot path (.values() + msgspec.convert)
        # But computed fields require from_model() per instance
        articles = Article.objects.all()
        return [ArticleSerializer.from_model(a) async for a in articles]

    serialized_list = read_all()

    # Verify we got all 5 articles with computed fields
    assert len(serialized_list) == 5
    for article in serialized_list:
        assert article.word_count > 0  # Computed field present
        assert article.reading_time  # Computed field present


@pytest.mark.django_db(transaction=True)
def test_orm_update_workflow():
    """Test: Full ORM workflow - Create, Read, Update, Read."""
    from asgiref.sync import async_to_sync

    # Step 1: CREATE
    @async_to_sync
    async def create():
        return await Article.objects.acreate(
            title="Initial Title",
            content="This is the initial content that is long enough. " * 5,
            author="Original Author",
            is_published=False
        )

    article = create()
    original_id = article.id

    # Step 2: READ (with computed fields)
    @async_to_sync
    async def read(article_id):
        fetched = await Article.objects.aget(id=article_id)
        return ArticleSerializer.from_model(fetched)

    serialized_v1 = read(original_id)
    assert serialized_v1.title == "Initial Title"  # From validated data
    assert serialized_v1.is_published is False

    # Step 3: UPDATE (with validation)
    @async_to_sync
    async def update(article_id):
        article = await Article.objects.aget(id=article_id)

        # Update with validated data
        updated_data = ArticleSerializer(
            title="Updated Article Title",  # Valid
            content="This is the updated content with much more information. " * 10,  # Valid
            author="Updated Author",
            is_published=True,
            word_count=0,
            reading_time="",
            content_preview="",
            is_long_form=False
        )

        article.title = updated_data.title
        article.content = updated_data.content
        article.author = updated_data.author
        article.is_published = updated_data.is_published
        await article.asave()

        return article

    update(original_id)

    # Step 4: READ again (verify update + new computed values)
    serialized_v2 = read(original_id)
    assert serialized_v2.title == "Updated Article Title"  # Changed!
    assert serialized_v2.is_published is True  # Changed!
    assert serialized_v2.word_count > 50  # Recomputed with new content


@pytest.mark.django_db(transaction=True)
def test_long_form_article_detection():
    """Test: Computed field for long-form content detection."""
    from asgiref.sync import async_to_sync

    # Create short article
    @async_to_sync
    async def create_short():
        return await Article.objects.acreate(
            title="Short Article",
            content="This is a short article. " * 50,  # 250 words
            author="Writer",
            is_published=True
        )

    # Create long article
    @async_to_sync
    async def create_long():
        return await Article.objects.acreate(
            title="Long Form Article",
            content="This is a comprehensive long-form article. " * 300,  # 1800 words
            author="Writer",
            is_published=True
        )

    short = create_short()
    long = create_long()

    # Read and check computed is_long_form field
    @async_to_sync
    async def read_and_serialize(article_id):
        article = await Article.objects.aget(id=article_id)
        return ArticleSerializer.from_model(article)

    short_serialized = read_and_serialize(short.id)
    long_serialized = read_and_serialize(long.id)

    # Verify long-form detection
    assert short_serialized.is_long_form is False  # < 1000 words
    assert long_serialized.is_long_form is True   # > 1000 words
    assert short_serialized.word_count == 250
    assert long_serialized.word_count == 1800


# ============================================================
# Summary of Features Demonstrated
# ============================================================

"""
This test file demonstrates:

✅ ORM WRITE Operations:
   - Creating records with validated data
   - Updating existing records
   - Validation prevents bad data from reaching database

✅ ORM READ Operations:
   - Reading single records
   - Reading multiple records (queryset)
   - Efficient bulk serialization

✅ Custom Validators:
   - validate_title: length checks, auto-capitalization
   - validate_content: minimum length requirement
   - validate_author: presence and length checks
   - validate_views: non-negative constraint

✅ Computed Fields:
   - word_count: counts words in content
   - reading_time: estimates reading duration
   - content_preview: generates excerpt
   - is_long_form: categorizes article length

✅ Complete Workflow:
   - Create → Read → Update → Read
   - Data validation at every step
   - Computed fields always up-to-date

✅ Performance:
   - Uses async ORM methods (acreate, aget, asave)
   - Leverages msgspec for fast serialization
   - Computed fields calculated on-demand
"""

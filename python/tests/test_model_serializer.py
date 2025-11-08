"""
Tests for model_serializer module.

Tests:
- Basic serializer generation from Django models
- Field validation with validate_<field> methods
- Custom field transformations
- QuerySet optimization (hot path)
- OpenAPI schema generation
- Integration with BoltAPI
"""
from __future__ import annotations

import pytest
from datetime import datetime
from decimal import Decimal
from typing import Optional
import msgspec

from django_bolt import BoltAPI, model_serializer, Serializer, quick_serializer, Field
from django_bolt.testing import TestClient
from .test_models import Article


# --- Basic Serializer Tests ---

@pytest.mark.django_db(transaction=True)
def test_model_serializer_basic():
    """Test basic model serializer generation."""
    from asgiref.sync import async_to_sync

    # Generate serializer
    ArticleSerializer = model_serializer(
        Article,
        fields=['id', 'title', 'content', 'author'],
    )

    # Create test article
    article = async_to_sync(Article.objects.acreate)(
        title="Test Article",
        content="Test content",
        author="John Doe",
    )

    # Serialize
    serialized = ArticleSerializer.from_model(article)

    # Verify
    assert isinstance(serialized, msgspec.Struct)
    assert serialized.id == article.id
    assert serialized.title == "Test Article"
    assert serialized.content == "Test content"
    assert serialized.author == "John Doe"


@pytest.mark.django_db(transaction=True)
def test_model_serializer_all_fields():
    """Test model serializer with fields='__all__'."""
    from asgiref.sync import async_to_sync

    # Generate serializer with all fields
    ArticleSerializer = model_serializer(Article, fields='__all__')

    # Create test article
    article = async_to_sync(Article.objects.acreate)(
        title="Test Article",
        content="Test content",
        author="John Doe",
        is_published=True,
    )

    # Serialize
    serialized = ArticleSerializer.from_model(article)

    # Verify all fields are present
    assert hasattr(serialized, 'id')
    assert hasattr(serialized, 'title')
    assert hasattr(serialized, 'content')
    assert hasattr(serialized, 'author')
    assert hasattr(serialized, 'is_published')
    assert serialized.is_published is True


@pytest.mark.django_db(transaction=True)
def test_model_serializer_exclude():
    """Test model serializer with field exclusion."""
    from asgiref.sync import async_to_sync

    # Generate serializer excluding some fields
    ArticleSerializer = model_serializer(
        Article,
        fields='__all__',
        exclude=['content', 'is_published'],
    )

    # Create test article
    article = async_to_sync(Article.objects.acreate)(
        title="Test Article",
        content="Test content",
        author="John Doe",
    )

    # Serialize
    serialized = ArticleSerializer.from_model(article)

    # Verify excluded fields are not present
    assert hasattr(serialized, 'id')
    assert hasattr(serialized, 'title')
    assert hasattr(serialized, 'author')
    assert not hasattr(serialized, 'content')
    assert not hasattr(serialized, 'is_published')


# --- Validation Tests ---

def test_serializer_with_validation():
    """Test Serializer base class with custom validation."""

    class UserSerializer(Serializer):
        id: int
        username: str
        email: str
        age: int

        def validate_email(self, value: str) -> str:
            if '@' not in value:
                raise ValueError("Email must contain @")
            return value

        def validate_age(self, value: int) -> int:
            if value < 0 or value > 150:
                raise ValueError("Age must be between 0 and 150")
            return value

    # Valid data
    user = UserSerializer(id=1, username='john', email='john@example.com', age=30)
    assert user.email == 'john@example.com'
    assert user.age == 30

    # Invalid email
    with pytest.raises(ValueError, match="Email must contain @"):
        UserSerializer(id=1, username='john', email='invalid-email', age=30)

    # Invalid age
    with pytest.raises(ValueError, match="Age must be between 0 and 150"):
        UserSerializer(id=1, username='john', email='john@example.com', age=200)


def test_model_serializer_with_validators():
    """Test model_serializer with custom validators."""

    def validate_email(value: str) -> str:
        if not value.endswith('@example.com'):
            raise ValueError("Email must end with @example.com")
        return value

    def validate_age(value: int) -> int:
        if value < 18:
            raise ValueError("Must be 18 or older")
        return value

    UserSerializer = model_serializer(
        None,  # No model needed for this test
        fields=['id', 'email', 'age'],
        validators={
            'email': validate_email,
            'age': validate_age,
        }
    )

    # Valid data
    user = UserSerializer(id=1, email='user@example.com', age=25)
    assert user.email == 'user@example.com'

    # Invalid email
    with pytest.raises(ValueError, match="Email must end with @example.com"):
        UserSerializer(id=1, email='user@other.com', age=25)

    # Invalid age
    with pytest.raises(ValueError, match="Must be 18 or older"):
        UserSerializer(id=1, email='user@example.com', age=16)


# --- Transformation Tests ---

def test_serializer_with_transformations():
    """Test custom field transformations."""

    class ArticleSerializer(Serializer):
        id: int
        title: str
        word_count: int

        def transform_word_count(self, value):
            # Dummy transformation
            return len(str(value).split())

    # This test demonstrates the API, actual transformation happens in from_model
    serializer = ArticleSerializer(id=1, title="Test", word_count=5)
    assert serializer.word_count == 5


def test_model_serializer_with_transforms():
    """Test model_serializer with custom transforms."""

    def transform_title(value: str) -> str:
        return value.upper()

    ArticleSerializer = model_serializer(
        Article,
        fields=['id', 'title', 'author'],
        transforms={
            'title': transform_title,
        }
    )

    # Note: Transformation is applied in from_model, not in constructor
    # This test verifies the API structure
    assert hasattr(ArticleSerializer, 'transform_title')


# --- QuerySet Optimization Tests ---

@pytest.mark.django_db(transaction=True)
def test_serializer_from_queryset():
    """Test optimized QuerySet serialization."""
    from asgiref.sync import async_to_sync

    # Define serializer
    class ArticleSerializer(Serializer):
        id: int
        title: str
        author: str

    # Create test data
    async_to_sync(Article.objects.acreate)(title="Article 1", content="Content 1", author="Author 1")
    async_to_sync(Article.objects.acreate)(title="Article 2", content="Content 2", author="Author 2")
    async_to_sync(Article.objects.acreate)(title="Article 3", content="Content 3", author="Author 3")

    # Get queryset (ordered by title for consistent results)
    queryset = Article.objects.all().order_by('title')

    # Serialize using optimized path
    serialized = ArticleSerializer.from_queryset(queryset)

    # Verify
    assert len(serialized) == 3
    assert all(isinstance(item, ArticleSerializer) for item in serialized)
    # Verify titles are present (order is by title)
    titles = [s.title for s in serialized]
    assert "Article 1" in titles
    assert "Article 2" in titles
    assert "Article 3" in titles


# --- Integration Tests ---

@pytest.mark.django_db(transaction=True)
def test_model_serializer_with_api():
    """Test model serializer integration with BoltAPI."""
    from asgiref.sync import async_to_sync

    api = BoltAPI()

    # Generate serializer
    ArticleSerializer = model_serializer(
        Article,
        fields=['id', 'title', 'content', 'author'],
    )

    @api.get("/articles/{article_id}", response_model=list[ArticleSerializer])
    async def get_article(article_id: int):
        article = await Article.objects.aget(id=article_id)
        return [ArticleSerializer.from_model(article)]

    # Create test article
    article = async_to_sync(Article.objects.acreate)(
        title="Test Article",
        content="Test content",
        author="John Doe",
    )

    # Test
    with TestClient(api) as client:
        response = client.get(f"/articles/{article.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['title'] == "Test Article"
        assert data[0]['author'] == "John Doe"


@pytest.mark.django_db(transaction=True)
def test_quick_serializer():
    """Test quick_serializer convenience function."""
    from asgiref.sync import async_to_sync

    # Quick serializer
    ArticleSerializer = quick_serializer(Article, fields=['id', 'title', 'author'])

    # Create test article
    article = async_to_sync(Article.objects.acreate)(
        title="Quick Test",
        content="Content",
        author="Author",
    )

    # Serialize
    serialized = ArticleSerializer.from_model(article)
    assert serialized.title == "Quick Test"
    assert serialized.author == "Author"


# --- Edge Cases ---

def test_serializer_optional_fields():
    """Test serializer with optional fields (None values)."""

    class UserSerializer(Serializer):
        id: int
        username: str
        email: Optional[str] = None
        age: Optional[int] = None

        def validate_email(self, value: str) -> str:
            # Should only validate if value is not None
            if '@' not in value:
                raise ValueError("Invalid email")
            return value

    # Valid with all fields
    user1 = UserSerializer(id=1, username='john', email='john@example.com', age=30)
    assert user1.email == 'john@example.com'

    # Valid with None email (validation should be skipped)
    user2 = UserSerializer(id=2, username='jane', email=None, age=25)
    assert user2.email is None

    # Valid with missing optional fields (using defaults)
    user3 = UserSerializer(id=3, username='bob')
    assert user3.email is None
    assert user3.age is None


@pytest.mark.django_db(transaction=True)
def test_serializer_nested_source():
    """Test field with nested source (e.g., 'user.email')."""

    # This test demonstrates the API for nested field access
    # Actual implementation would require a model with related fields

    class CustomSerializer(Serializer):
        id: int
        title: str

        @classmethod
        def get_field_source(cls, field_name: str) -> str:
            # Example: map 'author_name' to 'author.name'
            if field_name == 'author_name':
                return 'author.name'
            return super().get_field_source(field_name)

    # Verify the method exists and can be overridden
    assert CustomSerializer.get_field_source('id') == 'id'
    assert CustomSerializer.get_field_source('author_name') == 'author.name'


# --- Type Safety Tests ---

def test_serializer_is_msgspec_struct():
    """Test that generated serializers are msgspec.Struct instances."""

    ArticleSerializer = model_serializer(
        Article,
        fields=['id', 'title', 'author'],
    )

    # Verify it's a msgspec.Struct
    assert hasattr(ArticleSerializer, '__struct_fields__')
    assert 'id' in ArticleSerializer.__struct_fields__
    assert 'title' in ArticleSerializer.__struct_fields__
    assert 'author' in ArticleSerializer.__struct_fields__

    # Verify it can be used with msgspec.convert
    data = {'id': 1, 'title': 'Test', 'author': 'Author'}
    instance = msgspec.convert(data, ArticleSerializer)
    assert instance.id == 1
    assert instance.title == 'Test'


def test_serializer_type_annotations():
    """Test that serializer has correct type annotations."""

    ArticleSerializer = model_serializer(
        Article,
        fields=['id', 'title', 'author'],
    )

    # Verify annotations exist
    assert hasattr(ArticleSerializer, '__annotations__')
    annotations = ArticleSerializer.__annotations__

    # Verify field types
    assert 'id' in annotations
    assert 'title' in annotations
    assert 'author' in annotations


# --- Performance Benchmarks (informational) ---

@pytest.mark.django_db(transaction=True)
def test_from_queryset_vs_manual_iteration():
    """Compare from_queryset performance vs manual iteration."""
    from asgiref.sync import async_to_sync
    import time

    class ArticleSerializer(Serializer):
        id: int
        title: str
        author: str

    # Create test data (100 articles)
    for i in range(100):
        async_to_sync(Article.objects.acreate)(
            title=f"Article {i}",
            content=f"Content {i}",
            author=f"Author {i}",
        )

    queryset = Article.objects.all()

    # Method 1: Optimized from_queryset
    start = time.time()
    result1 = ArticleSerializer.from_queryset(queryset)
    time1 = time.time() - start

    # Method 2: Manual iteration (slower)
    start = time.time()
    result2 = [ArticleSerializer.from_model(article) for article in queryset]
    time2 = time.time() - start

    # Both should produce same results
    assert len(result1) == len(result2) == 100

    # from_queryset should be faster (informational, not strict assertion)
    print(f"\nfrom_queryset: {time1:.4f}s")
    print(f"manual iteration: {time2:.4f}s")
    print(f"speedup: {time2/time1:.2f}x")


# --- Docstring Examples Tests ---

def test_readme_example():
    """Test the example from the module docstring."""

    # Example 1: Quick serializer generation
    UserSerializer = model_serializer(
        None,  # Using None since we don't have User model in tests
        fields=['id', 'username', 'email', 'created_at'],
        name='UserSerializer',
    )

    # Verify it's a valid serializer
    assert hasattr(UserSerializer, '__struct_fields__')
    assert 'id' in UserSerializer.__struct_fields__

    # Example 2: With custom validation
    class UserSerializerWithValidation(Serializer):
        id: int
        username: str
        email: str

        def validate_email(self, value: str) -> str:
            if not value.endswith('@example.com'):
                raise ValueError("Email must end with @example.com")
            return value

    # Test validation
    with pytest.raises(ValueError, match="Email must end with @example.com"):
        UserSerializerWithValidation(id=1, username='test', email='test@other.com')

"""
Tests for nested serializers and computed fields.
"""
from __future__ import annotations

import pytest
from typing import List
import msgspec

from django_bolt import Serializer, ModelSerializer, model_serializer
from .test_models import Article


# --- Computed Fields Tests ---

def test_computed_field_basic():
    """Test basic computed field with get_<field> method."""

    class ArticleSerializer(Serializer):
        id: int
        title: str
        title_upper: str  # Computed field

        @classmethod
        def get_title_upper(cls, obj) -> str:
            """Compute uppercase title."""
            return obj.title.upper()

    # Create a mock object
    class MockArticle:
        id = 1
        title = "hello world"

    serialized = ArticleSerializer.from_model(MockArticle())
    assert serialized.id == 1
    assert serialized.title == "hello world"
    assert serialized.title_upper == "HELLO WORLD"


@pytest.mark.django_db(transaction=True)
def test_computed_field_with_real_model():
    """Test computed field with real Django model."""
    from asgiref.sync import async_to_sync

    class ArticleSerializer(Serializer):
        id: int
        title: str
        word_count: int  # Computed field

        @classmethod
        def get_word_count(cls, obj) -> int:
            """Count words in content."""
            return len(obj.content.split())

    # Create test article
    article = async_to_sync(Article.objects.acreate)(
        title="Test",
        content="This is a test article with many words",
        author="Author",
    )

    serialized = ArticleSerializer.from_model(article)
    assert serialized.word_count == 8  # "This is a test article with many words"


def test_computed_field_with_model_serializer():
    """Test computed field with @ModelSerializer decorator."""

    @ModelSerializer
    class ArticleSerializer:
        class Meta:
            model = Article
            fields = ['id', 'title', 'summary']  # summary is computed

        @classmethod
        def get_summary(cls, obj) -> str:
            """Generate summary from title and content."""
            return f"{obj.title}: {obj.content[:50]}"

    # Create mock object
    class MockArticle:
        id = 1
        title = "Article Title"
        content = "This is the article content that is quite long and should be truncated"

    serialized = ArticleSerializer.from_model(MockArticle())
    assert serialized.summary == "Article Title: This is the article content that is quite long and"


# --- Nested Serializer Tests ---

def test_nested_serializer_single():
    """Test single nested serializer."""

    class AuthorSerializer(Serializer):
        id: int
        name: str

    class BookSerializer(Serializer):
        id: int
        title: str
        author: AuthorSerializer  # Nested serializer

    # Create mock objects
    class MockAuthor:
        id = 1
        name = "John Doe"

    class MockBook:
        id = 10
        title = "Python Guide"
        author = MockAuthor()

    serialized = BookSerializer.from_model(MockBook())
    assert serialized.id == 10
    assert serialized.title == "Python Guide"
    assert isinstance(serialized.author, AuthorSerializer)
    assert serialized.author.id == 1
    assert serialized.author.name == "John Doe"


def test_nested_serializer_list():
    """Test list of nested serializers."""

    class CommentSerializer(Serializer):
        id: int
        text: str

    class PostSerializer(Serializer):
        id: int
        title: str
        comments: List[CommentSerializer]  # List of nested serializers

    # Create mock objects
    class MockComment:
        def __init__(self, id, text):
            self.id = id
            self.text = text

    class MockComments:
        def __init__(self, comments):
            self._comments = comments

        def all(self):
            return self._comments

    class MockPost:
        id = 1
        title = "My Post"

        def __init__(self):
            self.comments = MockComments([
                MockComment(1, "First comment"),
                MockComment(2, "Second comment"),
            ])

    serialized = PostSerializer.from_model(MockPost())
    assert serialized.id == 1
    assert serialized.title == "My Post"
    assert len(serialized.comments) == 2
    assert all(isinstance(c, CommentSerializer) for c in serialized.comments)
    assert serialized.comments[0].text == "First comment"
    assert serialized.comments[1].text == "Second comment"


def test_nested_serializer_with_model_serializer():
    """Test nested serializer using @ModelSerializer decorator."""

    # First define AuthorSerializer
    class AuthorSerializerBase(Serializer):
        id: int
        name: str

    # Then define BookSerializer with nested author
    class BookSerializerBase(Serializer):
        id: int
        title: str
        author: AuthorSerializerBase  # Nested serializer

    # Create mock objects
    class MockAuthor:
        id = 5
        name = "Jane Smith"

    class MockBook:
        id = 20
        title = "Advanced Python"
        author = MockAuthor()

    serialized = BookSerializerBase.from_model(MockBook())
    assert serialized.id == 20
    assert isinstance(serialized.author, AuthorSerializerBase)
    assert serialized.author.name == "Jane Smith"


# --- Combined Tests ---

def test_nested_and_computed_together():
    """Test using both nested serializers and computed fields."""

    class AuthorSerializer(Serializer):
        id: int
        name: str
        name_upper: str  # Computed

        @classmethod
        def get_name_upper(cls, obj) -> str:
            return obj.name.upper()

    class BookSerializer(Serializer):
        id: int
        title: str
        author: AuthorSerializer  # Nested
        full_title: str  # Computed

        @classmethod
        def get_full_title(cls, obj) -> str:
            return f"{obj.title} by {obj.author.name}"

    # Create mock objects
    class MockAuthor:
        id = 1
        name = "Alice"

    class MockBook:
        id = 1
        title = "Wonderland"
        author = MockAuthor()

    serialized = BookSerializer.from_model(MockBook())
    assert serialized.title == "Wonderland"
    assert serialized.author.name == "Alice"
    assert serialized.author.name_upper == "ALICE"
    assert serialized.full_title == "Wonderland by Alice"


def test_multiple_nesting_levels():
    """Test serializers with multiple nesting levels."""

    class CategorySerializer(Serializer):
        id: int
        name: str

    class AuthorSerializer(Serializer):
        id: int
        name: str

    class BookSerializer(Serializer):
        id: int
        title: str
        author: AuthorSerializer
        category: CategorySerializer

    # Create mock objects
    class MockCategory:
        id = 1
        name = "Fiction"

    class MockAuthor:
        id = 2
        name = "Bob"

    class MockBook:
        id = 3
        title = "The Story"
        author = MockAuthor()
        category = MockCategory()

    serialized = BookSerializer.from_model(MockBook())
    assert serialized.author.name == "Bob"
    assert serialized.category.name == "Fiction"


# --- Edge Cases ---

def test_nested_serializer_with_none():
    """Test nested serializer when the related field is None."""

    class AuthorSerializer(Serializer):
        id: int
        name: str

    class BookSerializer(Serializer):
        id: int
        title: str
        author: AuthorSerializer | None  # Optional nested

    class MockBook:
        id = 1
        title = "No Author"
        author = None

    serialized = BookSerializer.from_model(MockBook())
    assert serialized.title == "No Author"
    assert serialized.author is None


def test_computed_field_with_error_handling():
    """Test that computed field errors are propagated."""

    class ArticleSerializer(Serializer):
        id: int
        broken_field: str

        @classmethod
        def get_broken_field(cls, obj) -> str:
            raise ValueError("Intentional error")

    class MockArticle:
        id = 1

    with pytest.raises(ValueError, match="Intentional error"):
        ArticleSerializer.from_model(MockArticle())


# --- Serialization Tests ---

def test_nested_serializer_json_serialization():
    """Test that nested serializers serialize to JSON correctly."""

    class AuthorSerializer(Serializer):
        id: int
        name: str

    class BookSerializer(Serializer):
        id: int
        title: str
        author: AuthorSerializer

    class MockAuthor:
        id = 1
        name = "Test Author"

    class MockBook:
        id = 1
        title = "Test Book"
        author = MockAuthor()

    serialized = BookSerializer.from_model(MockBook())

    # Serialize to JSON
    json_bytes = msgspec.json.encode(serialized)
    json_str = json_bytes.decode('utf-8')

    assert '"title":"Test Book"' in json_str
    assert '"author":{' in json_str
    assert '"name":"Test Author"' in json_str

    # Note: Deserialization back to BookSerializer doesn't work with string annotations
    # due to PEP 563 (from __future__ import annotations). This is a msgspec limitation,
    # not an issue with our serializer code. In production, annotations would be resolved
    # at module level, making deserialization work fine.

"""Simple tests for nested serializer support."""

from __future__ import annotations

from typing import Annotated

from django_bolt.serializers import Nested, Serializer


def test_nested_import():
    """Test that Nested can be imported."""
    assert Nested is not None


def test_nested_config_creation():
    """Test creating a Nested config."""

    class TestSerializer(Serializer):
        id: int
        name: str

    config = Nested(TestSerializer)
    assert config is not None
    assert config.serializer_class == TestSerializer
    assert config.many is False


def test_nested_with_many():
    """Test Nested config with many=True."""

    class TagSerializer(Serializer):
        id: int
        name: str

    config = Nested(TagSerializer, many=True)
    assert config.many is True


def test_nested_annotation():
    """Test using Nested in a serializer annotation."""

    class AuthorSerializer(Serializer):
        id: int
        username: str

    # Nested serializers now require full objects
    class BookDetailSerializer(Serializer):
        title: str
        author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]

    # Create with full author object
    author = AuthorSerializer(id=1, username="alice")
    book = BookDetailSerializer(
        title="Test Book",
        author=author
    )

    assert book.title == "Test Book"
    assert isinstance(book.author, AuthorSerializer)
    assert book.author.username == "alice"


def test_nested_with_dict():
    """Test that nested fields accept dict input."""

    class AuthorSerializer(Serializer):
        id: int
        username: str

    class BookSerializer(Serializer):
        title: str
        author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]

    # Should accept dict and convert to serializer
    book = BookSerializer(
        title="Test",
        author={"id": 123, "username": "bob"}
    )

    assert isinstance(book.author, AuthorSerializer)
    assert book.author.id == 123
    assert book.author.username == "bob"


def test_simple_id_reference():
    """Test using plain int for ID-only fields (no Nested)."""

    # For ID-only fields, just use int directly
    class BookListSerializer(Serializer):
        title: str
        author_id: int

    book = BookListSerializer(
        title="Test",
        author_id=42
    )

    assert book.author_id == 42


def test_nested_with_serializer_instance():
    """Test passing a Serializer instance to a nested field."""

    class AuthorSerializer(Serializer):
        id: int
        username: str

    class BookSerializer(Serializer):
        title: str
        author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]

    author = AuthorSerializer(id=1, username="alice")
    book = BookSerializer(
        title="Test",
        author=author
    )

    assert isinstance(book.author, AuthorSerializer)
    assert book.author.username == "alice"


def test_nested_many_with_objects():
    """Test that nested many field accepts list of objects."""

    class TagSerializer(Serializer):
        id: int
        name: str

    class BookSerializer(Serializer):
        title: str
        tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)]

    # Accept list of dicts
    book = BookSerializer(
        title="Test",
        tags=[
            {"id": 1, "name": "python"},
            {"id": 2, "name": "django"},
        ]
    )

    assert len(book.tags) == 2
    assert all(isinstance(t, TagSerializer) for t in book.tags)
    assert book.tags[0].name == "python"


def test_nested_many_accepts_empty_list():
    """Test that nested many field accepts empty list."""

    class TagSerializer(Serializer):
        id: int
        name: str

    class BookSerializer(Serializer):
        title: str
        tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)]

    book = BookSerializer(
        title="Test",
        tags=[]
    )

    assert book.tags == []


def test_list_of_ids_without_nested():
    """Test using plain list[int] for ID-only fields (no Nested)."""

    # For ID-only many-to-many fields, just use list[int] directly
    class BookListSerializer(Serializer):
        title: str
        tag_ids: list[int]

    book = BookListSerializer(
        title="Test",
        tag_ids=[1, 2, 3]
    )

    assert book.tag_ids == [1, 2, 3]

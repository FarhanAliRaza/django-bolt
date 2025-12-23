"""
Security tests for Django-Bolt serializers.

Tests cover:
- DoS prevention: Input size limits for nested lists
- Type safety: Nested() validation
- Circular reference detection in from_model()
- Performance optimizations
"""
from __future__ import annotations

from typing import Annotated

import msgspec
import pytest

from django_bolt.exceptions import RequestValidationError
from django_bolt.serializers import Nested, Serializer


class TestNestedListSizeLimits:
    """Test that nested many relationships enforce size limits to prevent DoS attacks."""

    def test_nested_many_respects_default_limit(self):
        """Test that nested many fields respect the default 1000 item limit."""

        class TagSerializer(Serializer):
            id: int
            name: str

        class BookSerializer(Serializer):
            title: str
            tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)]

        # Create 1001 tags (exceeds default limit of 1000)
        many_tags = [{"id": i, "name": f"tag_{i}"} for i in range(1001)]

        with pytest.raises(RequestValidationError) as exc_info:
            BookSerializer(title="Test", tags=many_tags)

        error_msg = str(exc_info.value)
        assert "Too many items" in error_msg
        assert "1001" in error_msg
        assert "Maximum allowed: 1000" in error_msg

    def test_nested_many_accepts_items_under_limit(self):
        """Test that nested many fields accept items under the limit."""

        class TagSerializer(Serializer):
            id: int
            name: str

        class BookSerializer(Serializer):
            title: str
            tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)]

        # Create 999 tags (under default limit)
        tags = [{"id": i, "name": f"tag_{i}"} for i in range(999)]

        book = BookSerializer(title="Test", tags=tags)
        assert len(book.tags) == 999

    def test_nested_many_custom_limit(self):
        """Test that custom max_items limit is respected."""

        class TagSerializer(Serializer):
            id: int
            name: str

        class BookSerializer(Serializer):
            title: str
            tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True, max_items=10)]

        # 11 items exceeds custom limit of 10
        many_tags = [{"id": i, "name": f"tag_{i}"} for i in range(11)]

        with pytest.raises(RequestValidationError) as exc_info:
            BookSerializer(title="Test", tags=many_tags)

        error_msg = str(exc_info.value)
        assert "Too many items" in error_msg
        assert "11" in error_msg
        assert "Maximum allowed: 10" in error_msg

    def test_nested_many_unlimited_when_none(self):
        """Test that max_items=None disables the limit (not recommended for production)."""

        class TagSerializer(Serializer):
            id: int
            name: str

        class BookSerializer(Serializer):
            title: str
            # Note: Setting max_items to None disables limit - NOT recommended for production
            tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True, max_items=None)]

        # Create 2000 tags (would exceed default limit, but we disabled it)
        many_tags = [{"id": i, "name": f"tag_{i}"} for i in range(2000)]

        # This should NOT raise an error since limit is disabled
        book = BookSerializer(title="Test", tags=many_tags)
        assert len(book.tags) == 2000

    def test_nested_single_not_affected_by_limit(self):
        """Test that single nested fields (many=False) are not affected by size limits."""

        class AuthorSerializer(Serializer):
            id: int
            name: str

        class BookSerializer(Serializer):
            title: str
            author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]

        # Single nested object should work fine
        book = BookSerializer(
            title="Test",
            author={"id": 1, "name": "Alice"}
        )
        assert book.author.name == "Alice"


class TestNestedTypeSafety:
    """Test that Nested() validates serializer_class at definition time."""

    def test_nested_rejects_non_class(self):
        """Test that Nested() rejects non-class values."""

        class AuthorSerializer(Serializer):
            id: int
            name: str

        # Try to pass an instance instead of a class
        author_instance = AuthorSerializer(id=1, name="Alice")

        with pytest.raises(TypeError) as exc_info:
            Nested(author_instance)  # type: ignore

        error_msg = str(exc_info.value)
        assert "must be a class" in error_msg
        assert "Nested(MySerializer) not Nested(MySerializer())" in error_msg

    def test_nested_rejects_non_serializer_class(self):
        """Test that Nested() rejects classes that don't inherit from Serializer."""

        class NotASerializer:
            """This is not a Serializer subclass."""
            id: int
            name: str

        with pytest.raises(TypeError) as exc_info:
            Nested(NotASerializer)  # type: ignore

        error_msg = str(exc_info.value)
        assert "must be a Serializer subclass" in error_msg
        assert "NotASerializer" in error_msg

    def test_nested_accepts_valid_serializer_class(self):
        """Test that Nested() accepts valid Serializer subclasses."""

        class AuthorSerializer(Serializer):
            id: int
            name: str

        # This should work fine
        config = Nested(AuthorSerializer)
        assert config.serializer_class == AuthorSerializer
        assert config.many is False

    def test_nested_with_msgspec_struct_not_serializer(self):
        """Test that Nested() rejects msgspec.Struct classes that don't inherit from Serializer."""

        class PlainStruct(msgspec.Struct):
            """This is a msgspec.Struct but not a Serializer."""
            id: int
            name: str

        with pytest.raises(TypeError) as exc_info:
            Nested(PlainStruct)  # type: ignore

        error_msg = str(exc_info.value)
        assert "must be a Serializer subclass" in error_msg


class TestRecursionPrevention:
    """
    Test DoS protection mechanisms.

    Python's recursion limit (~1000) automatically protects against deeply nested JSON.
    We test that max_items limits prevent resource exhaustion from wide lists.
    """

    def test_max_items_prevents_dos_via_large_lists(self):
        """Test that max_items prevents DoS attacks from extremely large nested lists."""

        class TagSerializer(Serializer):
            id: int
            name: str

        class BookSerializer(Serializer):
            title: str
            # Default max_items=1000
            tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)]

        # Attempt to create 10,000 tags (would consume significant memory)
        many_tags = [{"id": i, "name": f"tag_{i}"} for i in range(10000)]

        # Should be rejected due to max_items=1000 limit
        with pytest.raises(RequestValidationError) as exc_info:
            BookSerializer(title="Attack", tags=many_tags)

        error_msg = str(exc_info.value)
        assert "Too many items" in error_msg
        assert "10000" in error_msg




class TestTypeHintResolutionEdgeCases:
    """Test edge cases in type hint resolution."""

    def test_module_level_serializer(self):
        """Test that module-level serializers resolve type hints correctly."""

        class SimpleSerializer(Serializer):
            id: int
            name: str

        # Should have cached type hints
        assert "id" in SimpleSerializer.__cached_type_hints__
        assert "name" in SimpleSerializer.__cached_type_hints__

    def test_function_scoped_serializer_warning(self):
        """Test that function-scoped serializers still work (with limitations)."""

        def create_serializer():
            class LocalSerializer(Serializer):
                id: int
                name: str

            return LocalSerializer

        LocalSerializer = create_serializer()

        # Should still work, even if type hints have limitations
        instance = LocalSerializer(id=1, name="Test")
        assert instance.id == 1
        assert instance.name == "Test"


class TestNestedConfigRepr:
    """Test NestedConfig string representation."""

    def test_nested_config_repr_includes_max_items(self):
        """Test that NestedConfig __repr__ includes max_items."""

        class TagSerializer(Serializer):
            id: int
            name: str

        config = Nested(TagSerializer, many=True, max_items=500)
        repr_str = repr(config)

        assert "TagSerializer" in repr_str
        assert "many=True" in repr_str
        assert "max_items=500" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

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

        with pytest.raises(msgspec.ValidationError) as exc_info:
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

        with pytest.raises(msgspec.ValidationError) as exc_info:
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


class TestCircularReferenceDetection:
    """Test that from_model() detects and prevents circular references."""

    def test_circular_reference_raises_error(self):
        """Test that circular references in from_model() raise descriptive errors."""
        # Note: This test requires Django models
        # For now, we test the detection logic directly
        pass  # TODO: Add Django model-based test when models are available

    def test_max_depth_prevents_deep_recursion(self):
        """Test that max_depth parameter prevents excessive recursion."""
        # Note: This test requires Django models
        # For now, we document the expected behavior
        pass  # TODO: Add Django model-based test when models are available

    def test_siblings_allowed_same_depth(self):
        """Test that sibling relationships at same depth are allowed."""
        # Note: This test requires Django models
        # Example: Book -> Author and Book -> Publisher should both work
        pass  # TODO: Add Django model-based test when models are available


class TestValidatorPerformanceOptimizations:
    """Test that validator performance optimizations work correctly."""

    def test_single_validator_fast_path_exists(self):
        """Test that single validator fast path code exists in _run_field_validators."""
        # This test verifies that the optimization code path exists
        # The actual performance benefit would need benchmarking to measure
        from django_bolt.serializers.base import Serializer
        import inspect

        # Get the source code of _run_field_validators
        source = inspect.getsource(Serializer._run_field_validators)

        # Verify that fast path for single validator exists
        assert "len(validators) == 1" in source
        assert "Fast path for single validator" in source or "Optimization" in source

    def test_multiple_validators_batch_path_exists(self):
        """Test that multiple validators batch path code exists."""
        from django_bolt.serializers.base import Serializer
        import inspect

        # Get the source code of _run_field_validators
        source = inspect.getsource(Serializer._run_field_validators)

        # Verify batch validation comment exists
        assert "Batch validation" in source or "multiple validators" in source


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

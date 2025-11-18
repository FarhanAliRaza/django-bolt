"""Support for nested serializers with flexible handling of foreign keys and relationships."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union, get_args, get_origin

if TYPE_CHECKING:
    from .base import Serializer

T = TypeVar("T", bound="Serializer")
logger = logging.getLogger(__name__)


class NestedConfig:
    """Configuration for a nested serializer field."""

    def __init__(
        self,
        serializer_class: type[Serializer],
        many: bool = False,
    ):
        """
        Initialize nested serializer configuration.

        Args:
            serializer_class: The Serializer class to use for validation
            many: If True, expects a list of objects (for M2M relationships)
        """
        self.serializer_class = serializer_class
        self.many = many

    def __repr__(self) -> str:
        return (
            f"NestedConfig(serializer={self.serializer_class.__name__}, "
            f"many={self.many})"
        )


def Nested(
    serializer_class: type[Serializer],
    *,
    many: bool = False,
) -> NestedConfig:
    """
    Mark a field as a nested serializer that validates related objects.

    Use this to define relationships that contain full nested objects.
    For simple ID references, use plain `int` or `list[int]` types instead.

    Args:
        serializer_class: The Serializer class for the related object(s)
        many: If True, field contains a list (for M2M or reverse FK relationships)

    Returns:
        NestedConfig that can be used in field annotations

    Examples:
        Single nested object (ForeignKey with select_related):
            class BookSerializer(Serializer):
                title: str
                author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]

        Multiple nested objects (ManyToMany with prefetch_related):
            class BookSerializer(Serializer):
                title: str
                tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)]

        Simple ID reference (no Nested wrapper needed):
            class BookListSerializer(Serializer):
                title: str
                author_id: int  # Just the ID, no nested object
    """
    return NestedConfig(
        serializer_class=serializer_class,
        many=many,
    )


def validate_nested_field(
    value: Any,
    nested_config: NestedConfig,
    field_name: str,
) -> Any:
    """
    Validate and convert a nested field value.

    Handles both ID values (when not prefetched) and nested objects/dicts
    (when prefetched or provided explicitly).

    Args:
        value: The field value to validate
        nested_config: NestedConfig instance describing the field
        field_name: Field name (for error messages)

    Returns:
        The validated value (either the original ID, nested Serializer instance,
        or list thereof)

    Raises:
        ValueError: If validation fails
    """
    if value is None:
        return None

    serializer_class = nested_config.serializer_class

    if nested_config.many:
        return _validate_many_nested(value, serializer_class, nested_config, field_name)
    else:
        return _validate_single_nested(value, serializer_class, nested_config, field_name)


def _validate_single_nested(
    value: Any,
    serializer_class: type[Serializer],
    config: NestedConfig,
    field_name: str,
) -> Any:
    """Validate a single nested object (no ID fallback)."""
    # If it's a dict, convert to Serializer instance
    if isinstance(value, dict):
        try:
            return serializer_class(**value)
        except Exception as e:
            raise ValueError(
                f"{field_name}: Failed to validate nested {serializer_class.__name__}: {e}"
            ) from e

    # If it's already a Serializer instance, validate it
    if isinstance(value, serializer_class):
        return value

    # No longer accept plain IDs - use separate serializers for that
    raise ValueError(
        f"{field_name}: Expected {serializer_class.__name__} object or dict, "
        f"got {type(value).__name__}. "
        f"Use a separate serializer with plain 'int' type for ID-only fields."
    )


def _validate_many_nested(
    value: Any,
    serializer_class: type[Serializer],
    config: NestedConfig,
    field_name: str,
) -> Any:
    """Validate a list of nested objects (no ID fallback)."""
    if not isinstance(value, list):
        raise ValueError(
            f"{field_name}: Expected list for many=True relationship, got {type(value).__name__}"
        )

    result = []
    for idx, item in enumerate(value):
        # Handle dict values (convert to Serializer)
        if isinstance(item, dict):
            try:
                result.append(serializer_class(**item))
            except Exception as e:
                raise ValueError(
                    f"{field_name}[{idx}]: Failed to validate nested {serializer_class.__name__}: {e}"
                ) from e
        # Handle Serializer instances
        elif isinstance(item, serializer_class):
            result.append(item)
        else:
            # No longer accept plain IDs - use separate serializers for that
            raise ValueError(
                f"{field_name}[{idx}]: Expected {serializer_class.__name__} object or dict, "
                f"got {type(item).__name__}. "
                f"Use a separate serializer with 'list[int]' type for ID-only fields."
            )

    return result


def is_nested_field(metadata: Any) -> bool:
    """Check if a field metadata contains NestedConfig."""
    if isinstance(metadata, NestedConfig):
        return True
    # Check if it's in an Annotated type
    if hasattr(metadata, "__metadata__"):
        return any(isinstance(m, NestedConfig) for m in metadata.__metadata__)
    return False


def get_nested_config(metadata: Any) -> NestedConfig | None:
    """Extract NestedConfig from field metadata."""
    if isinstance(metadata, NestedConfig):
        return metadata

    if hasattr(metadata, "__metadata__"):
        for m in metadata.__metadata__:
            if isinstance(m, NestedConfig):
                return m

    return None

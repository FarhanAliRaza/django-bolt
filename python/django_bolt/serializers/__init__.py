"""Enhanced Serializer system for django-bolt with validation and Django model integration."""

from __future__ import annotations

from .base import Serializer, SerializerView, clear_subset_cache, get_subset_cache_size
from .decorators import computed_field, field_validator, model_validator
from .fields import FieldConfig, field
from .helpers import create_serializer, create_serializer_set
from .nested import Nested

# Re-export common types for convenience
# Full list available in django_bolt.serializers.types
from .types import (
    Email,
    HttpUrl,
    HttpsUrl,
    PhoneNumber,
    Slug,
    Username,
    NonEmptyStr,
    PositiveInt,
    NonNegativeInt,
    Percentage,
)

__all__ = [
    # Core classes
    "Serializer",
    "SerializerView",
    # Field configuration
    "field",
    "FieldConfig",
    # Decorators
    "field_validator",
    "model_validator",
    "computed_field",
    # Helpers
    "create_serializer",
    "create_serializer_set",
    "Nested",
    # Cache utilities
    "clear_subset_cache",
    "get_subset_cache_size",
    # Common types (full list in .types module)
    "Email",
    "HttpUrl",
    "HttpsUrl",
    "PhoneNumber",
    "Slug",
    "Username",
    "NonEmptyStr",
    "PositiveInt",
    "NonNegativeInt",
    "Percentage",
]

"""
Field mapping utilities for converting Django model fields to msgspec type annotations.

This module provides comprehensive mapping between Django model fields and
msgspec-compatible type annotations, including constraint extraction for
validation.

Usage:
    from django_bolt.serializers.field_mapping import get_field_type, get_field_kwargs

    field_type = get_field_type(model_field, depth=0)
    kwargs = get_field_kwargs(model_field)
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Annotated, Any, Literal
from uuid import UUID

from django.core import validators as django_validators
from django.db import models
from msgspec import Meta

if TYPE_CHECKING:
    from .model_meta import RelationInfo


# Sentinel for required fields (no default)
class _Required:
    """Sentinel to indicate a field is required (has no default)."""

    def __repr__(self) -> str:
        return "REQUIRED"


REQUIRED = _Required()


def get_field_type(
    model_field: models.Field,
    depth: int = 0,
    relation_info: RelationInfo | None = None,
) -> type:
    """
    Get the msgspec-compatible type annotation for a Django model field.

    Args:
        model_field: Django model field instance
        depth: Nesting depth for relationships (0 = IDs only, >0 = nested)
        relation_info: Optional RelationInfo for relationship fields

    Returns:
        Type annotation suitable for msgspec struct fields

    Example:
        >>> get_field_type(models.CharField(max_length=100))
        Annotated[str, Meta(max_length=100)]
        >>> get_field_type(models.IntegerField(null=True))
        int | None
    """
    # Handle relationships separately
    if isinstance(model_field, models.ForeignKey):
        return _get_fk_type(model_field, depth)
    if isinstance(model_field, models.OneToOneField):
        return _get_one_to_one_type(model_field, depth)
    if isinstance(model_field, models.ManyToManyField):
        return _get_m2m_type(model_field, depth)

    # Get base type and constraints
    base_type = _get_base_type(model_field)
    constraints = _get_constraints(model_field)

    # Handle choices - use Literal type
    if model_field.choices:
        choice_values = tuple(choice[0] for choice in model_field.choices)
        base_type = Literal[choice_values]  # type: ignore
        constraints = {}  # Choices don't need additional constraints

    # Apply nullable
    if model_field.null and not isinstance(model_field, models.BooleanField):
        base_type = base_type | None

    # Apply constraints if any
    if constraints:
        return Annotated[base_type, Meta(**constraints)]

    return base_type


def _get_base_type(model_field: models.Field) -> type:
    """Get the Python type for a Django model field."""
    # Text fields
    if isinstance(model_field, models.CharField):
        return str
    if isinstance(model_field, models.TextField):
        return str
    if isinstance(model_field, models.EmailField):
        return str
    if isinstance(model_field, models.URLField):
        return str
    if isinstance(model_field, models.SlugField):
        return str
    if isinstance(model_field, models.FilePathField):
        return str
    if isinstance(model_field, models.GenericIPAddressField):
        return str

    # Numeric fields
    if isinstance(model_field, models.IntegerField):
        return int
    if isinstance(model_field, models.BigIntegerField):
        return int
    if isinstance(model_field, models.SmallIntegerField):
        return int
    if isinstance(model_field, models.PositiveIntegerField):
        return int
    if isinstance(model_field, models.PositiveSmallIntegerField):
        return int
    if isinstance(model_field, models.PositiveBigIntegerField):
        return int
    if isinstance(model_field, models.FloatField):
        return float
    if isinstance(model_field, models.DecimalField):
        # Use Decimal for precision, or float for JSON compatibility
        return Decimal

    # Boolean
    if isinstance(model_field, models.BooleanField):
        return bool
    if isinstance(model_field, models.NullBooleanField):
        return bool | None

    # Date/Time fields
    if isinstance(model_field, models.DateTimeField):
        return datetime
    if isinstance(model_field, models.DateField):
        return date
    if isinstance(model_field, models.TimeField):
        return time
    if isinstance(model_field, models.DurationField):
        return timedelta

    # UUID
    if isinstance(model_field, models.UUIDField):
        return UUID

    # Auto fields (read-only)
    if isinstance(model_field, (models.AutoField, models.BigAutoField)):
        return int

    # Binary
    if isinstance(model_field, models.BinaryField):
        return bytes

    # JSON
    if hasattr(models, "JSONField") and isinstance(model_field, models.JSONField):
        return dict | list

    # File fields - return string (URL/path)
    if isinstance(model_field, models.FileField):
        return str
    if isinstance(model_field, models.ImageField):
        return str

    # Fallback
    return Any


def _get_constraints(model_field: models.Field) -> dict[str, Any]:
    """
    Extract msgspec Meta constraints from a Django model field.

    Args:
        model_field: Django model field instance

    Returns:
        Dict of constraint kwargs for msgspec.Meta
    """
    constraints: dict[str, Any] = {}

    # String constraints
    max_length = getattr(model_field, "max_length", None)
    if max_length is not None and isinstance(
        model_field, (models.CharField, models.TextField, models.FileField)
    ):
        constraints["max_length"] = max_length

    # Extract from validators
    for validator in model_field.validators:
        # Min/Max length
        if isinstance(validator, django_validators.MinLengthValidator):
            constraints["min_length"] = validator.limit_value
        elif isinstance(validator, django_validators.MaxLengthValidator):
            if "max_length" not in constraints:
                constraints["max_length"] = validator.limit_value

        # Min/Max value
        elif isinstance(validator, django_validators.MinValueValidator):
            constraints["ge"] = validator.limit_value
        elif isinstance(validator, django_validators.MaxValueValidator):
            constraints["le"] = validator.limit_value

    # Decimal constraints
    if isinstance(model_field, models.DecimalField):
        # Note: msgspec doesn't directly support decimal_places
        # but we can use pattern for validation
        pass

    return constraints


def _get_fk_type(model_field: models.ForeignKey, depth: int) -> type:
    """Get type for ForeignKey field."""
    if depth > 0:
        # For nested serialization, we'd need to create a nested type
        # This is handled at the serializer level
        # For now, return int (PK)
        return int | None if model_field.null else int
    else:
        # Return PK type
        return int | None if model_field.null else int


def _get_one_to_one_type(model_field: models.OneToOneField, depth: int) -> type:
    """Get type for OneToOneField."""
    if depth > 0:
        return int | None if model_field.null else int
    else:
        return int | None if model_field.null else int


def _get_m2m_type(model_field: models.ManyToManyField, depth: int) -> type:
    """Get type for ManyToManyField."""
    if depth > 0:
        # Nested list of objects - handled at serializer level
        return list[int]
    else:
        # List of PKs
        return list[int]


def get_field_kwargs(field_name: str, model_field: models.Field) -> dict[str, Any]:
    """
    Get field configuration kwargs similar to DRF's get_field_kwargs.

    Args:
        field_name: Name of the field
        model_field: Django model field instance

    Returns:
        Dict of field configuration options
    """
    kwargs: dict[str, Any] = {}

    # Label (verbose_name)
    if model_field.verbose_name:
        default_label = field_name.replace("_", " ").capitalize()
        verbose = str(model_field.verbose_name).capitalize()
        if verbose != default_label:
            kwargs["label"] = verbose

    # Help text
    if model_field.help_text:
        kwargs["help_text"] = str(model_field.help_text)

    # Read-only detection
    if isinstance(model_field, (models.AutoField, models.BigAutoField)) or not model_field.editable:
        kwargs["read_only"] = True

    # Required detection
    if kwargs.get("read_only") or model_field.has_default() or model_field.blank or model_field.null:
        kwargs["required"] = False
    else:
        kwargs["required"] = True

    # Allow null
    if model_field.null:
        kwargs["allow_null"] = True

    # Allow blank (for strings)
    if model_field.blank and isinstance(
        model_field, (models.CharField, models.TextField)
    ):
        kwargs["allow_blank"] = True

    # Unique
    if getattr(model_field, "unique", False) and not model_field.primary_key:
        kwargs["unique"] = True

    # Choices
    if model_field.choices:
        kwargs["choices"] = model_field.choices

    # Decimal specifics
    if isinstance(model_field, models.DecimalField):
        kwargs["max_digits"] = model_field.max_digits
        kwargs["decimal_places"] = model_field.decimal_places

    return kwargs


def get_field_default(model_field: models.Field) -> Any:
    """
    Get the default value for a Django model field.

    Args:
        model_field: Django model field instance

    Returns:
        Default value, or REQUIRED sentinel if field has no default
    """
    # Auto fields - always read-only, default to None for input
    if isinstance(model_field, (models.AutoField, models.BigAutoField)):
        return None

    # Has explicit default
    if model_field.has_default():
        default = model_field.default
        # Don't call callable defaults here - let them be called at runtime
        if callable(default) and default is not list and default is not dict:
            return default
        return default

    # Nullable means None is valid
    if model_field.null:
        return None

    # Blank string fields
    if model_field.blank and isinstance(
        model_field, (models.CharField, models.TextField)
    ):
        return ""

    # Boolean fields
    if isinstance(model_field, models.BooleanField):
        # BooleanField without null usually means required
        if model_field.has_default():
            return model_field.default
        return REQUIRED

    # No default - required
    return REQUIRED


def is_field_read_only(model_field: models.Field) -> bool:
    """
    Check if a field should be read-only.

    Args:
        model_field: Django model field instance

    Returns:
        True if field should be read-only
    """
    # Auto fields are always read-only, and non-editable fields are read-only
    return isinstance(model_field, (models.AutoField, models.BigAutoField)) or not model_field.editable


def is_field_required(model_field: models.Field) -> bool:
    """
    Check if a field is required for input.

    Args:
        model_field: Django model field instance

    Returns:
        True if field is required
    """
    # Read-only fields are never required
    if is_field_read_only(model_field):
        return False

    # Has default -> not required
    if model_field.has_default():
        return False

    # Nullable -> not required
    if model_field.null:
        return False

    # Blank -> not required
    return not model_field.blank


def needs_unique_validator(model_field: models.Field) -> bool:
    """
    Check if a field needs a unique validator.

    Args:
        model_field: Django model field instance

    Returns:
        True if field has unique constraint and needs validation
    """
    return getattr(model_field, "unique", False) and not model_field.primary_key


__all__ = [
    "REQUIRED",
    "get_field_type",
    "get_field_kwargs",
    "get_field_default",
    "is_field_read_only",
    "is_field_required",
    "needs_unique_validator",
]

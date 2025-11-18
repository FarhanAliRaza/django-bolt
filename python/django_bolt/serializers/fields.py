"""Django field to msgspec type mapping utilities."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Annotated, Literal, Type, get_args
from uuid import UUID

import msgspec
from django.db import models
from msgspec import Meta


def get_msgspec_type_for_django_field(field: models.Field, **field_kwargs: Any) -> Type:
    """
    Convert a Django model field to a msgspec-compatible type annotation.

    Args:
        field: Django model field instance
        **field_kwargs: Additional type metadata (e.g., for constraints)

    Returns:
        A type annotation suitable for use in a msgspec.Struct

    Example:
        >>> get_msgspec_type_for_django_field(models.CharField(max_length=150))
        Annotated[str, Meta(max_length=150)]
    """
    # Build constraint metadata
    constraints: dict[str, Any] = {}

    # CharField and similar text fields
    if isinstance(field, models.CharField):
        # Check if field has choices - use Literal type for type safety
        if field.choices:
            # Extract choice values (first element of each tuple)
            choice_values = [choice[0] for choice in field.choices]
            # Create Literal type with all valid choices
            base_type = Literal[tuple(choice_values)]
        else:
            constraints["max_length"] = field.max_length
            base_type = str

    elif isinstance(field, models.TextField):
        base_type = str

    elif isinstance(field, models.EmailField):
        constraints["max_length"] = field.max_length
        base_type = str

    elif isinstance(field, models.URLField):
        constraints["max_length"] = field.max_length
        base_type = str

    elif isinstance(field, models.SlugField):
        constraints["max_length"] = field.max_length
        base_type = str

    # Numeric fields
    elif isinstance(field, models.IntegerField):
        # Check if field has choices - use Literal type for type safety
        if field.choices:
            # Extract choice values (first element of each tuple)
            choice_values = [choice[0] for choice in field.choices]
            # Create Literal type with all valid choices
            base_type = Literal[tuple(choice_values)]
        else:
            base_type = int
            # Handle validators for ranges
            for validator in field.validators:
                if hasattr(validator, "limit_value"):
                    if hasattr(validator, "message") and "greater" in validator.message:
                        constraints["ge"] = validator.limit_value
                    elif hasattr(validator, "message") and "less" in validator.message:
                        constraints["le"] = validator.limit_value

    elif isinstance(field, models.FloatField):
        base_type = float

    elif isinstance(field, models.DecimalField):
        # Decimal is a complex type, but we can use float for JSON API
        base_type = float

    elif isinstance(field, models.BooleanField):
        base_type = bool

    # Date/Time fields
    elif isinstance(field, models.DateTimeField):
        base_type = datetime

    elif isinstance(field, models.DateField):
        base_type = date

    elif isinstance(field, models.TimeField):
        base_type = time

    elif isinstance(field, models.DurationField):
        # Duration serializes as string in ISO format
        base_type = str

    # UUID field
    elif isinstance(field, models.UUIDField):
        base_type = UUID

    # ForeignKey and relationships (simplified)
    elif isinstance(field, models.ForeignKey):
        # For now, just use int (the primary key)
        # Can be enhanced with nested serializers later
        base_type = int

    elif isinstance(field, models.OneToOneField):
        base_type = int

    # ManyToManyField
    elif isinstance(field, models.ManyToManyField):
        # Use list of ints (primary keys)
        # Can be enhanced with nested serializers later
        base_type = list[int]

    else:
        # Fallback for unknown field types
        base_type = Any

    # Handle nullable fields
    if field.null and not isinstance(field, models.BooleanField):
        base_type = base_type | None

    # Apply constraints if any
    if constraints:
        return Annotated[base_type, Meta(**constraints)]

    return base_type


def create_msgspec_field_definition(
    field: models.Field,
    write_only: bool = False,
    read_only: bool = False,
) -> tuple[str, Type, dict[str, Any]]:
    """
    Create a msgspec field definition from a Django field.

    Args:
        field: Django model field
        write_only: If True, field is input-only
        read_only: If True, field is output-only

    Returns:
        Tuple of (field_name, field_type, field_metadata)
    """
    field_type = get_msgspec_type_for_django_field(field)

    # Build metadata dict
    metadata: dict[str, Any] = {
        "write_only": write_only,
        "read_only": read_only,
        "help_text": field.help_text or None,
        "verbose_name": field.verbose_name,
    }

    return field.name, field_type, metadata

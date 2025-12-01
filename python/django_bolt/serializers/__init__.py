"""Enhanced Serializer system for django-bolt with validation and Django model integration."""

from __future__ import annotations

from msgspec import Meta

from .base import Serializer, SerializerView
from .decorators import computed_field, field_validator, model_validator
from .fields import FieldConfig, field
from .helpers import create_serializer, create_serializer_set
from .nested import Nested

# Re-export common types for convenience
from .types import (
    IP,
    URL,
    UUID,
    BigInt,
    # String lengths
    Char50,
    Char100,
    Char150,
    Char200,
    Char255,
    Char500,
    Char1000,
    CountryCode,
    CurrencyCode,
    # Validated strings
    Email,
    # File path
    FilePath,
    # Floats
    Float,
    HexColor,
    HttpStatus,
    HttpsURL,
    Int,
    # Network
    IPv4,
    IPv6,
    LanguageCode,
    # Geographic
    Latitude,
    Longitude,
    # Simple constraints
    NonEmptyStr,
    NonNegativeInt,
    Password,
    # Rating/Percentage
    Percentage,
    # Utility
    Phone,
    Port,
    PositiveBigInt,
    PositiveFloat,
    PositiveInt,
    PositiveSmallInt,
    Rating,
    Rating10,
    Slug,
    Slug100,
    Slug200,
    # Integers
    SmallInt,
    Text,
    Timezone,
    # Auth
    Username,
)

__all__ = [
    "IP",
    "URL",
    "UUID",
    "BigInt",
    # String lengths
    "Char50",
    "Char100",
    "Char150",
    "Char200",
    "Char255",
    "Char500",
    "Char1000",
    "CountryCode",
    "CurrencyCode",
    # Validated strings
    "Email",
    "FieldConfig",
    # File path
    "FilePath",
    # Floats
    "Float",
    "HexColor",
    "HttpStatus",
    "HttpsURL",
    # Network
    "IPv4",
    "IPv6",
    "Int",
    "LanguageCode",
    # Geographic
    "Latitude",
    "Longitude",
    # msgspec Meta for type constraints (use class Config for serializer configuration)
    "Meta",
    "Nested",
    # Simple constraints
    "NonEmptyStr",
    "NonNegativeInt",
    "Password",
    # Rating/Percentage
    "Percentage",
    # Utility
    "Phone",
    "Port",
    "PositiveBigInt",
    "PositiveFloat",
    "PositiveInt",
    "PositiveSmallInt",
    "Rating",
    "Rating10",
    # Core classes
    "Serializer",
    "SerializerView",
    "Slug",
    "Slug100",
    "Slug200",
    # Integers
    "SmallInt",
    "Text",
    "Timezone",
    # Auth
    "Username",
    "computed_field",
    # Helpers
    "create_serializer",
    "create_serializer_set",
    # Field configuration
    "field",
    # Decorators
    "field_validator",
    "model_validator",
]

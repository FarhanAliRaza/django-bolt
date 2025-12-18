"""Enhanced Serializer system for django-bolt with validation and Django model integration."""

from __future__ import annotations

from msgspec import Meta

from .base import Serializer, SerializerView
from .decorators import computed_field, field_validator, model_validator
from .errors import FieldError, ValidationError

# Field mapping utilities
from .field_mapping import (
    REQUIRED,
    get_field_default,
    get_field_kwargs,
    get_field_type,
    is_field_read_only,
    is_field_required,
    needs_unique_validator,
)
from .fields import FieldConfig, field
from .helpers import create_serializer, create_serializer_set

# Model introspection utilities
from .model_meta import (
    FieldInfo,
    RelationInfo,
    get_all_field_names,
    get_field_info,
    get_unique_field_names,
    get_unique_together_constraints,
    is_abstract_model,
)
from .model_serializer import ModelSerializer
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
from .validators import (
    ChoicesValidator,
    EmailValidator,
    ExistsValidator,
    LengthValidator,
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    PhoneValidator,
    RangeValidator,
    RegexValidator,
    SlugValidator,
    UniqueForDateValidator,
    UniqueForMonthValidator,
    UniqueForYearValidator,
    UniqueTogetherValidator,
    UniqueValidator,
    URLValidator,
    UUIDValidator,
    Validator,
    validator,
)

__all__ = [
    # Core classes
    "Serializer",
    "ModelSerializer",
    "SerializerView",
    # Field configuration
    "field",
    "FieldConfig",
    # msgspec Meta for type constraints (use class Config for serializer configuration)
    "Meta",
    # Decorators
    "field_validator",
    "model_validator",
    "computed_field",
    # Helpers
    "create_serializer",
    "create_serializer_set",
    "Nested",
    # String lengths
    "Char50",
    "Char100",
    "Char150",
    "Char200",
    "Char255",
    "Char500",
    "Char1000",
    "Text",
    # Validated strings
    "Email",
    "URL",
    "HttpsURL",
    "Slug",
    "Slug100",
    "Slug200",
    "UUID",
    # Integers
    "SmallInt",
    "Int",
    "BigInt",
    "PositiveSmallInt",
    "PositiveInt",
    "PositiveBigInt",
    "NonNegativeInt",
    # Floats
    "Float",
    "PositiveFloat",
    # Network
    "IPv4",
    "IPv6",
    "IP",
    "Port",
    "HttpStatus",
    # File path
    "FilePath",
    # Auth
    "Username",
    "Password",
    # Utility
    "Phone",
    "HexColor",
    "CurrencyCode",
    "CountryCode",
    "LanguageCode",
    "Timezone",
    # Geographic
    "Latitude",
    "Longitude",
    # Rating/Percentage
    "Percentage",
    "Rating",
    "Rating10",
    # Simple constraints
    "NonEmptyStr",
    # Errors
    "ValidationError",
    "FieldError",
    # Validators
    "validator",
    "Validator",
    "MinLengthValidator",
    "MaxLengthValidator",
    "LengthValidator",
    "RegexValidator",
    "MinValueValidator",
    "MaxValueValidator",
    "RangeValidator",
    "ChoicesValidator",
    "UniqueValidator",
    "ExistsValidator",
    "UniqueTogetherValidator",
    "UniqueForDateValidator",
    "UniqueForMonthValidator",
    "UniqueForYearValidator",
    "EmailValidator",
    "URLValidator",
    "SlugValidator",
    "UUIDValidator",
    "PhoneValidator",
    # Model introspection
    "FieldInfo",
    "RelationInfo",
    "get_field_info",
    "is_abstract_model",
    "get_all_field_names",
    "get_unique_together_constraints",
    "get_unique_field_names",
    # Field mapping
    "REQUIRED",
    "get_field_type",
    "get_field_kwargs",
    "get_field_default",
    "is_field_read_only",
    "is_field_required",
    "needs_unique_validator",
]

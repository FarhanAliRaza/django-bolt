"""Reusable validated types for Serializer fields.

These types use msgspec's Annotated + Meta pattern for validation.
All validation happens during deserialization (parsing), not serialization.

Usage:
    from django_bolt.serializers import Serializer
    from django_bolt.serializers.types import Email, HttpUrl, PositiveInt

    class UserSerializer(Serializer):
        email: Email
        website: HttpUrl | None = None
        age: PositiveInt
"""

from __future__ import annotations

from typing import Annotated

from msgspec import Meta

# =============================================================================
# String Types with Pattern Validation
# =============================================================================

Email = Annotated[
    str,
    Meta(
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Email address",
        examples=["user@example.com"],
    ),
]
"""Email address with regex validation."""

EmailLower = Annotated[
    str,
    Meta(
        pattern=r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$",
        description="Lowercase email address",
        examples=["user@example.com"],
    ),
]
"""Lowercase-only email address."""

HttpUrl = Annotated[
    str,
    Meta(
        pattern=r"^https?://[^\s/$.?#].[^\s]*$",
        description="HTTP or HTTPS URL",
        examples=["https://example.com"],
    ),
]
"""HTTP or HTTPS URL."""

HttpsUrl = Annotated[
    str,
    Meta(
        pattern=r"^https://[^\s/$.?#].[^\s]*$",
        description="HTTPS URL only",
        examples=["https://example.com"],
    ),
]
"""HTTPS URL only (no HTTP)."""

PhoneNumber = Annotated[
    str,
    Meta(
        pattern=r"^\+?[1-9]\d{1,14}$",
        description="Phone number in E.164 format",
        examples=["+14155551234"],
    ),
]
"""Phone number in E.164 international format."""

UUIDString = Annotated[
    str,
    Meta(
        pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
        description="UUID string",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    ),
]
"""UUID string format (use uuid.UUID for actual UUID objects)."""

Slug = Annotated[
    str,
    Meta(
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="URL-safe slug",
        examples=["my-blog-post"],
    ),
]
"""URL-safe slug (lowercase alphanumeric with hyphens)."""

Username = Annotated[
    str,
    Meta(
        pattern=r"^[a-zA-Z0-9_-]{3,32}$",
        min_length=3,
        max_length=32,
        description="Username (3-32 chars, alphanumeric, underscore, hyphen)",
        examples=["john_doe", "user123"],
    ),
]
"""Username: 3-32 characters, alphanumeric with underscore/hyphen."""

IPv4Address = Annotated[
    str,
    Meta(
        pattern=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        description="IPv4 address",
        examples=["192.168.1.1"],
    ),
]
"""IPv4 address string."""

HexColor = Annotated[
    str,
    Meta(
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="Hex color code",
        examples=["#FF5733"],
    ),
]
"""Hex color code (#RRGGBB format)."""

# =============================================================================
# Constrained String Types
# =============================================================================

NonEmptyStr = Annotated[
    str,
    Meta(min_length=1, description="Non-empty string"),
]
"""String that must have at least 1 character."""

ShortStr = Annotated[
    str,
    Meta(max_length=50, description="Short string (max 50 chars)"),
]
"""String with maximum 50 characters."""

MediumStr = Annotated[
    str,
    Meta(max_length=255, description="Medium string (max 255 chars)"),
]
"""String with maximum 255 characters (common DB varchar)."""

LongStr = Annotated[
    str,
    Meta(max_length=1000, description="Long string (max 1000 chars)"),
]
"""String with maximum 1000 characters."""

TextStr = Annotated[
    str,
    Meta(max_length=10000, description="Text field (max 10000 chars)"),
]
"""Text field with maximum 10000 characters."""

# =============================================================================
# Constrained Integer Types
# =============================================================================

PositiveInt = Annotated[
    int,
    Meta(gt=0, description="Positive integer (> 0)"),
]
"""Integer greater than 0."""

NonNegativeInt = Annotated[
    int,
    Meta(ge=0, description="Non-negative integer (>= 0)"),
]
"""Integer greater than or equal to 0."""

NegativeInt = Annotated[
    int,
    Meta(lt=0, description="Negative integer (< 0)"),
]
"""Integer less than 0."""

SmallInt = Annotated[
    int,
    Meta(ge=-32768, le=32767, description="Small integer (-32768 to 32767)"),
]
"""Small integer matching SQL SMALLINT range."""

TinyInt = Annotated[
    int,
    Meta(ge=0, le=255, description="Tiny integer (0 to 255)"),
]
"""Tiny unsigned integer (0-255)."""

Port = Annotated[
    int,
    Meta(ge=1, le=65535, description="Network port number"),
]
"""Valid network port number (1-65535)."""

HttpStatusCode = Annotated[
    int,
    Meta(ge=100, le=599, description="HTTP status code"),
]
"""Valid HTTP status code (100-599)."""

# =============================================================================
# Constrained Float Types
# =============================================================================

PositiveFloat = Annotated[
    float,
    Meta(gt=0, description="Positive float (> 0)"),
]
"""Float greater than 0."""

NonNegativeFloat = Annotated[
    float,
    Meta(ge=0, description="Non-negative float (>= 0)"),
]
"""Float greater than or equal to 0."""

Percentage = Annotated[
    float,
    Meta(ge=0, le=100, description="Percentage (0-100)"),
]
"""Percentage value between 0 and 100."""

Probability = Annotated[
    float,
    Meta(ge=0, le=1, description="Probability (0-1)"),
]
"""Probability value between 0 and 1."""

Latitude = Annotated[
    float,
    Meta(ge=-90, le=90, description="Latitude (-90 to 90)"),
]
"""Geographic latitude (-90 to 90 degrees)."""

Longitude = Annotated[
    float,
    Meta(ge=-180, le=180, description="Longitude (-180 to 180)"),
]
"""Geographic longitude (-180 to 180 degrees)."""

# =============================================================================
# List Types
# =============================================================================

NonEmptyList = Annotated[
    list,
    Meta(min_length=1, description="Non-empty list"),
]
"""List that must have at least 1 item."""

SmallList = Annotated[
    list,
    Meta(max_length=10, description="Small list (max 10 items)"),
]
"""List with maximum 10 items."""

MediumList = Annotated[
    list,
    Meta(max_length=100, description="Medium list (max 100 items)"),
]
"""List with maximum 100 items."""

# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # String patterns
    "Email",
    "EmailLower",
    "HttpUrl",
    "HttpsUrl",
    "PhoneNumber",
    "UUIDString",
    "Slug",
    "Username",
    "IPv4Address",
    "HexColor",
    # Constrained strings
    "NonEmptyStr",
    "ShortStr",
    "MediumStr",
    "LongStr",
    "TextStr",
    # Constrained integers
    "PositiveInt",
    "NonNegativeInt",
    "NegativeInt",
    "SmallInt",
    "TinyInt",
    "Port",
    "HttpStatusCode",
    # Constrained floats
    "PositiveFloat",
    "NonNegativeFloat",
    "Percentage",
    "Probability",
    "Latitude",
    "Longitude",
    # List types
    "NonEmptyList",
    "SmallList",
    "MediumList",
]

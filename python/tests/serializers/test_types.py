"""Tests for serializer types (Email, URL, etc.).

NOTE: msgspec Meta constraints (pattern, ge, le, min_length, etc.) only validate
during JSON decoding, not during direct Python instantiation. This is by design.

For validation, use:
- model_validate_json() - for JSON strings/bytes
- model_validate() - for dicts (uses msgspec.convert internally)

Direct instantiation (MySerializer(field=value)) bypasses constraints.
"""

from __future__ import annotations

import json

import pytest

from django_bolt.exceptions import RequestValidationError
from django_bolt.serializers import (
    URL,
    Email,
    HttpsURL,
    NonEmptyStr,
    NonNegativeInt,
    Percentage,
    Phone,
    PositiveInt,
    Serializer,
    Slug,
    Username,
)
from django_bolt.serializers.types import (
    UUID,
    HexColor,
    Latitude,
    Longitude,
    Port,
)


def to_json(data: dict) -> bytes:
    """Helper to convert dict to JSON bytes."""
    return json.dumps(data).encode()


class TestEmailType:
    """Test Email type validation."""

    def test_valid_email(self):
        """Test valid email addresses pass validation."""

        class UserSerializer(Serializer):
            email: Email

        user = UserSerializer.model_validate_json(to_json({"email": "test@example.com"}))
        assert user.email == "test@example.com"

        user2 = UserSerializer.model_validate_json(to_json({"email": "user.name+tag@domain.co.uk"}))
        assert user2.email == "user.name+tag@domain.co.uk"

    def test_invalid_email(self):
        """Test invalid email addresses fail validation during JSON parsing."""

        class UserSerializer(Serializer):
            email: Email

        with pytest.raises(RequestValidationError):
            UserSerializer.model_validate_json(to_json({"email": "not-an-email"}))

        with pytest.raises(RequestValidationError):
            UserSerializer.model_validate_json(to_json({"email": "missing@domain"}))


class TestURLType:
    """Test URL type validation."""

    def test_valid_http_url(self):
        """Test valid HTTP/HTTPS URLs pass validation."""

        class LinkSerializer(Serializer):
            url: URL

        link = LinkSerializer.model_validate_json(to_json({"url": "https://example.com"}))
        assert link.url == "https://example.com"

        link2 = LinkSerializer.model_validate_json(to_json({"url": "http://example.com/path?query=1"}))
        assert link2.url == "http://example.com/path?query=1"

    def test_invalid_url(self):
        """Test invalid URLs fail validation."""

        class LinkSerializer(Serializer):
            url: URL

        with pytest.raises(RequestValidationError):
            LinkSerializer.model_validate_json(to_json({"url": "not-a-url"}))

        with pytest.raises(RequestValidationError):
            LinkSerializer.model_validate_json(to_json({"url": "ftp://example.com"}))


class TestHttpsURLType:
    """Test HttpsURL type validation (HTTPS only)."""

    def test_valid_https_url(self):
        """Test valid HTTPS URLs pass validation."""

        class SecureLinkSerializer(Serializer):
            url: HttpsURL

        link = SecureLinkSerializer.model_validate_json(to_json({"url": "https://example.com"}))
        assert link.url == "https://example.com"

    def test_http_rejected(self):
        """Test HTTP URLs are rejected."""

        class SecureLinkSerializer(Serializer):
            url: HttpsURL

        with pytest.raises(RequestValidationError):
            SecureLinkSerializer.model_validate_json(to_json({"url": "http://example.com"}))


class TestPhoneType:
    """Test Phone type validation."""

    def test_valid_phone_number(self):
        """Test valid phone numbers pass validation."""

        class ContactSerializer(Serializer):
            phone: Phone

        contact = ContactSerializer.model_validate_json(to_json({"phone": "+14155551234"}))
        assert contact.phone == "+14155551234"

        contact2 = ContactSerializer.model_validate_json(to_json({"phone": "14155551234"}))
        assert contact2.phone == "14155551234"

    def test_invalid_phone_number(self):
        """Test invalid phone numbers fail validation."""

        class ContactSerializer(Serializer):
            phone: Phone

        with pytest.raises(RequestValidationError):
            ContactSerializer.model_validate_json(to_json({"phone": "555-1234"}))

        with pytest.raises(RequestValidationError):
            ContactSerializer.model_validate_json(to_json({"phone": "abc123"}))


class TestSlugType:
    """Test Slug type validation."""

    def test_valid_slug(self):
        """Test valid slugs pass validation."""

        class PostSerializer(Serializer):
            slug: Slug

        post = PostSerializer.model_validate_json(to_json({"slug": "my-blog-post"}))
        assert post.slug == "my-blog-post"

        post2 = PostSerializer.model_validate_json(to_json({"slug": "post123"}))
        assert post2.slug == "post123"

        # Underscores are also valid in slugs
        post3 = PostSerializer.model_validate_json(to_json({"slug": "post_123"}))
        assert post3.slug == "post_123"

    def test_invalid_slug(self):
        """Test invalid slugs fail validation."""

        class PostSerializer(Serializer):
            slug: Slug

        with pytest.raises(RequestValidationError):
            PostSerializer.model_validate_json(to_json({"slug": "My Blog Post"}))

        with pytest.raises(RequestValidationError):
            PostSerializer.model_validate_json(to_json({"slug": "post@123"}))


class TestUsernameType:
    """Test Username type validation."""

    def test_valid_username(self):
        """Test valid usernames pass validation."""

        class UserSerializer(Serializer):
            username: Username

        user = UserSerializer.model_validate_json(to_json({"username": "john_doe"}))
        assert user.username == "john_doe"

        user2 = UserSerializer.model_validate_json(to_json({"username": "user-123"}))
        assert user2.username == "user-123"

        # @ is valid in Django usernames
        user3 = UserSerializer.model_validate_json(to_json({"username": "user@example"}))
        assert user3.username == "user@example"

    def test_invalid_username(self):
        """Test invalid usernames fail validation."""

        class UserSerializer(Serializer):
            username: Username

        # Space is not valid
        with pytest.raises(RequestValidationError):
            UserSerializer.model_validate_json(to_json({"username": "user name"}))


class TestNonEmptyStrType:
    """Test NonEmptyStr type validation."""

    def test_valid_non_empty_str(self):
        """Test non-empty strings pass validation."""

        class NameSerializer(Serializer):
            name: NonEmptyStr

        s = NameSerializer.model_validate_json(to_json({"name": "Hello"}))
        assert s.name == "Hello"

        s2 = NameSerializer.model_validate_json(to_json({"name": "a"}))
        assert s2.name == "a"

    def test_empty_str_rejected(self):
        """Test empty strings are rejected."""

        class NameSerializer(Serializer):
            name: NonEmptyStr

        with pytest.raises(RequestValidationError):
            NameSerializer.model_validate_json(to_json({"name": ""}))


class TestPositiveIntType:
    """Test PositiveInt type validation."""

    def test_valid_positive_int(self):
        """Test positive integers pass validation."""

        class CountSerializer(Serializer):
            count: PositiveInt

        s = CountSerializer.model_validate_json(to_json({"count": 1}))
        assert s.count == 1

        s2 = CountSerializer.model_validate_json(to_json({"count": 100}))
        assert s2.count == 100

    def test_zero_rejected(self):
        """Test zero is rejected (must be > 0)."""

        class CountSerializer(Serializer):
            count: PositiveInt

        with pytest.raises(RequestValidationError):
            CountSerializer.model_validate_json(to_json({"count": 0}))

    def test_negative_rejected(self):
        """Test negative numbers are rejected."""

        class CountSerializer(Serializer):
            count: PositiveInt

        with pytest.raises(RequestValidationError):
            CountSerializer.model_validate_json(to_json({"count": -1}))


class TestNonNegativeIntType:
    """Test NonNegativeInt type validation."""

    def test_valid_non_negative_int(self):
        """Test non-negative integers pass validation."""

        class IndexSerializer(Serializer):
            index: NonNegativeInt

        s = IndexSerializer.model_validate_json(to_json({"index": 0}))
        assert s.index == 0

        s2 = IndexSerializer.model_validate_json(to_json({"index": 100}))
        assert s2.index == 100

    def test_negative_rejected(self):
        """Test negative numbers are rejected."""

        class IndexSerializer(Serializer):
            index: NonNegativeInt

        with pytest.raises(RequestValidationError):
            IndexSerializer.model_validate_json(to_json({"index": -1}))


class TestPercentageType:
    """Test Percentage type validation."""

    def test_valid_percentage(self):
        """Test valid percentages pass validation."""

        class ProgressSerializer(Serializer):
            progress: Percentage

        s = ProgressSerializer.model_validate_json(to_json({"progress": 0.0}))
        assert s.progress == 0.0

        s2 = ProgressSerializer.model_validate_json(to_json({"progress": 50.5}))
        assert s2.progress == 50.5

        s3 = ProgressSerializer.model_validate_json(to_json({"progress": 100.0}))
        assert s3.progress == 100.0

    def test_out_of_range_rejected(self):
        """Test values outside 0-100 are rejected."""

        class ProgressSerializer(Serializer):
            progress: Percentage

        with pytest.raises(RequestValidationError):
            ProgressSerializer.model_validate_json(to_json({"progress": -1.0}))

        with pytest.raises(RequestValidationError):
            ProgressSerializer.model_validate_json(to_json({"progress": 100.1}))


class TestGeoTypes:
    """Test geographic coordinate types."""

    def test_valid_latitude(self):
        """Test valid latitudes pass validation."""

        class LocationSerializer(Serializer):
            lat: Latitude

        loc = LocationSerializer.model_validate_json(to_json({"lat": 37.7749}))
        assert loc.lat == 37.7749

        loc2 = LocationSerializer.model_validate_json(to_json({"lat": -90.0}))
        assert loc2.lat == -90.0

    def test_invalid_latitude(self):
        """Test invalid latitudes fail validation."""

        class LocationSerializer(Serializer):
            lat: Latitude

        with pytest.raises(RequestValidationError):
            LocationSerializer.model_validate_json(to_json({"lat": 91.0}))

    def test_valid_longitude(self):
        """Test valid longitudes pass validation."""

        class LocationSerializer(Serializer):
            lng: Longitude

        loc = LocationSerializer.model_validate_json(to_json({"lng": -122.4194}))
        assert loc.lng == -122.4194

    def test_invalid_longitude(self):
        """Test invalid longitudes fail validation."""

        class LocationSerializer(Serializer):
            lng: Longitude

        with pytest.raises(RequestValidationError):
            LocationSerializer.model_validate_json(to_json({"lng": 181.0}))


class TestPortType:
    """Test Port type validation."""

    def test_valid_port(self):
        """Test valid port numbers pass validation."""

        class ServerSerializer(Serializer):
            port: Port

        s = ServerSerializer.model_validate_json(to_json({"port": 80}))
        assert s.port == 80

        s2 = ServerSerializer.model_validate_json(to_json({"port": 8080}))
        assert s2.port == 8080

        s3 = ServerSerializer.model_validate_json(to_json({"port": 65535}))
        assert s3.port == 65535

    def test_invalid_port(self):
        """Test invalid port numbers fail validation."""

        class ServerSerializer(Serializer):
            port: Port

        with pytest.raises(RequestValidationError):
            ServerSerializer.model_validate_json(to_json({"port": 0}))

        with pytest.raises(RequestValidationError):
            ServerSerializer.model_validate_json(to_json({"port": 65536}))


class TestHexColorType:
    """Test HexColor type validation."""

    def test_valid_hex_color(self):
        """Test valid hex colors pass validation."""

        class ThemeSerializer(Serializer):
            color: HexColor

        t = ThemeSerializer.model_validate_json(to_json({"color": "#FF5733"}))
        assert t.color == "#FF5733"

        t2 = ThemeSerializer.model_validate_json(to_json({"color": "#000000"}))
        assert t2.color == "#000000"

    def test_invalid_hex_color(self):
        """Test invalid hex colors fail validation."""

        class ThemeSerializer(Serializer):
            color: HexColor

        with pytest.raises(RequestValidationError):
            ThemeSerializer.model_validate_json(to_json({"color": "FF5733"}))  # Missing #

        with pytest.raises(RequestValidationError):
            ThemeSerializer.model_validate_json(to_json({"color": "#FFF"}))  # Too short


class TestUUIDType:
    """Test UUID type validation."""

    def test_valid_uuid(self):
        """Test valid UUID strings pass validation."""

        class EntitySerializer(Serializer):
            id: UUID

        e = EntitySerializer.model_validate_json(to_json({"id": "550e8400-e29b-41d4-a716-446655440000"}))
        assert e.id == "550e8400-e29b-41d4-a716-446655440000"

    def test_invalid_uuid(self):
        """Test invalid UUID strings fail validation."""

        class EntitySerializer(Serializer):
            id: UUID

        with pytest.raises(RequestValidationError):
            EntitySerializer.model_validate_json(to_json({"id": "not-a-uuid"}))


class TestTypesWithSubset:
    """Test that custom types work with subset()."""

    def test_types_in_subset(self):
        """Test custom types are preserved in subset serializers."""

        class UserSerializer(Serializer):
            id: PositiveInt
            email: Email
            username: Username
            website: URL | None = None

        UserMini = UserSerializer.subset("id", "email")

        # Should validate correctly via JSON parsing
        user = UserMini.model_validate_json(to_json({"id": 1, "email": "test@example.com"}))
        assert user.id == 1
        assert user.email == "test@example.com"

        # Invalid values should still fail
        with pytest.raises(RequestValidationError):
            UserMini.model_validate_json(to_json({"id": -1, "email": "test@example.com"}))

        with pytest.raises(RequestValidationError):
            UserMini.model_validate_json(to_json({"id": 1, "email": "not-an-email"}))


class TestDirectInstantiationNote:
    """Document that direct instantiation bypasses validation."""

    def test_direct_instantiation_bypasses_validation(self):
        """Direct instantiation does NOT validate - this is by design in msgspec."""

        class UserSerializer(Serializer):
            email: Email
            count: PositiveInt

        # Direct instantiation bypasses constraint validation!
        # This is msgspec behavior - constraints are for parsing, not construction
        user = UserSerializer(email="invalid", count=-5)
        assert user.email == "invalid"
        assert user.count == -5

        # Use model_validate_json for validation
        with pytest.raises(RequestValidationError):
            UserSerializer.model_validate_json(to_json({"email": "invalid", "count": -5}))

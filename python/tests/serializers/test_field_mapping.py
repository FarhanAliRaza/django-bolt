"""Tests for field_mapping utilities."""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Annotated, Literal, get_args, get_origin
from uuid import UUID

import pytest
from django.db import models
from msgspec import Meta

from django_bolt.serializers.field_mapping import (
    REQUIRED,
    get_field_type,
    get_field_kwargs,
    get_field_default,
    is_field_read_only,
    is_field_required,
    needs_unique_validator,
)

# Import test models
from tests.test_models import Article, Author, BlogPost, Tag, User, UserProfile


class TestGetFieldType:
    """Tests for get_field_type function."""

    def test_char_field_returns_str(self):
        """Test that CharField returns str type."""
        field = Author._meta.get_field("name")
        field_type = get_field_type(field)

        # CharField with max_length should be Annotated[str, Meta(...)]
        assert get_origin(field_type) is Annotated
        assert get_args(field_type)[0] is str

    def test_text_field_returns_str(self):
        """Test that TextField returns str type."""
        field = Author._meta.get_field("bio")
        field_type = get_field_type(field)

        # TextField without max_length should be str | None (since blank=True)
        # or just str if not nullable
        assert str in (field_type, *getattr(get_args(field_type), "__iter__", lambda: [])())

    def test_email_field_returns_str(self):
        """Test that EmailField returns str type."""
        field = Author._meta.get_field("email")
        field_type = get_field_type(field)

        # EmailField should have str as base type
        if get_origin(field_type) is Annotated:
            assert get_args(field_type)[0] is str
        else:
            assert field_type is str or str in get_args(field_type)

    def test_integer_field_returns_int(self):
        """Test that IntegerField returns int type."""
        # Create a mock integer field for testing
        field = models.IntegerField()
        field.set_attributes_from_name("test_int")
        field_type = get_field_type(field)

        # IntegerField may be Annotated[int, Meta(...)] with ge/le constraints
        if get_origin(field_type) is Annotated:
            assert get_args(field_type)[0] is int
        else:
            assert field_type is int

    def test_boolean_field_returns_bool(self):
        """Test that BooleanField returns bool type."""
        field = Article._meta.get_field("is_published")
        field_type = get_field_type(field)

        assert field_type is bool

    def test_datetime_field_returns_datetime(self):
        """Test that DateTimeField returns datetime type."""
        field = Article._meta.get_field("created_at")
        field_type = get_field_type(field)

        assert field_type is datetime

    def test_date_field_returns_date(self):
        """Test that DateField returns date type."""
        field = UserProfile._meta.get_field("date_of_birth")
        field_type = get_field_type(field)

        # date_of_birth is nullable
        assert date in get_args(field_type) or field_type is date

    def test_nullable_field_includes_none(self):
        """Test that nullable fields include None in union."""
        field = UserProfile._meta.get_field("date_of_birth")  # null=True
        field_type = get_field_type(field)

        # Should be date | None
        args = get_args(field_type)
        assert type(None) in args

    def test_choices_field_returns_literal(self):
        """Test that fields with choices return Literal type."""
        field = Article._meta.get_field("status")
        field_type = get_field_type(field)

        # Should be Literal["draft", "published"]
        origin = get_origin(field_type)
        assert origin is Literal

        # Check the choice values are present
        args = get_args(field_type)
        assert "draft" in args
        assert "published" in args

    def test_foreign_key_returns_int(self):
        """Test that ForeignKey returns int (PK type) at depth 0."""
        field = BlogPost._meta.get_field("author")
        field_type = get_field_type(field, depth=0)

        assert field_type is int

    def test_nullable_foreign_key_returns_int_or_none(self):
        """Test that nullable ForeignKey returns int | None."""
        # Create a mock nullable FK
        field = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
        field.set_attributes_from_name("test_fk")
        field_type = get_field_type(field, depth=0)

        args = get_args(field_type)
        assert int in args
        assert type(None) in args

    def test_many_to_many_returns_list_int(self):
        """Test that ManyToManyField returns list[int] at depth 0."""
        field = BlogPost._meta.get_field("tags")
        field_type = get_field_type(field, depth=0)

        assert get_origin(field_type) is list
        assert get_args(field_type) == (int,)

    def test_decimal_field_returns_decimal(self):
        """Test that DecimalField returns Decimal type."""
        field = models.DecimalField(max_digits=10, decimal_places=2)
        field.set_attributes_from_name("price")
        field_type = get_field_type(field)

        assert field_type is Decimal

    def test_uuid_field_returns_uuid(self):
        """Test that UUIDField returns UUID type."""
        field = models.UUIDField()
        field.set_attributes_from_name("uuid")
        field_type = get_field_type(field)

        assert field_type is UUID

    def test_auto_field_returns_int(self):
        """Test that AutoField returns int type."""
        field = Article._meta.get_field("id")
        field_type = get_field_type(field)

        # AutoField may be Annotated[int, Meta(...)] with constraints
        if get_origin(field_type) is Annotated:
            assert get_args(field_type)[0] is int
        else:
            assert field_type is int

    def test_binary_field_returns_bytes(self):
        """Test that BinaryField returns bytes type."""
        field = models.BinaryField()
        field.set_attributes_from_name("data")
        field_type = get_field_type(field)

        assert field_type is bytes

    def test_duration_field_returns_timedelta(self):
        """Test that DurationField returns timedelta type."""
        field = models.DurationField()
        field.set_attributes_from_name("duration")
        field_type = get_field_type(field)

        assert field_type is timedelta

    def test_time_field_returns_time(self):
        """Test that TimeField returns time type."""
        field = models.TimeField()
        field.set_attributes_from_name("start_time")
        field_type = get_field_type(field)

        assert field_type is time

    def test_max_length_constraint_applied(self):
        """Test that max_length is applied as Meta constraint."""
        field = Author._meta.get_field("name")  # max_length=200
        field_type = get_field_type(field)

        # Should be Annotated[str, Meta(max_length=200)]
        assert get_origin(field_type) is Annotated
        args = get_args(field_type)
        meta = args[1]
        assert isinstance(meta, Meta)
        assert meta.max_length == 200


class TestGetFieldKwargs:
    """Tests for get_field_kwargs function."""

    def test_returns_dict(self):
        """Test that function returns a dict."""
        field = Author._meta.get_field("name")
        kwargs = get_field_kwargs("name", field)
        assert isinstance(kwargs, dict)

    def test_read_only_for_auto_field(self):
        """Test that AutoField is marked as read_only."""
        field = Article._meta.get_field("id")
        kwargs = get_field_kwargs("id", field)
        assert kwargs.get("read_only") is True

    def test_required_true_for_non_blank_field(self):
        """Test that non-blank, non-null, non-default fields are required."""
        field = Author._meta.get_field("name")
        kwargs = get_field_kwargs("name", field)
        assert kwargs.get("required") is True

    def test_required_false_for_blank_field(self):
        """Test that blank fields are not required."""
        field = Author._meta.get_field("bio")  # blank=True
        kwargs = get_field_kwargs("bio", field)
        assert kwargs.get("required") is False

    def test_allow_null_for_nullable_field(self):
        """Test that nullable fields have allow_null=True."""
        field = UserProfile._meta.get_field("date_of_birth")  # null=True
        kwargs = get_field_kwargs("date_of_birth", field)
        assert kwargs.get("allow_null") is True

    def test_allow_blank_for_blank_string_field(self):
        """Test that blank string fields have allow_blank=True."""
        field = Author._meta.get_field("bio")  # blank=True, TextField
        kwargs = get_field_kwargs("bio", field)
        assert kwargs.get("allow_blank") is True

    def test_unique_detected(self):
        """Test that unique constraint is detected."""
        field = User._meta.get_field("username")  # unique=True
        kwargs = get_field_kwargs("username", field)
        assert kwargs.get("unique") is True

    def test_choices_included(self):
        """Test that choices are included in kwargs."""
        field = Article._meta.get_field("status")
        kwargs = get_field_kwargs("status", field)
        assert "choices" in kwargs
        assert len(kwargs["choices"]) == 2

    def test_decimal_kwargs(self):
        """Test that DecimalField includes max_digits and decimal_places."""
        field = models.DecimalField(max_digits=10, decimal_places=2)
        field.set_attributes_from_name("price")
        kwargs = get_field_kwargs("price", field)

        assert kwargs.get("max_digits") == 10
        assert kwargs.get("decimal_places") == 2


class TestGetFieldDefault:
    """Tests for get_field_default function."""

    def test_auto_field_defaults_to_none(self):
        """Test that AutoField defaults to None."""
        field = Article._meta.get_field("id")
        default = get_field_default(field)
        assert default is None

    def test_nullable_field_defaults_to_none(self):
        """Test that nullable field defaults to None."""
        field = UserProfile._meta.get_field("date_of_birth")
        default = get_field_default(field)
        assert default is None

    def test_blank_string_field_defaults_to_empty_string(self):
        """Test that blank string field defaults to empty string."""
        field = Author._meta.get_field("bio")
        default = get_field_default(field)
        assert default == ""

    def test_required_field_returns_sentinel(self):
        """Test that required field returns REQUIRED sentinel."""
        field = Author._meta.get_field("name")
        default = get_field_default(field)
        assert default is REQUIRED

    def test_field_with_explicit_default(self):
        """Test that field with explicit default returns that default."""
        field = Article._meta.get_field("is_published")  # default=False
        default = get_field_default(field)
        assert default is False

    def test_field_with_choices_and_default(self):
        """Test that field with choices and default returns default."""
        field = Article._meta.get_field("status")  # default="draft"
        default = get_field_default(field)
        assert default == "draft"


class TestIsFieldReadOnly:
    """Tests for is_field_read_only function."""

    def test_auto_field_is_read_only(self):
        """Test that AutoField is read-only."""
        field = Article._meta.get_field("id")
        assert is_field_read_only(field) is True

    def test_editable_false_is_read_only(self):
        """Test that editable=False fields are read-only."""
        field = Article._meta.get_field("created_at")  # auto_now_add makes it editable=False
        assert is_field_read_only(field) is True

    def test_normal_field_is_not_read_only(self):
        """Test that normal editable fields are not read-only."""
        field = Author._meta.get_field("name")
        assert is_field_read_only(field) is False


class TestIsFieldRequired:
    """Tests for is_field_required function."""

    def test_auto_field_not_required(self):
        """Test that AutoField is not required."""
        field = Article._meta.get_field("id")
        assert is_field_required(field) is False

    def test_nullable_field_not_required(self):
        """Test that nullable field is not required."""
        field = UserProfile._meta.get_field("date_of_birth")
        assert is_field_required(field) is False

    def test_blank_field_not_required(self):
        """Test that blank field is not required."""
        field = Author._meta.get_field("bio")
        assert is_field_required(field) is False

    def test_field_with_default_not_required(self):
        """Test that field with default is not required."""
        field = Article._meta.get_field("is_published")
        assert is_field_required(field) is False

    def test_mandatory_field_is_required(self):
        """Test that mandatory field is required."""
        field = Author._meta.get_field("name")
        assert is_field_required(field) is True


class TestNeedsUniqueValidator:
    """Tests for needs_unique_validator function."""

    def test_unique_field_needs_validator(self):
        """Test that unique field needs validator."""
        field = User._meta.get_field("username")
        assert needs_unique_validator(field) is True

    def test_primary_key_does_not_need_validator(self):
        """Test that primary key doesn't need unique validator."""
        field = Article._meta.get_field("id")
        assert needs_unique_validator(field) is False

    def test_non_unique_field_does_not_need_validator(self):
        """Test that non-unique field doesn't need validator."""
        field = Author._meta.get_field("name")
        assert needs_unique_validator(field) is False

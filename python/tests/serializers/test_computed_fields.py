"""Tests for computed fields in Serializers."""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User as DjangoUser

from django_bolt.serializers import Serializer, computed_field, field_validator


class TestComputedFieldsBasic:
    """Test basic computed field functionality."""

    def test_computed_field_basic(self):
        """Test a simple computed field."""

        class UserSerializer(Serializer):
            first_name: str
            last_name: str

            @computed_field
            def full_name(self) -> str:
                return f"{self.first_name} {self.last_name}"

        user = UserSerializer(first_name="John", last_name="Doe")
        data = user.to_dict()

        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["full_name"] == "John Doe"

    def test_computed_field_with_parentheses(self):
        """Test computed field decorator with parentheses."""

        class UserSerializer(Serializer):
            first_name: str
            last_name: str

            @computed_field()
            def full_name(self) -> str:
                return f"{self.first_name} {self.last_name}"

        user = UserSerializer(first_name="Jane", last_name="Smith")
        data = user.to_dict()

        assert data["full_name"] == "Jane Smith"

    def test_multiple_computed_fields(self):
        """Test multiple computed fields in one serializer."""

        class PersonSerializer(Serializer):
            first_name: str
            last_name: str
            age: int

            @computed_field
            def full_name(self) -> str:
                return f"{self.first_name} {self.last_name}"

            @computed_field
            def is_adult(self) -> bool:
                return self.age >= 18

            @computed_field
            def display_name(self) -> str:
                return f"{self.full_name()} ({self.age})"

        person = PersonSerializer(first_name="Alice", last_name="Johnson", age=25)
        data = person.to_dict()

        assert data["full_name"] == "Alice Johnson"
        assert data["is_adult"] is True
        assert data["display_name"] == "Alice Johnson (25)"

    def test_computed_field_not_in_input(self):
        """Test that computed fields cannot be passed as input."""

        class UserSerializer(Serializer):
            first_name: str
            last_name: str

            @computed_field
            def full_name(self) -> str:
                return f"{self.first_name} {self.last_name}"

        # Computed fields are not struct fields, so passing them should be ignored/error
        # msgspec will raise an error for unknown fields if strict mode is on
        # For now, let's just verify it's not in struct fields
        assert "full_name" not in UserSerializer.__struct_fields__


class TestComputedFieldsWithDjango:
    """Test computed fields with Django model integration."""

    @pytest.mark.django_db
    def test_computed_field_from_model(self):
        """Test computed fields when creating from Django model."""

        class UserSerializer(Serializer):
            id: int
            username: str
            first_name: str
            last_name: str

            @computed_field
            def full_name(self) -> str:
                return f"{self.first_name} {self.last_name}".strip()

            @computed_field
            def display_name(self) -> str:
                if self.first_name or self.last_name:
                    return self.full_name()
                return self.username

        # Create a Django user
        user = DjangoUser.objects.create_user(
            username="jdoe",
            email="jdoe@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )

        # Convert to serializer
        serializer = UserSerializer.from_model(user)
        data = serializer.to_dict()

        assert data["username"] == "jdoe"
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["full_name"] == "John Doe"
        assert data["display_name"] == "John Doe"

    @pytest.mark.django_db
    def test_computed_field_with_no_name(self):
        """Test computed field when user has no first/last name."""

        class UserSerializer(Serializer):
            username: str
            first_name: str
            last_name: str

            @computed_field
            def display_name(self) -> str:
                if self.first_name or self.last_name:
                    return f"{self.first_name} {self.last_name}".strip()
                return self.username

        user = DjangoUser.objects.create_user(
            username="anonymous",
            email="anon@example.com",
            password="testpass123",
            first_name="",
            last_name="",
        )

        serializer = UserSerializer.from_model(user)
        data = serializer.to_dict()

        assert data["display_name"] == "anonymous"


class TestComputedFieldsWithValidators:
    """Test computed fields interaction with validators."""

    def test_computed_field_with_field_validator(self):
        """Test computed field using a validated field."""

        class UserSerializer(Serializer):
            email: str
            username: str

            @field_validator("email")
            def normalize_email(cls, value):
                return value.lower().strip()

            @computed_field
            def email_domain(self) -> str:
                return self.email.split("@")[1] if "@" in self.email else ""

        user = UserSerializer(email="  JOHN@EXAMPLE.COM  ", username="john")
        data = user.to_dict()

        assert data["email"] == "john@example.com"
        assert data["email_domain"] == "example.com"

    def test_computed_field_accessing_multiple_fields(self):
        """Test computed field that accesses multiple validated fields."""

        class ProductSerializer(Serializer):
            name: str
            price: float
            quantity: int

            @field_validator("name")
            def uppercase_name(cls, value):
                return value.upper()

            @computed_field
            def total_value(self) -> float:
                return self.price * self.quantity

            @computed_field
            def display(self) -> str:
                total = self.price * self.quantity
                return f"{self.name}: ${total:.2f}"

        product = ProductSerializer(name="widget", price=10.50, quantity=5)
        data = product.to_dict()

        assert data["name"] == "WIDGET"
        assert data["total_value"] == 52.5
        assert data["display"] == "WIDGET: $52.50"


class TestComputedFieldsInheritance:
    """Test computed fields with serializer inheritance."""

    def test_computed_field_inheritance(self):
        """Test that computed fields are inherited."""

        class BaseUserSerializer(Serializer):
            first_name: str
            last_name: str

            @computed_field
            def full_name(self) -> str:
                return f"{self.first_name} {self.last_name}"

        class ExtendedUserSerializer(BaseUserSerializer):
            email: str

            @computed_field
            def email_with_name(self) -> str:
                return f"{self.full_name()} <{self.email}>"

        user = ExtendedUserSerializer(
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
        )
        data = user.to_dict()

        # Both computed fields should be present
        assert data["full_name"] == "Jane Doe"
        assert data["email_with_name"] == "Jane Doe <jane@example.com>"


class TestComputedFieldsPerformance:
    """Test computed fields performance characteristics."""

    def test_no_computed_fields_zero_overhead(self):
        """Test that serializers without computed fields have no overhead."""

        class SimpleSerializer(Serializer):
            name: str
            value: int

        # This serializer has no computed fields
        assert SimpleSerializer.__has_computed_fields__ is False

        # Creating and converting should work normally
        data = SimpleSerializer(name="test", value=42)
        result = data.to_dict()

        assert result == {"name": "test", "value": 42}
        assert len(result) == 2  # Only struct fields

    def test_computed_fields_only_run_on_to_dict(self):
        """Test that computed fields are only evaluated when to_dict() is called."""

        call_count = {"count": 0}

        class CountingSerializer(Serializer):
            value: int

            @computed_field
            def computed_value(self) -> int:
                call_count["count"] += 1
                return self.value * 2

        # Create instance - computed field should NOT run yet
        instance = CountingSerializer(value=10)
        assert call_count["count"] == 0

        # Call to_dict() - computed field should run once
        data = instance.to_dict()
        assert call_count["count"] == 1
        assert data["computed_value"] == 20

        # Call to_dict() again - computed field runs again (not cached)
        data2 = instance.to_dict()
        assert call_count["count"] == 2


class TestComputedFieldsEdgeCases:
    """Test edge cases and error handling."""

    def test_computed_field_with_exception(self):
        """Test computed field that raises an exception."""

        class BuggySerializer(Serializer):
            value: int

            @computed_field
            def buggy_field(self) -> int:
                raise ValueError("Intentional error")

        instance = BuggySerializer(value=10)

        # to_dict should not crash, but log the error and skip the field
        data = instance.to_dict()

        # The computed field should not be in the output if it failed
        assert "buggy_field" not in data
        assert data["value"] == 10

    def test_computed_field_returns_none(self):
        """Test computed field that returns None."""

        class NullableSerializer(Serializer):
            name: str

            @computed_field
            def nullable_field(self) -> str | None:
                return None

        instance = NullableSerializer(name="test")
        data = instance.to_dict()

        assert data["nullable_field"] is None

    def test_computed_field_with_complex_types(self):
        """Test computed field returning complex types."""

        class ComplexSerializer(Serializer):
            items: list[int]

            @computed_field
            def item_stats(self) -> dict:
                return {
                    "count": len(self.items),
                    "sum": sum(self.items),
                    "avg": sum(self.items) / len(self.items) if self.items else 0,
                }

        instance = ComplexSerializer(items=[1, 2, 3, 4, 5])
        data = instance.to_dict()

        assert data["item_stats"]["count"] == 5
        assert data["item_stats"]["sum"] == 15
        assert data["item_stats"]["avg"] == 3.0

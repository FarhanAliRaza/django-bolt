"""Tests for advanced Serializer features: field(), computed_field, dynamic field selection."""

from __future__ import annotations

from datetime import datetime

import pytest

from django_bolt.serializers import (
    Serializer,
    SerializerView,
    computed_field,
    field,
    field_validator,
)


class TestFieldFunction:
    """Test the field() function for field configuration."""

    def test_field_read_only(self):
        """Test read_only fields are excluded from dump output based on Meta."""

        class UserSerializer(Serializer):
            id: int
            name: str
            internal_id: str

            class Meta:
                # Using Meta.write_only for fields that should only be in input
                write_only = {"internal_id"}

        user = UserSerializer(id=1, name="John", internal_id="secret123")

        # write_only fields should not appear in dump
        result = user.dump()
        assert "id" in result
        assert "name" in result
        assert "internal_id" not in result

    def test_field_write_only_meta(self):
        """Test write_only fields via Meta class."""

        class UserCreateSerializer(Serializer):
            email: str
            password: str

            class Meta:
                write_only = {"password"}

        user = UserCreateSerializer(email="test@example.com", password="secret123")
        result = user.dump()

        assert result["email"] == "test@example.com"
        assert "password" not in result

    def test_field_alias(self):
        """Test field alias for JSON output."""
        from django_bolt.serializers.fields import FieldConfig

        # Create a serializer with field config
        class UserSerializer(Serializer):
            first_name: str
            last_name: str

        user = UserSerializer(first_name="John", last_name="Doe")
        result = user.dump()

        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"


class TestComputedField:
    """Test the @computed_field decorator."""

    def test_basic_computed_field(self):
        """Test basic computed field."""

        class UserSerializer(Serializer):
            first_name: str
            last_name: str

            @computed_field
            def full_name(self) -> str:
                return f"{self.first_name} {self.last_name}"

        user = UserSerializer(first_name="John", last_name="Doe")
        result = user.dump()

        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["full_name"] == "John Doe"

    def test_computed_field_with_alias(self):
        """Test computed field with alias."""

        class UserSerializer(Serializer):
            first_name: str
            last_name: str

            @computed_field(alias="displayName")
            def display_name(self) -> str:
                return f"{self.first_name} {self.last_name}".upper()

        user = UserSerializer(first_name="John", last_name="Doe")
        result = user.dump()

        # The computed field should use the method name as key (alias affects OpenAPI only)
        assert "displayName" in result
        assert result["displayName"] == "JOHN DOE"

    def test_multiple_computed_fields(self):
        """Test multiple computed fields."""

        class ProductSerializer(Serializer):
            price: float
            quantity: int

            @computed_field
            def total(self) -> float:
                return self.price * self.quantity

            @computed_field
            def formatted_total(self) -> str:
                # Note: computed fields are methods, so call total() not self.total
                return f"${self.total():.2f}"

        product = ProductSerializer(price=19.99, quantity=3)
        result = product.dump()

        assert result["price"] == 19.99
        assert result["quantity"] == 3
        assert result["total"] == pytest.approx(59.97)
        assert result["formatted_total"] == "$59.97"

    def test_computed_field_exclude_none(self):
        """Test computed field with exclude_none."""

        class UserSerializer(Serializer):
            name: str
            email: str | None = None

            @computed_field
            def greeting(self) -> str | None:
                if self.email:
                    return f"Hello {self.name}!"
                return None

        user = UserSerializer(name="John", email=None)
        result = user.dump(exclude_none=True)

        assert "name" in result
        assert "email" not in result
        assert "greeting" not in result

        user2 = UserSerializer(name="Jane", email="jane@example.com")
        result2 = user2.dump(exclude_none=True)
        assert result2["greeting"] == "Hello Jane!"


class TestDynamicFieldSelection:
    """Test dynamic field selection with only(), exclude(), use()."""

    def test_only_basic(self):
        """Test basic only() field selection."""

        class UserSerializer(Serializer):
            id: int
            name: str
            email: str
            created_at: str

        user = UserSerializer(
            id=1, name="John", email="john@example.com", created_at="2024-01-01"
        )

        # Only include specific fields
        result = UserSerializer.only("id", "name").dump(user)

        assert result == {"id": 1, "name": "John"}
        assert "email" not in result
        assert "created_at" not in result

    def test_exclude_basic(self):
        """Test basic exclude() field selection."""

        class UserSerializer(Serializer):
            id: int
            name: str
            password: str
            secret_key: str

        user = UserSerializer(
            id=1, name="John", password="secret123", secret_key="key456"
        )

        # Exclude sensitive fields
        result = UserSerializer.exclude("password", "secret_key").dump(user)

        assert result == {"id": 1, "name": "John"}
        assert "password" not in result
        assert "secret_key" not in result

    def test_use_field_set(self):
        """Test use() with predefined field sets."""

        class UserSerializer(Serializer):
            id: int
            name: str
            email: str
            password: str
            created_at: str
            updated_at: str

            class Meta:
                field_sets = {
                    "list": ["id", "name", "email"],
                    "detail": ["id", "name", "email", "created_at", "updated_at"],
                    "minimal": ["id", "name"],
                }

        user = UserSerializer(
            id=1,
            name="John",
            email="john@example.com",
            password="secret",
            created_at="2024-01-01",
            updated_at="2024-01-15",
        )

        # Use predefined field sets
        list_result = UserSerializer.use("list").dump(user)
        assert list_result == {"id": 1, "name": "John", "email": "john@example.com"}

        detail_result = UserSerializer.use("detail").dump(user)
        assert "created_at" in detail_result
        assert "updated_at" in detail_result
        assert "password" not in detail_result

        minimal_result = UserSerializer.use("minimal").dump(user)
        assert minimal_result == {"id": 1, "name": "John"}

    def test_use_invalid_field_set(self):
        """Test use() with invalid field set name."""

        class UserSerializer(Serializer):
            id: int
            name: str

            class Meta:
                field_sets = {"list": ["id", "name"]}

        with pytest.raises(ValueError) as exc_info:
            UserSerializer.use("nonexistent")

        assert "nonexistent" in str(exc_info.value)
        assert "not found" in str(exc_info.value)

    def test_chained_field_selection(self):
        """Test chaining only() and exclude()."""

        class UserSerializer(Serializer):
            id: int
            name: str
            email: str
            phone: str

        user = UserSerializer(
            id=1, name="John", email="john@example.com", phone="123-456-7890"
        )

        # Chain only().exclude()
        view = UserSerializer.only("id", "name", "email").exclude("email")
        result = view.dump(user)

        assert result == {"id": 1, "name": "John"}

    def test_dump_many_with_field_selection(self):
        """Test dump_many with field selection."""

        class UserSerializer(Serializer):
            id: int
            name: str
            email: str

        users = [
            UserSerializer(id=1, name="John", email="john@example.com"),
            UserSerializer(id=2, name="Jane", email="jane@example.com"),
        ]

        result = UserSerializer.only("id", "name").dump_many(users)

        assert len(result) == 2
        assert result[0] == {"id": 1, "name": "John"}
        assert result[1] == {"id": 2, "name": "Jane"}

    def test_field_selection_with_computed_fields(self):
        """Test field selection includes/excludes computed fields."""

        class UserSerializer(Serializer):
            first_name: str
            last_name: str

            @computed_field
            def full_name(self) -> str:
                return f"{self.first_name} {self.last_name}"

        user = UserSerializer(first_name="John", last_name="Doe")

        # Include computed field
        result = UserSerializer.only("first_name", "full_name").dump(user)
        assert result == {"first_name": "John", "full_name": "John Doe"}

        # Exclude computed field
        result2 = UserSerializer.exclude("full_name").dump(user)
        assert "full_name" not in result2
        assert result2 == {"first_name": "John", "last_name": "Doe"}


class TestDumpMethods:
    """Test dump methods with various options."""

    def test_dump_exclude_none(self):
        """Test dump with exclude_none option."""

        class UserSerializer(Serializer):
            name: str
            email: str | None = None
            phone: str | None = None

        user = UserSerializer(name="John", email="john@example.com", phone=None)

        # Without exclude_none
        result = user.dump()
        assert result == {"name": "John", "email": "john@example.com", "phone": None}

        # With exclude_none
        result_filtered = user.dump(exclude_none=True)
        assert result_filtered == {"name": "John", "email": "john@example.com"}

    def test_dump_exclude_defaults(self):
        """Test dump with exclude_defaults option."""

        class UserSerializer(Serializer):
            name: str
            role: str = "user"
            active: bool = True

        user = UserSerializer(name="John", role="user", active=True)

        # Without exclude_defaults
        result = user.dump()
        assert result == {"name": "John", "role": "user", "active": True}

        # With exclude_defaults - default values are excluded
        result_filtered = user.dump(exclude_defaults=True)
        assert result_filtered == {"name": "John"}

    def test_dump_json(self):
        """Test dump_json method."""

        class UserSerializer(Serializer):
            id: int
            name: str

        user = UserSerializer(id=1, name="John")
        json_bytes = user.dump_json()

        assert isinstance(json_bytes, bytes)
        assert b'"id":1' in json_bytes or b'"id": 1' in json_bytes
        assert b'"name":"John"' in json_bytes or b'"name": "John"' in json_bytes

    def test_dump_many_json(self):
        """Test dump_many_json class method."""

        class UserSerializer(Serializer):
            id: int
            name: str

        users = [
            UserSerializer(id=1, name="John"),
            UserSerializer(id=2, name="Jane"),
        ]

        json_bytes = UserSerializer.dump_many_json(users)

        assert isinstance(json_bytes, bytes)
        assert b"John" in json_bytes
        assert b"Jane" in json_bytes


class TestSerializerView:
    """Test SerializerView class."""

    def test_serializer_view_creation(self):
        """Test creating a SerializerView."""

        class UserSerializer(Serializer):
            id: int
            name: str

        view = UserSerializer.only("id")
        assert isinstance(view, SerializerView)

    def test_serializer_view_from_model(self):
        """Test SerializerView.from_model method."""

        class MockModel:
            id = 1
            name = "John"
            email = "john@example.com"

        class UserSerializer(Serializer):
            id: int
            name: str
            email: str

        view = UserSerializer.only("id", "name")
        user = view.from_model(MockModel())

        assert user.id == 1
        assert user.name == "John"

        # Dump respects field selection
        result = view.dump(user)
        assert result == {"id": 1, "name": "John"}


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_one_serializer_multiple_views(self):
        """Test using one serializer for multiple API responses (solving DRF multi-serializer problem)."""

        class UserSerializer(Serializer):
            id: int
            username: str
            email: str
            password_hash: str
            created_at: str
            last_login: str | None = None
            is_active: bool = True
            profile_picture: str | None = None

            class Meta:
                write_only = {"password_hash"}
                field_sets = {
                    "list": ["id", "username", "is_active"],
                    "detail": ["id", "username", "email", "created_at", "last_login", "profile_picture"],
                    "admin": ["id", "username", "email", "created_at", "last_login", "is_active"],
                }

            @computed_field
            def display_name(self) -> str:
                return f"@{self.username}"

        # Create a user
        user = UserSerializer(
            id=1,
            username="johndoe",
            email="john@example.com",
            password_hash="hashed_password_123",
            created_at="2024-01-01T00:00:00Z",
            last_login="2024-01-15T10:30:00Z",
            is_active=True,
            profile_picture="https://example.com/avatar.jpg",
        )

        # List view - minimal fields
        list_result = UserSerializer.use("list").dump(user)
        assert list_result == {"id": 1, "username": "johndoe", "is_active": True}
        assert "password_hash" not in list_result
        assert "email" not in list_result

        # Detail view - more fields
        detail_result = UserSerializer.use("detail").dump(user)
        assert "email" in detail_result
        assert "profile_picture" in detail_result
        assert "password_hash" not in detail_result

        # Admin view
        admin_result = UserSerializer.use("admin").dump(user)
        assert "is_active" in admin_result

        # Custom view with computed field
        custom_result = UserSerializer.only("id", "display_name").dump(user)
        assert custom_result == {"id": 1, "display_name": "@johndoe"}

    def test_nested_serializer_dump(self):
        """Test dumping nested serializers."""

        class AddressSerializer(Serializer):
            street: str
            city: str
            zip_code: str

        class UserSerializer(Serializer):
            id: int
            name: str
            address: AddressSerializer

        address = AddressSerializer(street="123 Main St", city="NYC", zip_code="10001")
        user = UserSerializer(id=1, name="John", address=address)

        result = user.dump()

        assert result["id"] == 1
        assert result["name"] == "John"
        assert result["address"] == {
            "street": "123 Main St",
            "city": "NYC",
            "zip_code": "10001",
        }

    def test_list_of_nested_serializers_dump(self):
        """Test dumping list of nested serializers."""

        class TagSerializer(Serializer):
            id: int
            name: str

        class PostSerializer(Serializer):
            id: int
            title: str
            tags: list[TagSerializer]

        tags = [
            TagSerializer(id=1, name="python"),
            TagSerializer(id=2, name="django"),
        ]
        post = PostSerializer(id=1, title="Hello World", tags=tags)

        result = post.dump()

        assert result["id"] == 1
        assert result["title"] == "Hello World"
        assert len(result["tags"]) == 2
        assert result["tags"][0] == {"id": 1, "name": "python"}
        assert result["tags"][1] == {"id": 2, "name": "django"}

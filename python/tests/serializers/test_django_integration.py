"""Tests for Django model integration with Serializers."""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User as DjangoUser

from django_bolt.serializers import Serializer, create_serializer, create_serializer_set


class TestFromModel:
    """Test converting Django models to Serializers."""

    @pytest.mark.django_db
    def test_from_model_basic(self):
        """Test creating serializer from a model instance."""

        class UserSerializer(Serializer):
            id: int
            username: str
            email: str

        # Create a Django user
        user = DjangoUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Convert to serializer
        serializer = UserSerializer.from_model(user)
        
        assert serializer.id == user.id
        assert serializer.username == "testuser"
        assert serializer.email == "test@example.com"

    @pytest.mark.django_db
    def test_from_model_partial_fields(self):
        """Test from_model with subset of fields."""

        class UserPublicSerializer(Serializer):
            username: str
            email: str

        user = DjangoUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        serializer = UserPublicSerializer.from_model(user)

        assert serializer.username == "testuser"
        assert serializer.email == "test@example.com"


class TestToDict:
    """Test converting Serializers to dictionaries."""

    def test_to_dict_basic(self):
        """Test converting serializer to dict."""

        class UserSerializer(Serializer):
            username: str
            email: str
            is_active: bool = True

        user = UserSerializer(username="alice", email="alice@example.com")
        data = user.to_dict()

        assert isinstance(data, dict)
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert data["is_active"] is True


class TestToModel:
    """Test converting Serializers to Django model instances."""

    def test_to_model_creates_instance(self):
        """Test creating an unsaved model instance from serializer."""

        class UserSerializer(Serializer):
            username: str
            email: str
            first_name: str = ""
            last_name: str = ""

        serializer = UserSerializer(
            username="newuser",
            email="new@example.com",
            first_name="New",
        )

        # Create unsaved model instance
        user = serializer.to_model(DjangoUser)

        # Instance should be created but not saved
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.first_name == "New"
        assert user.pk is None  # Not saved yet

    @pytest.mark.django_db
    def test_to_model_then_save(self):
        """Test creating and saving a model from serializer."""

        class UserSerializer(Serializer):
            username: str
            email: str

        serializer = UserSerializer(
            username="saveuser",
            email="save@example.com",
        )

        # Create and save
        user = serializer.to_model(DjangoUser)
        user.set_password("testpass123")
        user.save()

        # Verify saved
        saved_user = DjangoUser.objects.get(username="saveuser")
        assert saved_user.email == "save@example.com"


class TestUpdateInstance:
    """Test updating model instances with Serializers."""

    @pytest.mark.django_db
    def test_update_instance_basic(self):
        """Test updating a model instance."""

        class UserUpdateSerializer(Serializer):
            username: str
            email: str

        user = DjangoUser.objects.create_user(
            username="oldname",
            email="old@example.com",
            password="testpass123",
        )

        # Update via serializer
        update_data = UserUpdateSerializer(
            username="newname",
            email="new@example.com",
        )
        updated_user = update_data.update_instance(user)

        assert updated_user.username == "newname"
        assert updated_user.email == "new@example.com"
        # Not saved yet
        assert DjangoUser.objects.filter(username="oldname").exists()

    @pytest.mark.django_db
    def test_update_instance_partial(self):
        """Test partial update of a model instance."""

        class UserPartialUpdateSerializer(Serializer, omit_defaults=True):
            username: str | None = None
            email: str | None = None

        user = DjangoUser.objects.create_user(
            username="original",
            email="original@example.com",
            password="testpass123",
        )

        # Update only email
        update_data = UserPartialUpdateSerializer(email="newemail@example.com")
        updated_user = update_data.update_instance(user)

        # Only email should be updated
        assert updated_user.username == "original"
        assert updated_user.email == "newemail@example.com"


class TestCreateSerializerHelper:
    """Test the create_serializer helper function."""

    def test_create_serializer_basic(self):
        """Test creating a serializer from a model."""
        UserSerializer = create_serializer(
            DjangoUser,
            fields=["id", "username", "email"],
        )

        assert hasattr(UserSerializer, "__annotations__")
        assert "username" in UserSerializer.__annotations__
        assert "email" in UserSerializer.__annotations__

    @pytest.mark.django_db
    def test_create_serializer_with_model_instance(self):
        """Test using auto-created serializer with model instance."""
        UserPublic = create_serializer(
            DjangoUser,
            fields=["id", "username", "email"],
        )

        user = DjangoUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Should be able to use from_model
        serializer = UserPublic.from_model(user)
        assert serializer.username == "testuser"
        assert serializer.email == "test@example.com"


class TestCreateSerializerSet:
    """Test the create_serializer_set helper function."""

    def test_create_serializer_set_returns_three(self):
        """Test that create_serializer_set returns 3 serializers."""
        UserCreate, UserUpdate, UserPublic = create_serializer_set(
            DjangoUser,
            create_fields=["username", "email"],
            update_fields=["email"],
            public_fields=["id", "username", "email"],
        )

        assert UserCreate is not None
        assert UserUpdate is not None
        assert UserPublic is not None

    def test_create_serializer_set_naming(self):
        """Test that created serializers have appropriate names."""
        UserCreate, UserUpdate, UserPublic = create_serializer_set(
            DjangoUser,
            create_fields=["username"],
            update_fields=["username"],
            public_fields=["id", "username"],
        )

        assert "Create" in UserCreate.__name__
        assert "Update" in UserUpdate.__name__
        assert "Public" in UserPublic.__name__

    def test_create_serializer_set_field_inclusion(self):
        """Test that each serializer has correct fields."""
        UserCreate, UserUpdate, UserPublic = create_serializer_set(
            DjangoUser,
            create_fields=["username", "email", "password"],
            update_fields=["email"],
            public_fields=["id", "username", "email"],
        )

        # Check field inclusion
        assert "username" in UserCreate.__annotations__
        assert "email" in UserCreate.__annotations__

        assert "email" in UserUpdate.__annotations__
        assert "username" not in UserUpdate.__annotations__

        assert "id" in UserPublic.__annotations__
        assert "username" in UserPublic.__annotations__
        assert "password" not in UserPublic.__annotations__

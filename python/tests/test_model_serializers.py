"""
Tests for ModelSerializer functionality.

Tests automatic field generation, from_model(), to_model(), and msgspec integration.
"""
from __future__ import annotations
import pytest
from datetime import datetime
from decimal import Decimal
from django_bolt.serializers import create_model_serializer
from django.contrib.auth.models import User
from django.db import models


# Simple test model (using Django's built-in User model for most tests)

class Product(models.Model):
    """Test model for products."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'tests'


# Tests

def test_create_model_serializer_basic():
    """Test creating a serializer from a model."""
    UserSerializer = create_model_serializer(
        User,
        fields=['id', 'username', 'email']
    )

    # Check that it's a msgspec.Struct
    import msgspec
    assert issubclass(UserSerializer, msgspec.Struct)

    # Check fields are generated
    assert hasattr(UserSerializer, '__struct_fields__')
    assert 'id' in UserSerializer.__struct_fields__
    assert 'username' in UserSerializer.__struct_fields__
    assert 'email' in UserSerializer.__struct_fields__


def test_create_model_serializer_all_fields():
    """Test creating a serializer with all fields."""
    UserSerializer = create_model_serializer(User, fields='__all__')

    # Should have many fields
    fields = UserSerializer.__struct_fields__
    assert 'id' in fields
    assert 'username' in fields
    assert 'email' in fields
    assert 'password' in fields
    assert 'is_staff' in fields
    assert 'is_active' in fields


def test_create_model_serializer_exclude():
    """Test excluding fields from serializer."""
    UserSerializer = create_model_serializer(
        User,
        fields='__all__',
        exclude=['password']
    )

    fields = UserSerializer.__struct_fields__
    assert 'username' in fields
    assert 'password' not in fields


@pytest.mark.django_db(transaction=True)
def test_from_model_basic(db):
    """Test from_model() with basic fields."""
    # Create a user using Django ORM
    user = User.objects.create(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User"
    )

    # Create serializer
    UserSerializer = create_model_serializer(
        User,
        fields=['id', 'username', 'email', 'first_name', 'last_name']
    )

    # Serialize
    serializer = UserSerializer.from_model(user)

    # Check values
    assert serializer.username == "testuser"
    assert serializer.email == "test@example.com"
    assert serializer.first_name == "Test"
    assert serializer.last_name == "User"
    assert serializer.id == user.id


def test_from_model_none():
    """Test that from_model raises error for None."""
    UserSerializer = create_model_serializer(User, fields=['id', 'username'])

    with pytest.raises(ValueError, match="Cannot serialize None instance"):
        UserSerializer.from_model(None)


def test_msgspec_integration():
    """Test that serializers work with msgspec encoding/decoding."""
    import msgspec

    UserSerializer = create_model_serializer(
        User,
        fields=['id', 'username', 'email']
    )

    # Create instance
    serializer = UserSerializer(id=1, username="john", email="john@example.com")

    # Encode
    encoded = msgspec.json.encode(serializer)
    assert b'"username":"john"' in encoded
    assert b'"email":"john@example.com"' in encoded

    # Decode
    decoded = msgspec.json.decode(encoded, type=UserSerializer)
    assert decoded.username == "john"
    assert decoded.email == "john@example.com"


def test_extra_fields():
    """Test adding extra custom fields."""
    UserSerializer = create_model_serializer(
        User,
        fields=['id', 'username'],
        extra_fields={
            'custom_field': (str, "default"),
            'optional_field': (int | None, None)
        }
    )

    fields = UserSerializer.__struct_fields__
    assert 'username' in fields
    assert 'custom_field' in fields
    assert 'optional_field' in fields


@pytest.mark.django_db(transaction=True)
def test_to_model_create(db):
    """Test to_model() creating a new instance."""
    UserSerializer = create_model_serializer(
        User,
        fields=['username', 'email', 'first_name']
    )

    # Create serializer with data
    serializer = UserSerializer(
        username="newuser",
        email="new@example.com",
        first_name="New"
    )

    # Convert to model
    user = serializer.to_model()

    # Check instance
    assert user.username == "newuser"
    assert user.email == "new@example.com"
    assert user.first_name == "New"
    assert user.pk is None  # Not saved yet


@pytest.mark.django_db(transaction=True)
def test_to_model_update(db):
    """Test to_model() updating an existing instance."""
    # Create existing user
    user = User.objects.create(
        username="oldname",
        email="old@example.com"
    )

    UserSerializer = create_model_serializer(
        User,
        fields=['username', 'email']
    )

    # Create serializer with updates
    serializer = UserSerializer(
        username="newname",
        email="new@example.com"
    )

    # Update existing
    updated_user = serializer.to_model(instance=user)

    # Check updates
    assert updated_user.pk == user.pk
    assert updated_user.username == "newname"
    assert updated_user.email == "new@example.com"


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_asave_create(db):
    """Test asave() creating a new instance."""
    UserSerializer = create_model_serializer(
        User,
        fields=['username', 'email']
    )

    # Create serializer
    serializer = UserSerializer(
        username="asyncuser",
        email="async@example.com"
    )

    # Save asynchronously
    user = await serializer.asave()

    # Check that it's saved
    assert user.pk is not None
    assert user.username == "asyncuser"

    # Verify in database
    db_user = await User.objects.aget(pk=user.pk)
    assert db_user.username == "asyncuser"


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_asave_update(db):
    """Test asave() updating an existing instance."""
    # Create existing user
    user = await User.objects.acreate(
        username="original",
        email="original@example.com"
    )
    original_pk = user.pk

    UserSerializer = create_model_serializer(
        User,
        fields=['username', 'email']
    )

    # Create serializer with updates
    serializer = UserSerializer(
        username="modified",
        email="modified@example.com"
    )

    # Update via asave
    updated_user = await serializer.asave(instance=user)

    # Check
    assert updated_user.pk == original_pk
    assert updated_user.username == "modified"

    # Verify in database
    db_user = await User.objects.aget(pk=original_pk)
    assert db_user.username == "modified"


def test_read_only_fields():
    """Test that read_only_fields are stored."""
    UserSerializer = create_model_serializer(
        User,
        fields=['id', 'username', 'email'],
        read_only_fields=['id']
    )

    # Check read-only fields are stored
    assert hasattr(UserSerializer, '_read_only_fields')
    assert 'id' in UserSerializer._read_only_fields


@pytest.mark.django_db(transaction=True)
def test_serializer_name(db):
    """Test that serializer name can be customized."""
    CustomSerializer = create_model_serializer(
        User,
        name="CustomUserSerializer",
        fields=['id', 'username']
    )

    assert CustomSerializer.__name__ == "CustomUserSerializer"


def test_model_serializer_alias():
    """Test that ModelSerializer is an alias for create_model_serializer."""
    from django_bolt.serializers import ModelSerializer

    assert ModelSerializer == create_model_serializer


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

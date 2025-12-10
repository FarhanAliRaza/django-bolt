"""Tests for ModelSerializer functionality and integration."""

import pytest
from typing import ClassVar, Any

from django_bolt.serializers import (
    ModelSerializer,
    Serializer,
    ValidationError,
)
from django_bolt.serializers.validators import UniqueValidator

# Import test models
from tests.test_models import Author, BlogPost, Comment, Tag, User


# Define serializers at module level to ensure type hints work correctly with msgspec/ClassVar

class AllFieldsSerializer(ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class NameEmailSerializer(ModelSerializer):
    class Meta:
        model = Author
        fields = ["name", "email"]

class ExcludeBioSerializer(ModelSerializer):
    class Meta:
        model = Author
        exclude = ["bio", "created_at"]

class ReadOnlySerializer(ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"
        read_only = {"email"}

class UserWriteSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        write_only = {"password_hash"}

class AuthorCreateSerializer(ModelSerializer):
    class Meta:
        model = Author
        fields = ["name", "email", "bio"]

class AuthorUpdateSerializer(ModelSerializer):
    class Meta:
        model = Author
        fields = ["name"]

class UserUniqueSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]

class PostSerializer(ModelSerializer):
    class Meta:
        model = BlogPost
        fields = "__all__"
        depth = 1

class PostM2MSerializer(ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ["title", "tags"]
        depth = 1


class TestModelSerializerBasics:
    """Test basic ModelSerializer features."""

    def test_meta_fields_all(self):
        """Test fields='__all__' includes all model fields."""
        assert "id" in AllFieldsSerializer.__struct_fields__
        assert "name" in AllFieldsSerializer.__struct_fields__
        assert "email" in AllFieldsSerializer.__struct_fields__
        assert "bio" in AllFieldsSerializer.__struct_fields__

    def test_meta_fields_list(self):
        """Test specific fields selection."""
        assert "name" in NameEmailSerializer.__struct_fields__
        assert "email" in NameEmailSerializer.__struct_fields__
        assert "id" not in NameEmailSerializer.__struct_fields__
        assert "bio" not in NameEmailSerializer.__struct_fields__

    def test_meta_exclude(self):
        """Test exclude option."""
        assert "name" in ExcludeBioSerializer.__struct_fields__
        assert "bio" not in ExcludeBioSerializer.__struct_fields__
        assert "created_at" not in ExcludeBioSerializer.__struct_fields__

    def test_meta_read_only(self):
        """Test read_only configuration."""
        # Force lazy collection of field configs (normally happens on first instantiation)
        # This is needed to pick up read_only from _FieldMarker (like id)
        ReadOnlySerializer._lazy_collect_field_configs()
        
        # Debugging info
        print(f"Meta present: {hasattr(ReadOnlySerializer, 'Meta')}")
        if hasattr(ReadOnlySerializer, 'Meta'):
            print(f"Meta.read_only: {getattr(ReadOnlySerializer.Meta, 'read_only', 'MISSING')}")
        print(f"ReadOnly Fields: {ReadOnlySerializer.__read_only_fields__}")

        assert "email" in ReadOnlySerializer.__read_only_fields__
        # id is auto-detected as read_only (AutoField)
        assert "id" in ReadOnlySerializer.__read_only_fields__
        assert "name" not in ReadOnlySerializer.__read_only_fields__

    def test_meta_write_only(self):
        """Test write_only configuration."""
        UserWriteSerializer._lazy_collect_field_configs()
        assert "password_hash" in UserWriteSerializer.__write_only_fields__


class TestModelSerializerIntegration:
    """Test ModelSerializer interactions with Django models."""

    @pytest.mark.django_db
    def test_create_basic(self):
        """Test creating a model instance."""
        data = {
            "name": "New Author",
            "email": "new@example.com",
            # bio is optional (blank=True on model), so omit it
        }
        
        serializer = AuthorCreateSerializer(**data)
        instance = serializer.create(data)
        instance.save()
        
        assert instance.pk is not None
        assert instance.name == "New Author"
        assert instance.bio == ""

    @pytest.mark.django_db
    def test_update_basic(self):
        """Test updating a model instance."""
        author = Author.objects.create(name="Original", email="orig@example.com")
        
        data = {"name": "Updated"}
        serializer = AuthorUpdateSerializer(name="Updated")
        
        updated = serializer.update(author, data)
        updated.save()
        
        assert updated.name == "Updated"
        assert updated.email == "orig@example.com"  # Unchanged

    @pytest.mark.django_db
    def test_unique_validator_integration(self):
        """Test that unique fields automatically get UniqueValidator."""
        # Create existing user
        User.objects.create(username="existing", email="e@e.com", password_hash="x")
        
        # Try to create user with same username
        # Validation runs on instantiation, so we expect ValidationError here
        with pytest.raises(ValidationError) as exc:
             serializer = UserUniqueSerializer(username="existing", email="new@e.com")
        
        assert "username" in exc.value.errors
        assert "already exists" in str(exc.value.errors["username"][0])


class TestNestedModelSerializer:
    """Test nested features of ModelSerializer."""

    @pytest.mark.django_db
    def test_nested_depth_1_fk(self):
        """Test auto-generated nested serializer for ForeignKey."""
        # Check annotations
        # author field should be handling specific type with Nested
        assert "author" in PostSerializer.__annotations__
        
        # Verify serialization
        author = Author.objects.create(name="Parent", email="p@p.com")
        post = BlogPost.objects.create(title="T", content="C", author=author)
        
        # Need to fetch related for depth > 0 serialization efficiency
        # otherwise individual queries happen
        post_fetched = BlogPost.objects.select_related("author").get(pk=post.pk)
        
        serializer = PostSerializer.from_model(post_fetched)
        dump = serializer.dump()
        
        assert isinstance(dump["author"], dict)
        assert dump["author"]["name"] == "Parent"

    @pytest.mark.django_db
    def test_nested_depth_1_m2m(self):
        """Test auto-generated nested serializer for ManyToMany."""
        tag = Tag.objects.create(name="Tag1")
        author = Author.objects.create(name="A", email="a@a.com")
        post = BlogPost.objects.create(title="T", content="C", author=author)
        post.tags.add(tag)
        
        post_fetched = BlogPost.objects.prefetch_related("tags").get(pk=post.pk)
        
        serializer = PostM2MSerializer.from_model(post_fetched)
        dump = serializer.dump()
        
        assert isinstance(dump["tags"], list)
        assert len(dump["tags"]) == 1
        assert dump["tags"][0]["name"] == "Tag1"

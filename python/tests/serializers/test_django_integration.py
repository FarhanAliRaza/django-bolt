"""Tests for Django model integration with Serializers.

This file tests all advanced serializer features with real Django models:
- from_model / to_model / update_instance
- field() with read_only/write_only
- @computed_field with Django model data
- @field_validator with Django models
- @model_validator for cross-field validation
- Dynamic field selection (only/exclude/use)
- Type-safe subsets (subset/fields)
- Reusable validated types (Email, URL, etc.)
- Nested serializers with Django relationships
- Dump options (exclude_none, exclude_defaults)

NOTE: msgspec Meta constraints (pattern, ge, le, min_length, etc.) and
@field_validator/@model_validator decorators only validate during:
- model_validate_json() - JSON string/bytes parsing
- model_validate() - dict parsing via msgspec.convert

Direct instantiation (MySerializer(field=value)) and from_model() DO run
custom @field_validator and @model_validator, but they bypass msgspec Meta
constraints. This is msgspec's design - Meta constraints are for parsing.
"""

from datetime import datetime
from typing import Annotated

import pytest
import msgspec

from django_bolt.serializers import (
    Serializer,
    computed_field,
    field_validator,
    model_validator,
    create_serializer,
    create_serializer_set,
    Nested,
    Email,
    URL,
    NonEmptyStr,
    PositiveInt,
)
from django_bolt.serializers.types import (
    Username,
    Percentage,
    Latitude,
    Longitude,
)

# Import test models
from tests.test_models import Author, Tag, BlogPost, Comment, User, UserProfile


# =============================================================================
# Serializers for testing
# =============================================================================


class AuthorSerializer(Serializer):
    """Serializer for Author model with computed field."""

    id: int
    name: NonEmptyStr
    email: Email
    bio: str = ""

    @computed_field
    def display_name(self) -> str:
        return f"{self.name} <{self.email}>"


class TagSerializer(Serializer):
    """Simple serializer for Tag model."""

    id: int
    name: str
    description: str = ""


class CommentSerializer(Serializer):
    """Serializer for Comment model with nested author."""

    id: int
    text: str
    author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]
    created_at: datetime


class BlogPostSerializer(Serializer):
    """Full serializer for BlogPost with all relationships."""

    id: int
    title: NonEmptyStr
    content: str
    author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]
    tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)]
    comments: Annotated[list[CommentSerializer], Nested(CommentSerializer, many=True)] = []
    published: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Meta:
        field_sets = {
            "list": ["id", "title", "published", "created_at"],
            "detail": ["id", "title", "content", "author", "tags", "published", "created_at", "updated_at"],
            "admin": ["id", "title", "content", "author", "tags", "comments", "published", "created_at", "updated_at"],
        }

    @computed_field
    def tag_names(self) -> list[str]:
        return [t.name for t in self.tags]

    @computed_field
    def comment_count(self) -> int:
        return len(self.comments)


class UserSerializer(Serializer):
    """User serializer with validators and computed fields."""

    id: int
    username: Username
    email: Email
    password_hash: str = ""
    is_active: bool = True
    is_staff: bool = False
    created_at: datetime | None = None

    class Meta:
        write_only = {"password_hash"}
        field_sets = {
            "list": ["id", "username", "is_active"],
            "detail": ["id", "username", "email", "is_active", "is_staff", "created_at"],
            "admin": ["id", "username", "email", "is_active", "is_staff", "created_at"],
        }

    @field_validator("username")
    def validate_username(cls, value: str) -> str:
        """Username must be lowercase."""
        return value.lower()

    @field_validator("email")
    def validate_email(cls, value: str) -> str:
        """Email must be lowercase."""
        return value.lower()

    @computed_field
    def display_name(self) -> str:
        return f"@{self.username}"


class UserProfileSerializer(Serializer):
    """User profile serializer with nested user."""

    id: int
    user: Annotated[UserSerializer, Nested(UserSerializer)]
    bio: str = ""
    avatar_url: URL | None = None
    phone: str = ""
    location: str = ""

    @computed_field
    def has_avatar(self) -> bool:
        return bool(self.avatar_url)


class UserCreateSerializer(Serializer):
    """Input serializer for creating users with validation."""

    username: Username
    email: Email
    password: NonEmptyStr
    password_confirm: NonEmptyStr

    @field_validator("username")
    def validate_username(cls, value: str) -> str:
        return value.lower().strip()

    @field_validator("email")
    def validate_email(cls, value: str) -> str:
        return value.lower().strip()

    @model_validator
    def validate_passwords(self) -> "UserCreateSerializer":
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class LocationSerializer(Serializer):
    """Serializer with geographic validated types."""

    name: NonEmptyStr
    latitude: Latitude
    longitude: Longitude
    accuracy: Percentage = 100.0


# =============================================================================
# Test Classes
# =============================================================================


class TestFromModelWithDjango:
    """Test converting Django models to Serializers."""

    @pytest.mark.django_db
    def test_from_model_simple(self):
        """Test basic from_model with Author."""
        author = Author.objects.create(
            name="John Doe",
            email="john@example.com",
            bio="A test author",
        )

        serializer = AuthorSerializer.from_model(author)

        assert serializer.id == author.id
        assert serializer.name == "John Doe"
        assert serializer.email == "john@example.com"
        assert serializer.bio == "A test author"

    @pytest.mark.django_db
    def test_from_model_with_computed_field(self):
        """Test from_model includes computed fields in dump."""
        author = Author.objects.create(
            name="Jane Smith",
            email="jane@example.com",
        )

        serializer = AuthorSerializer.from_model(author)
        result = serializer.dump()

        assert result["display_name"] == "Jane Smith <jane@example.com>"

    @pytest.mark.django_db
    def test_from_model_with_nested_fk(self):
        """Test from_model with ForeignKey relationship."""
        author = Author.objects.create(name="Alice", email="alice@example.com")
        post = BlogPost.objects.create(
            title="Test Post",
            content="Test content",
            author=author,
        )

        # Fetch with select_related for efficient query
        post = BlogPost.objects.select_related("author").get(id=post.id)

        # Create serializer manually with nested data
        author_serializer = AuthorSerializer.from_model(post.author)
        serializer = BlogPostSerializer(
            id=post.id,
            title=post.title,
            content=post.content,
            author=author_serializer,
            tags=[],
            published=post.published,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )

        result = serializer.dump()

        assert result["title"] == "Test Post"
        assert result["author"]["name"] == "Alice"
        assert result["author"]["email"] == "alice@example.com"

    @pytest.mark.django_db
    def test_from_model_with_m2m(self):
        """Test from_model with ManyToMany relationship."""
        author = Author.objects.create(name="Bob", email="bob@example.com")
        tag1 = Tag.objects.create(name="python", description="Python programming")
        tag2 = Tag.objects.create(name="django", description="Django framework")

        post = BlogPost.objects.create(
            title="Python Django Tutorial",
            content="Learn Django with Python",
            author=author,
        )
        post.tags.add(tag1, tag2)

        # Fetch with prefetch_related
        post = BlogPost.objects.select_related("author").prefetch_related("tags").get(id=post.id)

        # Build serializer with nested data
        author_serializer = AuthorSerializer.from_model(post.author)
        tag_serializers = [TagSerializer.from_model(t) for t in post.tags.all()]

        serializer = BlogPostSerializer(
            id=post.id,
            title=post.title,
            content=post.content,
            author=author_serializer,
            tags=tag_serializers,
            published=post.published,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )

        result = serializer.dump()

        assert len(result["tags"]) == 2
        assert result["tag_names"] == ["python", "django"]

    @pytest.mark.django_db
    def test_from_model_with_validators(self):
        """Test from_model runs field validators."""
        user = User.objects.create(
            username="TestUser",  # Will be lowercased by validator
            email="TEST@EXAMPLE.COM",  # Will be lowercased by validator
            password_hash="hashed",
        )

        serializer = UserSerializer.from_model(user)

        # Validators should have run
        assert serializer.username == "testuser"
        assert serializer.email == "test@example.com"


class TestToModelWithDjango:
    """Test converting Serializers to Django model instances."""

    def test_to_model_creates_unsaved_instance(self):
        """Test creating an unsaved model instance."""
        # Note: to_model transfers ALL fields from the serializer, including id
        # So if you pass id=0, the model will have id=0, not pk=None
        # For truly new instances, use a serializer without id field or omit it

        class AuthorCreateSerializer(Serializer):
            """Serializer without id field for creating new authors."""

            name: NonEmptyStr
            email: Email
            bio: str = ""

        serializer = AuthorCreateSerializer(
            name="New Author",
            email="new@example.com",
            bio="A new author bio",
        )

        author = serializer.to_model(Author)

        assert author.name == "New Author"
        assert author.email == "new@example.com"
        assert author.bio == "A new author bio"
        assert author.pk is None  # Not saved - no id was set

    @pytest.mark.django_db
    def test_to_model_and_save(self):
        """Test creating and saving a model from serializer."""
        serializer = AuthorSerializer(
            id=0,
            name="Saved Author",
            email="saved@example.com",
            bio="Will be saved",
        )

        author = serializer.to_model(Author)
        author.save()

        # Verify saved
        saved_author = Author.objects.get(email="saved@example.com")
        assert saved_author.name == "Saved Author"

    @pytest.mark.django_db
    def test_to_model_excludes_computed_fields(self):
        """Test that computed fields are not set on the model."""
        serializer = AuthorSerializer(
            id=0,
            name="Author With Computed",
            email="computed@example.com",
        )

        author = serializer.to_model(Author)

        # Should not have display_name attribute (it's computed)
        assert not hasattr(author, "display_name") or author.display_name != serializer.display_name()


class TestUpdateInstanceWithDjango:
    """Test updating Django model instances with Serializers."""

    @pytest.mark.django_db
    def test_update_instance_basic(self):
        """Test updating model instance fields."""
        author = Author.objects.create(
            name="Original Name",
            email="original@example.com",
        )

        update_data = AuthorSerializer(
            id=author.id,
            name="Updated Name",
            email="updated@example.com",
            bio="New bio",
        )

        updated_author = update_data.update_instance(author)

        assert updated_author.name == "Updated Name"
        assert updated_author.email == "updated@example.com"
        assert updated_author.bio == "New bio"
        # Not saved yet
        original = Author.objects.get(id=author.id)
        assert original.name == "Original Name"

    @pytest.mark.django_db
    def test_update_instance_and_save(self):
        """Test updating and saving model instance."""
        author = Author.objects.create(
            name="Original",
            email="original@example.com",
        )

        update_data = AuthorSerializer(
            id=author.id,
            name="Updated",
            email="updated@example.com",
        )

        updated_author = update_data.update_instance(author)
        updated_author.save()

        # Verify saved
        refreshed = Author.objects.get(id=author.id)
        assert refreshed.name == "Updated"


class TestFieldValidatorsWithDjango:
    """Test @field_validator with Django models."""

    @pytest.mark.django_db
    def test_field_validator_transforms_value(self):
        """Test field validators transform values during from_model."""
        user = User.objects.create(
            username="MixedCase",
            email="UPPER@CASE.COM",
            password_hash="hash",
        )

        serializer = UserSerializer.from_model(user)

        # Validators should lowercase
        assert serializer.username == "mixedcase"
        assert serializer.email == "upper@case.com"

    def test_field_validator_on_parse(self):
        """Test field validators run during JSON parsing."""
        json_data = b'{"username": "TestUser", "email": "TEST@EXAMPLE.COM", "password": "secret", "password_confirm": "secret"}'

        user_create = UserCreateSerializer.model_validate_json(json_data)

        assert user_create.username == "testuser"
        assert user_create.email == "test@example.com"

    def test_field_validator_transforms_and_strips(self):
        """Test field validators transform values during direct instantiation."""
        # Note: When using Username type with pattern validation, whitespace fails
        # msgspec Meta validation. So we test with direct instantiation where
        # pattern validation is bypassed but field validators still run.
        user_create = UserCreateSerializer(
            username="TESTUSER",  # Uppercase, will be lowercased
            email="  EMAIL@EXAMPLE.COM  ",  # Will be lowercased and stripped
            password="secret",
            password_confirm="secret",
        )

        # Field validators run on direct instantiation
        assert user_create.username == "testuser"
        assert user_create.email == "email@example.com"


class TestModelValidatorsWithDjango:
    """Test @model_validator with Django model scenarios."""

    def test_model_validator_passes(self):
        """Test model validator passes when valid."""
        user_create = UserCreateSerializer(
            username="validuser",
            email="valid@example.com",
            password="secret123",
            password_confirm="secret123",
        )

        # Should not raise
        assert user_create.password == user_create.password_confirm

    def test_model_validator_fails(self):
        """Test model validator raises on invalid data."""
        # Model validators raise msgspec.ValidationError (wrapping the ValueError)
        with pytest.raises(msgspec.ValidationError, match="Passwords do not match"):
            UserCreateSerializer(
                username="user",
                email="user@example.com",
                password="secret123",
                password_confirm="different",
            )

    def test_model_validator_via_json_parse(self):
        """Test model validator runs during JSON parsing."""
        json_data = b'{"username": "user", "email": "user@example.com", "password": "abc", "password_confirm": "xyz"}'

        # Model validators raise msgspec.ValidationError
        with pytest.raises(msgspec.ValidationError, match="Passwords do not match"):
            UserCreateSerializer.model_validate_json(json_data)


class TestComputedFieldsWithDjango:
    """Test @computed_field with Django models."""

    @pytest.mark.django_db
    def test_computed_field_in_dump(self):
        """Test computed fields appear in dump output."""
        author = Author.objects.create(name="Author", email="author@example.com")

        serializer = AuthorSerializer.from_model(author)
        result = serializer.dump()

        assert "display_name" in result
        assert result["display_name"] == "Author <author@example.com>"

    @pytest.mark.django_db
    def test_computed_field_with_relationships(self):
        """Test computed field accessing nested data."""
        author = Author.objects.create(name="Bob", email="bob@example.com")
        tag1 = Tag.objects.create(name="python")
        tag2 = Tag.objects.create(name="django")

        post = BlogPost.objects.create(title="Test", content="Content", author=author)
        post.tags.add(tag1, tag2)

        # Fetch with relationships
        post = BlogPost.objects.select_related("author").prefetch_related("tags", "comments").get(id=post.id)

        # Build serializer
        author_serializer = AuthorSerializer.from_model(post.author)
        tag_serializers = [TagSerializer.from_model(t) for t in post.tags.all()]
        comment_serializers = [
            CommentSerializer(
                id=c.id,
                text=c.text,
                author=AuthorSerializer.from_model(c.author),
                created_at=c.created_at,
            )
            for c in post.comments.all()
        ]

        serializer = BlogPostSerializer(
            id=post.id,
            title=post.title,
            content=post.content,
            author=author_serializer,
            tags=tag_serializers,
            comments=comment_serializers,
            published=post.published,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )

        result = serializer.dump()

        assert result["tag_names"] == ["python", "django"]
        assert result["comment_count"] == 0

    @pytest.mark.django_db
    def test_computed_field_exclude_none(self):
        """Test computed field respects exclude_none."""

        class OptionalComputedSerializer(Serializer):
            name: str
            value: int | None = None

            @computed_field
            def doubled(self) -> int | None:
                if self.value is not None:
                    return self.value * 2
                return None

        s1 = OptionalComputedSerializer(name="test", value=None)
        result = s1.dump(exclude_none=True)

        assert "value" not in result
        assert "doubled" not in result

        s2 = OptionalComputedSerializer(name="test", value=5)
        result2 = s2.dump(exclude_none=True)

        assert result2["doubled"] == 10


class TestDynamicFieldSelectionWithDjango:
    """Test only/exclude/use with Django models."""

    @pytest.mark.django_db
    def test_only_with_django_model(self):
        """Test only() with Django model data."""
        author = Author.objects.create(name="Alice", email="alice@example.com", bio="Bio text")

        serializer = AuthorSerializer.from_model(author)

        # Use only() to select specific fields
        result = AuthorSerializer.only("id", "name").dump(serializer)

        assert result == {"id": author.id, "name": "Alice"}
        assert "email" not in result
        assert "bio" not in result

    @pytest.mark.django_db
    def test_exclude_with_django_model(self):
        """Test exclude() with Django model data."""
        user = User.objects.create(
            username="testuser",
            email="test@example.com",
            password_hash="secret_hash",
        )

        serializer = UserSerializer.from_model(user)

        # Exclude sensitive fields (password_hash already excluded via Meta.write_only)
        result = UserSerializer.exclude("is_staff", "created_at").dump(serializer)

        assert "is_staff" not in result
        assert "created_at" not in result
        assert "username" in result

    @pytest.mark.django_db
    def test_use_field_set_with_django(self):
        """Test use() with predefined field sets."""
        author = Author.objects.create(name="Bob", email="bob@example.com")
        post = BlogPost.objects.create(
            title="Test Post",
            content="Content here",
            author=author,
            published=True,
        )

        author_serializer = AuthorSerializer.from_model(author)
        serializer = BlogPostSerializer(
            id=post.id,
            title=post.title,
            content=post.content,
            author=author_serializer,
            tags=[],
            published=post.published,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )

        # List view - minimal fields
        list_result = BlogPostSerializer.use("list").dump(serializer)
        assert set(list_result.keys()) == {"id", "title", "published", "created_at"}

        # Detail view - more fields
        detail_result = BlogPostSerializer.use("detail").dump(serializer)
        assert "author" in detail_result
        assert "content" in detail_result
        assert "comments" not in detail_result

    @pytest.mark.django_db
    def test_dump_many_with_field_selection(self):
        """Test dump_many with only() on multiple instances."""
        Author.objects.create(name="Author1", email="a1@example.com")
        Author.objects.create(name="Author2", email="a2@example.com")
        Author.objects.create(name="Author3", email="a3@example.com")

        authors = Author.objects.all()
        serializers = [AuthorSerializer.from_model(a) for a in authors]

        result = AuthorSerializer.only("id", "name").dump_many(serializers)

        assert len(result) == 3
        for item in result:
            assert set(item.keys()) == {"id", "name"}


class TestSubsetWithDjango:
    """Test subset() and fields() with Django models."""

    @pytest.mark.django_db
    def test_subset_from_model(self):
        """Test subset class works with from_model."""
        user = User.objects.create(
            username="testuser",
            email="test@example.com",
            password_hash="hash",
            is_staff=True,
        )

        # Create a mini serializer
        UserMini = UserSerializer.subset("id", "username", "email")

        mini_user = UserMini.from_model(user)

        assert mini_user.id == user.id
        assert mini_user.username == "testuser"
        assert mini_user.email == "test@example.com"

        result = mini_user.dump()
        assert set(result.keys()) == {"id", "username", "email"}

    @pytest.mark.django_db
    def test_fields_from_field_set_with_django(self):
        """Test fields() creates proper subset from field_sets."""
        user = User.objects.create(
            username="listuser",
            email="list@example.com",
            password_hash="hash",
        )

        # Create list serializer from field set
        UserListSerializer = UserSerializer.fields("list")

        list_user = UserListSerializer.from_model(user)

        result = list_user.dump()
        assert set(result.keys()) == {"id", "username", "is_active"}

    @pytest.mark.django_db
    def test_subset_preserves_validators(self):
        """Test that subset serializers preserve field validators."""
        UserMini = UserSerializer.subset("id", "username", "email")

        # Validators should still run
        mini = UserMini(
            id=1,
            username="UPPERCASE",
            email="UPPER@EXAMPLE.COM",
        )

        assert mini.username == "uppercase"
        assert mini.email == "upper@example.com"

    @pytest.mark.django_db
    def test_subset_with_computed_field(self):
        """Test subset includes computed fields."""
        user = User.objects.create(
            username="compute",
            email="compute@example.com",
            password_hash="hash",
        )

        # Include computed field in subset
        UserWithDisplay = UserSerializer.subset("id", "username", "display_name")

        user_serializer = UserWithDisplay.from_model(user)
        result = user_serializer.dump()

        assert result["display_name"] == "@compute"

    @pytest.mark.django_db
    def test_subset_from_parent(self):
        """Test creating subset instance from parent instance."""
        user = User.objects.create(
            username="parent",
            email="parent@example.com",
            password_hash="hash",
            is_staff=True,
        )

        full_user = UserSerializer.from_model(user)
        UserMini = UserSerializer.subset("id", "username")

        mini_user = UserMini.from_parent(full_user)

        assert mini_user.id == full_user.id
        assert mini_user.username == full_user.username
        assert set(mini_user.dump().keys()) == {"id", "username"}


class TestValidatedTypesWithDjango:
    """Test reusable validated types with Django models."""

    @pytest.mark.django_db
    def test_email_type_validation(self):
        """Test Email type validates correctly."""

        class StrictAuthorSerializer(Serializer):
            name: NonEmptyStr
            email: Email

        # Valid email
        author = StrictAuthorSerializer.model_validate_json(
            b'{"name": "Test", "email": "valid@example.com"}'
        )
        assert author.email == "valid@example.com"

        # Invalid email
        with pytest.raises(msgspec.ValidationError):
            StrictAuthorSerializer.model_validate_json(
                b'{"name": "Test", "email": "invalid-email"}'
            )

    def test_positive_int_validation(self):
        """Test PositiveInt type validates correctly."""

        class ItemSerializer(Serializer):
            name: str
            quantity: PositiveInt

        # Valid
        item = ItemSerializer.model_validate_json(b'{"name": "Widget", "quantity": 10}')
        assert item.quantity == 10

        # Invalid (zero)
        with pytest.raises(msgspec.ValidationError):
            ItemSerializer.model_validate_json(b'{"name": "Widget", "quantity": 0}')

        # Invalid (negative)
        with pytest.raises(msgspec.ValidationError):
            ItemSerializer.model_validate_json(b'{"name": "Widget", "quantity": -5}')

    def test_geographic_types_validation(self):
        """Test Latitude and Longitude types."""
        # Valid location
        loc = LocationSerializer.model_validate_json(
            b'{"name": "NYC", "latitude": 40.7128, "longitude": -74.0060}'
        )
        assert loc.latitude == 40.7128
        assert loc.longitude == -74.0060

        # Invalid latitude (> 90)
        with pytest.raises(msgspec.ValidationError):
            LocationSerializer.model_validate_json(
                b'{"name": "Invalid", "latitude": 91.0, "longitude": 0}'
            )

        # Invalid longitude (> 180)
        with pytest.raises(msgspec.ValidationError):
            LocationSerializer.model_validate_json(
                b'{"name": "Invalid", "latitude": 0, "longitude": 181.0}'
            )

    def test_validated_types_in_subset(self):
        """Test validated types are preserved in subset."""
        UserMini = UserSerializer.subset("id", "username", "email")

        # Validation should still work (via JSON parsing)
        with pytest.raises(msgspec.ValidationError):
            UserMini.model_validate_json(b'{"id": 1, "username": "ab", "email": "invalid"}')


class TestDumpOptionsWithDjango:
    """Test dump options with Django model data."""

    @pytest.mark.django_db
    def test_dump_exclude_none(self):
        """Test dump(exclude_none=True) with Django model."""
        author = Author.objects.create(name="Author", email="author@example.com")

        # Create serializer with optional None field
        class AuthorWithOptional(Serializer):
            id: int
            name: str
            email: str
            bio: str | None = None

        _ = AuthorWithOptional.from_model(author)  # verify from_model works
        # bio is empty string from Django, not None
        # Let's manually set it to None
        serializer_with_none = AuthorWithOptional(
            id=author.id,
            name=author.name,
            email=author.email,
            bio=None,
        )

        result = serializer_with_none.dump(exclude_none=True)

        assert "bio" not in result
        assert "name" in result

    @pytest.mark.django_db
    def test_dump_exclude_defaults(self):
        """Test dump(exclude_defaults=True) with Django model."""
        user = User.objects.create(
            username="defaultuser",
            email="default@example.com",
            password_hash="hash",
            is_active=True,  # Default value
            is_staff=False,  # Default value
        )

        serializer = UserSerializer.from_model(user)

        # exclude_defaults removes fields with default values
        result = serializer.dump(exclude_defaults=True)

        # is_active=True and is_staff=False are defaults, should be excluded
        assert "is_active" not in result
        assert "is_staff" not in result

    @pytest.mark.django_db
    def test_dump_exclude_none_with_computed(self):
        """Test exclude_none works with computed fields."""

        class ComputedNullable(Serializer):
            name: str
            status: str | None = None

            @computed_field
            def message(self) -> str | None:
                if self.status:
                    return f"Status: {self.status}"
                return None

        s = ComputedNullable(name="test", status=None)
        result = s.dump(exclude_none=True)

        assert "status" not in result
        assert "message" not in result


class TestNestedSerializersWithDjango:
    """Test nested serializers with Django relationships."""

    @pytest.mark.django_db
    def test_nested_foreignkey(self):
        """Test nested serializer with ForeignKey."""
        author = Author.objects.create(name="Author", email="author@example.com")
        post = BlogPost.objects.create(
            title="Nested Test",
            content="Testing nested FK",
            author=author,
        )

        post = BlogPost.objects.select_related("author").get(id=post.id)

        author_serializer = AuthorSerializer.from_model(post.author)
        serializer = BlogPostSerializer(
            id=post.id,
            title=post.title,
            content=post.content,
            author=author_serializer,
            tags=[],
            published=post.published,
        )

        result = serializer.dump()

        assert result["author"]["name"] == "Author"
        assert result["author"]["email"] == "author@example.com"
        assert result["author"]["display_name"] == "Author <author@example.com>"

    @pytest.mark.django_db
    def test_nested_many_to_many(self):
        """Test nested serializer with ManyToMany."""
        author = Author.objects.create(name="Author", email="author@example.com")
        tag1 = Tag.objects.create(name="tag1")
        tag2 = Tag.objects.create(name="tag2")

        post = BlogPost.objects.create(title="M2M Test", content="Content", author=author)
        post.tags.add(tag1, tag2)

        post = BlogPost.objects.select_related("author").prefetch_related("tags").get(id=post.id)

        author_serializer = AuthorSerializer.from_model(post.author)
        tag_serializers = [TagSerializer.from_model(t) for t in post.tags.all()]

        serializer = BlogPostSerializer(
            id=post.id,
            title=post.title,
            content=post.content,
            author=author_serializer,
            tags=tag_serializers,
            published=post.published,
        )

        result = serializer.dump()

        assert len(result["tags"]) == 2
        assert result["tags"][0]["name"] == "tag1"
        assert result["tags"][1]["name"] == "tag2"

    @pytest.mark.django_db
    def test_deeply_nested_relationships(self):
        """Test deeply nested serializers (post -> comments -> author)."""
        author1 = Author.objects.create(name="PostAuthor", email="post@example.com")
        author2 = Author.objects.create(name="Commenter", email="comment@example.com")

        post = BlogPost.objects.create(title="Deep Nesting", content="Content", author=author1)
        Comment.objects.create(post=post, author=author2, text="A comment")

        post = (
            BlogPost.objects.select_related("author")
            .prefetch_related("tags", "comments__author")
            .get(id=post.id)
        )

        author_serializer = AuthorSerializer.from_model(post.author)
        comment_serializers = [
            CommentSerializer(
                id=c.id,
                text=c.text,
                author=AuthorSerializer.from_model(c.author),
                created_at=c.created_at,
            )
            for c in post.comments.all()
        ]

        serializer = BlogPostSerializer(
            id=post.id,
            title=post.title,
            content=post.content,
            author=author_serializer,
            tags=[],
            comments=comment_serializers,
            published=post.published,
        )

        result = serializer.dump()

        assert len(result["comments"]) == 1
        assert result["comments"][0]["text"] == "A comment"
        assert result["comments"][0]["author"]["name"] == "Commenter"
        assert result["comment_count"] == 1

    @pytest.mark.django_db
    def test_onetoone_relationship(self):
        """Test nested serializer with OneToOne relationship."""
        user = User.objects.create(
            username="profileuser",
            email="profile@example.com",
            password_hash="hash",
        )
        profile = UserProfile.objects.create(
            user=user,
            bio="Test bio",
            location="NYC",
        )

        profile = UserProfile.objects.select_related("user").get(id=profile.id)

        user_serializer = UserSerializer.from_model(profile.user)
        profile_serializer = UserProfileSerializer(
            id=profile.id,
            user=user_serializer,
            bio=profile.bio,
            avatar_url=None,
            phone=profile.phone,
            location=profile.location,
        )

        result = profile_serializer.dump()

        assert result["user"]["username"] == "profileuser"
        assert result["bio"] == "Test bio"
        assert result["has_avatar"] is False


class TestWriteOnlyFieldsWithDjango:
    """Test write_only fields with Django models."""

    @pytest.mark.django_db
    def test_write_only_excluded_from_dump(self):
        """Test write_only fields are excluded from dump."""
        user = User.objects.create(
            username="secureuser",
            email="secure@example.com",
            password_hash="super_secret_hash",
        )

        serializer = UserSerializer.from_model(user)
        result = serializer.dump()

        # password_hash is write_only, should not appear
        assert "password_hash" not in result
        assert "username" in result

    @pytest.mark.django_db
    def test_write_only_in_various_views(self):
        """Test write_only fields excluded across field sets."""
        user = User.objects.create(
            username="viewuser",
            email="view@example.com",
            password_hash="hash",
        )

        serializer = UserSerializer.from_model(user)

        # All views should exclude password_hash
        for field_set in ["list", "detail", "admin"]:
            result = UserSerializer.use(field_set).dump(serializer)
            assert "password_hash" not in result


class TestCreateSerializerHelpersWithDjango:
    """Test create_serializer and create_serializer_set helpers."""

    def test_create_serializer_from_django_model(self):
        """Test creating serializer from Django model."""
        from django.contrib.auth.models import User as DjangoUser

        UserSerializer = create_serializer(
            DjangoUser,
            fields=["id", "username", "email", "is_active"],
        )

        assert "id" in UserSerializer.__annotations__
        assert "username" in UserSerializer.__annotations__
        assert "email" in UserSerializer.__annotations__
        assert "is_active" in UserSerializer.__annotations__

    @pytest.mark.django_db
    def test_create_serializer_set_with_django(self):
        """Test create_serializer_set with Django model."""
        from django.contrib.auth.models import User as DjangoUser

        UserCreate, UserUpdate, UserPublic = create_serializer_set(
            DjangoUser,
            create_fields=["username", "email", "password"],
            update_fields=["email", "first_name", "last_name"],
            public_fields=["id", "username", "email"],
        )

        # Verify each has correct fields
        assert "username" in UserCreate.__annotations__
        assert "password" in UserCreate.__annotations__

        assert "email" in UserUpdate.__annotations__
        assert "username" not in UserUpdate.__annotations__

        assert "id" in UserPublic.__annotations__
        assert "password" not in UserPublic.__annotations__


class TestBulkOperationsWithDjango:
    """Test bulk operations with Django models."""

    @pytest.mark.django_db
    def test_dump_many_with_django_queryset(self):
        """Test dump_many with a queryset of models."""
        Author.objects.create(name="Author1", email="a1@example.com")
        Author.objects.create(name="Author2", email="a2@example.com")
        Author.objects.create(name="Author3", email="a3@example.com")

        authors = Author.objects.all()
        serializers = [AuthorSerializer.from_model(a) for a in authors]

        result = AuthorSerializer.dump_many(serializers)

        assert len(result) == 3
        assert all("display_name" in item for item in result)

    @pytest.mark.django_db
    def test_dump_many_json_with_django(self):
        """Test dump_many_json with Django models."""
        Author.objects.create(name="JSON1", email="j1@example.com")
        Author.objects.create(name="JSON2", email="j2@example.com")

        authors = Author.objects.all()
        serializers = [AuthorSerializer.from_model(a) for a in authors]

        json_bytes = AuthorSerializer.dump_many_json(serializers)

        assert isinstance(json_bytes, bytes)
        assert b"JSON1" in json_bytes
        assert b"JSON2" in json_bytes

    @pytest.mark.django_db
    def test_dump_many_with_field_selection_django(self):
        """Test dump_many with only() on Django data."""
        User.objects.create(username="bulk1", email="bulk1@example.com", password_hash="h1")
        User.objects.create(username="bulk2", email="bulk2@example.com", password_hash="h2")

        users = User.objects.all()
        serializers = [UserSerializer.from_model(u) for u in users]

        result = UserSerializer.only("id", "username").dump_many(serializers)

        assert len(result) == 2
        for item in result:
            assert set(item.keys()) == {"id", "username"}


class TestComplexDjangoScenarios:
    """Test complex real-world Django scenarios."""

    @pytest.mark.django_db
    def test_api_list_view_pattern(self):
        """Test typical API list view pattern."""
        # Create test data
        author = Author.objects.create(name="Blogger", email="blogger@example.com")
        for i in range(5):
            BlogPost.objects.create(
                title=f"Post {i + 1}",
                content=f"Content for post {i + 1}",
                author=author,
                published=i % 2 == 0,
            )

        # Fetch posts with list optimization
        posts = BlogPost.objects.select_related("author").order_by("-created_at")

        # Use list field set for minimal data
        BlogPostList = BlogPostSerializer.fields("list")

        results = []
        for post in posts:
            # For list view, we don't need all nested data
            s = BlogPostList(
                id=post.id,
                title=post.title,
                published=post.published,
                created_at=post.created_at,
            )
            results.append(s.dump())

        assert len(results) == 5
        for item in results:
            assert set(item.keys()) == {"id", "title", "published", "created_at"}

    @pytest.mark.django_db
    def test_api_detail_view_pattern(self):
        """Test typical API detail view pattern with full relationships."""
        author = Author.objects.create(name="DetailAuthor", email="detail@example.com")
        tag1 = Tag.objects.create(name="detail-tag-1")
        tag2 = Tag.objects.create(name="detail-tag-2")

        post = BlogPost.objects.create(
            title="Detailed Post",
            content="Full content here",
            author=author,
            published=True,
        )
        post.tags.add(tag1, tag2)

        Comment.objects.create(post=post, author=author, text="Self comment")

        # Detail view needs full data
        post = (
            BlogPost.objects.select_related("author")
            .prefetch_related("tags", "comments__author")
            .get(id=post.id)
        )

        # Build full serializer
        author_serializer = AuthorSerializer.from_model(post.author)
        tag_serializers = [TagSerializer.from_model(t) for t in post.tags.all()]
        comment_serializers = [
            CommentSerializer(
                id=c.id,
                text=c.text,
                author=AuthorSerializer.from_model(c.author),
                created_at=c.created_at,
            )
            for c in post.comments.all()
        ]

        serializer = BlogPostSerializer(
            id=post.id,
            title=post.title,
            content=post.content,
            author=author_serializer,
            tags=tag_serializers,
            comments=comment_serializers,
            published=post.published,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )

        # Full dump includes computed fields
        result = serializer.dump()

        assert result["title"] == "Detailed Post"
        assert result["author"]["name"] == "DetailAuthor"
        assert len(result["tags"]) == 2
        assert len(result["comments"]) == 1
        # Computed fields are included in full dump
        assert result["tag_names"] == ["detail-tag-1", "detail-tag-2"]
        assert result["comment_count"] == 1

        # use("admin") filters to admin field_set only - computed fields must be
        # explicitly included in the field_set to appear in output
        admin_result = BlogPostSerializer.use("admin").dump(serializer)
        assert "title" in admin_result
        assert "comments" in admin_result

    @pytest.mark.django_db
    def test_one_serializer_multiple_views_pattern(self):
        """Test the DRF-replacement pattern: one serializer, multiple views."""
        # Create user
        user = User.objects.create(
            username="multiview",
            email="multi@example.com",
            password_hash="secret_hash",
            is_staff=True,
        )

        full_serializer = UserSerializer.from_model(user)

        # List view - minimal
        list_result = UserSerializer.use("list").dump(full_serializer)
        assert set(list_result.keys()) == {"id", "username", "is_active"}

        # Detail view - more info
        detail_result = UserSerializer.use("detail").dump(full_serializer)
        assert "email" in detail_result
        assert "password_hash" not in detail_result  # write_only

        # Admin view - all allowed fields
        admin_result = UserSerializer.use("admin").dump(full_serializer)
        assert "is_staff" in admin_result
        assert "password_hash" not in admin_result

        # Custom subset for public API
        UserPublic = UserSerializer.subset("id", "username", "display_name")
        public_user = UserPublic.from_parent(full_serializer)
        public_result = public_user.dump()
        assert public_result == {
            "id": user.id,
            "username": "multiview",
            "display_name": "@multiview",
        }

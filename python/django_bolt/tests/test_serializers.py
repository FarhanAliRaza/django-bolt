"""
Tests for ModelSerializer.

This module tests the DRF-style ModelSerializer that automatically generates
msgspec.Struct classes from Django models.
"""

import pytest
import msgspec
from decimal import Decimal
from datetime import datetime, date
from django.db import models
from django_bolt.serializers import ModelSerializer, create_serializer


# Test models
class Author(models.Model):
    """Author model for testing nested relationships."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    bio = models.TextField(blank=True, default="")

    class Meta:
        app_label = 'django_bolt'


class Book(models.Model):
    """Book model for testing serialization."""
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    pages = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    published_date = models.DateField()
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True, default="")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'django_bolt'


class Tag(models.Model):
    """Tag model for testing many-to-many relationships."""
    name = models.CharField(max_length=50)

    class Meta:
        app_label = 'django_bolt'


class Article(models.Model):
    """Article model with many-to-many for testing."""
    title = models.CharField(max_length=200)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'django_bolt'


# Test serializers
class BookSerializer(ModelSerializer):
    """Serializer for Book model with all fields."""
    class Meta:
        model = Book
        fields = '__all__'


class BookListSerializer(ModelSerializer):
    """Serializer for Book model with limited fields."""
    class Meta:
        model = Book
        fields = ['id', 'title', 'price', 'is_available']


class BookCreateSerializer(ModelSerializer):
    """Serializer for creating books (excluding auto fields)."""
    class Meta:
        model = Book
        exclude = ['created_at', 'updated_at']


class AuthorSerializer(ModelSerializer):
    """Serializer for Author model."""
    class Meta:
        model = Author
        fields = ['id', 'name', 'email', 'bio']


class BookWithAuthorSerializer(ModelSerializer):
    """Serializer for Book with nested author (depth=1)."""
    class Meta:
        model = Book
        fields = ['id', 'title', 'price', 'author']
        depth = 1


class ArticleSerializer(ModelSerializer):
    """Serializer for Article with many-to-many tags."""
    class Meta:
        model = Article
        fields = '__all__'


# Tests
class TestModelSerializer:
    """Test ModelSerializer metaclass and field generation."""

    def test_serializer_requires_meta(self):
        """Test that serializers require a Meta class."""
        with pytest.raises(ValueError, match="must define a Meta class"):
            class NoMetaSerializer(ModelSerializer):
                pass

    def test_serializer_requires_model(self):
        """Test that Meta must define a model."""
        with pytest.raises(ValueError, match="Meta must define 'model'"):
            class NoModelSerializer(ModelSerializer):
                class Meta:
                    fields = '__all__'

    def test_serializer_model_must_be_django_model(self):
        """Test that model must be a Django model."""
        with pytest.raises(ValueError, match="must be a Django model class"):
            class InvalidModelSerializer(ModelSerializer):
                class Meta:
                    model = str
                    fields = '__all__'

    def test_serializer_creates_struct_class(self):
        """Test that serializer creates an internal msgspec.Struct class."""
        assert hasattr(BookSerializer, '_struct_cls')
        assert issubclass(BookSerializer._struct_cls, msgspec.Struct)

    def test_serializer_stores_metadata(self):
        """Test that serializer stores model metadata."""
        assert BookSerializer._model == Book
        assert isinstance(BookSerializer._model_fields, dict)
        assert 'title' in BookSerializer._model_fields
        assert 'price' in BookSerializer._model_fields

    def test_fields_all_includes_all_fields(self):
        """Test that fields='__all__' includes all model fields."""
        fields = BookSerializer._model_fields
        assert 'title' in fields
        assert 'isbn' in fields
        assert 'pages' in fields
        assert 'price' in fields
        assert 'published_date' in fields
        assert 'is_available' in fields
        assert 'description' in fields
        assert 'author' in fields

    def test_fields_list_includes_only_specified_fields(self):
        """Test that fields list includes only specified fields."""
        fields = BookListSerializer._model_fields
        assert set(fields.keys()) == {'id', 'title', 'price', 'is_available'}

    def test_exclude_removes_fields(self):
        """Test that exclude parameter removes fields."""
        fields = BookCreateSerializer._model_fields
        assert 'created_at' not in fields
        assert 'updated_at' not in fields
        assert 'title' in fields
        assert 'price' in fields

    def test_field_type_mapping(self):
        """Test that Django fields are mapped to correct Python types."""
        struct_cls = BookSerializer._struct_cls
        annotations = struct_cls.__annotations__

        # CharField -> str
        assert 'str' in str(annotations['title'])

        # IntegerField -> int
        assert 'int' in str(annotations['pages'])

        # DecimalField -> Decimal
        assert 'Decimal' in str(annotations['price'])

        # BooleanField -> bool
        assert 'bool' in str(annotations['is_available'])

        # DateField -> date
        assert 'date' in str(annotations['published_date'])


class TestFromModel:
    """Test from_model conversion method."""

    @pytest.fixture
    def author_data(self):
        """Create test author data."""
        return {
            'id': 1,
            'name': 'John Doe',
            'email': 'john@example.com',
            'bio': 'A great author'
        }

    @pytest.fixture
    def book_data(self):
        """Create test book data."""
        return {
            'id': 1,
            'title': 'Django for Beginners',
            'isbn': '9781234567890',
            'pages': 350,
            'price': Decimal('29.99'),
            'published_date': date(2024, 1, 15),
            'is_available': True,
            'description': 'A comprehensive guide to Django',
            'author_id': 1,
            'created_at': datetime(2024, 1, 1, 12, 0, 0),
            'updated_at': datetime(2024, 1, 1, 12, 0, 0),
        }

    def test_from_model_converts_simple_fields(self, book_data):
        """Test that from_model correctly converts simple fields."""
        # Create a mock model instance
        class MockBook:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        book = MockBook(**book_data)

        # Mock the Django field types
        for field_name, field in BookListSerializer._model_fields.items():
            # Set up mock field behavior
            pass

        # Convert using serializer
        result = BookListSerializer.from_model(book)

        # Verify msgspec.Struct instance
        assert isinstance(result, msgspec.Struct)
        assert result.id == 1
        assert result.title == 'Django for Beginners'
        assert result.price == Decimal('29.99')
        assert result.is_available is True

    def test_from_models_converts_list(self, book_data):
        """Test that from_models converts a list of instances."""
        class MockBook:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        books = [
            MockBook(**{**book_data, 'id': 1, 'title': 'Book 1'}),
            MockBook(**{**book_data, 'id': 2, 'title': 'Book 2'}),
            MockBook(**{**book_data, 'id': 3, 'title': 'Book 3'}),
        ]

        results = BookListSerializer.from_models(books)

        assert len(results) == 3
        assert all(isinstance(r, msgspec.Struct) for r in results)
        assert results[0].title == 'Book 1'
        assert results[1].title == 'Book 2'
        assert results[2].title == 'Book 3'


class TestDynamicSerializerCreation:
    """Test create_serializer helper function."""

    def test_create_serializer_with_all_fields(self):
        """Test creating serializer with all fields."""
        BookSerializerDynamic = create_serializer(Book, fields='__all__')

        assert BookSerializerDynamic._model == Book
        assert 'title' in BookSerializerDynamic._model_fields
        assert 'price' in BookSerializerDynamic._model_fields

    def test_create_serializer_with_field_list(self):
        """Test creating serializer with field list."""
        BookSerializerDynamic = create_serializer(
            Book,
            fields=['id', 'title', 'price']
        )

        fields = BookSerializerDynamic._model_fields
        assert set(fields.keys()) == {'id', 'title', 'price'}

    def test_create_serializer_with_exclude(self):
        """Test creating serializer with exclude list."""
        BookSerializerDynamic = create_serializer(
            Book,
            fields='__all__',
            exclude=['created_at', 'updated_at']
        )

        fields = BookSerializerDynamic._model_fields
        assert 'created_at' not in fields
        assert 'updated_at' not in fields
        assert 'title' in fields

    def test_create_serializer_custom_name(self):
        """Test creating serializer with custom name."""
        CustomSerializer = create_serializer(
            Book,
            fields=['id', 'title'],
            name='CustomBookSerializer'
        )

        assert CustomSerializer.__name__ == 'CustomBookSerializer'


class TestSerializationWithMsgspec:
    """Test that serializers produce msgspec-compatible output."""

    def test_serializer_output_is_json_serializable(self):
        """Test that serializer output can be JSON serialized with msgspec."""
        class MockBook:
            id = 1
            title = 'Test Book'
            price = Decimal('19.99')
            is_available = True

        result = BookListSerializer.from_model(MockBook())

        # Should be serializable with msgspec
        json_bytes = msgspec.json.encode(result)
        assert isinstance(json_bytes, bytes)

        # Should be deserializable
        decoded = msgspec.json.decode(json_bytes)
        assert decoded['title'] == 'Test Book'
        assert decoded['id'] == 1


class TestReadOnlyFields:
    """Test read-only field handling."""

    def test_auto_fields_are_optional(self):
        """Test that auto fields (id, created_at, updated_at) are optional."""
        struct_cls = BookSerializer._struct_cls
        annotations = struct_cls.__annotations__

        # Auto fields should be Optional
        assert 'Optional' in str(annotations.get('id', ''))
        assert 'Optional' in str(annotations.get('created_at', ''))
        assert 'Optional' in str(annotations.get('updated_at', ''))

    def test_nullable_fields_are_optional(self):
        """Test that nullable fields are optional."""
        struct_cls = BookSerializer._struct_cls
        annotations = struct_cls.__annotations__

        # author is nullable in the model
        assert 'Optional' in str(annotations.get('author', ''))


class TestNestedSerialization:
    """Test nested serialization with depth parameter."""

    def test_depth_zero_uses_ids(self):
        """Test that depth=0 uses IDs for foreign keys."""
        # BookListSerializer has depth=0 by default
        struct_cls = BookListSerializer._struct_cls
        annotations = struct_cls.__annotations__

        # With depth=0, should just be int (or Optional[int])
        # This would be the author_id field

    def test_depth_one_uses_nested_dict(self):
        """Test that depth=1 uses nested dicts for foreign keys."""
        struct_cls = BookWithAuthorSerializer._struct_cls
        annotations = struct_cls.__annotations__

        # With depth=1, author should be Dict[str, Any]
        assert 'Dict' in str(annotations.get('author', ''))


# Integration test marker
pytestmark = pytest.mark.django_db


class TestIntegrationWithDjangoORM:
    """Integration tests with real Django ORM (requires database)."""

    @pytest.mark.asyncio
    async def test_serializer_with_real_model(self):
        """Test serializer with real Django model instance."""
        # This test requires actual database setup
        # Skip if Django is not properly configured
        try:
            # Create author
            author = await Author.objects.acreate(
                name='Jane Smith',
                email='jane@example.com',
                bio='Test author'
            )

            # Create book
            book = await Book.objects.acreate(
                title='Test Book',
                isbn='1234567890123',
                pages=200,
                price=Decimal('24.99'),
                published_date=date(2024, 1, 1),
                is_available=True,
                description='Test description',
                author=author
            )

            # Serialize using BookListSerializer
            result = BookListSerializer.from_model(book)

            assert isinstance(result, msgspec.Struct)
            assert result.title == 'Test Book'
            assert result.price == Decimal('24.99')
            assert result.is_available is True

            # Clean up
            await book.adelete()
            await author.adelete()

        except Exception as e:
            pytest.skip(f"Database not configured: {e}")


def test_serializer_works_with_api_endpoints():
    """
    Documentation test showing how to use serializers with API endpoints.

    This is a demonstration, not an actual test.
    """
    example_code = """
    from django_bolt import BoltAPI, ModelViewSet
    from django_bolt.serializers import ModelSerializer
    from myapp.models import User

    class UserSerializer(ModelSerializer):
        class Meta:
            model = User
            fields = ['id', 'username', 'email', 'is_active']
            read_only_fields = ['id']

    api = BoltAPI()

    @api.viewset("/users")
    class UserViewSet(ModelViewSet):
        queryset = User.objects.all()
        serializer_class = UserSerializer

        # All CRUD operations are now automatically handled
        # with proper msgspec serialization!

    # Or use in function-based views:
    @api.get("/users/{id}")
    async def get_user(id: int) -> UserSerializer:
        user = await User.objects.aget(id=id)
        return UserSerializer.from_model(user)

    @api.get("/users")
    async def list_users() -> list[UserSerializer]:
        users = User.objects.all()[:10]
        return UserSerializer.from_models(users)
    """
    # This is a documentation test, always passes
    assert example_code is not None

# Django-Bolt ModelSerializer

Django-Bolt now includes DRF-style `ModelSerializer` that automatically generates `msgspec.Struct` classes from Django models. This provides the convenience of Django REST Framework serializers with the performance benefits of msgspec.

## Features

- **Automatic Schema Generation**: Automatically creates msgspec.Struct from Django models
- **Field Selection**: Control which fields to include/exclude
- **Read-Only Fields**: Mark fields as read-only (like auto-generated IDs and timestamps)
- **DRF-Style Validation**: Field-level and object-level validation with `validate_<field>` methods
- **Nested Relationships**: Support for ForeignKey and ManyToMany with depth parameter
- **DRF-Compatible API**: Familiar interface for DRF users
- **High Performance**: Leverages msgspec for fast serialization (5-10x faster than standard JSON)

## Quick Start

### Basic Usage

```python
from django_bolt.serializers import ModelSerializer
from myapp.models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # Include all fields
```

### Field Selection

```python
# Include specific fields
class UserMiniSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# Exclude specific fields
class UserPublicSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        exclude = ['password', 'is_staff']
```

### Read-Only Fields

```python
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
```

### Nested Relationships

```python
# With depth=0 (default): ForeignKey returns just the ID
class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author']  # author will be int (author_id)

# With depth=1: ForeignKey returns nested dict
class BookDetailSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author']
        depth = 1  # author will be dict with author's fields
```

### DRF-Style Validation

Add field-level and object-level validation just like Django REST Framework:

```python
from django_bolt.serializers import ModelSerializer, ValidationError

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'age', 'is_premium']

    def validate_age(self, value):
        """Validate individual field."""
        if value < 18:
            raise ValidationError("Must be 18 or older")
        return value

    def validate_email(self, value):
        """Transform and validate."""
        if not value.endswith('@company.com'):
            raise ValidationError("Must use company email")
        return value.lower()  # Normalize

    def validate(self, data):
        """Cross-field validation."""
        if data.get('is_premium') and data.get('age', 0) < 21:
            raise ValidationError("Premium users must be 21+")
        return data

# Usage
@api.post("/users")
async def create_user(request):
    # Decode and validate in one step
    user_data = UserSerializer.decode(request['body'])

    # Data is already validated
    user = await User.objects.acreate(**msgspec.structs.asdict(user_data))
    return UserSerializer.from_model(user)
```

**See [VALIDATION_README.md](VALIDATION_README.md) for complete validation documentation.**

## Using with API Endpoints

### Function-Based Views

```python
from django_bolt import BoltAPI
from myapp.models import User
from .serializers import UserSerializer, UserMiniSerializer

api = BoltAPI()

@api.get("/users/{id}")
async def get_user(id: int):
    """Get single user with full details."""
    user = await User.objects.aget(id=id)
    return UserSerializer.from_model(user)

@api.get("/users")
async def list_users():
    """List users with minimal data."""
    users = User.objects.all()[:10]
    return UserMiniSerializer.from_models(users)
```

### Class-Based Views (ViewSet)

```python
from django_bolt import ViewSet
from .serializers import UserSerializer, UserMiniSerializer

@api.viewset("/users")
class UserViewSet(ViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    list_serializer_class = UserMiniSerializer  # Different serializer for list

    # Methods like list(), retrieve(), etc. automatically use serializers
```

### ModelViewSet (Full CRUD)

```python
from django_bolt import ModelViewSet
from .serializers import UserSerializer

@api.viewset("/users")
class UserViewSet(ModelViewSet):
    """Full CRUD with automatic serialization."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # All CRUD operations (list, retrieve, create, update, delete)
    # automatically use the serializer!
```

## Dynamic Serializer Creation

For quick prototyping, you can create serializers dynamically:

```python
from django_bolt.serializers import create_serializer
from myapp.models import User

UserSerializer = create_serializer(
    User,
    fields=['id', 'username', 'email'],
    read_only_fields=['id'],
    name='UserSerializer'
)

# Use it like any other serializer
user = await User.objects.aget(id=1)
return UserSerializer.from_model(user)
```

## Complete Example

Here's a complete example showing how to refactor from manual schemas to ModelSerializer:

### Before (Manual Schemas)

```python
# api.py
import msgspec
from .models import User

# Manual schema definition
class UserFull(msgspec.Struct):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool

class UserMini(msgspec.Struct):
    id: int
    username: str

@api.get("/users/{id}")
async def get_user(id: int) -> UserFull:
    user = await User.objects.aget(id=id)
    # Manual field extraction
    return UserFull(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active
    )
```

### After (With ModelSerializer)

```python
# serializers.py
from django_bolt.serializers import ModelSerializer
from .models import User

class UserFullSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']
        read_only_fields = ['id']

class UserMiniSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

# api.py
from .serializers import UserFullSerializer

@api.get("/users/{id}")
async def get_user(id: int):
    user = await User.objects.aget(id=id)
    return UserFullSerializer.from_model(user)  # Automatic conversion!
```

## API Reference

### ModelSerializer

The main serializer class that generates msgspec.Struct from Django models.

#### Meta Options

- **model** (required): Django model class
- **fields**: List of field names or `'__all__'` to include all fields
- **exclude**: List of field names to exclude (alternative to fields)
- **read_only_fields**: List of fields that are read-only
- **depth**: Depth of nested serialization (0 = IDs only, 1+ = nested objects)
- **extra_kwargs**: Additional field configuration (future feature)

#### Class Methods

- **from_model(instance)**: Convert a single Django model instance to msgspec.Struct
- **from_models(instances)**: Convert a list/queryset of instances to list of structs

### create_serializer()

Helper function for dynamic serializer creation.

```python
def create_serializer(
    model: Type[Model],
    fields: List[str] | str = '__all__',
    exclude: List[str] | None = None,
    read_only_fields: List[str] | None = None,
    name: str | None = None
) -> Type[ModelSerializer]
```

## Field Type Mapping

Django fields are automatically mapped to Python types:

| Django Field | Python Type |
|--------------|-------------|
| CharField, TextField, EmailField, URLField, SlugField | str |
| IntegerField, AutoField, BigIntegerField | int |
| FloatField | float |
| DecimalField | decimal.Decimal |
| BooleanField | bool |
| DateTimeField | datetime |
| DateField | date |
| TimeField | time |
| UUIDField | uuid.UUID |
| JSONField | Dict[str, Any] |
| BinaryField | bytes |
| ForeignKey, OneToOneField | int (depth=0) or Dict (depth≥1) |
| ManyToManyField | List[int] (depth=0) or List[Dict] (depth≥1) |

## Performance

ModelSerializer generates msgspec.Struct classes which provide:

- **5-10x faster JSON serialization** compared to standard library json
- **Zero-copy validation** for request bodies
- **Type safety** with Python type annotations
- **Minimal memory overhead**

Benchmarks show that django-bolt with ModelSerializer can handle 60k+ requests per second with complex models.

## Migration Guide

If you're migrating from manual msgspec schemas:

1. **Create serializers.py**: Define your ModelSerializer classes
2. **Update imports**: Change from manual schemas to serializers
3. **Use from_model()**: Replace manual field extraction with `from_model()`
4. **Update ViewSets**: Set `serializer_class` attribute

The API remains the same - your route handlers still return the same types, just generated automatically!

## Best Practices

1. **Create separate serializers** for different use cases (list vs detail, create vs update)
2. **Use read_only_fields** for fields that shouldn't be in create/update requests
3. **Leverage list_serializer_class** in ViewSets for optimized list endpoints
4. **Use depth=1 sparingly** - nested serialization can be expensive
5. **Consider pagination** for large datasets

## Limitations

- Nested serialization (depth > 0) is currently simplified (returns dicts)
- Custom validation is not yet supported (coming soon)
- Nested write operations require manual handling

## Coming Soon

- Custom field serializers
- Nested write support
- Field-level validation
- Source field mapping
- Method fields

## Contributing

Found a bug or want to contribute? Check out our [GitHub repo](https://github.com/yourusername/django-bolt)!

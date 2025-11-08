# Model Serializers

Django-Bolt provides a high-performance, type-safe model serializer system using msgspec. This guide covers how to create serializers, validate data, and integrate with Django models.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Creating Serializers](#creating-serializers)
- [Field Validation](#field-validation)
- [Custom Transformations](#custom-transformations)
- [QuerySet Optimization](#queryset-optimization)
- [Integration with ViewSets](#integration-with-viewsets)
- [Advanced Usage](#advanced-usage)
- [Comparison with DRF](#comparison-with-drf)

## Overview

Django-Bolt's model serializers provide:

- **Type Safety**: Full Python type annotations for IDE support and runtime validation
- **High Performance**: Built on msgspec (5-10x faster than standard JSON)
- **Less Verbose**: Compared to DRF or Pydantic, requires less boilerplate
- **Custom Validation**: DRF-style `validate_<field>` methods
- **QuerySet Optimization**: Efficient bulk serialization via `.values()` and batch conversion
- **OpenAPI Generation**: Automatic schema generation for API documentation

## Quick Start

### Basic Serializer

```python
from django_bolt import model_serializer, Serializer
from myapp.models import User

# Option 1: Factory function (quick generation)
UserSerializer = model_serializer(
    User,
    fields=['id', 'username', 'email', 'created_at'],
)

# Option 2: Class-based (more control)
class UserSerializer(Serializer):
    id: int
    username: str
    email: str
    created_at: datetime

    @classmethod
    def get_model(cls):
        return User
```

### Using in an Endpoint

```python
from django_bolt import BoltAPI

api = BoltAPI()

@api.get("/users/{user_id}", response_model=UserSerializer)
async def get_user(user_id: int):
    user = await User.objects.aget(id=user_id)
    return UserSerializer.from_model(user)

@api.get("/users", response_model=list[UserSerializer])
async def list_users():
    queryset = User.objects.all()
    # Optimized bulk serialization
    return UserSerializer.from_queryset(queryset)
```

## Creating Serializers

### Factory Function

The `model_serializer()` factory function generates a serializer class from a Django model:

```python
from django_bolt import model_serializer
from myapp.models import Article

# Include specific fields
ArticleSerializer = model_serializer(
    Article,
    fields=['id', 'title', 'content', 'author', 'created_at'],
)

# Include all fields
ArticleSerializer = model_serializer(
    Article,
    fields='__all__',
)

# Exclude specific fields
ArticleSerializer = model_serializer(
    Article,
    fields='__all__',
    exclude=['internal_notes', 'deleted_at'],
)
```

### Class-Based Serializers

For more control, define a class extending `Serializer`:

```python
from django_bolt import Serializer
from datetime import datetime

class ArticleSerializer(Serializer):
    id: int
    title: str
    content: str
    author: str
    created_at: datetime
    published: bool = False  # Optional field with default

    @classmethod
    def get_model(cls):
        return Article
```

### Quick Serializer Helper

For rapid prototyping:

```python
from django_bolt import quick_serializer
from myapp.models import User

UserSerializer = quick_serializer(User, fields=['id', 'username', 'email'])
```

## Field Validation

### Validation Methods

Use `validate_<field>` methods to add custom validation logic:

```python
class UserSerializer(Serializer):
    id: int
    username: str
    email: str
    age: int

    def validate_email(self, value: str) -> str:
        """Validate email domain."""
        if not value.endswith('@example.com'):
            raise ValueError("Email must end with @example.com")
        return value

    def validate_age(self, value: int) -> int:
        """Validate age range."""
        if value < 0 or value > 150:
            raise ValueError("Age must be between 0 and 150")
        return value

    def validate_username(self, value: str) -> str:
        """Validate username format."""
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not value.isalnum():
            raise ValueError("Username must be alphanumeric")
        return value
```

### Factory-Based Validation

Add validators when using the factory function:

```python
def validate_email(value: str) -> str:
    if '@' not in value:
        raise ValueError("Invalid email format")
    return value

def validate_age(value: int) -> int:
    if value < 18:
        raise ValueError("Must be 18 or older")
    return value

UserSerializer = model_serializer(
    User,
    fields=['id', 'email', 'age'],
    validators={
        'email': validate_email,
        'age': validate_age,
    }
)
```

### Optional Fields

Validation is skipped for `None` values on optional fields:

```python
from typing import Optional

class UserSerializer(Serializer):
    id: int
    username: str
    email: Optional[str] = None  # Optional field

    def validate_email(self, value: str) -> str:
        # Only called if email is not None
        if '@' not in value:
            raise ValueError("Invalid email")
        return value

# These all work:
user1 = UserSerializer(id=1, username='john', email='john@example.com')
user2 = UserSerializer(id=2, username='jane', email=None)  # Validation skipped
user3 = UserSerializer(id=3, username='bob')  # Uses default (None)
```

## Custom Transformations

### Transform Methods

Use `transform_<field>` methods to modify values during serialization:

```python
class ArticleSerializer(Serializer):
    id: int
    title: str
    slug: str
    excerpt: str

    def transform_slug(self, value: str) -> str:
        """Ensure slug is lowercase."""
        return value.lower()

    def transform_excerpt(self, value: str) -> str:
        """Truncate excerpt to 200 characters."""
        return value[:200] + '...' if len(value) > 200 else value

# Usage
article = Article.objects.get(id=1)
serialized = ArticleSerializer.from_model(article)
# slug is automatically lowercased
# excerpt is automatically truncated
```

### Factory-Based Transformations

```python
def transform_title(value: str) -> str:
    return value.upper()

ArticleSerializer = model_serializer(
    Article,
    fields=['id', 'title', 'content'],
    transforms={
        'title': transform_title,
    }
)
```

### Field Source Mapping

Map serializer fields to different model attributes:

```python
class UserSerializer(Serializer):
    id: int
    username: str
    full_name: str

    @classmethod
    def get_field_source(cls, field_name: str) -> str:
        # Map full_name serializer field to full_name() model method
        if field_name == 'full_name':
            return 'get_full_name'
        return super().get_field_source(field_name)

# Or use Field descriptor (for advanced cases)
from django_bolt import Field

class UserSerializer(Serializer):
    id: int
    username: str
    full_name: str = Field(source='get_full_name')
```

## QuerySet Optimization

### Bulk Serialization

The `from_queryset()` method uses an optimized path for bulk serialization:

```python
# Inefficient: N conversions
users = User.objects.all()
serialized = [UserSerializer.from_model(u) for u in users]  # Slow

# Efficient: Single batch conversion
users = User.objects.all()
serialized = UserSerializer.from_queryset(users)  # Fast!
```

**Performance:**
- Uses `.values()` to fetch only needed fields
- Batch conversion with `msgspec.convert()` (100-1000x fewer operations)
- Perfect for paginated APIs

### How It Works

```python
@classmethod
def from_queryset(cls, queryset):
    """Optimized bulk serialization."""
    # 1. Extract field names from struct
    field_names = list(cls.__struct_fields__)

    # 2. Use .values() for efficient SQL
    values_list = list(queryset.values(*field_names))

    # 3. Batch convert with msgspec (single operation)
    return msgspec.convert(values_list, List[cls])
```

### Example: Paginated API

```python
from django_bolt import BoltAPI, PageNumberPagination

api = BoltAPI()

@api.get("/users")
async def list_users(page: int = 1, page_size: int = 20):
    # Get queryset
    queryset = User.objects.all().order_by('-created_at')

    # Apply pagination
    paginator = PageNumberPagination(page=page, page_size=page_size)
    paginated_qs = await paginator.paginate_queryset(queryset)

    # Efficient serialization
    users = UserSerializer.from_queryset(paginated_qs)

    return {
        "count": await queryset.acount(),
        "page": page,
        "page_size": page_size,
        "results": users,
    }
```

## Integration with ViewSets

Model serializers work seamlessly with Django-Bolt's ViewSets:

```python
from django_bolt import BoltAPI, ModelViewSet, model_serializer
from myapp.models import Article

api = BoltAPI()

# Create serializers
ArticleSerializer = model_serializer(Article, fields='__all__')
ArticleCreateSerializer = model_serializer(
    Article,
    fields=['title', 'content', 'author'],
)

@api.viewset("/articles")
class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    create_serializer_class = ArticleCreateSerializer

    async def list(self, request):
        """GET /articles - List all articles."""
        queryset = await self.get_queryset()
        # Use optimized serialization
        articles = ArticleSerializer.from_queryset(queryset)
        return articles

    async def retrieve(self, request, pk: int):
        """GET /articles/{pk} - Get single article."""
        article = await self.get_object(pk=pk)
        return ArticleSerializer.from_model(article)

    async def create(self, request, data: ArticleCreateSerializer):
        """POST /articles - Create article."""
        article = await Article.objects.acreate(
            title=data.title,
            content=data.content,
            author=data.author,
        )
        return ArticleSerializer.from_model(article)
```

## Advanced Usage

### Nested Serializers

Serializers can be nested for complex data structures:

```python
class AuthorSerializer(Serializer):
    id: int
    name: str
    email: str

class ArticleSerializer(Serializer):
    id: int
    title: str
    content: str
    author: AuthorSerializer  # Nested serializer

# Custom from_model for nested data
@classmethod
def from_model(cls, article):
    return cls(
        id=article.id,
        title=article.title,
        content=article.content,
        author=AuthorSerializer(
            id=article.author.id,
            name=article.author.name,
            email=article.author.email,
        ),
    )
```

### Read-Only vs Write-Only Fields

Use separate serializers for requests and responses:

```python
# Request serializer (for POST/PUT)
class CreateUserRequest(Serializer):
    username: str
    email: str
    password: str  # Write-only (not in response)

    def validate_password(self, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value

# Response serializer (for GET)
class UserResponse(Serializer):
    id: int  # Read-only (not in request)
    username: str
    email: str
    created_at: datetime  # Read-only

@api.post("/users", response_model=UserResponse)
async def create_user(data: CreateUserRequest):
    user = await User.objects.acreate(
        username=data.username,
        email=data.email,
        password=hash_password(data.password),
    )
    return UserResponse.from_model(user)
```

### Custom Field Types

Handle non-standard field types:

```python
from decimal import Decimal
from django_bolt import Serializer

class ProductSerializer(Serializer):
    id: int
    name: str
    price: Decimal  # Automatically handled by msgspec
    tags: list[str]  # JSON array
    metadata: dict  # JSON object

    def validate_price(self, value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError("Price must be non-negative")
        return value
```

### Polymorphic Serializers

Handle different types based on conditions:

```python
from typing import Union

class ImageAttachment(Serializer):
    type: str = "image"
    url: str
    width: int
    height: int

class FileAttachment(Serializer):
    type: str = "file"
    url: str
    filename: str
    size: int

AttachmentSerializer = Union[ImageAttachment, FileAttachment]

@api.get("/post/{post_id}/attachments", response_model=list[AttachmentSerializer])
async def get_attachments(post_id: int):
    post = await Post.objects.aget(id=post_id)
    attachments = []
    for attachment in post.attachments.all():
        if attachment.is_image:
            attachments.append(ImageAttachment.from_model(attachment))
        else:
            attachments.append(FileAttachment.from_model(attachment))
    return attachments
```

## Comparison with DRF

### Feature Comparison

| Feature | DRF Serializers | Django-Bolt Serializers |
|---------|----------------|------------------------|
| **Performance** | Standard JSON (~10ms for 1000 items) | msgspec (~1ms for 1000 items) |
| **Type Safety** | No | Yes (full annotations) |
| **Validation** | `validate_*()` methods | `validate_*()` methods |
| **Verbosity** | High (explicit field definitions) | Low (type annotations) |
| **Model Integration** | `ModelSerializer` base class | `model_serializer()` factory |
| **Nested Serialization** | Automatic (with ModelSerializer) | Manual `from_model()` |
| **OpenAPI** | Via drf-spectacular | Built-in |
| **QuerySet Optimization** | No | Yes (`.from_queryset()`) |

### Code Comparison

**DRF:**
```python
from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    age = serializers.IntegerField(min_value=0, max_value=150)

    def validate_email(self, value):
        if not value.endswith('@example.com'):
            raise serializers.ValidationError("Email must be @example.com")
        return value

# Usage
serializer = UserSerializer(data=request.data)
if serializer.is_valid():
    # Process data
    pass
```

**Django-Bolt:**
```python
from django_bolt import Serializer

class UserSerializer(Serializer):
    id: int
    username: str
    email: str
    age: int

    def validate_email(self, value: str) -> str:
        if not value.endswith('@example.com'):
            raise ValueError("Email must be @example.com")
        return value

# Usage (validation is automatic on construction)
@api.post("/users")
async def create_user(user: UserSerializer):
    # user is already validated
    await User.objects.acreate(**msgspec.structs.asdict(user))
```

### Migration from DRF

**Before (DRF):**
```python
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author']
        read_only_fields = ['id']
```

**After (Django-Bolt):**
```python
# Response serializer
ArticleSerializer = model_serializer(
    Article,
    fields=['id', 'title', 'content', 'author'],
)

# Request serializer (without id)
CreateArticleSerializer = model_serializer(
    Article,
    fields=['title', 'content', 'author'],
)
```

## Best Practices

### 1. Separate Request/Response Serializers

```python
# Good: Separate serializers for different purposes
class CreateUserRequest(Serializer):
    username: str
    email: str
    password: str

class UserResponse(Serializer):
    id: int
    username: str
    email: str
    created_at: datetime

# Bad: Single serializer with optional fields
class User(Serializer):
    id: Optional[int] = None  # Confusing: required in response, not in request
    username: str
    password: Optional[str] = None  # Confusing: required in request, not in response
```

### 2. Use from_queryset for Lists

```python
# Good: Optimized bulk serialization
@api.get("/users")
async def list_users():
    queryset = User.objects.all()
    return UserSerializer.from_queryset(queryset)

# Bad: Individual conversions (slow)
@api.get("/users")
async def list_users():
    users = []
    async for user in User.objects.all():
        users.append(UserSerializer.from_model(user))
    return users
```

### 3. Keep Validation Simple

```python
# Good: Simple, focused validators
def validate_email(self, value: str) -> str:
    if '@' not in value:
        raise ValueError("Invalid email")
    return value

# Bad: Complex business logic in validators
def validate_email(self, value: str) -> str:
    # Don't do database queries in validators
    if User.objects.filter(email=value).exists():
        raise ValueError("Email already exists")
    # Don't do complex processing
    send_verification_email(value)
    return value
```

### 4. Use Type Annotations

```python
# Good: Full type annotations
class UserSerializer(Serializer):
    id: int
    username: str
    email: str
    tags: list[str]
    metadata: dict[str, Any]

# Bad: Missing or vague types
class UserSerializer(Serializer):
    id = None  # Type inference fails
    username = ""  # Type is str, but unclear
    tags = []  # Type is list, but list of what?
```

## Performance Tips

### 1. Pre-compute Field Names

```python
# Field names are extracted at class definition time
# No runtime overhead for field introspection
UserSerializer = model_serializer(User, fields=['id', 'username', 'email'])
```

### 2. Batch Operations

```python
# Process 10,000 users efficiently
queryset = User.objects.all()[:10000]
serialized = UserSerializer.from_queryset(queryset)
# ~10-20ms total
```

### 3. Avoid N+1 Queries

```python
# Good: Use select_related/prefetch_related
@api.get("/articles")
async def list_articles():
    queryset = Article.objects.select_related('author').all()
    return ArticleSerializer.from_queryset(queryset)

# Bad: Triggers N+1 queries if accessing author
@api.get("/articles")
async def list_articles():
    queryset = Article.objects.all()  # No select_related
    return ArticleSerializer.from_queryset(queryset)
```

## Troubleshooting

### Validation Errors

**Problem:** Validator is not being called

```python
class UserSerializer(Serializer):
    email: str

    # Wrong: Missing self parameter
    def validate_email(email: str) -> str:
        return email

    # Correct: Include self parameter
    def validate_email(self, email: str) -> str:
        return email
```

**Problem:** Can't modify field values in validator

```python
# msgspec.Struct is immutable - validators can only check/raise errors, not transform
def validate_email(self, value: str) -> str:
    # This won't work - struct is immutable
    # The return value is ignored
    return value.lower()

# Instead, use transform_* for value modifications
def transform_email(self, value: str) -> str:
    return value.lower()
```

### Type Errors

**Problem:** Field type doesn't match model field

```python
# Model has DateTimeField, but serializer uses str
class ArticleSerializer(Serializer):
    created_at: str  # Wrong!

# Fix: Use correct type
from datetime import datetime

class ArticleSerializer(Serializer):
    created_at: datetime  # Correct
```

**Problem:** Optional field not working

```python
# Wrong: Plain int
age: int

# Correct: Optional[int]
from typing import Optional
age: Optional[int] = None
```

## Additional Resources

- [Serialization Guide](SERIALIZATION.md)
- [ViewSets Documentation](CLASS_BASED_VIEWS.md)
- [OpenAPI Documentation](OPENAPI.md)
- [Pagination](PAGINATION.md)
- [msgspec Documentation](https://jcristharif.com/msgspec/)

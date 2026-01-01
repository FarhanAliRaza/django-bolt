# Serializers - Type-Safe Serialization for Django-Bolt

Django-Bolt includes an enhanced serialization system built on top of `msgspec.Struct` that provides Pydantic-like functionality with full type safety, while maintaining msgspec's superior performance (5-10x faster).

## Overview

The `Serializer` class extends `msgspec.Struct` with:

- **Field-level validation** via `@field_validator` decorator
- **Model-level validation** via `@model_validator` decorator
- **Computed fields** via `@computed_field` decorator
- **Nested serializers** with `Nested()` annotation for relationships
- **Django model integration** with `.from_model()`, `.to_dict()`, `.to_model()`
- **Dynamic field selection** with `only()`, `exclude()`, `use()` and field sets
- **Type-safe subsets** with `subset()` and `fields()` for response models
- **Async and sync support** - Works seamlessly with both `async def` and `def` handlers
- **100% type safety** - full IDE autocomplete and type checker support
- **Built-in validated types** - `Email`, `URL`, `Slug`, `PositiveInt`, `Percentage`, etc.
- **Leverage Django validators** - Use existing Django validation utilities
- **Helper functions** - Auto-generate serializers from models with `create_serializer()`

## Basic Usage

### Simple Serializer

```python
from django_bolt.serializers import Serializer, field_validator

class UserCreate(Serializer):
    username: str
    email: str
    password: str

    @field_validator('email')
    def validate_email(cls, value):
        if '@' not in value:
            raise ValueError('Invalid email address')
        return value.lower()
```

### Field Ordering (Like Pydantic/DRF)

Unlike raw msgspec, django-bolt Serializers automatically enable `kw_only=True`, so you can mix required and optional fields in any order - just like Pydantic and DRF:

```python
class UserSerializer(Serializer):
    id: int = field(read_only=True)  # Optional field
    username: str                     # Required field - OK after optional!
    email: str
    bio: str | None = None

# Must use keyword arguments for instantiation:
user = UserSerializer(username="john", email="john@example.com")
```

### Using in API Routes

```python
from django.contrib.auth.models import User
from django_bolt.api import BoltAPI

api = BoltAPI()

@api.post("/users", response_model=UserPublicSerializer)
async def create_user(data: UserCreate):
    # Validation happens automatically in __post_init__
    user = await User.objects.acreate(**data.to_dict())
    return UserPublicSerializer.from_model(user)
```

## Field Validators

Field validators allow you to validate and transform individual field values.

### Basic Field Validation

```python
class UserCreate(Serializer):
    email: str

    @field_validator('email')
    def validate_email(cls, value):
        if '@' not in value:
            raise ValueError('Invalid email')
        return value
```

### Validation with Django Validators

```python
from django.core.validators import validate_email, URLValidator

class UserCreate(Serializer):
    email: str
    website: str

    @field_validator('email')
    def validate_email_field(cls, value):
        validate_email(value)  # Use Django's validator
        return value.lower()

    @field_validator('website')
    def validate_website(cls, value):
        URLValidator()(value)  # Use Django's URL validator
        return value
```

### Field Transformation

Validators can transform values:

```python
class UserCreate(Serializer):
    username: str

    @field_validator('username')
    def normalize_username(cls, value):
        # Transform to lowercase and strip whitespace
        return value.lower().strip()
```

### Multiple Validators

Multiple validators can be applied to the same field:

```python
class UserCreate(Serializer):
    password: str

    @field_validator('password')
    def check_length(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters')
        return value

    @field_validator('password')
    def check_complexity(cls, value):
        if not any(c.isupper() for c in value):
            raise ValueError('Password must contain uppercase letter')
        return value
```

## Model Validators

Model validators run after all fields are validated and allow cross-field validation.

```python
class PasswordChangeSerializer(Serializer):
    old_password: str
    new_password: str
    new_password_confirm: str

    @model_validator
    def validate_passwords(self):
        if self.new_password != self.new_password_confirm:
            raise ValueError("New passwords don't match")
        if self.old_password == self.new_password:
            raise ValueError("New password must be different from old password")
```

## Nested Serializers

Nested serializers allow you to represent relationships between Django models with full type safety and validation.

### Basic Nested Relationships

Use `Annotated` with `Nested()` to declare nested relationships:

```python
from django_bolt.serializers import Serializer, Nested
from typing import Annotated

class AuthorSerializer(Serializer):
    id: int
    name: str
    email: str

class BlogPostSerializer(Serializer):
    id: int
    title: str
    content: str
    # Nested author - single object
    author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]
```

### Many-to-Many Relationships

For many-to-many relationships, use `Nested()` with `many=True`:

```python
class TagSerializer(Serializer):
    id: int
    name: str
    description: str = ""

class BlogPostSerializer(Serializer):
    id: int
    title: str
    # Nested tags - list of objects
    tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)]
```

### Deeply Nested Structures

You can nest serializers within nested serializers for complex relationships:

```python
class CommentSerializer(Serializer):
    id: int
    text: str
    # Nested author within comment
    author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]

class BlogPostDetailedSerializer(Serializer):
    id: int
    title: str
    content: str
    # Nested author
    author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]
    # Nested tags (many-to-many)
    tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)]
    # Nested comments, each with their own nested author
    comments: Annotated[list[CommentSerializer], Nested(CommentSerializer, many=True)]
```

### Using Nested Serializers with Django ORM

When fetching data, use `select_related()` and `prefetch_related()` to avoid N+1 queries:

```python
from django_bolt.api import BoltAPI

api = BoltAPI()

@api.get("/posts/{post_id}")
async def get_post(post_id: int):
    # Efficient query with relationships loaded
    post = await (
        BlogPost.objects
        .select_related("author")  # ForeignKey
        .prefetch_related("tags", "comments__author")  # ManyToMany and nested FK
        .aget(id=post_id)
    )
    return BlogPostDetailedSerializer.from_model(post)
```

### Nested Validation

Nested serializers are validated recursively:

```python
class AuthorSerializer(Serializer):
    id: int
    name: Annotated[str, Meta(min_length=2)]
    email: Annotated[str, Meta(pattern=r"^[^@]+@[^@]+\.[^@]+$")]

    @field_validator("email")
    def lowercase_email(cls, value: str) -> str:
        return value.lower()

class BlogPostInputSerializer(Serializer):
    title: Annotated[str, Meta(min_length=3)]
    content: Annotated[str, Meta(min_length=10)]
    # Author validation happens automatically
    author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]

# When creating a post, author email is validated and normalized
@api.post("/posts")
async def create_post(data: BlogPostInputSerializer):
    # data.author.email is already lowercased and validated
    post = await BlogPost.objects.acreate(
        title=data.title,
        content=data.content,
        author_id=data.author.id,
    )
    return BlogPostSerializer.from_model(post)
```

## Type Annotations with Constraints

Use `Annotated` with `msgspec.Meta` for field constraints:

```python
from typing import Annotated
from msgspec import Meta

class UserCreate(Serializer):
    username: Annotated[str, Meta(min_length=3, max_length=150)]
    email: str
    age: Annotated[int, Meta(ge=0, le=150)]
```

Supported constraints:

- **Strings**: `min_length`, `max_length`, `pattern` (regex)
- **Numbers**: `gt`, `ge`, `lt`, `le`, `multiple_of`
- **Collections**: `min_length`, `max_length`

## Django Model Integration

### Converting Models to Serializers

```python
class UserPublic(Serializer):
    id: int
    username: str
    email: str
    date_joined: datetime

user = await User.objects.aget(id=1)
serializer = UserPublic.from_model(user)
```

### Converting Serializers to Dicts

```python
user_data = UserCreate(username="alice", email="alice@example.com", password="secret")
data_dict = user_data.to_dict()
# {'username': 'alice', 'email': 'alice@example.com', 'password': 'secret'}

# Create Django model
user = await User.objects.acreate(**data_dict)
```

### Creating Model Instances

```python
user_data = UserCreate(username="bob", email="bob@example.com", password="secret")

# Create unsaved instance
user = user_data.to_model(User)

# Set password (required for User model)
user.set_password(user_data.password)

# Save
await user.asave()
```

### Updating Model Instances

```python
class UserUpdate(Serializer):
    username: str | None = None
    email: str | None = None

user = await User.objects.aget(id=1)
update_data = UserUpdate(email="newemail@example.com")

# Update instance
updated_user = update_data.update_instance(user)
await updated_user.asave()
```

## Helper Functions

### Auto-Generate Serializers

Create serializers directly from Django models:

```python
from django_bolt.serializers import create_serializer

UserSerializer = create_serializer(
    User,
    fields=['id', 'username', 'email', 'date_joined'],
    read_only={'id', 'date_joined'},
)
```

### Generate CRUD Serializer Set

Automatically create Create, Update, and Public serializers:

```python
from django_bolt.serializers import create_serializer_set

UserCreate, UserUpdate, UserPublic = create_serializer_set(
    User,
    create_fields=['username', 'email', 'password'],
    update_fields=['username', 'email'],
    public_fields=['id', 'username', 'email', 'date_joined'],
)
```

## Async and Sync Support

Django-Bolt serializers work seamlessly with both async and sync endpoints. The framework automatically handles the async/sync boundary.

### Async Endpoints with Async ORM

Use Django's async ORM methods (`.aget()`, `.acreate()`, `.aexists()`, etc.) in async handlers:

```python
@api.post("/auth/signup")
async def signup(data: UserSignupSerializer):
    """Async endpoint with async ORM queries."""
    # Check uniqueness asynchronously
    if await User.objects.filter(username=data.username).aexists():
        raise BadRequest(detail="Username already exists")

    if await User.objects.filter(email=data.email).aexists():
        raise BadRequest(detail="Email already exists")

    # Create user asynchronously
    user = await User.objects.acreate(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
    )

    # Serializer works the same way
    return UserSerializer.from_model(user)
```

### Sync Endpoints with Sync ORM

Traditional sync handlers work as expected:

```python
@api.get("/users/{user_id}")
def get_user(user_id: int):
    """Sync endpoint with sync ORM queries."""
    user = User.objects.get(id=user_id)
    return UserSerializer.from_model(user)
```

### Mixed Async/Sync in Same API

You can mix async and sync handlers in the same API:

```python
api = BoltAPI()

# Async handler
@api.get("/posts/{post_id}")
async def get_post_async(post_id: int):
    post = await BlogPost.objects.select_related("author").aget(id=post_id)
    return BlogPostSerializer.from_model(post)

# Sync handler
@api.get("/tags")
def list_tags():
    tags = Tag.objects.all()
    return [TagSerializer.from_model(tag) for tag in tags]
```

### Important: Prefetch for Async

When using async handlers with nested serializers, always use `prefetch_related()` to avoid sync queries:

```python
# ✅ Correct - prefetch relationships
@api.get("/posts/{post_id}")
async def get_post(post_id: int):
    post = await (
        BlogPost.objects
        .select_related("author")
        .prefetch_related("tags")  # Must prefetch for nested serializers
        .aget(id=post_id)
    )
    return BlogPostSerializer.from_model(post)

# ❌ Wrong - will cause SynchronousOnlyOperation error
@api.get("/posts/{post_id}")
async def get_post_bad(post_id: int):
    post = await BlogPost.objects.aget(id=post_id)
    # This will fail - .from_model() accesses post.tags.all() synchronously
    return BlogPostSerializer.from_model(post)
```

## Complete Example: User Authentication System

A comprehensive example demonstrating nested serializers, validation, and async/sync patterns:

```python
from django.contrib.auth.models import User
from django_bolt.api import BoltAPI
from django_bolt.serializers import Serializer, Nested, field_validator, model_validator
from django_bolt.exceptions import BadRequest
from msgspec import Meta
from typing import Annotated
import hashlib

api = BoltAPI()

# ============================================================================
# Serializers
# ============================================================================

class UserSerializer(Serializer):
    """User output serializer."""
    id: int
    username: str
    email: str
    is_active: bool = True
    is_staff: bool = False


class UserSignupSerializer(Serializer):
    """User registration with password confirmation validation."""
    username: Annotated[str, Meta(min_length=3, max_length=150)]
    email: Annotated[str, Meta(pattern=r"^[^@]+@[^@]+\.[^@]+$")]
    password: Annotated[str, Meta(min_length=8)]
    confirm_password: str

    @field_validator("username")
    def strip_username(cls, value: str) -> str:
        return value.strip()

    @field_validator("email")
    def lowercase_email(cls, value: str) -> str:
        return value.lower()

    @model_validator
    def validate_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class UserProfileSerializer(Serializer):
    """User profile with nested user data."""
    id: int
    user: Annotated[UserSerializer, Nested(UserSerializer)]
    bio: Annotated[str, Meta(max_length=500)] = ""
    avatar_url: str = ""
    phone: Annotated[str, Meta(max_length=20)] = ""
    location: Annotated[str, Meta(max_length=100)] = ""


# ============================================================================
# Helper Functions
# ============================================================================

def hash_password(password: str) -> str:
    """Simple password hashing (use bcrypt/argon2 in production)."""
    return hashlib.sha256(password.encode()).hexdigest()


# ============================================================================
# API Routes (Async Examples)
# ============================================================================

@api.post("/auth/signup")
async def signup(data: UserSignupSerializer):
    """User registration endpoint - demonstrates async ORM with validation."""
    # Check username uniqueness (async)
    if await User.objects.filter(username=data.username).aexists():
        raise BadRequest(detail="Username already exists")

    # Check email uniqueness (async)
    if await User.objects.filter(email=data.email).aexists():
        raise BadRequest(detail="Email already exists")

    # Create user (async)
    user = await User.objects.acreate(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        is_active=True,
        is_staff=False,
    )

    # Return serialized response
    return UserSerializer.from_model(user)


@api.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get user - demonstrates async ORM query."""
    user = await User.objects.aget(id=user_id)
    return UserSerializer.from_model(user)


@api.get("/profiles/{profile_id}")
async def get_profile(profile_id: int):
    """Get profile with nested user - demonstrates async with relationships."""
    # Must use select_related for nested serializers in async
    profile = await (
        UserProfile.objects
        .select_related("user")
        .aget(id=profile_id)
    )
    return UserProfileSerializer.from_model(profile)


# ============================================================================
# API Routes (Sync Examples)
# ============================================================================

@api.get("/users")
def list_users():
    """List all users - demonstrates sync ORM."""
    users = User.objects.all()
    return [UserSerializer.from_model(user) for user in users]


@api.patch("/users/{user_id}")
def update_user(user_id: int, username: str = None, email: str = None):
    """Update user - demonstrates sync ORM update."""
    user = User.objects.get(id=user_id)

    if username:
        user.username = username
    if email:
        user.email = email

    user.save()
    return UserSerializer.from_model(user)
```

## Validation Error Handling

Validation errors are raised as `msgspec.ValidationError`:

```python
from msgspec import ValidationError

try:
    user = UserCreate(username="", email="invalid", password="weak")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

Validation happens automatically during `__post_init__`, so errors are raised when creating the serializer instance.

## Meta Configuration

Configure serializer behavior via the `Meta` class:

```python
class UserSerializer(Serializer):
    username: str
    email: str

    class Config:
        model = User  # Associated Django model
        write_only = {'password'}  # Input-only fields
        read_only = {'id', 'date_joined'}  # Output-only fields
```

## Advanced Features

### Field Configuration with `field()`

Use the `field()` function for serializer-specific field behavior:

```python
from django_bolt.serializers import Serializer, field

class UserSerializer(Serializer):
    id: int = field(read_only=True)  # Only in output, not input
    email: str = field(source="email_address")  # Map to different model attribute
    password: str = field(write_only=True)  # Only in input, not output
    tags: list[str] = field(default_factory=list)  # Mutable default
```

**Available options:**

| Option               | Description                                           |
| -------------------- | ----------------------------------------------------- |
| `read_only=True`     | Field only appears in output (dump), ignored in input |
| `write_only=True`    | Field only accepted in input, excluded from output    |
| `source="attr"`      | Map API field name to different model attribute       |
| `alias="name"`       | Alternative JSON key name                             |
| `default=value`      | Default value for the field                           |
| `default_factory=fn` | Factory function for mutable defaults                 |
| `exclude=True`       | Always exclude from serialization                     |
| `description`        | Description for OpenAPI documentation                 |
| `deprecated=True`    | Mark field as deprecated in OpenAPI docs              |

**For validation constraints**, use `Meta` with `Annotated` instead:

```python
from typing import Annotated
from django_bolt.serializers import Serializer, Meta

class UserSerializer(Serializer):
    name: Annotated[str, Meta(min_length=1, max_length=100)]
    age: Annotated[int, Meta(ge=0, le=150)]
    email: Annotated[str, Meta(pattern=r"^[^@]+@[^@]+\.[^@]+$")]
```

### Computed Fields with `@computed_field`

Add calculated fields that are computed during serialization:

```python
from django_bolt.serializers import Serializer, computed_field

class UserSerializer(Serializer):
    first_name: str
    last_name: str

    @computed_field
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @computed_field
    def initials(self) -> str:
        return f"{self.first_name[0]}{self.last_name[0]}".upper()

# Usage:
user = UserSerializer(first_name="John", last_name="Doe")
user.dump()
# {"first_name": "John", "last_name": "Doe", "full_name": "John Doe", "initials": "JD"}
```

**Note:** Computed fields are OUTPUT ONLY - they don't exist during parsing/loading.

### Dynamic Field Selection

One of the biggest pain points with DRF is needing multiple serializer classes for different views (list vs detail, admin vs public). Django-Bolt solves this with dynamic field selection:

#### Using `only()` - Include specific fields

```python
class UserSerializer(Serializer):
    id: int
    name: str
    email: str
    created_at: datetime
    internal_notes: str

# For list view - only essential fields
UserSerializer.only("id", "name", "email").dump_many(users)
# Returns: [{"id": 1, "name": "John", "email": "john@example.com"}, ...]
```

#### Using `exclude()` - Remove specific fields

```python
# Exclude sensitive fields
UserSerializer.exclude("internal_notes", "created_at").dump(user)
# Returns: {"id": 1, "name": "John", "email": "john@example.com"}
```

#### Using `use()` - Predefined field sets

Define common field combinations once, reuse everywhere:

```python
class UserSerializer(Serializer):
    id: int
    name: str
    email: str
    password: str
    created_at: datetime
    last_login: datetime
    internal_notes: str

    class Config:
        write_only = {"password"}
        field_sets = {
            "list": ["id", "name", "email"],
            "detail": ["id", "name", "email", "created_at", "last_login"],
            "admin": ["id", "name", "email", "created_at", "last_login", "internal_notes"],
        }

# In your API handlers:
@api.get("/users")
async def list_users():
    users = await User.objects.all()
    return UserSerializer.use("list").dump_many([UserSerializer.from_model(u) for u in users])

@api.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await User.objects.aget(id=user_id)
    return UserSerializer.use("detail").dump(UserSerializer.from_model(user))

@api.get("/admin/users/{user_id}")
async def admin_get_user(user_id: int):
    user = await User.objects.aget(id=user_id)
    return UserSerializer.use("admin").dump(UserSerializer.from_model(user))
```

#### Chaining field selection

```python
# Start with a field set, then further customize
UserSerializer.use("detail").exclude("last_login").dump(user)

# Chain multiple exclusions
UserSerializer.only("id", "name", "email", "phone").exclude("email").dump(user)
```

### Dump Methods

Serializers now have powerful `dump()` methods with various options:

```python
class UserSerializer(Serializer):
    name: str
    email: str | None = None
    role: str = "user"

user = UserSerializer(name="John", email=None, role="user")

# Basic dump
user.dump()  # {"name": "John", "email": None, "role": "user"}

# Exclude None values (great for sparse responses)
user.dump(exclude_none=True)  # {"name": "John", "role": "user"}

# Exclude default values (great for PATCH responses)
user.dump(exclude_defaults=True)  # {"name": "John"}

# Dump to JSON bytes (fast, using msgspec)
user.dump_json()  # b'{"name":"John","email":null,"role":"user"}'

# Dump multiple instances
users = [UserSerializer(name="John", role="admin"), UserSerializer(name="Jane")]
UserSerializer.dump_many(users)  # [{"name": "John", ...}, {"name": "Jane", ...}]
UserSerializer.dump_many_json(users)  # JSON bytes
```

### Complete Example: One Serializer, Multiple Views

Here's how to replace multiple DRF serializers with ONE Django-Bolt serializer:

```python
# BEFORE (DRF style - 4 serializers)
class UserListSerializer(serializers.ModelSerializer):
    class Config:
        model = User
        fields = ['id', 'name']

class UserDetailSerializer(serializers.ModelSerializer):
    class Config:
        model = User
        fields = ['id', 'name', 'email', 'created_at']

class UserCreateSerializer(serializers.ModelSerializer):
    class Config:
        model = User
        fields = ['name', 'email', 'password']

class UserAdminSerializer(serializers.ModelSerializer):
    class Config:
        model = User
        fields = ['id', 'name', 'email', 'created_at', 'is_staff', 'internal_notes']


# AFTER (Django-Bolt style - 1 serializer)
from django_bolt.serializers import Serializer, computed_field, field

class UserSerializer(Serializer):
    id: int
    name: str
    email: str
    password: str
    created_at: datetime
    is_staff: bool = False
    internal_notes: str | None = None

    class Config:
        write_only = {"password"}  # Never include in output
        field_sets = {
            "list": ["id", "name"],
            "detail": ["id", "name", "email", "created_at"],
            "admin": ["id", "name", "email", "created_at", "is_staff", "internal_notes"],
        }

    @computed_field
    def display_name(self) -> str:
        return f"@{self.name}"

# Usage in handlers (runtime field filtering):
UserSerializer.use("list").dump_many(users)      # List view
UserSerializer.use("detail").dump(user)          # Detail view
UserSerializer.use("admin").dump(user)           # Admin view
UserSerializer.only("id", "display_name").dump(user)  # Custom view
```

### Type-Safe Serializer Subsets

For full type safety with `response_model`, use `subset()` or `fields()` to create actual Serializer classes:

```python
from django_bolt.serializers import Serializer, computed_field

class UserSerializer(Serializer):
    id: int
    name: str
    email: str
    password: str
    created_at: datetime
    is_staff: bool = False

    class Config:
        write_only = {"password"}
        field_sets = {
            "list": ["id", "name"],
            "detail": ["id", "name", "email", "created_at"],
            "admin": ["id", "name", "email", "created_at", "is_staff"],
        }

    @computed_field
    def display_name(self) -> str:
        return f"@{self.name}"

# Create TYPE-SAFE serializer classes (not views!)
UserListSerializer = UserSerializer.fields("list")      # From field_set
UserDetailSerializer = UserSerializer.fields("detail")  # From field_set
UserAdminSerializer = UserSerializer.fields("admin")    # From field_set
UserPublicSerializer = UserSerializer.subset("id", "name", "display_name")  # Explicit fields

# These are real Serializer subclasses - use as response_model!
@api.get("/users", response_model=list[UserListSerializer])
async def list_users() -> list[UserListSerializer]:
    users = await User.objects.all()
    return [UserListSerializer.from_model(u) for u in users]

@api.get("/users/{id}", response_model=UserDetailSerializer)
async def get_user(id: int) -> UserDetailSerializer:
    user = await User.objects.aget(id=id)
    return UserDetailSerializer.from_model(user)

@api.get("/users/{id}/public", response_model=UserPublicSerializer)
async def get_user_public(id: int) -> UserPublicSerializer:
    user = await User.objects.aget(id=id)
    return UserPublicSerializer.from_model(user)
```

**Key Methods:**

| Method             | Returns              | Use Case                                |
| ------------------ | -------------------- | --------------------------------------- |
| `subset(*fields)`  | New Serializer class | Type-safe class with explicit fields    |
| `fields(set_name)` | New Serializer class | Type-safe class from Meta.field_sets    |
| `only(*fields)`    | SerializerView       | Runtime field filtering (dump time)     |
| `exclude(*fields)` | SerializerView       | Runtime field filtering (dump time)     |
| `use(set_name)`    | SerializerView       | Runtime field filtering from field_sets |

**When to use which:**

- Use `subset()`/`fields()` when you need a proper **type** for `response_model` or type annotations
- Use `only()`/`exclude()`/`use()` for quick **runtime** field filtering without creating new classes

## Features Inherited from msgspec.Struct

Since `Serializer` extends `msgspec.Struct`, you get all msgspec features:

### Frozen (Immutable) Serializers

```python
class ImmutableUser(Serializer, frozen=True):
    username: str
    email: str

user = ImmutableUser(username="alice", email="alice@example.com")
# user.email = "new@example.com"  # Raises AttributeError
```

### Omit Defaults

```python
class UserUpdate(Serializer, omit_defaults=True):
    username: str | None = None
    email: str | None = None

# Only non-None fields are included in to_dict()
update = UserUpdate(email="new@example.com")
update.to_dict()  # {'email': 'new@example.com'}
```

### Field Renaming

```python
from msgspec import field

class UserAPI(Serializer):
    user_name: str = field(name="username")
    user_email: str = field(name="email")

user = UserAPI(user_name="alice", user_email="alice@example.com")
user.to_dict()  # {'username': 'alice', 'email': 'alice@example.com'}
```

## Type Safety

All serializer fields are fully typed and visible to type checkers:

```python
# Full IDE autocomplete and type checking
user_create = UserCreate(username="alice", email="alice@example.com", password="secret")
#              ^^^^^^^^^^                                                        ^^^^^^^^
#              Type checker knows all available attributes

user_public = UserPublic.from_model(user)
print(user_public.username)  # Type checker knows this is str
#     ^^^^^^^^^^^^
#     Autocomplete works perfectly
```

## Performance

Django-Bolt serializers are significantly faster than alternatives:

- **5-10x faster** serialization than Pydantic
- **Zero allocation** routing and parsing
- **Rust-powered** msgspec backend

Benchmark results available in the project repository.

## Migration from DRF ModelSerializer

If you're familiar with Django REST Framework:

| Feature                | DRF                         | Django-Bolt                                          |
| ---------------------- | --------------------------- | ---------------------------------------------------- |
| Field declaration      | Implicit (Meta.fields)      | Explicit annotations                                 |
| Validation             | `validate_<field>()` method | `@field_validator` decorator                         |
| Cross-field validation | `validate()` method         | `@model_validator` decorator                         |
| Model integration      | `.create()`, `.update()`    | `.from_model()`, `.to_model()`, `.update_instance()` |
| Type safety            | ❌ String-based             | ✅ Full type safety                                  |
| Performance            | Baseline                    | 5-10x faster                                         |

## Troubleshooting

### ValidationError not being raised

Validators only run during serializer initialization. Make sure you're creating the serializer instance:

```python
# ✅ Correct - validation runs
user = UserCreate(username="", email="invalid")

# ❌ Doesn't validate - just accessing type
data: UserCreate = ...
```

### Type checker doesn't recognize fields

Ensure fields are explicitly declared with type annotations:

```python
# ✅ Correct
class UserCreate(Serializer):
    username: str  # Explicit annotation

# ❌ Won't work with type checker
UserCreate = create_serializer(User, fields=['username'])
# Type checker can't see fields - use explicit class definition instead
```

## Best Practices

### 1. Separate Input and Output Serializers

Create separate serializers for input and output to maintain clear contracts:

```python
# Output - what clients receive
class UserSerializer(Serializer):
    id: int
    username: str
    email: str
    created_at: datetime

# Input - what clients send
class UserCreateSerializer(Serializer):
    username: str
    email: str
    password: str
```

### 2. Use Nested Serializers for Relationships

Represent relationships explicitly instead of using IDs:

```python
# ✅ Good - explicit nested structure
class BlogPostSerializer(Serializer):
    id: int
    title: str
    author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]

# ❌ Avoid - forces clients to make additional requests
class BlogPostSerializer(Serializer):
    id: int
    title: str
    author_id: int  # Client must fetch author separately
```

### 3. Always Prefetch in Async Handlers

When using nested serializers in async handlers, always prefetch relationships:

```python
# ✅ Correct
@api.get("/posts/{post_id}")
async def get_post(post_id: int):
    post = await (
        BlogPost.objects
        .select_related("author")
        .prefetch_related("tags")
        .aget(id=post_id)
    )
    return BlogPostSerializer.from_model(post)
```

### 4. Validate Business Logic in Model Validators

Use `@model_validator` for cross-field validation:

```python
class DateRangeSerializer(Serializer):
    start_date: date
    end_date: date

    @model_validator
    def validate_date_range(self):
        if self.end_date < self.start_date:
            raise ValueError("End date must be after start date")
        return self
```

### 5. Normalize Data in Field Validators

Transform data consistently using field validators:

```python
class UserSerializer(Serializer):
    username: str
    email: str

    @field_validator("username")
    def normalize_username(cls, value: str) -> str:
        return value.lower().strip()

    @field_validator("email")
    def normalize_email(cls, value: str) -> str:
        return value.lower()
```

### 6. Use Meta Constraints for Simple Validation

Prefer declarative `Meta` constraints over custom validators when possible:

```python
# ✅ Simpler - declarative
class UserSerializer(Serializer):
    username: Annotated[str, Meta(min_length=3, max_length=150)]
    age: Annotated[int, Meta(ge=0, le=150)]

# ❌ More verbose - custom validator
class UserSerializer(Serializer):
    username: str

    @field_validator("username")
    def validate_username(cls, value: str) -> str:
        if len(value) < 3 or len(value) > 150:
            raise ValueError("Username must be 3-150 characters")
        return value
```

### 7. Handle Uniqueness Checks in Handlers

Check database uniqueness in the handler, not in validators:

```python
# ✅ Correct - async check in handler
@api.post("/users")
async def create_user(data: UserCreateSerializer):
    if await User.objects.filter(email=data.email).aexists():
        raise BadRequest(detail="Email already exists")
    user = await User.objects.acreate(**data.to_dict())
    return UserSerializer.from_model(user)

# ❌ Avoid - sync database call in validator (breaks in async)
class UserCreateSerializer(Serializer):
    email: str

    @field_validator("email")
    def check_unique_email(cls, value: str) -> str:
        if User.objects.filter(email=value).exists():  # Sync query!
            raise ValueError("Email already exists")
        return value
```

## Common Patterns

### Pattern 1: User Registration with Password Confirmation

```python
class UserSignupSerializer(Serializer):
    username: Annotated[str, Meta(min_length=3, max_length=150)]
    email: Annotated[str, Meta(pattern=r"^[^@]+@[^@]+\.[^@]+$")]
    password: Annotated[str, Meta(min_length=8)]
    confirm_password: str

    @field_validator("email")
    def lowercase_email(cls, value: str) -> str:
        return value.lower()

    @model_validator
    def validate_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

@api.post("/auth/signup")
async def signup(data: UserSignupSerializer):
    if await User.objects.filter(username=data.username).aexists():
        raise BadRequest(detail="Username already exists")

    user = await User.objects.acreate(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    return UserSerializer.from_model(user)
```

### Pattern 2: Nested CRUD Operations

```python
# Create post with nested author
@api.post("/posts")
async def create_post(data: BlogPostInputSerializer):
    post = await BlogPost.objects.acreate(
        title=data.title,
        content=data.content,
        author_id=data.author.id,  # Extract ID from nested serializer
    )

    # Refetch with relationships for response
    post = await (
        BlogPost.objects
        .select_related("author")
        .prefetch_related("tags")
        .aget(id=post.id)
    )
    return BlogPostSerializer.from_model(post)
```

### Pattern 3: Partial Updates

```python
class UserUpdateSerializer(Serializer, omit_defaults=True):
    username: str | None = None
    email: str | None = None
    bio: str | None = None

@api.patch("/users/{user_id}")
async def update_user(user_id: int, data: UserUpdateSerializer):
    user = await User.objects.aget(id=user_id)

    # Only update provided fields
    update_data = data.to_dict()
    for field, value in update_data.items():
        setattr(user, field, value)

    await user.asave()
    return UserSerializer.from_model(user)
```

## Limitations and Caveats

### Validation Timing

**Important:** msgspec's `Meta` constraints (pattern, min_length, max_length, ge, le, etc.) only validate during **parsing**, not during direct Python instantiation:

```python
from django_bolt.serializers import Serializer, Email, PositiveInt

class UserSerializer(Serializer):
    email: Email  # Email pattern validation (max 254 chars)
    age: PositiveInt  # Must be > 0

# ✅ VALIDATES - JSON parsing triggers Meta constraints
user = UserSerializer.model_validate_json(b'{"email": "invalid", "age": -5}')
# Raises msgspec.ValidationError

# ✅ VALIDATES - Dict parsing triggers Meta constraints
user = UserSerializer.model_validate({"email": "invalid", "age": -5})
# Raises msgspec.ValidationError

# ❌ NO META VALIDATION - Direct instantiation bypasses constraints
user = UserSerializer(email="invalid", age=-5)
# No error! Meta constraints are NOT checked
print(user.email)  # "invalid"
print(user.age)    # -5
```

**Why?** This is msgspec's design - `Meta` constraints are for parsing/deserialization, not construction. This provides maximum performance for trusted internal code while still validating external input.

**Custom validators (`@field_validator`, `@model_validator`) DO run on direct instantiation:**

```python
class UserSerializer(Serializer):
    username: str

    @field_validator("username")
    def lowercase_username(cls, value):
        return value.lower()  # This DOES run

user = UserSerializer(username="UPPERCASE")
print(user.username)  # "uppercase" - validator ran
```

### `from_model()` Validation Behavior

The `from_model()` method creates instances via direct instantiation, so:

- ✅ Custom `@field_validator` and `@model_validator` decorators **DO run**
- ❌ msgspec `Meta` constraints (pattern, min_length, etc.) **DO NOT validate**

```python
class UserSerializer(Serializer):
    username: Username  # Has pattern constraint (Django auth compatible)
    email: Email

    @field_validator("email")
    def lowercase_email(cls, value):
        return value.lower()

# If database has invalid data, from_model() won't catch Meta violations
user_model = User.objects.get(id=1)  # username may have invalid chars
serializer = UserSerializer.from_model(user_model)
# No error - Meta pattern not checked
# But email IS lowercased by the field validator
```

**Recommendation:** Trust your database constraints, or use `validate()` method to re-validate:

```python
serializer = UserSerializer.from_model(user_model)
serializer = serializer.validate()  # Re-runs msgspec validation
```

### Computed Fields and Field Sets

Computed fields (`@computed_field`) are **not automatically included** in field sets. You must explicitly list them:

```python
class UserSerializer(Serializer):
    first_name: str
    last_name: str

    class Config:
        field_sets = {
            # ❌ display_name won't appear - not in field_set
            "basic": ["first_name", "last_name"],
            # ✅ display_name will appear - explicitly included
            "full": ["first_name", "last_name", "display_name"],
        }

    @computed_field
    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

user = UserSerializer(first_name="John", last_name="Doe")

# "display_name" NOT included - not in field_set
UserSerializer.use("basic").dump(user)
# {"first_name": "John", "last_name": "Doe"}

# "display_name" IS included - explicitly in field_set
UserSerializer.use("full").dump(user)
# {"first_name": "John", "last_name": "Doe", "display_name": "John Doe"}

# Full dump() always includes computed fields
user.dump()
# {"first_name": "John", "last_name": "Doe", "display_name": "John Doe"}
```

### Subset Validators

When using `subset()` to create derived serializer classes, field validators for included fields are copied, but they reference the **parent class**:

```python
class UserSerializer(Serializer):
    username: str
    email: str

    @field_validator("username")
    def lowercase_username(cls, value):
        return value.lower()

UserMini = UserSerializer.subset("username")

# Validator still works
mini = UserMini(username="UPPER")
print(mini.username)  # "upper" - validator ran
```

However, if your validator references other fields that aren't in the subset, it may fail:

```python
class UserSerializer(Serializer):
    username: str
    email: str

    @model_validator
    def check_domain(self):
        # References self.email - will fail if email not in subset!
        if not self.email.endswith("@company.com"):
            raise ValueError("Must use company email")
        return self

# ❌ This will fail - model_validator references email which isn't in subset
UserMini = UserSerializer.subset("username")
mini = UserMini(username="test")  # AttributeError: 'UserMini' has no attribute 'email'
```

**Recommendation:** Keep subset serializers simple, or create explicit serializer classes for complex validation needs.

### Nested Serializer Circular References

Circular nested serializers can cause infinite recursion. The `from_model()` method has a `max_depth` parameter (default: 10) to prevent runaway recursion:

```python
class AuthorSerializer(Serializer):
    id: int
    name: str
    # posts: list[PostSerializer]  # Would create circular reference

class PostSerializer(Serializer):
    id: int
    title: str
    author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]
    # If AuthorSerializer had 'posts', this would be circular
```

**Recommendation:** Avoid circular nested serializers. Use separate serializers for different views:

```python
# For post list - author without posts
class PostListSerializer(Serializer):
    id: int
    title: str
    author: Annotated[AuthorBasicSerializer, Nested(AuthorBasicSerializer)]

# For author detail - posts without nested author
class AuthorDetailSerializer(Serializer):
    id: int
    name: str
    posts: Annotated[list[PostBasicSerializer], Nested(PostBasicSerializer, many=True)]
```

### Async ORM and Nested Serializers

When using `from_model()` with nested serializers in async handlers, you **must** prefetch relationships:

```python
# ❌ WRONG - Will cause SynchronousOnlyOperation error
@api.get("/posts/{id}")
async def get_post(id: int):
    post = await BlogPost.objects.aget(id=id)
    return PostSerializer.from_model(post)  # Accesses post.author synchronously!

# ✅ CORRECT - Prefetch all nested relationships
@api.get("/posts/{id}")
async def get_post(id: int):
    post = await (
        BlogPost.objects
        .select_related("author")
        .prefetch_related("tags", "comments__author")
        .aget(id=id)
    )
    return PostSerializer.from_model(post)
```

### `to_model()` Transfers All Fields

The `to_model()` method transfers **all** serializer fields to the model, including `id`:

```python
class AuthorSerializer(Serializer):
    id: int
    name: str
    email: str

serializer = AuthorSerializer(id=0, name="New", email="new@example.com")
author = serializer.to_model(Author)

# author.id is 0, not None!
print(author.pk)  # 0
```

**Recommendation:** For create operations, use a serializer without `id`, or exclude it:

```python
class AuthorCreateSerializer(Serializer):
    name: str
    email: str

serializer = AuthorCreateSerializer(name="New", email="new@example.com")
author = serializer.to_model(Author)
print(author.pk)  # None - ready to save
```

### Error Wrapping

Custom validators that raise `ValueError` or `TypeError` are automatically wrapped in `msgspec.ValidationError`:

```python
class UserSerializer(Serializer):
    password: str
    password_confirm: str

    @model_validator
    def check_passwords(self):
        if self.password != self.password_confirm:
            raise ValueError("Passwords don't match")
        return self

# The ValueError is wrapped
try:
    UserSerializer(password="a", password_confirm="b")
except msgspec.ValidationError as e:  # Not ValueError!
    print(e)  # "Passwords don't match"
```

### Performance vs Pydantic

While django-bolt serializers are generally faster than Pydantic v2:

| Operation             | django-bolt   | Pydantic v2 |
| --------------------- | ------------- | ----------- |
| Object → Dict         | 3.5-6x faster | baseline    |
| Object → JSON         | 5-6x faster   | baseline    |
| Dict → Object (basic) | ~1.15x faster | baseline    |
| JSON → Object         | ~1.5x faster  | baseline    |
| Custom validators     | ~1.3x slower  | baseline    |

Custom `@field_validator` execution is slightly slower than Pydantic because Pydantic's validators are implemented in Rust (pydantic-core), while ours execute in Python. However, the overall serialization performance still makes django-bolt faster for most use cases.

### Function-Scoped Serializers

Serializers defined inside functions have limited type hint resolution:

```python
def my_handler():
    # ⚠️ Limited support - may not resolve all type hints
    class LocalSerializer(Serializer):
        value: SomeComplexType  # May fail to resolve

    return LocalSerializer(value=...)
```

**Recommendation:** Always define serializers at module level for full type hint resolution and better IDE support.

## See Also

- [Django-Bolt API Documentation](./API.md)
- [Django Model Documentation](https://docs.djangoproject.com/en/stable/ref/models/)
- [msgspec Documentation](https://jcrist.github.io/msgspec/)

# ModelSerializer - Type-Safe Serialization for Django-Bolt

Django-Bolt includes an enhanced serialization system built on top of `msgspec.Struct` that provides Pydantic-like functionality with full type safety, while maintaining msgspec's superior performance (5-10x faster).

## Overview

The `Serializer` class extends `msgspec.Struct` with:

- **Field-level validation** via `@field_validator` decorator
- **Model-level validation** via `@model_validator` decorator
- **Django model integration** with `.from_model()`, `.to_dict()`, `.to_model()`
- **100% type safety** - full IDE autocomplete and type checker support
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

## Complete Example

```python
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django_bolt.api import BoltAPI
from django_bolt.serializers import Serializer, field_validator, model_validator
from msgspec import Meta
from typing import Annotated

api = BoltAPI()

# Define serializers
class UserCreate(Serializer):
    username: Annotated[str, Meta(min_length=3, max_length=150)]
    email: str
    password: str
    password_confirm: str

    @field_validator('email')
    def validate_email_field(cls, value):
        validate_email(value)
        return value.lower()

    @field_validator('username')
    def validate_username_unique(cls, value):
        if User.objects.filter(username=value).exists():
            raise ValueError('Username already taken')
        return value.lower()

    @model_validator
    def validate_passwords(self):
        if self.password != self.password_confirm:
            raise ValueError("Passwords don't match")

class UserPublic(Serializer):
    id: int
    username: str
    email: str
    date_joined: str

# API routes
@api.post("/users", response_model=UserPublic)
async def create_user(data: UserCreate):
    # Validation happens automatically
    user = User(username=data.username, email=data.email)
    user.set_password(data.password)
    await user.asave()
    return UserPublic.from_model(user)

@api.get("/users/{user_id}", response_model=UserPublic)
async def get_user(user_id: int):
    user = await User.objects.aget(id=user_id)
    return UserPublic.from_model(user)

@api.patch("/users/{user_id}", response_model=UserPublic)
async def update_user(user_id: int, data: UserUpdate):
    user = await User.objects.aget(id=user_id)
    updated_user = data.update_instance(user)
    await updated_user.asave()
    return UserPublic.from_model(updated_user)
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

    class Meta:
        model = User  # Associated Django model
        write_only = {'password'}  # Input-only fields
        read_only = {'id', 'date_joined'}  # Output-only fields
```

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

| Feature | DRF | Django-Bolt |
|---------|-----|------------|
| Field declaration | Implicit (Meta.fields) | Explicit annotations |
| Validation | `validate_<field>()` method | `@field_validator` decorator |
| Cross-field validation | `validate()` method | `@model_validator` decorator |
| Model integration | `.create()`, `.update()` | `.from_model()`, `.to_model()`, `.update_instance()` |
| Type safety | ❌ String-based | ✅ Full type safety |
| Performance | Baseline | 5-10x faster |

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

## See Also

- [Django-Bolt API Documentation](./API.md)
- [Django Model Documentation](https://docs.djangoproject.com/en/stable/ref/models/)
- [msgspec Documentation](https://jcrist.github.io/msgspec/)

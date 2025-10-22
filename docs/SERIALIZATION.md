# Serialization in Django-Bolt

## Overview

Django-Bolt provides a high-performance serialization system powered by [msgspec](https://github.com/jcrist/msgspec), delivering 5-10x faster JSON encoding/decoding compared to Python's standard library. The serialization layer handles:

- Request body deserialization with type validation
- Response serialization with automatic type coercion
- Custom type encoders for non-JSON-native types
- Thread-local encoder/decoder caching for optimal performance
- Response model validation and transformation

## Table of Contents

- [Why msgspec?](#why-msgspec)
- [Architecture Overview](#architecture-overview)
- [Request Deserialization](#request-deserialization)
- [Response Serialization](#response-serialization)
- [Custom Type Encoders](#custom-type-encoders)
- [Type Coercion System](#type-coercion-system)
- [Response Model Validation](#response-model-validation)
- [Performance Optimizations](#performance-optimizations)
- [Comparison with DRF Serializers](#comparison-with-drf-serializers)
- [Best Practices](#best-practices)

## Why msgspec?

Django-Bolt uses msgspec instead of Python's standard `json` module for several compelling reasons:

**Performance:**
- 5-10x faster JSON encoding/decoding
- Zero-allocation design for common types
- Highly optimized C implementation
- Minimal memory allocations

**Type Safety:**
- Built-in validation during deserialization
- Schema-driven type coercion
- Clear error messages with field paths
- Compile-time type checking with `msgspec.Struct`

**Developer Experience:**
- Simple dataclass-like syntax with `msgspec.Struct`
- Automatic serialization of common Python types
- Extensible encoder hooks for custom types
- No decorator overhead or complex metaclasses

**Example benchmark:**

```python
import json
import msgspec
from django_bolt import _json

data = {"users": [{"id": i, "name": f"User{i}"} for i in range(1000)]}

# Standard library json
%timeit json.dumps(data)  # ~2.5 ms

# msgspec (Django-Bolt)
%timeit _json.encode(data)  # ~0.3 ms (8x faster)
```

## Architecture Overview

Django-Bolt's serialization system consists of three core modules:

1. **`_json.py`**: Low-level msgspec encoder/decoder with thread-local caching
2. **`serialization.py`**: Response serialization and format detection
3. **`binding.py`**: Request deserialization and type coercion

### Request Flow

```
Request Body (bytes)
    ↓
msgspec.json.decode() with type validation
    ↓
msgspec.Struct instance (validated)
    ↓
Handler function receives typed object
```

### Response Flow

```
Handler returns Python object
    ↓
Response type detection (dict/list/Struct/etc.)
    ↓
Optional: Response model validation
    ↓
Type coercion (if needed)
    ↓
msgspec.json.encode() with custom encoders
    ↓
JSON bytes sent to client
```

## Request Deserialization

Request bodies are automatically deserialized and validated using msgspec.

### Basic Usage

```python
from django_bolt import BoltAPI
import msgspec

api = BoltAPI()

class CreateUserRequest(msgspec.Struct):
    name: str
    email: str
    age: int

@api.post("/users")
async def create_user(user: CreateUserRequest):
    # user is already validated and typed
    print(f"Name: {user.name}, Email: {user.email}, Age: {user.age}")
    return {"id": 1, "name": user.name}
```

**Request:**
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "age": 30}'
```

**What happens:**
1. Request body bytes are passed to `create_body_extractor()`
2. Cached msgspec decoder validates against `CreateUserRequest`
3. Validation errors raise `RequestValidationError` (422 response)
4. Valid data is passed as typed `CreateUserRequest` object

### Validation Errors

msgspec provides detailed validation errors:

```python
class Item(msgspec.Struct):
    name: str
    price: float
    quantity: int

@api.post("/items")
async def create_item(item: Item):
    return item
```

**Invalid request:**
```bash
curl -X POST http://localhost:8000/items \
  -d '{"name": "Widget", "price": "invalid", "quantity": 5}'
```

**Response (422 Unprocessable Entity):**
```json
{
  "errors": [
    {
      "field": "price",
      "message": "Expected `float`, got `str`",
      "input": "invalid"
    }
  ]
}
```

### Decoder Caching

Decoders are cached per type for performance:

```python
# From binding.py
_DECODER_CACHE: Dict[Any, msgspec.json.Decoder] = {}

def get_msgspec_decoder(type_: Any) -> msgspec.json.Decoder:
    """Get or create a cached msgspec decoder for a type."""
    if type_ not in _DECODER_CACHE:
        _DECODER_CACHE[type_] = msgspec.json.Decoder(type_)
    return _DECODER_CACHE[type_]
```

**Benefits:**
- Decoder is compiled once per type
- Subsequent requests reuse the same decoder
- No per-request allocation overhead

### Handling Malformed JSON

Django-Bolt distinguishes between JSON syntax errors and validation errors:

```python
# Malformed JSON
curl -X POST http://localhost:8000/items \
  -d '{"name": "Widget", "price": 10.5,'  # Missing closing brace
```

**Response (422):**
```json
{
  "errors": [
    {
      "message": "JSON parsing error at line 1, column 34: unexpected end of input",
      "type": "json_decode_error"
    }
  ],
  "body": "{\"name\": \"Widget\", \"price\": 10.5,"
}
```

Error parsing extracts line/column information from `msgspec.DecodeError`:

```python
# From binding.py - create_body_extractor()
try:
    return decoder.decode(body_bytes)
except msgspec.ValidationError:
    # Field validation errors - handled separately
    raise
except msgspec.DecodeError as e:
    # JSON syntax error - parse and return detailed error
    error_detail = parse_msgspec_decode_error(e, body_bytes)
    raise RequestValidationError(errors=[error_detail], body=body_bytes)
```

## Response Serialization

Responses are automatically serialized based on their type.

### Automatic Type Detection

```python
from django_bolt import BoltAPI
import msgspec

api = BoltAPI()

# Dict/list → JSON
@api.get("/data")
async def get_data():
    return {"key": "value"}  # Serialized with msgspec

# msgspec.Struct → JSON
class User(msgspec.Struct):
    id: int
    name: str

@api.get("/user")
async def get_user():
    return User(id=1, name="Alice")  # Serialized with msgspec

# String → Plain text
@api.get("/text")
async def get_text():
    return "Hello"  # Content-Type: text/plain

# Bytes → Binary
@api.get("/binary")
async def get_binary():
    return b"data"  # Content-Type: application/octet-stream
```

### Serialization Priority

From `serialization.py`, responses are checked in this order:

```python
async def serialize_response(result: Any, meta: Dict[str, Any]) -> ResponseTuple:
    # 1. Raw response tuple (status, headers, body)
    if isinstance(result, tuple) and len(result) == 3:
        return status, headers, bytes(body)

    # 2. Dict/list (most common) → JSON
    if isinstance(result, (dict, list)):
        return await serialize_json_data(result, response_tp, meta)

    # 3. JSON response wrapper
    elif isinstance(result, JSON):
        return await serialize_json_response(result, response_tp)

    # 4. Streaming response
    elif isinstance(result, StreamingResponse):
        return result

    # 5. Other response types (PlainText, HTML, etc.)
    # ...

    # Fallback: msgspec encoding
    else:
        return await serialize_json_data(result, response_tp, meta)
```

### Thread-Local Encoder Caching

Encoders are cached per thread for performance:

```python
# From _json.py
_thread_local = threading.local()

def _get_encoder() -> msgspec.json.Encoder:
    """Return a thread-local msgspec JSON Encoder instance."""
    encoder = getattr(_thread_local, "encoder", None)
    if encoder is None:
        encoder = msgspec.json.Encoder(enc_hook=default_serializer)
        _thread_local.encoder = encoder
    return encoder

def encode(value: Any) -> bytes:
    """Encode a Python object to JSON bytes."""
    return _get_encoder().encode(value)
```

**Why thread-local?**
- msgspec encoders maintain an internal buffer
- Reusing the buffer across calls reduces allocations
- Thread-local storage prevents cross-thread contention
- Each worker thread has its own encoder instance

## Custom Type Encoders

Django-Bolt provides automatic serialization for common non-JSON-native types.

### Supported Types

```python
# From _json.py
DEFAULT_TYPE_ENCODERS: dict[type, Callable[[Any], Any]] = {
    # Paths → str
    Path: str,
    PurePath: str,

    # Dates/Times → ISO format
    datetime: lambda v: v.isoformat(),
    date: lambda v: v.isoformat(),
    time: lambda v: v.isoformat(),

    # Decimals → int or float
    Decimal: lambda v: int(v) if v.as_tuple().exponent >= 0 else float(v),

    # IP addresses → str
    IPv4Address: str,
    IPv4Interface: str,
    IPv4Network: str,
    IPv6Address: str,
    IPv6Interface: str,
    IPv6Network: str,

    # UUID → str
    UUID: str,
}
```

### Usage Examples

```python
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from uuid import UUID
import msgspec

class FileMetadata(msgspec.Struct):
    path: Path
    created_at: datetime
    size: Decimal
    id: UUID

@api.get("/file/{file_id}")
async def get_file_metadata(file_id: int):
    return FileMetadata(
        path=Path("/var/uploads/file.pdf"),
        created_at=datetime.now(),
        size=Decimal("1024.50"),
        id=UUID("123e4567-e89b-12d3-a456-426614174000")
    )
```

**Response:**
```json
{
  "path": "/var/uploads/file.pdf",
  "created_at": "2025-10-22T12:34:56.789012",
  "size": 1024.5,
  "id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Encoder Hook Logic

The encoder hook walks the MRO (Method Resolution Order) to support subclasses:

```python
def default_serializer(value: Any) -> Any:
    """Transform values non-natively supported by msgspec."""
    # Walk MRO to support polymorphic types
    for base in value.__class__.__mro__[:-1]:  # Skip 'object'
        encoder = DEFAULT_TYPE_ENCODERS.get(base)
        if encoder is not None:
            return encoder(value)

    raise TypeError(f"Unsupported type: {type(value)!r}")
```

**Example with subclass:**
```python
from pathlib import PosixPath

# PosixPath inherits from Path
file_path = PosixPath("/tmp/file.txt")

# Encoder hook finds Path in MRO and uses str encoder
result = _json.encode({"path": file_path})
# → {"path": "/tmp/file.txt"}
```

### Custom Encoder Hooks

You can provide custom encoders for specific types:

```python
from django_bolt import _json
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    COMPLETED = "completed"

def custom_serializer(value):
    if isinstance(value, Status):
        return value.value
    # Fallback to default
    return _json.default_serializer(value)

# Use custom encoder
data = {"status": Status.PENDING}
encoded = _json.encode(data, serializer=custom_serializer)
# → b'{"status":"pending"}'
```

## Type Coercion System

Django-Bolt automatically coerces Python objects to match declared response models.

### Coercion for Django Models

```python
from django.db import models
import msgspec

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    age = models.IntegerField()

class UserResponse(msgspec.Struct):
    name: str
    email: str
    age: int

@api.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = await User.objects.aget(id=user_id)
    # Django model is automatically coerced to UserResponse
    return user
```

**What happens:**

1. Handler returns Django `User` model instance
2. `coerce_to_response_type()` is called with `UserResponse` as target
3. Attributes are extracted from model: `{name: user.name, email: user.email, age: user.age}`
4. Mapping is converted to `UserResponse` via `msgspec.convert()`
5. Result is serialized to JSON

### Coercion Implementation

```python
# From binding.py
def coerce_to_response_type(value: Any, annotation: Any) -> Any:
    """Coerce arbitrary Python objects into declared response type."""
    from typing import get_origin, get_args, List

    origin = get_origin(annotation)

    # Handle List[T]
    if origin in (list, List):
        args = get_args(annotation)
        elem_type = args[0] if args else Any
        return [coerce_to_response_type(elem, elem_type) for elem in (value or [])]

    # Handle Struct
    if is_msgspec_struct(annotation):
        if isinstance(value, annotation):
            return value
        if isinstance(value, dict):
            return msgspec.convert(value, annotation)
        # Build mapping from attributes based on struct annotations
        fields = getattr(annotation, "__annotations__", {})
        mapped = {name: getattr(value, name, None) for name in fields.keys()}
        return msgspec.convert(mapped, annotation)

    # Default convert path
    return msgspec.convert(value, annotation)
```

### QuerySet Coercion

Django QuerySets are automatically converted to lists:

```python
# From binding.py
async def coerce_to_response_type_async(value: Any, annotation: Any) -> Any:
    """Async version that handles Django QuerySets."""
    # Check if value is a Django QuerySet
    if hasattr(value, '_iterable_class') and hasattr(value, 'model'):
        # Convert to list asynchronously
        result = []
        async for item in value:
            result.append(item)
        value = result

    return coerce_to_response_type(value, annotation)
```

**Usage:**
```python
@api.get("/users", response_model=list[UserResponse])
async def list_users():
    # QuerySet is automatically converted to list
    return User.objects.all()
    # Each User model is coerced to UserResponse
```

### Primitive Type Conversion

For query parameters, path parameters, etc., `convert_primitive()` handles type coercion:

```python
# From binding.py
def convert_primitive(value: str, annotation: Any) -> Any:
    """Convert string value to appropriate type."""
    tp = unwrap_optional(annotation)

    if tp is str or tp is Any or tp is None:
        return value

    if tp is int:
        try:
            return int(value)
        except ValueError:
            raise HTTPException(422, detail=f"Invalid integer value: '{value}'")

    if tp is float:
        try:
            return float(value)
        except ValueError:
            raise HTTPException(422, detail=f"Invalid float value: '{value}'")

    if tp is bool:
        v = value.lower()
        if v in ("1", "true", "t", "yes", "y", "on"):
            return True
        if v in ("0", "false", "f", "no", "n", "off"):
            return False
        return bool(value)

    # Fallback: try msgspec decode for JSON in value
    try:
        return msgspec.json.decode(value.encode())
    except Exception:
        return value
```

**Example:**
```python
@api.get("/items")
async def get_items(
    page: int = 1,  # "1" → 1
    active: bool = True,  # "true" → True
    price: float = 0.0  # "19.99" → 19.99
):
    return {"page": page, "active": active, "price": price}
```

## Response Model Validation

Response models ensure API contracts are enforced.

### Basic Validation

```python
import msgspec

class ItemResponse(msgspec.Struct):
    id: int
    name: str
    price: float
    in_stock: bool

@api.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    # Return dict - will be validated and coerced to ItemResponse
    return {
        "id": item_id,
        "name": "Widget",
        "price": 19.99,
        "in_stock": True
    }
```

**What happens:**
1. Handler returns dict
2. `serialize_json_data()` calls `coerce_to_response_type_async()`
3. Dict is converted to `ItemResponse` via `msgspec.convert()`
4. Validation errors return 500 with "Response validation error"
5. Valid struct is serialized with `_json.encode()`

### List Validation

```python
@api.get("/items", response_model=list[ItemResponse])
async def list_items():
    return [
        {"id": 1, "name": "Item 1", "price": 10.0, "in_stock": True},
        {"id": 2, "name": "Item 2", "price": 20.0, "in_stock": False},
    ]
    # Each dict is validated against ItemResponse
```

### Validation with Django Models

```python
from django.db import models
import msgspec

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.BooleanField(default=True)

class ProductResponse(msgspec.Struct):
    name: str
    price: float
    in_stock: bool

@api.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    product = await Product.objects.aget(id=product_id)
    # Model instance is coerced to ProductResponse
    return product
```

**Coercion steps:**
1. Extract fields: `{name: product.name, price: product.price, in_stock: product.in_stock}`
2. `Decimal` is converted to `float` during `msgspec.convert()`
3. Result is validated against `ProductResponse` schema
4. Serialized with custom encoder (Decimal → float)

### Error Handling

If response validation fails, a 500 error is returned:

```python
class StrictResponse(msgspec.Struct):
    id: int
    name: str

@api.get("/strict", response_model=StrictResponse)
async def strict_endpoint():
    # Missing required field 'name'
    return {"id": 1}
```

**Response (500 Internal Server Error):**
```
Response validation error: Object missing required field `name`
```

**Implementation:**
```python
# From serialization.py
async def serialize_json_data(result: Any, response_tp: Optional[Any], meta: Dict[str, Any]):
    if response_tp is not None:
        try:
            validated = await coerce_to_response_type_async(result, response_tp)
            data = _json.encode(validated)
        except Exception as e:
            err = f"Response validation error: {e}"
            return 500, [("content-type", "text/plain; charset=utf-8")], err.encode()
    else:
        data = _json.encode(result)

    status = int(meta.get("default_status_code", 200))
    return status, [("content-type", "application/json")], data
```

### Response Model vs Return Annotation

You can specify response type via decorator parameter or return annotation:

```python
# 1. Using response_model parameter (takes precedence)
@api.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    return {"id": item_id, "name": "Widget"}

# 2. Using return annotation
@api.get("/items/{item_id}")
async def get_item(item_id: int) -> ItemResponse:
    return ItemResponse(id=item_id, name="Widget")

# 3. Both specified - response_model takes precedence
@api.get("/items/{item_id}", response_model=dict)
async def get_item(item_id: int) -> ItemResponse:  # Ignored
    return {"id": item_id}  # Validated as dict, not ItemResponse
```

## Performance Optimizations

Django-Bolt's serialization system is designed for maximum performance.

### 1. Thread-Local Caching

Encoders and decoders are cached per thread:

```python
# Single encoder/decoder per thread - no cross-thread contention
_thread_local = threading.local()

def _get_encoder():
    encoder = getattr(_thread_local, "encoder", None)
    if encoder is None:
        encoder = msgspec.json.Encoder(enc_hook=default_serializer)
        _thread_local.encoder = encoder
    return encoder
```

**Benefits:**
- Buffer reuse across requests (reduces allocations)
- No locking overhead (thread-local storage)
- Encoder compilation happens once per thread

### 2. Type-Specific Decoder Caching

Each type gets a compiled decoder:

```python
_DECODER_CACHE: Dict[Any, msgspec.json.Decoder] = {}

def get_msgspec_decoder(type_: Any):
    if type_ not in _DECODER_CACHE:
        _DECODER_CACHE[type_] = msgspec.json.Decoder(type_)
    return _DECODER_CACHE[type_]
```

**Benefits:**
- Decoder compiles schema once
- Subsequent requests reuse compiled decoder
- Zero per-request compilation overhead

### 3. Pre-Compiled Extractors

Parameter extractors are compiled once at route registration:

```python
# From binding.py
def create_body_extractor(name: str, annotation: Any) -> Callable:
    """Pre-compile extractor for request body."""
    if is_msgspec_struct(annotation):
        decoder = get_msgspec_decoder(annotation)
        def extract(body_bytes: bytes) -> Any:
            return decoder.decode(body_bytes)
    else:
        def extract(body_bytes: bytes) -> Any:
            return msgspec.json.decode(body_bytes, type=annotation)
    return extract
```

**Benefits:**
- No runtime type checking
- Direct function calls (no dictionary lookups)
- Decoder is pre-fetched and ready to use

### 4. Fast Type Detection

Response serialization uses ordered type checks (most common first):

```python
# Most common: dict/list → JSON
if isinstance(result, (dict, list)):
    return await serialize_json_data(...)

# Common: JSON wrapper
elif isinstance(result, JSON):
    return await serialize_json_response(...)

# Less common: Other types
elif isinstance(result, PlainText):
    ...
```

**Benefits:**
- Most requests hit the first branch
- Minimal isinstance() checks for common cases
- Fast path for dict/list responses

### 5. Zero-Copy Paths

msgspec uses zero-copy optimizations internally:

- String interning for repeated keys
- Direct UTF-8 encoding without intermediate steps
- Minimal memory allocations
- Efficient buffer management

### Benchmark Results

Typical performance improvements over stdlib json:

```python
# Encoding (Python object → JSON bytes)
stdlib json.dumps():     2.5 ms
msgspec encode():        0.3 ms  (8.3x faster)

# Decoding (JSON bytes → Python object)
stdlib json.loads():     1.8 ms
msgspec decode():        0.2 ms  (9.0x faster)

# With validation (JSON → msgspec.Struct)
stdlib json + validation: 3.0 ms
msgspec decode_typed():   0.3 ms  (10x faster)
```

## Comparison with DRF Serializers

Django-Bolt's msgspec-based approach differs significantly from Django REST Framework serializers.

### Architecture Comparison

| Aspect | DRF Serializers | Django-Bolt (msgspec) |
|--------|----------------|----------------------|
| **Definition** | Class-based with fields | Dataclass-like structs |
| **Validation** | Explicit field validators | Type-driven validation |
| **Performance** | Slow (Python overhead) | Fast (C implementation) |
| **Type Safety** | Runtime only | Compile-time + runtime |
| **Code Verbosity** | High (explicit fields) | Low (type annotations) |
| **Learning Curve** | Steep | Gentle |

### Code Comparison

**DRF Serializers:**
```python
from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    age = serializers.IntegerField(min_value=0, max_value=120)
    is_active = serializers.BooleanField(default=True)

    def validate_email(self, value):
        if not value.endswith('@example.com'):
            raise serializers.ValidationError("Email must be @example.com")
        return value

    def create(self, validated_data):
        return User.objects.create(**validated_data)

# Usage
serializer = UserSerializer(data=request.data)
if serializer.is_valid():
    user = serializer.save()
else:
    return Response(serializer.errors, status=400)
```

**Django-Bolt (msgspec):**
```python
import msgspec

class UserRequest(msgspec.Struct):
    name: str
    email: str
    age: int
    is_active: bool = True

@api.post("/users")
async def create_user(user: UserRequest):
    # Validation already done automatically
    # If email/age are invalid, 422 is returned
    new_user = await User.objects.acreate(
        name=user.name,
        email=user.email,
        age=user.age,
        is_active=user.is_active
    )
    return {"id": new_user.id}
```

### Performance Comparison

**DRF:**
- Uses Python `json` module (slow)
- Field validation loops through all fields
- Heavy metaclass machinery
- Slow for large payloads

**Django-Bolt:**
- Uses msgspec C implementation (fast)
- Compiled validation schema
- Minimal Python overhead
- Fast for any payload size

**Benchmark (1000 users):**
```python
# DRF
serializer = UserSerializer(users, many=True)
%timeit serializer.data  # ~150 ms

# Django-Bolt
%timeit _json.encode(users)  # ~15 ms (10x faster)
```

### Feature Comparison

| Feature | DRF | Django-Bolt |
|---------|-----|------------|
| Nested serialization | Yes | Yes (nested Structs) |
| Custom validation | `validate_*()` methods | Custom hooks/validators |
| Model serialization | `ModelSerializer` | Automatic coercion |
| Partial updates | `partial=True` | Manual (PATCH handlers) |
| Field-level permissions | Yes | Manual (guards) |
| Hyperlinked relations | `HyperlinkedModelSerializer` | Manual |
| File uploads | `FileField` | `File` parameter marker |
| Read-only fields | `read_only=True` | Separate request/response models |

### When to Use Each

**Use DRF Serializers when:**
- You need field-level permissions
- Complex nested writes with validation
- Hyperlinked API with relations
- ModelViewSet convenience features
- Existing DRF ecosystem/plugins

**Use Django-Bolt (msgspec) when:**
- Performance is critical (high RPS)
- Simple request/response validation
- Type safety and IDE support matter
- Prefer explicit over implicit
- Building new high-performance APIs

### Migration Strategy

If migrating from DRF, split serializers into separate request/response models:

**DRF:**
```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']
```

**Django-Bolt:**
```python
# Request model (writes)
class CreateUserRequest(msgspec.Struct):
    name: str
    email: str

# Response model (reads)
class UserResponse(msgspec.Struct):
    id: int
    name: str
    email: str
    created_at: datetime

@api.post("/users", response_model=UserResponse)
async def create_user(user: CreateUserRequest):
    new_user = await User.objects.acreate(name=user.name, email=user.email)
    return new_user  # Auto-coerced to UserResponse
```

## Best Practices

### 1. Use msgspec.Struct for Schemas

```python
# Good - Type-safe, validated, performant
import msgspec

class CreateItemRequest(msgspec.Struct):
    name: str
    price: float
    quantity: int = 1

@api.post("/items")
async def create_item(item: CreateItemRequest):
    return {"id": 1, "name": item.name}

# Bad - No validation, type errors at runtime
@api.post("/items")
async def create_item(item: dict):
    # item could be anything - no guarantees
    return {"id": 1}
```

### 2. Separate Request/Response Models

```python
# Good - Clear separation of concerns
class CreateUserRequest(msgspec.Struct):
    name: str
    email: str
    password: str  # Only for input

class UserResponse(msgspec.Struct):
    id: int
    name: str
    email: str
    created_at: datetime  # Only for output
    # password is never included in response

@api.post("/users", response_model=UserResponse)
async def create_user(user: CreateUserRequest):
    new_user = await User.objects.acreate(...)
    return new_user

# Bad - Same model for request/response
class UserModel(msgspec.Struct):
    id: Optional[int]  # Not needed for create
    name: str
    email: str
    password: Optional[str]  # Security risk if returned
    created_at: Optional[datetime]  # Client shouldn't provide this
```

### 3. Use Response Model Validation

```python
# Good - Enforce API contract
class ProductResponse(msgspec.Struct):
    id: int
    name: str
    price: float

@api.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    product = await Product.objects.aget(id=product_id)
    return product  # Validated against ProductResponse

# Bad - No validation, typos can slip through
@api.get("/products/{product_id}")
async def get_product(product_id: int):
    product = await Product.objects.aget(id=product_id)
    return {"id": product.id, "nmae": product.name}  # Typo!
```

### 4. Leverage Automatic Type Coercion

```python
# Good - Let Django-Bolt handle conversion
from datetime import datetime
from decimal import Decimal

class OrderResponse(msgspec.Struct):
    id: int
    total: float  # Decimal → float
    created_at: datetime  # Automatically serialized to ISO format

@api.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int):
    order = await Order.objects.aget(id=order_id)
    # Decimal and datetime are auto-converted
    return order

# Bad - Manual conversion
@api.get("/orders/{order_id}")
async def get_order(order_id: int):
    order = await Order.objects.aget(id=order_id)
    return {
        "id": order.id,
        "total": float(order.total),  # Manual
        "created_at": order.created_at.isoformat()  # Manual
    }
```

### 5. Use Custom Encoders for Domain Types

```python
# Good - Register custom encoder for enum
from enum import Enum
from django_bolt import _json

class OrderStatus(Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

# Add to DEFAULT_TYPE_ENCODERS
_json.DEFAULT_TYPE_ENCODERS[OrderStatus] = lambda v: v.value

class OrderResponse(msgspec.Struct):
    id: int
    status: OrderStatus  # Automatically serialized to "pending"/"shipped"/etc.

# Bad - Manual string conversion
class OrderResponse(msgspec.Struct):
    id: int
    status: str  # Loses type safety

@api.get("/orders/{order_id}")
async def get_order(order_id: int):
    order = await Order.objects.aget(id=order_id)
    return {
        "id": order.id,
        "status": order.status.value  # Manual conversion
    }
```

### 6. Handle QuerySets Efficiently

```python
# Good - Let coercion handle QuerySet → list
@api.get("/users", response_model=list[UserResponse])
async def list_users():
    return User.objects.all()  # Auto-converted to list

# Also good - Explicit async iteration for control
@api.get("/users", response_model=list[UserResponse])
async def list_users():
    users = []
    async for user in User.objects.all():
        users.append(user)
    return users

# Bad - Blocking iteration in async handler
@api.get("/users")
async def list_users():
    return list(User.objects.all())  # Blocks event loop!
```

### 7. Use Type Hints for Query Parameters

```python
# Good - Automatic type conversion
@api.get("/items")
async def get_items(
    page: int = 1,  # "?page=5" → 5
    active: bool = True,  # "?active=false" → False
    min_price: float = 0.0  # "?min_price=9.99" → 9.99
):
    return {"page": page, "active": active, "min_price": min_price}

# Bad - Manual type conversion
@api.get("/items")
async def get_items(page: str = "1", active: str = "true"):
    page_int = int(page)  # Manual, can raise ValueError
    active_bool = active.lower() == "true"  # Manual
    return {"page": page_int, "active": active_bool}
```

### 8. Validate Early, Fail Fast

```python
# Good - Validation happens before handler execution
class CreateItemRequest(msgspec.Struct):
    name: str
    price: float
    quantity: int

    def __post_init__(self):
        # Custom validation after msgspec validation
        if self.price <= 0:
            raise ValueError("Price must be positive")
        if self.quantity < 1:
            raise ValueError("Quantity must be at least 1")

@api.post("/items")
async def create_item(item: CreateItemRequest):
    # item is already validated - safe to use
    return await Item.objects.acreate(**item.__dict__)

# Bad - Validation inside handler
@api.post("/items")
async def create_item(item: dict):
    if item.get("price", 0) <= 0:
        raise HTTPException(400, "Price must be positive")
    if item.get("quantity", 0) < 1:
        raise HTTPException(400, "Quantity must be at least 1")
    # Validation scattered throughout handler
```

### 9. Use Optional Fields Appropriately

```python
# Good - Clear optional fields
class UpdateItemRequest(msgspec.Struct):
    name: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None

@api.patch("/items/{item_id}")
async def update_item(item_id: int, updates: UpdateItemRequest):
    item = await Item.objects.aget(id=item_id)
    if updates.name is not None:
        item.name = updates.name
    if updates.price is not None:
        item.price = updates.price
    await item.asave()
    return item

# Bad - Required fields for partial update
class UpdateItemRequest(msgspec.Struct):
    name: str  # Forces client to always send all fields
    price: float
    quantity: int

@api.patch("/items/{item_id}")
async def update_item(item_id: int, updates: UpdateItemRequest):
    # Client must send name/price/quantity even if unchanged
    ...
```

### 10. Cache Decoders for Hot Paths

```python
# Good - Pre-compile decoder for frequently used types
from django_bolt.binding import get_msgspec_decoder

class UserRequest(msgspec.Struct):
    name: str
    email: str

# Decoder is automatically cached globally
decoder = get_msgspec_decoder(UserRequest)

# Reused across all requests - no recompilation
@api.post("/users")
async def create_user(user: UserRequest):
    # Decoder was compiled once, reused here
    return {"id": 1}

# Bad - Create new decoder on every request
@api.post("/users")
async def create_user(body: bytes):
    # New decoder created every request!
    decoder = msgspec.json.Decoder(UserRequest)
    user = decoder.decode(body)
    return {"id": 1}
```

## See Also

- [RESPONSES.md](RESPONSES.md) - Response types and serialization formats
- [EXCEPTIONS.md](EXCEPTIONS.md) - Error handling and validation errors
- [ANNOTATION_GUIDE.md](ANNOTATION_GUIDE.md) - Type annotations and parameter extraction
- [DEPENDENCY_INJECTION.md](DEPENDENCY_INJECTION.md) - Using Depends() with validated models
- [ASYNC_DJANGO.md](ASYNC_DJANGO.md) - Async ORM usage with response models

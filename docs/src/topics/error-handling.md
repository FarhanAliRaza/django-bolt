---
icon: lucide/triangle-alert
---

# Error handling

Django-Bolt provides a structured exception hierarchy for HTTP errors and automatic error response formatting.

## Exception classes

### HTTPException

The base class for all HTTP errors:

```python
from django_bolt.exceptions import HTTPException

raise HTTPException(status_code=400, detail="Bad request")
```

Parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status_code` | `int` | required | HTTP status code |
| `detail` | `str` | HTTP phrase | Error message |
| `headers` | `dict` | `{}` | Response headers |
| `extra` | `dict` | `None` | Additional error data |

### Specialized exceptions

Django-Bolt provides pre-configured exceptions for common status codes:

```python
from django_bolt.exceptions import (
    # 4xx Client Errors
    BadRequest,           # 400
    Unauthorized,         # 401
    Forbidden,            # 403
    NotFound,             # 404
    MethodNotAllowed,     # 405
    NotAcceptable,        # 406
    Conflict,             # 409
    Gone,                 # 410
    UnprocessableEntity,  # 422
    TooManyRequests,      # 429

    # 5xx Server Errors
    InternalServerError,  # 500
    BadGateway,           # 502
    ServiceUnavailable,   # 503
    GatewayTimeout,       # 504
)
```

Usage:

```python
@api.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await User.objects.filter(id=user_id).afirst()
    if not user:
        raise NotFound(detail="User not found")
    return {"id": user.id, "username": user.username}
```

### Custom headers

Add headers to error responses:

```python
raise Unauthorized(
    detail="Authentication required",
    headers={"WWW-Authenticate": "Bearer"}
)
```

### Extra data

Include additional information in the error response:

```python
raise BadRequest(
    detail="Invalid input",
    extra={
        "field": "email",
        "value": "invalid@",
        "reason": "Invalid email format"
    }
)
```

Response:

```json
{
    "detail": "Invalid input",
    "extra": {
        "field": "email",
        "value": "invalid@",
        "reason": "Invalid email format"
    }
}
```

## Validation errors

### RequestValidationError

Raised when request validation fails. Django-Bolt's Serializer **automatically collects all validation errors** from `@field_validator` and `@model_validator` before raising, so users see all issues at once:

```python
from django_bolt.serializers import Serializer, field_validator

class UserSerializer(Serializer):
    email: str
    age: int

    @field_validator("email")
    def validate_email(cls, value):
        if "@" not in value:
            raise ValueError("Invalid email format")
        return value

    @field_validator("age")
    def validate_age(cls, value):
        if value < 0:
            raise ValueError("Must be positive")
        return value

# Both fields fail - ALL errors returned, not just the first
UserSerializer(email="invalid", age=-5)
# Raises RequestValidationError with both errors
```

You can also raise manually:

```python
from django_bolt.exceptions import RequestValidationError

errors = [
    {
        "loc": ["body", "email"],
        "msg": "Invalid email format",
        "type": "value_error"
    },
    {
        "loc": ["body", "age"],
        "msg": "Must be positive",
        "type": "value_error"
    }
]
raise RequestValidationError(errors)
```

Response (422 Unprocessable Entity):

```json
{
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "Invalid email format",
            "type": "value_error"
        },
        {
            "loc": ["body", "age"],
            "msg": "Must be positive",
            "type": "value_error"
        }
    ]
}
```

### ResponseValidationError

Raised when response validation fails (returns 500):

```python
from django_bolt.exceptions import ResponseValidationError

errors = [
    {
        "loc": ["response", "id"],
        "msg": "Field required",
        "type": "missing"
    }
]
raise ResponseValidationError(errors)
```

Response validation errors indicate a server bug, so they return 500 Internal Server Error.

## Error handlers

Django-Bolt provides built-in error handlers:

### http_exception_handler

Handles `HTTPException` and its subclasses:

```python
from django_bolt.error_handlers import http_exception_handler

exc = NotFound(detail="User not found")
status, headers, body = http_exception_handler(exc)
# status: 404
# body: b'{"detail": "User not found"}'
```

### request_validation_error_handler

Handles `RequestValidationError`:

```python
from django_bolt.error_handlers import request_validation_error_handler

errors = [{"loc": ["body"], "msg": "Invalid", "type": "value_error"}]
exc = RequestValidationError(errors)
status, headers, body = request_validation_error_handler(exc)
# status: 422
```

### generic_exception_handler

Handles unexpected exceptions:

```python
from django_bolt.error_handlers import generic_exception_handler

exc = ValueError("Something went wrong")

# Production mode - hide details
status, headers, body = generic_exception_handler(exc, debug=False)
# body: b'{"detail": "Internal Server Error"}'

# Debug mode - show Django error page
status, headers, body = generic_exception_handler(exc, debug=True)
# Returns HTML error page with traceback
```

### handle_exception

The main entry point that routes to appropriate handlers:

```python
from django_bolt.error_handlers import handle_exception

# Automatically detects exception type
status, headers, body = handle_exception(some_exception)
```

## Debug mode

In debug mode (`DEBUG=True` in Django settings), unhandled exceptions return Django's HTML error page with full traceback:

```python
# debug=True: Full HTML traceback page
status, headers, body = handle_exception(exc, debug=True)
# content-type: text/html

# debug=False: JSON error response
status, headers, body = handle_exception(exc, debug=False)
# content-type: application/json
```

The debug parameter defaults to Django's `DEBUG` setting.

## msgspec validation errors

Django-Bolt converts `msgspec.ValidationError` to the standard error format:

```python
from django_bolt.error_handlers import msgspec_validation_error_to_dict

try:
    msgspec.json.decode(b'{"age": "invalid"}', type=MyStruct)
except msgspec.ValidationError as e:
    errors = msgspec_validation_error_to_dict(e)
    # [{"loc": [...], "msg": "...", "type": "..."}]
```

## Error response format

All errors follow a consistent format:

```json
{
    "detail": "Error message",
    "extra": {}
}
```

For validation errors:

```json
{
    "detail": [
        {
            "loc": ["body", "field_name"],
            "msg": "Error message",
            "type": "error_type"
        }
    ]
}
```

## Example: Custom error handling

```python
from django_bolt import BoltAPI
from django_bolt.exceptions import HTTPException, NotFound, BadRequest

api = BoltAPI()

@api.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id < 1:
        raise BadRequest(
            detail="Invalid user ID",
            extra={"user_id": user_id, "reason": "Must be positive"}
        )

    user = await User.objects.filter(id=user_id).afirst()
    if not user:
        raise NotFound(detail=f"User {user_id} not found")

    return {"id": user.id, "username": user.username}

@api.post("/orders")
async def create_order(data: OrderCreate):
    try:
        order = await Order.objects.acreate(**data.__dict__)
        return {"id": order.id}
    except IntegrityError:
        raise BadRequest(
            detail="Order creation failed",
            extra={"reason": "Duplicate order reference"}
        )
```

## Chaining exceptions

Preserve the original exception context:

```python
try:
    result = some_operation()
except ValueError as e:
    raise InternalServerError(detail=str(e))
```

The original traceback is preserved for debugging.

## Exception reference

### Client errors (4xx)

| Exception | Status Code | Default Message |
|-----------|-------------|-----------------|
| `BadRequest` | 400 | Bad Request |
| `Unauthorized` | 401 | Unauthorized |
| `Forbidden` | 403 | Forbidden |
| `NotFound` | 404 | Not Found |
| `MethodNotAllowed` | 405 | Method Not Allowed |
| `NotAcceptable` | 406 | Not Acceptable |
| `Conflict` | 409 | Conflict |
| `Gone` | 410 | Gone |
| `UnprocessableEntity` | 422 | Unprocessable Entity |
| `TooManyRequests` | 429 | Too Many Requests |

### Server errors (5xx)

| Exception | Status Code | Default Message |
|-----------|-------------|-----------------|
| `InternalServerError` | 500 | Internal Server Error |
| `BadGateway` | 502 | Bad Gateway |
| `ServiceUnavailable` | 503 | Service Unavailable |
| `GatewayTimeout` | 504 | Gateway Timeout |

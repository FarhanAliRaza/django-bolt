# Exception Handling in Django-Bolt

## Overview

Django-Bolt provides a comprehensive exception handling system that automatically converts Python exceptions into appropriate HTTP responses. The system supports both production and debug modes, with automatic integration with Django's DEBUG setting.

## Exception Types

### HTTPException

Base exception class for all HTTP errors. Automatically converts to proper HTTP responses.

```python
from django_bolt.exceptions import HTTPException

raise HTTPException(
    status_code=400,
    detail="Invalid request",
    headers={"X-Error-Code": "INVALID_REQUEST"},
    extra={"field": "email", "reason": "Invalid format"}
)
```

**Parameters:**
- `status_code` (int): HTTP status code (required)
- `detail` (str): Human-readable error message (defaults to HTTP status phrase)
- `headers` (dict): Additional HTTP headers to include in response
- `extra` (dict): Additional context data included in JSON response

### Specialized HTTP Exceptions

Pre-configured exception classes for common HTTP errors:

```python
from django_bolt.exceptions import (
    BadRequest,           # 400
    Unauthorized,         # 401
    Forbidden,            # 403
    NotFound,             # 404
    UnprocessableEntity,  # 422
    TooManyRequests,      # 429
    InternalServerError,  # 500
    ServiceUnavailable,   # 503
)

# Usage
raise NotFound(detail="User not found")
raise Unauthorized(
    detail="Authentication required",
    headers={"WWW-Authenticate": "Bearer"}
)
```

### Validation Exceptions

#### RequestValidationError

Raised when request data fails validation (e.g., invalid msgspec struct):

```python
from django_bolt.exceptions import RequestValidationError

errors = [
    {
        "loc": ["body", "email"],
        "msg": "Invalid email format",
        "type": "value_error"
    }
]
raise RequestValidationError(errors, body=request_body)
```

Returns 422 Unprocessable Entity with detailed error information.

#### ResponseValidationError

Raised when response data fails validation:

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

Returns 500 Internal Server Error (response validation failures are server-side bugs).

## Error Responses

### Production Mode (DEBUG=False)

In production, Django-Bolt returns clean JSON responses without exposing internal details:

```json
{
  "detail": "Internal Server Error"
}
```

For HTTPException and validation errors, appropriate details are included:

```json
{
  "detail": "User not found"
}
```

For validation errors:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error"
    }
  ]
}
```

### Debug Mode (DEBUG=True)

In debug mode, Django-Bolt uses Django's ExceptionReporter to generate beautiful HTML error pages with full tracebacks:

- **HTML Error Pages**: Full Django debug page with syntax highlighting, local variables, and request context
- **Fallback JSON**: If HTML generation fails, returns JSON with full traceback:

```json
{
  "detail": "ValueError: Something went wrong",
  "extra": {
    "exception": "Something went wrong",
    "exception_type": "ValueError",
    "traceback": [
      "Traceback (most recent call last):",
      "  File \"/path/to/file.py\", line 42, in function_name",
      "    raise ValueError(\"Something went wrong\")",
      "ValueError: Something went wrong"
    ]
  }
}
```

## Usage in Handlers

### Raising Exceptions

```python
from django_bolt import BoltAPI
from django_bolt.exceptions import NotFound, BadRequest
import msgspec

api = BoltAPI()

class UserCreateRequest(msgspec.Struct):
    email: str
    name: str

@api.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await User.objects.aget(id=user_id)
    if not user:
        raise NotFound(detail=f"User {user_id} not found")
    return user

@api.post("/users")
async def create_user(user: UserCreateRequest):
    # Validation happens automatically via msgspec
    # If invalid, RequestValidationError is raised automatically

    if await User.objects.filter(email=user.email).aexists():
        raise BadRequest(
            detail="User already exists",
            extra={"email": user.email}
        )

    new_user = await User.objects.acreate(
        email=user.email,
        name=user.name
    )
    return new_user
```

### Custom Error Handling

You can handle exceptions in your code and convert them to HTTPException:

```python
@api.post("/upload")
async def upload_file(file: bytes):
    try:
        process_file(file)
    except ValueError as e:
        raise BadRequest(detail=f"Invalid file: {str(e)}")
    except Exception as e:
        # Generic exceptions are automatically converted to 500 errors
        # But you can customize the response:
        raise InternalServerError(
            detail="File processing failed",
            extra={"error": str(e)}
        )

    return {"status": "uploaded"}
```

## Automatic Exception Handling

Django-Bolt automatically handles all exceptions raised in your handlers:

### 1. HTTPException
Converted to appropriate HTTP response with status code and headers.

### 2. RequestValidationError / ResponseValidationError
Converted to 422 or 500 responses with validation error details.

### 3. msgspec.ValidationError
Automatically converted to 422 Unprocessable Entity with formatted errors.

### 4. Generic Python Exceptions
- **Production (DEBUG=False)**: Returns generic 500 error without exposing details
- **Debug (DEBUG=True)**: Returns HTML error page or JSON with full traceback

## Error Logging

All exceptions are automatically logged via Django-Bolt's logging middleware:

```python
# Errors are logged at ERROR level with request context
ERROR - 2025-10-10 20:41:21 - django_bolt - Exception in GET /api/users/123: NotFound: User not found
```

See [LOGGING.md](LOGGING.md) for details on logging configuration.

## Request Context in Exceptions

When an exception occurs, the request context is automatically passed to the error handler and ExceptionReporter. This provides:

- Request method and path
- Request headers and query parameters
- Stack trace showing the full call chain
- Local variables at each stack frame (in HTML debug mode)

Example error page includes:

```
Request Method: POST
Request URL: /api/users
Python Version: 3.12.11
Django Version: 5.1.4

Traceback (most recent call last):
  File "/path/to/handler.py", line 42, in create_user
    raise ValueError("Invalid user data")

ValueError: Invalid user data
```

## Best Practices

### 1. Use Specific Exception Types

```python
# Good - Clear intent
raise NotFound(detail="User not found")

# Bad - Generic exception in production
raise Exception("User not found")
```

### 2. Provide Meaningful Error Messages

```python
# Good - Actionable error message
raise BadRequest(
    detail="Email address is already registered",
    extra={"field": "email", "value": user.email}
)

# Bad - Vague error message
raise BadRequest(detail="Invalid input")
```

### 3. Include Context in Extra Field

```python
# Good - Provides debugging context
raise UnprocessableEntity(
    detail="Validation failed",
    extra={
        "errors": [
            {"field": "email", "message": "Invalid format"},
            {"field": "age", "message": "Must be positive"}
        ]
    }
)
```

### 4. Don't Expose Sensitive Information

```python
# Good - Safe error message
raise BadRequest(detail="Authentication failed")

# Bad - Exposes user existence
raise BadRequest(detail=f"Password incorrect for user {email}")
```

### 5. Let Django-Bolt Handle Validation Errors

```python
# Good - Let msgspec and Django-Bolt handle validation
class UserRequest(msgspec.Struct):
    email: str
    age: int

@api.post("/users")
async def create_user(user: UserRequest):
    # Validation happens automatically
    # If invalid, RequestValidationError is raised
    return user

# Bad - Manual validation (unnecessary)
@api.post("/users")
async def create_user(user: UserRequest):
    if not user.email:
        raise BadRequest(detail="Email required")
    # msgspec already validated this!
```

## Error Response Format

### Standard Error Response

```json
{
  "detail": "Error message"
}
```

### Error Response with Extra Data

```json
{
  "detail": "Validation failed",
  "extra": {
    "field": "email",
    "reason": "Invalid format"
  }
}
```

### Validation Error Response

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
      "msg": "Must be a positive integer",
      "type": "value_error"
    }
  ]
}
```

## Configuration

### Django DEBUG Setting

Exception handling behavior is controlled by Django's DEBUG setting:

```python
# settings.py
DEBUG = True   # Enable HTML error pages with full tracebacks
DEBUG = False  # Return clean JSON errors without internal details
```

### Custom Exception Handling

To customize exception handling, you can catch exceptions in your handlers:

```python
@api.post("/process")
async def process_data(data: dict):
    try:
        result = await process(data)
        return result
    except SpecificError as e:
        # Custom handling for specific error
        raise BadRequest(detail=str(e))
    except Exception:
        # Let Django-Bolt handle generic exceptions
        raise
```

## Testing Exception Handling

```python
import pytest
from django_bolt import BoltAPI
from django_bolt.exceptions import NotFound

def test_exception_handling():
    api = BoltAPI()

    @api.get("/users/{user_id}")
    async def get_user(user_id: int):
        if user_id == 999:
            raise NotFound(detail="User not found")
        return {"id": user_id}

    # Test error case
    request = {"method": "GET", "path": "/users/999"}
    status, headers, body = await api._dispatch(get_user, request, handler_id=0)

    assert status == 404
    assert b"User not found" in body
```

## Advanced: Custom Error Handlers

For advanced use cases, you can import and use the error handlers directly:

```python
from django_bolt.error_handlers import (
    handle_exception,
    http_exception_handler,
    request_validation_error_handler,
)

# Manually handle an exception
status, headers, body = handle_exception(
    exc=ValueError("Custom error"),
    debug=True,
    request=request_dict
)
```

## Migration from Django REST Framework

If migrating from Django REST Framework:

| DRF | Django-Bolt |
|-----|-------------|
| `ValidationError` | `RequestValidationError` |
| `NotFound` | `NotFound` |
| `PermissionDenied` | `Forbidden` |
| `AuthenticationFailed` | `Unauthorized` |
| `APIException` | `HTTPException` |

Example migration:

```python
# DRF
from rest_framework.exceptions import ValidationError, NotFound

def get_user(user_id):
    if not user:
        raise NotFound("User not found")
    if not valid:
        raise ValidationError({"email": ["Invalid format"]})

# Django-Bolt
from django_bolt.exceptions import NotFound, RequestValidationError

async def get_user(user_id: int):
    if not user:
        raise NotFound(detail="User not found")
    if not valid:
        raise RequestValidationError([
            {"loc": ["body", "email"], "msg": "Invalid format", "type": "value_error"}
        ])
```

## See Also

- [LOGGING.md](LOGGING.md) - Request/response logging configuration
- [Authentication & Guards](../README.md#authentication) - Authentication and permission errors
- [Validation](../README.md#request-validation) - Request/response validation

# OpenAPI Error Response Documentation

## Overview

Django-Bolt automatically documents **422 Unprocessable Entity** validation errors in the OpenAPI schema for endpoints that accept request bodies. This follows the **FastAPI-compatible** error format.

## Error Response Format

### 422 Validation Error (FastAPI-Compatible)

When a request body fails validation, Django-Bolt returns a 422 response with this structure:

```json
{
  "detail": [
    {
      "type": "validation_error",
      "loc": ["body", "is_active"],
      "msg": "Expected `bool`, got `int`",
      "input": 1
    }
  ]
}
```

**Field Descriptions:**
- `detail`: Array of validation error objects (FastAPI format)
- `type`: Error type (e.g., `validation_error`, `missing_field`, `json_invalid`)
- `loc`: Array representing the location of the error (e.g., `["body", "field_name"]`)
- `msg`: Human-readable error message
- `input`: (Optional) The invalid input value that caused the error

### OpenAPI Schema

The OpenAPI schema automatically includes the 422 response for endpoints with request bodies:

```yaml
responses:
  '200':
    description: Successful response
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/YourResponseModel'
  '422':
    description: Validation Error - Request data failed validation
    content:
      application/json:
        schema:
          type: object
          required:
            - detail
          properties:
            detail:
              type: array
              description: List of validation errors
              items:
                type: object
                required:
                  - type
                  - loc
                  - msg
                properties:
                  type:
                    type: string
                    description: Error type
                    example: validation_error
                  loc:
                    type: array
                    description: Location of the error (field path)
                    items:
                      oneOf:
                        - type: string
                        - type: integer
                    example: ["body", "is_active"]
                  msg:
                    type: string
                    description: Error message
                    example: "Expected `bool`, got `int`"
                  input:
                    description: The input value that caused the error (optional)
```

## When 422 is Documented

The 422 response is **automatically included** in the OpenAPI schema when:

✅ Endpoint has a request body (JSON struct, form data, or file upload)
✅ `include_error_responses=True` in OpenAPIConfig (default)

The 422 response is **NOT included** when:

❌ Endpoint has no request body (GET, DELETE, HEAD, OPTIONS)
❌ `include_error_responses=False` in OpenAPIConfig

## Configuration

### Enable/Disable Error Responses

```python
from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig

# Include 422 validation errors (default)
api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        include_error_responses=True  # Default
    )
)

# Only show successful responses
api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        include_error_responses=False
    )
)
```

## Examples

### Endpoint with Request Body

```python
import msgspec
from django_bolt import BoltAPI

api = BoltAPI(openapi_config=OpenAPIConfig(title="API", version="1.0.0"))

class User(msgspec.Struct):
    username: str
    email: str
    is_active: bool

@api.post("/users")
async def create_user(user: User):
    return {"id": 1, "username": user.username}
```

**OpenAPI Documentation:**
- ✅ 200: Successful response
- ✅ 422: Validation error (automatically added)

### Endpoint without Request Body

```python
@api.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "username": "john"}
```

**OpenAPI Documentation:**
- ✅ 200: Successful response
- ❌ 422: NOT included (no request body)

## Standard HTTP Errors (NOT Documented)

The following standard HTTP errors are **NOT** included in the OpenAPI schema because they are well-understood HTTP standards:

- **400 Bad Request**: Malformed request
- **401 Unauthorized**: Authentication required/failed
- **403 Forbidden**: Insufficient permissions
- **500 Internal Server Error**: Unexpected server errors

These errors are still returned by Django-Bolt at runtime, they just aren't documented in the OpenAPI schema to avoid clutter.

## Compatibility

This implementation is **100% compatible with FastAPI's error format**, making it easy to migrate between frameworks or use the same client code.

### Comparison with FastAPI

**Django-Bolt:**
```json
{
  "detail": [
    {"type": "validation_error", "loc": ["body", "field"], "msg": "Error message"}
  ]
}
```

**FastAPI:**
```json
{
  "detail": [
    {"type": "value_error", "loc": ["body", "field"], "msg": "Error message"}
  ]
}
```

Both use the exact same structure: `{"detail": [array of errors]}`.

## Testing

See [test_openapi_errors.py](../test_openapi_errors.py) for comprehensive test coverage.

---
icon: lucide/code
---

# BoltAPI Reference

This page documents the `BoltAPI` class and its methods.

## BoltAPI

The main class for creating Django-Bolt APIs.

```python
from django_bolt import BoltAPI

api = BoltAPI()
```

### Constructor

```python
BoltAPI(
    openapi_config=None,       # OpenAPIConfig for documentation
    compression=None,          # CompressionConfig for response compression
    default_auth=None,         # Default authentication backends
    default_guards=None,       # Default permission guards
    middleware=None,           # List of middleware classes
)
```

### Route decorators

#### @api.get(path, **options)

Register a GET endpoint.

```python
@api.get("/users")
async def list_users():
    return []
```

#### @api.post(path, **options)

Register a POST endpoint.

```python
@api.post("/users")
async def create_user():
    return {}
```

#### @api.put(path, **options)

Register a PUT endpoint.

#### @api.patch(path, **options)

Register a PATCH endpoint.

#### @api.delete(path, **options)

Register a DELETE endpoint.

#### @api.head(path, **options)

Register a HEAD endpoint.

#### @api.options(path, **options)

Register an OPTIONS endpoint.

### Route options

All route decorators accept these options:

| Option | Type | Description |
|--------|------|-------------|
| `status_code` | `int` | Default response status code |
| `response_model` | `type` | Schema for response validation |
| `summary` | `str` | Short description for OpenAPI |
| `description` | `str` | Detailed description for OpenAPI |
| `tags` | `list[str]` | OpenAPI tags for grouping |
| `auth` | `list` | Authentication backends |
| `guards` | `list` | Permission guards |
| `include_in_schema` | `bool` | Include in OpenAPI docs |

### Class-based view decorators

#### @api.view(path)

Register a class-based view (APIView).

```python
@api.view("/resource")
class ResourceView(APIView):
    async def get(self, request):
        return {}
```

#### @api.viewset(path)

Register a ViewSet with automatic CRUD routing.

```python
@api.viewset("/items")
class ItemViewSet(ViewSet):
    async def list(self, request):
        return []
```

### WebSocket decorator

#### @api.websocket(path)

Register a WebSocket endpoint.

```python
@api.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    await websocket.accept()
```

### API mounting

#### api.mount(prefix, other_api)

Mount another BoltAPI under a prefix.

```python
api.mount("/v1", v1_api)
```

## Dependency injection

### Depends

Mark a parameter as a dependency.

```python
from django_bolt import Depends

async def get_db():
    return Database()

@api.get("/data")
async def get_data(db=Depends(get_db)):
    return db.query()
```

Dependencies can:

- Return any value
- Be async or sync functions
- Have their own dependencies
- Access request parameters

### get_current_user

Built-in dependency for getting the authenticated user.

```python
from django_bolt.auth import get_current_user

@api.get("/me", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def me(user=Depends(get_current_user)):
    return {"username": user.username}
```

## Request object

The request dict contains:

| Key | Type | Description |
|-----|------|-------------|
| `method` | `str` | HTTP method |
| `path` | `str` | Request path |
| `query` | `dict` | Query parameters |
| `params` | `dict` | Path parameters |
| `headers` | `dict` | Request headers |
| `body` | `bytes` | Raw request body |
| `context` | `dict` | Authentication context |

### Type-safe Request

```python
from django_bolt import Request

@api.get("/info")
async def info(request: Request):
    user = request.user        # Lazy-loaded Django user
    context = request.context  # Auth context dict
```

## Exceptions

### HTTPException

Base class for HTTP errors.

```python
from django_bolt.exceptions import HTTPException

raise HTTPException(status_code=404, detail="Not found")
```

### Built-in exceptions

| Exception | Status Code |
|-----------|-------------|
| `BadRequest` | 400 |
| `Unauthorized` | 401 |
| `Forbidden` | 403 |
| `NotFound` | 404 |
| `MethodNotAllowed` | 405 |
| `Conflict` | 409 |
| `UnprocessableEntity` | 422 |
| `InternalServerError` | 500 |

```python
from django_bolt.exceptions import NotFound, BadRequest

raise NotFound(detail="User not found")
raise BadRequest(detail="Invalid input")
```

### RequestValidationError

For validation errors with field-level details.

```python
from django_bolt.exceptions import RequestValidationError

errors = [
    {"loc": ["body", "email"], "msg": "Invalid email", "type": "value_error"}
]
raise RequestValidationError(errors)
```

## Parameter markers

### Header

Extract a header value.

```python
from django_bolt.param_functions import Header

async def handler(auth: Annotated[str, Header(alias="Authorization")]):
    pass
```

### Cookie

Extract a cookie value.

```python
from django_bolt.param_functions import Cookie

async def handler(session: Annotated[str, Cookie(alias="sessionid")]):
    pass
```

### Form

Extract form data.

```python
from django_bolt.param_functions import Form

async def handler(username: Annotated[str, Form()]):
    pass
```

### File

Extract uploaded files.

```python
from django_bolt.param_functions import File

async def handler(files: Annotated[list[dict], File(alias="file")]):
    pass
```

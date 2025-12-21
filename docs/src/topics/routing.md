---
icon: lucide/route
---

# Routing

This guide explains how routing works in Django-Bolt and covers all the ways you can define API endpoints.

## Basic routing

Routes are defined using decorator methods on a `BoltAPI` instance:

```python
from django_bolt import BoltAPI

api = BoltAPI()

@api.get("/users")
async def list_users():
    return {"users": []}

@api.post("/users")
async def create_user():
    return {"created": True}
```

## HTTP methods

Django-Bolt supports all common HTTP methods:

| Decorator | HTTP Method | Typical use |
|-----------|-------------|-------------|
| `@api.get()` | GET | Retrieve resources |
| `@api.post()` | POST | Create resources |
| `@api.put()` | PUT | Replace resources |
| `@api.patch()` | PATCH | Partial updates |
| `@api.delete()` | DELETE | Remove resources |
| `@api.head()` | HEAD | Get headers only |
| `@api.options()` | OPTIONS | Get allowed methods |

Example with all methods:

```python
@api.get("/items")
async def list_items():
    return {"items": []}

@api.post("/items")
async def create_item():
    return {"created": True}

@api.put("/items/{item_id}")
async def replace_item(item_id: int):
    return {"replaced": True}

@api.patch("/items/{item_id}")
async def update_item(item_id: int):
    return {"updated": True}

@api.delete("/items/{item_id}")
async def delete_item(item_id: int):
    return {"deleted": True}

@api.head("/items")
async def head_items():
    return {}  # Body not sent for HEAD

@api.options("/items")
async def options_items():
    from django_bolt import Response
    return Response({}, headers={"Allow": "GET, POST, PUT, PATCH, DELETE"})
```

## Path parameters

Capture dynamic segments of the URL using curly braces:

```python
@api.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

@api.get("/posts/{post_id}/comments/{comment_id}")
async def get_comment(post_id: int, comment_id: int):
    return {"post_id": post_id, "comment_id": comment_id}
```

Path parameters are automatically converted to the type specified in the function signature:

- `user_id: int` - converts to integer, returns 422 if not a valid integer
- `user_id: str` - keeps as string (default)
- `user_id: float` - converts to float

## Query parameters

Function parameters that don't match path placeholders become query parameters:

```python
@api.get("/search")
async def search(q: str, page: int = 1, limit: int = 10):
    return {"query": q, "page": page, "limit": limit}
```

- `q` is required (no default value)
- `page` and `limit` are optional with defaults

Request: `GET /search?q=python&page=2`

Response: `{"query": "python", "page": 2, "limit": 10}`

### Optional parameters

Use `| None` with a default of `None` for truly optional parameters:

```python
@api.get("/items")
async def list_items(category: str | None = None, sort: str | None = None):
    return {"category": category, "sort": sort}
```

## Request body

Accept JSON request bodies using `msgspec.Struct`:

```python
import msgspec

class CreateUser(msgspec.Struct):
    username: str
    email: str
    age: int | None = None

@api.post("/users")
async def create_user(user: CreateUser):
    return {"username": user.username, "email": user.email}
```

The request body is automatically validated. Invalid data returns a 422 error.

## Headers

Extract header values using `Annotated` with `Header`:

```python
from typing import Annotated
from django_bolt.param_functions import Header

@api.get("/protected")
async def protected(authorization: Annotated[str, Header(alias="Authorization")]):
    return {"auth": authorization}
```

The `alias` parameter specifies the actual header name (headers are case-insensitive).

## Cookies

Extract cookie values using `Annotated` with `Cookie`:

```python
from typing import Annotated
from django_bolt.param_functions import Cookie

@api.get("/session")
async def get_session(session_id: Annotated[str, Cookie(alias="session")]):
    return {"session_id": session_id}
```

## Form data

Accept form-urlencoded or multipart form data:

```python
from typing import Annotated
from django_bolt.param_functions import Form

@api.post("/login")
async def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()]
):
    return {"username": username}
```

## File uploads

Accept file uploads using `File`:

```python
from typing import Annotated
from django_bolt.param_functions import File

@api.post("/upload")
async def upload(files: Annotated[list[dict], File(alias="file")]):
    return {
        "uploaded": len(files),
        "names": [f.get("filename") for f in files]
    }
```

Each file in the list is a dict with:

- `filename` - original filename
- `content_type` - MIME type
- `size` - file size in bytes
- `content` - file content as bytes

## Route options

The route decorator accepts additional options:

```python
@api.get(
    "/users/{user_id}",
    status_code=200,           # Default response status code
    summary="Get user",        # Short description for OpenAPI
    description="Get a user by ID",  # Detailed description
    tags=["users"],            # OpenAPI tags for grouping
    response_model=UserSchema, # Response validation schema
)
async def get_user(user_id: int):
    """This docstring also appears in OpenAPI docs."""
    return {"user_id": user_id}
```

## Accessing the request object

Access the full request object as the first parameter:

```python
@api.get("/info")
async def request_info(request):
    return {
        "method": request.get("method"),
        "path": request.get("path"),
        "query": request.get("query"),
        "headers": dict(request.get("headers", {})),
    }
```

The request dict contains:

- `method` - HTTP method
- `path` - Request path
- `query` - Query parameters dict
- `headers` - Headers dict
- `params` - Path parameters dict
- `body` - Raw body bytes
- `context` - Authentication context (when auth is configured)

## Sync handlers

While async handlers are recommended, you can also use synchronous functions:

```python
@api.get("/sync")
def sync_handler():
    return {"sync": True}
```

Sync handlers are automatically wrapped to run in a thread pool.

## WebSocket routes

Define WebSocket endpoints using `@api.websocket()`:

```python
from django_bolt import WebSocket

@api.websocket("/ws/echo")
async def echo(websocket: WebSocket):
    await websocket.accept()
    async for message in websocket.iter_text():
        await websocket.send_text(f"Echo: {message}")
```

See the [WebSocket guide](websocket.md) for more details.

## Auto-discovery

Django-Bolt automatically discovers `api.py` files in:

1. Your project directory (where `settings.py` is)
2. Each installed Django app

All routes from discovered files are combined into a single router. This lets you organize routes per app:

```
myproject/
    myproject/
        settings.py
        api.py              # /health, /docs
    users/
        api.py              # /users, /users/{id}
    products/
        api.py              # /products, /products/{id}
```

## Multiple API instances

You can create multiple `BoltAPI` instances and mount them:

```python
# users/api.py
from django_bolt import BoltAPI

api = BoltAPI()

@api.get("/users")
async def list_users():
    return {"users": []}
```

```python
# myproject/api.py
from django_bolt import BoltAPI
from users.api import api as users_api

api = BoltAPI()

# Mount users API under /api/v1
api.mount("/api/v1", users_api)
```

Routes from `users_api` are now available at `/api/v1/users`.

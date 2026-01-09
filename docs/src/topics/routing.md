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

See [Request Handling](requests.md) for details on path parameters, query parameters, headers, cookies, form data, and file uploads.

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

## Trailing slash handling

Django-Bolt normalizes trailing slashes at route registration time. By default, trailing slashes are stripped from paths:

```python
api = BoltAPI()

@api.get("/users/")  # Registered as /users
async def list_users():
    return []
```

### Trailing slash modes

You can control this behavior with the `trailing_slash` parameter:

| Mode | Description | Example |
|------|-------------|---------|
| `"strip"` | Remove trailing slashes (default) | `/users/` → `/users` |
| `"append"` | Add trailing slashes | `/users` → `/users/` |
| `"keep"` | No normalization | `/users/` → `/users/` |

### Strip mode (default)

The default mode removes trailing slashes, which produces clean URLs:

```python
api = BoltAPI()  # trailing_slash="strip" is the default

@api.get("/users/")   # Accessible at /users
@api.get("/items")    # Accessible at /items
```

### Append mode

Use append mode to follow Django's URL convention where paths end with slashes:

```python
api = BoltAPI(trailing_slash="append")

@api.get("/users")    # Accessible at /users/
@api.get("/items/")   # Accessible at /items/
```

### Keep mode

Use keep mode when you need explicit control over each path:

```python
api = BoltAPI(trailing_slash="keep")

@api.get("/users")    # Accessible at /users
@api.get("/items/")   # Accessible at /items/
```

### Mounted APIs

When mounting APIs, the child API inherits the parent's `trailing_slash` setting:

```python
parent = BoltAPI(trailing_slash="append")
child = BoltAPI()

@child.get("/users")  # Will be at /api/users/ (inherits append mode)
async def list_users():
    return []

parent.mount("/api", child)
```

## URL prefix

Apply a prefix to all routes using the `prefix` parameter:

```python
api = BoltAPI(prefix="/api/v1")

@api.get("/users")  # Accessible at /api/v1/users
async def list_users():
    return []
```

This is useful for versioning your API or grouping routes under a common path.

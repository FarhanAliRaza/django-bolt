---
icon: lucide/file-code-2
---

# OpenAPI Documentation

Django-Bolt automatically generates OpenAPI documentation for your API. This guide covers how to configure and customize the documentation.

## Accessing the documentation

By default, documentation is available at:

- `/docs` - Interactive Swagger UI

Start your server and visit `http://localhost:8000/docs`.

## Configuring OpenAPI

Customize the documentation using `OpenAPIConfig`:

```python
from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        description="API for my application",
        enabled=True,
    )
)
```

## Available options

```python
OpenAPIConfig(
    title="My API",              # API title
    version="1.0.0",             # API version
    description="Description",   # API description
    enabled=True,                # Enable/disable docs
    docs_url="/docs",            # Swagger UI URL
    openapi_url="/openapi.json", # OpenAPI JSON URL
    django_auth=False,           # Enable Django admin auth for docs
)
```

## Documenting endpoints

### Summary and description

```python
@api.get(
    "/users/{user_id}",
    summary="Get a user",
    description="Retrieve a user by their unique ID.",
    tags=["users"]
)
async def get_user(user_id: int):
    """
    This docstring also appears in the documentation.

    Additional details about the endpoint can go here.
    """
    return {"user_id": user_id}
```

### Tags

Group endpoints using tags:

```python
@api.get("/users", tags=["users"])
async def list_users():
    return []

@api.post("/users", tags=["users"])
async def create_user():
    return {}

@api.get("/articles", tags=["articles"])
async def list_articles():
    return []
```

Tags appear as sections in the Swagger UI.

### Response models

Document response schemas:

```python
import msgspec

class User(msgspec.Struct):
    id: int
    username: str
    email: str

@api.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    return {"id": user_id, "username": "john", "email": "john@example.com"}
```

The schema is automatically generated from the `msgspec.Struct`.

### Request body schemas

Request bodies are documented automatically:

```python
class CreateUser(msgspec.Struct):
    username: str
    email: str
    password: str

@api.post("/users")
async def create_user(user: CreateUser):
    return {"id": 1, "username": user.username}
```

### Status codes

Document the default status code:

```python
@api.post("/users", status_code=201)
async def create_user():
    return {"id": 1}
```

## Alternative documentation UIs

Django-Bolt supports multiple documentation renderers:

### Swagger UI (default)

```python
from django_bolt.openapi import SwaggerRenderPlugin

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        render_plugin=SwaggerRenderPlugin(),
    )
)
```

### ReDoc

```python
from django_bolt.openapi import RedocRenderPlugin

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        render_plugin=RedocRenderPlugin(),
    )
)
```

### Scalar

```python
from django_bolt.openapi import ScalarRenderPlugin

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        render_plugin=ScalarRenderPlugin(),
    )
)
```

### Stoplight Elements

```python
from django_bolt.openapi import StoplightRenderPlugin

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        render_plugin=StoplightRenderPlugin(),
    )
)
```

### RapiDoc

```python
from django_bolt.openapi import RapidocRenderPlugin

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        render_plugin=RapidocRenderPlugin(),
    )
)
```

## Raw OpenAPI JSON/YAML

Access the raw OpenAPI specification:

- `/openapi.json` - JSON format
- `/openapi.yaml` - YAML format

```python
from django_bolt.openapi import JsonRenderPlugin, YamlRenderPlugin
```

## Protecting documentation

### Django admin authentication

Require Django admin login to access docs:

```python
api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        django_auth=True,  # Requires Django admin login
    )
)
```

### Disabling documentation

Disable documentation in production:

```python
import os

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        enabled=os.environ.get("DEBUG", "false").lower() == "true",
    )
)
```

## Parameter documentation

Parameters are documented automatically from function signatures:

```python
@api.get("/search")
async def search(
    q: str,           # Required query parameter
    page: int = 1,    # Optional with default
    limit: int = 20,  # Optional with default
):
    """
    Search for items.

    - **q**: Search query string (required)
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20)
    """
    return {"query": q, "page": page, "limit": limit}
```

## Hiding endpoints

Exclude endpoints from documentation:

```python
@api.get("/internal", include_in_schema=False)
async def internal():
    return {"internal": True}
```

## OpenAPI extensions

The generated OpenAPI spec follows the OpenAPI 3.1.0 specification and includes:

- Path parameters with types
- Query parameters with defaults
- Request body schemas from `msgspec.Struct`
- Response schemas from `response_model`
- Authentication requirements from `auth=` and `guards=`
- Tag grouping
- Operation summaries and descriptions

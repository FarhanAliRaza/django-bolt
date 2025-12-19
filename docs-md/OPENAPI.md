# OpenAPI Documentation Guide

Django-Bolt provides comprehensive OpenAPI 3.1 documentation generation with multiple interactive UI options. The OpenAPI implementation is adapted from [Litestar](https://github.com/litestar-org/litestar) and provides automatic schema generation, validation error documentation, and security scheme integration.

## Table of Contents

- [Quick Start](#quick-start)
- [Render Plugins](#render-plugins)
  - [Scalar (Default)](#scalar-default)
  - [Swagger UI](#swagger-ui)
  - [ReDoc](#redoc)
  - [RapiDoc](#rapidoc)
  - [Stoplight Elements](#stoplight-elements)
  - [JSON](#json)
  - [YAML](#yaml)
- [OpenAPI Configuration](#openapi-configuration)
- [Schema Generation](#schema-generation)
  - [From msgspec.Struct](#from-msgspecstruct)
  - [From Route Handlers](#from-route-handlers)
  - [From Docstrings](#from-docstrings)
- [Security Schemes](#security-schemes)
- [Response Documentation](#response-documentation)
- [Validation Error Schemas](#validation-error-schemas)
- [Customizing OpenAPI Metadata](#customizing-openapi-metadata)
- [Multiple UI Plugins](#multiple-ui-plugins)
- [Excluding Routes](#excluding-routes)
- [Disabling OpenAPI](#disabling-openapi)
- [Protecting Docs with Django Authentication](#protecting-docs-with-django-authentication)
- [Best Practices](#best-practices)

---

## Quick Start

OpenAPI documentation is enabled by default with Swagger UI. Simply create a BoltAPI instance and your docs will be available at `/docs`:

```python
from django_bolt import BoltAPI
import msgspec

api = BoltAPI()

class Item(msgspec.Struct):
    name: str
    price: float

@api.post("/items", response_model=Item)
async def create_item(item: Item) -> Item:
    """Create a new item."""
    return item
```

**Available endpoints:**
- `/docs` - Swagger UI (default)
- `/docs/openapi.json` - JSON schema
- `/docs/openapi.yaml` - YAML schema
- `/docs/redoc` - ReDoc UI
- `/docs/scalar` - Scalar UI
- `/docs/rapidoc` - RapiDoc UI
- `/docs/stoplight` - Stoplight Elements UI

### Custom Configuration

```python
from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig, SwaggerRenderPlugin

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        description="A comprehensive API for managing resources",
        render_plugins=[SwaggerRenderPlugin()]
    )
)
```

---

## Render Plugins

Django-Bolt supports 7 different OpenAPI documentation renderers. Each plugin serves interactive documentation at a specific path.

By default, all UI plugins are enabled with Swagger UI as the default at the root path (`/docs`).

### Swagger UI (Default)

The classic OpenAPI documentation interface with try-it-out functionality. This is the default UI served at `/docs`.

```python
from django_bolt.openapi import SwaggerRenderPlugin

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        render_plugins=[SwaggerRenderPlugin(path="/")]  # Serve at root
    )
)
```

**Paths:** `/docs/swagger` or `/docs` (when configured as root)

**Options:**
```python
SwaggerRenderPlugin(
    version="5.18.2",                    # Swagger UI version from CDN
    js_url=None,                         # Custom JS bundle URL
    css_url=None,                        # Custom CSS bundle URL
    standalone_preset_js_url=None,       # Custom preset JS URL
    path="/swagger"                      # Path to serve at
)
```

### Scalar

Modern, fast, and feature-rich OpenAPI documentation viewer.

```python
from django_bolt.openapi import OpenAPIConfig, ScalarRenderPlugin

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        render_plugins=[ScalarRenderPlugin()]
    )
)
```

**Paths:** `/docs/scalar`

**Options:**
```python
ScalarRenderPlugin(
    version="latest",              # Scalar version from CDN
    js_url=None,                   # Custom JS bundle URL
    css_url=None,                  # Custom CSS URL (uses Litestar branding by default)
    path=["/scalar", "/"],         # Paths to serve at
    options={                      # Scalar configuration options
        "theme": "purple",
        "darkMode": True
    }
)
```

### ReDoc

Clean, three-panel OpenAPI documentation with search and navigation.

```python
from django_bolt.openapi import RedocRenderPlugin

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        render_plugins=[RedocRenderPlugin()]
    )
)
```

**Paths:** `/docs/redoc`

**Options:**
```python
RedocRenderPlugin(
    version="next",              # Redoc version from CDN
    js_url=None,                 # Custom JS bundle URL
    google_fonts=True,           # Load Google Fonts via CDN
    path="/redoc"                # Path to serve at
)
```

### RapiDoc

Highly customizable OpenAPI documentation with multiple layout options.

```python
from django_bolt.openapi import RapidocRenderPlugin

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        render_plugins=[RapidocRenderPlugin()]
    )
)
```

**Paths:** `/docs/rapidoc`

**Options:**
```python
RapidocRenderPlugin(
    version="9.3.4",             # Rapidoc version from CDN
    js_url=None,                 # Custom JS bundle URL
    path="/rapidoc"              # Path to serve at
)
```

### Stoplight Elements

Beautiful, developer-friendly API documentation powered by Stoplight.

```python
from django_bolt.openapi import StoplightRenderPlugin

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        render_plugins=[StoplightRenderPlugin()]
    )
)
```

**Paths:** `/docs/stoplight`

**Options:**
```python
StoplightRenderPlugin(
    version="7.7.18",            # Stoplight Elements version from CDN
    js_url=None,                 # Custom JS bundle URL
    css_url=None,                # Custom CSS bundle URL
    path="/elements"             # Path to serve at
)
```

### JSON

Returns the raw OpenAPI schema as JSON.

```python
from django_bolt.openapi import JsonRenderPlugin

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        render_plugins=[JsonRenderPlugin()]
    )
)
```

**Paths:** `/docs/openapi.json` (automatically registered)

**Content-Type:** `application/vnd.oai.openapi+json`

**Note:** JSON endpoint is always available, even if not explicitly added to render_plugins.

### YAML

Returns the raw OpenAPI schema as YAML.

```python
from django_bolt.openapi import YamlRenderPlugin

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        render_plugins=[YamlRenderPlugin()]
    )
)
```

**Paths:** `/docs/openapi.yaml`, `/docs/openapi.yml` (automatically registered)

**Content-Type:** `text/yaml; charset=utf-8`

**Note:** YAML endpoints are always available. Requires PyYAML (`pip install pyyaml`).

---

## OpenAPI Configuration

The `OpenAPIConfig` class provides comprehensive control over documentation generation.

### Basic Configuration

```python
from django_bolt.openapi import OpenAPIConfig

config = OpenAPIConfig(
    title="My API",                    # Required: API title
    version="1.0.0",                   # Required: API version
    description="API description",     # Optional: API description
    path="/docs"                       # Optional: Base path for docs (default: "/docs")
)
```

### Complete Configuration

```python
from django_bolt.openapi import (
    OpenAPIConfig,
    SwaggerRenderPlugin,
    RedocRenderPlugin
)
from django_bolt.openapi.spec import (
    Contact,
    License,
    Server,
    Tag,
    ExternalDocumentation
)

config = OpenAPIConfig(
    # Required
    title="My API",
    version="1.0.0",

    # Basic Info
    description="Comprehensive API for resource management",
    summary="Resource Management API",
    terms_of_service="https://example.com/terms",

    # Contact Info
    contact=Contact(
        name="API Support",
        email="support@example.com",
        url="https://example.com/support"
    ),

    # License
    license=License(
        name="MIT",
        url="https://opensource.org/licenses/MIT"
    ),

    # External Documentation
    external_docs=ExternalDocumentation(
        url="https://docs.example.com",
        description="Full API documentation"
    ),

    # Servers
    servers=[
        Server(url="https://api.example.com", description="Production"),
        Server(url="https://staging.example.com", description="Staging"),
        Server(url="http://localhost:8000", description="Development")
    ],

    # Tags for grouping operations
    tags=[
        Tag(name="Users", description="User management endpoints"),
        Tag(name="Items", description="Item management endpoints")
    ],

    # Documentation Paths
    path="/docs",                      # Base path (default: "/docs")

    # Render Plugins
    render_plugins=[
        SwaggerRenderPlugin(),         # Swagger UI at /docs/swagger
        RedocRenderPlugin()            # ReDoc at /docs/redoc
    ],

    # Auto-documentation
    use_handler_docstrings=True,       # Extract docs from handler docstrings (default: True)

    # Error Responses
    include_error_responses=True,      # Include 422 validation errors (default: True)

    # Path Exclusions
    exclude_paths=[                    # Paths to exclude from schema (default: ["/admin", "/static"])
        "/admin",
        "/static",
        "/internal"
    ]
)

api = BoltAPI(openapi_config=config)
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | `str` | **Required** | API title |
| `version` | `str` | **Required** | API version |
| `description` | `str \| None` | `None` | API description (supports CommonMark) |
| `summary` | `str \| None` | `None` | Short summary text |
| `contact` | `Contact \| None` | `None` | Contact information |
| `license` | `License \| None` | `None` | License information |
| `terms_of_service` | `str \| None` | `None` | Terms of service URL |
| `external_docs` | `ExternalDocumentation \| None` | `None` | External documentation link |
| `servers` | `List[Server]` | `[Server(url="/")]` | Server configurations |
| `tags` | `List[Tag] \| None` | `None` | Operation grouping tags |
| `path` | `str` | `"/docs"` | Base path for documentation endpoints |
| `render_plugins` | `List[OpenAPIRenderPlugin]` | All UI plugins with Swagger at root | UI plugins |
| `enabled` | `bool` | `True` | Enable/disable OpenAPI documentation |
| `use_handler_docstrings` | `bool` | `True` | Extract operation descriptions from docstrings |
| `include_error_responses` | `bool` | `True` | Include 422 validation error responses |
| `exclude_paths` | `List[str]` | `["/admin", "/static"]` | Path prefixes to exclude from schema |
| `security` | `List[SecurityRequirement] \| None` | `None` | Global security requirements |
| `components` | `Components` | `Components()` | Reusable components |
| `webhooks` | `Dict[str, PathItem \| Reference] \| None` | `None` | Webhook definitions |
| `django_auth` | `Callable \| bool \| None` | `None` | Django auth decorator for docs protection |

---

## Schema Generation

Django-Bolt automatically generates OpenAPI schemas from your route handlers, type annotations, and msgspec.Struct definitions.

### From msgspec.Struct

Request and response bodies defined with msgspec.Struct are automatically converted to OpenAPI schemas with full validation rules.

```python
import msgspec
from typing import Optional

class User(msgspec.Struct):
    """User model."""
    username: str
    email: str
    age: int
    is_active: Optional[bool] = True

@api.post("/users", response_model=User)
async def create_user(user: User) -> User:
    """Create a new user."""
    return user
```

**Generated Schema:**
```yaml
components:
  schemas:
    User:
      type: object
      required:
        - username
        - email
        - age
      properties:
        username:
          type: string
        email:
          type: string
        age:
          type: integer
        is_active:
          type: boolean
```

**Supported Types:**
- `str` → `string`
- `int` → `integer`
- `float` → `number`
- `bool` → `boolean`
- `bytes` → `string` (format: binary)
- `List[T]` → `array` (items: T)
- `Dict[K, V]` → `object` (additionalProperties: true)
- `Optional[T]` → Makes field optional
- `msgspec.Struct` → Referenced schema in components

### From Route Handlers

Parameters are extracted from function signatures and type annotations.

```python
from typing import Annotated, Optional
from django_bolt.param_functions import Header, Cookie, Form, File

@api.get("/items/{item_id}")
async def get_item(
    item_id: int,                                    # Path parameter
    q: Optional[str] = None,                         # Query parameter
    api_key: Annotated[str, Header(alias="x-api-key")] = None,  # Header
    session: Annotated[str, Cookie()] = None         # Cookie
):
    """Get an item by ID with optional filtering."""
    return {"item_id": item_id, "q": q}
```

**Generated Parameters:**
```yaml
parameters:
  - name: item_id
    in: path
    required: true
    schema:
      type: integer
  - name: q
    in: query
    required: false
    schema:
      type: string
  - name: x-api-key
    in: header
    required: false
    schema:
      type: string
  - name: session
    in: cookie
    required: false
    schema:
      type: string
```

### From Docstrings

Operation descriptions are automatically extracted from handler docstrings when `use_handler_docstrings=True` (default).

```python
@api.get("/items/{item_id}")
async def get_item(item_id: int):
    """Get an item by ID.

    This endpoint retrieves a single item from the database
    using its unique identifier.

    Returns:
        Item: The requested item with all its properties.
    """
    return {"item_id": item_id}
```

**Generated Operation:**
```yaml
get:
  summary: Get an item by ID.
  description: |
    This endpoint retrieves a single item from the database
    using its unique identifier.

    Returns:
        Item: The requested item with all its properties.
  operationId: get_get_item
```

**Docstring Format:**
- **First line** → `summary`
- **Remaining lines** → `description`
- Cleaned with `inspect.cleandoc()` for proper formatting

**Disable docstrings:**
```python
config = OpenAPIConfig(
    title="My API",
    version="1.0.0",
    use_handler_docstrings=False  # Don't extract from docstrings
)
```

### Auto-Generated Tags

Operations are automatically tagged based on their module name for organization:

```python
# In myapp/api.py
@api.get("/items")
async def list_items():
    return []

# Generated tag: "Myapp"
```

**Tag Extraction Logic:**
1. Extract module name from handler's `__module__` attribute
2. Use last component (e.g., `"myapp.api"` → `"api"`)
3. If last component is `"api"`, use second-to-last (e.g., `"myapp.api"` → `"myapp"`)
4. Capitalize the tag name

---

## Security Schemes

Django-Bolt automatically documents authentication requirements and generates security schemes in the OpenAPI spec.

### JWT Authentication

```python
from django_bolt.auth import JWTAuthentication, IsAuthenticated

jwt_auth = JWTAuthentication(
    secret="your-secret-key",
    algorithms=["HS256"]
)

@api.get("/protected", auth=[jwt_auth], guards=[IsAuthenticated()])
async def protected_route(request):
    """Protected endpoint requiring JWT authentication."""
    auth = request.get("auth", {})
    return {"user_id": auth.get("user_id")}
```

**Generated Security:**
```yaml
paths:
  /protected:
    get:
      security:
        - BearerAuth: []

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

### API Key Authentication

```python
from django_bolt.auth import APIKeyAuthentication, IsAuthenticated

api_key_auth = APIKeyAuthentication(
    api_keys={"key1", "key2"},
    header="x-api-key"
)

@api.get("/api/data", auth=[api_key_auth], guards=[IsAuthenticated()])
async def get_data(request):
    """Endpoint requiring API key authentication."""
    return {"data": "sensitive"}
```

**Generated Security:**
```yaml
paths:
  /api/data:
    get:
      security:
        - ApiKeyAuth: []

components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: x-api-key
```

### Multiple Authentication Methods

```python
from django_bolt.auth import JWTAuthentication, APIKeyAuthentication

jwt_auth = JWTAuthentication(secret="secret")
api_key_auth = APIKeyAuthentication(api_keys={"key1"})

# Both JWT and API key accepted
@api.get("/flexible", auth=[jwt_auth, api_key_auth], guards=[IsAuthenticated()])
async def flexible_auth(request):
    """Accepts either JWT or API key."""
    return {"status": "ok"}
```

**Generated Security:**
```yaml
security:
  - BearerAuth: []
  - ApiKeyAuth: []
```

**Note:** Security schemes are automatically detected from route handlers with authentication backends. No manual configuration needed.

---

## Response Documentation

Django-Bolt documents successful responses based on `response_model` or return type annotations.

### Response Model

```python
class Item(msgspec.Struct):
    id: int
    name: str
    price: float

@api.post("/items", response_model=Item)
async def create_item(item: Item) -> Item:
    """Create a new item."""
    return item
```

**Generated Response:**
```yaml
responses:
  '200':
    description: Successful response
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Item'
```

### Return Type Annotation

```python
@api.get("/items", response_model=list[Item])
async def list_items() -> list[Item]:
    """List all items."""
    return []
```

**Generated Response:**
```yaml
responses:
  '200':
    description: Successful response
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/Item'
```

### Custom Status Codes

```python
from django_bolt import JSON

@api.post("/items")
async def create_item(item: Item):
    """Create a new item."""
    return JSON(item, status_code=201)
```

**Note:** Custom status codes are not yet automatically detected. Default is 200.

---

## Validation Error Schemas

Django-Bolt automatically documents 422 Unprocessable Entity responses for endpoints with request bodies. This follows the FastAPI-compatible error format.

### Automatic 422 Documentation

```python
class User(msgspec.Struct):
    username: str
    email: str
    is_active: bool

@api.post("/users")
async def create_user(user: User):
    """Create a new user."""
    return {"id": 1}
```

**Generated Responses:**
```yaml
responses:
  '200':
    description: Successful response
    content:
      application/json:
        schema:
          type: object
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

### When 422 is Included

422 responses are **automatically added** when:
- Endpoint accepts a request body (JSON, form data, or file upload)
- `include_error_responses=True` (default)

422 responses are **NOT added** when:
- Endpoint has no request body (GET, DELETE, HEAD, OPTIONS)
- `include_error_responses=False`

### Disable Validation Error Documentation

```python
config = OpenAPIConfig(
    title="My API",
    version="1.0.0",
    include_error_responses=False  # Don't document 422 responses
)
```

### Example Validation Error Response

When a client sends invalid data:

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "is_active": 1}'
```

**Response (422):**
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

**See Also:** [OPENAPI_ERROR_RESPONSES.md](/home/farhan/code/django-bolt/docs/OPENAPI_ERROR_RESPONSES.md) for detailed documentation.

---

## Customizing OpenAPI Metadata

### Contact Information

```python
from django_bolt.openapi.spec import Contact

config = OpenAPIConfig(
    title="My API",
    version="1.0.0",
    contact=Contact(
        name="API Support Team",
        email="support@example.com",
        url="https://example.com/support"
    )
)
```

### License

```python
from django_bolt.openapi.spec import License

config = OpenAPIConfig(
    title="My API",
    version="1.0.0",
    license=License(
        name="Apache 2.0",
        url="https://www.apache.org/licenses/LICENSE-2.0.html"
    )
)
```

### Servers

```python
from django_bolt.openapi.spec import Server

config = OpenAPIConfig(
    title="My API",
    version="1.0.0",
    servers=[
        Server(
            url="https://api.example.com/v1",
            description="Production server"
        ),
        Server(
            url="https://staging-api.example.com/v1",
            description="Staging server"
        ),
        Server(
            url="http://localhost:8000",
            description="Development server"
        )
    ]
)
```

### Tags for Organization

```python
from django_bolt.openapi.spec import Tag

config = OpenAPIConfig(
    title="My API",
    version="1.0.0",
    tags=[
        Tag(
            name="Users",
            description="User management endpoints"
        ),
        Tag(
            name="Items",
            description="Item management and inventory"
        ),
        Tag(
            name="Admin",
            description="Administrative operations"
        )
    ]
)
```

### External Documentation

```python
from django_bolt.openapi.spec import ExternalDocumentation

config = OpenAPIConfig(
    title="My API",
    version="1.0.0",
    external_docs=ExternalDocumentation(
        url="https://docs.example.com",
        description="Complete API documentation and guides"
    )
)
```

---

## Multiple UI Plugins

You can serve multiple documentation UIs simultaneously:

```python
from django_bolt.openapi import (
    OpenAPIConfig,
    SwaggerRenderPlugin,
    RedocRenderPlugin,
    ScalarRenderPlugin,
    RapidocRenderPlugin
)

config = OpenAPIConfig(
    title="My API",
    version="1.0.0",
    render_plugins=[
        ScalarRenderPlugin(),      # /schema/ and /schema/scalar
        SwaggerRenderPlugin(),     # /schema/swagger
        RedocRenderPlugin(),       # /schema/redoc
        RapidocRenderPlugin()      # /schema/rapidoc
    ]
)

api = BoltAPI(openapi_config=config)
```

**Available endpoints:**
- `/schema/` - Scalar UI (first plugin with root path)
- `/schema/scalar` - Scalar UI
- `/schema/swagger` - Swagger UI
- `/schema/redoc` - ReDoc
- `/schema/rapidoc` - RapiDoc
- `/schema/openapi.json` - JSON schema (always available)
- `/schema/openapi.yaml` - YAML schema (always available)

**Note:** This example uses `/schema` as the base path. The default is `/docs`.

### Custom Plugin Paths

```python
ScalarRenderPlugin(path="/docs"),           # Custom path
SwaggerRenderPlugin(path=["/ui", "/swag"])  # Multiple paths
```

---

## Excluding Routes

### Exclude Specific Paths

```python
config = OpenAPIConfig(
    title="My API",
    version="1.0.0",
    exclude_paths=[
        "/admin",      # Django admin
        "/static",     # Static files
        "/internal",   # Internal endpoints
        "/debug"       # Debug endpoints
    ]
)
```

**How it works:**
- Paths are matched by **prefix**
- `/admin` excludes `/admin`, `/admin/users`, `/admin/settings`, etc.
- OpenAPI docs paths (e.g., `/schema/*`) are **always excluded** automatically
- Default exclusions: `["/admin", "/static"]`

### Include All Routes

```python
config = OpenAPIConfig(
    title="My API",
    version="1.0.0",
    exclude_paths=[]  # Empty list = include everything (except docs)
)
```

---

## Disabling OpenAPI

### Using enabled=False

The recommended way to disable OpenAPI documentation:

```python
from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        enabled=False  # Disable all doc endpoints
    )
)
```

This will prevent any documentation routes from being registered. All requests to `/docs/*` will return 404.

**Note:** When using multiple APIs with autodiscovery, the first API's `enabled` setting takes priority. If your main project API sets `enabled=False`, documentation will be disabled even if other discovered APIs have it enabled.

### Using openapi_config=None

Alternatively, you can pass `None`:

```python
api = BoltAPI(openapi_config=None)  # No OpenAPI docs
```

### Environment-based Configuration

```python
from django.conf import settings
from django_bolt.openapi import OpenAPIConfig

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        enabled=settings.DEBUG  # Only enable in development
    )
)
```

---

## Protecting Docs with Django Authentication

You can protect OpenAPI documentation using Django's built-in authentication decorators like `login_required` or `staff_member_required`. This is useful when you want to restrict access to API docs to authenticated users only.

### Using login_required (Shorthand)

The simplest way to require login is to set `django_auth=True`:

```python
from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        django_auth=True  # Requires Django login
    )
)
```

When a user visits `/docs` without being logged in, they will be redirected to Django's login page. After successful authentication, they'll be redirected back to the documentation.

### Using staff_member_required

For admin-only access to documentation:

```python
from django.contrib.admin.views.decorators import staff_member_required
from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        django_auth=staff_member_required  # Staff only
    )
)
```

### Using Custom Django Decorators

You can pass any Django view decorator:

```python
from django.contrib.auth.decorators import login_required, permission_required
from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig

# Require specific permission
api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        django_auth=permission_required("api.view_docs")
    )
)
```

### How It Works

When `django_auth` is configured:

1. A separate internal BoltAPI is created with `django_middleware=True`
2. All documentation routes are registered on this internal API
3. The Django decorator is applied to each handler
4. The internal API is mounted at the docs path (e.g., `/docs`)

This ensures Django session authentication works properly with the documentation endpoints while keeping your main API routes unchanged.

### Protected Routes

All documentation endpoints are protected:

- `/docs` - Root UI
- `/docs/openapi.json` - JSON schema
- `/docs/openapi.yaml` - YAML schema
- `/docs/swagger` - Swagger UI
- `/docs/redoc` - ReDoc UI
- `/docs/scalar` - Scalar UI
- `/docs/rapidoc` - RapiDoc UI
- `/docs/stoplight` - Stoplight Elements UI

### Configuration Options

| Value | Description |
|-------|-------------|
| `True` | Apply `login_required` (redirects to login page) |
| `login_required` | Explicit login required |
| `staff_member_required` | Requires staff status |
| `permission_required("perm")` | Requires specific permission |
| Custom decorator | Any Django view decorator |

---

## Best Practices

### 1. Use Descriptive Docstrings

```python
@api.post("/users", response_model=User)
async def create_user(user: User) -> User:
    """Create a new user account.

    Creates a new user in the system with the provided information.
    The username must be unique and the email must be a valid format.

    Args:
        user: User data including username, email, and optional fields.

    Returns:
        User: The created user with assigned ID.

    Raises:
        409: Username or email already exists.
        422: Invalid user data.
    """
    return user
```

### 2. Use response_model for Type Safety

```python
# Good: Explicit response model
@api.get("/items", response_model=list[Item])
async def list_items() -> list[Item]:
    return items

# Less ideal: No response model
@api.get("/items")
async def list_items():
    return items  # Schema will be generic object
```

### 3. Document All Parameters

```python
from typing import Annotated
from django_bolt.param_functions import Header

@api.get("/search")
async def search(
    q: str,                                          # Required query parameter
    page: int = 1,                                   # Optional with default
    limit: int = 10,                                 # Optional with default
    api_key: Annotated[str, Header(alias="x-api-key")] = None  # Header parameter
):
    """Search items with pagination."""
    return []
```

### 4. Organize with Tags

```python
config = OpenAPIConfig(
    title="My API",
    version="1.0.0",
    tags=[
        Tag(name="Users", description="User management"),
        Tag(name="Items", description="Item operations"),
        Tag(name="Admin", description="Admin endpoints")
    ]
)
```

Tags are auto-generated from module names, but explicit tags provide better organization.

### 5. Use Appropriate HTTP Methods

```python
@api.get("/items")          # Read - GET
async def list_items(): ...

@api.post("/items")         # Create - POST
async def create_item(): ...

@api.put("/items/{id}")     # Update (full) - PUT
async def update_item(): ...

@api.patch("/items/{id}")   # Update (partial) - PATCH
async def patch_item(): ...

@api.delete("/items/{id}")  # Delete - DELETE
async def delete_item(): ...
```

### 6. Configure for Production

```python
from django.conf import settings

# Production config
config = OpenAPIConfig(
    title="My API",
    version="1.0.0",
    description="Production API for Example Corp",
    contact=Contact(
        name="API Team",
        email="api@example.com"
    ),
    license=License(
        name="Proprietary",
        url="https://example.com/license"
    ),
    servers=[
        Server(url="https://api.example.com", description="Production")
    ],
    exclude_paths=["/admin", "/static", "/internal", "/debug"],
    render_plugins=[SwaggerRenderPlugin()] if settings.DEBUG else []
)
```

### 7. Version Your API

```python
# In your API
config = OpenAPIConfig(
    title="My API",
    version="2.1.0",  # Semantic versioning
    servers=[
        Server(url="/v2", description="API v2"),
        Server(url="/v1", description="API v1 (deprecated)")
    ]
)
```

### 8. Document Security Requirements

```python
from django_bolt.auth import JWTAuthentication, IsAuthenticated

# Authentication is automatically documented
@api.get("/protected", auth=[jwt_auth], guards=[IsAuthenticated()])
async def protected():
    """Protected endpoint.

    Requires valid JWT token in Authorization header.
    """
    return {"status": "ok"}
```

### 9. Keep Dependencies Updated

```bash
# For YAML support
pip install pyyaml

# Keep Django-Bolt updated
pip install --upgrade django-bolt
```

### 10. Test OpenAPI Schema

```python
from django_bolt.testing import TestClient

def test_openapi_schema():
    """Test that OpenAPI schema is valid."""
    with TestClient(api) as client:
        # Get JSON schema
        response = client.get("/docs/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert schema["openapi"] == "3.1.0"
        assert schema["info"]["title"] == "My API"
        assert "/users" in schema["paths"]
```

---

## Additional Resources

- **OpenAPI Specification:** [https://spec.openapis.org/oas/v3.1.0](https://spec.openapis.org/oas/v3.1.0)
- **Litestar OpenAPI:** [https://github.com/litestar-org/litestar](https://github.com/litestar-org/litestar)
- **msgspec Documentation:** [https://jcristharif.com/msgspec/](https://jcristharif.com/msgspec/)
- **Validation Errors:** [OPENAPI_ERROR_RESPONSES.md](/home/farhan/code/django-bolt/docs/OPENAPI_ERROR_RESPONSES.md)
- **Security Guide:** [SECURITY.md](/home/farhan/code/django-bolt/docs/SECURITY.md)
- **Testing Guide:** [TESTING_UTILITIES.md](/home/farhan/code/django-bolt/docs/TESTING_UTILITIES.md)

---

**Last Updated:** December 2025
**Django-Bolt Version:** 0.2.0

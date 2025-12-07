# Django-Bolt Documentation

Welcome to the Django-Bolt documentation! Django-Bolt is a high-performance API framework for Django that provides **Rust-powered API endpoints** with **60k+ RPS** performance.

## Overview

Django-Bolt combines the elegance of Django with the speed of Rust, providing:

- **Blazing Fast Performance** - Actix Web + Rust handles HTTP, achieving 60k+ requests per second
- **Rust-Powered Auth** - JWT and API Key validation runs without Python GIL overhead
- **Fast Serialization** - msgspec provides 5-10x faster JSON encoding than standard library
- **Seamless Django Integration** - Use your existing Django models, ORM, and project structure
- **Full Async Support** - Built for modern async Python with coroutines
- **Type Safety** - Automatic request/response validation with Python type hints

---

## ✨ Getting Started

**New to Django-Bolt?** Start here:

- **[Getting Started Guide](GETTING_STARTED.md)** - Complete tutorial from installation to your first API
  - Installation and setup
  - Hello World in 60 seconds
  - Basic concepts and route decorators
  - Request parameters and validation
  - Response types
  - Complete example application

**Quick Installation:**

```bash
# Clone and build (not yet on PyPI)
git clone https://github.com/yourusername/django-bolt.git
cd django-bolt
uv sync
make build

# Run tests to verify
make test-py
```

**Key Concepts:**

- **BoltAPI** - The main API object for defining routes
- **Route Decorators** - `@api.get()`, `@api.post()`, etc. for HTTP methods
- **Async Handlers** - All route handlers must be `async def`
- **Auto-Discovery** - Automatically finds `api.py` files in your Django project and apps
- **Type Validation** - Uses msgspec.Struct for automatic request/response validation

---

## 🚀 Core Features

### Routing & Parameters

- **[Annotation Guide](ANNOTATION_GUIDE.md)** - Complete guide to parameter extraction
  - Path parameters: `{user_id}`
  - Query parameters: `?page=1&limit=20`
  - Headers: `Annotated[str, Header("x-api-key")]`
  - Cookies: `Annotated[str, Cookie("session")]`
  - Form data: `Annotated[str, Form("username")]`
  - File uploads: `Annotated[list[dict], File("file")]`
  - Type coercion and validation

### Responses

- **[Response Types](RESPONSES.md)** - All supported response types
  - JSON (default)
  - PlainText
  - HTML
  - Redirect
  - File (in-memory)
  - FileResponse (streaming from disk)
  - StreamingResponse (SSE, long-polling)

### Data Validation & Serialization

All request and response data uses **msgspec** for ultra-fast serialization (5-10x faster than standard JSON):

```python
import msgspec

class User(msgspec.Struct):
    username: str
    email: str
    age: int

@api.post("/users", response_model=User)
async def create_user(user: User) -> User:
    # Automatic validation and serialization
    return user
```

### Dependency Injection

- **[Dependency Injection Guide](DEPENDENCY_INJECTION.md)** - Reusable dependencies
  - Using `Depends()` for shared logic
  - Authentication dependencies
  - Database session dependencies
  - Custom dependency providers
  - Dependency caching and scopes

### Class-Based Views

- **[Class-Based Views Guide](CLASS_BASED_VIEWS.md)** - Organize routes with classes
  - **APIView** - Group related HTTP methods
  - **ViewSet** - Full CRUD with automatic routing
  - **ModelViewSet** - Django ORM integration
  - Custom actions with `@action` decorator
  - DRF-style conventions

### Pagination

- **[Pagination Guide](PAGINATION.md)** - Built-in pagination support
  - **PageNumber** - Traditional page-based pagination
  - **LimitOffset** - Offset-based pagination
  - **Cursor** - Cursor-based pagination for large datasets
  - Custom paginator classes
  - Integration with Django ORM

### OpenAPI Documentation

- **[OpenAPI & Swagger](OPENAPI.md)** - Auto-generated API documentation
  - Automatic schema generation
  - Swagger UI integration
  - Custom OpenAPI metadata
  - Request/response schemas
  - **[Error Response Documentation](OPENAPI_ERROR_RESPONSES.md)** - Documenting error responses

---

## 🔒 Security

### Authentication

Django-Bolt includes high-performance authentication that runs in Rust without Python GIL overhead:

```python
from django_bolt.auth import JWTAuthentication, IsAuthenticated

@api.get("/protected", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def protected_route(request):
    auth = request.get("auth", {})
    return {"user_id": auth.get("user_id")}
```

- **[Security Guide](SECURITY.md)** - Comprehensive security documentation
  - **JWT Authentication** - Stateless token-based auth
  - **API Key Authentication** - Service-to-service auth
  - **Token Revocation** - In-memory, cache, and ORM-based revocation
  - Security best practices and audit checklist

### Authorization & Guards

Built-in permission guards that run in Rust:

```python
from django_bolt.auth import IsAdminUser, HasPermission

@api.post("/articles", guards=[HasPermission("blog.add_article")])
async def create_article(request): ...
```

Guards available:

- `IsAuthenticated()` - Requires valid authentication
- `IsAdminUser()` - Requires superuser status
- `IsStaff()` - Requires staff status
- `HasPermission("app.perm")` - Specific Django permission
- `HasAnyPermission([...])` - Any of the permissions (OR)
- `HasAllPermissions([...])` - All permissions (AND)

See the **[Security Guide](SECURITY.md)** for details on custom guards.

### CORS

Cross-Origin Resource Sharing with secure defaults:

```python
from django_bolt.middleware import cors

# Per-route CORS
@api.get("/public")
@cors(origins=["https://example.com"], credentials=True)
async def public_endpoint(): ...

# Or configure globally in settings.py
BOLT_CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://app.example.com",
]
```

See the **[Security Guide](SECURITY.md)** for CORS security features and the **[Middleware Guide](MIDDLEWARE.md)** for advanced configuration.

### Rate Limiting

Token bucket rate limiting that runs in Rust:

```python
from django_bolt.middleware import rate_limit

@api.get("/search")
@rate_limit(rps=10, burst=20)  # 10 requests/sec, burst of 20
async def search(query: str): ...
```

See the **[Middleware Guide](MIDDLEWARE.md)** for rate limiting strategies.

### File Serving Security

Secure file serving with path traversal protection:

```python
from django_bolt.responses import FileResponse

# settings.py - Whitelist allowed directories
BOLT_ALLOWED_FILE_PATHS = [
    "/var/app/uploads",
    "/var/app/public",
]

@api.get("/download/{filename}")
async def download(filename: str):
    # Automatic path validation and security checks
    return FileResponse(f"/var/app/uploads/{filename}")
```

See the **[Security Guide](SECURITY.md)** for file serving security features.

---

## WebSocket

Django-Bolt provides full WebSocket support with a FastAPI-like interface:

```python
from django_bolt import BoltAPI, WebSocket

api = BoltAPI()

@api.websocket("/ws/chat/{room_id}")
async def chat(websocket: WebSocket, room_id: str):
    await websocket.accept()
    async for message in websocket.iter_text():
        await websocket.send_text(f"[{room_id}] {message}")
```

- **[WebSocket Guide](WEBSOCKET.md)** - Complete WebSocket documentation
  - WebSocket decorator and handler patterns
  - Sending/receiving text, binary, and JSON messages
  - Path parameters with type coercion
  - Authentication and guards
  - Origin validation and rate limiting
  - Testing with `WebSocketTestClient`
  - Close codes and exception handling

---

## ⚡ Middleware

- **[Middleware Guide](MIDDLEWARE.md)** - Complete middleware documentation

  - Middleware system overview
  - Global vs. per-route middleware
  - Built-in middleware (CORS, rate limiting)
  - Custom middleware creation
  - Middleware execution order
  - Skipping middleware with `@skip_middleware`

- **[Compression](COMPRESSION.md)** - Response compression
  - Automatic gzip, brotli, and zstd compression
  - Configuration and tuning
  - Disabling compression for specific routes
  - Performance considerations

---

## 🛠️ Operations

### Logging

- **[Logging Guide](LOGGING.md)** - Request/response logging
  - Structured logging
  - Request timing and metrics
  - Error logging
  - Custom log formatters
  - Integration with Django logging

### Exception Handling

- **[Exception Handling](EXCEPTIONS.md)** - Error handling patterns
  - Built-in HTTP exceptions
  - Custom exception classes
  - Global exception handlers
  - Error response formatting
  - Error logging and monitoring

### Testing

- **[Testing Utilities](TESTING_UTILITIES.md)** - Testing your APIs
  - Test client utilities
  - Mocking authentication
  - Testing file uploads
  - Integration testing patterns
  - Performance testing

---

## 📚 Advanced Topics

### Working with Django

- **[Async Django](ASYNC_DJANGO.md)** - Using Django ORM with async

  - Async ORM methods (`aget`, `acreate`, `afilter`)
  - `sync_to_async` for sync code
  - Transaction handling
  - Connection pooling
  - Performance tips

- **[Django Admin Integration](DJANGO_ADMIN.md)** - Using Django-Bolt with Django Admin
  - Running both systems together
  - Shared authentication
  - Admin panel for API data
  - Management commands

### Performance Optimization

- **[GIL Optimization](GIL_OPTIMIZATION.md)** - Understanding Django-Bolt's performance
  - How Rust avoids the Python GIL
  - Authentication in Rust vs. Python
  - Middleware execution model
  - Zero-copy routing
  - Multi-process scaling with SO_REUSEPORT
  - Benchmarking and profiling
  - Performance best practices

---

## 📖 Reference Documentation

### All Documentation Files

| Document                                                  | Description                                       |
| --------------------------------------------------------- | ------------------------------------------------- |
| **[Getting Started](GETTING_STARTED.md)**                 | Complete tutorial from installation to first API  |
| **[Annotation Guide](ANNOTATION_GUIDE.md)**               | Parameter extraction (path, query, headers, etc.) |
| **[Responses](RESPONSES.md)**                             | All response types and usage                      |
| **[Dependency Injection](DEPENDENCY_INJECTION.md)**       | Reusable dependencies with `Depends()`            |
| **[Class-Based Views](CLASS_BASED_VIEWS.md)**             | APIView and ViewSet patterns                      |
| **[Pagination](PAGINATION.md)**                           | PageNumber, LimitOffset, and Cursor pagination    |
| **[OpenAPI](OPENAPI.md)**                                 | Auto-generated API documentation                  |
| **[OpenAPI Error Responses](OPENAPI_ERROR_RESPONSES.md)** | Documenting error responses                       |
| **[Security Guide](SECURITY.md)**                         | Authentication, authorization, and security       |
| **[Middleware](MIDDLEWARE.md)**                           | Middleware system and built-in middleware         |
| **[Compression](COMPRESSION.md)**                         | Response compression (gzip, brotli, zstd)         |
| **[Logging](LOGGING.md)**                                 | Request/response logging and metrics              |
| **[Exception Handling](EXCEPTIONS.md)**                   | Error handling patterns                           |
| **[Testing Utilities](TESTING_UTILITIES.md)**             | Testing tools and patterns                        |
| **[WebSocket](WEBSOCKET.md)**                             | WebSocket support and testing                     |
| **[Async Django](ASYNC_DJANGO.md)**                       | Using Django ORM with async                       |
| **[Django Admin](DJANGO_ADMIN.md)**                       | Django Admin integration                          |
| **[GIL Optimization](GIL_OPTIMIZATION.md)**               | Performance architecture and optimization         |
| **[Publishing Guide](PUBLISHING.md)**                     | Guide for publishing to PyPI                      |

---

## 🎯 Examples

Complete example applications are available in the repository:

- **[Example Project](../python/example/)** - Full Django project with:
  - Authentication (JWT and API Key)
  - CRUD operations with Django ORM
  - File uploads and downloads
  - Pagination examples
  - Middleware usage
  - Class-based views

---

## 🤝 Contributing

We welcome contributions! Please see:

- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute (if it exists)
- **[Publishing Guide](PUBLISHING.md)** - Guide for maintainers publishing releases
- **GitHub Issues** - Report bugs or request features
- **GitHub Discussions** - Ask questions and share projects

---

## 📝 Quick Reference

### Route Decorators

```python
@api.get("/path")           # GET request
@api.post("/path")          # POST request
@api.put("/path")           # PUT request
@api.patch("/path")         # PATCH request
@api.delete("/path")        # DELETE request
@api.head("/path")          # HEAD request (no body)
@api.options("/path")       # OPTIONS request (no body)
```

### Authentication & Guards

```python
from django_bolt.auth import JWTAuthentication, IsAuthenticated

@api.get(
    "/protected",
    auth=[JWTAuthentication()],
    guards=[IsAuthenticated()]
)
```

### Middleware Decorators

```python
from django_bolt.middleware import cors, rate_limit, skip_middleware

@api.get("/public")
@cors(origins=["*"])
@rate_limit(rps=10, burst=20)
async def handler(): ...

@api.get("/no-middleware")
@skip_middleware("cors", "rate_limit")
async def handler(): ...
```

### Response Types

```python
from django_bolt.responses import PlainText, HTML, Redirect, File, FileResponse, StreamingResponse

return {"data": "value"}              # JSON (default)
return PlainText("Hello")             # Plain text
return HTML("<h1>Hello</h1>")         # HTML
return Redirect("/new-path")          # Redirect
return File(content, filename="f.txt") # File download
return FileResponse("/path/to/file")   # Streaming file
return StreamingResponse(generator())  # Streaming response
```

### Parameter Extraction

```python
from typing import Annotated
from django_bolt.param_functions import Header, Cookie, Form, File

async def handler(
    # Path parameter
    user_id: int,

    # Query parameter
    page: int = 1,

    # Header
    api_key: Annotated[str, Header("x-api-key")],

    # Cookie
    session: Annotated[str, Cookie("sessionid")],

    # Form data
    username: Annotated[str, Form()],

    # File upload
    files: Annotated[list[dict], File("file")],
): ...
```

---

## 🔗 External Resources

- **Django Documentation** - [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
- **msgspec Documentation** - [https://jcristharif.com/msgspec/](https://jcristharif.com/msgspec/)
- **Actix Web** - [https://actix.rs/](https://actix.rs/)
- **PyO3** - [https://pyo3.rs/](https://pyo3.rs/)

---

## 📄 License

Django-Bolt is open source and available under the MIT License.

---

**Built with ⚡ by developers who need speed without sacrificing Python's elegance.**

For questions, issues, or feature requests, please visit our [GitHub repository](https://github.com/yourusername/django-bolt).

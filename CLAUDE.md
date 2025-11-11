# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django-Bolt is a high-performance API framework for Django that provides Rust-powered API endpoints with 60k+ RPS performance. It integrates with existing Django projects, using Actix Web for HTTP handling, PyO3 to bridge Python handlers with Rust's async runtime, msgspec for fast serialization, and supports multi-process scaling with SO_REUSEPORT.

## Key Commands

### Build & Development

```bash
# Build Rust extension (required after any Rust code changes)
make build  # or: uv run maturin develop --release

# Full rebuild (clean + build)
make rebuild

# Clean build artifacts
make clean
```

### Running the Server

```bash
# From Django project directory (e.g., python/example)
python manage.py runbolt --host 0.0.0.0 --port 8000 --processes 2 --workers 2

# Development mode with auto-reload (single process, watches for file changes)
python manage.py runbolt --dev

# Background multi-process (for testing)
make run-bg HOST=127.0.0.1 PORT=8000 P=2 WORKERS=2

# Kill any running servers
make kill
```

### Testing

```bash
# Python unit tests
make test-py  # or: uv run --with pytest pytest python/tests -s -vv

# Run specific test file
uv run --with pytest pytest python/tests/test_syntax.py -s -vv

# Run specific test function
uv run --with pytest pytest python/tests/test_syntax.py::test_streaming_async_mixed_types -s -vv

# Quick endpoint smoke tests
make smoke      # Test basic endpoints
make orm-smoke  # Test ORM endpoints (requires seeded data)
```

### Benchmarking

```bash
# Full benchmark suite (saves results)
make save-bench  # Creates/rotates BENCHMARK_BASELINE.md and BENCHMARK_DEV.md

# Custom benchmark
make bench C=100 N=50000  # 100 concurrent, 50k requests

# High-performance test
make perf-test  # 4 processes × 1 worker, 50k requests

# ORM-specific benchmark
make orm-test   # Sets up DB, seeds data, benchmarks ORM endpoints
```

### Database (Standard Django)

```bash
# From Django project directory
python manage.py migrate
python manage.py makemigrations [app_name]
```

### Release

```bash
# Create a new release (bumps version, commits, tags, and pushes)
make release VERSION=0.2.2              # Standard release
make release VERSION=0.3.0-alpha1       # Pre-release
make release VERSION=0.2.2 DRY_RUN=1    # Test without changes

# Or use the script directly
./scripts/release.sh 0.2.2              # Standard release
./scripts/release.sh 0.2.2 --dry-run    # Test without changes
```

### CLI Tool

```bash
# Initialize Django-Bolt in a new Django project
python -m django_bolt init

# This creates:
# - api.py in project root
# - Adds django_bolt to INSTALLED_APPS
# - Configures basic settings
```

## Architecture Overview

### Core Components

1. **Rust Layer (`src/`)**

   - `lib.rs` - PyO3 module entry point, registers Python-callable functions
   - `server.rs` - Actix Web server with tokio runtime, handles multi-worker/multi-process setup (includes CORS and compression via Actix middleware)
   - `router.rs` - matchit-based routing (zero-copy path matching)
   - `handler.rs` - Python callback dispatcher via PyO3
   - `middleware/` - Custom middleware pipeline running in Rust (no Python GIL overhead)
     - `auth.rs` - JWT/API Key/Session authentication in Rust
     - `rate_limit.rs` - Token bucket rate limiting
   - `permissions.rs` - Guard/permission evaluation in Rust
   - `streaming.rs` - Streaming response handling (SSE, async generators)
   - `state.rs` - Shared server state (auth config, middleware config)
   - `metadata.rs` - Route metadata structures
   - `error.rs` - Error handling and HTTP exceptions
   - `request.rs` - Request handling utilities

2. **Python Framework (`python/django_bolt/`)**

   - `api.py` - BoltAPI class with decorator-based routing (`@api.get/post/put/patch/delete/head/options`)
   - `binding.py` - Parameter extraction and type coercion
   - `responses.py` - Response types (PlainText, HTML, Redirect, File, FileResponse, StreamingResponse)
   - `exceptions.py` - HTTPException and error handling
   - `params.py` - Parameter markers (Header, Cookie, Form, File, Depends)
   - `dependencies.py` - Dependency injection system
   - `serialization.py` - msgspec-based serialization
   - `bootstrap.py` - Django configuration helper
   - `cli.py` - CLI tool for project initialization
   - `health.py` - Health check endpoints
   - `openapi.py` - OpenAPI schema generation
   - `pagination.py` - Pagination helpers (PageNumber, LimitOffset, Cursor)
   - `viewsets.py` - Class-based ViewSet and ModelViewSet
   - `auth/` - Authentication system
     - `guards.py` - Permission guards (IsAuthenticated, IsAdminUser, HasPermission, etc.)
     - `jwt_utils.py` - JWT utilities (create_jwt_for_user)
     - `token.py` - Token handling and validation
     - `revocation.py` - Token revocation stores (InMemoryRevocation, DjangoCacheRevocation, DjangoORMRevocation)
     - `middleware.py` - Middleware decorators (@cors, @rate_limit, @skip_middleware)
   - `middleware/compiler.py` - Compiles Python middleware config to Rust metadata
   - `management/commands/runbolt.py` - Django management command with autodiscovery

3. **Django Integration**
   - `runbolt` management command auto-discovers `api.py` files in:
     - Django project root (same directory as settings.py)
     - All installed Django apps (looks for `app_name/api.py`)
   - Merges all discovered BoltAPI instances into a single router
   - Supports standard Django ORM (async methods: `aget`, `afilter`, etc.)

### Request Flow

```
HTTP Request → Actix Web (Rust)
           ↓
    Route Matching (matchit - zero-copy)
           ↓
    Middleware Pipeline (Rust - no GIL)
      - CORS preflight/handling
      - Rate limiting (token bucket)
      - Compression (gzip/brotli/zstd)
           ↓
    Authentication (Rust - no GIL for JWT/API key/session validation)
      - JWT signature verification
      - Token expiration check
      - API key validation
      - Session validation (Django integration)
           ↓
    Guards/Permissions (Rust - no GIL)
      - IsAuthenticated, IsAdminUser, IsStaff
      - HasPermission, HasAnyPermission, HasAllPermissions
           ↓
    Python Handler (PyO3 bridge - acquires GIL)
           ↓
    Parameter Extraction & Validation
      - Path params: {user_id} → function arg
      - Query params: ?page=1 → optional function arg
      - Headers: Annotated[str, Header("x-api-key")]
      - Cookies: Annotated[str, Cookie("session")]
      - Form: Annotated[str, Form("username")]
      - Files: Annotated[bytes, File("upload")]
      - Body: msgspec.Struct → validation
      - Dependencies: Depends(get_current_user)
           ↓
    Handler Execution (async Python coroutine)
      - Django ORM access (async methods)
      - Business logic
           ↓
    Response Serialization
      - msgspec for JSON (5-10x faster than stdlib)
      - Response model validation if specified
           ↓
    Response Compression (if enabled)
      - Client-negotiated (Accept-Encoding)
      - gzip/brotli/zstd support
           ↓
    HTTP Response (back to Actix Web)
```

### Performance Characteristics

- **Authentication/Guards run in Rust**: JWT validation, API key checks, and permission guards execute without Python GIL overhead
- **Zero-copy routing**: matchit router matches paths without allocations
- **Batched middleware**: Middleware (CORS, rate limiting, compression) runs in a pipeline before Python handler is invoked
- **Multi-process scaling**: SO_REUSEPORT allows kernel-level load balancing across processes
- **msgspec serialization**: 5-10x faster than standard JSON for request/response handling
- **Efficient compression**: Client-negotiated gzip/brotli/zstd compression in Rust

## API Development Patterns

### Route Definition

Routes are defined in `api.py` files using decorators:

```python
from django_bolt import BoltAPI
import msgspec

api = BoltAPI()

# Path parameters
@api.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"item_id": item_id}

# Request body with validation
class Item(msgspec.Struct):
    name: str
    price: float

@api.post("/items", response_model=Item)
async def create_item(item: Item) -> Item:
    # item is already validated
    return item

# HEAD and OPTIONS methods
@api.head("/items/{item_id}")
async def head_item(item_id: int):
    # Returns headers only (same as GET but no body)
    return {"item_id": item_id}

@api.options("/items")
async def options_items():
    # Custom OPTIONS handler
    return {"methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]}
```

**Note**: HEAD and OPTIONS methods cannot have body parameters (like GET/DELETE). They're designed for metadata and preflight requests.

### Authentication & Guards

```python
from django_bolt.auth import (
    JWTAuthentication,
    APIKeyAuthentication,    IsAuthenticated,
    HasPermission
)

# JWT Authentication
@api.get("/protected", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def protected_route(request):
    auth = request.get("auth", {})
    user_id = auth.get("user_id")
    return {"user_id": user_id}

# Multiple auth backends (tries in order)
@api.get("/flexible", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def flexible_auth(request):
    auth = request.get("auth", {})
    backend = auth.get("auth_backend")  # "jwt", "api_key", or "session"
    return {"backend": backend}
```

**See [docs/SECURITY.md](docs/SECURITY.md) for complete authentication documentation.**

### Middleware

- **Global middleware**: Applied via `BoltAPI(middleware_config={...})`
- **Per-route middleware**: Applied via decorators (`@cors`, `@rate_limit`)
- **Skip middleware**: Use `@skip_middleware("cors", "rate_limit", "compression")` to selectively disable
- **Compression**: Automatic gzip/brotli/zstd compression based on Accept-Encoding header

**See [docs/MIDDLEWARE.md](docs/MIDDLEWARE.md) for complete middleware documentation.**

### Response Types

- **JSON** (default): Return dict/list, serialized with msgspec
- **PlainText**: `return PlainText("Hello")`
- **HTML**: `return HTML("<h1>Hello</h1>")`
- **Redirect**: `return Redirect("/new-location")`
- **File**: `return File(content, filename="download.pdf")`
- **FileResponse**: `return FileResponse(path, filename="doc.pdf")` (streaming from Rust)
- **StreamingResponse**: `return StreamingResponse(async_generator(), media_type="text/event-stream")`

**See [docs/RESPONSES.md](docs/RESPONSES.md) for complete response documentation.**

### Class-Based Views

Django-Bolt supports DRF-style ViewSets:

```python
from django_bolt.viewsets import ViewSet, ModelViewSet
from django.contrib.auth.models import User
import msgspec

# Basic ViewSet
@api.viewset("/users")
class UserViewSet(ViewSet):
    async def list(self, request):
        users = await User.objects.all()
        return [{"id": u.id, "username": u.username} async for u in users]

    async def retrieve(self, request, pk: int):
        user = await User.objects.aget(id=pk)
        return {"id": user.id, "username": user.username}

# ModelViewSet (includes CRUD operations)
@api.viewset("/articles")
class ArticleViewSet(ModelViewSet):
    model = Article
    queryset = Article.objects.all()
    serializer_class = ArticleSchema

    # Custom actions
    @action(methods=["GET"], detail=False)
    async def published(self, request):
        articles = await Article.objects.filter(published=True).all()
        return [{"id": a.id, "title": a.title} async for a in articles]

```

**See [docs/CLASS_BASED_VIEWS.md](docs/CLASS_BASED_VIEWS.md) for complete documentation.**

### Pagination

Django-Bolt provides built-in pagination helpers:

```python
from django_bolt.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination

# Page number pagination
@api.get("/users")
async def list_users(page: int = 1, page_size: int = 10):
    paginator = PageNumberPagination(page=page, page_size=page_size)
    users = await User.objects.all()
    return await paginator.paginate(users)

# Limit/offset pagination
@api.get("/articles")
async def list_articles(limit: int = 10, offset: int = 0):
    paginator = LimitOffsetPagination(limit=limit, offset=offset)
    articles = await Article.objects.all()
    return await paginator.paginate(articles)

# Cursor-based pagination (for large datasets)
@api.get("/posts")
async def list_posts(cursor: str = None, page_size: int = 20):
    paginator = CursorPagination(cursor=cursor, page_size=page_size)
    posts = await Post.objects.order_by("-created_at").all()
    return await paginator.paginate(posts)
```

**See [docs/PAGINATION.md](docs/PAGINATION.md) for complete documentation.**

### Health Check Endpoints

Django-Bolt provides built-in health check endpoints:

```python
from django_bolt import BoltAPI

api = BoltAPI()

# Built-in health endpoints (automatically available)
# GET /health - Basic health check (returns {"status": "ok"})
# GET /ready - Readiness check (returns {"status": "ready"})

# Custom health checks
from django_bolt.health import register_health_check

@register_health_check
async def check_database():
    # Custom health check logic
    return {"database": "connected"}
```

### OpenAPI Documentation

Django-Bolt automatically generates OpenAPI documentation:

```python
from django_bolt import BoltAPI

# OpenAPI documentation is automatically available at:
# - /docs - Swagger UI
# - /redoc - ReDoc
# - /scalar - Scalar API Reference
# - /rapidoc - RapiDoc
# - /stoplight - Stoplight Elements
# - /openapi.json - OpenAPI JSON schema
# - /openapi.yaml - OpenAPI YAML schema

api = BoltAPI(
    title="My API",
    version="1.0.0",
    description="API description",
    openapi_url="/openapi.json"  # Customize OpenAPI endpoint
)

# Document routes with tags and descriptions
@api.get("/users/{user_id}", tags=["users"], summary="Get a user")
async def get_user(user_id: int):
    """
    Retrieve a user by ID.

    - **user_id**: The user's unique identifier
    """
    return {"user_id": user_id}
```

**See [docs/OPENAPI.md](docs/OPENAPI.md) for complete documentation.**

## Testing Strategy

### Unit Tests

Located in `python/tests/`:

**Core Functionality**:

- `test_syntax.py` - Route syntax, parameter extraction, response types
- `test_decorator_syntax.py` - Decorator-based route definitions
- `test_parameter_validation.py` - Parameter validation logic
- `test_json_validation.py` - JSON request/response validation
- `test_integration_validation.py` - End-to-end validation tests
- `test_file_response.py` - File download and streaming

**Authentication & Authorization**:

- `test_jwt_auth.py` - JWT authentication logic
- `test_jwt_token.py` - Token generation and validation
- `test_guards_auth.py` - Guard/permission logic
- `test_guards_integration.py` - Integration tests for guards
- `test_auth_secret_key.py` - Secret key handling

**Middleware & CORS**:

- `test_middleware.py` - Middleware system tests
- `test_global_cors.py` - Global CORS configuration
- `test_middleware_server.py` - Middleware integration tests

**Advanced Features**:

- `test_error_handling.py` - Error handling and exceptions
- `test_logging.py` - Request/response logging
- `test_logging_merge.py` - Logging configuration merging
- `test_health.py` - Health check endpoints
- `test_openapi_docs.py` - OpenAPI documentation generation
- `test_pagination.py` - Pagination helpers (PageNumber, LimitOffset, Cursor)
- `test_testing_utilities.py` - Testing utilities and test client

**Class-Based Views**:

- `cbv/test_viewset_unified.py` - ViewSet pattern tests
- `cbv/test_model_viewset.py` - ModelViewSet pattern tests
- `cbv/test_action_decorator.py` - Custom action decorators

**Django Integration**:

- `admin_tests/` - Django admin integration tests
- `test_models.py` - Django model integration

### Test Servers

Test infrastructure uses separate server files:

- `syntax_test_server.py` - Routes for testing basic functionality
- `middleware_test_server.py` - Routes for testing middleware
- Server instances are started in subprocess for integration tests

### Running Tests

Always run tests with `-s -vv` for detailed output:

```bash
uv run --with pytest pytest python/tests -s -vv
```

## Common Development Tasks

### After Modifying Rust Code

1. Run `make build` or `uv run maturin develop --release`
2. Run tests: `make test-py`
3. Optionally run benchmarks: `make save-bench`

### After Modifying Python Code

1. Run tests: `make test-py`
2. No rebuild needed (Python is interpreted)

### Adding a New Route

1. Create/modify `api.py` in project root or Django app
2. Define route with `@api.get/post/put/patch/delete`
3. Ensure handler is async
4. Test with `make smoke` or specific test

### Adding Authentication

1. Configure auth backend: `JWTAuthentication(secret_key="...", algorithm="HS256")`
2. Add to route: `@api.get("/path", auth=[JWTAuthentication()], guards=[IsAuthenticated()])`
3. Auth context available in handler via `request.get("auth", {})`

### Debugging Performance Issues

1. Run `make save-bench` to establish baseline
2. Make changes
3. Run `make save-bench` again (rotates baseline, creates new dev benchmark)
4. Compare BENCHMARK_BASELINE.md vs BENCHMARK_DEV.md
5. Key metrics: Requests per second, Failed requests

## Important Implementation Notes

- **Handlers must be async**: All route handlers must be defined as `async def`
- **Django ORM**: Use async methods (`aget`, `acreate`, `afilter`, etc.) or wrap sync methods with `sync_to_async`
- **Middleware compilation**: Python middleware config is compiled to Rust metadata at server startup
- **Route autodiscovery**: Runs once at server startup, no hot-reload in production mode (use `--dev` for development)
- **Multi-process**: Each process has its own Python interpreter and imports Django independently
- never silently ignore the error or exception. At least we have print method about this happened. This create obscure errors .
- only add tests that test actual functionality and that test must fail when that code is changed or removed
- always try to use from **future** import annotations instead of string annotations
- imports should always be on top
- always import on the top
- do not pass the test by removing asserts or remove the failing tests if the behabior expected is correct. Tell me it is failing and why it is failing and if i allow only than remove the test
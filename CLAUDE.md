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
# From Django project directory (e.g., python/examples/testproject/)
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
make test-py  # or: uv run --with pytest pytest python/django_bolt/tests -s -vv

# Run specific test file
uv run --with pytest pytest python/django_bolt/tests/test_syntax.py -s -vv

# Run specific test function
uv run --with pytest pytest python/django_bolt/tests/test_syntax.py::test_streaming_async_mixed_types -s -vv

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

## Architecture Overview

### Core Components

1. **Rust Layer (`src/`)**
   - `lib.rs` - PyO3 module entry point, registers Python-callable functions
   - `server.rs` - Actix Web server with tokio runtime, handles multi-worker/multi-process setup
   - `router.rs` - matchit-based routing (zero-copy path matching)
   - `handler.rs` - Python callback dispatcher via PyO3
   - `middleware/` - Middleware pipeline running in Rust (no Python GIL overhead)
     - `auth.rs` - JWT/API Key authentication in Rust
     - `cors.rs` - CORS handling with preflight support
     - `rate_limit.rs` - Token bucket rate limiting
   - `permissions.rs` - Guard/permission evaluation in Rust
   - `streaming.rs` - Streaming response handling
   - `state.rs` - Shared server state (auth config, middleware config)
   - `metadata.rs` - Route metadata structures

2. **Python Framework (`python/django_bolt/`)**
   - `api.py` - BoltAPI class with decorator-based routing (`@api.get/post/put/patch/delete`)
   - `binding.py` - Parameter extraction and type coercion
   - `responses.py` - Response types (PlainText, HTML, Redirect, File, FileResponse, StreamingResponse)
   - `exceptions.py` - HTTPException and error handling
   - `params.py` - Parameter markers (Header, Cookie, Form, File, Depends)
   - `dependencies.py` - Dependency injection system
   - `serialization.py` - msgspec-based serialization
   - `bootstrap.py` - Django configuration helper
   - `auth/` - Authentication system
     - `backends.py` - JWTAuthentication, APIKeyAuthentication classes
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
           ↓
    Authentication (Rust - no GIL for JWT/API key validation)
      - JWT signature verification
      - Token expiration check
      - API key validation
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
    HTTP Response (back to Actix Web)
```

### Performance Characteristics

- **Authentication/Guards run in Rust**: JWT validation, API key checks, and permission guards execute without Python GIL overhead
- **Zero-copy routing**: matchit router matches paths without allocations
- **Batched middleware**: Middleware runs in a pipeline before Python handler is invoked
- **Multi-process scaling**: SO_REUSEPORT allows kernel-level load balancing across processes
- **msgspec serialization**: 5-10x faster than standard JSON for request/response handling

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
```

### Authentication & Guards

```python
from django_bolt.auth import JWTAuthentication, IsAuthenticated, HasPermission

@api.get("/protected", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def protected_route(request):
    auth = request.get("auth", {})
    user_id = auth.get("user_id")
    return {"user_id": user_id}
```

### Middleware

- **Global middleware**: Applied via `BoltAPI(middleware_config={...})`
- **Per-route middleware**: Applied via decorators (`@cors`, `@rate_limit`)
- **Skip middleware**: Use `@skip_middleware("cors", "rate_limit")` to selectively disable

### Response Types

- **JSON** (default): Return dict/list, serialized with msgspec
- **PlainText**: `return PlainText("Hello")`
- **HTML**: `return HTML("<h1>Hello</h1>")`
- **Redirect**: `return Redirect("/new-location")`
- **File**: `return File(content, filename="download.pdf")`
- **FileResponse**: `return FileResponse(path, filename="doc.pdf")` (streaming from Rust)
- **StreamingResponse**: `return StreamingResponse(async_generator(), media_type="text/event-stream")`

## Testing Strategy

### Unit Tests

Located in `python/django_bolt/tests/`:
- `test_syntax.py` - Route syntax, parameter extraction, response types
- `test_jwt_auth.py` - JWT authentication logic
- `test_jwt_token.py` - Token generation and validation
- `test_guards_auth.py` - Guard/permission logic
- `test_guards_integration.py` - Integration tests for guards
- `test_middleware.py` - Middleware system tests
- `test_auth_secret_key.py` - Secret key handling

### Test Servers

Test infrastructure uses separate server files:
- `syntax_test_server.py` - Routes for testing basic functionality
- `middleware_test_server.py` - Routes for testing middleware
- Server instances are started in subprocess for integration tests

### Running Tests

Always run tests with `-s -vv` for detailed output:
```bash
uv run --with pytest pytest python/django_bolt/tests -s -vv
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

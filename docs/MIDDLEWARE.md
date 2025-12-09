# Django-Bolt Middleware System

## Overview

Django-Bolt provides a high-performance middleware system with two layers:

1. **Rust-accelerated middleware** (CORS, rate limiting, authentication) - runs without Python GIL overhead
2. **Python middleware** (Django-compatible) - for custom logic and Django middleware integration

**Key Design Principles:**
- **Work once at registration time** - middleware instances, patterns, and headers are pre-compiled at startup
- **Zero per-request allocations** - CORS headers, rate limit responses use pre-computed strings
- **Django compatibility** - use existing Django middleware with the same `__init__(get_response)` pattern

## Quick Start

```python
# settings.py - Configure CORS globally (recommended)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
CORS_ALLOW_CREDENTIALS = True
```

```python
# api.py
from django_bolt import BoltAPI
from django_bolt.middleware import rate_limit, cors, TimingMiddleware
from django_bolt.auth import JWTAuthentication, IsAuthenticated

# Use Django middleware from settings.MIDDLEWARE
api = BoltAPI(django_middleware=True)

# Or with custom Python middleware (pass classes, not instances)
api = BoltAPI(middleware=[TimingMiddleware])

# Per-route rate limiting (Rust-accelerated)
@api.get("/api/data")
@rate_limit(rps=100, burst=200)
async def get_data():
    return {"status": "ok"}

# Route-level CORS override
@api.get("/special")
@cors(origins=["https://special.com"], credentials=False)
async def special_endpoint():
    return {"data": "custom CORS"}

# Authentication via route parameters (NOT decorators)
@api.get("/protected", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def protected_endpoint(request):
    return {"user_id": request.auth.get("user_id")}
```

## Rust-Accelerated Middleware

These middleware types run entirely in Rust without Python GIL overhead:

### Rate Limiting

Token bucket algorithm with burst capacity:

```python
from django_bolt.middleware import rate_limit

@api.get("/api/endpoint")
@rate_limit(rps=100, burst=200, key="ip")
async def limited_endpoint():
    return {"data": "rate limited"}
```

**Parameters:**
| Parameter | Description | Default |
|-----------|-------------|---------|
| `rps` | Requests per second (sustained rate) | Required |
| `burst` | Burst capacity for traffic spikes | `2 * rps` |
| `key` | Rate limit key strategy | `"ip"` |

**Key Strategies:**
- `"ip"` - Client IP (checks X-Forwarded-For, X-Real-IP, then Remote-Addr)
- `"user"` - User ID from authentication context
- `"api_key"` - API key from authentication
- Custom header name (e.g., `"x-tenant-id"`)

**Implementation:**
- DashMap concurrent storage (lock-free reads)
- Per-handler + key isolation
- Returns 429 with `Retry-After` header when exceeded
- Security limits: 100k max limiters, 256 byte max key length

### CORS

Pre-compiled headers for zero-allocation responses:

#### Global Configuration (Recommended)

```python
# settings.py - Compatible with django-cors-headers
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://example.com",
]

# Or use regex patterns for dynamic subdomains
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://\w+\.example\.com$",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = ["accept", "authorization", "content-type"]
CORS_EXPOSE_HEADERS = []
CORS_PREFLIGHT_MAX_AGE = 3600
```

**Important:** Origins must include the scheme (`http://` or `https://`).

#### Route-Level Override

```python
from django_bolt.middleware import cors

@api.get("/special")
@cors(
    origins=["https://special.com"],
    methods=["GET", "POST"],
    headers=["Content-Type", "Authorization"],
    credentials=False,
    max_age=7200
)
async def special_endpoint():
    return {"data": "with custom CORS"}
```

**How It Works:**
- Origins and regexes compiled at startup
- Header strings pre-joined (`"GET, POST, PUT"`)
- O(1) hash set lookup for exact origins
- Automatic OPTIONS preflight handling

### Authentication

Authentication is configured via route parameters, not decorators:

```python
from django_bolt.auth import JWTAuthentication, APIKeyAuthentication
from django_bolt.auth import IsAuthenticated, IsAdminUser, HasPermission

# JWT Authentication
@api.get("/protected", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def protected_route(request):
    return {"user_id": request.auth.get("user_id")}

# API Key Authentication
@api.get("/api-data", auth=[APIKeyAuthentication(api_keys={"key1", "key2"})], guards=[IsAuthenticated()])
async def api_data(request):
    return {"authenticated": True}

# Multiple backends (tries in order)
@api.get("/flexible", auth=[JWTAuthentication(), APIKeyAuthentication()], guards=[IsAuthenticated()])
async def flexible_auth(request):
    return {"backend": request.auth.get("auth_backend")}
```

**Auth Context (available in `request.auth`):**
- `user_id` - User identifier
- `is_staff` - Staff status
- `is_admin` - Admin/superuser status
- `auth_backend` - Which backend authenticated (`"jwt"` or `"api_key"`)
- `permissions` - List of permissions
- `auth_claims` - Full JWT claims (JWT only)

## Python Middleware

For custom logic and Django middleware integration. Uses Django's standard pattern.

### Django-Style Pattern

All Python middleware follows Django's pattern:

```python
class MyMiddleware:
    def __init__(self, get_response):
        """Called ONCE at registration time."""
        self.get_response = get_response
        # Do expensive setup here (compiled patterns, connections, etc.)

    async def __call__(self, request):
        """Called for each request."""
        # Before request processing
        request.state["custom_value"] = "hello"

        response = await self.get_response(request)

        # After request processing
        response.headers["X-Custom-Header"] = "value"
        return response
```

**Key Point:** `__init__` is called once at startup, not per-request.

### Using Django Middleware

```python
from django_bolt import BoltAPI

# Load all middleware from settings.MIDDLEWARE
api = BoltAPI(django_middleware=True)

# Or select specific middleware
api = BoltAPI(django_middleware=[
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
])

# Or use include/exclude config
api = BoltAPI(django_middleware={
    "include": ["django.contrib.sessions.middleware.SessionMiddleware"],
    "exclude": ["django.middleware.csrf.CsrfViewMiddleware"],
})
```

Django middleware attributes are available on the request:

```python
@api.get("/me")
async def get_current_user(request):
    # User from AuthenticationMiddleware
    user = request.user

    # Session from SessionMiddleware
    session = request.state.get("_django_session")

    return {"user_id": user.id if user.is_authenticated else None}
```

### Built-in Python Middleware

```python
from django_bolt.middleware import TimingMiddleware, LoggingMiddleware, ErrorHandlerMiddleware

# Pass classes (not instances) - Django-style
api = BoltAPI(middleware=[
    TimingMiddleware,      # Adds X-Request-ID and X-Response-Time headers
    LoggingMiddleware,     # Logs requests/responses
    ErrorHandlerMiddleware,  # Catches unhandled exceptions
])
```

**TimingMiddleware:**
- Adds `request.state["request_id"]` and `request.state["start_time"]`
- Response headers: `X-Request-ID`, `X-Response-Time`

**LoggingMiddleware:**
- Logs method, path, query params
- Excludes `/health`, `/metrics`, `/docs` by default

**ErrorHandlerMiddleware:**
- Catches unhandled exceptions
- Returns 500 with details in debug mode

### BaseMiddleware Helper

For middleware with path/method exclusions:

```python
from django_bolt.middleware import BaseMiddleware

class AuthMiddleware(BaseMiddleware):
    exclude_paths = ["/health", "/metrics", "/docs/*"]  # Glob patterns
    exclude_methods = ["OPTIONS"]

    async def process_request(self, request):
        if not request.headers.get("authorization"):
            raise HTTPException(401, "Unauthorized")
        return await self.get_response(request)
```

**Features:**
- `exclude_paths` - Glob patterns compiled once at startup
- `exclude_methods` - O(1) set lookup
- Automatic skip check before `process_request`

### Combining Django and Custom Middleware

```python
from django_bolt import BoltAPI
from django_bolt.middleware import TimingMiddleware

# Django middleware runs first, then custom middleware
api = BoltAPI(
    django_middleware=True,
    middleware=[TimingMiddleware],
)
```

## Skipping Middleware

```python
from django_bolt.middleware import skip_middleware, no_compress

# Skip specific middleware
@api.get("/health")
@skip_middleware("cors", "rate_limit")
async def health():
    return {"status": "ok"}

# Skip all middleware
@api.get("/raw")
@skip_middleware("*")
async def raw_endpoint():
    return {"raw": True}

# Skip compression (shorthand)
@api.get("/stream")
@no_compress
async def stream_data():
    return StreamingResponse(...)
```

## Execution Order

```
HTTP Request
     ↓
┌─────────────────────────────────┐
│  RUST MIDDLEWARE (No GIL)       │
│  1. Rate Limiting               │
│     └─ DashMap lookup + check   │
│  2. Authentication              │
│     └─ JWT/API key validation   │
│  3. Guards/Permissions          │
│     └─ Check permissions        │
└─────────────────────────────────┘
     ↓
┌─────────────────────────────────┐
│  PYTHON MIDDLEWARE (GIL)        │
│  4. Django middleware chain     │
│  5. Custom Python middleware    │
└─────────────────────────────────┘
     ↓
Python Handler Execution
     ↓
┌─────────────────────────────────┐
│  RESPONSE PROCESSING (Rust)     │
│  6. CORS headers (pre-compiled) │
│  7. Compression (Actix)         │
└─────────────────────────────────┘
     ↓
HTTP Response
```

**Key Points:**
- Rate limiting runs FIRST (prevents auth bypass attacks)
- Auth and guards run in Rust (no GIL overhead)
- CORS headers added on response (pre-compiled strings)
- Compression negotiated with client

## Performance Characteristics

### Registration-Time Compilation

At server startup:
- Middleware instances created once
- Path exclusion patterns compiled to regex
- CORS headers pre-joined (`"GET, POST, PUT"`)
- Origin sets built for O(1) lookup

### Per-Request Cost

| Middleware Type | Per-Request Cost |
|-----------------|------------------|
| Rate limiting | DashMap lookup (~100ns) |
| JWT validation | Signature verify (Rust) |
| API key validation | Constant-time compare |
| CORS headers | String copy (pre-compiled) |
| Python middleware | GIL acquisition |

### Benchmarks

| Configuration | RPS |
|--------------|-----|
| No middleware | 60k+ |
| Rust middleware only | 55k+ |
| With Python middleware | 30k+ |

## Testing CORS

```python
from django_bolt.testing import TestClient

def test_cors_from_settings():
    client = TestClient(api, use_http_layer=True)

    response = client.get(
        "/api/data",
        headers={"Origin": "https://example.com"}
    )
    assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"

def test_cors_preflight():
    client = TestClient(api, use_http_layer=True)

    response = client.options(
        "/api/users",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
    )
    assert response.status_code == 200
    assert "Access-Control-Allow-Methods" in response.headers
```

## Architecture

### Compilation Flow

```
Python Config (decorators, BoltAPI params)
              ↓
     compile_middleware_meta() [Python]
              ↓
     Dict-based metadata (JSON-serializable)
              ↓
     RouteMetadata::from_python() [Rust]
              ↓
     Typed Rust structs:
     - CorsConfig (pre-compiled headers)
     - RateLimitConfig
     - AuthBackend
     - Guard
              ↓
     Stored in ROUTE_METADATA (AHashMap)
              ↓
     O(1) lookup per request by handler_id
```

### Storage

```rust
// Rate limiters - DashMap for concurrent access
static IP_LIMITERS: DashMap<(usize, String), Arc<Limiter>>

// Route metadata - AHashMap for fast lookup
static ROUTE_METADATA: AHashMap<usize, RouteMetadata>
```

### Security Limits

| Limit | Value | Purpose |
|-------|-------|---------|
| MAX_LIMITERS | 100,000 | Prevent memory exhaustion |
| MAX_KEY_LENGTH | 256 bytes | Prevent memory attacks |
| MAX_HEADERS | 100 | Prevent header flooding |
| BOLT_MAX_HEADER_SIZE | 8KB default | Limit individual header size |

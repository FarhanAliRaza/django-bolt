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

# Or with built-in Bolt middleware (pass classes)
api = BoltAPI(middleware=[TimingMiddleware])

# For custom Django-style middleware, use DjangoMiddlewareStack
from django_bolt.middleware import DjangoMiddlewareStack

class MyCustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        response = self.get_response(request)
        response["X-Custom"] = "value"
        return response

api = BoltAPI(middleware=[DjangoMiddlewareStack([MyCustomMiddleware])])

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

For custom logic and Django middleware integration.

### Custom Django-Style Middleware

For custom middleware using Django's pattern, wrap in `DjangoMiddlewareStack`:

```python
from django_bolt import BoltAPI
from django_bolt.middleware import DjangoMiddlewareStack

# Define custom middleware with Django's pattern
class HeaderAddingMiddleware:
    def __init__(self, get_response):
        """Called ONCE at registration time."""
        self.get_response = get_response

    def __call__(self, request):
        """Called for each request."""
        response = self.get_response(request)
        response["X-Custom-Header"] = "value"
        return response

class ShortCircuitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/blocked":
            from django.http import HttpResponse
            return HttpResponse("Blocked", status=403)
        return self.get_response(request)

# Use custom middleware wrapped in DjangoMiddlewareStack
api = BoltAPI()
api.middleware = [DjangoMiddlewareStack([
    HeaderAddingMiddleware,
    ShortCircuitMiddleware,
])]
```

**Key Points:**
- `__init__(get_response)` is called once at startup, not per-request
- Custom Django-style middleware must be wrapped in `DjangoMiddlewareStack`
- This handles sync/async bridging automatically

### Using Django Middleware

Django-Bolt automatically optimizes Django middleware using `DjangoMiddlewareStack` for best performance.

```python
from django_bolt import BoltAPI

# Load all middleware from settings.MIDDLEWARE (automatically uses DjangoMiddlewareStack)
api = BoltAPI(django_middleware=True)

# Or select specific middleware (automatically wrapped in DjangoMiddlewareStack)
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

#### DjangoMiddlewareStack: Performance Optimization

When you use `django_middleware=True` or pass a list of Django middleware, Django-Bolt automatically wraps them in a `DjangoMiddlewareStack`. This is a **critical performance optimization** that provides 5-8x faster performance for middleware-heavy requests.

**Why it matters:**

Without `DjangoMiddlewareStack` (wrapping each middleware individually):
```python
# DON'T DO THIS - Much slower!
from django_bolt.middleware import DjangoMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

api = BoltAPI(middleware=[
    DjangoMiddleware(SessionMiddleware),        # Bolt→Django conversion
    DjangoMiddleware(AuthenticationMiddleware), # Bolt→Django conversion
    DjangoMiddleware(MessageMiddleware),        # Bolt→Django conversion
])
```

Each middleware does:
- ❌ Bolt→Django request conversion
- ❌ Django→Bolt response conversion
- ❌ Context variable operations
- **Result: N conversions for N middleware**

With `DjangoMiddlewareStack` (automatic when using `django_middleware`):
```python
# RECOMMENDED - Automatically optimized!
api = BoltAPI(django_middleware=[
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
])
```

The stack does:
- ✅ 1 Bolt→Django conversion at start
- ✅ Django's native middleware chain (no conversions between middleware)
- ✅ 1 Django→Bolt conversion at end
- **Result: Only 2 conversions total, regardless of middleware count**

**Manual usage** (only if you need fine control):

```python
from django_bolt.middleware import DjangoMiddlewareStack
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

# Manually create a stack
api = BoltAPI(middleware=[
    DjangoMiddlewareStack([
        SessionMiddleware,
        AuthenticationMiddleware,
        MessageMiddleware,
    ])
])
```

**Performance comparison:**

| Configuration | Conversions | Performance |
|--------------|-------------|-------------|
| Individual wrappers (3 middleware) | 6 conversions | Baseline |
| DjangoMiddlewareStack (3 middleware) | 2 conversions | 5-8x faster |
| DjangoMiddlewareStack (10 middleware) | 2 conversions | 20-30x faster |

**Key takeaway:** Always use `django_middleware=True` or pass a list to `django_middleware=` parameter. Django-Bolt automatically creates an optimized `DjangoMiddlewareStack` for you.

Django middleware attributes are available on the request:

```python
@api.get("/me")
async def get_current_user(request):
    # User from AuthenticationMiddleware
    user = request.user

    # Session from SessionMiddleware
    session = request.state.get("session")

    return {"user_id": user.id if user.is_authenticated else None}
```

### Common Django Middleware

Django-Bolt supports all standard Django middleware. Here are commonly used ones and their effects:

#### Security Middleware

```python
api = BoltAPI(django_middleware=[
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
])
```

**SecurityMiddleware** adds security headers:
- `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
- `Strict-Transport-Security` - Forces HTTPS (if enabled in settings)
- `Referrer-Policy` - Controls referrer information

**XFrameOptionsMiddleware** adds:
- `X-Frame-Options: DENY` - Prevents clickjacking attacks

**CsrfViewMiddleware**:
- Validates CSRF tokens on unsafe methods (POST, PUT, DELETE)
- Adds `csrftoken` cookie for form submissions

#### Session & Authentication

```python
api = BoltAPI(django_middleware=[
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
])

@api.get("/profile")
async def get_profile(request):
    # Session is available via request.state
    session = request.state.get("session")

    # User is available via request.user
    user = request.user

    if user.is_authenticated:
        return {"username": user.username, "email": user.email}
    return {"error": "Not authenticated"}
```

**SessionMiddleware**:
- Provides `request.state["session"]` for session storage
- Manages session cookies automatically

**AuthenticationMiddleware**:
- Sets `request.user` (AnonymousUser for unauthenticated requests)
- Requires SessionMiddleware

#### Messages Framework

```python
api = BoltAPI(django_middleware=[
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
])

@api.post("/action")
async def perform_action(request):
    from django.contrib import messages

    # Add messages that persist across requests
    messages.success(request, "Action completed successfully!")
    messages.info(request, "Processing your request...")

    return {"status": "ok"}
```

**MessageMiddleware**:
- Enables Django's messages framework
- Messages available via `django.contrib.messages`
- Requires SessionMiddleware

#### Common Middleware

```python
api = BoltAPI(django_middleware=[
    'django.middleware.common.CommonMiddleware',
])
```

**CommonMiddleware**:
- Adds `Content-Length` header
- Handles URL normalization (trailing slashes)
- Sets `Vary: Accept-Encoding` header

#### GZip Compression

```python
api = BoltAPI(django_middleware=[
    'django.middleware.gzip.GZipMiddleware',
])
```

**GZipMiddleware**:
- Compresses responses for clients that support gzip
- Checks `Accept-Encoding: gzip` header
- Only compresses responses above a certain size threshold

#### Locale/Internationalization

```python
api = BoltAPI(django_middleware=[
    'django.middleware.locale.LocaleMiddleware',
])
```

**LocaleMiddleware**:
- Processes `Accept-Language` header
- Activates appropriate translation
- Requires `LOCALE_PATHS` in settings

#### Full Production Stack

Here's a typical production middleware configuration:

```python
api = BoltAPI(django_middleware=[
    # Security
    'django.middleware.security.SecurityMiddleware',

    # Session & Auth
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # Common functionality
    'django.middleware.common.CommonMiddleware',

    # CSRF protection (if serving forms)
    'django.middleware.csrf.CsrfViewMiddleware',

    # Messages framework
    'django.contrib.messages.middleware.MessageMiddleware',

    # Clickjacking protection
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
])

@api.get("/dashboard")
async def dashboard(request):
    # All middleware effects are active:
    # - Security headers added
    # - Session available
    # - User authenticated
    # - CSRF protection enabled
    # - Messages framework ready
    # - Clickjacking protection active

    if not request.user.is_authenticated:
        return {"error": "Please log in"}

    # Access session data
    visit_count = request.state.get("session", {}).get("visit_count", 0)
    request.state["session"]["visit_count"] = visit_count + 1

    return {
        "username": request.user.username,
        "visits": visit_count + 1,
    }
```

### Built-in Bolt Middleware

Django-Bolt provides built-in async middleware that extends `BaseMiddleware`. These can be passed directly as classes:

```python
from django_bolt.middleware import TimingMiddleware, LoggingMiddleware, ErrorHandlerMiddleware

# Built-in Bolt middleware - pass as classes (not instances)
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

For **async Bolt middleware** with path/method exclusions, extend `BaseMiddleware`. Unlike Django-style middleware, these are passed directly as classes (no `DjangoMiddlewareStack` needed):

```python
from django_bolt.middleware import BaseMiddleware
from django_bolt.exceptions import HTTPException

class AuthMiddleware(BaseMiddleware):
    exclude_paths = ["/health", "/metrics", "/docs/*"]  # Glob patterns
    exclude_methods = ["OPTIONS"]

    async def process_request(self, request):
        if not request.headers.get("authorization"):
            raise HTTPException(401, "Unauthorized")
        return await self.get_response(request)

# Pass directly as class
api = BoltAPI(middleware=[AuthMiddleware])
```

**Features:**
- `exclude_paths` - Glob patterns compiled once at startup
- `exclude_methods` - O(1) set lookup
- Automatic skip check before `process_request`
- Async by design - works directly in middleware chain

### Combining Django and Custom Middleware

```python
from django_bolt import BoltAPI
from django_bolt.middleware import TimingMiddleware

# Django middleware runs first (automatically as DjangoMiddlewareStack), then custom middleware
api = BoltAPI(
    django_middleware=True,  # Automatically wrapped in DjangoMiddlewareStack
    middleware=[TimingMiddleware],
)
```

**Execution order:**
1. Django middleware stack (all Django middleware in one optimized stack)
2. Custom Bolt middleware (TimingMiddleware, LoggingMiddleware, etc.)
3. Handler execution
4. Response flows back through middleware in reverse order

**Why this is fast:**
- All Django middleware execute in a single optimized stack (1 conversion in, 1 conversion out)
- Custom Bolt middleware don't need conversions (native to Bolt)
- Best of both worlds: Django compatibility + Bolt performance

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
┌─────────────────────────────────────────────────┐
│  PYTHON MIDDLEWARE (GIL)                        │
│  4. DjangoMiddlewareStack (if django_middleware)│
│     ┌─ 1 Bolt→Django conversion                 │
│     ├─ SessionMiddleware                        │
│     ├─ AuthenticationMiddleware                 │
│     ├─ MessageMiddleware                        │
│     ├─ ... (Django's native chain)              │
│     └─ 1 Django→Bolt conversion                 │
│  5. Custom Python middleware                    │
│     └─ TimingMiddleware, LoggingMiddleware, etc.│
└─────────────────────────────────────────────────┘
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
- **DjangoMiddlewareStack optimizes Django middleware** (only 2 conversions regardless of middleware count)
- Custom Bolt middleware run natively (no conversions needed)
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

## Testing Middleware

### Testing CORS

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

### Testing Django Middleware

Verify that Django middleware actually runs and affects requests/responses:

```python
import pytest
from django_bolt import BoltAPI
from django_bolt.testing import TestClient

@pytest.mark.django_db
def test_security_middleware_adds_headers():
    """Test SecurityMiddleware adds security headers."""
    api = BoltAPI(django_middleware=[
        'django.middleware.security.SecurityMiddleware',
    ])

    @api.get("/test")
    async def test_route():
        return {"status": "ok"}

    with TestClient(api) as client:
        response = client.get("/test")
        assert response.status_code == 200

        # Verify security headers are added
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        assert "x-content-type-options" in headers_lower
        assert headers_lower["x-content-type-options"] == "nosniff"

@pytest.mark.django_db
def test_session_middleware_sets_session():
    """Test SessionMiddleware provides session storage."""
    api = BoltAPI(django_middleware=[
        'django.contrib.sessions.middleware.SessionMiddleware',
    ])

    session_available = False

    @api.get("/test")
    async def test_route(request):
        nonlocal session_available
        # Session should be available via request.state
        session = request.state.get("session")
        session_available = session is not None
        return {"status": "ok"}

    with TestClient(api) as client:
        response = client.get("/test")
        assert response.status_code == 200
        assert session_available is True

@pytest.mark.django_db
def test_auth_middleware_sets_user():
    """Test AuthenticationMiddleware sets request.user."""
    api = BoltAPI(django_middleware=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    ])

    user_info = {"has_user": False, "is_anonymous": False}

    @api.get("/test")
    async def test_route(request):
        if hasattr(request, 'user'):
            user_info["has_user"] = True
            user_info["is_anonymous"] = request.user.is_anonymous
        return {"status": "ok"}

    with TestClient(api) as client:
        response = client.get("/test")
        assert response.status_code == 200
        # User should be set (AnonymousUser for unauthenticated)
        assert user_info["has_user"] is True
        assert user_info["is_anonymous"] is True

@pytest.mark.django_db
def test_multiple_middleware_all_run():
    """Test multiple Django middleware execute together."""
    api = BoltAPI(django_middleware=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ])

    checks = {"has_session": False, "has_xframe": False, "has_security": False}

    @api.get("/test")
    async def test_route(request):
        # Check session from SessionMiddleware
        if request.state.get("session") is not None:
            checks["has_session"] = True
        return {"status": "ok"}

    with TestClient(api) as client:
        response = client.get("/test")
        assert response.status_code == 200

        # Verify all middleware ran
        assert checks["has_session"] is True

        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        checks["has_xframe"] = "x-frame-options" in headers_lower
        checks["has_security"] = "x-content-type-options" in headers_lower

        assert checks["has_xframe"] is True
        assert checks["has_security"] is True
```

**Key Testing Points:**
- Use `TestClient` for full HTTP cycle testing
- Check response headers to verify middleware added them
- Check `request.state` and `request.user` for middleware effects
- Test multiple middleware together to ensure they don't conflict
- Use `@pytest.mark.django_db` for tests that need database access

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

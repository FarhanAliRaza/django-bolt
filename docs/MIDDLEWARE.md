# Django-Bolt Middleware System

## Overview

Django-Bolt provides a high-performance middleware pipeline that executes primarily in Rust for minimal overhead. Middleware can be applied globally or per-route, with zero cost when not used.

**Key Features:**
- **Rust-native execution**: Hot-path middleware (auth, rate limit, CORS) runs in Rust without Python GIL overhead
- **Compiled at startup**: Python middleware config is compiled into typed Rust metadata for zero-allocation request processing
- **DashMap concurrent storage**: Thread-safe middleware state with lock-free reads
- **Pre-compiled headers**: CORS headers pre-computed at startup for zero-allocation responses
- **Security limits**: Built-in protections against memory exhaustion attacks

## Quick Start

```python
from django_bolt import BoltAPI
from django_bolt.middleware import rate_limit, cors
from django_bolt.auth import JWTAuthentication, IsAuthenticated

# Global middleware via config
api = BoltAPI(
    middleware_config={
        'cors': {
            'origins': ['http://localhost:3000'],
            'credentials': True
        }
    }
)

# Per-route middleware via decorators
@api.get("/limited")
@rate_limit(rps=100, burst=200)
async def limited_endpoint():
    return {"status": "ok"}

# Authentication using auth parameter (NOT decorator)
@api.get("/protected", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def protected_endpoint(request: dict):
    # Access auth context
    auth = request.get("auth", {})
    user_id = auth.get("user_id")
    return {"user_id": user_id}
```

## Built-in Middleware

### Rate Limiting

**Token Bucket Algorithm**: Django-Bolt uses the token bucket algorithm for rate limiting, providing smooth rate limiting with burst capacity.

```python
@rate_limit(rps=100, burst=200, key="ip")
async def limited_endpoint():
    return {"data": "rate limited"}
```

**Parameters:**
- `rps`: Requests per second limit (sustained rate)
- `burst`: Burst capacity (default: 2x rps) - allows temporary spikes
- `key`: Rate limit key strategy (see below)

**Rate Limit Key Strategies:**
- `"ip"` - Client IP address (checks X-Forwarded-For, X-Real-IP, Remote-Addr headers)
- `"user"` - User ID from authentication context
- `"api_key"` - API key from authentication
- Custom header name - Rate limit by any header (e.g., `"x-tenant-id"`)

**Security Limits:**
- `MAX_LIMITERS`: 100,000 limiters maximum to prevent memory exhaustion
- `MAX_KEY_LENGTH`: 256 bytes maximum key length
- Automatic cleanup: Removes 20% of limiters when limit is reached

**Implementation Details:**
- Uses DashMap for concurrent storage (lock-free reads)
- Per-handler + key limiter instances
- Returns 429 with Retry-After header when limit exceeded

**Example - Custom Key:**
```python
@api.get("/tenant-data")
@rate_limit(rps=50, burst=100, key="x-tenant-id")
async def tenant_data():
    return {"data": "per-tenant rate limited"}
```

### CORS

CORS handling with pre-compiled header strings for zero-allocation responses.

```python
@cors(
    origins=["https://example.com", "https://app.example.com"],
    methods=["GET", "POST", "PUT", "DELETE"],
    headers=["Content-Type", "Authorization"],
    credentials=True,
    max_age=3600
)
async def cors_endpoint():
    return {"data": "with CORS"}
```

**Parameters:**
- `origins`: List of allowed origins (default: empty list for security)
- `methods`: Allowed HTTP methods (default: GET, POST, PUT, PATCH, DELETE, OPTIONS)
- `headers`: Allowed headers (default: Content-Type, Authorization)
- `credentials`: Allow credentials (default: False)
- `max_age`: Preflight cache duration in seconds (default: 3600)

**Security Notes:**
- Default changed from `["*"]` to `[]` (empty) for better security
- Wildcard `"*"` with `credentials=True` is rejected (violates CORS spec)
- Configure `BOLT_CORS_ALLOWED_ORIGINS` in Django settings for global origins

**Pre-compiled Headers:**
At server startup, CORS config is compiled into pre-computed header strings:
- `methods_str`: "GET, POST, PUT, DELETE" (pre-joined)
- `headers_str`: "Content-Type, Authorization" (pre-joined)
- `max_age_str`: "3600" (pre-computed string)

This eliminates per-request string allocations.

**Automatic OPTIONS Handling:**
Django-Bolt automatically handles OPTIONS preflight requests for routes with CORS configured. No explicit OPTIONS handler needed.

#### Testing CORS with TestClient

Django-Bolt's TestClient provides full support for testing CORS middleware, including Django settings-based configuration and preflight request handling.

**Django Settings-Based CORS:**

TestClient automatically reads CORS configuration from Django settings:

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://app.example.com"
]
CORS_ALLOW_ALL_ORIGINS = False  # Set to True for wildcard (*)

# test_cors.py
from django_bolt.testing import TestClient
from myapp.api import api

def test_cors_from_settings():
    client = TestClient(api)

    # Test with allowed origin
    response = client.get(
        "/api/data",
        headers={"Origin": "https://example.com"}
    )
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"

    # Test with disallowed origin
    response = client.get(
        "/api/data",
        headers={"Origin": "https://evil.com"}
    )
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response.headers
```

**Full Middleware Validation:**

Use `use_http_layer=True` to test CORS middleware through the complete request pipeline:

```python
def test_cors_with_http_layer():
    client = TestClient(api, use_http_layer=True)

    # Test CORS headers on actual request
    response = client.get(
        "/api/users",
        headers={
            "Origin": "https://example.com",
            "Content-Type": "application/json"
        }
    )

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"
    assert "Access-Control-Allow-Credentials" in response.headers
```

**Testing CORS Preflight Requests:**

TestClient supports OPTIONS preflight validation:

```python
def test_cors_preflight():
    client = TestClient(api, use_http_layer=True)

    # Send OPTIONS preflight request
    response = client.options(
        "/api/users",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type, Authorization"
        }
    )

    # Validate preflight response
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"
    assert response.headers["Access-Control-Allow-Methods"] == "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    assert "Content-Type" in response.headers["Access-Control-Allow-Headers"]
    assert "Authorization" in response.headers["Access-Control-Allow-Headers"]
    assert response.headers["Access-Control-Max-Age"] == "3600"
```

**Route-Level CORS Override:**

Route-level `@cors()` decorators override Django settings:

```python
# api.py
@api.get("/special")
@cors(origins=["https://special.com"], credentials=False)
async def special_endpoint():
    return {"data": "special"}

# test_cors.py
def test_route_level_cors_override():
    client = TestClient(api, use_http_layer=True)

    # Route-level CORS overrides Django settings
    response = client.get(
        "/special",
        headers={"Origin": "https://special.com"}
    )
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "https://special.com"

    # Django settings origin won't work for this route
    response = client.get(
        "/special",
        headers={"Origin": "https://example.com"}
    )
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response.headers
```

**Architecture Note:**

CORS middleware runs in Rust for both production and testing environments. The testing path uses the same code as production (shared functions in `src/validation.rs`), ensuring that tests accurately reflect production behavior. This means:

- JWT validation logic is identical in tests and production
- CORS origin matching uses the same algorithm
- Preflight request handling follows the exact same code path
- No mocking or test-specific behavior differences

### Authentication

**IMPORTANT:** Authentication is NOT a decorator. Use the `auth` parameter in route definition.

```python
from django_bolt.auth import JWTAuthentication, APIKeyAuthentication
from django_bolt.auth import IsAuthenticated, IsAdminUser

# JWT Authentication
@api.get("/protected", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def protected_route(request: dict):
    auth = request.get("auth", {})
    user_id = auth.get("user_id")
    is_staff = auth.get("is_staff", False)
    return {"user_id": user_id, "is_staff": is_staff}

# API Key Authentication
@api.get("/api-data", auth=[APIKeyAuthentication(api_keys={"key1", "key2"})], guards=[IsAuthenticated()])
async def api_data(request: dict):
    auth = request.get("auth", {})
    return {"authenticated": True}

# Multiple authentication backends
@api.get("/flexible", auth=[JWTAuthentication(), APIKeyAuthentication()], guards=[IsAuthenticated()])
async def flexible_auth(request: dict):
    # Tries JWT first, then API key
    auth = request.get("auth", {})
    backend = auth.get("auth_backend")  # "jwt" or "api_key"
    return {"backend": backend}
```

**JWT Authentication:**
- Validates JWT signature in Rust (no GIL overhead)
- Supports algorithms: HS256, HS384, HS512, RS256, RS384, RS512, ES256, ES384
- Checks expiration (`exp`) and not-before (`nbf`) claims
- Optional audience and issuer validation

**API Key Authentication:**
- Constant-time key comparison (security)
- Supports Bearer or ApiKey prefix in header
- Rejects requests if no keys configured (security)
- Per-key permissions support

**Auth Context:**
Authentication populates `request.auth` with:
- `user_id`: User identifier (from JWT `sub` or API key)
- `is_staff`: Staff status (from JWT claims)
- `is_admin`: Admin status (from JWT `is_superuser` or `is_admin`)
- `auth_backend`: Backend name ("jwt" or "api_key")
- `permissions`: List of permissions
- `auth_claims`: Full JWT claims (JWT only)

## Middleware Context

Authentication context is available via `request.auth`:

```python
@api.get("/me", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_current_user(request: dict):
    auth = request.get("auth", {})

    # Access auth data
    user_id = auth.get("user_id")
    is_staff = auth.get("is_staff", False)
    is_admin = auth.get("is_admin", False)
    backend = auth.get("auth_backend")
    permissions = auth.get("permissions", [])

    # JWT-specific claims
    auth_claims = auth.get("auth_claims", {})

    return {
        "user_id": user_id,
        "is_staff": is_staff,
        "is_admin": is_admin,
        "backend": backend,
        "permissions": permissions
    }
```

## Skipping Global Middleware

```python
from django_bolt.middleware import skip_middleware

@api.get("/no-cors")
@skip_middleware("cors", "rate_limit")
async def no_middleware():
    return {"unrestricted": True}
```

## Middleware Compilation System

Django-Bolt compiles Python middleware configuration into typed Rust metadata at server startup, eliminating per-request Python overhead.

### Compilation Flow

```
Python Middleware Config (api.py)
           ↓
   compile_middleware_meta() [Python]
           ↓
   Python Dict (JSON-serializable)
           ↓
   register_middleware_metadata() [Rust]
           ↓
   RouteMetadata::from_python() [Rust]
           ↓
   Typed Rust Structs:
   - CorsConfig (pre-compiled header strings)
   - RateLimitConfig
   - AuthBackend (JWT/APIKey)
   - Guard (permissions)
           ↓
   Stored in ROUTE_METADATA (AHashMap)
           ↓
   Per-request O(1) lookup by handler_id
           ↓
   Rust middleware execution (NO GIL)
```

### Compilation Benefits

1. **Zero-cost abstraction**: No Python execution during request processing
2. **Type safety**: Rust enums catch configuration errors at startup
3. **Pre-computed strings**: CORS headers joined once at startup
4. **Fast lookups**: AHashMap lookup by handler_id (O(1))
5. **Security validation**: Config errors fail at startup, not runtime

### Example Compilation

```python
# Python config (at route definition)
@api.get("/data")
@cors(origins=["https://example.com"], methods=["GET", "POST"], max_age=7200)
@rate_limit(rps=100, burst=200, key="ip")
async def get_data():
    return {"data": "example"}
```

Compiles to Rust:

```rust
RouteMetadata {
    cors_config: Some(CorsConfig {
        origins: vec!["https://example.com"],
        methods: vec!["GET", "POST"],
        methods_str: "GET, POST",  // Pre-joined!
        max_age: 7200,
        max_age_str: "7200",  // Pre-computed!
        // ... other fields
    }),
    rate_limit_config: Some(RateLimitConfig {
        rps: 100,
        burst: 200,
        key_type: "ip",
    }),
    // ... other fields
}
```

### Custom Middleware (Python)

For custom middleware logic not available in Rust:

```python
from django_bolt.middleware import Middleware

class LoggingMiddleware(Middleware):
    async def process_request(self, request, call_next):
        print(f"Request: {request['method']} {request['path']}")
        response = await call_next(request)
        return response

api = BoltAPI(middleware=[LoggingMiddleware()])
```

**Note**: Custom Python middleware incurs GIL overhead. Use built-in Rust middleware when possible for best performance.

## Middleware Execution Order

Middleware executes in a specific order for optimal performance and correctness:

```
1. RATE LIMITING (Rust, pre-GIL)
   ├─ Check rate limit for handler_id + key
   ├─ DashMap lookup: IP_LIMITERS[(handler_id, key)]
   ├─ Token bucket check
   └─ Early return 429 if exceeded

2. AUTHENTICATION (Rust, pre-GIL)
   ├─ Try each auth backend in order
   ├─ JWT: Verify signature, check exp/nbf
   ├─ API Key: Constant-time comparison
   └─ Build AuthContext (no Python yet)

3. GUARDS/PERMISSIONS (Rust, pre-GIL)
   ├─ Evaluate guards using AuthContext
   ├─ IsAuthenticated, IsAdmin, IsStaff
   ├─ HasPermission, HasAnyPermission, HasAllPermissions
   └─ Early return 401/403 if denied

4. PYTHON HANDLER (acquire GIL)
   ├─ Build PyRequest with auth context
   ├─ Call Python handler
   └─ Generate response

5. CORS HEADERS (Rust, post-handler)
   ├─ Add Access-Control-Allow-Origin
   ├─ Add Access-Control-Allow-Credentials
   ├─ Add Access-Control-Expose-Headers
   └─ Use pre-compiled header strings (zero allocation)

6. COMPRESSION (Actix, post-response)
   └─ Negotiate with client Accept-Encoding
```

**Key Points:**
- Rate limiting happens FIRST (before auth) to prevent auth bypass attacks
- Authentication and guards run in Rust without GIL overhead
- CORS headers added AFTER handler execution (on response)
- Compression is always enabled but only activates when client supports it

## Performance Characteristics

### Rust Execution (No GIL Overhead)

**Hot-path operations execute in Rust:**
- Rate limiting: DashMap lookup + token bucket algorithm
- JWT validation: Signature verification, expiration checks
- API key validation: Constant-time comparison
- Guard evaluation: Permission checks
- CORS headers: Pre-compiled string insertion

**Zero allocations for:**
- CORS header values (pre-computed at startup)
- Rate limit responses (static JSON strings)
- Header lookups (direct AHashMap access)

### DashMap Concurrent Storage

**Rate Limiting Storage:**
```rust
static IP_LIMITERS: Lazy<DashMap<(usize, String), Arc<Limiter>>> = Lazy::new(DashMap::new);
```

- **Lock-free reads**: Multiple threads can read simultaneously
- **Concurrent writes**: Lock striping for minimal contention
- **Per-handler isolation**: Key includes handler_id to prevent cross-route interference

**Benefits:**
- No global lock contention
- Scales linearly with CPU cores
- Sub-microsecond lookups

### Pre-compiled Header Strings

At startup, CORS config compiles header strings once:

```rust
pub struct CorsConfig {
    pub methods: Vec<String>,           // ["GET", "POST"]
    pub methods_str: String,            // "GET, POST" (pre-joined!)
    pub headers: Vec<String>,           // ["Content-Type"]
    pub headers_str: String,            // "Content-Type" (pre-joined!)
    pub max_age: u32,                   // 3600
    pub max_age_str: String,            // "3600" (pre-computed!)
}
```

**Per-request cost**: Zero allocations, just copy pre-computed strings to response headers.

### Security Limits

**Rate Limiting:**
- `MAX_LIMITERS`: 100,000 (prevents memory exhaustion)
- `MAX_KEY_LENGTH`: 256 bytes (prevents memory attacks)
- Automatic cleanup: Removes 20% when limit reached

**Header Processing:**
- `MAX_HEADERS`: 100 headers per request
- `BOLT_MAX_HEADER_SIZE`: Configurable per-header size limit (default 8KB)

**API Key Authentication:**
- Rejects requests if no keys configured (fail-secure)
- Constant-time comparison (timing attack prevention)

## Architecture

### Request Flow with Middleware

```
HTTP Request → Actix Web (Rust)
           ↓
    Route Matching (matchit - zero-copy)
           ↓
    ┌──────────────────────────────────┐
    │  MIDDLEWARE PIPELINE (Rust)      │
    │  ──────────────────────────────  │
    │  1. Rate Limiting                │
    │     └─ DashMap lookup            │
    │     └─ Token bucket check        │
    │                                  │
    │  2. Authentication               │
    │     └─ JWT signature verify      │
    │     └─ API key validation        │
    │                                  │
    │  3. Guards/Permissions           │
    │     └─ Check IsAuthenticated     │
    │     └─ Check HasPermission       │
    └──────────────────────────────────┘
           ↓
    GIL Acquisition (SINGLE time)
           ↓
    Python Handler Execution
      - Parameter extraction
      - Business logic
      - Response generation
           ↓
    GIL Release
           ↓
    ┌──────────────────────────────────┐
    │  RESPONSE MIDDLEWARE (Rust)      │
    │  ──────────────────────────────  │
    │  1. CORS Headers                 │
    │     └─ Pre-compiled strings      │
    │                                  │
    │  2. Compression (Actix)          │
    │     └─ Client-negotiated         │
    └──────────────────────────────────┘
           ↓
    HTTP Response
```

**Performance Impact:**
- Routes without middleware: 60k+ RPS (zero overhead)
- Routes with Rust middleware: 55k+ RPS (minimal overhead)
- Routes with Python middleware: 30k+ RPS (GIL overhead)

The middleware system maintains Django-Bolt's high performance while enabling powerful request processing capabilities.
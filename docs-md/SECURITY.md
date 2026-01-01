# Security Guide

Django-Bolt includes comprehensive security features to protect your API endpoints. This guide covers authentication, authorization, CORS, rate limiting, and security best practices.

## Table of Contents

- [Authentication](#authentication)
  - [JWT Authentication](#jwt-authentication)
  - [API Key Authentication](#api-key-authentication)
  - [Session Authentication](#session-authentication)
  - [Token Revocation](#token-revocation)
  - [Auth Context](#auth-context)
- [Authorization & Guards](#authorization--guards)
- [CORS Security](#cors-security)
- [Rate Limiting](#rate-limiting)
- [Server-Sent Events (SSE) Security](#server-sent-events-sse-security)
  - [Thread Resource Model](#thread-resource-model)
  - [Thread Exhaustion Prevention](#thread-exhaustion-prevention)
  - [Generator Cleanup Errors](#generator-cleanup-errors)
  - [Security Best Practices for SSE](#security-best-practices-for-sse)
- [File Serving Security](#file-serving-security)
- [Input Validation](#input-validation)
- [Security Best Practices](#security-best-practices)
- [Security Settings Reference](#security-settings-reference)

---

## Authentication

Django-Bolt provides built-in authentication backends that run in Rust for maximum performance, avoiding Python GIL overhead.

### JWT Authentication

JWT (JSON Web Token) authentication provides stateless, token-based authentication.

#### Basic Usage

```python
from django_bolt import BoltAPI
from django_bolt.auth import JWTAuthentication, IsAuthenticated

api = BoltAPI()

# Configure JWT authentication
jwt_auth = JWTAuthentication(
    secret="your-secret-key",  # Or uses Django's SECRET_KEY by default
    algorithms=["HS256"],
    audience="your-app",  # Optional
    issuer="your-service",  # Optional
)

@api.get("/protected", auth=[jwt_auth], guards=[IsAuthenticated()])
async def protected_route(request):
    auth = request.get("auth", {})
    user_id = auth.get("user_id")
    return {"user_id": user_id}
```

#### Creating JWT Tokens

```python
from django_bolt.auth.jwt_utils import create_jwt_for_user
from django.contrib.auth import get_user_model

User = get_user_model()
user = await User.objects.aget(username="john")

# Create token for Django user
token = create_jwt_for_user(
    user,
    secret="your-secret-key",
    algorithm="HS256",
    expires_in=3600,  # 1 hour
    extra_claims={"role": "admin"}  # Optional
)
```

#### JWT Configuration Options

- **secret**: Secret key for signing tokens (defaults to Django's `SECRET_KEY`)
- **algorithms**: List of allowed algorithms (e.g., `["HS256"]`)
  - **IMPORTANT**: Only the FIRST algorithm in the list is used for validation
  - No fallback to other algorithms - if validation fails with the first algorithm, the request is rejected
  - For maximum performance, specify exactly one algorithm: `algorithms=["HS256"]`
  - Supported algorithms: HS256, HS384, HS512, RS256, RS384, RS512, ES256, ES384
- **header**: Header name to read token from (default: `"authorization"`)
- **audience**: Expected audience claim (optional)
- **issuer**: Expected issuer claim (optional)
- **revocation_store**: Token revocation store (see [Token Revocation](#token-revocation))
- **revoked_token_handler**: Alias for `revocation_store` (deprecated, use `revocation_store`)
- **require_jti**: Require JWT ID claim in tokens (default: `False`, auto-enabled if revocation is configured)

#### Security Considerations

**✅ Secret Key Validation**

```python
# GOOD: Explicit secret
jwt_auth = JWTAuthentication(secret="strong-secret-key-here")

# GOOD: Uses Django SECRET_KEY (must be configured)
jwt_auth = JWTAuthentication()  # Automatically uses settings.SECRET_KEY

# BAD: Will raise ImproperlyConfigured
jwt_auth = JWTAuthentication(secret=None)  # Error!
jwt_auth = JWTAuthentication(secret="")    # Error!
```

**✅ Algorithm Specification**

```python
# Best practice: Specify ONE algorithm for maximum performance
jwt_auth = JWTAuthentication(
    secret="secret",
    algorithms=["HS256"]  # Single algorithm - optimal performance
)

# Multiple algorithms in list: Only FIRST is used (no fallback!)
jwt_auth = JWTAuthentication(
    secret="secret",
    algorithms=["HS256", "HS512"]  # ⚠️ Only HS256 is validated!
    # HS512 is NEVER tried - if HS256 validation fails, request is rejected
)
```

**Performance Note**: Authentication runs in Rust without Python GIL overhead. Using a single algorithm ensures zero overhead from algorithm selection logic.

**❌ Empty Algorithm List**

```python
# Defaults to ["HS256"] if empty
jwt_auth = JWTAuthentication(algorithms=[])  # Uses HS256
```

### API Key Authentication

API key authentication provides simple, stateless authentication using pre-shared keys.

```python
from django_bolt.auth import APIKeyAuthentication, IsAuthenticated

api_key_auth = APIKeyAuthentication(
    api_keys={"key1", "key2", "key3"},
    header="x-api-key",  # Default header
    key_permissions={
        "key1": ["read", "write"],
        "key2": ["read"]
    }
)

@api.get("/api/data", auth=[api_key_auth], guards=[IsAuthenticated()])
async def get_data(request):
    auth = request.get("auth", {})
    permissions = auth.get("permissions", [])
    return {"permissions": permissions}
```

#### Security Considerations

**✅ Non-Empty Key Set Required**

```python
# GOOD: API keys provided
api_key_auth = APIKeyAuthentication(api_keys={"key1", "key2"})

# BAD: Empty set is rejected (prevents authentication bypass)
api_key_auth = APIKeyAuthentication(api_keys=set())  # No access granted!
```

**✅ Constant-Time Comparison**
API keys are compared using constant-time algorithms to prevent timing attacks.

### Token Revocation

Django-Bolt supports token revocation for JWT tokens with `jti` (JWT ID) claims.

```python
from django_bolt.auth import JWTAuthentication
from django_bolt.auth.revocation import (
    InMemoryRevocation,
    DjangoCacheRevocation,
    DjangoORMRevocation
)

# In-Memory Revocation (single process)
revocation = InMemoryRevocation()

# Django Cache Revocation (multi-process)
revocation = DjangoCacheRevocation(cache_alias="default")

# Django ORM Revocation (persistent)
revocation = DjangoORMRevocation()

# Configure JWT with revocation support
jwt_auth = JWTAuthentication(
    secret="secret",
    revocation_store=revocation,  # Preferred parameter name
    require_jti=True  # Enforce jti claim in all tokens
)

# Alternative (deprecated): revoked_token_handler
jwt_auth = JWTAuthentication(
    secret="secret",
    revoked_token_handler=revocation,  # Alias for revocation_store
    require_jti=True
)

# Revoke a token
await revocation.revoke_token("token-jti-here")

# Check if revoked
is_revoked = await revocation.is_revoked("token-jti-here")
```

#### Auto-Enable require_jti

When `revocation_store` or `revoked_token_handler` is provided, `require_jti` is automatically enabled:

```python
# require_jti is automatically set to True
jwt_auth = JWTAuthentication(
    secret="secret",
    revocation_store=DjangoCacheRevocation()
)
# Token validation will reject tokens without 'jti' claim
```

### Auth Context

After successful authentication, Django-Bolt populates the request context with authentication information. This context is built in Rust and passed to your Python handlers.

#### Accessing Auth Context

```python
@api.get("/protected", auth=[jwt_auth], guards=[IsAuthenticated()])
async def protected_route(request):
    # Get authentication context
    auth = request.get("auth", {})

    # Access auth fields
    user_id = auth.get("user_id")          # User identifier
    is_staff = auth.get("is_staff", False)  # Staff status
    is_admin = auth.get("is_admin", False)  # Admin/superuser status
    backend = auth.get("auth_backend")      # "jwt", "api_key", or "session"
    permissions = auth.get("permissions", []) # List of permissions

    return {
        "user_id": user_id,
        "is_staff": is_staff,
        "is_admin": is_admin,
        "permissions": permissions
    }
```

#### Auth Context Fields

The following fields are populated in the auth context:

| Field          | Type          | Description                 | Source                                                    |
| -------------- | ------------- | --------------------------- | --------------------------------------------------------- |
| `user_id`      | `str \| None` | User identifier             | JWT `sub` claim or `apikey:{key}` for API keys            |
| `is_staff`     | `bool`        | Staff status                | JWT `is_staff` claim (default: `False`)                   |
| `is_admin`     | `bool`        | Admin/superuser status      | JWT `is_superuser` or `is_admin` claim (default: `False`) |
| `auth_backend` | `str`         | Authentication backend used | `"jwt"`, `"api_key"`, or `"session"`                      |
| `permissions`  | `list[str]`   | User permissions            | JWT `permissions` claim or API key permissions            |
| `auth_claims`  | `dict`        | Full JWT claims (JWT only)  | All JWT claims including custom fields                    |

#### JWT-Specific Fields

When using JWT authentication, the `auth_claims` field contains all JWT claims:

```python
@api.get("/profile", auth=[jwt_auth])
async def profile(request):
    auth = request.get("auth", {})
    claims = auth.get("auth_claims", {})

    # Standard JWT claims
    sub = claims.get("sub")          # Subject (user ID)
    exp = claims.get("exp")          # Expiration timestamp
    iat = claims.get("iat")          # Issued at timestamp
    iss = claims.get("iss")          # Issuer
    aud = claims.get("aud")          # Audience
    jti = claims.get("jti")          # JWT ID

    # Custom claims (from extra_claims in create_jwt_for_user)
    role = claims.get("role")
    department = claims.get("department")

    return {"sub": sub, "role": role}
```

#### API Key Auth Context

For API key authentication, the `user_id` is in the format `apikey:{key}`:

```python
@api.get("/data", auth=[api_key_auth])
async def get_data(request):
    auth = request.get("auth", {})
    user_id = auth.get("user_id")  # Returns "apikey:abc123"
    permissions = auth.get("permissions", [])  # From key_permissions

    return {"user_id": user_id, "permissions": permissions}
```

#### Performance Note

Auth context population happens in Rust using PyO3. Only the necessary fields are copied to Python, minimizing GIL overhead. The entire authentication process (token validation, permission extraction) runs in Rust without acquiring the Python GIL.

---

## Authorization & Guards

Guards provide permission checks that run in Rust before your Python handler executes.

### Built-in Guards

```python
from django_bolt.auth import (
    IsAuthenticated,
    IsAdminUser,
    IsStaff,
    HasPermission,
    HasAnyPermission,
    HasAllPermissions,
)

# Require authentication
@api.get("/profile", guards=[IsAuthenticated()])
async def profile(request): ...

# Require admin user
@api.get("/admin", guards=[IsAdminUser()])
async def admin_panel(request): ...

# Require staff member
@api.get("/staff", guards=[IsStaff()])
async def staff_panel(request): ...

# Require specific permission
@api.post("/articles", guards=[HasPermission("blog.add_article")])
async def create_article(request): ...

# Require any of the permissions
@api.get("/content", guards=[HasAnyPermission(["blog.view", "news.view"])])
async def view_content(request): ...

# Require all permissions
@api.post("/publish", guards=[HasAllPermissions(["blog.add", "blog.publish"])])
async def publish_article(request): ...
```

### Custom Guards

```python
from django_bolt.auth import BaseGuard

class HasRoleGuard(BaseGuard):
    def __init__(self, role: str):
        self.role = role

    async def __call__(self, request):
        auth = request.get("auth", {})
        user_role = auth.get("role")

        if user_role != self.role:
            from django_bolt.exceptions import Forbidden
            raise Forbidden(f"Requires role: {self.role}")

# Use custom guard
@api.get("/admin", guards=[HasRoleGuard("admin")])
async def admin_only(request): ...
```

---

## CORS Security

Django-Bolt provides secure CORS handling with proper validation.

### Configuration

```python
from django_bolt.middleware import cors

# Per-route CORS (NOT recommended for production)
@api.get("/public")
@cors(origins=["https://example.com"], credentials=True)
async def public_endpoint(): ...

# Global CORS via Django settings (RECOMMENDED)
# In settings.py:
BOLT_CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://app.example.com",
]
```

### Security Features

**✅ Wildcard + Credentials Validation**

```python
# BAD: This is rejected (violates CORS spec)
@cors(origins=["*"], credentials=True)  # Error!

# GOOD: Specific origins with credentials
@cors(origins=["https://example.com"], credentials=True)

# GOOD: Wildcard without credentials
@cors(origins=["*"], credentials=False)
```

**✅ Secure Defaults**

```python
# Default: Empty origin list (no origins allowed)
# You must explicitly configure allowed origins
@cors()  # No origins allowed! Returns 403 on CORS preflight

# Django setting default (secure)
BOLT_CORS_ALLOWED_ORIGINS = []  # Empty by default
```

**✅ Origin Validation**

- Origins are validated against the allowlist
- Requests from unauthorized origins receive no CORS headers
- Proper `Vary` headers for caching

### Django Settings Integration

```python
# settings.py
BOLT_CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://app.example.com",
]

# Routes can use these global settings via middleware configuration
# Note: Route-level @cors() decorator overrides global settings
@api.get("/api/data")
async def get_data(): ...
```

**Performance Note**: CORS origins are read from Django settings ONCE at server startup and cached in the Rust layer. Changes to `BOLT_CORS_ALLOWED_ORIGINS` require a server restart to take effect.

---

## Rate Limiting

Prevent abuse with built-in rate limiting that runs in Rust.

### Basic Usage

```python
from django_bolt.middleware import rate_limit

@api.get("/search")
@rate_limit(rps=10, burst=20)  # 10 requests/sec, burst of 20
async def search(query: str): ...
```

### Configuration Options

```python
@rate_limit(
    rps=100,        # Requests per second
    burst=200,      # Burst capacity
    key="ip"        # Rate limit by IP (default)
)

# Rate limit by custom header
@rate_limit(rps=50, key="x-api-key")

# Rate limit by user ID (from auth context)
@rate_limit(rps=100, key="user_id")
```

### Security Features

**✅ Key Length Validation**

```python
# Keys are limited to 256 bytes to prevent memory attacks
# Long keys are rejected with 400 Bad Request
```

**✅ Automatic Cleanup**

```python
# Maximum 100,000 rate limiters
# Automatic cleanup when limit is reached (removes 20% oldest)
```

**✅ IP-based Rate Limiting**

```python
# Checks X-Forwarded-For, X-Real-IP headers
# Falls back to peer address
# Validates IP format
```

---

## Server-Sent Events (SSE) Security

Server-Sent Events (SSE) provides long-lived connections for streaming responses. This introduces unique security and resource management considerations.

### Thread Resource Model

SSE connections use dedicated OS threads for streaming:

- **Async SSE**: Uses Tokio async tasks (lightweight, many connections supported)
- **Sync SSE**: Uses dedicated OS threads (one thread per connection)
  - Each sync generator runs on its own OS thread to avoid blocking Tokio's thread pool
  - This prevents SSE connections from starving other blocking operations in your app

### Thread Exhaustion Prevention

**Problem**: A malicious client could open thousands of SSE connections, exhausting OS thread resources and preventing the server from handling other requests.

**Solution**: Django-Bolt provides connection limiting.

#### Configuration

Can be configured via Django settings or environment variable (env var takes precedence):

```python
# settings.py - Django Setting (default: 1000)
# NOTE: Setting name is BOLT_* (without DJANGO_ prefix)
BOLT_MAX_SYNC_STREAMING_THREADS = 1000
```

Or via environment variable:

```bash
# Environment variable (without DJANGO_ prefix would also work but convention uses it)
export DJANGO_BOLT_MAX_SYNC_STREAMING_THREADS=1000
```

**IMPORTANT: Django Setting vs Environment Variable Names**

| Type                     | Variable Name                            | Example                                              |
| ------------------------ | ---------------------------------------- | ---------------------------------------------------- |
| **Django Setting**       | `BOLT_MAX_SYNC_STREAMING_THREADS`        | `BOLT_MAX_SYNC_STREAMING_THREADS = 1000`             |
| **Environment Variable** | `DJANGO_BOLT_MAX_SYNC_STREAMING_THREADS` | `export DJANGO_BOLT_MAX_SYNC_STREAMING_THREADS=1000` |

**Precedence** (first match wins):

1. Environment variable: `DJANGO_BOLT_MAX_SYNC_STREAMING_THREADS`
2. Django setting: `BOLT_MAX_SYNC_STREAMING_THREADS` (no `DJANGO_` prefix!)
3. Default: 1000

#### How It Works

1. **Check limit before spawning thread**: When a sync SSE request arrives, the server checks current active connections
2. **Reject if limit exceeded**: If limit is reached, server sends SSE retry directive (RFC 6553)
3. **Track active connections**: Counter increments when thread spawns, decrements when thread exits
4. **No per-request overhead**: Uses atomic counters (lock-free)

#### Example

```python
# settings.py
BOLT_MAX_SYNC_STREAMING_THREADS = 500  # Limit to 500 concurrent threads (default: 1000)

@api.get("/stream/events")
async def stream_events():
    """SSE endpoint limited to 500 concurrent streaming threads."""
    def gen():
        for i in range(100):
            yield f"data: event-{i}\n\n"
            await asyncio.sleep(0.1)

    return StreamingResponse(gen(), media_type="text/event-stream")
```

Server logs:

```
[SSE INFO] Spawning sync streaming thread (active: 42)
[SSE INFO] Sync streaming thread closed (remaining: 41)
[SSE WARNING] Sync streaming thread limit reached: 500 >= 500
```

#### Recommended Limits

- **Small apps** (< 100 concurrent users): 500-1000 connections
- **Medium apps** (100-1000 concurrent users): 2000-5000 connections
- **Large apps** (1000+ concurrent users): 5000+ connections, use load balancing

### Generator Cleanup Errors

SSE generators must be properly cleaned up when clients disconnect to prevent resource leaks.

#### Error Logging

Django-Bolt logs all cleanup errors to stderr:

```
[SSE WARNING] Error during sync generator cleanup on client disconnect: <error>
[SSE WARNING] Error during sync generator cleanup at end of stream: <error>
[SSE WARNING] Unable to get task locals for async generator cleanup on disconnect
[SSE ERROR] Failed to spawn sync generator thread: <error>
```

**Note**: These errors should never occur in normal operation. If you see them, they indicate:

1. A problem in your generator's cleanup code (finally block)
2. System resource exhaustion (thread limit hit)
3. Python runtime errors in generator cleanup

#### Example - Generator with Cleanup

```python
import asyncio
from django_bolt import BoltAPI, StreamingResponse

api = BoltAPI()

@api.get("/stream/with-cleanup")
async def stream_with_cleanup():
    """SSE with proper resource cleanup."""
    async def gen():
        db_connection = None
        try:
            # Setup
            db_connection = await get_db_connection()

            # Stream events
            for i in range(100):
                event = await db_connection.fetch_one()
                yield f"data: {event}\n\n"
                await asyncio.sleep(0.1)

        finally:
            # Cleanup (runs even if client disconnects)
            if db_connection:
                await db_connection.close()
                print("Database connection closed")

    return StreamingResponse(gen(), media_type="text/event-stream")
```

When client disconnects:

```
[SSE INFO] Spawning sync SSE connection (active: 5)
Database connection closed
[SSE INFO] Sync SSE connection closed (remaining: 4)
```

### Security Best Practices for SSE

**1. Set appropriate sync streaming thread limits**

```python
# settings.py (Django Setting - without DJANGO_ prefix)
BOLT_MAX_SYNC_STREAMING_THREADS = 500

# Or via environment variable (with DJANGO_ prefix)
export DJANGO_BOLT_MAX_SYNC_STREAMING_THREADS=500
```

**2. Add authentication to SSE endpoints**

```python
from django_bolt.auth import JWTAuthentication, IsAuthenticated

jwt_auth = JWTAuthentication()

@api.get("/stream", auth=[jwt_auth], guards=[IsAuthenticated()])
async def stream_events(request):
    # Only authenticated users can stream
    auth = request.get("auth", {})
    user_id = auth.get("user_id")

    async def gen():
        async for event in get_user_events(user_id):
            yield f"data: {event}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
```

**3. Implement per-user rate limiting**

```python
from django_bolt.middleware import rate_limit

@api.get("/stream")
@rate_limit(rps=10, burst=20, key="user_id")  # 10 streams per user per second
async def stream_user_data(request):
    # User can open multiple connections but is rate-limited
    async def gen():
        async for event in get_events():
            yield f"data: {event}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
```

**4. Implement request timeouts**

```python
import asyncio

@api.get("/stream")
async def stream_events():
    async def gen():
        try:
            for i in range(1000):
                yield f"data: {i}\n\n"
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            # Client disconnected, cleanup happens in finally block
            raise

    return StreamingResponse(gen(), media_type="text/event-stream")
```

**5. Monitor active streaming threads**

```python
from django_bolt.state import ACTIVE_SYNC_STREAMING_THREADS, get_max_sync_streaming_threads
import logging
from datetime import datetime

logger = logging.getLogger("sse")

@api.get("/status")
async def streaming_status(request):
    """Get sync streaming thread statistics."""
    active = ACTIVE_SYNC_STREAMING_THREADS.load(Ordering::Relaxed)
    max_threads = get_max_sync_streaming_threads()
    return {
        "active_sync_streaming_threads": active,
        "max_sync_streaming_threads": max_threads,
        "utilization_percent": (active / max_threads * 100) if max_threads > 0 else 0,
        "timestamp": datetime.now().isoformat()
    }
```

### Configuration Variables

**Django Settings** (in `settings.py` - use `BOLT_*` prefix without `DJANGO_`):

```python
# Maximum concurrent sync streaming threads (default: 1000)
BOLT_MAX_SYNC_STREAMING_THREADS = 1000
```

**Environment Variables** (override Django settings):

```bash
# Maximum concurrent sync streaming threads (default: 1000)
export DJANGO_BOLT_MAX_SYNC_STREAMING_THREADS=1000

# Stream batch size for regular streaming (async)
export DJANGO_BOLT_STREAM_BATCH_SIZE=20

# Stream batch size for SSE (sync)
export DJANGO_BOLT_STREAM_SYNC_BATCH_SIZE=5

# Channel capacity for streaming responses
export DJANGO_BOLT_STREAM_CHANNEL_CAPACITY=32
```

### Monitoring and Alerts

```python
# Example: Alert if too many streaming threads
from django_bolt.state import ACTIVE_SYNC_STREAMING_THREADS, get_max_sync_streaming_threads
import logging
import asyncio

logger = logging.getLogger("django_bolt")

async def check_streaming_health():
    """Background task to monitor sync streaming threads."""
    max_threads = get_max_sync_streaming_threads()
    active = ACTIVE_SYNC_STREAMING_THREADS.load(Ordering::Relaxed)

    if active >= max_threads * 0.9:  # 90% of limit
        logger.warning(f"Sync streaming thread limit approaching: {active}/{max_threads}")
        # Consider rejecting new connections or alerting ops

    if active >= max_threads:
        logger.error(f"Sync streaming thread limit reached: {active}/{max_threads}")

# Run periodically
async def monitor_loop():
    while True:
        await check_streaming_health()
        await asyncio.sleep(10)  # Check every 10 seconds
```

---

## File Serving Security

Django-Bolt provides secure file serving with path traversal protection.

### FileResponse Usage

```python
from django_bolt.responses import FileResponse

@api.get("/download/{filename}")
async def download_file(filename: str):
    # Path traversal protection is automatic
    file_path = f"/var/app/files/{filename}"
    return FileResponse(
        file_path,
        filename="download.pdf",  # Override filename
        media_type="application/pdf"
    )
```

### Security Features

**✅ Path Canonicalization**

```python
# Paths are resolved and validated
FileResponse("/path/to/file.txt")
# - Resolves symlinks
# - Resolves .. and .
# - Validates file exists and is a regular file
```

**✅ Directory Whitelist**

```python
# settings.py
BOLT_ALLOWED_FILE_PATHS = [
    "/var/app/uploads",
    "/var/app/public",
]

# GOOD: Within allowed directory
FileResponse("/var/app/uploads/file.txt")  # ✅

# BAD: Outside allowed directories
FileResponse("/etc/passwd")  # 🚫 PermissionError (403)
FileResponse("/var/app/uploads/../../../etc/passwd")  # 🚫 Blocked
```

**✅ Automatic Error Handling**

```python
# FileNotFoundError -> 404
FileResponse("/nonexistent.txt")  # Returns 404

# PermissionError -> 403
FileResponse("/etc/shadow")  # Returns 403

# Path traversal -> 403
FileResponse("../../etc/passwd")  # Returns 403
```

---

## Input Validation

### Header Size Limits

```python
# settings.py
BOLT_MAX_HEADER_SIZE = 8192  # 8KB per header value (default)

# Enforced limits:
# - Max 100 headers per request (hardcoded in Rust)
# - Each header value limited to BOLT_MAX_HEADER_SIZE
# - Requests exceeding limits return 400 Bad Request
```

**Performance Note**: `BOLT_MAX_HEADER_SIZE` is read ONCE at server startup and cached in the Rust layer. Changes require a server restart to take effect.

### Upload Size Limits

```python
# settings.py
BOLT_MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB (default)

# Applied to:
# - Multipart form data
# - File uploads
# - Request body size
```

### Multipart Parsing Security

Django-Bolt uses the battle-tested `multipart` library with security features:

```python
# Automatic features:
# - Boundary validation (max 200 bytes)
# - Size limits per part
# - Maximum number of parts (100)
# - Memory limits
# - No disk spooling (memory-only for security)
```

---

## Performance & Security Trade-offs

Django-Bolt optimizes security checks to run at maximum performance by reading configuration ONCE at server startup and caching it in the Rust layer.

### Settings Read at Startup

The following settings are read from Django settings.py when the server starts and cached in Rust:

```python
# These settings are READ ONCE at startup (NOT per-request)
BOLT_MAX_HEADER_SIZE = 8192         # Header validation limit
BOLT_CORS_ALLOWED_ORIGINS = [...]   # CORS origin whitelist
BOLT_MAX_UPLOAD_SIZE = 10485760     # Upload size limit
BOLT_ALLOWED_FILE_PATHS = [...]     # File serving whitelist
```

**Important**: Changes to these settings require a server restart to take effect.

### Why This Matters

**Before (Slow - Regression)**:

```python
# ❌ BAD: Reading Django settings on EVERY request
def handle_request():
    from django.conf import settings
    max_size = settings.BOLT_MAX_HEADER_SIZE  # Python import + GIL acquisition
    # ... validate headers ...
```

**After (Fast - Current)**:

```python
# ✅ GOOD: Read once at startup, cached in Rust
fn handle_request(state: &AppState) {
    let max_size = state.max_header_size;  // Direct memory access, no Python calls
    // ... validate headers ...
}
```

**Performance Impact**:

- Reading Django settings per-request: ~30-40% performance loss (33k → 44k RPS)
- Caching at startup: Zero per-request overhead

### Authentication Algorithm Performance

JWT authentication uses only the FIRST algorithm specified for maximum performance:

```python
# OPTIMAL: Single algorithm validation
jwt_auth = JWTAuthentication(algorithms=["HS256"])
# Validates using HS256 only - zero overhead from algorithm selection

# SUBOPTIMAL: Multiple algorithms listed (only first is used!)
jwt_auth = JWTAuthentication(algorithms=["HS256", "HS512", "RS256"])
# Still only validates with HS256 (first in list)
# Other algorithms are IGNORED - no fallback on failure
```

**Current Behavior**:

- Only the first algorithm in the list is used for validation
- If validation fails with the first algorithm, the request is rejected immediately
- No fallback to other algorithms (this prevents algorithm confusion attacks)
- If you need to support multiple algorithms, create separate authentication backends

**Why This Matters**:

- **Old approach** (trying multiple algorithms on failure): Vulnerable to algorithm downgrade attacks, adds overhead
- **Current approach** (single algorithm only): Secure, fast, predictable behavior

### Best Practices for Performance

1. **Specify ONE algorithm for JWT**:

   ```python
   JWTAuthentication(algorithms=["HS256"])  # Not ["HS256", "HS512"]
   ```

2. **Configure settings before server start**:

   ```python
   # settings.py - loaded ONCE at startup
   BOLT_MAX_HEADER_SIZE = 8192
   BOLT_CORS_ALLOWED_ORIGINS = ["https://example.com"]
   ```

3. **Restart server after settings changes**:
   ```bash
   # After modifying Django settings
   python manage.py runbolt --reload  # Or restart your process
   ```

---

## Security Best Practices

### 1. Use Environment Variables for Secrets

```python
# settings.py
import os

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# In your API
jwt_auth = JWTAuthentication()  # Uses SECRET_KEY from settings
```

### 2. Enable HTTPS in Production

```python
# settings.py
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 3. Configure CORS Properly

```python
# ❌ DON'T: Allow all origins in production
BOLT_CORS_ALLOWED_ORIGINS = ["*"]

# ✅ DO: Specify exact origins
BOLT_CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]
```

### 4. Use Strong JWT Algorithms

```python
# ✅ GOOD: Strong algorithm (single for best performance)
JWTAuthentication(algorithms=["HS256"])    # HMAC-SHA256 (symmetric)
JWTAuthentication(algorithms=["RS256"])    # RSA signatures (asymmetric)
JWTAuthentication(algorithms=["ES256"])    # ECDSA signatures (asymmetric)

# ⚠️ AVOID: Multiple algorithms (only first is used, no fallback!)
JWTAuthentication(algorithms=["HS256", "HS512"])  # Only HS256 is validated!
# If token uses HS512, validation will FAIL

# ⚠️ AVOID: Weak algorithms
# None algorithm is not supported (security)
```

**Algorithm Selection**: Only the first algorithm in the list is used. If your tokens use different algorithms, you must create separate authentication backends.

### 5. Implement Rate Limiting

```python
# Protect expensive endpoints
@api.post("/search")
@rate_limit(rps=10, burst=20)
async def search(query: str): ...

# Protect auth endpoints
@api.post("/login")
@rate_limit(rps=5, burst=10, key="ip")
async def login(credentials: LoginCredentials): ...
```

### 6. Validate File Paths

```python
# settings.py
BOLT_ALLOWED_FILE_PATHS = [
    "/var/app/uploads",      # User uploads
    "/var/app/public",       # Public assets
]

# Never serve from:
# - System directories (/etc, /var, /usr)
# - Application code directories
# - Database files
```

### 7. Use Token Revocation for Critical Apps

```python
# For apps requiring logout or token invalidation
jwt_auth = JWTAuthentication(
    revocation_store=DjangoCacheRevocation(),
    # require_jti=True  # Auto-enabled when revocation_store is set
)

# Implement logout endpoint
@api.post("/logout", auth=[jwt_auth], guards=[IsAuthenticated()])
async def logout(request):
    auth = request.get("auth", {})
    claims = auth.get("auth_claims", {})
    jti = claims.get("jti")

    if jti:
        await jwt_auth.revocation_store.revoke_token(jti)
        return {"message": "Logged out successfully"}
    else:
        return {"message": "Token has no JTI claim"}, 400
```

### 8. Monitor and Log Security Events

```python
from django_bolt.logging import LoggingMiddleware

api = BoltAPI(
    logging_middleware=LoggingMiddleware(
        logger_name="security",
        log_requests=True,
        log_responses=True,
        log_errors=True
    )
)

# Log authentication failures
@api.post("/login")
async def login(credentials: LoginCredentials):
    # ... authentication logic ...
    if not authenticated:
        logger.warning(f"Failed login attempt for {credentials.username}")
```

### 9. Don't Expose Sensitive Information

```python
# ❌ DON'T: Expose internal errors in production
DEBUG = True  # In production

# ✅ DO: Use proper error handling
DEBUG = False  # In production

from django_bolt.exceptions import HTTPException

@api.get("/user/{user_id}")
async def get_user(user_id: int):
    try:
        user = await User.objects.aget(id=user_id)
        return user
    except User.DoesNotExist:
        # Return generic error, don't expose "User not found" details
        raise HTTPException(404, "Resource not found")
```

### 10. Use Dependency Injection for Auth

```python
from django_bolt.dependencies import Depends
from django_bolt.exceptions import Unauthorized

async def get_current_user(request):
    """Dependency that extracts and validates the current user."""
    auth = request.get("auth", {})
    user_id = auth.get("user_id")

    if not user_id:
        raise Unauthorized("Authentication required")

    # For API keys, user_id is "apikey:{key}" format
    if user_id.startswith("apikey:"):
        raise Unauthorized("API key authentication not supported for this endpoint")

    try:
        return await User.objects.aget(id=user_id)
    except User.DoesNotExist:
        raise Unauthorized("User not found")

@api.get("/profile")
async def profile(user = Depends(get_current_user)):
    return {
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff
    }
```

This pattern centralizes authentication logic and makes handlers cleaner.

---

## Security Settings Reference

### Core Security Settings

```python
# Django-Bolt Security Settings
# Add to your Django settings.py

# CORS Configuration
BOLT_CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://app.example.com",
]

# File Serving Security
BOLT_ALLOWED_FILE_PATHS = [
    "/var/app/uploads",
    "/var/app/public",
]

# Request Limits
BOLT_MAX_HEADER_SIZE = 8192  # 8KB per header value
BOLT_MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# Note: The following are enforced at the Rust layer:
# - Max 100 headers per request
# - Max 100,000 rate limiters
# - Max 256 bytes per rate limit key
# - Max 100 multipart parts per request
```

### Django Security Settings

Also configure standard Django security settings:

```python
# Django Security Settings (recommended)
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = False
ALLOWED_HOSTS = ["yourdomain.com"]

# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

## Security Audit Checklist

Before deploying to production:

- [ ] `DEBUG = False` in production
- [ ] Strong `SECRET_KEY` from environment variable
- [ ] HTTPS enabled and enforced
- [ ] CORS properly configured with specific origins
- [ ] File serving restricted to whitelisted directories
- [ ] Rate limiting enabled on sensitive endpoints
- [ ] Authentication required on protected routes
- [ ] Token revocation implemented for critical apps
- [ ] Upload size limits configured appropriately
- [ ] Security headers enabled
- [ ] Error messages don't expose sensitive information
- [ ] Logging configured for security events
- [ ] Dependencies up to date
- [ ] If using SSE/Streaming:
  - [ ] `BOLT_MAX_SYNC_STREAMING_THREADS` configured (thread exhaustion protection, default: 1000)
  - [ ] Authentication enabled on streaming endpoints
  - [ ] Generator cleanup errors are monitored (log stderr for `[SSE WARNING]`)
  - [ ] Rate limiting applied to streaming endpoints
  - [ ] Thread utilization monitoring/alerts configured
  - [ ] Reviewed SECURITY.md - Server-Sent Events section

---

## Reporting Security Issues

If you discover a security vulnerability in Django-Bolt, please report it responsibly:

1. **Do not** open a public GitHub issue
2. Email security details to the maintainers
3. Include steps to reproduce, impact assessment, and potential fixes
4. Allow time for a patch before public disclosure

---

## Additional Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [CORS Specification](https://fetch.spec.whatwg.org/#http-cors-protocol)

---

**Last Updated:** October 2025
**Django-Bolt Version:** 0.1.0

# Django-Bolt Authentication System

High-performance authentication and authorization system where **validation happens in Rust without the GIL**, achieving 60k+ RPS with JWT authentication.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ Python Layer (Configuration)                                    │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ JWTAuth      │  │ APIKeyAuth   │  │ Guards       │         │
│  │              │  │              │  │              │         │
│  │ .to_metadata()│  │ .to_metadata()│  │ .to_metadata()│         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                  │
│                            │                                     │
│                   Compile to metadata                           │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Rust Layer (Validation - NO GIL)                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Route Registration                                       │  │
│  │ • Parse metadata → typed Rust enums                     │  │
│  │ • Store auth backends & guards per route               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Request Processing (HOT PATH - NO GIL)                  │  │
│  │                                                          │  │
│  │  1. Extract token from header                           │  │
│  │  2. Validate JWT (jsonwebtoken crate)                   │  │
│  │  3. Check guards/permissions                            │  │
│  │  4. Populate request.context with auth data             │  │
│  │                                                          │  │
│  │  ⚡ All happens without touching Python/GIL              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Python Handler (WITH AuthContext)                              │
│                                                                  │
│  async def my_handler(request):                                 │
│      user_id = request["context"]["user_id"]                    │
│      is_admin = request["context"]["is_admin"]                  │
│      permissions = request["context"]["permissions"]            │
│      claims = request["context"]["auth_claims"]                 │
│      ...                                                         │
└─────────────────────────────────────────────────────────────────┘
```

## Module Structure

```
django_bolt/auth/
├── __init__.py          # Public API exports
├── README.md            # This file
├── backends.py          # Authentication backends (JWT, API key, Session)
├── guards.py            # Permission guards (IsAuthenticated, IsAdmin, etc.)
├── middleware.py        # Middleware decorators (cors, rate_limit, etc.)
└── token.py             # JWT Token dataclass with encode/decode
```

## Quick Start

### 1. Define Authentication Backend

```python
from django_bolt import BoltAPI, JWTAuthentication, IsAuthenticated, Token
from datetime import timedelta

api = BoltAPI()

# Create JWT token for a user
def create_token_for_user(user):
    return Token.create(
        sub=str(user.id),
        expires_delta=timedelta(hours=1),
        is_staff=user.is_staff,
        is_admin=user.is_superuser,
        permissions=list(user.get_all_permissions()),
        email=user.email,
    ).encode(secret=settings.SECRET_KEY)

# Protected endpoint
@api.get(
    "/profile",
    auth=[JWTAuthentication()],
    guards=[IsAuthenticated()]
)
async def get_profile(request):
    user_id = request["context"]["user_id"]
    is_admin = request["context"]["is_admin"]

    return {
        "user_id": user_id,
        "is_admin": is_admin,
        "permissions": request["context"].get("permissions", [])
    }
```

### 2. Global Authentication (Settings)

```python
# settings.py

BOLT_AUTHENTICATION_CLASSES = [
    JWTAuthentication(
        secret=SECRET_KEY,
        algorithms=["HS256"],
        header="authorization",
        audience="my-api",
    )
]

BOLT_DEFAULT_PERMISSION_CLASSES = [
    IsAuthenticated()
]
```

Now all routes are protected by default unless you override with `guards=[AllowAny()]`.

### 3. Per-Route Authentication Override

```python
from django_bolt import APIKeyAuthentication, HasPermission

# Admin-only endpoint with API key auth
@api.delete(
    "/users/{user_id}",
    auth=[APIKeyAuthentication(api_keys={"admin-key-123"})],
    guards=[HasPermission("users.delete")]
)
async def delete_user(user_id: int):
    # Only callable with valid API key and users.delete permission
    return {"deleted": user_id}
```

## Authentication Backends

### JWTAuthentication

High-performance JWT validation in Rust using the `jsonwebtoken` crate.

```python
from django_bolt import JWTAuthentication

auth = JWTAuthentication(
    secret="your-secret-key",              # Default: Django SECRET_KEY
    algorithms=["HS256"],                  # Supported: HS256/384/512, RS256/384/512, ES256/384
    header="authorization",                # Header to extract token from
    audience="my-api",                     # Optional: validate aud claim
    issuer="auth-service",                 # Optional: validate iss claim
)
```

**Token Format**: `Authorization: Bearer <jwt-token>`

**Performance**: ~60k RPS with JWT validation

### APIKeyAuthentication

Simple API key validation with optional per-key permissions.

```python
from django_bolt import APIKeyAuthentication

auth = APIKeyAuthentication(
    api_keys={"key1", "key2", "admin-key"},
    header="x-api-key",
    key_permissions={
        "admin-key": ["users.create", "users.delete", "posts.create"],
        "key1": ["users.view"],
        "key2": ["posts.view", "posts.create"],
    }
)
```

**Header Format**: `X-API-Key: your-api-key`

### SessionAuthentication

Django session-based authentication (falls back to Python execution).

```python
from django_bolt import SessionAuthentication

auth = SessionAuthentication()
```

**Note**: This has higher overhead than JWT/API key as it requires Python execution per request.

## Permission Guards

Guards are checked **after authentication** in Rust, providing early 403 responses without GIL overhead.

### AllowAny

Allow unauthenticated requests (bypasses global defaults).

```python
from django_bolt import AllowAny

@api.get("/public", guards=[AllowAny()])
async def public_endpoint():
    return {"message": "Anyone can access this"}
```

### IsAuthenticated

Require valid authentication (any backend).

```python
from django_bolt import IsAuthenticated

@api.get("/protected", guards=[IsAuthenticated()])
async def protected():
    return {"message": "Must be authenticated"}
```

### IsAdminUser / IsStaff

Require admin or staff status (from JWT claims `is_superuser`, `is_admin`, or `is_staff`).

```python
from django_bolt import IsAdminUser, IsStaff

@api.get("/admin", guards=[IsAdminUser()])
async def admin_only():
    return {"message": "Admin access"}

@api.get("/staff", guards=[IsStaff()])
async def staff_only():
    return {"message": "Staff access"}
```

### HasPermission / HasAnyPermission / HasAllPermissions

Fine-grained permission checking.

```python
from django_bolt import HasPermission, HasAnyPermission, HasAllPermissions

# Require specific permission
@api.delete("/users/{id}", guards=[HasPermission("users.delete")])
async def delete_user(id: int):
    pass

# Require at least one permission
@api.put("/users/{id}", guards=[HasAnyPermission("users.edit", "users.admin")])
async def edit_user(id: int):
    pass

# Require all permissions
@api.post("/admin/reset", guards=[HasAllPermissions("admin.full", "admin.reset")])
async def reset_system():
    pass
```

## JWT Token Class

The `Token` dataclass provides a Pythonic interface for JWT tokens with validation.

### Creating Tokens

```python
from django_bolt import Token
from datetime import datetime, timedelta, timezone

# Option 1: Direct instantiation
token = Token(
    sub="user123",
    exp=datetime.now(timezone.utc) + timedelta(hours=1),
    is_staff=True,
    permissions=["read", "write"],
)

# Option 2: Factory method (recommended)
token = Token.create(
    sub="user123",
    expires_delta=timedelta(hours=1),
    is_staff=True,
    is_admin=False,
    permissions=["users.view", "posts.create"],
    # Extra custom claims
    tenant_id="acme-corp",
    role="manager",
)

# Encode to JWT string
jwt_string = token.encode(secret="my-secret", algorithm="HS256")
```

### Decoding Tokens

```python
# Decode and validate
token = Token.decode(
    jwt_string,
    secret="my-secret",
    algorithm="HS256",
    audience="my-api",        # Optional
    issuer="auth-service",    # Optional
    verify_exp=True,          # Verify expiration
    verify_nbf=True,          # Verify not-before
)

print(token.sub)          # "user123"
print(token.is_staff)     # True
print(token.permissions)  # ["users.view", "posts.create"]
print(token.extras)       # {"tenant_id": "acme-corp", "role": "manager"}
```

### Integration with Django Users

```python
from django_bolt.jwt_utils import create_jwt_for_user

# Create token from Django User instance
user = await User.objects.aget(username="john")
token = create_jwt_for_user(
    user,
    expires_in=3600,  # 1 hour
    extra_claims={
        "permissions": ["users.view", "posts.create"],
        "tenant": "acme",
    }
)

# Use in login endpoint
@api.post("/login")
async def login(username: str, password: str):
    # Authenticate user...
    token = create_jwt_for_user(user)
    return {"access_token": token, "token_type": "bearer"}
```

## Request Context

After authentication, the request context is populated with auth data:

```python
@api.get("/me")
async def get_current_user_info(request):
    ctx = request["context"]

    # Always available after successful auth
    user_id = ctx["user_id"]              # str: User identifier
    is_staff = ctx["is_staff"]            # bool: Staff status
    is_admin = ctx["is_admin"]            # bool: Admin status
    backend = ctx["auth_backend"]         # str: "jwt", "api_key", etc.

    # Available if permissions configured
    permissions = ctx.get("permissions", [])  # list[str]: Permission strings

    # Available for JWT auth
    if "auth_claims" in ctx:
        claims = ctx["auth_claims"]
        exp = claims["exp"]               # Expiration timestamp
        iat = claims["iat"]               # Issued at timestamp
        # Plus any custom claims

    return {"user_id": user_id, "is_admin": is_admin}
```

### Helper Functions

```python
from django_bolt.jwt_utils import (
    get_current_user,           # Fetch Django User from DB
    extract_user_id_from_context,
    get_auth_context,
)
from django_bolt.params import Depends

# Dependency injection to get Django User
@api.get("/profile")
async def my_profile(user=Depends(get_current_user)):
    if not user:
        return {"error": "Not authenticated"}

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }

# Extract just the user ID
@api.get("/data")
async def get_data(request):
    user_id = extract_user_id_from_context(request)
    # Use user_id...
```

## Performance Characteristics

| Operation | Performance | Notes |
|-----------|-------------|-------|
| JWT Validation | ~60k+ RPS | Entirely in Rust, no GIL |
| API Key Check | ~65k+ RPS | Simple HashSet lookup |
| Guard Check | ~65k+ RPS | In-memory permission check |
| Session Auth | ~10-15k RPS | Falls back to Python/Django |

**Key Insight**: Authentication/authorization happens in the hot path **before** calling Python handlers, so most invalid requests are rejected at ~60k RPS without ever touching the GIL.

## Rust Implementation Details

### Key Files

- **`src/middleware/auth.rs`**: JWT/API key validation, Claims struct, AuthContext
- **`src/metadata.rs`**: Parse Python metadata → Rust types at registration
- **`src/permissions.rs`**: Guard enum and validation logic
- **`src/lib.rs`**: Request processing pipeline

### Performance Optimizations

1. **Zero-copy validation**: JWT validation uses `jsonwebtoken` crate directly on request bytes
2. **No GIL during auth**: Entire auth pipeline runs without acquiring GIL
3. **Early rejection**: Invalid tokens/permissions rejected before Python handler call
4. **Metadata compilation**: Auth config parsed once at registration, not per-request
5. **Efficient data structures**: DashMap for rate limiting, HashSet for permissions

## Testing

```bash
# Run auth tests
uv run pytest python/django_bolt/tests/test_guards_auth.py -v
uv run pytest python/django_bolt/tests/test_jwt_token.py -v

# All tests
uv run pytest python/django_bolt/tests/ -v
```

## Migration from Old Code

If you had direct imports from `django_bolt.auth` or `django_bolt.permissions`, they still work:

```python
# Old imports (still work via backward compat shim)
from django_bolt.auth import JWTAuthentication
from django_bolt.permissions import IsAuthenticated

# New organized imports (recommended)
from django_bolt.auth import JWTAuthentication, IsAuthenticated
# or
from django_bolt import JWTAuthentication, IsAuthenticated
```

## Examples

See `/python/examples/testproject/testproject/api.py` for real-world usage examples.

## Benchmarks

```bash
# Run auth-specific benchmarks
make bench-auth  # TODO: Add auth benchmarks to Makefile
```

---
icon: lucide/key-round
---

# Authentication

Django-Bolt provides built-in authentication backends that run in Rust for high performance. This guide covers how to set up and use authentication in your API.

## JWT authentication

JWT (JSON Web Token) is the most common authentication method for APIs. Django-Bolt validates JWT tokens in Rust without the Python GIL overhead.

### Basic usage

```python
from django_bolt import BoltAPI
from django_bolt.auth import JWTAuthentication, IsAuthenticated

api = BoltAPI()

@api.get("/profile", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def profile(request):
    return {"user_id": request.user.id}
```

This endpoint:

1. Expects a JWT token in the `Authorization` header: `Bearer <token>`
2. Validates the token signature and expiration
3. Rejects the request with 401 if the token is invalid
4. Populates `request.context` with token claims

### Creating tokens for users

Use `create_jwt_for_user` to generate tokens for Django users:

```python
from django.contrib.auth import aauthenticate
from django_bolt.auth import create_jwt_for_user
from django_bolt.exceptions import Unauthorized
import msgspec

class LoginRequest(msgspec.Struct):
    username: str
    password: str

@api.post("/auth/token")
async def login(credentials: LoginRequest):
    user = await aauthenticate(
        username=credentials.username,
        password=credentials.password
    )

    if user is None:
        raise Unauthorized(detail="Invalid credentials")

    token = create_jwt_for_user(user, expires_in=3600)  # 1 hour

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 3600
    }
```

The generated token includes:

- `sub` - User's primary key
- `is_staff` - Staff status
- `is_superuser` - Superuser status
- `username` - Username
- `exp` - Expiration timestamp

!!! note "Permissions not included by default"

    Permissions are NOT automatically included in the token. To use `HasPermission` guards, pass permissions via `extra_claims`:

    ```python
    token = create_jwt_for_user(
        user,
        extra_claims={"permissions": list(user.get_all_permissions())}
    )
    ```

### Accessing the authenticated user

Django-Bolt provides lazy user loading via `request.user`:

```python
@api.get("/me", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_me(request):
    user = request.user  # Lazily loads from database

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }
```

The user is only loaded from the database when you access `request.user`. If you don't need the full user object, use `request.context` which is available without a database query.

### Using dependency injection

Alternatively, use the `get_current_user` dependency:

```python
from django_bolt import Depends
from django_bolt.auth import get_current_user

@api.get("/me", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_me(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username
    }
```

### JWT configuration options

Customize JWT validation:

```python
JWTAuthentication(
    secret="your-secret-key",    # Default: Django's SECRET_KEY
    algorithms=["HS256"],        # Allowed algorithms
    header="authorization",      # Header name
    audience="your-app",         # Required audience claim
    issuer="your-issuer",        # Required issuer claim
)
```

Supported algorithms:

- `HS256`, `HS384`, `HS512` - HMAC with SHA-2
- `RS256`, `RS384`, `RS512` - RSA with SHA-2
- `ES256`, `ES384`, `ES512` - ECDSA with SHA-2

## API key authentication

!!! info "In Development"

    API key permissions (`key_permissions` parameter) are in development. Basic API key validation works, but per-key permissions are not yet finalized.

For service-to-service communication, use API key authentication:

```python
from django_bolt.auth import APIKeyAuthentication, IsAuthenticated

api_keys = {"sk-prod-123abc", "sk-prod-456def"}

@api.get(
    "/internal",
    auth=[APIKeyAuthentication(api_keys=api_keys)],
    guards=[IsAuthenticated()]
)
async def internal_endpoint(request):
    return {"status": "authorized"}
```

API keys are sent in the `X-API-Key` header by default.

### API key permissions (In Development)

Assign different permissions to different keys:

```python
key_permissions = {
    "sk-admin-key": {"admin.read", "admin.write"},
    "sk-reader-key": {"admin.read"},
}

APIKeyAuthentication(
    api_keys=set(key_permissions.keys()),
    key_permissions=key_permissions
)
```

### Custom header

Use a different header for API keys:

```python
APIKeyAuthentication(
    api_keys=api_keys,
    header="Authorization"  # Or any custom header
)
```

## Combining authentication methods

Accept multiple authentication methods:

```python
@api.get(
    "/data",
    auth=[JWTAuthentication(), APIKeyAuthentication(api_keys=api_keys)],
    guards=[IsAuthenticated()]
)
async def get_data(request):
    backend = request.context.get("auth_backend")
    return {"authenticated_via": backend}
```

Django-Bolt tries each backend in order until one succeeds.

## Authentication context

After successful authentication, `request.context` contains:

```python
@api.get("/context", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def show_context(request):
    context = request.context

    return {
        "user_id": context.get("user_id"),
        "is_staff": context.get("is_staff"),
        "is_superuser": context.get("is_superuser"),
        "auth_backend": context.get("auth_backend"),  # "jwt" or "api_key"
        "permissions": context.get("permissions", []),
        "auth_claims": context.get("auth_claims", {}),  # JWT only
    }
```

## Token revocation

For logout functionality, Django-Bolt supports token revocation stores.

### In-memory revocation (development)

```python
from django_bolt.auth import JWTAuthentication, InMemoryRevocation

store = InMemoryRevocation()

jwt_auth = JWTAuthentication(revocation_store=store)

@api.post("/logout", auth=[jwt_auth], guards=[IsAuthenticated()])
async def logout(request):
    token_jti = request.context.get("auth_claims", {}).get("jti")
    if token_jti:
        store.revoke(token_jti)
    return {"status": "logged out"}
```

### Django cache revocation (production)

```python
from django_bolt.auth import DjangoCacheRevocation

store = DjangoCacheRevocation(
    cache_alias="default",
    key_prefix="revoked_tokens:"
)
```

### Django ORM revocation

```python
from django_bolt.auth import DjangoORMRevocation

store = DjangoORMRevocation(model_path="myapp.models.RevokedToken")
```

Requires a model with a `jti` field.

## Endpoints without authentication

Use `AllowAny` to explicitly allow unauthenticated access:

```python
from django_bolt.auth import AllowAny

@api.get("/public", guards=[AllowAny()])
async def public_endpoint():
    return {"message": "Anyone can access this"}
```

## Global authentication

Configure default authentication and guards for all endpoints in `settings.py`:

```python
# settings.py
from django_bolt.auth import JWTAuthentication, IsAuthenticated

# Default authentication backends for all endpoints
BOLT_AUTHENTICATION_CLASSES = [
    JWTAuthentication(),
]

# Default permission guards for all endpoints
BOLT_DEFAULT_PERMISSION_CLASSES = [
    IsAuthenticated(),
]
```

!!! warning "Security Notice"

    If `BOLT_DEFAULT_PERMISSION_CLASSES` is not set, it defaults to `[AllowAny()]` which means **all endpoints are publicly accessible**. Always configure both settings in production.

When configured, all endpoints require authentication by default:

```python
# Uses global auth + guards - requires valid JWT
@api.get("/profile")
async def profile(request):
    return {"user_id": request.user.id}

# Override guards for public endpoint
@api.get("/public", guards=[AllowAny()])
async def public():
    return {"message": "Anyone can access"}

# Override auth for specific endpoint
@api.get("/api-only", auth=[APIKeyAuthentication(api_keys={"secret"})])
async def api_only(request):
    return {"status": "ok"}
```

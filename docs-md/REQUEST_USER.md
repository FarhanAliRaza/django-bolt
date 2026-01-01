# request.user - Lazy-Loaded User Objects

Django-Bolt provides lazy-loaded user objects accessible via `request.user`. Users are loaded from the database only when `request.user` is first accessed, using Django's `SimpleLazyObject` pattern for optimal performance.

## Overview

Instead of manually extracting `user_id` from auth context and querying the database:

```python
# Old way - manual user lookup
@api.get("/me", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_user(request):
    auth = request.get("auth", {})
    user_id = auth.get("user_id")
    user = await User.objects.aget(pk=user_id)  # Manual query
    return {"username": user.username}
```

You can now use `request.user` for cleaner code - **automatically loaded on first access**:

```python
# New way - user lazy-loaded by Django-Bolt
@api.get("/me", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_me(request):
    user = request.user  # Loaded on first access
    if user:  # Safe to access directly
        return {"username": user.username}
    return {"error": "User not found"}
```

This also works seamlessly in **sync handlers**:

```python
@api.get("/profile", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
def get_profile(request):
    # Works in sync handlers - user loaded on access
    user = request.user
    if user:
        return {"username": user.username}
    return {"error": "User not found"}
```

**Lazy loading**: User is only loaded from the database when `request.user` is first accessed. If your handler never accesses `request.user`, no database query is made.

## Features

- **Lazy-Loaded**: User is loaded from database only when `request.user` is first accessed
- **Zero Overhead**: Endpoints that don't access `request.user` incur no DB query
- **No Await Required**: Works in both sync and async handlers with the same syntax
- **Custom User Models**: Uses Django's `get_user_model()` for custom user support
- **Extensible**: Override `get_user()` in auth backends for custom user resolution
- **Auth-Backend Aware**: Automatically uses the correct backend to load user

## Basic Usage

### With JWT Authentication

```python
from django_bolt import BoltAPI
from django_bolt.auth import JWTAuthentication, IsAuthenticated

api = BoltAPI()

@api.get("/profile", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_profile(request):
    user = request.user  # Loaded on first access
    if not user:
        return {"error": "User not found"}
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
    }
```

### With Session Authentication

```python
from django_bolt.auth import SessionAuthentication

@api.get("/dashboard", auth=[SessionAuthentication()], guards=[IsAuthenticated()])
async def dashboard(request):
    user = request.user  # Loaded on first access
    if user:
        return {"welcome": f"Welcome back, {user.first_name}!"}
    return {"error": "Not authenticated"}
```

### Without Authentication (Public Endpoints)

For public endpoints without authentication, `request.user` is `None` (no user loading):

```python
@api.get("/public")
async def public_endpoint(request):
    user = request.user  # None - no auth configured
    if user:
        return {"authenticated": True, "user_id": user.id}
    return {"authenticated": False}
```

### JWT-Only Verification (No User Access)

For endpoints that only need to verify the JWT is valid but don't need the user object:

```python
@api.get("/verify-token", auth=[JWTAuthentication()])
async def verify_token(request):
    # Token validated in Rust, user NOT loaded (we never access request.user)
    context = request.get("auth", {})
    return {
        "is_valid": True,
        "user_id": context.get("user_id"),
        "backend": context.get("auth_backend"),
    }
```

## User Loading Behavior

`request.user` uses Django's `SimpleLazyObject` - the user is loaded once on first access and cached for the entire request lifecycle:

```python
@api.get("/user-stats", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_user_stats(request):
    # User loaded on first access
    user = request.user
    user_count = await User.objects.filter(is_staff=user.is_staff).acount()

    # Multiple accesses return the same cached instance (no additional queries)
    user_profile = request.user

    assert user is user_profile  # Same instance
    return {"user_id": user.id, "staff_users": user_count}
```

## Performance Considerations

User loading is lazy - the database query only happens when `request.user` is accessed:

```python
# Route 1: JWT-only verification - no user access
@api.get("/verify-token", auth=[JWTAuthentication()])
async def verify_token(request):
    # JWT validated in Rust, user NOT loaded (never accessed)
    return {"verified": True}  # ~100k RPS (no DB query)

# Route 2: User access required
@api.get("/profile", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_profile(request):
    user = request.user  # User loaded here (first access)
    return {"username": user.username}  # ~15k RPS (includes DB query)
```

## Extensibility: Custom User Resolution

Each authentication backend supports custom user resolution via the `get_user()` method. Override it to implement custom logic:

### API Key to User Mapping

```python
from django_bolt.auth import APIKeyAuthentication
from myapp.models import APIKey

class CustomAPIKeyAuth(APIKeyAuthentication):
    """API key authentication with user mapping"""

    async def get_user(self, user_id: str, auth_context: dict):
        """Map API key to user"""
        try:
            # user_id for API keys is formatted as "apikey:{key}"
            api_key_str = user_id.replace("apikey:", "")
            api_key = await APIKey.objects.select_related("user").aget(key=api_key_str)
            return api_key.user
        except APIKey.DoesNotExist:
            return None

# Usage
@api.get("/api-user", auth=[CustomAPIKeyAuth(api_keys={"secret123"})], guards=[IsAuthenticated()])
async def get_api_user(request):
    user = request.user  # Returns the actual user, not None!
    return {"user_id": user.id, "username": user.username}
```

### OAuth/Social Auth Integration

```python
from django_bolt.auth import BaseAuthentication

class OAuthAuthentication(BaseAuthentication):
    """OAuth with user mapping"""

    def __init__(self, provider: str):
        self.provider = provider

    @property
    def scheme_name(self) -> str:
        return f"oauth_{self.provider}"

    def to_metadata(self):
        return {"type": "oauth", "provider": self.provider}

    async def get_user(self, user_id: str, auth_context: dict):
        """Map OAuth ID to user"""
        from myapp.models import OAuthConnection
        try:
            connection = await OAuthConnection.objects.select_related("user").aget(
                provider=self.provider,
                provider_user_id=user_id
            )
            return connection.user
        except OAuthConnection.DoesNotExist:
            return None

# Usage
@api.get("/oauth-profile", auth=[OAuthAuthentication("github")], guards=[IsAuthenticated()])
async def get_oauth_profile(request):
    user = request.user  # Returns user linked to GitHub OAuth
    return {"username": user.username, "oauth_provider": "github"}
```

### Service Accounts

```python
from myapp.models import ServiceAccount

class ServiceAccountAuth(BaseAuthentication):
    """Service account authentication"""

    @property
    def scheme_name(self) -> str:
        return "service_account"

    def to_metadata(self):
        return {"type": "service_account"}

    async def get_user(self, user_id: str, auth_context: dict):
        """Map service account ID to service account object"""
        try:
            return await ServiceAccount.objects.aget(service_id=user_id)
        except ServiceAccount.DoesNotExist:
            return None
```

## Auth Backend Defaults

If you don't override `get_user()`, Django-Bolt provides sensible defaults:

### JWT / Session Authentication

Default implementation loads user by primary key:

```python
async def get_user(self, user_id: str, auth_context: dict):
    try:
        return await User.objects.aget(pk=user_id)
    except User.DoesNotExist:
        return None
```

The `user_id` from the JWT `sub` claim or session should be the user's primary key.

### API Key Authentication

Default implementation returns `None` (no user mapping):

```python
async def get_user(self, user_id: str, auth_context: dict):
    return None  # API keys don't have users by default
```

To map API keys to users, subclass `APIKeyAuthentication` and override `get_user()`.

## Auth Context Fields

The `auth_context` dict passed to `get_user()` contains:

```python
{
    "user_id": str,              # User identifier from auth
    "is_staff": bool,            # Staff status (from token/backend)
    "is_admin": bool,            # Admin/superuser status
    "auth_backend": str,         # Backend name: "jwt", "api_key", "session", etc.
    "permissions": set[str],     # Permission strings
    "auth_claims": dict,         # JWT claims (if JWT backend)
}
```

## Error Handling

If a user cannot be loaded (not found, database error), `request.user` is `None`. Check for this condition:

```python
@api.get("/user-data", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_user_data(request):
    user = request.user
    if not user:
        # User authenticated but no longer exists in database
        raise HTTPException(status_code=410, detail="User no longer exists")
    return {"id": user.id, "username": user.username}
```

For database errors during user loading, check stderr logs - errors are printed but don't prevent the request:

```python
@api.get("/user-info", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_user_info(request):
    user = request.user
    if user is None:
        # Could be user not found, or database error during loading
        # Check logs for details
        raise HTTPException(status_code=410, detail="Unable to load user")
    return {"id": user.id, "username": user.username}
```

## Performance Implications

- **No user access**: Zero database queries (only JWT auth in Rust) - ~100k RPS
- **User access**: One database query on first `request.user` access - ~15k RPS
- **Multiple accesses**: No additional queries (user cached via SimpleLazyObject) - Same as first access
- **Custom backends**: Query cost depends on your `get_user()` implementation

## Example: Complete User Service

```python
from typing import Optional
from django_bolt import BoltAPI
from django_bolt.auth import JWTAuthentication, IsAuthenticated, HasPermission
from django.contrib.auth.models import User

api = BoltAPI()

@api.get("/me", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_current_user(request) -> dict:
    """Get current authenticated user"""
    user = request.user
    if not user:
        return {"error": "User not found"}
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
    }

@api.put("/me", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def update_profile(request, email: str) -> dict:
    """Update current user's profile"""
    user = request.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email = email
    await user.asave()
    return {"email": user.email, "username": user.username}

@api.delete("/users/{user_id}",
    auth=[JWTAuthentication()],
    guards=[HasPermission("auth.delete_user")]
)
async def delete_user(request, user_id: int) -> dict:
    """Delete a user (admin only)"""
    current_user = request.user
    if not current_user or not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Permission denied")

    try:
        user = await User.objects.aget(id=user_id)
        await user.adelete()
        return {"deleted": True, "user_id": user_id}
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
```

## Implementing for Custom User Models

Django-Bolt automatically uses `django.contrib.auth.get_user_model()`, so it works with custom user models:

```python
# settings.py
AUTH_USER_MODEL = 'myapp.CustomUser'

# views.py - automatically uses CustomUser!
@api.get("/profile", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_profile(request):
    user = request.user  # Type: CustomUser
    return {"user_type": type(user).__name__}
```

## Extending Custom Types

Django-Bolt provides several Protocol types for type safety and IDE autocomplete. These types can be extended to match your custom implementations:

### Creating a Custom UserType

If your user model has additional fields or methods, create a custom Protocol that extends `UserType`:

```python
from typing import Protocol
from django_bolt import UserType

class CustomUserType(UserType, Protocol):
    """Extended user type with custom fields"""

    # Django-Bolt's UserType fields (inherited)
    # - id, pk, is_active
    # - email, first_name, last_name, is_staff, is_superuser
    # - ORM methods: save, delete, refresh_from_db, asave, adelete, etc.

    # Your custom fields
    organization_id: int
    phone_number: str
    bio: str
    profile_picture: str

    # Your custom methods
    def get_organization(self) -> 'Organization': ...
    async def aget_organization(self) -> 'Organization': ...
```

Then use it in your handlers:

```python
from typing import cast
from django_bolt import BoltAPI

api = BoltAPI()

@api.get("/profile", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_profile(request) -> dict:
    user: CustomUserType = cast(request.user, CustomUserType)
    return {
        "username": user.username,
        "organization_id": user.organization_id,
        "phone": user.phone_number,
    }
```

### Extending DjangoModel for Custom ORM Methods

If you have custom model methods or managers, extend `DjangoModel`:

```python
from django_bolt import DjangoModel
from typing import Protocol

class CustomModel(DjangoModel, Protocol):
    """Extended model type with custom methods"""

    # Inherited ORM methods from DjangoModel:
    # - save, delete, refresh_from_db, full_clean
    # - asave, adelete, arefresh_from_db

    # Your custom model methods
    def get_absolute_url(self) -> str: ...
    async def aget_related_data(self) -> dict: ...
    def is_published(self) -> bool: ...
```

### Extending AuthContext

If you add custom claims or fields to your authentication context:

```python
from django_bolt import AuthContext
from typing import Protocol, Optional, Dict, Any

class CustomAuthContext(AuthContext, Protocol):
    """Extended auth context with custom fields"""

    # Inherited from AuthContext:
    # - user_id, is_staff, is_admin, backend
    # - permissions, claims

    # Your custom fields
    organization_id: Optional[str]
    """Organization the user belongs to"""

    api_version: Optional[str]
    """API version being used"""

    custom_scopes: Optional[set[str]]
    """Custom application-specific scopes"""
```

Then access it in handlers:

```python
@api.get("/org-data", guards=[IsAuthenticated()])
async def get_org_data(request) -> dict:
    ctx: CustomAuthContext = cast(request.context, CustomAuthContext)
    return {
        "org_id": ctx.organization_id,
        "api_version": ctx.api_version,
        "scopes": list(ctx.custom_scopes or set()),
    }
```

### Custom Request Type via Type Annotation

The best way to use a custom Request type is to simply annotate the parameter with your custom Protocol. Python's type system is erased at runtime, so the actual object being passed is still the Django-Bolt `Request` - but your type checker and IDE will provide autocomplete for your custom fields:

```python
from typing import Protocol, Optional
from django_bolt import Request, BoltAPI

class CustomRequest(Request, Protocol):
    """Extended Request with custom properties from middleware"""

    # Inherited from Request:
    # - method, path, body, context, user
    # - get(), __getitem__()

    # Your custom fields (added by middleware or other mechanisms)
    tenant_id: Optional[str]
    request_id: str
    user_org_id: Optional[int]

api = BoltAPI()

@api.get("/endpoint")
async def handler(request: CustomRequest):  # Direct type annotation!
    # Full IDE autocomplete for both Request and custom fields
    method = request.method                 # From Request
    tenant = request.tenant_id              # From CustomRequest
    request_id = request.request_id         # From CustomRequest

    return {"tenant": tenant, "request_id": request_id}
```

**Why this works**:
1. **Type erasure at runtime**: Python ignores type hints at runtime, so the actual Rust-backed Request object is passed unchanged
2. **Type checking at dev time**: Your type checker (mypy, pyright, pylance) validates that you're using valid fields
3. **IDE autocomplete**: IDEs like VSCode show all fields from both `Request` and `CustomRequest`
4. **No casting overhead**: No runtime cost, just clean type annotations
5. **Natural Python pattern**: This is how Protocols are meant to be used

### Organizing Custom Types in a Centralized Module

For better organization and reusability, create a `types.py` module with all your custom Protocols:

```python
# myapp/types.py
from typing import Protocol, Optional
from django_bolt import Request, UserType, AuthContext

class CustomRequest(Request, Protocol):
    """Extended Request type with custom properties"""

    # Inherited from Request:
    # - method, path, body, context, user
    # - get(), __getitem__()

    # Custom properties (added by middleware or other mechanisms)
    tenant_id: Optional[str]
    request_id: str
    user_org_id: Optional[int]

class CustomUser(UserType, Protocol):
    """Extended user with custom fields from your user model"""

    # Inherited from UserType (which inherits from DjangoModel):
    # - id, pk, is_active, email, first_name, last_name, is_staff, is_superuser
    # - ORM methods: save, delete, asave, adelete, refresh_from_db, etc.

    # Custom user fields
    organization_id: int
    phone_number: str
    department: str

class CustomAuthContext(AuthContext, Protocol):
    """Extended auth context with custom fields"""

    # Inherited from AuthContext:
    # - user_id, is_staff, is_admin, backend, permissions, claims

    # Custom auth context fields
    organization_id: Optional[str]
    api_version: Optional[str]
```

Then use these custom types in your handlers with direct type annotation:

```python
# myapp/api.py
from django_bolt import BoltAPI, JWTAuthentication, IsAuthenticated
from myapp.types import CustomRequest, CustomUser, CustomAuthContext

api = BoltAPI()

@api.get("/profile", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_profile(request: CustomRequest):
    """Get user profile with custom fields"""

    # Full IDE autocomplete for all properties
    user: CustomUser = request.user
    ctx: CustomAuthContext = request.context

    return {
        "user_id": user.id,
        "username": user.username,
        "org_id": user.organization_id,
        "department": user.department,
        "tenant_id": request.tenant_id,
        "request_id": request.request_id,
        "context_org": ctx.organization_id,
    }

@api.post("/org-data")
async def create_org_data(request: CustomRequest):
    """Create data for organization"""
    return {
        "tenant_id": request.tenant_id,
        "org_id": request.user_org_id,
    }
```

### Why Protocol-Based Typing?

Django-Bolt uses Protocols instead of concrete base classes because:

1. **Structural typing**: Works with any Django model without inheritance
2. **IDE support**: Full autocomplete for custom user models
3. **Flexibility**: Easy to extend for custom implementations
4. **No overhead**: No runtime performance impact
5. **Type safety**: Catches errors at development time

## See Also

- [SECURITY.md](./SECURITY.md) - Authentication and guards
- [DEPENDENCY_INJECTION.md](./DEPENDENCY_INJECTION.md) - Dependency injection patterns
- [CLASS_BASED_VIEWS.md](./CLASS_BASED_VIEWS.md) - Class-based views with request.user

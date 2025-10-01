# Token Revocation Examples

Token revocation is **OPTIONAL** in Django-Bolt. Only use it if you need logout functionality or token invalidation.

## Quick Start

### Option 1: In-Memory (Development/Single-Process)

```python
from django_bolt import BoltAPI, JWTAuthentication, Token, IsAuthenticated
from django_bolt.auth.revocation import InMemoryRevocation
from datetime import timedelta
import uuid

# Create revocation store
revocation = InMemoryRevocation()

# Create API with revocation-enabled auth
api = BoltAPI()

auth = JWTAuthentication(
    secret=settings.SECRET_KEY,
    revocation_store=revocation,  # ← OPTIONAL: Enables revocation
    require_jti=True,  # ← Auto-enabled when revocation_store is provided
)

# Login endpoint - create tokens with JTI
@api.post("/login")
async def login(username: str, password: str):
    user = await authenticate(username=username, password=password)

    if not user:
        return {"error": "Invalid credentials"}, 401

    # Create token with JTI (required for revocation)
    token = Token.create(
        sub=str(user.id),
        expires_delta=timedelta(hours=1),
        jti=str(uuid.uuid4()),  # ← Unique token ID (required for revocation)
        is_staff=user.is_staff,
        is_admin=user.is_superuser,
    )

    return {
        "access_token": token.encode(settings.SECRET_KEY),
        "token_type": "bearer"
    }

# Logout endpoint - revoke token
@api.post("/logout", auth=[auth], guards=[IsAuthenticated()])
async def logout(request):
    jti = request["context"]["auth_claims"]["jti"]

    # Revoke the token
    await revocation.revoke(jti, ttl=3600)  # TTL = remaining token lifetime

    return {"message": "Logged out successfully"}

# Protected endpoint
@api.get("/profile", auth=[auth], guards=[IsAuthenticated()])
async def get_profile(request):
    user_id = request["context"]["user_id"]
    return {"user_id": user_id}
```

---

### Option 2: Django Cache (Production - Redis/Memcached)

```python
from django_bolt import BoltAPI, JWTAuthentication
from django_bolt.auth.revocation import DjangoCacheRevocation

# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# api.py
revocation = DjangoCacheRevocation(
    cache_alias='default',
    key_prefix='revoked:',  # Keys will be "revoked:{jti}"
)

auth = JWTAuthentication(
    secret=settings.SECRET_KEY,
    revocation_store=revocation,
)

@api.post("/logout", auth=[auth])
async def logout(request):
    jti = request["context"]["auth_claims"]["jti"]

    # Revoke token - stored in Redis with TTL
    await revocation.revoke(jti, ttl=86400 * 30)  # 30 days

    return {"message": "Token revoked"}
```

---

### Option 3: Database (No Cache Infrastructure)

```python
# myapp/models.py
from django.db import models

class RevokedToken(models.Model):
    jti = models.CharField(max_length=255, unique=True, db_index=True)
    revoked_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['jti']),
            models.Index(fields=['expires_at']),
        ]
```

```python
# api.py
from django_bolt.auth.revocation import DjangoORMRevocation

revocation = DjangoORMRevocation(model='myapp.RevokedToken')

auth = JWTAuthentication(
    secret=settings.SECRET_KEY,
    revocation_store=revocation,
)

@api.post("/logout", auth=[auth])
async def logout(request):
    jti = request["context"]["auth_claims"]["jti"]

    # Revoke token - stored in database
    await revocation.revoke(jti, ttl=86400 * 30)

    return {"message": "Token revoked"}
```

**⚠️ Important**: Add cleanup task for expired tokens:

```python
# Celery task or cron job
from datetime import datetime, timezone
from myapp.models import RevokedToken

async def cleanup_expired_tokens():
    """Run this periodically (e.g., daily)"""
    await RevokedToken.objects.filter(
        expires_at__lt=datetime.now(timezone.utc)
    ).adelete()
```

---

### Option 4: Custom Revocation Handler

If you have custom logic or use a different storage backend:

```python
from django_bolt import JWTAuthentication
import httpx

# Custom handler - checks external service
async def check_token_revoked(jti: str) -> bool:
    """Custom revocation logic"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://auth-service/check-revoked/{jti}")
        return response.json()["revoked"]

auth = JWTAuthentication(
    secret=settings.SECRET_KEY,
    revoked_token_handler=check_token_revoked,  # ← Custom function
    require_jti=True,
)
```

---

## Without Revocation (Simpler, Faster)

If you don't need logout functionality, just don't provide a revocation handler:

```python
# NO revocation - tokens valid until expiry
auth = JWTAuthentication(
    secret=settings.SECRET_KEY,
    # No revocation_store or revoked_token_handler
)

# Users can't logout - tokens expire naturally
# ✅ Simpler
# ✅ Faster (~60k RPS vs ~50k RPS with revocation)
# ❌ No logout support
```

---

## Performance Comparison

| Revocation Strategy | RPS | Multi-Process | Notes |
|---------------------|-----|---------------|-------|
| **No Revocation** | ~60k | ✅ | Fastest, no logout |
| **InMemoryRevocation** | ~58k | ❌ | Single process only |
| **DjangoCacheRevocation (Redis)** | ~50k | ✅ | **Recommended for production** |
| **DjangoCacheRevocation (Memcached)** | ~48k | ✅ | Good alternative |
| **DjangoORMRevocation (PostgreSQL)** | ~5k | ✅ | Slowest, use if no cache |
| **DjangoORMRevocation (SQLite)** | ~2k | ⚠️ | Not for production |

---

## Complete Login/Logout Example

```python
from django_bolt import BoltAPI, JWTAuthentication, Token, IsAuthenticated, AllowAny
from django_bolt.auth.revocation import DjangoCacheRevocation
from django.contrib.auth import authenticate
from datetime import timedelta
import uuid

api = BoltAPI()

# Setup revocation
revocation = DjangoCacheRevocation()

auth = JWTAuthentication(
    secret=settings.SECRET_KEY,
    revocation_store=revocation,
)

# Public login endpoint
@api.post("/auth/login", guards=[AllowAny()])
async def login(username: str, password: str):
    """Authenticate and return JWT token."""
    user = await authenticate(username=username, password=password)

    if not user:
        return {"error": "Invalid credentials"}, 401

    # Create access token (short-lived)
    access_token = Token.create(
        sub=str(user.id),
        expires_delta=timedelta(minutes=15),
        jti=str(uuid.uuid4()),  # Required for revocation
        is_staff=user.is_staff,
        is_admin=user.is_superuser,
        permissions=list(user.get_all_permissions()),
        extras={
            "username": user.username,
            "email": user.email,
        }
    )

    # Optional: Create refresh token (long-lived)
    refresh_token = Token.create(
        sub=str(user.id),
        expires_delta=timedelta(days=30),
        jti=str(uuid.uuid4()),
        extras={"type": "refresh"}
    )

    return {
        "access_token": access_token.encode(settings.SECRET_KEY),
        "refresh_token": refresh_token.encode(settings.SECRET_KEY),
        "token_type": "bearer",
        "expires_in": 900  # 15 minutes
    }

# Protected logout endpoint
@api.post("/auth/logout", auth=[auth], guards=[IsAuthenticated()])
async def logout(request):
    """Logout - revoke current token."""
    jti = request["context"]["auth_claims"]["jti"]

    # Calculate TTL from token expiry
    exp = request["context"]["auth_claims"]["exp"]
    import time
    ttl = max(0, exp - int(time.time()))

    # Revoke token
    await revocation.revoke(jti, ttl=ttl)

    return {"message": "Logged out successfully"}

# Refresh token endpoint
@api.post("/auth/refresh", guards=[AllowAny()])
async def refresh_access_token(refresh_token: str):
    """Exchange refresh token for new access token."""
    try:
        # Decode refresh token
        token = Token.decode(refresh_token, secret=settings.SECRET_KEY)

        # Validate it's a refresh token
        if token.extras.get("type") != "refresh":
            return {"error": "Invalid token type"}, 401

        # Check if revoked
        if await revocation.is_revoked(token.jti):
            return {"error": "Token has been revoked"}, 401

        # Create new access token
        new_access = Token.create(
            sub=token.sub,
            expires_delta=timedelta(minutes=15),
            jti=str(uuid.uuid4()),
        )

        return {
            "access_token": new_access.encode(settings.SECRET_KEY),
            "token_type": "bearer",
            "expires_in": 900
        }

    except ValueError as e:
        return {"error": "Invalid token"}, 401

# Protected endpoint
@api.get("/profile", auth=[auth], guards=[IsAuthenticated()])
async def get_profile(request):
    """Get current user profile."""
    user_id = request["context"]["user_id"]
    is_admin = request["context"]["is_admin"]
    permissions = request["context"].get("permissions", [])

    return {
        "user_id": user_id,
        "is_admin": is_admin,
        "permissions": permissions,
    }
```

---

## Best Practices

### 1. Always Use JTI with Revocation

```python
# ✅ Good - JTI for revocation
token = Token.create(
    sub="user123",
    jti=str(uuid.uuid4()),  # Unique ID
    expires_delta=timedelta(hours=1)
)

# ❌ Bad - No JTI, can't revoke
token = Token.create(
    sub="user123",
    expires_delta=timedelta(hours=1)
)
```

### 2. Set Appropriate TTL

```python
# Match revocation TTL to token expiry
token = Token.create(sub="user123", expires_delta=timedelta(hours=1))

# Revoke with same TTL (3600 seconds = 1 hour)
await revocation.revoke(jti, ttl=3600)

# After 1 hour, token expires AND revocation entry is cleaned up
```

### 3. Use DjangoCacheRevocation in Production

```python
# ✅ Recommended for production
revocation = DjangoCacheRevocation()  # Uses Redis/Memcached

# ⚠️ Only for development
revocation = InMemoryRevocation()  # Single-process only

# 🐌 Slower but works without cache
revocation = DjangoORMRevocation(model='myapp.RevokedToken')
```

---

## Summary

- **Revocation is OPTIONAL** - only use if you need logout
- **Multiple storage options** - In-memory, Cache, Database, Custom
- **No Redis requirement** - Works with Django cache (any backend)
- **Performance-aware** - Cache-based revocation still does ~50k RPS
- **JTI auto-required** - When revocation is enabled, JTI becomes mandatory
- **Flexible** - Bring your own storage with custom handler

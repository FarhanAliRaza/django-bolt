# Dependency Injection Guide

Django-Bolt provides a powerful dependency injection system inspired by FastAPI that allows you to inject reusable dependencies into your route handlers. Dependencies are resolved automatically before your handler executes, making your code cleaner and more testable.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [The Depends() Marker](#the-depends-marker)
- [Caching Behavior](#caching-behavior)
- [Dependency Lifecycle](#dependency-lifecycle)
- [Nested Dependencies](#nested-dependencies)
- [Common Patterns](#common-patterns)
  - [get_current_user](#get_current_user)
  - [get_db](#get_db)
  - [get_settings](#get_settings)
  - [Query Parameter Extraction](#query-parameter-extraction)
  - [Header Validation](#header-validation)
- [Integration with Authentication](#integration-with-authentication)
- [Dependency Resolution Order](#dependency-resolution-order)
- [Error Handling](#error-handling)
- [Testing Dependencies](#testing-dependencies)
- [Class-Based Views](#class-based-views)
- [Best Practices](#best-practices)
- [Comparison with FastAPI](#comparison-with-fastapi)

---

## Overview

Dependency injection allows you to:

- Extract common logic into reusable functions
- Inject authenticated users, database connections, or configuration
- Test handlers independently by mocking dependencies
- Avoid repetitive parameter extraction code
- Compose complex dependencies from simpler ones

**Key Features:**
- Dependencies are async functions that receive request context
- Automatic caching per request (configurable)
- Type-safe parameter extraction and validation
- Integration with authentication and guards
- Support for nested dependencies

---

## Quick Start

```python
from django_bolt import BoltAPI
from django_bolt.params import Depends

api = BoltAPI()

# Define a dependency
async def get_current_time():
    from datetime import datetime
    return datetime.now()

# Inject the dependency
@api.get("/time")
async def show_time(current_time = Depends(get_current_time)):
    return {"time": current_time.isoformat()}
```

When a request hits `/time`, Django-Bolt:
1. Calls `get_current_time()` to resolve the dependency
2. Passes the result as `current_time` to your handler
3. Returns the response

---

## The Depends() Marker

The `Depends()` marker tells Django-Bolt that a parameter should be resolved via dependency injection.

### Basic Syntax

```python
from django_bolt.params import Depends

@api.get("/route")
async def handler(dep = Depends(dependency_function)):
    # dep contains the result of dependency_function()
    return {"value": dep}
```

### Parameters

```python
class Depends:
    dependency: Optional[Callable[..., Any]] = None
    """Function to call for dependency resolution"""

    use_cache: bool = True
    """Whether to cache the dependency result per request"""
```

### Dependency Function Requirements

Dependency functions must:
- Be `async` functions
- Return a value (or None)
- Accept any valid parameters (path, query, headers, body, other dependencies)

```python
# Valid dependency signatures
async def simple_dep():
    return {"value": 1}

async def dep_with_request(request):
    return request.get("headers", {})

async def dep_with_params(user_id: int, request):
    return await get_user(user_id)

async def dep_with_deps(db = Depends(get_db)):
    return await db.query()
```

---

## Caching Behavior

By default, dependencies are cached **per request** to avoid redundant computation.

### Default Caching (use_cache=True)

```python
call_count = 0

async def expensive_operation():
    global call_count
    call_count += 1
    # Expensive computation here
    await asyncio.sleep(1)
    return {"result": "data"}

@api.get("/route1")
async def route1(data = Depends(expensive_operation)):
    return data

@api.get("/route2")
async def route2(
    data1 = Depends(expensive_operation),
    data2 = Depends(expensive_operation)
):
    # expensive_operation() is called only ONCE per request
    # data1 and data2 reference the same cached result
    return {"data1": data1, "data2": data2}
```

**Request 1 to `/route1`**: `call_count = 1`
**Request 2 to `/route2`**: `call_count = 2` (called once for this request)

### Disable Caching (use_cache=False)

```python
async def get_fresh_data():
    # Always fetch latest data
    return await fetch_latest()

@api.get("/fresh")
async def fresh_route(
    data1 = Depends(get_fresh_data, use_cache=False),
    data2 = Depends(get_fresh_data, use_cache=False)
):
    # get_fresh_data() is called TWICE (once for each parameter)
    return {"data1": data1, "data2": data2}
```

**Use Cases for `use_cache=False`:**
- Fetching real-time data (e.g., current timestamp)
- Random number generation
- Operations with side effects that must run multiple times

---

## Dependency Lifecycle

Dependencies follow a strict lifecycle per request:

1. **Request arrives** at the server
2. **Dependency resolution** starts in order:
   - Django-Bolt inspects handler signature
   - Identifies parameters marked with `Depends()`
   - Resolves dependencies recursively (nested deps first)
3. **Dependency execution**:
   - Each dependency function is called
   - Result is cached (if `use_cache=True`)
   - Result is passed to handler parameter
4. **Handler execution** with resolved dependencies
5. **Response returned**
6. **Cache cleared** (dependency cache is per-request only)

```python
async def dep_a():
    print("dep_a called")
    return "A"

async def dep_b(a = Depends(dep_a)):
    print(f"dep_b called with {a}")
    return "B"

@api.get("/test")
async def handler(b = Depends(dep_b)):
    print(f"handler called with {b}")
    return {"result": b}

# Request to /test prints:
# dep_a called
# dep_b called with A
# handler called with B
```

---

## Nested Dependencies

Dependencies can depend on other dependencies, creating a dependency tree.

### Example: Database Connection → User Repository → Current User

```python
from django.db import connection as django_connection

# Level 1: Database connection
async def get_db():
    """Provide database connection"""
    return django_connection

# Level 2: User repository (depends on db)
async def get_user_repository(db = Depends(get_db)):
    """Provide user repository with database access"""
    class UserRepository:
        def __init__(self, db):
            self.db = db

        async def get_by_id(self, user_id: int):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return await User.objects.aget(id=user_id)

    return UserRepository(db)

# Level 3: Current user (depends on repository and request context)
async def get_current_user(
    request,
    user_repo = Depends(get_user_repository)
):
    """Get authenticated user from request context"""
    context = request.get("context", {})
    user_id = context.get("user_id")

    if not user_id:
        from django_bolt.exceptions import Unauthorized
        raise Unauthorized("Authentication required")

    return await user_repo.get_by_id(int(user_id))

# Use in route
@api.get("/profile")
async def get_profile(user = Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }
```

**Resolution Order:**
1. `get_db()` → returns db connection
2. `get_user_repository(db)` → returns repository
3. `get_current_user(request, user_repo)` → returns user
4. `get_profile(user)` → returns response

**Caching Applies to All Levels:**
If multiple dependencies use `get_db()`, it's only called once per request.

---

## Common Patterns

### get_current_user

The most common dependency pattern is extracting the authenticated user.

```python
from django_bolt.auth.jwt_utils import get_current_user
from django_bolt.auth import JWTAuthentication, IsAuthenticated

# Built-in get_current_user is provided by Django-Bolt
# Located in: django_bolt.auth.jwt_utils

@api.get(
    "/me",
    auth=[JWTAuthentication()],
    guards=[IsAuthenticated()]
)
async def get_my_profile(user = Depends(get_current_user)):
    """
    Returns current authenticated user's profile.

    The user is fetched from the database using the user_id
    from the JWT token's context.
    """
    if not user:
        from django_bolt.exceptions import Unauthorized
        raise Unauthorized("User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff
    }
```

**Custom get_current_user:**

```python
async def get_current_user_custom(request):
    """Custom implementation with additional checks"""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    context = request.get("context", {})
    user_id = context.get("user_id")

    if not user_id:
        return None

    try:
        user = await User.objects.select_related('profile').aget(pk=user_id)

        # Additional check: User must be active
        if not user.is_active:
            return None

        return user
    except User.DoesNotExist:
        return None

@api.get("/dashboard")
async def dashboard(user = Depends(get_current_user_custom)):
    if not user:
        return {"error": "Authentication required"}, 401

    return {"welcome": user.username}
```

### get_db

Provide database access to routes.

```python
from django.db import connection

async def get_db():
    """
    Provide database connection.

    Returns Django's database connection for executing raw queries
    or accessing the connection directly.
    """
    return connection

@api.get("/stats")
async def get_stats(db = Depends(get_db)):
    """Execute raw SQL query"""
    with db.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM auth_user")
        user_count = cursor.fetchone()[0]

    return {"total_users": user_count}
```

**Using with Django ORM:**

```python
async def get_db_session():
    """
    Provide a context manager for database operations.

    Note: Django ORM doesn't require explicit session management
    like SQLAlchemy. This is more for consistency if you're coming
    from other frameworks.
    """
    # Django handles connections automatically
    # Just return a marker or None
    return None

@api.post("/users")
async def create_user(user_data: UserCreate, db = Depends(get_db_session)):
    """Create user with dependency injection pattern"""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = await User.objects.acreate(
        username=user_data.username,
        email=user_data.email
    )

    return {"id": user.id, "username": user.username}
```

### get_settings

Inject configuration into routes.

```python
from django.conf import settings

async def get_settings():
    """Provide Django settings"""
    return settings

@api.get("/config")
async def get_config(settings = Depends(get_settings)):
    """Return public configuration"""
    return {
        "debug": settings.DEBUG,
        "allowed_hosts": settings.ALLOWED_HOSTS,
        "api_version": "1.0.0"
    }
```

**Cached Settings Object:**

```python
class AppSettings:
    """Application settings with caching"""
    def __init__(self):
        from django.conf import settings
        self.debug = settings.DEBUG
        self.api_version = getattr(settings, 'API_VERSION', '1.0.0')
        self.max_upload_size = getattr(settings, 'BOLT_MAX_UPLOAD_SIZE', 10485760)
        self.feature_flags = getattr(settings, 'FEATURE_FLAGS', {})

    def is_feature_enabled(self, feature_name: str) -> bool:
        return self.feature_flags.get(feature_name, False)

_app_settings = None

async def get_app_settings() -> AppSettings:
    """Get cached application settings"""
    global _app_settings
    if _app_settings is None:
        _app_settings = AppSettings()
    return _app_settings

@api.post("/upload")
async def upload_file(
    file: bytes,
    settings = Depends(get_app_settings)
):
    """Upload file with size limit from settings"""
    if len(file) > settings.max_upload_size:
        from django_bolt.exceptions import HTTPException
        raise HTTPException(413, "File too large")

    # Process upload...
    return {"uploaded": True, "size": len(file)}
```

### Query Parameter Extraction

Dependencies can extract and validate query parameters.

```python
from typing import Optional

class PaginationParams:
    """Pagination parameters with defaults"""
    def __init__(self, page: int = 1, page_size: int = 100):
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), 1000)  # Cap at 1000
        self.offset = (self.page - 1) * self.page_size

async def get_pagination(
    page: int = 1,
    page_size: int = 100
) -> PaginationParams:
    """Extract pagination parameters from query string"""
    return PaginationParams(page, page_size)

@api.get("/users")
async def list_users(pagination = Depends(get_pagination)):
    """List users with pagination"""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    users = await User.objects.all()[
        pagination.offset:pagination.offset + pagination.page_size
    ]

    return {
        "page": pagination.page,
        "page_size": pagination.page_size,
        "users": [{"id": u.id, "username": u.username} async for u in users]
    }
```

### Header Validation

Dependencies can validate and extract headers.

```python
from typing import Annotated
from django_bolt.params import Header
from django_bolt.exceptions import HTTPException

async def verify_api_version(
    api_version: Annotated[str, Header(alias="x-api-version")] = "1.0"
):
    """Verify API version from header"""
    supported_versions = ["1.0", "1.1", "2.0"]

    if api_version not in supported_versions:
        raise HTTPException(
            400,
            {
                "error": "Unsupported API version",
                "supported": supported_versions,
                "requested": api_version
            }
        )

    return api_version

@api.get("/data")
async def get_data(version = Depends(verify_api_version)):
    """Get data (API version checked automatically)"""
    return {
        "api_version": version,
        "data": "some data"
    }
```

---

## Integration with Authentication

Dependencies work seamlessly with authentication and guards.

### Extracting Auth Context

```python
from django_bolt.auth.jwt_utils import get_auth_context

@api.get("/profile")
async def get_profile(request):
    """Access auth context directly"""
    auth_ctx = get_auth_context(request)

    return {
        "user_id": auth_ctx.get("user_id"),
        "is_staff": auth_ctx.get("is_staff"),
        "auth_backend": auth_ctx.get("auth_backend")
    }
```

### Custom Auth Dependency

```python
async def require_admin(request):
    """Dependency that requires admin user"""
    context = request.get("context", {})
    is_admin = context.get("is_admin", False)

    if not is_admin:
        from django_bolt.exceptions import Forbidden
        raise Forbidden("Admin access required")

    return True

@api.get("/admin/stats", auth=[JWTAuthentication()])
async def admin_stats(is_admin = Depends(require_admin)):
    """Admin-only endpoint (enforced by dependency)"""
    # is_admin is True if we reach here
    return {"stats": "admin data"}
```

### Combining Guards and Dependencies

```python
from django_bolt.auth import JWTAuthentication, IsAuthenticated

# Guards run in Rust (fast, no Python GIL overhead)
# Dependencies run in Python (full access to Django ORM)

@api.post(
    "/articles",
    auth=[JWTAuthentication()],
    guards=[IsAuthenticated()]  # Fast Rust check
)
async def create_article(
    article: ArticleCreate,
    user = Depends(get_current_user)  # Python dependency (fetches from DB)
):
    """
    1. JWTAuthentication validates token (Rust)
    2. IsAuthenticated checks auth context (Rust)
    3. get_current_user fetches user from DB (Python)
    4. Handler executes
    """
    article_obj = await Article.objects.acreate(
        title=article.title,
        content=article.content,
        author=user
    )

    return {"id": article_obj.id, "title": article_obj.title}
```

**Performance Insight:**
- Guards execute in Rust before Python handler is invoked (no GIL overhead)
- Dependencies execute in Python after guards pass (with GIL, but full ORM access)
- Best practice: Use guards for simple checks, dependencies for database operations

---

## Dependency Resolution Order

Dependencies are resolved in the order they appear in the function signature, with nested dependencies resolved depth-first.

### Example: Resolution Order

```python
async def dep_1():
    print("1. dep_1")
    return "D1"

async def dep_2():
    print("2. dep_2")
    return "D2"

async def dep_3(d1 = Depends(dep_1)):
    print(f"3. dep_3 (needs {d1})")
    return "D3"

async def dep_4(d2 = Depends(dep_2), d3 = Depends(dep_3)):
    print(f"4. dep_4 (needs {d2} and {d3})")
    return "D4"

@api.get("/test")
async def handler(d4 = Depends(dep_4), d1 = Depends(dep_1)):
    print(f"5. handler (needs {d4} and {d1})")
    return {"result": "done"}

# Request to /test prints:
# 1. dep_1         (for dep_3)
# 3. dep_3 (needs D1)
# 2. dep_2         (for dep_4)
# 4. dep_4 (needs D2 and D3)
# 5. handler (needs D4 and D1)  <- dep_1 is cached, not called again
```

**Key Points:**
- Dependencies are resolved recursively (nested first)
- Each dependency is only called once per request (cached)
- Order in function signature doesn't affect resolution (dependency tree determines order)

---

## Error Handling

Dependencies can raise exceptions that are propagated to the error handler.

### Raising HTTPException

```python
from django_bolt.exceptions import HTTPException, Unauthorized, Forbidden

async def get_authenticated_user(request):
    """Dependency that raises if not authenticated"""
    context = request.get("context", {})
    user_id = context.get("user_id")

    if not user_id:
        raise Unauthorized("Authentication required")

    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        return await User.objects.aget(id=user_id)
    except User.DoesNotExist:
        raise Forbidden("User account not found")

@api.get("/profile")
async def get_profile(user = Depends(get_authenticated_user)):
    # If dependency raises, handler is never called
    # Error is returned to client automatically
    return {"username": user.username}
```

### Custom Validation Errors

```python
from django_bolt.exceptions import RequestValidationError

async def validate_api_key(
    api_key: Annotated[str, Header(alias="x-api-key")]
):
    """Validate API key format"""
    if len(api_key) < 32:
        raise RequestValidationError(
            errors=[{
                "loc": ["header", "x-api-key"],
                "msg": "API key must be at least 32 characters",
                "type": "value_error"
            }]
        )

    return api_key

@api.get("/data")
async def get_data(api_key = Depends(validate_api_key)):
    return {"api_key": api_key[:8] + "..."}
```

### Handling Errors in Dependencies

```python
import logging

logger = logging.getLogger(__name__)

async def get_external_service():
    """Dependency that handles errors gracefully"""
    try:
        # Connect to external service
        service = await connect_to_service()
        return service
    except ConnectionError as e:
        logger.error(f"Failed to connect to service: {e}")
        # Return None or raise
        raise HTTPException(503, "Service temporarily unavailable")

@api.get("/external-data")
async def get_external_data(service = Depends(get_external_service)):
    # Service is guaranteed to be available here
    data = await service.fetch_data()
    return {"data": data}
```

---

## Testing Dependencies

Dependency injection makes testing easier by allowing you to override dependencies.

### Testing with TestClient

```python
from django_bolt.testing import TestClient

# Original dependency
async def get_current_user(request):
    # Real implementation
    ...

# Test override
async def get_mock_user(request):
    """Mock user for testing"""
    class MockUser:
        id = 1
        username = "testuser"
        email = "test@example.com"
        is_staff = False

    return MockUser()

# In your test
def test_profile_endpoint():
    api = BoltAPI()

    @api.get("/profile")
    async def get_profile(user = Depends(get_current_user)):
        return {"username": user.username}

    # Override dependency for testing
    # Note: You'd typically do this via dependency override mechanism
    # For now, you can create a separate test API with mock dependencies

    with TestClient(api) as client:
        response = client.get("/profile")
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
```

### Testing Individual Dependencies

```python
import pytest

@pytest.mark.asyncio
async def test_pagination_dependency():
    """Test pagination dependency in isolation"""

    # Test default values
    pagination = await get_pagination(page=1, page_size=50)
    assert pagination.page == 1
    assert pagination.page_size == 50
    assert pagination.offset == 0

    # Test page 2
    pagination = await get_pagination(page=2, page_size=50)
    assert pagination.offset == 50

    # Test max page_size cap
    pagination = await get_pagination(page=1, page_size=5000)
    assert pagination.page_size == 1000  # Capped at 1000
```

### Mocking Database Dependencies

```python
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_get_user_dependency():
    """Test get_current_user with mocked database"""

    # Create mock user
    mock_user = MagicMock()
    mock_user.id = 123
    mock_user.username = "testuser"

    # Create mock request
    mock_request = {
        "context": {"user_id": "123"}
    }

    # Mock the User.objects.aget method
    from django.contrib.auth import get_user_model
    User = get_user_model()
    User.objects.aget = AsyncMock(return_value=mock_user)

    # Test the dependency
    from django_bolt.auth.jwt_utils import get_current_user
    user = await get_current_user(mock_request)

    assert user.id == 123
    assert user.username == "testuser"
```

---

## Class-Based Views

Dependencies work with class-based views (APIView, ViewSet, ModelViewSet).

### Basic Usage

```python
from django_bolt.views import APIView
from django_bolt.params import Depends

async def get_current_user(request):
    """Shared dependency"""
    # ... implementation ...
    return user

@api.view("/profile")
class ProfileView(APIView):
    """Class-based view with dependency injection"""

    async def get(self, request, user = Depends(get_current_user)):
        """GET handler with injected user"""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }

    async def patch(self, request, data: ProfileUpdate, user = Depends(get_current_user)):
        """PATCH handler with injected user and request body"""
        user.email = data.email or user.email
        await user.asave()
        return {"updated": True}
```

### ViewSet with Dependencies

```python
from django_bolt.views import ViewSet

@api.viewset("/articles")
class ArticleViewSet(ViewSet):
    """ViewSet with dependency injection"""

    async def list(self, request, pagination = Depends(get_pagination)):
        """List articles with pagination"""
        articles = await Article.objects.all()[
            pagination.offset:pagination.offset + pagination.page_size
        ]
        return {
            "page": pagination.page,
            "articles": [{"id": a.id, "title": a.title} async for a in articles]
        }

    async def retrieve(self, request, pk: int, user = Depends(get_current_user)):
        """Retrieve single article (track view)"""
        article = await Article.objects.aget(pk=pk)

        # Log view by current user
        if user:
            await ArticleView.objects.acreate(article=article, user=user)

        return {"id": article.id, "title": article.title, "content": article.content}

    async def create(
        self,
        request,
        data: ArticleCreate,
        user = Depends(get_current_user)
    ):
        """Create article (user required)"""
        if not user:
            from django_bolt.exceptions import Unauthorized
            raise Unauthorized("Must be authenticated to create articles")

        article = await Article.objects.acreate(
            title=data.title,
            content=data.content,
            author=user
        )

        return {"id": article.id, "title": article.title}
```

---

## Best Practices

### 1. Keep Dependencies Focused

Each dependency should have a single responsibility.

```python
# ❌ BAD: Dependency does too much
async def get_user_with_posts_and_comments(request):
    user = await get_user(request)
    posts = await get_user_posts(user)
    comments = await get_user_comments(user)
    return {"user": user, "posts": posts, "comments": comments}

# ✅ GOOD: Separate dependencies
async def get_current_user(request):
    return await get_user(request)

async def get_user_posts(user = Depends(get_current_user)):
    return await Post.objects.filter(author=user).all()

async def get_user_comments(user = Depends(get_current_user)):
    return await Comment.objects.filter(author=user).all()
```

### 2. Use Type Hints

Type hints improve code clarity and enable better IDE support.

```python
from typing import Optional
from django.contrib.auth.models import User

async def get_current_user(request) -> Optional[User]:
    """Returns Django User or None"""
    ...

@api.get("/profile")
async def get_profile(user: Optional[User] = Depends(get_current_user)):
    if not user:
        return {"error": "Not authenticated"}, 401
    return {"username": user.username}
```

### 3. Cache Expensive Operations

Use default caching for expensive operations.

```python
# ✅ GOOD: Cached by default
async def get_system_config():
    """Load configuration (cached per request)"""
    config = await SystemConfig.objects.aget(pk=1)
    return config

# ❌ BAD: Disable cache unnecessarily
async def get_user_id(request):
    # This is cheap, but caching doesn't hurt
    return request.get("context", {}).get("user_id")
```

### 4. Validate Early

Use dependencies to validate parameters before handler execution.

```python
async def validate_article_id(article_id: int):
    """Validate article exists"""
    try:
        article = await Article.objects.aget(pk=article_id)
        return article
    except Article.DoesNotExist:
        from django_bolt.exceptions import NotFound
        raise NotFound(f"Article {article_id} not found")

@api.get("/articles/{article_id}")
async def get_article(article = Depends(validate_article_id)):
    # article is guaranteed to exist here
    return {"id": article.id, "title": article.title}
```

### 5. Avoid Side Effects in Dependencies

Dependencies should be idempotent and not modify state.

```python
# ❌ BAD: Side effect in dependency
async def log_request(request):
    """Don't log in dependencies"""
    await RequestLog.objects.acreate(path=request["path"])
    return request

# ✅ GOOD: Side effects in handler
@api.get("/data")
async def get_data(request):
    """Log in handler, not dependency"""
    await RequestLog.objects.acreate(path=request["path"])
    return {"data": "some data"}
```

### 6. Document Dependencies

Add docstrings to dependency functions.

```python
async def get_pagination(page: int = 1, page_size: int = 100):
    """
    Extract and validate pagination parameters.

    Args:
        page: Page number (1-indexed, default: 1)
        page_size: Items per page (1-1000, default: 100)

    Returns:
        PaginationParams with validated page, page_size, and offset

    Example:
        @api.get("/items")
        async def list_items(pagination = Depends(get_pagination)):
            items = await Item.objects.all()[
                pagination.offset:pagination.offset + pagination.page_size
            ]
            return {"items": items}
    """
    return PaginationParams(page, page_size)
```

### 7. Use Nested Dependencies for Composition

Build complex dependencies from simpler ones.

```python
# Simple dependencies
async def get_db():
    return connection

async def get_cache():
    from django.core.cache import cache
    return cache

# Composite dependency
async def get_user_service(
    db = Depends(get_db),
    cache = Depends(get_cache)
):
    """User service with database and cache access"""
    class UserService:
        def __init__(self, db, cache):
            self.db = db
            self.cache = cache

        async def get_user(self, user_id: int):
            # Try cache first
            cached = self.cache.get(f"user:{user_id}")
            if cached:
                return cached

            # Fetch from database
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = await User.objects.aget(id=user_id)

            # Cache for 5 minutes
            self.cache.set(f"user:{user_id}", user, 300)
            return user

    return UserService(db, cache)
```

### 8. Handle None Gracefully

Always check for None when dependencies can return None.

```python
async def get_optional_user(request):
    """Returns user or None (doesn't raise)"""
    context = request.get("context", {})
    user_id = context.get("user_id")

    if not user_id:
        return None

    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        return await User.objects.aget(id=user_id)
    except User.DoesNotExist:
        return None

@api.get("/dashboard")
async def dashboard(user = Depends(get_optional_user)):
    """Handle both authenticated and anonymous users"""
    if user:
        return {
            "welcome": user.username,
            "personalized": True
        }
    else:
        return {
            "welcome": "Guest",
            "personalized": False
        }
```

---

## Comparison with FastAPI

Django-Bolt's dependency injection is heavily inspired by FastAPI with some differences.

### Similarities

| Feature | Django-Bolt | FastAPI |
|---------|-------------|---------|
| `Depends()` marker | ✅ | ✅ |
| Nested dependencies | ✅ | ✅ |
| Per-request caching | ✅ | ✅ |
| Type hints | ✅ | ✅ |
| Async dependencies | ✅ | ✅ |

### Differences

| Feature | Django-Bolt | FastAPI |
|---------|-------------|---------|
| **Request object** | Always async dict | Starlette Request object |
| **Sync dependencies** | ❌ (async only) | ✅ (sync + async) |
| **Dependency overrides** | Manual (testing) | `app.dependency_overrides` |
| **Yield dependencies** | ❌ | ✅ (cleanup/teardown) |
| **Security dependencies** | Guards (Rust-based) | Dependencies (Python) |
| **ORM integration** | Django ORM (async) | SQLAlchemy or Tortoise |

### Migration from FastAPI

```python
# FastAPI
from fastapi import Depends, FastAPI
from fastapi.security import HTTPBearer

app = FastAPI()
security = HTTPBearer()

@app.get("/users/me")
async def read_current_user(token: str = Depends(security)):
    return {"token": token}

# Django-Bolt equivalent
from django_bolt import BoltAPI
from django_bolt.auth import JWTAuthentication, IsAuthenticated
from django_bolt.params import Depends

api = BoltAPI()

@api.get(
    "/users/me",
    auth=[JWTAuthentication()],
    guards=[IsAuthenticated()]
)
async def read_current_user(user = Depends(get_current_user)):
    return {"user_id": user.id}
```

**Key Differences:**
1. **Security**: Django-Bolt uses `auth=[...]` + `guards=[...]` instead of dependencies for auth
2. **Performance**: Django-Bolt auth/guards run in Rust (no Python GIL overhead)
3. **Request object**: Django-Bolt uses dict, FastAPI uses Starlette Request
4. **Async requirement**: Django-Bolt requires async dependencies, FastAPI supports both

---

## Advanced Examples

### Multi-Tenant Application

```python
async def get_tenant(
    tenant_id: Annotated[str, Header(alias="x-tenant-id")]
):
    """Extract and validate tenant from header"""
    tenant = await Tenant.objects.filter(tenant_id=tenant_id).afirst()

    if not tenant:
        from django_bolt.exceptions import NotFound
        raise NotFound(f"Tenant {tenant_id} not found")

    return tenant

async def get_tenant_db(tenant = Depends(get_tenant)):
    """Get database connection for tenant"""
    from django.db import connections
    return connections[tenant.database_alias]

@api.get("/data")
async def get_tenant_data(
    tenant = Depends(get_tenant),
    db = Depends(get_tenant_db)
):
    """Multi-tenant data access"""
    # Data is automatically scoped to tenant's database
    data = await TenantModel.objects.using(db.alias).all()
    return {
        "tenant": tenant.name,
        "data": [{"id": d.id} async for d in data]
    }
```

### Rate Limiting with Dependencies

```python
from datetime import datetime, timedelta

# Simple in-memory rate limiter (use Redis in production)
rate_limit_cache = {}

async def rate_limit_user(request):
    """Rate limit by user (5 requests per minute)"""
    context = request.get("context", {})
    user_id = context.get("user_id")

    if not user_id:
        return True  # Don't rate limit anonymous users

    now = datetime.now()
    key = f"rate_limit:{user_id}"

    # Get request timestamps from cache
    timestamps = rate_limit_cache.get(key, [])

    # Remove timestamps older than 1 minute
    timestamps = [ts for ts in timestamps if now - ts < timedelta(minutes=1)]

    # Check if limit exceeded
    if len(timestamps) >= 5:
        from django_bolt.exceptions import HTTPException
        raise HTTPException(429, "Rate limit exceeded. Try again later.")

    # Add current timestamp
    timestamps.append(now)
    rate_limit_cache[key] = timestamps

    return True

@api.post("/expensive-operation")
async def expensive_operation(
    rate_limited = Depends(rate_limit_user)
):
    """Rate-limited endpoint"""
    # Perform expensive operation
    return {"success": True}
```

---

## Additional Resources

- [FastAPI Dependencies Documentation](https://fastapi.tiangolo.com/tutorial/dependencies/) - Original inspiration
- [Django Async Views](https://docs.djangoproject.com/en/stable/topics/async/) - Django async support
- [Python Type Hints](https://docs.python.org/3/library/typing.html) - Type annotations
- [Testing Guide](./TESTING_UTILITIES.md) - Testing with Django-Bolt

---

**Last Updated:** October 2025
**Django-Bolt Version:** 0.1.0

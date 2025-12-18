# Django-Bolt Middleware System Design Document

**Version:** 1.0
**Status:** Draft
**Authors:** Django-Bolt Team
**Date:** December 2025

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Goals and Non-Goals](#2-goals-and-non-goals)
3. [Background and Research](#3-background-and-research)
4. [Design Overview](#4-design-overview)
5. [Type-Safe Request Object](#5-type-safe-request-object)
6. [Middleware System](#6-middleware-system)
7. [Django Middleware Compatibility](#7-django-middleware-compatibility)
8. [Hierarchical Middleware Scoping](#8-hierarchical-middleware-scoping)
9. [Rust Integration](#9-rust-integration)
10. [API Reference](#10-api-reference)
11. [Migration Guide](#11-migration-guide)
12. [Performance Considerations](#12-performance-considerations)
13. [Implementation Plan](#13-implementation-plan)

---

## 1. Executive Summary

This document describes the design for a complete rewrite of Django-Bolt's middleware system. The new system provides:

- **Full Django middleware compatibility** - Any Django middleware works without modification
- **Type-safe request object** - Generic `Request[UserT, AuthT, StateT]` with IDE autocomplete
- **Hierarchical middleware scoping** - App, router, and route-level middleware with inheritance
- **Best-in-class DX** - Inspired by Elysia, Litestar, and TanStack Router patterns
- **Zero-overhead abstractions** - Hot-path operations remain in Rust

The key insight driving this design is that **the request object IS the context** - following Django and Starlette patterns rather than introducing a separate context parameter.

---

## 2. Goals and Non-Goals

### Goals

1. **Django Compatibility**: Any Django middleware (SessionMiddleware, AuthenticationMiddleware, CsrfViewMiddleware, custom middlewares) should work with minimal wrapping
2. **Type Safety**: Full IDE autocomplete and type checking for `request.user`, `request.auth`, `request.state`
3. **Hierarchical Scoping**: Middleware can be applied at app, router, or route level with proper inheritance
4. **Performance**: Maintain 60k+ RPS by keeping hot-path operations in Rust
5. **Developer Experience**: Simple, intuitive API inspired by best frameworks
6. **Backwards Compatibility**: Existing `@cors()`, `@rate_limit()` decorators continue working

### Non-Goals

1. **Separate context object**: We do NOT introduce a `ctx` parameter - request IS the context
2. **Runtime type validation**: Type parameters are for static analysis, not runtime checks
3. **Django settings integration**: Middleware is configured via code, not `settings.MIDDLEWARE`
4. **Full ASGI middleware compatibility**: Focus is on Django middleware, not arbitrary ASGI middleware

---

## 3. Background and Research

### 3.1 How Django Handles Context

Django middlewares mutate the `HttpRequest` object directly:

```python
# Django's AuthenticationMiddleware
class AuthenticationMiddleware:
    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: get_user(request))
```

Handlers access middleware data via request attributes:

```python
def my_view(request):
    user = request.user  # Set by AuthenticationMiddleware
    session = request.session  # Set by SessionMiddleware
```

**Key insight**: Django does NOT use a separate context object. The request IS the context.

### 3.2 How Starlette/FastAPI Handles Context

Starlette uses ASGI scope with a `state` wrapper:

```python
# Middleware adds to scope
scope["user"] = authenticated_user
scope["state"]["custom"] = value

# Handler accesses via request properties
@app.get("/")
def handler(request: Request):
    user = request.user        # Property that reads scope["user"]
    custom = request.state.custom  # Wrapper around scope["state"]
```

### 3.3 How Litestar Achieves Type Safety

Litestar uses generic type parameters on Request:

```python
class Request(Generic[UserT, AuthT, StateT]):
    @property
    def user(self) -> UserT: ...

    @property
    def auth(self) -> AuthT: ...

# Handler with typed request
@get("/profile")
def handler(request: Request[User, JWTToken, MyState]) -> dict:
    request.user.email  # IDE knows User has email
```

### 3.4 How Elysia Achieves Type Safety

Elysia uses TypeScript's type inference through middleware chain:

```typescript
new Elysia()
  .derive(({ headers }) => ({
    user: validateToken(headers.authorization),
  }))
  .get("/", ({ user }) => user.name); // TypeScript knows user exists
```

### 3.5 Current Django-Bolt State

- Request is a Rust-backed `PyRequest` class with dict-like access
- Middleware metadata attached via decorators (`@cors`, `@rate_limit`)
- Compiled to Rust metadata at startup for hot-path execution
- No type safety for middleware-provided data
- No Django middleware compatibility

---

## 4. Design Overview

### 4.1 Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Request Lifecycle                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  HTTP Request                                                            │
│       │                                                                  │
│       ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ RUST LAYER (No GIL) - Hot Path                                  │    │
│  │  ├─ Route Matching (matchit)                                    │    │
│  │  ├─ Rate Limiting (governor)                                    │    │
│  │  ├─ CORS Preflight Handling                                     │    │
│  │  ├─ JWT/API Key Validation                                      │    │
│  │  └─ Permission Guards                                           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│       │                                                                  │
│       ▼ (GIL acquired)                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ PYTHON MIDDLEWARE LAYER                                         │    │
│  │  ├─ Django Middleware Adapter (wraps Django middlewares)        │    │
│  │  ├─ Native Bolt Middleware                                      │    │
│  │  └─ Request object populated with typed data                    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│       │                                                                  │
│       ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ HANDLER EXECUTION                                               │    │
│  │  └─ Receives Request[UserT, AuthT, StateT] with full typing     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│       │                                                                  │
│       ▼                                                                  │
│  HTTP Response                                                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Core Principles

1. **Request IS context**: No separate `ctx` parameter
2. **Type safety via generics**: `Request[UserT, AuthT, StateT]`
3. **Django patterns**: Middleware mutates request, handlers read from it
4. **Hierarchical inheritance**: Child routes inherit parent middleware
5. **Performance first**: Hot-path stays in Rust

---

## 5. Type-Safe Request Object

### 5.1 Request Class Definition

```python
from __future__ import annotations
from typing import TypeVar, Generic, Optional, Any, Dict, TYPE_CHECKING
from dataclasses import dataclass, field

# Type variables with defaults (PEP 696 - Python 3.13+, or typing_extensions)
UserT = TypeVar("UserT", default=Any)
AuthT = TypeVar("AuthT", default=Any)
StateT = TypeVar("StateT", bound=Dict[str, Any], default=Dict[str, Any])


@dataclass
class Request(Generic[UserT, AuthT, StateT]):
    """
    Type-safe HTTP request object.

    The request object serves as the context container for middleware data,
    following Django's pattern where middleware adds attributes to the request.

    Type Parameters:
        UserT: Type of authenticated user (e.g., Django User model)
        AuthT: Type of auth context (e.g., JWTClaims, APIKeyInfo)
        StateT: Type of custom state dict (e.g., TypedDict with custom fields)

    Examples:
        # Fully typed request with IDE autocomplete
        @api.get("/profile")
        async def profile(request: Request[User, JWTClaims, dict]) -> dict:
            return {"email": request.user.email}  # IDE knows User has email

        # Simple request without type parameters
        @api.get("/health")
        async def health(request: Request) -> dict:
            return {"status": "ok"}
    """

    # ═══════════════════════════════════════════════════════════════════════
    # Core HTTP Data (always available, always typed)
    # ═══════════════════════════════════════════════════════════════════════

    method: str
    """HTTP method (GET, POST, PUT, PATCH, DELETE, etc.)"""

    path: str
    """Request path (e.g., '/users/123')"""

    body: bytes = b""
    """Raw request body bytes"""

    headers: Dict[str, str] = field(default_factory=dict)
    """HTTP headers (lowercase keys)"""

    cookies: Dict[str, str] = field(default_factory=dict)
    """Parsed cookies"""

    query: Dict[str, str] = field(default_factory=dict)
    """Query string parameters"""

    params: Dict[str, str] = field(default_factory=dict)
    """Path parameters extracted from URL pattern"""

    # ═══════════════════════════════════════════════════════════════════════
    # Middleware-Provided Data (typed via generics)
    # ═══════════════════════════════════════════════════════════════════════

    _user: Optional[UserT] = field(default=None, repr=False)
    _auth: Optional[AuthT] = field(default=None, repr=False)
    _state: Dict[str, Any] = field(default_factory=dict, repr=False)

    # ═══════════════════════════════════════════════════════════════════════
    # Django Compatibility
    # ═══════════════════════════════════════════════════════════════════════

    _django_request: Optional[Any] = field(default=None, repr=False)
    """Reference to wrapped Django HttpRequest for middleware compatibility"""

    @property
    def user(self) -> UserT:
        """
        Authenticated user object.

        Set by authentication middleware (Django's AuthenticationMiddleware
        or Bolt's JWTAuthentication, etc.)

        Raises:
            AttributeError: If no authentication middleware is configured

        Returns:
            The authenticated user with type UserT
        """
        if self._user is None:
            raise AttributeError(
                "request.user is not available. "
                "Configure authentication middleware to enable user access.\n"
                "Example: api = BoltAPI(middleware=[DjangoMiddleware(AuthenticationMiddleware)])"
            )
        return self._user

    @user.setter
    def user(self, value: UserT) -> None:
        """Set the authenticated user (called by middleware)."""
        self._user = value

    @property
    def auth(self) -> AuthT:
        """
        Authentication context (JWT claims, API key info, etc.)

        Set by authentication middleware. Contains authentication metadata
        like JWT claims, API key permissions, session info, etc.

        Raises:
            AttributeError: If no authentication middleware is configured

        Returns:
            Authentication context with type AuthT
        """
        if self._auth is None:
            raise AttributeError(
                "request.auth is not available. "
                "Configure authentication middleware to enable auth context.\n"
                "Example: @api.get('/route', auth=[JWTAuthentication()])"
            )
        return self._auth

    @auth.setter
    def auth(self, value: AuthT) -> None:
        """Set the auth context (called by middleware)."""
        self._auth = value

    @property
    def state(self) -> State[StateT]:
        """
        Custom middleware state.

        A type-safe container for arbitrary data added by middleware.
        Supports both attribute and dict-style access.

        Examples:
            # Middleware adds data
            request.state["request_id"] = str(uuid4())
            request.state.start_time = time.time()

            # Handler reads data
            elapsed = time.time() - request.state.start_time

        Returns:
            State wrapper with type StateT
        """
        return State(self._state)

    # ═══════════════════════════════════════════════════════════════════════
    # Django Compatibility Properties
    # ═══════════════════════════════════════════════════════════════════════

    @property
    def session(self) -> Any:
        """
        Django session object.

        Available when DjangoMiddleware(SessionMiddleware) is configured.
        Provides the same interface as Django's request.session.

        Returns:
            Django SessionBase instance or None
        """
        return self._state.get("_django_session")

    @property
    def csrf_token(self) -> Optional[str]:
        """
        CSRF token for form submissions.

        Available when DjangoMiddleware(CsrfViewMiddleware) is configured.

        Returns:
            CSRF token string or None
        """
        return self._state.get("_csrf_token")

    # ═══════════════════════════════════════════════════════════════════════
    # Dict-Style Access (backwards compatibility)
    # ═══════════════════════════════════════════════════════════════════════

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-style get for backwards compatibility."""
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key: str) -> Any:
        """Dict-style access for backwards compatibility."""
        if key in ("method", "path", "body", "headers", "cookies", "query", "params"):
            return getattr(self, key)
        elif key == "user":
            return self._user
        elif key in ("auth", "context"):
            return self._auth
        elif key == "state":
            return self._state
        else:
            raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Dict-style assignment for backwards compatibility."""
        if key == "user":
            self._user = value
        elif key in ("auth", "context"):
            self._auth = value
        else:
            self._state[key] = value
```

### 5.2 State Class Definition

```python
from typing import TypeVar, Generic, Any, Dict, Iterator

StateT = TypeVar("StateT", bound=Dict[str, Any])


class State(Generic[StateT]):
    """
    Type-safe state container with attribute and dict access.

    Wraps a dictionary to provide both `state.key` and `state["key"]` access
    patterns while maintaining type safety through generics.

    When StateT is a TypedDict, IDEs provide autocomplete for known keys:

        class MyState(TypedDict):
            request_id: str
            start_time: float

        def handler(request: Request[User, Auth, MyState]):
            request.state.request_id  # IDE knows this is str
            request.state.start_time  # IDE knows this is float
    """

    __slots__ = ("_data",)

    def __init__(self, data: StateT) -> None:
        object.__setattr__(self, "_data", data)

    # ═══════════════════════════════════════════════════════════════════════
    # Dict-Style Access
    # ═══════════════════════════════════════════════════════════════════════

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    # ═══════════════════════════════════════════════════════════════════════
    # Attribute-Style Access (for TypedDict autocomplete)
    # ═══════════════════════════════════════════════════════════════════════

    def __getattr__(self, key: str) -> Any:
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            )

    def __setattr__(self, key: str, value: Any) -> None:
        if key == "_data":
            object.__setattr__(self, key, value)
        else:
            self._data[key] = value

    def __delattr__(self, key: str) -> None:
        try:
            del self._data[key]
        except KeyError:
            raise AttributeError(key)

    def __repr__(self) -> str:
        return f"State({self._data!r})"
```

### 5.3 Common Type Aliases

```python
# django_bolt/types.py

from typing import TypedDict, Optional, Any, List
from typing_extensions import NotRequired

# ═══════════════════════════════════════════════════════════════════════════
# Authentication Types
# ═══════════════════════════════════════════════════════════════════════════

class JWTClaims(TypedDict, total=False):
    """
    Standard JWT claims structure.

    See RFC 7519 for standard claim definitions.
    """
    # Registered claims (RFC 7519)
    sub: str                    # Subject (typically user ID)
    exp: int                    # Expiration time (Unix timestamp)
    iat: int                    # Issued at (Unix timestamp)
    nbf: int                    # Not before (Unix timestamp)
    iss: str                    # Issuer
    aud: str                    # Audience
    jti: str                    # JWT ID (unique identifier)

    # Common custom claims
    user_id: int
    username: str
    email: str
    is_staff: bool
    is_superuser: bool
    permissions: List[str]
    groups: List[str]


class APIKeyAuth(TypedDict):
    """API key authentication context."""
    key_id: str
    key_name: str
    permissions: List[str]
    rate_limit: NotRequired[int]
    metadata: NotRequired[dict]


class SessionAuth(TypedDict):
    """Session-based authentication context."""
    session_key: str
    user_id: int
    created_at: str
    last_activity: str


# ═══════════════════════════════════════════════════════════════════════════
# Request Type Aliases
# ═══════════════════════════════════════════════════════════════════════════

# For Django's AbstractUser
from django.contrib.auth.models import AbstractUser

# Authenticated request with Django user and JWT
AuthenticatedRequest = Request[AbstractUser, JWTClaims, dict]

# Request with API key authentication
APIKeyRequest = Request[None, APIKeyAuth, dict]

# Public request (no authentication)
PublicRequest = Request[None, None, dict]

# ═══════════════════════════════════════════════════════════════════════════
# Custom State Examples
# ═══════════════════════════════════════════════════════════════════════════

class TimingState(TypedDict):
    """State for timing middleware."""
    start_time: float
    request_id: str


class TracingState(TypedDict):
    """State for distributed tracing."""
    trace_id: str
    span_id: str
    parent_span_id: NotRequired[str]
    baggage: NotRequired[dict]
```

---

## 6. Middleware System

### 6.1 Middleware Protocol

```python
from typing import Protocol, Callable, Awaitable, Union, runtime_checkable
from django_bolt.responses import Response


@runtime_checkable
class Middleware(Protocol):
    """
    Protocol for Django-Bolt middleware.

    Middleware can be:
    1. A class implementing this protocol
    2. A callable (function or lambda)
    3. A Django middleware wrapped with DjangoMiddleware()

    The middleware receives the request and a `call_next` function to continue
    the chain. It can:
    - Modify the request before passing it on
    - Short-circuit by returning a response directly
    - Modify the response after the handler executes
    - Add data to request.state for downstream handlers

    Example:
        class TimingMiddleware:
            async def __call__(
                self,
                request: Request,
                call_next: CallNext
            ) -> Response:
                start = time.time()
                request.state["start_time"] = start

                response = await call_next(request)

                elapsed = time.time() - start
                response.headers["X-Response-Time"] = f"{elapsed:.3f}s"
                return response
    """

    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        ...


# Type alias for call_next function
CallNext = Callable[[Request], Awaitable[Response]]

# Type alias for middleware (class, function, or wrapped Django middleware)
MiddlewareType = Union[
    Middleware,
    Callable[[Request, CallNext], Awaitable[Response]],
    "DjangoMiddleware",
]
```

### 6.2 Base Middleware Class

```python
from abc import ABC, abstractmethod
from typing import Optional, Set, Pattern
import re


class BaseMiddleware(ABC):
    """
    Base class for Django-Bolt middleware with common functionality.

    Provides:
    - Path exclusion patterns
    - Method filtering
    - Scope control (global, scoped, local)

    Example:
        class AuthMiddleware(BaseMiddleware):
            exclude_paths = ["/health", "/metrics", "/docs/*"]
            exclude_methods = ["OPTIONS"]

            async def handle(self, request: Request, call_next: CallNext) -> Response:
                if not request.headers.get("authorization"):
                    raise HTTPException(401, "Unauthorized")
                return await call_next(request)
    """

    # Paths to exclude from this middleware (supports wildcards)
    exclude_paths: Optional[list[str]] = None

    # HTTP methods to exclude
    exclude_methods: Optional[list[str]] = None

    # Middleware scope
    scope: "MiddlewareScope" = "local"

    _exclude_pattern: Optional[Pattern] = None

    def __init__(self):
        if self.exclude_paths:
            # Convert glob patterns to regex
            patterns = []
            for path in self.exclude_paths:
                pattern = path.replace("*", ".*").replace("?", ".")
                patterns.append(f"^{pattern}$")
            self._exclude_pattern = re.compile("|".join(patterns))

    async def __call__(
        self,
        request: Request,
        call_next: CallNext
    ) -> Response:
        # Check exclusions
        if self._should_skip(request):
            return await call_next(request)

        return await self.handle(request, call_next)

    def _should_skip(self, request: Request) -> bool:
        """Check if this request should skip the middleware."""
        # Check method exclusion
        if self.exclude_methods and request.method in self.exclude_methods:
            return True

        # Check path exclusion
        if self._exclude_pattern and self._exclude_pattern.match(request.path):
            return True

        return False

    @abstractmethod
    async def handle(
        self,
        request: Request,
        call_next: CallNext
    ) -> Response:
        """
        Handle the request. Override this in subclasses.

        Args:
            request: The incoming request
            call_next: Function to call the next middleware/handler

        Returns:
            Response object
        """
        ...


# Middleware scope types
from typing import Literal
MiddlewareScope = Literal["global", "scoped", "local"]
```

### 6.3 Built-in Middleware Examples

```python
import time
import uuid
from typing import Optional


class TimingMiddleware(BaseMiddleware):
    """
    Adds request timing information.

    Adds to request.state:
        - request_id: Unique request identifier
        - start_time: Request start timestamp

    Adds response headers:
        - X-Request-ID: Request identifier
        - X-Response-Time: Time taken in seconds
    """

    async def handle(self, request: Request, call_next: CallNext) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        request.state["request_id"] = request_id
        request.state["start_time"] = start_time

        response = await call_next(request)

        elapsed = time.perf_counter() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{elapsed:.4f}s"

        return response


class LoggingMiddleware(BaseMiddleware):
    """
    Logs request and response information.

    Configurable log levels and formats.
    """

    exclude_paths = ["/health", "/metrics"]

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        log_body: bool = False,
        log_headers: bool = False
    ):
        super().__init__()
        self.logger = logger or logging.getLogger("django_bolt.requests")
        self.log_body = log_body
        self.log_headers = log_headers

    async def handle(self, request: Request, call_next: CallNext) -> Response:
        # Log request
        log_data = {
            "method": request.method,
            "path": request.path,
            "query": request.query,
        }
        if self.log_headers:
            log_data["headers"] = dict(request.headers)
        if self.log_body and request.body:
            log_data["body_size"] = len(request.body)

        self.logger.info(f"Request: {log_data}")

        # Process request
        response = await call_next(request)

        # Log response
        self.logger.info(f"Response: {response.status_code} for {request.method} {request.path}")

        return response


class ErrorHandlerMiddleware(BaseMiddleware):
    """
    Global error handler middleware.

    Catches exceptions and converts them to appropriate HTTP responses.
    Should be one of the first middleware in the chain.
    """

    scope = "global"

    def __init__(self, debug: bool = False):
        super().__init__()
        self.debug = debug

    async def handle(self, request: Request, call_next: CallNext) -> Response:
        try:
            return await call_next(request)
        except HTTPException:
            raise  # Let HTTP exceptions pass through
        except Exception as e:
            self.logger.exception(f"Unhandled exception: {e}")

            if self.debug:
                import traceback
                detail = traceback.format_exc()
            else:
                detail = "Internal Server Error"

            raise HTTPException(500, detail)
```

---

## 7. Django Middleware Compatibility

### 7.1 Django Middleware Adapter

```python
from typing import Any, Callable, Optional, Type, Union
from django.http import HttpRequest, HttpResponse
from django.utils.module_loading import import_string
import asyncio
import inspect


class DjangoMiddleware:
    """
    Wraps a Django middleware class to work with Django-Bolt.

    Supports both old-style (process_request/process_response) and
    new-style (callable) Django middleware patterns.

    Examples:
        # Wrap Django's built-in middleware
        from django.contrib.auth.middleware import AuthenticationMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware

        api = BoltAPI(
            middleware=[
                DjangoMiddleware(SessionMiddleware),
                DjangoMiddleware(AuthenticationMiddleware),
            ]
        )

        # Wrap by import path string
        api = BoltAPI(
            middleware=[
                DjangoMiddleware("django.contrib.sessions.middleware.SessionMiddleware"),
                DjangoMiddleware("myapp.middleware.CustomMiddleware"),
            ]
        )

    Note:
        Order matters! Django middlewares should be in the same order as
        they would be in Django's MIDDLEWARE setting.
    """

    def __init__(
        self,
        middleware_class: Union[Type, str],
        **init_kwargs: Any
    ):
        """
        Initialize the Django middleware wrapper.

        Args:
            middleware_class: Django middleware class or import path string
            **init_kwargs: Additional kwargs passed to middleware __init__
        """
        if isinstance(middleware_class, str):
            middleware_class = import_string(middleware_class)

        self.middleware_class = middleware_class
        self.init_kwargs = init_kwargs
        self._middleware_instance: Optional[Any] = None

    async def __call__(
        self,
        request: Request,
        call_next: CallNext
    ) -> Response:
        """Process request through the Django middleware."""

        # Convert Bolt request to Django HttpRequest
        django_request = self._to_django_request(request)

        # Create or get middleware instance
        middleware = self._get_middleware_instance(call_next, request)

        # Check for old-style process_request
        if hasattr(middleware, 'process_request'):
            result = await self._maybe_await(
                middleware.process_request(django_request)
            )
            if result is not None:
                # Middleware returned a response, short-circuit
                return self._to_bolt_response(result)

        # Check for process_view (called right before view)
        if hasattr(middleware, 'process_view'):
            result = await self._maybe_await(
                middleware.process_view(django_request, None, (), {})
            )
            if result is not None:
                return self._to_bolt_response(result)

        # Call the next middleware/handler
        try:
            response = await call_next(request)
        except Exception as exc:
            # Check for process_exception
            if hasattr(middleware, 'process_exception'):
                result = await self._maybe_await(
                    middleware.process_exception(django_request, exc)
                )
                if result is not None:
                    return self._to_bolt_response(result)
            raise

        # Sync any attributes Django middleware added to request
        self._sync_request_attributes(django_request, request)

        # Convert response to Django HttpResponse for process_response
        django_response = self._to_django_response(response)

        # Check for process_response
        if hasattr(middleware, 'process_response'):
            django_response = await self._maybe_await(
                middleware.process_response(django_request, django_response)
            )

        # Convert back to Bolt response
        return self._to_bolt_response(django_response)

    def _get_middleware_instance(
        self,
        call_next: CallNext,
        request: Request
    ) -> Any:
        """Get or create middleware instance with get_response callable."""

        # Create a synchronous get_response for Django middleware
        def get_response(django_request: HttpRequest) -> HttpResponse:
            # This is called by new-style middleware
            # We need to run the async chain synchronously
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create a future and run in executor
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(
                        asyncio.run,
                        call_next(request)
                    )
                    bolt_response = future.result()
            else:
                bolt_response = loop.run_until_complete(call_next(request))

            return self._to_django_response(bolt_response)

        # Async version for async-capable middleware
        async def aget_response(django_request: HttpRequest) -> HttpResponse:
            bolt_response = await call_next(request)
            return self._to_django_response(bolt_response)

        # Create middleware instance
        return self.middleware_class(get_response, **self.init_kwargs)

    def _to_django_request(self, request: Request) -> HttpRequest:
        """Convert Bolt Request to Django HttpRequest."""
        django_request = HttpRequest()

        # Copy basic attributes
        django_request.method = request.method
        django_request.path = request.path
        django_request.path_info = request.path
        django_request.META = self._build_meta(request)
        django_request.COOKIES = request.cookies.copy()
        django_request.GET = QueryDict(mutable=True)
        django_request.POST = QueryDict(mutable=True)

        # Populate GET params
        for key, value in request.query.items():
            django_request.GET[key] = value

        # Store body for lazy parsing
        django_request._body = request.body
        django_request._stream = io.BytesIO(request.body)

        # Store reference to Bolt request
        django_request._bolt_request = request

        return django_request

    def _build_meta(self, request: Request) -> dict:
        """Build Django META dict from Bolt request headers."""
        meta = {
            "REQUEST_METHOD": request.method,
            "PATH_INFO": request.path,
            "QUERY_STRING": "&".join(f"{k}={v}" for k, v in request.query.items()),
            "CONTENT_TYPE": request.headers.get("content-type", ""),
            "CONTENT_LENGTH": request.headers.get("content-length", ""),
        }

        # Convert headers to META format
        for key, value in request.headers.items():
            meta_key = f"HTTP_{key.upper().replace('-', '_')}"
            meta[meta_key] = value

        return meta

    def _sync_request_attributes(
        self,
        django_request: HttpRequest,
        bolt_request: Request
    ) -> None:
        """
        Sync attributes added by Django middleware to Bolt request.

        Django middlewares commonly add:
        - request.user (AuthenticationMiddleware)
        - request.session (SessionMiddleware)
        - request.csrf_processing_done (CsrfViewMiddleware)
        """
        # Sync user
        if hasattr(django_request, 'user'):
            bolt_request.user = django_request.user



        # Sync session
        if hasattr(django_request, 'session'):
            bolt_request._state["_django_session"] = django_request.session

        # Sync CSRF token
        if hasattr(django_request, 'META') and 'CSRF_COOKIE' in django_request.META:
            bolt_request._state["_csrf_token"] = django_request.META['CSRF_COOKIE']

        # Sync any other custom attributes
        standard_attrs = {
            'method', 'path', 'path_info', 'META', 'GET', 'POST',
            'COOKIES', 'FILES', 'resolver_match', '_body', '_stream',
            '_bolt_request', 'content_type', 'content_params'
        }

        for attr in dir(django_request):
            if not attr.startswith('_') and attr not in standard_attrs:
                value = getattr(django_request, attr, None)
                if value is not None and not callable(value):
                    bolt_request._state[f"_django_{attr}"] = value

    def _to_django_response(self, response: Response) -> HttpResponse:
        """Convert Bolt Response to Django HttpResponse."""
        django_response = HttpResponse(
            content=response.body,
            status=response.status_code,
            content_type=response.headers.get("content-type", "application/json"),
        )

        for key, value in response.headers.items():
            django_response[key] = value

        return django_response

    def _to_bolt_response(self, django_response: HttpResponse) -> Response:
        """Convert Django HttpResponse to Bolt Response."""
        headers = dict(django_response.items())

        return Response(
            body=django_response.content,
            status_code=django_response.status_code,
            headers=headers,
        )

    async def _maybe_await(self, result: Any) -> Any:
        """Await result if it's a coroutine."""
        if inspect.iscoroutine(result):
            return await result
        return result
```

### 7.2 Common Django Middleware Patterns

```python
# Example: Using Django's built-in middleware with Bolt

from django_bolt import BoltAPI
from django_bolt.middleware import DjangoMiddleware

# Import Django middleware classes
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.middleware.csrf import CsrfViewMiddleware
from django.middleware.security import SecurityMiddleware
from django.middleware.common import CommonMiddleware

api = BoltAPI(
    middleware=[
        # Order matters! Same as Django's MIDDLEWARE setting
        DjangoMiddleware(SecurityMiddleware),
        DjangoMiddleware(SessionMiddleware),
        DjangoMiddleware(CommonMiddleware),
        DjangoMiddleware(CsrfViewMiddleware),
        DjangoMiddleware(AuthenticationMiddleware),
    ]
)

# Now handlers can access Django middleware features
@api.get("/profile")
async def profile(request: Request[User, None, dict]) -> dict:
    # request.user is set by AuthenticationMiddleware
    # request.session is available from SessionMiddleware
    return {
        "username": request.user.username,
        "last_login": request.session.get("last_login"),
    }


# Example: Using a custom Django middleware
class MyDjangoMiddleware:
    """A custom Django middleware."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add custom attribute
        request.custom_data = {"source": "django_middleware"}

        response = self.get_response(request)

        # Add custom header
        response["X-Custom-Header"] = "value"

        return response

api = BoltAPI(
    middleware=[
        DjangoMiddleware(MyDjangoMiddleware),
    ]
)
```

---

## 8. Hierarchical Middleware Scoping

### 8.1 Scope Levels

```python
from enum import Enum
from typing import Literal


class MiddlewareScope(str, Enum):
    """
    Middleware scope determines where middleware applies.

    GLOBAL: Applies to all routes in the application
    SCOPED: Applies to routes in current router and child routers
    LOCAL:  Applies only to the specific route it's attached to
    """
    GLOBAL = "global"
    SCOPED = "scoped"
    LOCAL = "local"
```

### 8.2 App-Level Middleware

```python
from django_bolt import BoltAPI
from django_bolt.middleware import DjangoMiddleware, TimingMiddleware

# App-level middleware runs on ALL routes
api = BoltAPI(
    middleware=[
        # Django middleware
        DjangoMiddleware(SessionMiddleware),
        DjangoMiddleware(AuthenticationMiddleware),

        # Native Bolt middleware
        TimingMiddleware(),
        LoggingMiddleware(),
    ]
)

@api.get("/")
async def index(request: Request) -> dict:
    # All app-level middleware runs before this handler
    return {"message": "Hello"}
```

### 8.3 Router-Level Middleware

```python
from django_bolt import Router

# Router with its own middleware (adds to app middleware)
admin_router = Router(
    prefix="/admin",
    middleware=[
        AdminAuthMiddleware(),  # Only runs on /admin/* routes
    ]
)

@admin_router.get("/users")
async def admin_users(request: Request) -> dict:
    # Runs: App middleware → AdminAuthMiddleware → handler
    return {"users": [...]}

# Include router in app
api.include_router(admin_router)
```

### 8.4 Route-Level Middleware

```python
from django_bolt.middleware import middleware

# Route-level middleware (most specific)
@api.get("/special")
@middleware(SpecialMiddleware(), AnotherMiddleware())
async def special_endpoint(request: Request) -> dict:
    # Runs: App middleware → SpecialMiddleware → AnotherMiddleware → handler
    return {"special": True}
```

### 8.5 Middleware Inheritance

```python
"""
Middleware execution order (outer to inner):

1. App-level middleware (in order defined)
2. Router-level middleware (inherited from parent routers)
3. Route-level middleware (in order defined)
4. Handler

Response flows back in reverse order.
"""

# Example hierarchy
api = BoltAPI(
    middleware=[M1(), M2()]  # App level
)

router_a = Router(
    prefix="/a",
    middleware=[M3()]  # Router level
)

router_b = Router(
    prefix="/b",
    middleware=[M4()],  # Nested router level
    parent=router_a
)

@router_b.get("/endpoint")
@middleware(M5())  # Route level
async def handler(request: Request):
    pass

# Execution order for GET /a/b/endpoint:
# M1 → M2 → M3 → M4 → M5 → handler → M5 → M4 → M3 → M2 → M1
```

### 8.6 Middleware Skip/Override

```python
from django_bolt.middleware import skip_middleware, override_middleware

# Skip specific middleware for a route
@api.get("/health")
@skip_middleware(TimingMiddleware, LoggingMiddleware)
async def health(request: Request) -> dict:
    return {"status": "ok"}

# Skip all middleware
@api.get("/raw")
@skip_middleware("*")
async def raw_endpoint(request: Request) -> dict:
    return {"raw": True}

# Override parent middleware with different config
@api.get("/custom-rate")
@override_middleware(
    RateLimitMiddleware,
    RateLimitMiddleware(rps=1000)  # Different rate limit
)
async def high_traffic(request: Request) -> dict:
    return {"data": [...]}
```

---

## 9. Rust Integration

### 9.1 Two-Layer Architecture

The middleware system operates in two layers:

1. **Rust Layer** (No GIL): Hot-path middleware that runs before Python
2. **Python Layer**: Django-compatible middleware and custom middleware

```
Request Flow:
─────────────────────────────────────────────────────────────────────
│ RUST LAYER (No GIL)                                               │
│  ├─ Rate Limiting      → 429 Too Many Requests                    │
│  ├─ CORS Preflight     → 200 OK with CORS headers                │
│  ├─ JWT Validation     → 401 Unauthorized                         │
│  └─ Permission Guards  → 403 Forbidden                            │
│                                                                    │
│ If all pass, acquire GIL and continue...                          │
─────────────────────────────────────────────────────────────────────
│ PYTHON LAYER                                                       │
│  ├─ DjangoMiddleware(SessionMiddleware)                           │
│  ├─ DjangoMiddleware(AuthenticationMiddleware)                    │
│  ├─ TimingMiddleware                                              │
│  └─ Handler                                                        │
─────────────────────────────────────────────────────────────────────
```

### 9.2 Rust-Accelerated Middleware

Existing decorators continue to work and compile to Rust:

```python
from django_bolt.middleware import cors, rate_limit

@api.get("/fast")
@cors(origins=["https://example.com"])  # Handled in Rust
@rate_limit(rps=1000)                    # Handled in Rust
async def fast_endpoint(request: Request) -> dict:
    return {"fast": True}
```

### 9.3 Metadata Compilation

```python
# At startup, middleware is compiled to metadata for Rust
def compile_middleware_metadata(route) -> dict:
    """Compile middleware to Rust-compatible metadata."""
    return {
        # Rust-handled middleware
        "cors": route.cors_config,
        "rate_limit": route.rate_limit_config,
        "auth_backends": route.auth_backends,
        "guards": route.guards,

        # Python middleware (list of callables to run)
        "python_middleware": route.python_middleware,

        # Optimization flags
        "needs_body": route.needs_body,
        "needs_headers": route.needs_headers,
        "needs_cookies": route.needs_cookies,
    }
```

---

## 10. API Reference

### 10.1 BoltAPI Configuration

```python
from django_bolt import BoltAPI
from django_bolt.middleware import DjangoMiddleware

api = BoltAPI(
    # App-level middleware (runs on all routes)
    middleware=[
        DjangoMiddleware(SessionMiddleware),
        DjangoMiddleware(AuthenticationMiddleware),
        TimingMiddleware(),
    ],

    # Default authentication (can be overridden per-route)
    auth=[JWTAuthentication(secret="...")],

    # Default guards (can be overridden per-route)
    guards=[IsAuthenticated()],

    # Global CORS config (Rust-handled)
    cors=CORSConfig(
        origins=["https://example.com"],
        credentials=True,
    ),

    # Global rate limiting (Rust-handled)
    rate_limit=RateLimitConfig(
        rps=1000,
        burst=100,
    ),
)
```

### 10.2 Router Configuration

```python
from django_bolt import Router

router = Router(
    prefix="/api/v1",

    # Router-level middleware (adds to app middleware)
    middleware=[
        APIVersionMiddleware(version="1"),
    ],

    # Router-level auth (overrides app default for this router)
    auth=[APIKeyAuthentication()],

    # Tags for OpenAPI
    tags=["v1"],
)

api.include_router(router)
```

### 10.3 Route Decorators

```python
from django_bolt.middleware import middleware, skip_middleware
from django_bolt.auth import JWTAuthentication
from django_bolt.guards import IsAuthenticated, HasPermission

@api.get(
    "/users/{user_id}",

    # Route-level auth
    auth=[JWTAuthentication()],

    # Route-level guards
    guards=[IsAuthenticated(), HasPermission("users.view")],

    # OpenAPI metadata
    summary="Get user by ID",
    tags=["users"],
)
@middleware(AuditLogMiddleware())  # Route-level middleware
async def get_user(
    request: Request[User, JWTClaims, dict],
    user_id: int
) -> UserResponse:
    user = await User.objects.aget(id=user_id)
    return UserResponse.from_orm(user)
```

### 10.4 Middleware Decorator

```python
from django_bolt.middleware import middleware

# Multiple middleware on a route
@api.post("/upload")
@middleware(
    ValidateContentTypeMiddleware(allowed=["multipart/form-data"]),
    FileSizeLimitMiddleware(max_size=10 * 1024 * 1024),
    VirusScanMiddleware(),
)
async def upload_file(request: Request) -> dict:
    return {"uploaded": True}
```

---

## 11. Migration Guide

### 11.1 From Current Django-Bolt

```python
# Before (current)
@api.get("/users", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_users(request: dict) -> list:
    return [...]

# After (new)
@api.get("/users", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def get_users(request: Request[User, JWTClaims, dict]) -> list:
    # Now with full type safety!
    user = request.user  # IDE knows this is User
    return [...]
```

### 11.2 From Django Views

```python
# Django view
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def get_profile(request):
    return JsonResponse({
        "username": request.user.username,
        "email": request.user.email,
    })

# Django-Bolt equivalent
from django_bolt import BoltAPI, Request
from django_bolt.middleware import DjangoMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

api = BoltAPI(
    middleware=[
        DjangoMiddleware(SessionMiddleware),
        DjangoMiddleware(AuthenticationMiddleware),
    ]
)

@api.get("/profile", guards=[IsAuthenticated()])
async def get_profile(request: Request[User, None, dict]) -> dict:
    return {
        "username": request.user.username,
        "email": request.user.email,
    }
```

### 11.3 From FastAPI

```python
# FastAPI
from fastapi import FastAPI, Depends, Request
from fastapi.middleware import Middleware

app = FastAPI(middleware=[Middleware(TimingMiddleware)])

@app.get("/users")
async def get_users(request: Request, user: User = Depends(get_current_user)):
    return {"user": user.name}

# Django-Bolt equivalent
from django_bolt import BoltAPI, Request, Depends

api = BoltAPI(middleware=[TimingMiddleware()])

@api.get("/users")
async def get_users(
    request: Request[User, JWTClaims, dict],
    user: User = Depends(get_current_user)
) -> dict:
    return {"user": user.name}
```

---

## 12. Performance Considerations

### 12.1 Middleware Overhead

| Middleware Type         | Overhead  | Location                 |
| ----------------------- | --------- | ------------------------ |
| Rust (CORS, Rate Limit) | ~1-5μs    | No GIL                   |
| Native Bolt             | ~10-50μs  | Python                   |
| Django Middleware       | ~50-200μs | Python (with conversion) |

### 12.2 Optimization Strategies

1. **Hot-path in Rust**: Keep CORS, rate limiting, JWT validation in Rust
2. **Lazy conversion**: Only convert to Django HttpRequest when needed
3. **Metadata compilation**: Compile middleware config once at startup
4. **Skip unnecessary middleware**: Use `@skip_middleware` for hot paths

### 12.3 Benchmarks

Target performance with full middleware stack:

| Configuration         | RPS    | p99 Latency |
| --------------------- | ------ | ----------- |
| No middleware         | 65,000 | 2ms         |
| Rust middleware only  | 60,000 | 3ms         |
| + 2 Bolt middleware   | 45,000 | 5ms         |
| + 3 Django middleware | 25,000 | 10ms        |

---

## 13. Implementation Plan

### Phase 1: Core Request Object (Week 1-2)

1. Create `Request[UserT, AuthT, StateT]` generic class
2. Create `State[StateT]` wrapper class
3. Add type aliases (`JWTClaims`, `AuthenticatedRequest`, etc.)
4. Update Rust `PyRequest` to support new structure
5. Unit tests for type safety

### Phase 2: Middleware Protocol (Week 2-3)

1. Define `Middleware` protocol
2. Create `BaseMiddleware` class with exclusion patterns
3. Implement built-in middleware (Timing, Logging, ErrorHandler)
4. Add `@middleware` decorator for routes
5. Integration tests

### Phase 3: Django Compatibility (Week 3-4)

1. Implement `DjangoMiddleware` adapter
2. Test with SessionMiddleware, AuthenticationMiddleware
3. Test with CsrfViewMiddleware
4. Test with custom Django middlewares
5. Handle async Django middleware

### Phase 4: Hierarchical Scoping (Week 4-5)

1. Add middleware support to `Router`
2. Implement middleware inheritance
3. Add `@skip_middleware` decorator
4. Add `@override_middleware` decorator
5. Integration tests for complex hierarchies

### Phase 5: Rust Integration (Week 5-6)

1. Update metadata compiler for new structure
2. Ensure existing `@cors`, `@rate_limit` work
3. Update `src/handler.rs` for Python middleware layer
4. Performance optimization
5. Benchmarks

### Phase 6: Documentation & Migration (Week 6-7)

1. Update `docs/MIDDLEWARE.md`
2. Write migration guide
3. Update API documentation
4. Add examples
5. Release notes

---

## Appendix A: Full Example Application

```python
"""
Complete example showing all middleware features.
"""
from __future__ import annotations
from typing import TypedDict

from django_bolt import BoltAPI, Router, Request, Depends
from django_bolt.middleware import (
    DjangoMiddleware,
    BaseMiddleware,
    middleware,
    skip_middleware,
)
from django_bolt.auth import JWTAuthentication
from django_bolt.guards import IsAuthenticated, HasPermission
from django_bolt.types import JWTClaims

from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from myapp.models import User


# ═══════════════════════════════════════════════════════════════════════════
# Custom State Types
# ═══════════════════════════════════════════════════════════════════════════

class AppState(TypedDict, total=False):
    request_id: str
    start_time: float
    trace_id: str


# ═══════════════════════════════════════════════════════════════════════════
# Custom Middleware
# ═══════════════════════════════════════════════════════════════════════════

class TracingMiddleware(BaseMiddleware):
    """Adds distributed tracing headers."""

    async def handle(self, request: Request, call_next) -> Response:
        trace_id = request.headers.get("x-trace-id") or str(uuid4())
        request.state["trace_id"] = trace_id

        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id

        return response


# ═══════════════════════════════════════════════════════════════════════════
# App Configuration
# ═══════════════════════════════════════════════════════════════════════════

api = BoltAPI(
    title="My API",
    version="1.0.0",

    # Global middleware
    middleware=[
        DjangoMiddleware(SessionMiddleware),
        DjangoMiddleware(AuthenticationMiddleware),
        TracingMiddleware(),
    ],

    # Default auth
    auth=[JWTAuthentication(secret="my-secret")],
)


# ═══════════════════════════════════════════════════════════════════════════
# API Router
# ═══════════════════════════════════════════════════════════════════════════

api_router = Router(
    prefix="/api/v1",
    tags=["api"],
)


# ═══════════════════════════════════════════════════════════════════════════
# Public Endpoints
# ═══════════════════════════════════════════════════════════════════════════

@api.get("/health")
@skip_middleware("*")  # No middleware for health checks
async def health(request: Request) -> dict:
    return {"status": "ok"}


@api.post("/auth/login", guards=[])  # No auth required
async def login(request: Request, credentials: LoginRequest) -> TokenResponse:
    user = await authenticate(credentials)
    token = create_jwt(user)
    return TokenResponse(access_token=token)


# ═══════════════════════════════════════════════════════════════════════════
# Protected Endpoints
# ═══════════════════════════════════════════════════════════════════════════

@api_router.get("/me")
async def get_me(request: Request[User, JWTClaims, AppState]) -> UserResponse:
    # Full type safety!
    return UserResponse(
        id=request.user.id,
        username=request.user.username,
        email=request.user.email,
        trace_id=request.state.trace_id,  # IDE autocomplete works
    )


@api_router.get("/users", guards=[HasPermission("users.list")])
async def list_users(request: Request[User, JWTClaims, AppState]) -> list[UserResponse]:
    users = await User.objects.all()
    return [UserResponse.from_orm(u) for u in users]


@api_router.get("/users/{user_id}")
@middleware(AuditLogMiddleware())  # Additional route-level middleware
async def get_user(
    request: Request[User, JWTClaims, AppState],
    user_id: int
) -> UserResponse:
    user = await User.objects.aget(id=user_id)
    return UserResponse.from_orm(user)


# ═══════════════════════════════════════════════════════════════════════════
# Include Router
# ═══════════════════════════════════════════════════════════════════════════

api.include_router(api_router)


# ═══════════════════════════════════════════════════════════════════════════
# Run Server
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # python manage.py runbolt --host 0.0.0.0 --port 8000
    pass
```

---

## Appendix B: Type Safety Verification

```python
"""
Examples showing type checker behavior.
"""
from django_bolt import Request
from django_bolt.types import JWTClaims
from myapp.models import User

# ✓ Correct usage - type checker passes
@api.get("/correct")
async def correct(request: Request[User, JWTClaims, dict]) -> dict:
    username: str = request.user.username  # ✓ User has username
    exp: int = request.auth["exp"]          # ✓ JWTClaims has exp
    return {"username": username}

# ✗ Incorrect usage - type checker catches error
@api.get("/incorrect")
async def incorrect(request: Request[User, JWTClaims, dict]) -> dict:
    foo: str = request.user.foo  # ✗ Error: User has no attribute 'foo'
    bar: str = request.auth["bar"]  # ✗ Error: 'bar' not in JWTClaims
    return {}

# ✓ Custom state type
class MyState(TypedDict):
    request_id: str

@api.get("/custom-state")
async def custom_state(request: Request[User, JWTClaims, MyState]) -> dict:
    rid: str = request.state.request_id  # ✓ MyState has request_id
    return {"request_id": rid}
```

---

**End of Design Document**

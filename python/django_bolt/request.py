"""
Type-safe Request object for Django-Bolt.

This module provides the generic Request[UserT, AuthT, StateT] class that serves
as the context container for middleware data, following Django's pattern where
middleware adds attributes to the request.

Performance is critical - all hot-path operations are optimized:
- __slots__ for memory efficiency
- Lazy loading of user objects
- Minimal attribute access overhead
- Zero-copy where possible
"""
from __future__ import annotations

from typing import (
    TypeVar,
    Generic,
    Optional,
    Any,
    Dict,
    Iterator,
    TYPE_CHECKING,
    Union,
    overload,
)

if TYPE_CHECKING:
    from django.http import HttpRequest


# Type variables with defaults for backward compatibility
# These provide IDE autocomplete and type safety
UserT = TypeVar("UserT")
AuthT = TypeVar("AuthT")
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

    Performance:
        - Uses __slots__ for memory efficiency
        - Direct dict access with minimal overhead
        - No copying of data
    """

    __slots__ = ("_data",)

    def __init__(self, data: Dict[str, Any]) -> None:
        object.__setattr__(self, "_data", data)

    # ═══════════════════════════════════════════════════════════════════════
    # Dict-Style Access (hot path - optimized)
    # ═══════════════════════════════════════════════════════════════════════

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __contains__(self, key: object) -> bool:
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

    def pop(self, key: str, *args) -> Any:
        return self._data.pop(key, *args)

    def update(self, other: Dict[str, Any] = None, **kwargs) -> None:
        if other:
            self._data.update(other)
        if kwargs:
            self._data.update(kwargs)

    def setdefault(self, key: str, default: Any = None) -> Any:
        return self._data.setdefault(key, default)

    def clear(self) -> None:
        self._data.clear()

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

    def __bool__(self) -> bool:
        return bool(self._data)


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

    Performance:
        - Uses __slots__ for memory efficiency (no __dict__)
        - Lazy loading of user objects (zero queries if not accessed)
        - Properties use direct attribute access
        - State wrapper is created on-demand
    """

    __slots__ = (
        "method",
        "path",
        "body",
        "headers",
        "cookies",
        "query",
        "params",
        "_user",
        "_auth",
        "_state",
        "_django_request",
        "_state_wrapper",
    )

    def __init__(
        self,
        method: str = "GET",
        path: str = "/",
        body: bytes = b"",
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        query: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        user: Optional[UserT] = None,
        auth: Optional[AuthT] = None,
        state: Optional[Dict[str, Any]] = None,
        django_request: Optional["HttpRequest"] = None,
    ) -> None:
        # ═══════════════════════════════════════════════════════════════════
        # Core HTTP Data (always available, always typed)
        # ═══════════════════════════════════════════════════════════════════
        self.method = method
        self.path = path
        self.body = body
        self.headers = headers if headers is not None else {}
        self.cookies = cookies if cookies is not None else {}
        self.query = query if query is not None else {}
        self.params = params if params is not None else {}

        # ═══════════════════════════════════════════════════════════════════
        # Middleware-Provided Data (typed via generics)
        # ═══════════════════════════════════════════════════════════════════
        self._user: Optional[UserT] = user
        self._auth: Optional[AuthT] = auth
        self._state: Dict[str, Any] = state if state is not None else {}

        # ═══════════════════════════════════════════════════════════════════
        # Django Compatibility
        # ═══════════════════════════════════════════════════════════════════
        self._django_request: Optional["HttpRequest"] = django_request
        self._state_wrapper: Optional[State] = None

    # ═══════════════════════════════════════════════════════════════════════
    # Middleware-Provided Properties (typed via generics)
    # ═══════════════════════════════════════════════════════════════════════

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
    def context(self) -> AuthT:
        """Alias for auth (backwards compatibility)."""
        return self.auth

    @context.setter
    def context(self, value: AuthT) -> None:
        """Set the auth context (backwards compatibility)."""
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
        # Lazy create state wrapper to avoid allocation if not used
        if self._state_wrapper is None:
            self._state_wrapper = State(self._state)
        return self._state_wrapper

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

    @property
    def django_request(self) -> Optional["HttpRequest"]:
        """
        Original Django HttpRequest if available.

        Useful for accessing Django-specific features not exposed
        by the Bolt request interface.

        Returns:
            Django HttpRequest or None
        """
        return self._django_request

    # ═══════════════════════════════════════════════════════════════════════
    # User availability check (avoids exception)
    # ═══════════════════════════════════════════════════════════════════════

    def has_user(self) -> bool:
        """Check if a user is available without raising an exception."""
        return self._user is not None

    def has_auth(self) -> bool:
        """Check if auth context is available without raising an exception."""
        return self._auth is not None

    def get_user(self, default: Any = None) -> Union[UserT, Any]:
        """Get user or return default if not available."""
        return self._user if self._user is not None else default

    def get_auth(self, default: Any = None) -> Union[AuthT, Any]:
        """Get auth context or return default if not available."""
        return self._auth if self._auth is not None else default

    # ═══════════════════════════════════════════════════════════════════════
    # Dict-Style Access (backwards compatibility)
    # ═══════════════════════════════════════════════════════════════════════

    @overload
    def get(self, key: str) -> Any: ...

    @overload
    def get(self, key: str, default: Any) -> Any: ...

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-style get for backwards compatibility."""
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key: str) -> Any:
        """Dict-style access for backwards compatibility."""
        if key == "method":
            return self.method
        elif key == "path":
            return self.path
        elif key == "body":
            return self.body
        elif key == "headers":
            return self.headers
        elif key == "cookies":
            return self.cookies
        elif key == "query":
            return self.query
        elif key == "params":
            return self.params
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
        elif key == "method":
            self.method = value
        elif key == "path":
            self.path = value
        elif key == "body":
            self.body = value
        elif key == "headers":
            self.headers = value
        elif key == "cookies":
            self.cookies = value
        elif key == "query":
            self.query = value
        elif key == "params":
            self.params = value
        else:
            self._state[key] = value

    def __contains__(self, key: object) -> bool:
        """Support 'in' operator for backwards compatibility."""
        return key in (
            "method", "path", "body", "headers", "cookies",
            "query", "params", "user", "auth", "context", "state"
        ) or key in self._state

    def __repr__(self) -> str:
        return (
            f"Request(method={self.method!r}, path={self.path!r}, "
            f"has_user={self._user is not None}, has_auth={self._auth is not None})"
        )

    # ═══════════════════════════════════════════════════════════════════════
    # Factory Methods (for internal use)
    # ═══════════════════════════════════════════════════════════════════════

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Request":
        """
        Create a Request from a dictionary (e.g., from Rust PyRequest).

        This is used internally to convert from the Rust-backed request
        to the Python Request object for middleware processing.
        """
        return cls(
            method=data.get("method", "GET"),
            path=data.get("path", "/"),
            body=data.get("body", b""),
            headers=data.get("headers", {}),
            cookies=data.get("cookies", {}),
            query=data.get("query", {}),
            params=data.get("params", {}),
            user=data.get("user"),
            auth=data.get("auth") or data.get("context"),
            state=data.get("state", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Request to a dictionary (for passing back to Rust).

        This preserves all data including middleware-added state.
        """
        return {
            "method": self.method,
            "path": self.path,
            "body": self.body,
            "headers": self.headers,
            "cookies": self.cookies,
            "query": self.query,
            "params": self.params,
            "user": self._user,
            "auth": self._auth,
            "context": self._auth,  # alias
            "state": self._state,
        }


# Type alias for call_next function used in middleware
CallNext = Any  # Callable[[Request], Awaitable[Response]]


__all__ = [
    "Request",
    "State",
    "UserT",
    "AuthT",
    "StateT",
    "CallNext",
]

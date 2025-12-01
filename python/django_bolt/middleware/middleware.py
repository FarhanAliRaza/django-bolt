"""
Middleware system for Django-Bolt.

Provides both decorator-based and class-based middleware approaches.
Middleware can be applied globally to all routes or selectively to specific routes.
"""

import warnings
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Union


class Middleware(ABC):
    """Base class for middleware implementations."""

    @abstractmethod
    async def process_request(self, request: Any, call_next: Callable) -> Any:
        """
        Process the request and optionally call the next middleware/handler.

        Args:
            request: The incoming request object
            call_next: Callable to invoke the next middleware or handler

        Returns:
            Response object or result from call_next
        """


class MiddlewareGroup:
    """Groups multiple middleware for reuse across routes."""

    def __init__(self, *middleware: Union[Middleware, "MiddlewareConfig"]):
        self.middleware = list(middleware)

    def __add__(self, other: "MiddlewareGroup") -> "MiddlewareGroup":
        """Combine middleware groups."""
        return MiddlewareGroup(*(self.middleware + other.middleware))


@dataclass
class MiddlewareConfig:
    """Configuration for a middleware instance with metadata."""

    middleware: Union[type, Middleware]
    config: dict[str, Any] = field(default_factory=dict)
    skip_routes: set[str] = field(default_factory=set)
    only_routes: set[str] | None = None

    def applies_to_route(self, route_key: str) -> bool:
        """Check if middleware should apply to a specific route."""
        if route_key in self.skip_routes:
            return False
        return not (self.only_routes is not None and route_key not in self.only_routes)


def middleware(*args, **kwargs):
    """
    Decorator to attach middleware to a route handler.

    Can be used as:
    - @middleware(RateLimitMiddleware(rps=100))
    - @middleware(cors={"origins": ["*"]})
    - @middleware(skip=["auth"])
    """

    def decorator(func):
        if not hasattr(func, "__bolt_middleware__"):
            func.__bolt_middleware__ = []

        for arg in args:
            if isinstance(arg, (Middleware, MiddlewareConfig, type)):
                func.__bolt_middleware__.append(arg)
            elif isinstance(arg, MiddlewareGroup):
                func.__bolt_middleware__.extend(arg.middleware)

        if kwargs:
            func.__bolt_middleware__.append(kwargs)

        return func

    # Support both @middleware and @middleware()
    if (
        len(args) == 1
        and callable(args[0])
        and not isinstance(args[0], (Middleware, type))
    ):
        return decorator(args[0])
    return decorator


def rate_limit(rps: int = 100, burst: int | None = None, key: str = "ip"):
    """
    Rate limiting decorator.

    Args:
        rps: Requests per second limit
        burst: Burst capacity (defaults to 2x rps)
        key: Rate limit key strategy ("ip", "user", "api_key", or header name)
    """

    def decorator(func):
        if not hasattr(func, "__bolt_middleware__"):
            func.__bolt_middleware__ = []
        func.__bolt_middleware__.append(
            {"type": "rate_limit", "rps": rps, "burst": burst or rps * 2, "key": key}
        )
        return func

    return decorator


def cors(
    origins: Union[list[str], str] | None = None,
    methods: list[str] | None = None,
    headers: list[str] | None = None,
    credentials: bool = False,
    max_age: int = 3600,
):
    """
    CORS configuration decorator for route-level CORS configuration.

    Args:
        origins: Allowed origins (REQUIRED). Use ["*"] for all origins, or specific origins
                 like ["https://example.com"]. For global config, use Django settings instead.
        methods: Allowed methods (default: GET, POST, PUT, PATCH, DELETE, OPTIONS)
        headers: Allowed headers
        credentials: Allow credentials (cannot be combined with wildcard "*")
        max_age: Preflight cache duration in seconds (default: 3600)

    Examples:
        @cors(origins=["https://example.com"])
        async def my_endpoint(): ...

        @cors(origins=["*"])  # Allow all origins
        async def public_endpoint(): ...

        @cors(origins=["https://app.example.com"], credentials=True)
        async def with_cookies(): ...

    Note:
        If you want to use global CORS settings from Django (CORS_ALLOWED_ORIGINS),
        do NOT use the @cors decorator - the global config will apply automatically.
        The @cors decorator is for route-specific CORS overrides only.

    Raises:
        ValueError: If origins is not specified (empty @cors() is not allowed)
    """

    def decorator(func):
        # SECURITY: Require explicit origins - empty @cors() is a common mistake
        if origins is None:
            raise ValueError(
                "@cors() requires 'origins' argument. Examples:\n"
                "  @cors(origins=['https://example.com'])  # Specific origin\n"
                "  @cors(origins=['*'])  # Allow all origins\n"
                "\n"
                "If you want to use global CORS settings from Django (CORS_ALLOWED_ORIGINS),\n"
                "simply remove the @cors decorator - global config applies automatically."
            )

        if not hasattr(func, "__bolt_middleware__"):
            func.__bolt_middleware__ = []

        # Parse origins
        origin_list = origins if isinstance(origins, list) else [origins]

        # SECURITY: Validate wildcard + credentials
        if "*" in origin_list and credentials:
            warnings.warn(
                "CORS misconfiguration: Cannot use wildcard '*' with credentials=True. "
                "This violates the CORS specification. Please specify explicit origins.",
                RuntimeWarning,
                stacklevel=2,
            )

        func.__bolt_middleware__.append(
            {
                "type": "cors",
                "origins": origin_list,
                "methods": methods
                or ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "headers": headers,
                "credentials": credentials,
                "max_age": max_age,
            }
        )
        return func

    return decorator


def skip_middleware(*middleware_names: str):
    """
    Skip specific global middleware for this route.

    Args:
        middleware_names: Names of middleware to skip (e.g., "cors", "rate_limit", "compression")

    Examples:
        @api.get("/no-compression")
        @skip_middleware("compression")
        async def no_compress():
            return {"data": "large response without compression"}

        @api.get("/minimal")
        @skip_middleware("cors", "compression")
        async def minimal():
            return {"fast": True}
    """

    def decorator(func):
        if not hasattr(func, "__bolt_skip_middleware__"):
            func.__bolt_skip_middleware__ = set()
        func.__bolt_skip_middleware__.update(middleware_names)
        return func

    return decorator


def no_compress(func):
    """
    Disable compression for this route.

    Shorthand for @skip_middleware("compression").

    Examples:
        @api.get("/stream")
        @no_compress
        async def stream_data():
            # Compression would slow down streaming
            return StreamingResponse(...)
    """
    return skip_middleware("compression")(func)


class CORSMiddleware(Middleware):
    """Built-in CORS middleware implementation."""

    def __init__(
        self,
        origins: list[str] | None = None,
        methods: list[str] | None = None,
        headers: list[str] | None = None,
        credentials: bool = False,
        max_age: int = 3600,
    ):
        self.origins = origins or ["*"]
        self.methods = methods or ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
        self.headers = headers or ["Content-Type", "Authorization"]
        self.credentials = credentials
        self.max_age = max_age

    async def process_request(self, request: Any, call_next: Callable) -> Any:
        # This will be handled in Rust for performance
        # Python implementation is for compatibility
        response = await call_next(request)
        return response


class RateLimitMiddleware(Middleware):
    """Built-in rate limiting middleware implementation."""

    def __init__(self, rps: int = 100, burst: int | None = None, key: str = "ip"):
        self.rps = rps
        self.burst = burst or rps * 2
        self.key = key

    async def process_request(self, request: Any, call_next: Callable) -> Any:
        # This will be handled in Rust for performance
        # Python implementation is for compatibility/fallback
        response = await call_next(request)
        return response

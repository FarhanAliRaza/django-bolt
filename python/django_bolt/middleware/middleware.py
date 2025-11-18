"""
Middleware system for Django-Bolt.

Provides both decorator-based and class-based middleware approaches.
Middleware can be applied globally to all routes or selectively to specific routes.
"""

import inspect
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Union


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
        pass


class MiddlewareGroup:
    """Groups multiple middleware for reuse across routes."""
    
    def __init__(self, *middleware: Union[Middleware, 'MiddlewareConfig']):
        self.middleware = list(middleware)
    
    def __add__(self, other: 'MiddlewareGroup') -> 'MiddlewareGroup':
        """Combine middleware groups."""
        return MiddlewareGroup(*(self.middleware + other.middleware))


@dataclass
class MiddlewareConfig:
    """Configuration for a middleware instance with metadata."""
    
    middleware: Union[type, Middleware]
    config: Dict[str, Any] = field(default_factory=dict)
    skip_routes: Set[str] = field(default_factory=set)
    only_routes: Optional[Set[str]] = None
    
    def applies_to_route(self, route_key: str) -> bool:
        """Check if middleware should apply to a specific route."""
        if route_key in self.skip_routes:
            return False
        if self.only_routes is not None and route_key not in self.only_routes:
            return False
        return True


def middleware(*args, **kwargs):
    """
    Decorator to attach middleware to a route handler.
    
    Can be used as:
    - @middleware(RateLimitMiddleware(rps=100))
    - @middleware(cors={"origins": ["*"]})
    - @middleware(skip=["auth"])
    """
    def decorator(func):
        if not hasattr(func, '__bolt_middleware__'):
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
    if len(args) == 1 and callable(args[0]) and not isinstance(args[0], (Middleware, type)):
        return decorator(args[0])
    return decorator


def rate_limit(rps: int = 100, burst: int = None, key: str = "ip"):
    """
    Rate limiting decorator.
    
    Args:
        rps: Requests per second limit
        burst: Burst capacity (defaults to 2x rps)
        key: Rate limit key strategy ("ip", "user", "api_key", or header name)
    """
    def decorator(func):
        if not hasattr(func, '__bolt_middleware__'):
            func.__bolt_middleware__ = []
        func.__bolt_middleware__.append({
            'type': 'rate_limit',
            'rps': rps,
            'burst': burst or rps * 2,
            'key': key
        })
        return func
    return decorator


def cors(
    origins: Union[List[str], str] = None,
    methods: List[str] = None,
    headers: List[str] = None,
    credentials: bool = False,
    max_age: int = 3600
):
    """
    CORS configuration decorator.

    Args:
        origins: Allowed origins. Use Django setting BOLT_CORS_ALLOWED_ORIGINS for global config.
                 Default is empty list (no origins allowed) for security.
        methods: Allowed methods
        headers: Allowed headers
        credentials: Allow credentials (cannot be combined with wildcard "*")
        max_age: Preflight cache duration

    Security Notes:
        - Default changed from ["*"] to [] (empty) for better security
        - Wildcard "*" with credentials=True is not allowed (violates CORS spec)
        - Configure BOLT_CORS_ALLOWED_ORIGINS in Django settings for global origins
    """
    def decorator(func):
        if not hasattr(func, '__bolt_middleware__'):
            func.__bolt_middleware__ = []

        # Parse origins
        origin_list = origins if isinstance(origins, list) else [origins] if origins else []

        # SECURITY: Validate wildcard + credentials
        if "*" in origin_list and credentials:
            warnings.warn(
                "CORS misconfiguration: Cannot use wildcard '*' with credentials=True. "
                "This violates the CORS specification. Please specify explicit origins.",
                RuntimeWarning,
                stacklevel=2
            )

        func.__bolt_middleware__.append({
            'type': 'cors',
            'origins': origin_list,
            'methods': methods or ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            'headers': headers,
            'credentials': credentials,
            'max_age': max_age
        })
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
        if not hasattr(func, '__bolt_skip_middleware__'):
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
        origins: List[str] = None,
        methods: List[str] = None,
        headers: List[str] = None,
        credentials: bool = False,
        max_age: int = 3600
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
    
    def __init__(self, rps: int = 100, burst: int = None, key: str = "ip"):
        self.rps = rps
        self.burst = burst or rps * 2
        self.key = key
    
    async def process_request(self, request: Any, call_next: Callable) -> Any:
        # This will be handled in Rust for performance
        # Python implementation is for compatibility/fallback
        response = await call_next(request)
        return response



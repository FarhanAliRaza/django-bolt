"""
Django-Bolt Middleware System.

Uses Django's middleware pattern for unified syntax:
- __init__(get_response): Receives the next middleware/handler in chain
- __call__(request): Processes the request

Performance is the utmost priority - the middleware system is designed for zero overhead:
- Hot-path operations (CORS, rate limiting, JWT validation) run in Rust
- Python middleware only runs when explicitly configured
- Pattern matching compiled once at startup
- Lazy evaluation and minimal allocations

Usage:
    # Use Django's settings.MIDDLEWARE automatically
    api = BoltAPI(django_middleware=True)

    # Or with custom middleware classes (Django-style)
    api = BoltAPI(
        middleware=[
            TimingMiddleware,      # Pass class, not instance
            LoggingMiddleware,
        ]
    )

    # Or combine both - uses settings.MIDDLEWARE + custom
    api = BoltAPI(
        django_middleware=True,
        middleware=[TimingMiddleware],
    )

    # Custom middleware (Django-style pattern):
    class MyMiddleware:
        def __init__(self, get_response):
            self.get_response = get_response

        async def __call__(self, request):
            # Before request processing
            response = await self.get_response(request)
            # After request processing
            return response

    # Skip middleware
    @api.get("/health")
    @skip_middleware("*")
    async def health(request: Request) -> dict:
        return {"status": "ok"}
"""

from .compression import CompressionConfig
from .django_adapter import DjangoMiddleware, DjangoMiddlewareStack
from .django_loader import (
    DEFAULT_EXCLUDED_MIDDLEWARE,
    get_django_middleware_setting,
    load_django_middleware,
)
from .middleware import (
    BaseMiddleware,
    ErrorHandlerMiddleware,
    GetResponse,
    LoggingMiddleware,
    Middleware,
    # Protocols and base classes
    MiddlewareProtocol,
    MiddlewareType,
    # Built-in middleware (Python)
    TimingMiddleware,
    cors,
    # Decorators
    middleware,
    no_compress,
    rate_limit,
    skip_middleware,
)

__all__ = [
    # Protocols and base classes
    "MiddlewareProtocol",
    "BaseMiddleware",
    "Middleware",
    "GetResponse",
    "MiddlewareType",
    # Configuration
    "CompressionConfig",
    # Decorators
    "middleware",
    "rate_limit",
    "cors",
    "skip_middleware",
    "no_compress",
    # Built-in middleware (Python)
    "TimingMiddleware",
    "LoggingMiddleware",
    "ErrorHandlerMiddleware",
    # Django compatibility
    "DjangoMiddleware",
    "DjangoMiddlewareStack",
    "load_django_middleware",
    "get_django_middleware_setting",
    "DEFAULT_EXCLUDED_MIDDLEWARE",
]

"""
Django-Bolt Middleware System.

Provides decorators and classes for adding middleware to routes.
Middleware can be global, router-scoped, or per-route.

Performance is the utmost priority - the middleware system is designed for zero overhead:
- Hot-path operations (CORS, rate limiting, JWT validation) run in Rust
- Python middleware only runs when explicitly configured
- Pattern matching compiled once at startup
- Lazy evaluation and minimal allocations

Usage:
    # App-level middleware
    api = BoltAPI(
        middleware=[
            TimingMiddleware(),
            LoggingMiddleware(),
            DjangoMiddleware(SessionMiddleware),
            DjangoMiddleware(AuthenticationMiddleware),
        ]
    )

    # Route-level middleware
    @api.get("/upload")
    @middleware(ValidateContentTypeMiddleware())
    async def upload(request: Request) -> dict:
        return {"uploaded": True}

    # Skip middleware
    @api.get("/health")
    @skip_middleware("*")
    async def health(request: Request) -> dict:
        return {"status": "ok"}
"""

from .middleware import (
    # Protocols and base classes
    MiddlewareProtocol,
    BaseMiddleware,
    Middleware,
    MiddlewareScope,
    CallNext,
    MiddlewareType,
    # Configuration
    MiddlewareGroup,
    MiddlewareConfig,
    # Decorators
    middleware,
    rate_limit,
    cors,
    skip_middleware,
    override_middleware,
    no_compress,
    # Built-in middleware (Rust-accelerated)
    CORSMiddleware,
    RateLimitMiddleware,
    # Built-in middleware (Python)
    TimingMiddleware,
    LoggingMiddleware,
    ErrorHandlerMiddleware,
)
from .compression import CompressionConfig
from .django_adapter import DjangoMiddleware

__all__ = [
    # Protocols and base classes
    "MiddlewareProtocol",
    "BaseMiddleware",
    "Middleware",
    "MiddlewareScope",
    "CallNext",
    "MiddlewareType",
    # Configuration
    "MiddlewareGroup",
    "MiddlewareConfig",
    "CompressionConfig",
    # Decorators
    "middleware",
    "rate_limit",
    "cors",
    "skip_middleware",
    "override_middleware",
    "no_compress",
    # Built-in middleware (Rust-accelerated)
    "CORSMiddleware",
    "RateLimitMiddleware",
    # Built-in middleware (Python)
    "TimingMiddleware",
    "LoggingMiddleware",
    "ErrorHandlerMiddleware",
    # Django compatibility
    "DjangoMiddleware",
]

"""
Django-Bolt Middleware System.

Provides decorators and classes for adding middleware to routes.
Middleware can be global or per-route.
"""

from .compression import CompressionConfig
from .middleware import (
    CORSMiddleware,
    Middleware,
    MiddlewareConfig,
    MiddlewareGroup,
    RateLimitMiddleware,
    cors,
    middleware,
    no_compress,
    rate_limit,
    skip_middleware,
)

__all__ = [
    "CORSMiddleware",
    "CompressionConfig",
    "Middleware",
    "MiddlewareConfig",
    "MiddlewareGroup",
    "RateLimitMiddleware",
    "cors",
    "middleware",
    "no_compress",
    "rate_limit",
    "skip_middleware",
]

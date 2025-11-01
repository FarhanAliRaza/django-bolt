"""
Django-Bolt Middleware System.

Provides decorators and classes for adding middleware to routes.
Middleware can be global or per-route.
"""

from .middleware import (
    Middleware,
    MiddlewareGroup,
    MiddlewareConfig,
    middleware,
    rate_limit,
    cors,
    skip_middleware,
    no_compress,
    CORSMiddleware,
    RateLimitMiddleware,
)
from .compression import CompressionConfig

__all__ = [
    "Middleware",
    "MiddlewareGroup",
    "MiddlewareConfig",
    "middleware",
    "rate_limit",
    "cors",
    "skip_middleware",
    "no_compress",
    "CORSMiddleware",
    "RateLimitMiddleware",
    "CompressionConfig",
]

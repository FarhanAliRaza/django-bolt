from .api import BoltAPI
from .responses import JSON, StreamingResponse

# Auth module
from .auth import (
    # Authentication backends
    JWTAuthentication,
    APIKeyAuthentication,
    SessionAuthentication,
    AuthContext,
    # Guards/Permissions
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsStaff,
    HasPermission,
    HasAnyPermission,
    HasAllPermissions,
    # JWT Token & Utilities
    Token,
    create_jwt_for_user,
    get_current_user,
    extract_user_id_from_context,
    get_auth_context,
)

# Middleware module
from .middleware import (
    Middleware,
    MiddlewareGroup,
    MiddlewareConfig,
    middleware,
    rate_limit,
    cors,
    skip_middleware,
    CORSMiddleware,
    RateLimitMiddleware,
)

__all__ = [
    "BoltAPI",
    "JSON",
    "StreamingResponse",
    # Auth - Authentication
    "JWTAuthentication",
    "APIKeyAuthentication",
    "SessionAuthentication",
    "AuthContext",
    # Auth - Guards/Permissions
    "AllowAny",
    "IsAuthenticated",
    "IsAdminUser",
    "IsStaff",
    "HasPermission",
    "HasAnyPermission",
    "HasAllPermissions",
    # Auth - Middleware
    "middleware",
    "rate_limit",
    "cors",
    "skip_middleware",
    "CORSMiddleware",
    "RateLimitMiddleware",
    # Auth - JWT Token & Utilities
    "Token",
    "create_jwt_for_user",
    "get_current_user",
    "extract_user_id_from_context",
    "get_auth_context",
]

default_app_config = 'django_bolt.apps.DjangoBoltConfig'



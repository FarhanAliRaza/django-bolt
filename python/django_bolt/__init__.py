from .api import BoltAPI
from .responses import Response, JSON, StreamingResponse
from .compression import CompressionConfig

# Views module
from .views import (
    APIView,
    ViewSet,
    ModelViewSet,
    ReadOnlyModelViewSet,
    ListMixin,
    RetrieveMixin,
    CreateMixin,
    UpdateMixin,
    PartialUpdateMixin,
    DestroyMixin,
)

# Decorators module
from .decorators import action

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
    no_compress,
    CORSMiddleware,
    RateLimitMiddleware,
)

# OpenAPI module
from .openapi import (
    OpenAPIConfig,
    SwaggerRenderPlugin,
    RedocRenderPlugin,
    ScalarRenderPlugin,
    RapidocRenderPlugin,
    StoplightRenderPlugin,
    JsonRenderPlugin,
    YamlRenderPlugin,
)

__all__ = [
    "BoltAPI",
    "Response",
    "JSON",
    "StreamingResponse",
    "CompressionConfig",
    # Views
    "APIView",
    "ViewSet",
    "ModelViewSet",
    "ReadOnlyModelViewSet",
    "ListMixin",
    "RetrieveMixin",
    "CreateMixin",
    "UpdateMixin",
    "PartialUpdateMixin",
    "DestroyMixin",
    # Decorators
    "action",
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
    # Middleware
    "middleware",
    "rate_limit",
    "cors",
    "skip_middleware",
    "no_compress",
    "CORSMiddleware",
    "RateLimitMiddleware",
    # Auth - JWT Token & Utilities
    "Token",
    "create_jwt_for_user",
    "get_current_user",
    "extract_user_id_from_context",
    "get_auth_context",
    # OpenAPI
    "OpenAPIConfig",
    "SwaggerRenderPlugin",
    "RedocRenderPlugin",
    "ScalarRenderPlugin",
    "RapidocRenderPlugin",
    "StoplightRenderPlugin",
    "JsonRenderPlugin",
    "YamlRenderPlugin",
]

default_app_config = 'django_bolt.apps.DjangoBoltConfig'



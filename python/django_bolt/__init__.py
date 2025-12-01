from .api import BoltAPI

# Auth module
from .auth import (
    # Guards/Permissions
    AllowAny,
    # Authentication backends
    APIKeyAuthentication,
    HasAllPermissions,
    HasAnyPermission,
    HasPermission,
    IsAdminUser,
    IsAuthenticated,
    IsStaff,
    JWTAuthentication,
    SessionAuthentication,  # Session authentication is not implemented
    # JWT Token & Utilities
    Token,
    create_jwt_for_user,
    extract_user_id_from_context,
    get_auth_context,
    get_current_user,
)

# Decorators module
from .decorators import action

# Middleware module
from .middleware import (
    CompressionConfig,
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

# OpenAPI module
from .openapi import (
    JsonRenderPlugin,
    OpenAPIConfig,
    RapidocRenderPlugin,
    RedocRenderPlugin,
    ScalarRenderPlugin,
    StoplightRenderPlugin,
    SwaggerRenderPlugin,
    YamlRenderPlugin,
)

# Pagination module
from .pagination import (
    CursorPagination,
    LimitOffsetPagination,
    PageNumberPagination,
    PaginatedResponse,
    PaginationBase,
    paginate,
)
from .params import Depends
from .responses import JSON, Response, StreamingResponse
from .types import AuthContext, DjangoModel, Request, UserType

# Views module
from .views import (
    APIView,
    CreateMixin,
    DestroyMixin,
    ListMixin,
    ModelViewSet,
    PartialUpdateMixin,
    ReadOnlyModelViewSet,
    RetrieveMixin,
    UpdateMixin,
    ViewSet,
)

__all__ = [
    "JSON",
    "APIKeyAuthentication",
    # Views
    "APIView",
    # Auth - Guards/Permissions
    "AllowAny",
    # Types
    "AuthContext",
    # Core
    "BoltAPI",
    "CORSMiddleware",
    "CompressionConfig",
    "CreateMixin",
    "CursorPagination",
    "Depends",
    "DestroyMixin",
    "DjangoModel",
    "HasAllPermissions",
    "HasAnyPermission",
    "HasPermission",
    "IsAdminUser",
    "IsAuthenticated",
    "IsStaff",
    # Auth - Authentication backends
    "JWTAuthentication",
    "JsonRenderPlugin",
    "LimitOffsetPagination",
    "ListMixin",
    # Middleware
    "Middleware",
    "MiddlewareConfig",
    "MiddlewareGroup",
    "ModelViewSet",
    # OpenAPI
    "OpenAPIConfig",
    "PageNumberPagination",
    "PaginatedResponse",
    # Pagination
    "PaginationBase",
    "PartialUpdateMixin",
    "RapidocRenderPlugin",
    "RateLimitMiddleware",
    "ReadOnlyModelViewSet",
    "RedocRenderPlugin",
    "Request",
    "Response",
    "RetrieveMixin",
    "ScalarRenderPlugin",
    "SessionAuthentication",
    "StoplightRenderPlugin",
    "StreamingResponse",
    "SwaggerRenderPlugin",
    # Auth - JWT Token & Utilities
    "Token",
    "UpdateMixin",
    "UserType",
    "ViewSet",
    "YamlRenderPlugin",
    # Decorators
    "action",
    "cors",
    "create_jwt_for_user",
    "extract_user_id_from_context",
    "get_auth_context",
    "get_current_user",
    "middleware",
    "no_compress",
    "paginate",
    "rate_limit",
    "skip_middleware",
]

default_app_config = "django_bolt.apps.DjangoBoltConfig"

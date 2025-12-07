"""
Django-Bolt: High-performance API framework for Django.

Provides Rust-powered API endpoints with 60k+ RPS performance, integrating
with existing Django projects via Actix Web, PyO3, and msgspec.

Quick Start:
    from django_bolt import BoltAPI, Request

    api = BoltAPI()

    @api.get("/hello")
    async def hello(request: Request) -> dict:
        return {"message": "Hello, World!"}

Type-Safe Requests:
    from django_bolt import BoltAPI, Request
    from django_bolt.types import JWTClaims
    from myapp.models import User

    api = BoltAPI()

    @api.get("/profile", guards=[IsAuthenticated()])
    async def profile(request: Request[User, JWTClaims, dict]) -> dict:
        return {"email": request.user.email}  # IDE knows User has email

Middleware:
    from django_bolt import BoltAPI
    from django_bolt.middleware import (
        DjangoMiddleware,
        TimingMiddleware,
        LoggingMiddleware,
    )
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.contrib.auth.middleware import AuthenticationMiddleware

    api = BoltAPI(
        middleware=[
            DjangoMiddleware(SessionMiddleware),
            DjangoMiddleware(AuthenticationMiddleware),
            TimingMiddleware(),
            LoggingMiddleware(),
        ]
    )
"""

from .api import BoltAPI
from .responses import Response, JSON, StreamingResponse
from .middleware import CompressionConfig
from .router import Router, APIRouter

# Type-safe Request object
from .request import Request, State

# Types and protocols
from .types import (
    Request as RequestProtocol,  # Protocol for type checking
    UserType,
    AuthContext,
    DjangoModel,
    JWTClaims,
    APIKeyAuth,
    SessionAuth,
    TimingState,
    TracingState,
)
from .params import Depends

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

# Pagination module
from .pagination import (
    PaginationBase,
    PageNumberPagination,
    LimitOffsetPagination,
    CursorPagination,
    PaginatedResponse,
    paginate,
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
    # Protocols and base classes
    MiddlewareProtocol,
    BaseMiddleware,
    Middleware,
    MiddlewareScope,
    CallNext,
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
    # Django compatibility
    DjangoMiddleware,
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

# WebSocket module
from .websocket import (
    WebSocket,
    WebSocketState,
    WebSocketDisconnect,
    WebSocketClose,
    WebSocketException,
    CloseCode,
)

__all__ = [
    # Core
    "BoltAPI",
    "Request",
    "State",
    "Response",
    "JSON",
    "StreamingResponse",
    "CompressionConfig",
    "Depends",
    # Router
    "Router",
    "APIRouter",
    # Types
    "RequestProtocol",
    "UserType",
    "AuthContext",
    "DjangoModel",
    "JWTClaims",
    "APIKeyAuth",
    "SessionAuth",
    "TimingState",
    "TracingState",
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
    # Pagination
    "PaginationBase",
    "PageNumberPagination",
    "LimitOffsetPagination",
    "CursorPagination",
    "PaginatedResponse",
    "paginate",
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
    # Middleware - Protocols and base classes
    "MiddlewareProtocol",
    "BaseMiddleware",
    "Middleware",
    "MiddlewareScope",
    "CallNext",
    # Middleware - Configuration
    "MiddlewareGroup",
    "MiddlewareConfig",
    # Middleware - Decorators
    "middleware",
    "rate_limit",
    "cors",
    "skip_middleware",
    "override_middleware",
    "no_compress",
    # Middleware - Built-in (Rust-accelerated)
    "CORSMiddleware",
    "RateLimitMiddleware",
    # Middleware - Built-in (Python)
    "TimingMiddleware",
    "LoggingMiddleware",
    "ErrorHandlerMiddleware",
    # Middleware - Django compatibility
    "DjangoMiddleware",
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
    # WebSocket
    "WebSocket",
    "WebSocketState",
    "WebSocketDisconnect",
    "WebSocketClose",
    "WebSocketException",
    "CloseCode",
]

default_app_config = 'django_bolt.apps.DjangoBoltConfig'

"""
Django-Bolt Authentication and Authorization System.

High-performance auth system where validation happens in Rust without the GIL.
Python classes define configuration that gets compiled to Rust types.
"""

# Authentication backends
from .backends import (
    BaseAuthentication,
    JWTAuthentication,
    APIKeyAuthentication,
    SessionAuthentication, # Session authentication is not implemented
    AuthContext,
    get_default_authentication_classes,
)

# Permission guards
from .guards import (
    BasePermission,
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsStaff,
    HasPermission,
    HasAnyPermission,
    HasAllPermissions,
    get_default_permission_classes,
)

# JWT Token handling
from .token import Token

# JWT utilities for Django User integration
from .jwt_utils import (
    create_jwt_for_user,
    get_current_user,
    extract_user_id_from_context,
    get_auth_context,
)

# Token revocation (optional)
from .revocation import (
    RevocationStore,
    InMemoryRevocation,
    DjangoCacheRevocation,
    DjangoORMRevocation,
    create_revocation_handler,
)

# User loading for request.user
from .user_loader import (
    register_auth_backend,
    get_registered_backend,
    load_user,
)

__all__ = [
    # Authentication
    "BaseAuthentication",
    "JWTAuthentication",
    "APIKeyAuthentication",
    "SessionAuthentication", # Session authentication is not implemented
    "AuthContext",
    "get_default_authentication_classes",

    # Guards/Permissions
    "BasePermission",
    "AllowAny",
    "IsAuthenticated",
    "IsAdminUser",
    "IsStaff",
    "HasPermission",
    "HasAnyPermission",
    "HasAllPermissions",
    "get_default_permission_classes",

    # JWT
    "Token",
    "create_jwt_for_user",
    "get_current_user",
    "extract_user_id_from_context",
    "get_auth_context",

    # Revocation (optional)
    "RevocationStore",
    "InMemoryRevocation",
    "DjangoCacheRevocation",
    "DjangoORMRevocation",
    "create_revocation_handler",

    # User loading
    "register_auth_backend",
    "get_registered_backend",
    "load_user",
]

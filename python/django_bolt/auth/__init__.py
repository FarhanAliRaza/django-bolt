"""
Django-Bolt Authentication and Authorization System.

High-performance auth system where validation happens in Rust without the GIL.
Python classes define configuration that gets compiled to Rust types.
"""

# Authentication backends
from .backends import (
    APIKeyAuthentication,
    AuthContext,
    BaseAuthentication,
    JWTAuthentication,
    SessionAuthentication,  # Session authentication is not implemented
    get_default_authentication_classes,
)

# Permission guards
from .guards import (
    AllowAny,
    BasePermission,
    HasAllPermissions,
    HasAnyPermission,
    HasPermission,
    IsAdminUser,
    IsAuthenticated,
    IsStaff,
    get_default_permission_classes,
)

# JWT utilities for Django User integration
from .jwt_utils import (
    create_jwt_for_user,
    extract_user_id_from_context,
    get_auth_context,
    get_current_user,
)

# Token revocation (optional)
from .revocation import (
    DjangoCacheRevocation,
    DjangoORMRevocation,
    InMemoryRevocation,
    RevocationStore,
    create_revocation_handler,
)

# JWT Token handling
from .token import Token

# User loading for request.user
from .user_loader import (
    get_registered_backend,
    load_user,
    register_auth_backend,
)

__all__ = [
    "APIKeyAuthentication",
    "AllowAny",
    "AuthContext",
    # Authentication
    "BaseAuthentication",
    # Guards/Permissions
    "BasePermission",
    "DjangoCacheRevocation",
    "DjangoORMRevocation",
    "HasAllPermissions",
    "HasAnyPermission",
    "HasPermission",
    "InMemoryRevocation",
    "IsAdminUser",
    "IsAuthenticated",
    "IsStaff",
    "JWTAuthentication",
    # Revocation (optional)
    "RevocationStore",
    "SessionAuthentication",  # Session authentication is not implemented
    # JWT
    "Token",
    "create_jwt_for_user",
    "create_revocation_handler",
    "extract_user_id_from_context",
    "get_auth_context",
    "get_current_user",
    "get_default_authentication_classes",
    "get_default_permission_classes",
    "get_registered_backend",
    "load_user",
    # User loading
    "register_auth_backend",
]

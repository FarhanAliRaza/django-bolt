"""
Permission/guard system for Django-Bolt.

Provides DRF-inspired permission classes (called "guards" in Litestar terminology)
that are compiled to Rust types for zero-GIL performance.
"""

from abc import ABC, abstractmethod
from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class BasePermission(ABC):
    """
    Base class for permission guards.

    Guards are evaluated in Rust after authentication to determine if
    a request should be allowed. This happens before the Python handler
    is called, enabling early 403 responses without GIL overhead.
    """

    @property
    @abstractmethod
    def guard_name(self) -> str:
        """Return the guard type name for Rust compilation"""
        pass

    @abstractmethod
    def to_metadata(self) -> dict[str, Any]:
        """
        Compile this permission guard into metadata for Rust.

        Returns a dict that will be parsed by Rust into typed enums.
        """
        pass

    def has_permission(self, auth_context: Any | None) -> bool:
        """
        Check if the authenticated user has permission (Python fallback).

        This is primarily for documentation/compatibility. The actual check
        happens in Rust for performance.
        """
        return True


class AllowAny(BasePermission):
    """
    Allow any request, authenticated or not.

    This is the default permission when no guards are specified.
    Using this explicitly bypasses any global default permissions.
    """

    @property
    def guard_name(self) -> str:
        return "allow_any"

    def to_metadata(self) -> dict[str, Any]:
        return {"type": "allow_any"}

    def has_permission(self, auth_context: Any | None) -> bool:
        return True


class IsAuthenticated(BasePermission):
    """
    Require that the request is authenticated.

    Returns 401 if no authentication was successful.
    """

    @property
    def guard_name(self) -> str:
        return "is_authenticated"

    def to_metadata(self) -> dict[str, Any]:
        return {"type": "is_authenticated"}

    def has_permission(self, auth_context: Any | None) -> bool:
        return auth_context is not None and auth_context.user_id is not None


class IsAdminUser(BasePermission):
    """
    Require that the authenticated user is an admin/superuser.

    Returns 403 if user is not a superuser.
    Requires JWT token to include 'is_superuser' claim.
    """

    @property
    def guard_name(self) -> str:
        return "is_superuser"

    def to_metadata(self) -> dict[str, Any]:
        return {"type": "is_superuser"}

    def has_permission(self, auth_context: Any | None) -> bool:
        return auth_context is not None and auth_context.is_superuser


class IsStaff(BasePermission):
    """
    Require that the authenticated user is staff.

    Returns 403 if user is not staff.
    Requires JWT token to include 'is_staff' claim.
    """

    @property
    def guard_name(self) -> str:
        return "is_staff"

    def to_metadata(self) -> dict[str, Any]:
        return {"type": "is_staff"}

    def has_permission(self, auth_context: Any | None) -> bool:
        return auth_context is not None and auth_context.is_staff


class HasPermission(BasePermission):
    """
    Require that the authenticated user has a specific permission.

    Args:
        permission: Permission string (e.g., "app.view_model", "api.create_resource")

    For JWT: token should include "permissions" claim as list of strings
    For API keys: configured via key_permissions mapping in APIKeyAuthentication
    """

    def __init__(self, permission: str):
        self.permission = permission

    @property
    def guard_name(self) -> str:
        return "has_permission"

    def to_metadata(self) -> dict[str, Any]:
        return {
            "type": "has_permission",
            "permission": self.permission,
        }

    def has_permission(self, auth_context: Any | None) -> bool:
        if auth_context is None or auth_context.permissions is None:
            return False
        return self.permission in auth_context.permissions


class HasAnyPermission(BasePermission):
    """
    Require that the authenticated user has at least one of the specified permissions.

    Args:
        permissions: List of permission strings
    """

    def __init__(self, *permissions: str):
        self.permissions = list(permissions)

    @property
    def guard_name(self) -> str:
        return "has_any_permission"

    def to_metadata(self) -> dict[str, Any]:
        return {
            "type": "has_any_permission",
            "permissions": self.permissions,
        }

    def has_permission(self, auth_context: Any | None) -> bool:
        if auth_context is None or auth_context.permissions is None:
            return False
        return any(perm in auth_context.permissions for perm in self.permissions)


class HasAllPermissions(BasePermission):
    """
    Require that the authenticated user has all of the specified permissions.

    Args:
        permissions: List of permission strings
    """

    def __init__(self, *permissions: str):
        self.permissions = list(permissions)

    @property
    def guard_name(self) -> str:
        return "has_all_permissions"

    def to_metadata(self) -> dict[str, Any]:
        return {
            "type": "has_all_permissions",
            "permissions": self.permissions,
        }

    def has_permission(self, auth_context: Any | None) -> bool:
        if auth_context is None or auth_context.permissions is None:
            return False
        return all(perm in auth_context.permissions for perm in self.permissions)


def get_default_permission_classes() -> list[BasePermission]:
    """
    Get default permission classes from Django settings.

    Looks for BOLT_DEFAULT_PERMISSION_CLASSES in settings. If not found,
    returns [AllowAny()] (no restrictions by default).
    """
    try:
        try:
            if hasattr(settings, 'BOLT_DEFAULT_PERMISSION_CLASSES'):
                return settings.BOLT_DEFAULT_PERMISSION_CLASSES
        except ImproperlyConfigured:
            # Settings not configured, return default
            pass
    except (ImportError, AttributeError):
        pass

    return [AllowAny()]

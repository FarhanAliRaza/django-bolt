"""
Authentication system for Django-Bolt.

Provides DRF-inspired authentication classes that are compiled to Rust types
for zero-GIL performance in the hot path.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class AuthContext:
    """
    Authentication context returned by authentication backends.

    This is populated in Rust and passed to Python handlers via request.context.
    """
    user_id: Optional[str] = None
    is_staff: bool = False
    is_admin: bool = False
    backend: str = "none"
    claims: Optional[Dict[str, Any]] = None
    permissions: Optional[Set[str]] = None


class BaseAuthentication(ABC):
    """
    Base class for authentication backends.

    Authentication happens in Rust for performance. These classes compile
    their configuration into metadata that Rust uses to validate tokens/keys.
    """

    @property
    @abstractmethod
    def scheme_name(self) -> str:
        """Return the authentication scheme name (e.g., 'jwt', 'api_key')"""
        pass

    @abstractmethod
    def to_metadata(self) -> Dict[str, Any]:
        """
        Compile this authentication backend into metadata for Rust.

        Returns a dict that will be parsed by Rust into typed enums.
        """
        pass


class JWTAuthentication(BaseAuthentication):
    """
    JWT token authentication.

    Validates JWT tokens using the configured secret and algorithms.
    Tokens should be provided in the Authorization header as "Bearer <token>".

    Args:
        secret: Secret key for JWT validation. If None, uses Django's SECRET_KEY.
        algorithms: List of allowed JWT algorithms (default: ["HS256"])
        header: Header name to extract token from (default: "authorization")
        audience: Optional JWT audience claim to validate
        issuer: Optional JWT issuer claim to validate
    """

    def __init__(
        self,
        secret: Optional[str] = None,
        algorithms: Optional[List[str]] = None,
        header: str = "authorization",
        audience: Optional[str] = None,
        issuer: Optional[str] = None,
    ):
        self.secret = secret
        self.algorithms = algorithms or ["HS256"]
        self.header = header
        self.audience = audience
        self.issuer = issuer

        # If no secret provided, try to get Django's SECRET_KEY
        if self.secret is None:
            try:
                from django.conf import settings
                self.secret = settings.SECRET_KEY
            except (ImportError, AttributeError):
                pass  # Will be handled at runtime

    @property
    def scheme_name(self) -> str:
        return "jwt"

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "type": "jwt",
            "secret": self.secret,
            "algorithms": self.algorithms,
            "header": self.header.lower(),
            "audience": self.audience,
            "issuer": self.issuer,
        }


class APIKeyAuthentication(BaseAuthentication):
    """
    API key authentication.

    Validates API keys against a configured set of valid keys.
    Keys should be provided in the configured header (default: X-API-Key).

    Args:
        api_keys: Set of valid API keys
        header: Header name to extract API key from (default: "x-api-key")
        key_permissions: Optional mapping of API keys to permission sets
    """

    def __init__(
        self,
        api_keys: Optional[Set[str]] = None,
        header: str = "x-api-key",
        key_permissions: Optional[Dict[str, Set[str]]] = None,
    ):
        self.api_keys = api_keys or set()
        self.header = header
        self.key_permissions = key_permissions or {}

    @property
    def scheme_name(self) -> str:
        return "api_key"

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "type": "api_key",
            "api_keys": list(self.api_keys),
            "header": self.header.lower(),
            "key_permissions": {
                k: list(v) for k, v in self.key_permissions.items()
            },
        }


class SessionAuthentication(BaseAuthentication):
    """
    Django session authentication.

    Uses Django's session framework to authenticate users.
    This requires Django to be configured and session middleware enabled.

    Note: This has higher overhead than JWT/API key auth as it requires
    Python execution for every request.
    """

    def __init__(self):
        pass

    @property
    def scheme_name(self) -> str:
        return "session"

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "type": "session",
        }


def get_default_authentication_classes() -> List[BaseAuthentication]:
    """
    Get default authentication classes from Django settings.

    Looks for BOLT_AUTHENTICATION_CLASSES in settings. If not found,
    returns an empty list (no authentication by default).
    """
    try:
        from django.conf import settings
        from django.core.exceptions import ImproperlyConfigured
        try:
            if hasattr(settings, 'BOLT_AUTHENTICATION_CLASSES'):
                return settings.BOLT_AUTHENTICATION_CLASSES
        except ImproperlyConfigured:
            # Settings not configured, return empty list
            pass
    except (ImportError, AttributeError):
        pass

    return []
"""
Authentication system for Django-Bolt.

Provides DRF-inspired authentication classes that are compiled to Rust types
for zero-GIL performance in the hot path.

The authentication flow:
1. Python defines auth backends (JWT, API key, session)
2. Backends compile to metadata dicts via to_metadata()
3. Rust parses metadata at registration time
4. Rust validates tokens/keys without GIL on each request
5. AuthContext is populated and passed to Python handlers

Performance: ~60k+ RPS with JWT validation happening entirely in Rust.
"""
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

@dataclass
class AuthContext:
    """
    Authentication context returned by authentication backends.

    This is populated in Rust and passed to Python handlers via request.context.
    """
    user_id: Optional[str] = None
    is_staff: bool = False
    is_superuser: bool = False
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

    async def get_user(self, user_id: Optional[str], auth_context: Dict[str, Any]) -> Optional[Any]:
        """
        Resolve a User instance from the authentication context.

        This method is called when request.user is awaited. Override this method
        to provide custom user resolution logic for your authentication backend.

        Args:
            user_id: The user identifier from the auth context
            auth_context: The full authentication context dict containing:
                - user_id: User identifier
                - is_staff: Whether user is staff
                - is_superuser: Whether user is a superuser
                - auth_backend: Backend name (jwt, api_key, session)
                - permissions: Set of permission strings
                - auth_claims: JWT claims dict (if JWT backend)

        Returns:
            User instance or None if user not found or backend doesn't support user loading
        """
        # Default: no user resolution
        return None


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
        revoked_token_handler: Optional[callable] = None,
        revocation_store: Optional[Any] = None,
        require_jti: bool = False,
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
                from django.core.exceptions import ImproperlyConfigured

                if not hasattr(settings, 'SECRET_KEY'):
                    raise ImproperlyConfigured(
                        "JWTAuthentication requires a 'secret' parameter or Django's SECRET_KEY setting. "
                        "Neither was provided."
                    )

                self.secret = settings.SECRET_KEY

                if not self.secret or self.secret == '':
                    raise ImproperlyConfigured(
                        "JWTAuthentication secret cannot be empty. "
                        "Please provide a non-empty 'secret' parameter or set Django's SECRET_KEY."
                    )
            except ImportError:
                from django.core.exceptions import ImproperlyConfigured
                raise ImproperlyConfigured(
                    "JWTAuthentication requires Django to be installed and configured, "
                    "or a 'secret' parameter must be explicitly provided."
                )

        # Revocation support (OPTIONAL - only checked if provided)
        self.revoked_token_handler = revoked_token_handler
        self.revocation_store = revocation_store

        # Auto-enable require_jti if revocation is configured
        if (revoked_token_handler or revocation_store) and not require_jti:
            require_jti = True
        self.require_jti = require_jti

        # If revocation_store provided, create handler from it
        if revocation_store and not revoked_token_handler:
            from .revocation import create_revocation_handler
            self.revoked_token_handler = create_revocation_handler(revocation_store)

    @property
    def scheme_name(self) -> str:
        return "jwt"

    def to_metadata(self) -> Dict[str, Any]:
        metadata = {
            "type": "jwt",
            "secret": self.secret,
            "algorithms": self.algorithms,
            "header": self.header.lower(),
            "audience": self.audience,
            "issuer": self.issuer,
            "require_jti": self.require_jti,
        }

        # Add revocation handler reference (will be called from Rust if present)
        if self.revoked_token_handler:
            metadata["has_revocation_handler"] = True

        return metadata

    async def get_user(self, user_id: Optional[str], auth_context: Dict[str, Any]) -> Optional[Any]:
        """
        Load user from database using the user_id from JWT token.

        The user_id should be the primary key of the user in the database.
        Uses sync_to_async for proper thread-safety with Django ORM.
        """
        if not user_id:
            return None


        User = get_user_model()

        try:
            # Use sync_to_async wrapper for proper thread-safety and database context
            # Ensures Django's connection pooling is used correctly
            return await sync_to_async(User.objects.get, thread_sensitive=False)(pk=user_id)
        except User.DoesNotExist:
            # User not found - this is expected in some cases
            return None
        except Exception as e:
            # Unexpected error - log it for debugging
            print(f"Error loading user {user_id} in JWTAuthentication: {type(e).__name__}: {e}", file=sys.stderr)
            return None


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

    async def get_user(self, user_id: Optional[str], auth_context: Dict[str, Any]) -> Optional[Any]:
        """
        Load user from database using the user_id from session.

        The user_id should be the primary key of the user in the database.
        Uses sync_to_async for proper thread-safety with Django ORM.
        """
        if not user_id:
            return None
        User = get_user_model()

        try:
            # Use sync_to_async wrapper for proper thread-safety and database context
            # Ensures Django's connection pooling is used correctly
            return await sync_to_async(User.objects.get, thread_sensitive=False)(pk=user_id)
        except User.DoesNotExist:
            # User not found - this is expected in some cases
            return None
        except Exception as e:
            # Unexpected error - log it for debugging
            print(f"Error loading user {user_id} in SessionAuthentication: {type(e).__name__}: {e}", file=sys.stderr)
            return None


def get_default_authentication_classes() -> List[BaseAuthentication]:
    """
    Get default authentication classes from Django settings.

    Looks for BOLT_AUTHENTICATION_CLASSES in settings. If not found,
    returns an empty list (no authentication by default).
    """
    try:
        
        try:
            if hasattr(settings, 'BOLT_AUTHENTICATION_CLASSES'):
                return settings.BOLT_AUTHENTICATION_CLASSES
        except ImproperlyConfigured:
            # Settings not configured, return empty list
            pass
    except (ImportError, AttributeError):
        pass

    return []

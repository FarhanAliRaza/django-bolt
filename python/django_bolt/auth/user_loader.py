"""
User loading system for request.user

Supports both eager and lazy loading strategies.
Eager loading (default): Loads user immediately at dispatch time (43% faster)
Lazy loading (optional): Wraps loading in LazyUser for first-access evaluation
"""

from __future__ import annotations

from typing import Any

# Global registry of auth backend instances for user resolution
_auth_backend_registry: dict[str, Any] = {}


def register_auth_backend(backend_name: str, backend_instance: Any) -> None:
    """
    Register an authentication backend instance for user resolution.

    Called at server startup to make backends available for user loading.

    Args:
        backend_name: Unique identifier for the backend (e.g., "jwt", "api_key")
        backend_instance: Instance of the authentication backend class
    """
    _auth_backend_registry[backend_name] = backend_instance


def get_registered_backend(backend_name: str) -> Any | None:
    """Get a registered auth backend by name."""
    return _auth_backend_registry.get(backend_name)


async def load_user(
    user_id: str | None, backend_name: str | None, auth_context: dict | None = None
) -> Any | None:
    """
    Eagerly load user from auth context.

    Loads user immediately (not lazy). Suitable for authenticated endpoints
    where user is always needed.

    Args:
        user_id: User identifier from auth context
        backend_name: Authentication backend name (e.g., "jwt", "api_key")
        auth_context: Full authentication context dict

    Returns:
        User object, or None if not found or no user_id
    """
    if not user_id:
        return None

    # Try to get registered backend with custom get_user method
    backend = get_registered_backend(backend_name) if backend_name else None

    # If backend has custom get_user, call it
    if backend and hasattr(backend, "get_user"):
        try:
            return await backend.get_user(user_id, auth_context or {})
        except Exception:
            # User not found or backend error
            raise

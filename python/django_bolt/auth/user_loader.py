"""
User loading system for request.user

Supports both eager and lazy loading strategies.
Lazy loading (default): Uses SimpleLazyObject to defer DB query until first access
Eager loading (optional): Loads user immediately at dispatch time
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
from typing import Any

from django.contrib.auth import get_user_model

# Global registry of auth backend instances for user resolution
_auth_backend_registry: dict[str, Any] = {}

# Global shared thread pool for user loading - avoids expensive pool creation per request
# Using max_workers=4 to limit resource usage while allowing concurrent user loads
_user_loader_executor: concurrent.futures.ThreadPoolExecutor | None = None


def _get_executor() -> concurrent.futures.ThreadPoolExecutor:
    """Get or create the shared thread pool executor."""
    global _user_loader_executor
    if _user_loader_executor is None:
        _user_loader_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="user_loader"
        )
    return _user_loader_executor


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

    return None


def load_user_sync(
    user_id: str | None,
    backend_name: str | None,
    auth_context: dict | None = None,
    is_async_context: bool = False,
) -> Any | None:
    """
    Synchronously load user from auth context.

    This is the sync version used by SimpleLazyObject for lazy loading.
    Handles thread pool wrapping for async contexts.

    Args:
        user_id: User identifier from auth context
        backend_name: Authentication backend name (e.g., "jwt", "api_key")
        auth_context: Full authentication context dict
        is_async_context: Whether we're in an async handler (use thread pool)

    Returns:
        User object, or None if not found or no user_id
    """
    if not user_id:
        return None

    # Try to get registered backend with custom get_user_sync method
    backend = get_registered_backend(backend_name) if backend_name else None

    # If backend has custom get_user_sync, call it (with thread pool wrapping if needed)
    if backend and hasattr(backend, "get_user_sync"):
        if is_async_context:
            future = _get_executor().submit(backend.get_user_sync, user_id)
            return future.result()
        else:
            return backend.get_user_sync(user_id)

    # If backend has async get_user (but no sync version), call it via thread pool
    if backend and hasattr(backend, "get_user"):
        get_user_method = backend.get_user
        if inspect.iscoroutinefunction(get_user_method):
            def run_async_get_user():
                return asyncio.run(get_user_method(user_id, auth_context or {}))

            future = _get_executor().submit(run_async_get_user)
            return future.result()

    # Fallback: Django ORM call (with thread pool wrapping if needed)
    User = get_user_model()

    if is_async_context:
        future = _get_executor().submit(User.objects.get, pk=user_id)
        return future.result()
    else:
        return User.objects.get(pk=user_id)

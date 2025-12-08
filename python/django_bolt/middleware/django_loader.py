"""
Django middleware loader for Django-Bolt.

Automatically loads middleware from Django's settings.MIDDLEWARE configuration,
providing seamless integration with existing Django projects.

Usage:
    # Use all Django middleware from settings.MIDDLEWARE
    api = BoltAPI(django_middleware=True)

    # Exclude specific middleware
    api = BoltAPI(django_middleware={"exclude": ["django.middleware.csrf.CsrfViewMiddleware"]})

    # Only include specific middleware
    api = BoltAPI(django_middleware={"include": [
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    ]})
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .middleware import MiddlewareType


# Middleware that may be excluded for API-only endpoints (opt-in exclusion)
# By default, ALL middleware from settings.MIDDLEWARE are loaded
DEFAULT_EXCLUDED_MIDDLEWARE: set = set()  # Empty by default - load everything


def load_django_middleware(
    config: Union[bool, List[str], Dict[str, Any]] = True,
    *,
    exclude_defaults: bool = True,
) -> List["MiddlewareType"]:
    """
    Load middleware from Django's settings.MIDDLEWARE configuration.

    Args:
        config: Middleware configuration. Can be:
            - True: Load all middleware from settings.MIDDLEWARE
            - False/None: Return empty list
            - List[str]: Load only these specific middleware classes
            - Dict with:
                - "include": List of middleware to include (if specified, only these are used)
                - "exclude": List of middleware to exclude
        exclude_defaults: If True, exclude middleware that don't make sense for APIs
                         (CSRF, Clickjacking, Messages). Default True.

    Returns:
        List of wrapped Django middleware instances ready for use with Bolt.

    Example:
        # In your api.py
        from django_bolt import BoltAPI
        from django_bolt.middleware.django_loader import load_django_middleware

        api = BoltAPI(
            middleware=load_django_middleware()  # Uses settings.MIDDLEWARE
        )

        # Or with configuration
        api = BoltAPI(
            middleware=load_django_middleware({
                "exclude": ["django.middleware.csrf.CsrfViewMiddleware"]
            })
        )
    """
    from django.conf import settings
    from django.utils.module_loading import import_string
    from .django_adapter import DjangoMiddleware

    if config is False or config is None:
        return []

    # Get the middleware list from Django settings
    django_middleware_list = getattr(settings, 'MIDDLEWARE', [])

    if not django_middleware_list:
        return []

    # Determine which middleware to include/exclude
    include_set: Optional[Set[str]] = None
    exclude_set: Set[str] = set()

    if exclude_defaults:
        exclude_set.update(DEFAULT_EXCLUDED_MIDDLEWARE)

    if isinstance(config, list):
        # Explicit list of middleware to include
        include_set = set(config)
    elif isinstance(config, dict):
        if "include" in config:
            include_set = set(config["include"])
        if "exclude" in config:
            exclude_set.update(config["exclude"])
    # If config is True, use all from settings with default exclusions

    # Build the middleware list
    middleware_instances: List["MiddlewareType"] = []

    for middleware_path in django_middleware_list:
        # Check if we should include this middleware
        if include_set is not None and middleware_path not in include_set:
            continue
        if middleware_path in exclude_set:
            continue

        try:
            middleware_class = import_string(middleware_path)
            wrapped = DjangoMiddleware(middleware_class)
            middleware_instances.append(wrapped)
        except ImportError as e:
            import logging
            logging.getLogger("django_bolt").warning(
                f"Could not import Django middleware '{middleware_path}': {e}"
            )

    return middleware_instances


def get_django_middleware_setting() -> List[str]:
    """
    Get the current MIDDLEWARE setting from Django.

    Returns:
        List of middleware class paths from settings.MIDDLEWARE
    """
    try:
        from django.conf import settings
        return list(getattr(settings, 'MIDDLEWARE', []))
    except Exception:
        return []


__all__ = [
    "load_django_middleware",
    "get_django_middleware_setting",
    "DEFAULT_EXCLUDED_MIDDLEWARE",
]

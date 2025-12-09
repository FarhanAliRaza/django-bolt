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

import logging
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.utils.module_loading import import_string

from .django_adapter import DjangoMiddlewareStack

if TYPE_CHECKING:
    from .middleware import MiddlewareType


# Middleware that may be excluded for API-only endpoints (opt-in exclusion)
# By default, ALL middleware from settings.MIDDLEWARE are loaded
DEFAULT_EXCLUDED_MIDDLEWARE: set = set()  # Empty by default - load everything


def load_django_middleware(
    config: bool | list[str] | dict[str, Any] = True,
    *,
    exclude_defaults: bool = True,
) -> list[MiddlewareType]:
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
    if config is False or config is None:
        return []

    # Get the middleware list from Django settings
    django_middleware_list = getattr(settings, 'MIDDLEWARE', [])

    if not django_middleware_list:
        return []

    # Determine which middleware to include/exclude
    include_set: set[str] | None = None
    exclude_set: set[str] = set()

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

    # Collect middleware classes (not instances)
    middleware_classes: list = []

    for middleware_path in django_middleware_list:
        # Check if we should include this middleware
        if include_set is not None and middleware_path not in include_set:
            continue
        if middleware_path in exclude_set:
            continue

        try:
            middleware_class = import_string(middleware_path)
            middleware_classes.append(middleware_class)
        except ImportError as e:
            logging.getLogger("django_bolt").warning(
                f"Could not import Django middleware '{middleware_path}': {e}"
            )

    # Return a single DjangoMiddlewareStack that wraps ALL middleware
    # This is a critical performance optimization:
    # - Instead of N Bolt↔Django conversions (one per middleware)
    # - We do just 1 conversion at start and 1 at end
    if middleware_classes:
        return [DjangoMiddlewareStack(middleware_classes)]
    return []


def get_django_middleware_setting() -> list[str]:
    """
    Get the current MIDDLEWARE setting from Django.

    Returns:
        List of middleware class paths from settings.MIDDLEWARE
    """
    try:
        return list(getattr(settings, 'MIDDLEWARE', []))
    except Exception:
        return []


__all__ = [
    "load_django_middleware",
    "get_django_middleware_setting",
    "DEFAULT_EXCLUDED_MIDDLEWARE",
]

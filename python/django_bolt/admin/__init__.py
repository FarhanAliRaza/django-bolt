"""
Django admin integration for django-bolt.

This module provides Django admin detection utilities for integration with
django-bolt's ASGI mount system.
"""

from .admin_detection import (
    detect_admin_url_prefix,
    get_admin_info,
    get_admin_route_patterns,
    is_admin_installed,
    should_enable_admin,
)

__all__ = [
    "is_admin_installed",
    "detect_admin_url_prefix",
    "get_admin_route_patterns",
    "should_enable_admin",
    "get_admin_info",
]

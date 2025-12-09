"""
Django admin integration for django-bolt.

This module provides ASGI bridge functionality to integrate Django's admin
interface with django-bolt's high-performance routing system.
"""

from .admin_detection import (
    detect_admin_url_prefix,
    get_admin_info,
    get_admin_route_patterns,
    is_admin_installed,
    should_enable_admin,
)
from .asgi_bridge import ASGIFallbackHandler

__all__ = [
    "is_admin_installed",
    "detect_admin_url_prefix",
    "get_admin_route_patterns",
    "should_enable_admin",
    "get_admin_info",
    "ASGIFallbackHandler",
]

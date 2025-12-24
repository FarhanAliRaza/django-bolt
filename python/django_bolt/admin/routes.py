"""
Django admin route registration for BoltAPI.

This module handles the registration of Django admin routes via ASGI bridge,
keeping the BoltAPI class lean and focused.
"""
from typing import TYPE_CHECKING

from django_bolt.admin.admin_detection import get_admin_route_patterns, should_enable_admin
from django_bolt.admin.asgi_bridge import ASGIFallbackHandler

if TYPE_CHECKING:
    from django_bolt.api import BoltAPI


class AdminRouteRegistrar:
    """Handles registration of Django admin routes via ASGI bridge."""

    def __init__(self, api: 'BoltAPI'):
        """Initialize the registrar with a BoltAPI instance.

        Args:
            api: The BoltAPI instance to register routes on
        """
        self.api = api

    def register_routes(self, host: str = "localhost", port: int = 8000) -> None:
        """Register Django admin routes via ASGI bridge.

        This method auto-registers routes for Django admin if it's installed
        and enabled. The routes use an ASGI bridge to handle Django's middleware
        stack (sessions, CSRF, auth, etc.).

        Args:
            host: Server hostname for ASGI scope
            port: Server port for ASGI scope
        """
        if self.api._admin_routes_registered:
            return

        # Check if admin should be enabled
        if not should_enable_admin():
            return

        # Get admin route patterns
        route_patterns = get_admin_route_patterns()
        if not route_patterns:
            return

        # Lazy-load ASGI handler
        if self.api._asgi_handler is None:
            self.api._asgi_handler = ASGIFallbackHandler(host, port)

        # Register admin routes for each method
        for path_pattern, methods in route_patterns:
            for method in methods:
                self._register_admin_route(method, path_pattern)

        self.api._admin_routes_registered = True

    def _register_admin_route(self, method: str, path_pattern: str) -> None:
        """Register a single admin route.

        Args:
            method: HTTP method (GET, POST, etc.)
            path_pattern: URL path pattern
        """
        # Create handler that delegates to ASGI bridge
        # NOTE: We need to create a new function for each route to avoid closure issues
        def make_admin_handler(asgi_handler):
            async def admin_handler(request):
                return await asgi_handler.handle_request(request)
            return admin_handler

        admin_handler = make_admin_handler(self.api._asgi_handler)

        # Register the route using internal route registration
        # This bypasses the decorator to avoid async enforcement issues
        handler_id = self.api._next_handler_id
        self.api._next_handler_id += 1

        self.api._routes.append((method, path_pattern, handler_id, admin_handler))
        self.api._handlers[handler_id] = admin_handler

        # Create minimal metadata for admin handlers
        meta = {
            "mode": "request_only",
            "sig": None,
            "fields": [],
        }
        self.api._handler_meta[handler_id] = meta

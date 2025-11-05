"""
Django view route registration for BoltAPI.

Handles registration of Django views (FBVs and CBVs) via ASGI bridge,
with support for URL resolution skipping to improve performance.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from django_bolt.api import BoltAPI


class DjangoViewRegistrar:
    """Handles registration of Django views via ASGI bridge."""

    def __init__(self, api: BoltAPI):
        """Initialize the registrar with a BoltAPI instance.

        Args:
            api: The BoltAPI instance to register routes on
        """
        self.api = api

    def register_view(
        self,
        path: str,
        view: Callable,
        methods: Optional[List[str]] = None,
        host: str = "localhost",
        port: int = 8000,
    ) -> None:
        """Register a single Django view.

        Args:
            path: Route path pattern (matchit syntax, e.g., '/articles/{id}')
            view: Django view callable (FBV or CBV via as_view())
            methods: HTTP methods to support (defaults to GET, POST, PUT, PATCH, DELETE)
            host: Server hostname for ASGI scope
            port: Server port for ASGI scope
        """
        if methods is None:
            methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']

        # Ensure ASGI handler is initialized
        if self.api._asgi_handler is None:
            from django_bolt.admin.asgi_bridge import ASGIFallbackHandler
            self.api._asgi_handler = ASGIFallbackHandler(host, port)

        # Register route for each method
        for method in methods:
            self._register_single_route(method, path, view)

    def register_views(
        self,
        views: List[tuple[str, Callable, List[str]]],
        host: str = "localhost",
        port: int = 8000,
    ) -> None:
        """Register multiple Django views.

        Args:
            views: List of (path_pattern, view_callable, methods) tuples
            host: Server hostname for ASGI scope
            port: Server port for ASGI scope
        """
        # Ensure ASGI handler is initialized
        if self.api._asgi_handler is None:
            from django_bolt.admin.asgi_bridge import ASGIFallbackHandler
            self.api._asgi_handler = ASGIFallbackHandler(host, port)

        # Register each view, continuing on error instead of failing on first error
        failed_routes = []
        for path_pattern, view, methods in views:
            try:
                for method in methods:
                    self._register_single_route(method, path_pattern, view)
            except ValueError as e:
                # Log the error but continue with other routes
                failed_routes.append((path_pattern, str(e)))
                import sys
                print(f"[django-bolt] Skipped route {path_pattern}: {e}", file=sys.stderr)

        # If we had any failures, report them
        if failed_routes:
            import sys
            print(f"[django-bolt] Note: {len(failed_routes)} route(s) could not be registered due to pattern validation", file=sys.stderr)

    def _is_valid_pattern(self, path_pattern: str) -> bool:
        """Check if a path pattern is valid for matchit router.

        Args:
            path_pattern: The path pattern to validate

        Returns:
            True if valid, False otherwise
        """
        # Check for catch-all in the middle
        if '{' in path_pattern and ':path}' in path_pattern:
            # Catch-all must be at the end
            if not path_pattern.endswith(':path}'):
                return False

        # Check for valid pattern syntax
        try:
            # Patterns should have matching braces
            open_count = path_pattern.count('{')
            close_count = path_pattern.count('}')
            if open_count != close_count:
                return False

            # Should not have invalid characters
            if any(c in path_pattern for c in ['\\', '^', '$', '+', '*', '?', '|', '(', ')']):
                return False
        except Exception:
            return False

        return True

    def _register_single_route(self, method: str, path_pattern: str, view: Callable) -> None:
        """Register a single Django view route.

        Args:
            method: HTTP method (GET, POST, etc.)
            path_pattern: URL path pattern
            view: Django view callable
        """
        # Final validation of the pattern
        if not self._is_valid_pattern(path_pattern):
            raise ValueError(f"Invalid pattern for router: {path_pattern}")

        # Create handler that delegates to ASGI bridge with url_route info
        # This skips Django's URL resolution
        def make_django_view_handler(asgi_handler, django_view):
            async def django_view_handler(request: Dict[str, Any]) -> tuple:
                # Extract path parameters from django-bolt's request dict
                # These were already extracted by matchit router
                path_kwargs = request.get("params", {})

                # Create url_route dict to skip Django URL resolution
                url_route = {
                    "view": django_view,
                    "kwargs": path_kwargs,
                    "url_name": None,
                    "app_names": [],
                    "namespaces": [],
                    "route": path_pattern,
                }

                # Call ASGI handler with url_route to skip Django URL resolution
                return await asgi_handler.handle_request(request, url_route=url_route)

            return django_view_handler

        django_handler = make_django_view_handler(self.api._asgi_handler, view)

        # Register the route using internal route registration
        handler_id = self.api._next_handler_id
        self.api._next_handler_id += 1

        self.api._routes.append((method, path_pattern, handler_id, django_handler))
        self.api._handlers[handler_id] = django_handler

        # Create minimal metadata for Django view handlers
        meta = {
            "mode": "request_only",
            "sig": None,
            "fields": [],
            "is_django_view": True,  # Flag for debugging/identification
        }
        self.api._handler_meta[django_handler] = meta

"""
Django admin route registration for BoltAPI.

This module handles registration of Django admin via ASGI mounts.
"""

from typing import TYPE_CHECKING, Any

from django.core.asgi import get_asgi_application

from django_bolt.admin.admin_detection import detect_admin_url_prefix, should_enable_admin

if TYPE_CHECKING:
    from django_bolt.api import BoltAPI


class AdminRouteRegistrar:
    """Handles registration of Django admin via ASGI mount."""

    def __init__(self, api: "BoltAPI"):
        """Initialize the registrar with a BoltAPI instance.

        Args:
            api: The BoltAPI instance to register routes on
        """
        self.api = api

    def register_routes(self, host: str = "localhost", port: int = 8000) -> None:
        """Register Django admin using mount_asgi().

        host/port are accepted for backward compatibility and ignored.
        """
        _ = (host, port)
        if self.api._admin_routes_registered:
            return

        if not should_enable_admin():
            return

        admin_prefix = detect_admin_url_prefix()
        if not admin_prefix:
            return

        mount_path = f"/{admin_prefix.strip('/')}"
        django_app = get_asgi_application()

        async def admin_mount_wrapper(scope: dict[str, Any], receive: Any, send: Any) -> None:
            if scope.get("type") != "http":
                await django_app(scope, receive, send)
                return

            # Mounted scopes arrive with path stripped to subpath and root_path set to mount prefix.
            # For Django admin URL resolution, restore full path and clear root_path so URLconf
            # containing /admin/... patterns resolves correctly.
            subpath = scope.get("path") or "/"
            if not isinstance(subpath, str):
                subpath = str(subpath)
            if not subpath.startswith("/"):
                subpath = "/" + subpath

            full_path = f"{mount_path}/" if subpath == "/" else f"{mount_path}{subpath}"
            full_raw_path = full_path.encode("utf-8")

            raw_path_obj = scope.get("raw_path")
            if isinstance(raw_path_obj, memoryview):
                raw_path = raw_path_obj.tobytes()
            elif isinstance(raw_path_obj, (bytes, bytearray)):
                raw_path = bytes(raw_path_obj)
            elif isinstance(raw_path_obj, str):
                raw_path = raw_path_obj.encode("utf-8")
            else:
                raw_path = subpath.encode("utf-8")

            if not raw_path.startswith(mount_path.encode("utf-8")):
                full_raw_path = mount_path.encode("utf-8") + raw_path

            django_scope = dict(scope)
            django_scope["path"] = full_path
            django_scope["raw_path"] = full_raw_path
            django_scope["root_path"] = ""

            await django_app(django_scope, receive, send)

        self.api.mount_asgi(mount_path, admin_mount_wrapper)
        self.api._admin_routes_registered = True

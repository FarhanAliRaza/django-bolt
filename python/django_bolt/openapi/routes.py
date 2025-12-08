"""
OpenAPI route registration for BoltAPI.

This module handles the registration of OpenAPI documentation routes
(JSON, YAML, and UI plugins) separately from the main BoltAPI class.
"""
from typing import Dict, Any, TYPE_CHECKING

from django_bolt.openapi.plugins import JsonRenderPlugin, YamlRenderPlugin
from django_bolt.openapi.schema_generator import SchemaGenerator
from django_bolt.responses import HTML, JSON, PlainText

if TYPE_CHECKING:
    from django_bolt.api import BoltAPI


class OpenAPIRouteRegistrar:
    """Handles registration of OpenAPI documentation routes."""

    def __init__(self, api: 'BoltAPI'):
        """Initialize the registrar with a BoltAPI instance.

        Args:
            api: The BoltAPI instance to register routes on
        """
        self.api = api

    def register_routes(self) -> None:
        """Register OpenAPI documentation routes.

        This registers:
        - /docs/openapi.json - JSON schema endpoint
        - /docs/openapi.yaml - YAML schema endpoint
        - /docs/openapi.yml - YAML schema endpoint (alternative)
        - UI plugin routes (e.g., /docs/swagger, /docs/redoc)
        - Root redirect to default UI
        """
        if not self.api.openapi_config or self.api._openapi_routes_registered:
            return

        # Always register JSON endpoint
        json_plugin = JsonRenderPlugin()

        @self.api.get(f"{self.api.openapi_config.path}/openapi.json")
        async def openapi_json_handler(request):
            """Serve OpenAPI schema as JSON."""
            try:
                schema = self._get_schema()
                rendered = json_plugin.render(schema, "")
                # Return with proper OpenAPI JSON content-type
                return JSON(
                    rendered,
                    status_code=200,
                    headers={"content-type": json_plugin.media_type}
                )
            except Exception as e:
                # Re-raise with more context for debugging
                raise Exception(f"Failed to generate OpenAPI JSON schema: {type(e).__name__}: {str(e)}") from e

        # Always register YAML endpoints
        yaml_plugin = YamlRenderPlugin()

        @self.api.get(f"{self.api.openapi_config.path}/openapi.yaml")
        async def openapi_yaml_handler(request):
            """Serve OpenAPI schema as YAML."""
            schema = self._get_schema()
            rendered = yaml_plugin.render(schema, "")
            # Return with proper YAML content-type
            return PlainText(
                rendered,
                status_code=200,
                headers={"content-type": yaml_plugin.media_type}
            )

        @self.api.get(f"{self.api.openapi_config.path}/openapi.yml")
        async def openapi_yml_handler(request):
            """Serve OpenAPI schema as YAML (alternative extension)."""
            schema = self._get_schema()
            rendered = yaml_plugin.render(schema, "")
            # Return with proper YAML content-type
            return PlainText(
                rendered,
                status_code=200,
                headers={"content-type": yaml_plugin.media_type}
            )

        # Register UI plugin routes
        self._register_ui_plugins()

        # Add root redirect to default plugin
        self._register_root_redirect()

        self.api._openapi_routes_registered = True

    def _get_schema(self) -> Dict[str, Any]:
        """Get or generate OpenAPI schema.

        Returns:
            OpenAPI schema as dictionary
        """
        if self.api._openapi_schema is None:
            generator = SchemaGenerator(self.api, self.api.openapi_config)
            openapi = generator.generate()
            self.api._openapi_schema = openapi.to_schema()

        return self.api._openapi_schema

    def _register_ui_plugins(self) -> None:
        """Register UI plugin routes (Swagger UI, ReDoc, etc.)."""
        schema_url = f"{self.api.openapi_config.path}/openapi.json"

        for plugin in self.api.openapi_config.render_plugins:
            for plugin_path in plugin.paths:
                full_path = f"{self.api.openapi_config.path}{plugin_path}"

                # Create closure to capture plugin reference
                def make_handler(p):
                    async def ui_handler():
                        """Serve OpenAPI UI."""
                        try:
                            schema = self._get_schema()
                            rendered = p.render(schema, schema_url)
                            # Return with proper content-type from plugin
                            return HTML(
                                rendered,
                                status_code=200,
                                headers={"content-type": p.media_type}
                            )
                        except Exception as e:
                            # Re-raise with more context for debugging
                            raise Exception(
                                f"Failed to render OpenAPI UI plugin {p.__class__.__name__}: "
                                f"{type(e).__name__}: {str(e)}"
                            ) from e
                    return ui_handler

                self.api.get(full_path)(make_handler(plugin))

    def _register_root_redirect(self) -> None:
        """Register root path to serve default UI directly.

        Serves the default UI at the root path instead of redirecting.
        This avoids redirect loops caused by NormalizePath::trim() middleware
        which strips trailing slashes (e.g., /docs/ -> /docs).
        """
        if self.api.openapi_config.default_plugin:
            schema_url = f"{self.api.openapi_config.path}/openapi.json"
            plugin = self.api.openapi_config.default_plugin

            # Capture plugin in closure
            def make_root_handler(p, url):
                async def openapi_root_handler():
                    """Serve default OpenAPI UI at root path."""
                    try:
                        schema = self._get_schema()
                        rendered = p.render(schema, url)
                        return HTML(
                            rendered,
                            status_code=200,
                            headers={"content-type": p.media_type}
                        )
                    except Exception as e:
                        raise Exception(
                            f"Failed to render OpenAPI UI: {type(e).__name__}: {str(e)}"
                        ) from e
                return openapi_root_handler

            self.api.get(self.api.openapi_config.path)(make_root_handler(plugin, schema_url))

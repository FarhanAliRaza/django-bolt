from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional, List, Dict

from .spec import (
    Components,
    Contact,
    ExternalDocumentation,
    Info,
    License,
    OpenAPI,
    PathItem,
    Reference,
    SecurityRequirement,
    Server,
    Tag,
)

if TYPE_CHECKING:
    from .plugins import OpenAPIRenderPlugin

__all__ = ("OpenAPIConfig",)


@dataclass
class OpenAPIConfig:
    """Configuration for OpenAPI documentation generation.

    Pass an instance of this class to BoltAPI to enable OpenAPI schema
    generation and interactive documentation UIs.

    Example:
        ```python
        from django_bolt import BoltAPI
        from django_bolt.openapi import OpenAPIConfig, SwaggerRenderPlugin

        api = BoltAPI(
            openapi_config=OpenAPIConfig(
                title="My API",
                version="1.0.0",
                render_plugins=[SwaggerRenderPlugin()]
            )
        )
        ```
    """

    title: str
    """Title of API documentation."""

    version: str
    """API version, e.g. '1.0.0'."""

    contact: Optional[Contact] = field(default=None)
    """API contact information."""

    description: Optional[str] = field(default=None)
    """API description."""

    external_docs: Optional[ExternalDocumentation] = field(default=None)
    """Links to external documentation."""

    license: Optional[License] = field(default=None)
    """API licensing information."""

    security: Optional[List[SecurityRequirement]] = field(default=None)
    """API security requirements."""

    components: Components = field(default_factory=Components)
    """API components (schemas, security schemes, etc.)."""

    servers: List[Server] = field(default_factory=lambda: [Server(url="/")])
    """A list of Server instances."""

    summary: Optional[str] = field(default=None)
    """A summary text."""

    tags: Optional[List[Tag]] = field(default=None)
    """A list of Tag instances for grouping operations."""

    terms_of_service: Optional[str] = field(default=None)
    """URL to page that contains terms of service."""

    use_handler_docstrings: bool = field(default=True)
    """Draw operation description from route handler docstring if not otherwise provided."""

    webhooks: Optional[Dict[str, PathItem | Reference]] = field(default=None)
    """A mapping of webhook name to PathItem or Reference."""

    path: str = "/schema"
    """Base path for the OpenAPI documentation endpoints."""

    render_plugins: List[OpenAPIRenderPlugin] = field(default_factory=lambda: [])
    """Plugins for rendering OpenAPI documentation UIs.

    If empty, ScalarRenderPlugin will be used by default.
    """

    def __post_init__(self) -> None:
        """Initialize default render plugin if none provided."""
        if not self.render_plugins:
            from .plugins import ScalarRenderPlugin
            self.render_plugins = [ScalarRenderPlugin()]

        # Normalize path
        self.path = "/" + self.path.strip("/")

        # Find default plugin (one that serves root path)
        self.default_plugin: Optional[OpenAPIRenderPlugin] = None
        for plugin in self.render_plugins:
            if plugin.has_path("/"):
                self.default_plugin = plugin
                break

        # If no root plugin, use first plugin as default
        if not self.default_plugin and self.render_plugins:
            self.default_plugin = self.render_plugins[0]

    def to_openapi_schema(self) -> OpenAPI:
        """Convert config to OpenAPI schema object.

        Returns:
            An OpenAPI instance with info populated from config.
        """
        return OpenAPI(
            external_docs=self.external_docs,
            security=self.security,
            components=self.components,
            servers=self.servers,
            tags=self.tags,
            webhooks=self.webhooks,
            info=Info(
                title=self.title,
                version=self.version,
                description=self.description,
                contact=self.contact,
                license=self.license,
                summary=self.summary,
                terms_of_service=self.terms_of_service,
            ),
            paths={},  # Will be populated by schema generator
        )

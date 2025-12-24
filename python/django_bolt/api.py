from __future__ import annotations

import contextvars
import inspect
import logging
import re
import sys
import time
import types
from collections.abc import Callable
from functools import partial
from typing import Annotated, Any, get_args, get_origin, get_type_hints

import msgspec

# Django import - may fail if Django not configured
try:
    from django.conf import settings as django_settings
except ImportError:
    django_settings = None


# Import local modules
from django.utils.functional import SimpleLazyObject

from . import _json
from .admin.routes import AdminRouteRegistrar
from .admin.static_routes import StaticRouteRegistrar
from .analysis import analyze_handler, warn_blocking_handler
from .auth import get_default_authentication_classes, register_auth_backend
from .auth.user_loader import load_user_sync

# Import modularized components
from .binding import (
    convert_primitive,
    create_extractor_for_field,
    get_msgspec_decoder,
)
from .concurrency import sync_to_thread
from .decorators import ActionHandler
from .dependencies import resolve_dependency
from .error_handlers import handle_exception
from .exceptions import HTTPException, RequestValidationError, parse_msgspec_decode_error
from .logging.middleware import LoggingMiddleware, create_logging_middleware
from .middleware import CompressionConfig
from .middleware.compiler import add_optimization_flags_to_metadata, compile_middleware_meta
from .middleware.django_loader import load_django_middleware
from .middleware_response import MiddlewareResponse
from .openapi import (
    OpenAPIConfig,
    RapidocRenderPlugin,
    RedocRenderPlugin,
    ScalarRenderPlugin,
    StoplightRenderPlugin,
    SwaggerRenderPlugin,
)
from .openapi.routes import OpenAPIRouteRegistrar
from .openapi.schema_generator import SchemaGenerator
from .params import Depends as DependsMarker
from .params import Param
from .request_parsing import parse_form_data
from .router import Router
from .serialization import serialize_response
from .status_codes import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from .typing import FieldDefinition, HandlerMetadata, HandlerPattern, is_msgspec_struct
from .views import APIView, ViewSet
from .websocket import WebSocket as WebSocketType
from .websocket import mark_websocket_handler

Response = tuple[int, list[tuple[str, str]], bytes]


# Global registry for BoltAPI instances (used by autodiscovery)
_BOLT_API_REGISTRY = []

# Pre-compiled regex pattern for extracting path parameters
_PATH_PARAM_REGEX = re.compile(r'\{(\w+)\}')


def _extract_path_params(path: str) -> set[str]:
    """
    Extract path parameter names from a route pattern.

    Examples:
        "/users/{user_id}" -> {"user_id"}
        "/posts/{post_id}/comments/{comment_id}" -> {"post_id", "comment_id"}
    """
    return set(_PATH_PARAM_REGEX.findall(path))


def extract_parameter_value(
    field: FieldDefinition,
    request: dict[str, Any],
    params_map: dict[str, Any],
    query_map: dict[str, Any],
    headers_map: dict[str, str],
    cookies_map: dict[str, str],
    form_map: dict[str, Any],
    files_map: dict[str, Any],
    meta: HandlerMetadata,
    body_obj: Any,
    body_loaded: bool
) -> tuple[Any, Any, bool]:
    """
    Extract value for a handler parameter using FieldDefinition.

    Args:
        field: FieldDefinition object describing the parameter
        request: Request dictionary
        params_map: Path parameters
        query_map: Query parameters
        headers_map: Request headers
        cookies_map: Request cookies
        form_map: Form data
        files_map: Uploaded files
        meta: Handler metadata
        body_obj: Cached body object
        body_loaded: Whether body has been loaded

    Returns:
        Tuple of (value, body_obj, body_loaded)
    """
    name = field.name
    annotation = field.annotation
    default = field.default
    source = field.source
    alias = field.alias
    key = alias or name

    # Handle different sources
    if source == "path":
        if key in params_map:
            return convert_primitive(str(params_map[key]), annotation), body_obj, body_loaded
        raise HTTPException(status_code=422, detail=f"Missing required path parameter: {key}")

    elif source == "query":
        if key in query_map:
            return convert_primitive(str(query_map[key]), annotation), body_obj, body_loaded
        elif field.is_optional:
            return (None if default is inspect.Parameter.empty else default), body_obj, body_loaded
        raise HTTPException(status_code=422, detail=f"Missing required query parameter: {key}")

    elif source == "header":
        lower_key = key.lower()
        if lower_key in headers_map:
            return convert_primitive(str(headers_map[lower_key]), annotation), body_obj, body_loaded
        elif field.is_optional:
            return (None if default is inspect.Parameter.empty else default), body_obj, body_loaded
        raise HTTPException(status_code=422, detail=f"Missing required header: {key}")

    elif source == "cookie":
        if key in cookies_map:
            return convert_primitive(str(cookies_map[key]), annotation), body_obj, body_loaded
        elif field.is_optional:
            return (None if default is inspect.Parameter.empty else default), body_obj, body_loaded
        raise HTTPException(status_code=422, detail=f"Missing required cookie: {key}")

    elif source == "form":
        if key in form_map:
            return convert_primitive(str(form_map[key]), annotation), body_obj, body_loaded
        elif field.is_optional:
            return (None if default is inspect.Parameter.empty else default), body_obj, body_loaded
        raise HTTPException(status_code=422, detail=f"Missing required form field: {key}")

    elif source == "file":
        if key in files_map:
            file_info = files_map[key]
            # Use pre-computed type properties from FieldDefinition (no runtime introspection)
            unwrapped_type = field.unwrapped_annotation
            origin = field.origin

            if unwrapped_type is bytes:
                # For bytes annotation, extract content from single file
                if isinstance(file_info, list):
                    # Multiple files, but bytes expects single - take first
                    return file_info[0].get("content", b""), body_obj, body_loaded
                return file_info.get("content", b""), body_obj, body_loaded
            elif origin is list:
                # For list annotation, ensure value is a list
                if isinstance(file_info, list):
                    return file_info, body_obj, body_loaded
                else:
                    # Wrap single file in list
                    return [file_info], body_obj, body_loaded
            else:
                # Return full file info for dict/Any annotations
                if isinstance(file_info, list):
                    # List but annotation doesn't expect list - take first
                    return file_info[0], body_obj, body_loaded
                return file_info, body_obj, body_loaded
        elif field.is_optional:
            return (None if default is inspect.Parameter.empty else default), body_obj, body_loaded
        raise HTTPException(status_code=422, detail=f"Missing required file: {key}")

    elif source == "body":
        # Handle body parameter
        if meta.get("body_struct_param") == name:
            if not body_loaded:
                body_bytes: bytes = request["body"]
                if is_msgspec_struct(meta["body_struct_type"]):

                    decoder = get_msgspec_decoder(meta["body_struct_type"])
                    try:
                        value = decoder.decode(body_bytes)
                    except msgspec.ValidationError:
                        # Re-raise ValidationError as-is (field validation errors handled by error_handlers.py)
                        # IMPORTANT: Must catch ValidationError BEFORE DecodeError since ValidationError subclasses DecodeError
                        raise
                    except msgspec.DecodeError as e:
                        # JSON parsing error (malformed JSON) - return 422 with error details including line/column
                        error_detail = parse_msgspec_decode_error(e, body_bytes)
                        raise RequestValidationError(
                            errors=[error_detail],
                            body=body_bytes,
                        ) from e
                else:

                    try:
                        value = msgspec.json.decode(body_bytes, type=meta["body_struct_type"])
                    except msgspec.ValidationError:
                        # Re-raise ValidationError as-is (field validation errors handled by error_handlers.py)
                        # IMPORTANT: Must catch ValidationError BEFORE DecodeError since ValidationError subclasses DecodeError
                        raise
                    except msgspec.DecodeError as e:
                        # JSON parsing error (malformed JSON) - return 422 with error details including line/column
                        error_detail = parse_msgspec_decode_error(e, body_bytes)
                        raise RequestValidationError(
                            errors=[error_detail],
                            body=body_bytes,
                        ) from e
                return value, value, True
            else:
                return body_obj, body_obj, body_loaded
        else:
            if field.is_optional:
                return (None if default is inspect.Parameter.empty else default), body_obj, body_loaded
            raise HTTPException(status_code=422, detail=f"Missing required parameter: {name}")

    else:
        # Unknown source
        if field.is_optional:
            return (None if default is inspect.Parameter.empty else default), body_obj, body_loaded
        raise HTTPException(status_code=422, detail=f"Missing required parameter: {name}")

class BoltAPI:
    def __init__(
        self,
        prefix: str = "",
        middleware: list[Any] | None = None,
        middleware_config: dict[str, Any] | None = None,
        django_middleware: bool | list[str] | dict[str, Any] | None = None,
        enable_logging: bool = True,
        logging_config: Any | None = None,
        compression: Any | None = None,
        openapi_config: Any | None = None,
    ) -> None:
        """
        Initialize a BoltAPI instance.

        Args:
            prefix: URL prefix for all routes (e.g., "/api/v1")
            middleware: List of Bolt middleware instances
            middleware_config: Dict-based middleware configuration (legacy)
            django_middleware: Django middleware configuration. Can be:
                - True: Use all middleware from settings.MIDDLEWARE (excluding CSRF, etc.)
                - False/None: Don't use Django middleware
                - List[str]: Use only these specific Django middleware
                - Dict with "include"/"exclude" keys for fine control
            enable_logging: Enable request/response logging
            logging_config: Custom logging configuration
            compression: Compression configuration (CompressionConfig or False to disable)
            openapi_config: OpenAPI documentation configuration
        """
        self._routes: list[tuple[str, str, int, Callable]] = []
        self._websocket_routes: list[tuple[str, int, Callable]] = []  # (path, handler_id, handler)
        self._handlers: dict[int, Callable] = {}
        # OPTIMIZATION: Use handler_id (int) as key instead of callable
        # Integer hashing is O(1) with minimal overhead vs callable hashing
        self._handler_meta: dict[int, HandlerMetadata] = {}
        self._handler_middleware: dict[int, dict[str, Any]] = {}  # Middleware metadata per handler
        self._next_handler_id = 0
        self.prefix = prefix.rstrip("/")  # Remove trailing slash

        # Build middleware list: Django middleware first, then custom middleware
        self.middleware = []

        # Load Django middleware if configured
        # Store flag for optimization bypass (Django middleware needs cookies/headers)
        self._has_django_middleware = bool(django_middleware)
        if django_middleware:
            self.middleware.extend(load_django_middleware(django_middleware))

        # Add custom middleware
        if middleware:
            self.middleware.extend(middleware)

        self.middleware_config = middleware_config or {}

        # Logging configuration (opt-in, setup happens at server startup)
        self.enable_logging = enable_logging
        self._logging_middleware = None

        if self.enable_logging:
            # Create logging middleware (actual logging setup happens at server startup)
            if logging_config is not None:
                self._logging_middleware = LoggingMiddleware(logging_config)
            else:
                # Use default logging configuration
                self._logging_middleware = create_logging_middleware()

        # Compression configuration
        # compression=None means disabled, not providing compression arg means default enabled
        if compression is False:
            # Explicitly disabled
            self.compression = None
        elif compression is None:
            # Not provided, use default
            self.compression = CompressionConfig()
        else:
            # Custom config provided
            self.compression = compression

        # OpenAPI configuration - enabled by default with sensible defaults
        if openapi_config is None:
            # Create default OpenAPI config
            try:
                # Try to get Django project name from settings
                title = getattr(django_settings, 'PROJECT_NAME', None) or getattr(django_settings, 'SITE_NAME', None) or "API" if django_settings else "API"
            except Exception:
                title = "API"

            self.openapi_config = OpenAPIConfig(
                title=title,
                version="1.0.0",
                path="/docs",
                render_plugins=[
                    SwaggerRenderPlugin(path="/"),
                    RedocRenderPlugin(path="/redoc"),
                    ScalarRenderPlugin(path="/scalar"),
                    RapidocRenderPlugin(path="/rapidoc"),
                    StoplightRenderPlugin(path="/stoplight"),
                ]
            )
        else:
            self.openapi_config = openapi_config

        self._openapi_schema: dict[str, Any] | None = None
        self._openapi_routes_registered = False

        # Django admin configuration (controlled by --no-admin flag)
        self._admin_routes_registered = False
        self._static_routes_registered = False
        self._asgi_handler = None

        # Middleware chain (built lazily on first request)
        self._middleware_chain_built = False
        self._middleware_chain = None  # Will be the outermost middleware instance

        # Handler-to-API mapping for merged APIs (initialized here to avoid hasattr in hot path)
        self._handler_api_map: dict[int, BoltAPI] = {}

        # Register this instance globally for autodiscovery
        _BOLT_API_REGISTRY.append(self)

    def get(
        self,
        path: str,
        *,
        response_model: Any | None = None,
        status_code: int | None = None,
        guards: list[Any] | None = None,
        auth: list[Any] | None = None,
        tags: list[str] | None = None,
        summary: str | None = None,
        description: str | None = None,
    ):
        return self._route_decorator("GET", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth, tags=tags, summary=summary, description=description)

    def post(
        self,
        path: str,
        *,
        response_model: Any | None = None,
        status_code: int | None = None,
        guards: list[Any] | None = None,
        auth: list[Any] | None = None,
        tags: list[str] | None = None,
        summary: str | None = None,
        description: str | None = None,
    ):
        return self._route_decorator("POST", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth, tags=tags, summary=summary, description=description)

    def put(
        self,
        path: str,
        *,
        response_model: Any | None = None,
        status_code: int | None = None,
        guards: list[Any] | None = None,
        auth: list[Any] | None = None,
        tags: list[str] | None = None,
        summary: str | None = None,
        description: str | None = None,
    ):
        return self._route_decorator("PUT", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth, tags=tags, summary=summary, description=description)

    def patch(
        self,
        path: str,
        *,
        response_model: Any | None = None,
        status_code: int | None = None,
        guards: list[Any] | None = None,
        auth: list[Any] | None = None,
        tags: list[str] | None = None,
        summary: str | None = None,
        description: str | None = None,
    ):
        return self._route_decorator("PATCH", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth, tags=tags, summary=summary, description=description)

    def delete(
        self,
        path: str,
        *,
        response_model: Any | None = None,
        status_code: int | None = None,
        guards: list[Any] | None = None,
        auth: list[Any] | None = None,
        tags: list[str] | None = None,
        summary: str | None = None,
        description: str | None = None,
    ):
        return self._route_decorator("DELETE", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth, tags=tags, summary=summary, description=description)

    def head(
        self,
        path: str,
        *,
        response_model: Any | None = None,
        status_code: int | None = None,
        guards: list[Any] | None = None,
        auth: list[Any] | None = None,
        tags: list[str] | None = None,
        summary: str | None = None,
        description: str | None = None,
    ):
        return self._route_decorator("HEAD", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth, tags=tags, summary=summary, description=description)

    def options(
        self,
        path: str,
        *,
        response_model: Any | None = None,
        status_code: int | None = None,
        guards: list[Any] | None = None,
        auth: list[Any] | None = None,
        tags: list[str] | None = None,
        summary: str | None = None,
        description: str | None = None,
    ):
        return self._route_decorator("OPTIONS", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth, tags=tags, summary=summary, description=description)

    def websocket(
        self,
        path: str,
        *,
        guards: list[Any] | None = None,
        auth: list[Any] | None = None,
    ):
        """
        Register a WebSocket endpoint with FastAPI-like syntax.

        Usage:
            from django_bolt.websocket import WebSocket

            @api.websocket("/ws")
            async def websocket_endpoint(websocket: WebSocket):
                await websocket.accept()
                while True:
                    data = await websocket.receive_text()
                    await websocket.send_text(f"Echo: {data}")

            @api.websocket("/ws/{room_id}")
            async def room_websocket(websocket: WebSocket, room_id: str):
                await websocket.accept()
                await websocket.send_json({"room": room_id})
                async for message in websocket.iter_json():
                    await websocket.send_json({"echo": message})
        """
        return self._websocket_decorator(path, guards=guards, auth=auth)

    def _websocket_decorator(
        self,
        path: str,
        *,
        guards: list[Any] | None = None,
        auth: list[Any] | None = None,
    ):
        """Internal decorator for WebSocket routes."""

        def decorator(fn: Callable) -> Callable:
            # Ensure handler is async
            if not inspect.iscoroutinefunction(fn):
                raise TypeError(
                    f"WebSocket handler '{fn.__name__}' must be an async function"
                )

            # Mark as WebSocket handler
            fn = mark_websocket_handler(fn)

            # Assign handler ID
            handler_id = self._next_handler_id
            self._next_handler_id += 1

            # Build full path with prefix
            full_path = f"{self.prefix}{path}" if self.prefix else path

            # Store the route
            self._websocket_routes.append((full_path, handler_id, fn))
            self._handlers[handler_id] = fn

            # Compile parameter binder for WebSocket (reuses HTTP binding logic)
            # This enables injection of path params, query params, headers, cookies
            meta = self._compile_websocket_binder(fn, full_path, WebSocketType)
            meta["is_async"] = True
            meta["is_websocket"] = True

            # Compile optimized argument injector (same as HTTP handlers)
            injector = self._compile_argument_injector(meta)
            meta["injector"] = injector
            meta["injector_is_async"] = inspect.iscoroutinefunction(injector)

            self._handler_meta[handler_id] = meta

            # Compile middleware metadata for WebSocket handler
            # Always call compile_middleware_meta to pick up:
            # 1. Handler-level decorators (@rate_limit, @cors, etc.)
            # 2. Global middleware from self.middleware
            # 3. Guards and auth backends
            middleware_meta = compile_middleware_meta(
                handler=fn,
                method="WEBSOCKET",
                path=full_path,
                global_middleware=self.middleware,
                global_middleware_config=self.middleware_config or {},
                guards=guards,
                auth=auth,
            )
            if middleware_meta:
                self._handler_middleware[handler_id] = middleware_meta
                # Store auth backend instances for user resolution
                if auth is not None:
                    middleware_meta['_auth_backend_instances'] = auth

            return fn

        return decorator

    def view(
        self,
        path: str,
        *,
        methods: list[str] | None = None,
        guards: list[Any] | None = None,
        auth: list[Any] | None = None,
        status_code: int | None = None,
    ):
        """
        Register a class-based view as a decorator.

        Usage:
            @api.view("/users")
            class UserView(APIView):
                async def get(self) -> list[User]:
                    return User.objects.all()[:10]

        This method discovers available HTTP method handlers from the view class
        and registers them with the router. It supports the same parameter extraction,
        dependency injection, guards, and authentication as function-based handlers.

        Args:
            path: URL path pattern (e.g., "/users/{user_id}")
            methods: Optional list of HTTP methods to register (defaults to all implemented methods)
            guards: Optional per-route guard overrides (merged with class-level guards)
            auth: Optional per-route auth overrides (merged with class-level auth)
            status_code: Optional per-route status code override

        Returns:
            Decorator function that registers the view class

        Raises:
            ValueError: If view class doesn't implement any requested methods
        """

        def decorator(view_cls: type) -> type:
            # Validate that view_cls is an APIView subclass
            if not issubclass(view_cls, APIView):
                raise TypeError(
                    f"View class {view_cls.__name__} must inherit from APIView"
                )

            # Determine which methods to register
            if methods is None:
                # Auto-discover all implemented methods
                available_methods = view_cls.get_allowed_methods()
                if not available_methods:
                    raise ValueError(
                        f"View class {view_cls.__name__} does not implement any HTTP methods"
                    )
                methods_to_register = [m.lower() for m in available_methods]
            else:
                # Validate requested methods are implemented
                methods_to_register = [m.lower() for m in methods]
                available_methods = {m.lower() for m in view_cls.get_allowed_methods()}
                for method in methods_to_register:
                    if method not in available_methods:
                        raise ValueError(
                            f"View class {view_cls.__name__} does not implement method '{method}'"
                        )

            # Register each method
            for method in methods_to_register:
                method_upper = method.upper()

                # Create handler using as_view()
                handler = view_cls.as_view(method)

                # Merge guards: route-level overrides class-level
                merged_guards = guards
                if merged_guards is None and hasattr(handler, '__bolt_guards__'):
                    merged_guards = handler.__bolt_guards__

                # Merge auth: route-level overrides class-level
                merged_auth = auth
                if merged_auth is None and hasattr(handler, '__bolt_auth__'):
                    merged_auth = handler.__bolt_auth__

                # Merge status_code: route-level overrides class-level
                merged_status_code = status_code
                if merged_status_code is None and hasattr(handler, '__bolt_status_code__'):
                    merged_status_code = handler.__bolt_status_code__

                # Register using existing route decorator
                route_decorator = self._route_decorator(
                    method_upper,
                    path,
                    response_model=None,  # Use method's return annotation
                    status_code=merged_status_code,
                    guards=merged_guards,
                    auth=merged_auth,
                )

                # Apply decorator to register the handler
                route_decorator(handler)

            # Scan for custom action methods (methods decorated with @action)
            # Note: api.view() doesn't have base path context for @action decorator
            # Custom actions with @action should use api.viewset() instead
            self._register_custom_actions(view_cls, base_path=None, lookup_field=None)

            return view_cls

        return decorator

    def viewset(
        self,
        path: str,
        *,
        guards: list[Any] | None = None,
        auth: list[Any] | None = None,
        status_code: int | None = None,
        lookup_field: str = "pk"
    ):
        """
        Register a ViewSet with automatic CRUD route generation as a decorator.

        Usage:
            @api.viewset("/users")
            class UserViewSet(ViewSet):
                async def list(self) -> list[User]:
                    return User.objects.all()[:100]

                async def retrieve(self, id: int) -> User:
                    return await User.objects.aget(id=id)

                @action(methods=["POST"], detail=True)
                async def activate(self, id: int):
                    user = await User.objects.aget(id=id)
                    user.is_active = True
                    await user.asave()
                    return user

        This method auto-generates routes for standard DRF-style actions:
        - list: GET /path (200 OK)
        - create: POST /path (201 Created)
        - retrieve: GET /path/{pk} (200 OK)
        - update: PUT /path/{pk} (200 OK)
        - partial_update: PATCH /path/{pk} (200 OK)
        - destroy: DELETE /path/{pk} (204 No Content)

        Args:
            path: Base URL path (e.g., "/users")
            guards: Optional guards to apply to all routes
            auth: Optional auth backends to apply to all routes
            status_code: Optional default status code (overrides action-specific defaults)
            lookup_field: Field name for object lookup (default: "pk")

        Returns:
            Decorator function that registers the viewset
        """

        def decorator(viewset_cls: type) -> type:
            # Validate that viewset_cls is a ViewSet subclass
            if not issubclass(viewset_cls, ViewSet):
                raise TypeError(
                    f"ViewSet class {viewset_cls.__name__} must inherit from ViewSet"
                )

            # Use lookup_field from ViewSet class if not provided
            actual_lookup_field = lookup_field
            if actual_lookup_field == "pk" and hasattr(viewset_cls, 'lookup_field'):
                actual_lookup_field = viewset_cls.lookup_field

            # Define standard action mappings with HTTP-compliant status codes
            # Format: action_name: (method, path, action_override, default_status_code)
            action_routes = {
                # Collection routes (no pk)
                'list': ('GET', path, None, None),
                'create': ('POST', path, None, HTTP_201_CREATED),

                # Detail routes (with pk)
                'retrieve': ('GET', f"{path}/{{{actual_lookup_field}}}", 'retrieve', None),
                'update': ('PUT', f"{path}/{{{actual_lookup_field}}}", 'update', None),
                'partial_update': ('PATCH', f"{path}/{{{actual_lookup_field}}}", 'partial_update', None),
                'destroy': ('DELETE', f"{path}/{{{actual_lookup_field}}}", 'destroy', HTTP_204_NO_CONTENT),
            }

            # Register routes for each implemented action
            for action_name, (http_method, route_path, action_override, action_status_code) in action_routes.items():
                # Check if the viewset implements this action
                if not hasattr(viewset_cls, action_name):
                    continue

                action_method = getattr(viewset_cls, action_name)
                if not inspect.iscoroutinefunction(action_method):
                    continue

                # Use action name (e.g., "list") not HTTP method name (e.g., "get")
                handler = viewset_cls.as_view(http_method.lower(), action=action_override or action_name)

                # Merge guards and auth
                merged_guards = guards
                if merged_guards is None and hasattr(handler, '__bolt_guards__'):
                    merged_guards = handler.__bolt_guards__

                merged_auth = auth
                if merged_auth is None and hasattr(handler, '__bolt_auth__'):
                    merged_auth = handler.__bolt_auth__

                # Status code priority: explicit status_code param > handler attribute > action default
                merged_status_code = status_code
                if merged_status_code is None and hasattr(handler, '__bolt_status_code__'):
                    merged_status_code = handler.__bolt_status_code__
                if merged_status_code is None:
                    merged_status_code = action_status_code

                # Register the route
                route_decorator = self._route_decorator(
                    http_method,
                    route_path,
                    response_model=None,
                    status_code=merged_status_code,
                    guards=merged_guards,
                    auth=merged_auth
                )
                route_decorator(handler)

            # Scan for custom actions (@action decorator)
            self._register_custom_actions(viewset_cls, base_path=path, lookup_field=actual_lookup_field)

            return viewset_cls

        return decorator

    def _register_custom_actions(self, view_cls: type, base_path: str | None, lookup_field: str | None):
        """
        Scan a ViewSet class for custom action methods and register them.

        Custom actions are methods decorated with @action decorator.

        Args:
            view_cls: The ViewSet class to scan
            base_path: Base path for the ViewSet (e.g., "/users")
            lookup_field: Lookup field name for detail actions (e.g., "id", "pk")
        """

        # Get class-level auth and guards (if any)
        class_auth = getattr(view_cls, 'auth', None)
        class_guards = getattr(view_cls, 'guards', None)

        # Scan all attributes in the class
        for name in dir(view_cls):
            # Skip private attributes and standard action methods
            if name.startswith('_') or name.lower() in [
                'get', 'post', 'put', 'patch', 'delete', 'head', 'options',
                'list', 'retrieve', 'create', 'update', 'partial_update', 'destroy'
            ]:
                continue

            attr = getattr(view_cls, name)

            # Check if it's an ActionHandler instance (decorated with @action)
            if isinstance(attr, ActionHandler):
                # Validate that we have base_path for auto-generation
                if base_path is None:
                    raise ValueError(
                        f"Custom action {view_cls.__name__}.{name} uses @action decorator, "
                        f"but ViewSet was registered with api.view() instead of api.viewset(). "
                        f"Use api.viewset() for automatic action path generation."
                    )

                # Extract the unbound function from the ActionHandler
                unbound_fn = attr.fn

                # Auto-generate route path based on detail flag
                if attr.detail:
                    # Instance-level action: /base_path/{lookup_field}/action_name
                    # Example: /users/{id}/activate
                    action_path = f"{base_path}/{{{lookup_field}}}/{attr.path}"
                else:
                    # Collection-level action: /base_path/action_name
                    # Example: /users/active
                    action_path = f"{base_path}/{attr.path}"

                # Register route for each HTTP method
                for http_method in attr.methods:
                    # Create a wrapper that calls the method as an instance method
                    async def custom_action_handler(
                        *args,
                        __unbound_fn=unbound_fn,
                        __view_cls=view_cls,
                        **kwargs
                    ):
                        """Wrapper for custom action method."""
                        view = __view_cls()
                        # Bind the unbound method to the view instance
                        bound_method = types.MethodType(__unbound_fn, view)
                        return await bound_method(*args, **kwargs)

                    # Preserve signature and annotations from original method
                    sig = inspect.signature(unbound_fn)
                    params = list(sig.parameters.values())[1:]  # Skip 'self'
                    custom_action_handler.__signature__ = sig.replace(parameters=params)
                    custom_action_handler.__annotations__ = {
                        k: v for k, v in unbound_fn.__annotations__.items() if k != 'self'
                    }
                    custom_action_handler.__name__ = f"{view_cls.__name__}.{name}"
                    custom_action_handler.__doc__ = unbound_fn.__doc__
                    custom_action_handler.__module__ = unbound_fn.__module__

                    # Merge class-level auth/guards with action-specific auth/guards
                    # Action-specific takes precedence if explicitly set
                    final_auth = attr.auth if attr.auth is not None else class_auth
                    final_guards = attr.guards if attr.guards is not None else class_guards

                    # Register the custom action
                    decorator = self._route_decorator(
                        http_method,
                        action_path,
                        response_model=attr.response_model,
                        status_code=attr.status_code,
                        guards=final_guards,
                        auth=final_auth,
                        tags=attr.tags,
                        summary=attr.summary,
                        description=attr.description,
                    )
                    decorator(custom_action_handler)

    def _route_decorator(
        self,
        method: str,
        path: str,
        *,
        response_model: Any | None = None,
        status_code: int | None = None,
        guards: list[Any] | None = None,
        auth: list[Any] | None = None,
        tags: list[str] | None = None,
        summary: str | None = None,
        description: str | None = None,
    ):
        def decorator(fn: Callable):
            # Detect if handler is async or sync
            is_async = inspect.iscoroutinefunction(fn)

            handler_id = self._next_handler_id
            self._next_handler_id += 1

            # Apply prefix to path (conversion happens in Rust)
            full_path = self.prefix + path if self.prefix else path

            self._routes.append((method, full_path, handler_id, fn))
            self._handlers[handler_id] = fn

            # Pre-compile parameter binder (handles parameter binding only)
            meta = self._compile_binder(fn, method, full_path)

            # Store sync/async metadata
            meta["is_async"] = is_async

            # Detect csrf_exempt for Django CSRF middleware support
            # Django's @csrf_exempt decorator sets handler.csrf_exempt = True
            meta["csrf_exempt"] = getattr(fn, 'csrf_exempt', False)

            # Static ORM analysis: Detect blocking operations at registration time
            handler_analysis = analyze_handler(fn)
            meta["is_blocking"] = handler_analysis.is_blocking

            # Emit warning for sync handlers with ORM (will run in thread pool)
            warn_blocking_handler(fn, full_path, is_async, handler_analysis)

            # Determine final response type with proper priority:
            # 1. response_model parameter (explicit, takes precedence)
            # 2. sig.return_annotation (fallback if response_model not provided)
            final_response_type = None
            if response_model is not None:
                # Explicit response_model provided - use it (ignore annotation)
                final_response_type = response_model
            else:
                # No response_model - check for return annotation
                # Need to resolve string annotations (from __future__ import annotations)
                globalns = sys.modules.get(fn.__module__, {}).__dict__ if fn.__module__ else {}
                type_hints = get_type_hints(fn, globalns=globalns, include_extras=True)
                final_response_type = type_hints.get("return", None)

            # Extract metadata from final type (after priority resolution)
            if final_response_type is not None:
                meta["response_type"] = final_response_type
                # Pre-compute field names for QuerySet optimization (registration time only)
                response_meta = self._extract_response_metadata(final_response_type)
                meta.update(response_meta)

            if status_code is not None:
                meta["default_status_code"] = int(status_code)
            # Store OpenAPI metadata
            if tags is not None:
                meta["openapi_tags"] = tags
            if summary is not None:
                meta["openapi_summary"] = summary
            if description is not None:
                meta["openapi_description"] = description

            # Compile optimized argument injector (once at registration time)
            # This pre-compiles all parameter extraction logic for maximum performance
            injector = self._compile_argument_injector(meta)
            meta["injector"] = injector
            # Store whether injector is async (avoids runtime check with inspect.iscoroutinefunction)
            meta["injector_is_async"] = inspect.iscoroutinefunction(injector)

            self._handler_meta[handler_id] = meta

            # Compile middleware metadata for this handler (including guards and auth)
            middleware_meta = compile_middleware_meta(
                fn, method, full_path,
                self.middleware, self.middleware_config,
                guards=guards, auth=auth
            )

            # Add optimization flags to middleware metadata
            # These are parsed by Rust's RouteMetadata::from_python() to skip unused parsing
            middleware_meta = add_optimization_flags_to_metadata(middleware_meta, meta)

            # Python middleware requires cookies and headers regardless of handler params
            # Django middleware needs cookies/headers (CSRF, session, auth, etc.)
            # Custom middleware may also inspect headers for routing, auth, etc.
            if self._has_django_middleware or self.middleware:
                middleware_meta['needs_cookies'] = True
                middleware_meta['needs_headers'] = True

            if middleware_meta:
                self._handler_middleware[handler_id] = middleware_meta
                # Also store actual auth backend instances for user resolution
                # (not just metadata) so we can call their get_user() methods
                if auth is not None:
                    middleware_meta['_auth_backend_instances'] = auth
                else:
                    # Store default auth backends if not explicitly set
                    default_backends = get_default_authentication_classes()
                    if default_backends:
                        middleware_meta['_auth_backend_instances'] = default_backends

            return fn
        return decorator

    def _extract_response_metadata(self, response_type: Any) -> dict[str, Any]:
        """
        Extract serialization metadata from response type annotation.

        Pre-computes field names for QuerySet.values() optimization.
        This method is called once at route registration time, not per-request.

        Args:
            response_type: Type annotation (e.g., list[UserMini], User, dict, etc.)

        Returns:
            Metadata dictionary with optional 'response_field_names' key

        Example:
            meta = self._extract_response_metadata(list[UserMini])
            # Returns: {"response_field_names": ["id", "username"]}
        """
        metadata = {}

        # Check if response type is list[Struct] for QuerySet optimization
        origin = get_origin(response_type)
        if origin in (list, list):
            args = get_args(response_type)
            if args:
                elem_type = args[0]
                if is_msgspec_struct(elem_type):
                    # Extract field names for QuerySet.values() optimization
                    # This allows us to do: queryset.values("id", "username")
                    # instead of loading all fields and converting to dict
                    fields = getattr(elem_type, "__annotations__", {})
                    metadata["response_field_names"] = list(fields.keys())

        return metadata

    def _classify_handler_pattern(
        self,
        fields: list[FieldDefinition],
        meta: HandlerMetadata,
        needs_form_parsing: bool
    ) -> HandlerPattern:
        """
        Classify handler into a pattern for specialized injector selection.

        This enables optimized fast paths for common handler patterns,
        eliminating unnecessary checks at request time.

        Returns:
            HandlerPattern enum value for specialized injector selection
        """
        # Check field sources once
        sources = {f.source for f in fields}
        has_deps = "dependency" in sources
        has_request = "request" in sources
        has_headers = "header" in sources

        # Get flags from metadata
        has_path = meta["needs_path_params"]
        has_query = meta["needs_query"]
        has_body = meta["needs_body"]
        has_cookies = meta["needs_cookies"]

        # Priority-ordered pattern matching
        if has_deps:
            return HandlerPattern.WITH_DEPS
        if not fields:
            return HandlerPattern.NO_PARAMS
        if has_request or needs_form_parsing:
            return HandlerPattern.FULL

        # Check for simple patterns (no headers/cookies)
        if has_headers or has_cookies:
            return HandlerPattern.FULL

        # Single-source patterns
        if has_body and not has_path and not has_query:
            return HandlerPattern.BODY_ONLY
        if has_path and not has_query and not has_body:
            return HandlerPattern.PATH_ONLY
        if has_query and not has_path and not has_body:
            return HandlerPattern.QUERY_ONLY
        if (has_path or has_query) and not has_body:
            return HandlerPattern.SIMPLE

        return HandlerPattern.FULL

    def _compile_binder(self, fn: Callable, http_method: str = "", path: str = "") -> HandlerMetadata:
        """
        Compile parameter binding metadata for a handler function.

        This method:
        1. Parses function signature and type hints
        2. Creates FieldDefinition for each parameter
        3. Infers parameter sources (path, query, body, etc.)
        4. Validates HTTP method compatibility
        5. Pre-compiles extractors for performance

        Args:
            fn: Handler function
            http_method: HTTP method (GET, POST, etc.)
            path: Route path pattern

        Returns:
            Metadata dictionary for parameter binding

        Raises:
            TypeError: If GET/HEAD/DELETE/OPTIONS handlers have body parameters
        """
        sig = inspect.signature(fn)
        # Get the correct namespace for resolving string annotations (from __future__ import annotations)
        # Use fn.__module__ to get the module where annotations were defined (especially important for
        # class-based views where the handler wrapper is created in views.py but annotations come from user's module)
        globalns = sys.modules.get(fn.__module__, {}).__dict__ if fn.__module__ else {}
        type_hints = get_type_hints(fn, globalns=globalns, include_extras=True)

        # Extract path parameters from route pattern
        path_params = _extract_path_params(path)

        meta: HandlerMetadata = {
            "sig": sig,
            "fields": [],
            "path_params": path_params,
            "http_method": http_method,
        }

        # Quick path: single parameter that looks like request
        params = list(sig.parameters.values())
        if len(params) == 1 and params[0].name in {"request", "req"}:
            meta["mode"] = "request_only"
            return meta

        # Parse each parameter into FieldDefinition
        field_definitions: list[FieldDefinition] = []

        for param in params:
            name = param.name
            annotation = type_hints.get(name, param.annotation)

            # Extract explicit markers from Annotated or default
            explicit_marker = None

            # Check Annotated[T, ...]
            origin = get_origin(annotation)
            if origin is Annotated:
                args = get_args(annotation)
                annotation = args[0] if args else annotation  # Unwrap to get actual type
                for meta_val in args[1:]:
                    if isinstance(meta_val, (Param, DependsMarker)):
                        explicit_marker = meta_val
                        break

            # Check default value for marker
            if explicit_marker is None and isinstance(param.default, (Param, DependsMarker)):
                explicit_marker = param.default

            # Create FieldDefinition with inference
            field = FieldDefinition.from_parameter(
                parameter=param,
                annotation=annotation,
                path_params=path_params,
                http_method=http_method,
                explicit_marker=explicit_marker,
            )

            # Attach pre-compiled extractor to field (performance optimization)
            # This allows the injector to call the extractor directly without source checking
            extractor = create_extractor_for_field(field)
            if extractor is not None:
                # Use object.__setattr__ since FieldDefinition is frozen
                object.__setattr__(field, "extractor", extractor)

            field_definitions.append(field)

        # HTTP Method Validation: Ensure GET/HEAD/DELETE/OPTIONS don't have body params
        body_fields = [f for f in field_definitions if f.source == "body"]
        if http_method in ("GET", "HEAD", "DELETE", "OPTIONS") and body_fields:
            param_names = [f.name for f in body_fields]
            raise TypeError(
                f"Handler {fn.__name__} for {http_method} {path} cannot have body parameters.\n"
                f"Found body parameters: {param_names}\n"
                f"Solutions:\n"
                f"  1. Change HTTP method to POST/PUT/PATCH\n"
                f"  2. Use Query() marker for query parameters\n"
                f"  3. Use simple types (str, int) which auto-infer as query params"
            )

        # Store FieldDefinition objects directly (Phase 4: completed migration)
        meta["fields"] = field_definitions

        # Detect single body parameter for fast path
        if len(body_fields) == 1:
            body_field = body_fields[0]
            if body_field.is_msgspec_struct:
                meta["body_struct_param"] = body_field.name
                meta["body_struct_type"] = body_field.annotation

        # Response type handling is done in _route_decorator() after priority resolution
        # This keeps _compile_binder() focused on parameter binding only

        meta["mode"] = "mixed"

        # Performance: Check if handler needs form/file parsing
        # This allows us to skip expensive form parsing for 95% of endpoints
        needs_form_parsing = any(f.source in ("form", "file") for f in field_definitions)
        meta["needs_form_parsing"] = needs_form_parsing

        # Static analysis: Determine which request components are actually used
        # This allows skipping unused parsing at request time
        meta["needs_body"] = any(f.source in ("body", "form", "file") for f in field_definitions)
        meta["needs_query"] = any(f.source == "query" for f in field_definitions)
        # Note: Form/File parsing depends on Content-Type header, so needs_headers must include form handlers
        meta["needs_headers"] = any(f.source == "header" for f in field_definitions) or needs_form_parsing
        meta["needs_cookies"] = any(f.source == "cookie" for f in field_definitions)
        meta["needs_path_params"] = any(f.source == "path" for f in field_definitions)

        # Static route detection: routes without path params can use O(1) lookup
        meta["is_static_route"] = len(path_params) == 0

        # Classify handler pattern for specialized injector selection
        meta["handler_pattern"] = self._classify_handler_pattern(
            field_definitions, meta, needs_form_parsing
        )

        return meta

    def _compile_websocket_binder(self, fn: Callable, path: str, websocket_type: type) -> HandlerMetadata:
        """
        Compile parameter binding metadata for a WebSocket handler.

        Similar to _compile_binder but:
        1. Skips the first parameter if it's a WebSocket type (it's injected separately)
        2. No body/form/file parameters (WebSocket doesn't have request body at connect time)
        3. Supports path, query, header, cookie injection

        Args:
            fn: WebSocket handler function
            path: Route path pattern
            websocket_type: The WebSocket class type to detect

        Returns:
            Metadata dictionary for parameter binding
        """
        sig = inspect.signature(fn)
        globalns = sys.modules.get(fn.__module__, {}).__dict__ if fn.__module__ else {}
        type_hints = get_type_hints(fn, globalns=globalns, include_extras=True)

        # Extract path parameters from route pattern
        path_params = _extract_path_params(path)

        meta: HandlerMetadata = {
            "sig": sig,
            "fields": [],
            "path_params": path_params,
            "http_method": "WEBSOCKET",
        }

        params = list(sig.parameters.values())

        # If no params or just websocket param, return empty fields
        if not params:
            meta["mode"] = "websocket_only"
            meta["needs_body"] = False
            meta["needs_query"] = False
            meta["needs_headers"] = False
            meta["needs_cookies"] = False
            meta["needs_path_params"] = False
            meta["needs_form_parsing"] = False
            meta["handler_pattern"] = HandlerPattern.NO_PARAMS
            return meta

        # Parse each parameter into FieldDefinition, skipping WebSocket param
        field_definitions: list[FieldDefinition] = []

        for param in params:
            name = param.name
            annotation = type_hints.get(name, param.annotation)

            # Unwrap Annotated to get the base type
            base_annotation = annotation
            origin = get_origin(annotation)
            if origin is Annotated:
                args = get_args(annotation)
                base_annotation = args[0] if args else annotation

            # Skip WebSocket parameter - it's injected by Rust
            if base_annotation is websocket_type or (
                isinstance(base_annotation, type) and issubclass(base_annotation, websocket_type)
            ):
                continue

            # Also skip if param name is 'websocket' or 'ws' with no annotation
            if name in ("websocket", "ws") and annotation is inspect.Parameter.empty:
                continue

            # Extract explicit markers from Annotated or default
            explicit_marker = None

            if origin is Annotated:
                args = get_args(annotation)
                annotation = args[0] if args else annotation
                for meta_val in args[1:]:
                    if isinstance(meta_val, (Param, DependsMarker)):
                        explicit_marker = meta_val
                        break

            if explicit_marker is None and isinstance(param.default, (Param, DependsMarker)):
                explicit_marker = param.default

            # Create FieldDefinition with inference
            # WebSocket doesn't have body, so primitives should default to query
            field = FieldDefinition.from_parameter(
                parameter=param,
                annotation=annotation,
                path_params=path_params,
                http_method="GET",  # Use GET-like inference (no body)
                explicit_marker=explicit_marker,
            )

            # Attach pre-compiled extractor to field
            extractor = create_extractor_for_field(field)
            if extractor is not None:
                object.__setattr__(field, "extractor", extractor)

            field_definitions.append(field)

        meta["fields"] = field_definitions

        if not field_definitions:
            meta["mode"] = "websocket_only"
            meta["needs_body"] = False
            meta["needs_query"] = False
            meta["needs_headers"] = False
            meta["needs_cookies"] = False
            meta["needs_path_params"] = False
            meta["needs_form_parsing"] = False
            meta["handler_pattern"] = HandlerPattern.NO_PARAMS
            return meta

        meta["mode"] = "mixed"
        meta["needs_form_parsing"] = False  # WebSocket doesn't have form data
        meta["needs_body"] = False  # WebSocket doesn't have body at connect
        meta["needs_query"] = any(f.source == "query" for f in field_definitions)
        meta["needs_headers"] = any(f.source == "header" for f in field_definitions)
        meta["needs_cookies"] = any(f.source == "cookie" for f in field_definitions)
        meta["needs_path_params"] = any(f.source == "path" for f in field_definitions)
        meta["is_static_route"] = len(path_params) == 0

        # Classify pattern for injector optimization
        meta["handler_pattern"] = self._classify_handler_pattern(
            field_definitions, meta, False
        )

        return meta

    async def _build_handler_arguments(self, meta: HandlerMetadata, request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
        """Build arguments for handler invocation."""
        args: list[Any] = []
        kwargs: dict[str, Any] = {}

        # Access PyRequest mappings
        params_map = request["params"]
        query_map = request["query"]
        headers_map = request.get("headers", {})
        cookies_map = request.get("cookies", {})

        # Parse form/multipart data ONLY if handler uses Form() or File() parameters
        # This optimization skips parsing for 95% of endpoints (JSON/GET endpoints)
        if meta.get("needs_form_parsing", False):
            form_map, files_map = parse_form_data(request, headers_map)
        else:
            form_map, files_map = {}, {}

        # Body decode cache
        body_obj: Any = None
        body_loaded: bool = False
        dep_cache: dict[Any, Any] = {}

        # Use FieldDefinition objects directly
        fields = meta["fields"]
        for field in fields:
            if field.source == "request":
                value = request
            elif field.source == "dependency":
                if field.dependency is None:
                    raise ValueError(f"Depends for parameter {field.name} requires a callable")
                value = await resolve_dependency(
                    field.dependency.dependency, field.dependency, request, dep_cache,
                    params_map, query_map, headers_map, cookies_map,
                    self._handler_meta, self._compile_binder,
                    meta.get("http_method", ""), meta.get("path", "")
                )
            else:
                value, body_obj, body_loaded = extract_parameter_value(
                    field, request, params_map, query_map, headers_map, cookies_map,
                    form_map, files_map, meta, body_obj, body_loaded
                )

            # Respect positional-only/keyword-only kinds
            if field.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                args.append(value)
            else:
                kwargs[field.name] = value

        return args, kwargs

    def _compile_argument_injector(self, meta: HandlerMetadata) -> Callable[[dict[str, Any]], tuple[list[Any], dict[str, Any]]]:
        """
        Compile a specialized argument injector function for a handler.

        This method creates a closure that captures all parameter extraction logic
        at route registration time, eliminating the overhead of _build_handler_arguments()
        at request time.

        The compiled injector is stored in meta["injector"] and returns a tuple of
        (args, kwargs) ready for handler invocation.

        Args:
            meta: Handler metadata containing field definitions

        Returns:
            Injector function that takes request dict and returns (args, kwargs)

        Performance benefits:
            - Eliminates function call overhead (_build_handler_arguments)
            - Pre-compiles all parameter extraction logic
            - Reduces branching with specialized paths for common cases
            - Better CPU cache locality with single inline function
            - Skips unused request data access based on static analysis
            - Uses pre-compiled extractors (eliminates source type checking)
        """
        fields = meta.get("fields", [])
        mode = meta.get("mode", "mixed")
        pattern = meta.get("handler_pattern", HandlerPattern.FULL)

        # Fast path 1: Request-only mode (single request parameter)
        if mode == "request_only":
            def injector_request_only(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
                return ([request], {})
            return injector_request_only

        # Fast path 2: No parameters
        if not fields or pattern is HandlerPattern.NO_PARAMS:
            def injector_no_params(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
                return ([], {})
            return injector_no_params

        # Fast path 3: Path-only parameters (e.g., GET /users/{id})
        # Uses pre-compiled extractors directly on params_map
        if pattern is HandlerPattern.PATH_ONLY:
            # Pre-compute extractors list for direct access
            extractors = [(f.extractor, f.kind, f.name) for f in fields]

            def injector_path_only(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
                params_map = request["params"]
                args: list[Any] = []
                kwargs: dict[str, Any] = {}
                for extractor, kind, name in extractors:
                    value = extractor(params_map)
                    if kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                        args.append(value)
                    else:
                        kwargs[name] = value
                return args, kwargs
            return injector_path_only

        # Fast path 4: Query-only parameters (e.g., GET /search?q=...)
        if pattern is HandlerPattern.QUERY_ONLY:
            extractors = [(f.extractor, f.kind, f.name) for f in fields]

            def injector_query_only(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
                query_map = request["query"]
                args: list[Any] = []
                kwargs: dict[str, Any] = {}
                for extractor, kind, name in extractors:
                    value = extractor(query_map)
                    if kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                        args.append(value)
                    else:
                        kwargs[name] = value
                return args, kwargs
            return injector_query_only

        # Fast path 5: Body-only parameters (e.g., POST with single JSON struct)
        if pattern is HandlerPattern.BODY_ONLY and len(fields) == 1:
            field = fields[0]
            body_extractor = field.extractor
            is_positional = field.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            field_name = field.name

            if is_positional:
                def injector_body_only_positional(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
                    body_bytes = request["body"]
                    return ([body_extractor(body_bytes)], {})
                return injector_body_only_positional
            else:
                def injector_body_only_kwarg(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
                    body_bytes = request["body"]
                    return ([], {field_name: body_extractor(body_bytes)})
                return injector_body_only_kwarg

        # Fast path 6: Simple pattern (path + query, no body/headers/cookies)
        if pattern is HandlerPattern.SIMPLE:
            # Pre-categorize fields by source for direct access
            path_fields = [(f.extractor, f.kind, f.name) for f in fields if f.source == "path"]
            query_fields = [(f.extractor, f.kind, f.name) for f in fields if f.source == "query"]
            # Maintain original field order for args
            field_order = [(f.source, i) for i, f in enumerate(fields)]

            def injector_simple(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
                params_map = request["params"]
                query_map = request["query"]
                args: list[Any] = []
                kwargs: dict[str, Any] = {}

                # Extract in original field order
                path_idx = 0
                query_idx = 0
                for source, _ in field_order:
                    if source == "path":
                        extractor, kind, name = path_fields[path_idx]
                        value = extractor(params_map)
                        path_idx += 1
                    else:  # query
                        extractor, kind, name = query_fields[query_idx]
                        value = extractor(query_map)
                        query_idx += 1

                    if kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                        args.append(value)
                    else:
                        kwargs[name] = value
                return args, kwargs
            return injector_simple

        # Dependency injection path (async required)
        if pattern is HandlerPattern.WITH_DEPS:
            needs_form = meta.get("needs_form_parsing", False)
            needs_query = meta.get("needs_query", True)
            needs_headers = meta.get("needs_headers", True)
            needs_cookies = meta.get("needs_cookies", True)
            needs_path_params = meta.get("needs_path_params", True)

            async def injector_with_deps(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
                """Optimized argument injector with dependency support."""
                args: list[Any] = []
                kwargs: dict[str, Any] = {}

                params_map = request["params"] if needs_path_params else {}
                query_map = request["query"] if needs_query else {}
                headers_map = request.get("headers", {}) if needs_headers else {}
                cookies_map = request.get("cookies", {}) if needs_cookies else {}

                if needs_form:
                    form_map, files_map = parse_form_data(request, headers_map)
                else:
                    form_map, files_map = {}, {}

                body_obj: Any = None
                body_loaded: bool = False
                dep_cache: dict[Any, Any] = {}

                for field in fields:
                    if field.source == "request":
                        value = request
                    elif field.source == "dependency":
                        if field.dependency is None:
                            raise ValueError(f"Depends for parameter {field.name} requires a callable")
                        value = await resolve_dependency(
                            field.dependency.dependency, field.dependency, request, dep_cache,
                            params_map, query_map, headers_map, cookies_map,
                            self._handler_meta, self._compile_binder,
                            meta.get("http_method", ""), meta.get("path", "")
                        )
                    elif field.extractor is not None:
                        # Use pre-compiled extractor
                        source = field.source
                        if source == "path":
                            value = field.extractor(params_map)
                        elif source == "query":
                            value = field.extractor(query_map)
                        elif source == "header":
                            value = field.extractor(headers_map)
                        elif source == "cookie":
                            value = field.extractor(cookies_map)
                        elif source == "form":
                            value = field.extractor(form_map)
                        elif source == "file":
                            value = field.extractor(files_map)
                        elif source == "body":
                            if not body_loaded:
                                body_obj = field.extractor(request["body"])
                                body_loaded = True
                            value = body_obj
                        else:
                            value, body_obj, body_loaded = extract_parameter_value(
                                field, request, params_map, query_map, headers_map, cookies_map,
                                form_map, files_map, meta, body_obj, body_loaded
                            )
                    else:
                        value, body_obj, body_loaded = extract_parameter_value(
                            field, request, params_map, query_map, headers_map, cookies_map,
                            form_map, files_map, meta, body_obj, body_loaded
                        )

                    if field.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                        args.append(value)
                    else:
                        kwargs[field.name] = value

                return args, kwargs
            return injector_with_deps

        # Full pattern (form, headers, cookies, or complex combinations)
        # Uses pre-compiled extractors with source-based dispatch
        needs_form = meta.get("needs_form_parsing", False)
        needs_query = meta.get("needs_query", True)
        needs_headers = meta.get("needs_headers", True)
        needs_cookies = meta.get("needs_cookies", True)
        needs_path_params = meta.get("needs_path_params", True)

        def injector_full(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
            """Full injector with pre-compiled extractors."""
            args: list[Any] = []
            kwargs: dict[str, Any] = {}

            params_map = request["params"] if needs_path_params else {}
            query_map = request["query"] if needs_query else {}
            headers_map = request.get("headers", {}) if needs_headers else {}
            cookies_map = request.get("cookies", {}) if needs_cookies else {}

            if needs_form:
                form_map, files_map = parse_form_data(request, headers_map)
            else:
                form_map, files_map = {}, {}

            body_obj: Any = None
            body_loaded: bool = False

            for field in fields:
                if field.source == "request":
                    value = request
                elif field.extractor is not None:
                    # Use pre-compiled extractor based on source
                    source = field.source
                    if source == "path":
                        value = field.extractor(params_map)
                    elif source == "query":
                        value = field.extractor(query_map)
                    elif source == "header":
                        value = field.extractor(headers_map)
                    elif source == "cookie":
                        value = field.extractor(cookies_map)
                    elif source == "form":
                        value = field.extractor(form_map)
                    elif source == "file":
                        value = field.extractor(files_map)
                    elif source == "body":
                        if not body_loaded:
                            body_obj = field.extractor(request["body"])
                            body_loaded = True
                        value = body_obj
                    else:
                        # Fallback for unknown sources
                        value, body_obj, body_loaded = extract_parameter_value(
                            field, request, params_map, query_map, headers_map, cookies_map,
                            form_map, files_map, meta, body_obj, body_loaded
                        )
                else:
                    # No pre-compiled extractor, use generic extraction
                    value, body_obj, body_loaded = extract_parameter_value(
                        field, request, params_map, query_map, headers_map, cookies_map,
                        form_map, files_map, meta, body_obj, body_loaded
                    )

                if field.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                    args.append(value)
                else:
                    kwargs[field.name] = value

            return args, kwargs

        return injector_full


    def _handle_http_exception(self, he: HTTPException) -> Response:
        """Handle HTTPException and return response."""
        try:
            body = _json.encode({"detail": he.detail})
            headers = [("content-type", "application/json")]
        except Exception:
            body = str(he.detail).encode()
            headers = [("content-type", "text/plain; charset=utf-8")]

        if he.headers:
            headers.extend([(k.lower(), v) for k, v in he.headers.items()])

        return int(he.status_code), headers, body

    def _handle_generic_exception(self, e: Exception, request: dict[str, Any] = None) -> Response:
        """Handle generic exception using error_handlers module."""
        # Use the error handler which respects Django DEBUG setting
        return handle_exception(e, debug=None, request=request)  # debug will be checked dynamically

    def _build_middleware_chain(self, api: BoltAPI) -> Callable | None:
        """
        Build the middleware chain for an API instance (Django-style).

        Creates a chain where each middleware wraps the next:
        - Outermost middleware is called first
        - Each middleware receives `get_response` (the next layer)
        - Innermost layer is the handler execution

        Args:
            api: The BoltAPI instance to build chain for

        Returns:
            The outermost middleware callable, or None if no middleware
        """
        if not api.middleware:
            return None

        # The innermost "get_response" is a placeholder - it will be replaced per-request
        # by the actual handler execution. We use a sentinel callable here.
        # The real handler dispatch happens in _dispatch_with_middleware.
        return api.middleware  # Return middleware classes for per-request chain building

    async def _dispatch_with_middleware(
        self,
        handler: Callable,
        request: dict[str, Any],
        handler_id: int,
        api: BoltAPI,
        meta: dict[str, Any],
    ) -> Response:
        """
        Execute the middleware chain and then the handler (Django-style).

        Builds the chain ONCE per API and caches it. Uses a context variable to pass
        the actual handler execution to the innermost layer, allowing middleware
        instances to maintain state across requests.

        The inner handler returns a MiddlewareResponse object (not a tuple) so that
        middleware can modify response.headers and response.status_code. After the
        middleware chain completes, we convert back to tuple format.

        Args:
            handler: The route handler function
            request: The request dictionary
            handler_id: Handler ID
            api: The BoltAPI instance that owns this handler (may be sub-app)
            meta: Handler metadata
        """
        # Context variable for per-request handler execution
        # This allows the middleware chain to be built once and reused
        _handler_context: contextvars.ContextVar[dict] = getattr(
            api, '_handler_context', None
        )
        if _handler_context is None:
            _handler_context = contextvars.ContextVar('_bolt_handler_context')
            api._handler_context = _handler_context

        # Build middleware chain once per API and cache it
        if not api._middleware_chain_built:
            # Create the innermost get_response - dispatches to the handler from context
            async def inner_handler(req):
                """The innermost layer that executes the actual handler from context."""
                ctx = _handler_context.get()
                _handler = ctx['handler']
                _meta = ctx['meta']

                # Execute handler based on mode
                if _meta.get("mode") == "request_only":
                    if _meta.get("is_async", True):
                        result = await _handler(req)
                    else:
                        if _meta.get("is_blocking", False):
                            result = await sync_to_thread(_handler, req)
                        else:
                            result = _handler(req)
                else:
                    # Use pre-compiled injector
                    if _meta.get("injector_is_async", False):
                        args, kwargs = await _meta["injector"](req)
                    else:
                        args, kwargs = _meta["injector"](req)

                    if _meta.get("is_async", True):
                        result = await _handler(*args, **kwargs)
                    else:
                        if _meta.get("is_blocking", False):
                            result = await sync_to_thread(_handler, *args, **kwargs)
                        else:
                            result = _handler(*args, **kwargs)

                # Serialize response to tuple format
                response_tuple = await serialize_response(result, _meta)
                # Convert to MiddlewareResponse for middleware compatibility
                return MiddlewareResponse.from_tuple(response_tuple)

            # Build the middleware chain (innermost to outermost)
            # Each middleware class receives get_response in __init__
            chain = inner_handler
            for middleware_cls in reversed(api.middleware):
                # Check if this is a DjangoMiddleware instance (pre-configured wrapper)
                if hasattr(middleware_cls, '_create_middleware_instance'):
                    # DjangoMiddleware: call _create_middleware_instance with get_response
                    middleware_cls._create_middleware_instance(chain)
                    chain = middleware_cls
                else:
                    # Regular middleware class: instantiate with get_response
                    chain = middleware_cls(chain)

            api._middleware_chain = chain
            api._middleware_chain_built = True

        # Store csrf_exempt in request.state for CSRF middleware to check
        # This is set at registration time from handler's csrf_exempt attribute
        request.state["_csrf_exempt"] = meta.get("csrf_exempt", False)

        # Set the handler context for this request
        ctx = {'handler': handler, 'meta': meta}
        token = _handler_context.set(ctx)

        try:
            # Execute through the cached chain
            middleware_response = await api._middleware_chain(request)

            # Convert back to tuple format for return
            return middleware_response.to_tuple()
        finally:
            _handler_context.reset(token)

    async def _dispatch(self, handler: Callable, request: dict[str, Any], handler_id: int = None) -> Response:
        """
        Optimized async dispatch that calls the handler and returns response tuple.

        Performance optimizations:
        - Unchecked metadata access (guaranteed to exist)
        - Inline user loading (eliminates function call overhead)
        - Pre-compiled argument injector (zero parameter binding overhead)
        - Streamlined execution flow (minimal branching)
        - Eliminated hasattr() checks via __init__ initialization
        - Cached logging decisions to avoid per-request isEnabledFor() calls

        Args:
            handler: The route handler function
            request: The request dictionary
            handler_id: Handler ID to lookup original API (for merged APIs)
        """
        # For merged APIs, use the original API's logging middleware and middleware chain
        # This preserves per-API logging, auth, and middleware config (Litestar-style)
        # Note: _handler_api_map is always initialized in __init__ (no hasattr needed)
        original_api = self._handler_api_map.get(handler_id) if handler_id is not None else None
        logging_middleware = original_api._logging_middleware if original_api else self._logging_middleware

        # Start timing only if we might log
        # Use cached should_time flag (computed once per logging middleware instance)
        start_time = None
        if logging_middleware:
            # Check cached timing decision (computed once at first request)
            if not hasattr(logging_middleware, '_should_time_cached'):
                # First request: compute and cache the timing decision
                should_time = False
                try:
                    if logging_middleware.logger.isEnabledFor(logging.INFO):
                        should_time = True
                except Exception:
                    # Logger might not be fully configured; default to no timing
                    # This is expected during testing or when logger is unavailable
                    should_time = False
                if not should_time:
                    should_time = bool(getattr(logging_middleware.config, 'min_duration_ms', None))
                logging_middleware._should_time_cached = should_time

            if logging_middleware._should_time_cached:
                start_time = time.time()

            # Log request if logging enabled (DEBUG-level guard happens inside)
            logging_middleware.log_request(request)

        try:
            # 1. Direct metadata access using handler_id (int key is faster than callable key)
            # Integer hashing is O(1) with minimal overhead vs callable hashing
            meta = self._handler_meta[handler_id]

            # 2. Lazy user loading using SimpleLazyObject (Django pattern)
            # User is only loaded from DB when request.user is actually accessed
            auth_context = request.get("auth")
            if auth_context and auth_context.get("user_id"):
                user_id = auth_context["user_id"]  # Direct access - key exists
                backend_name = auth_context.get("auth_backend")
                # Use pre-computed is_async from handler metadata (avoids runtime loop check)
                # Default True for ASGI bridge handlers that don't set is_async
                is_async_ctx = meta.get("is_async", True)
                # Use functools.partial instead of lambda - faster, no closure overhead
                request["user"] = SimpleLazyObject(
                    partial(load_user_sync, user_id, backend_name, auth_context, is_async_ctx)
                )
            else:
                request["user"] = None

            # 3. Check if we need to execute middleware
            # Middleware runs for:
            # - Mounted sub-apps (original_api has middleware)
            # - Main API (self has middleware)
            if original_api and original_api.middleware:
                api_with_middleware = original_api
            elif self.middleware:
                api_with_middleware = self
            else:
                api_with_middleware = None

            if api_with_middleware:
                # Execute through middleware chain (Django-style)
                response = await self._dispatch_with_middleware(
                    handler, request, handler_id, api_with_middleware, meta
                )
            else:
                # Fast path: no middleware, execute handler directly
                # Pre-extract commonly used metadata to avoid repeated dict lookups
                mode = meta.get("mode")
                is_async = meta.get("is_async", True)  # Default True for ASGI bridge handlers
                is_blocking = meta.get("is_blocking", False)

                # 3. Fast path for request-only handlers (no parameter extraction)
                if mode == "request_only":
                    if is_async:
                        result = await handler(request)
                    else:
                        # Smart thread pool: only use for blocking handlers
                        if is_blocking:
                            result = await sync_to_thread(handler, request)
                        else:
                            result = handler(request)
                else:
                    # 4. Use pre-compiled injector (sync or async based on needs)
                    # Note: injector_is_async defaults to False for most handlers
                    if meta.get("injector_is_async", False):
                        args, kwargs = await meta["injector"](request)
                    else:
                        args, kwargs = meta["injector"](request)

                    # 5. Execute handler (async or sync)
                    if is_async:
                        result = await handler(*args, **kwargs)
                    else:
                        # Sync handler execution with smart thread pool usage:
                        # - is_blocking=True (ORM/IO detected): Use thread pool to avoid blocking event loop
                        # - is_blocking=False (pure CPU): Call directly for maximum performance
                        if is_blocking:
                            # Handler does blocking I/O (ORM, file, network) - use thread pool
                            result = await sync_to_thread(handler, *args, **kwargs)
                        else:
                            # Pure sync handler (no blocking I/O) - call directly
                            # This avoids thread pool overhead per request
                            result = handler(*args, **kwargs)

                # 6. Serialize response
                response = await serialize_response(result, meta)

            # Log response if logging enabled
            if logging_middleware and start_time is not None:
                duration = time.time() - start_time
                # Response is usually a tuple (status, headers, body) but StreamingResponse is passed through
                status_code = response[0] if isinstance(response, tuple) else 200
                logging_middleware.log_response(request, status_code, duration)

            return response

        except HTTPException as he:
            # Log exception if logging enabled
            if logging_middleware and start_time is not None:
                duration = time.time() - start_time
                logging_middleware.log_response(request, he.status_code, duration)

            return self._handle_http_exception(he)
        except Exception as e:
            # Log exception if logging enabled
            if logging_middleware:
                logging_middleware.log_exception(request, e, exc_info=True)

            return self._handle_generic_exception(e, request=request)


    def _get_openapi_schema(self) -> dict[str, Any]:
        """Get or generate OpenAPI schema.

        Returns:
            OpenAPI schema as dictionary.
        """
        if self._openapi_schema is None:
            generator = SchemaGenerator(self, self.openapi_config)
            openapi = generator.generate()
            self._openapi_schema = openapi.to_schema()

        return self._openapi_schema

    def _register_openapi_routes(self) -> None:
        """Register OpenAPI documentation routes.

        Delegates to OpenAPIRouteRegistrar for cleaner separation of concerns.
        """

        registrar = OpenAPIRouteRegistrar(self)
        registrar.register_routes()

    def _register_admin_routes(self, host: str = "localhost", port: int = 8000) -> None:
        """Register Django admin routes via ASGI bridge.

        Delegates to AdminRouteRegistrar for cleaner separation of concerns.

        Args:
            host: Server hostname for ASGI scope
            port: Server port for ASGI scope
        """

        registrar = AdminRouteRegistrar(self)
        registrar.register_routes(host, port)

    def _register_static_routes(self) -> None:
        """Register static file serving routes for Django admin.

        Delegates to StaticRouteRegistrar for cleaner separation of concerns.
        """

        registrar = StaticRouteRegistrar(self)
        registrar.register_routes()

    def _register_auth_backends(self) -> None:
        """
        Register authentication backends for user resolution.

        Scans all handler middleware metadata to find unique auth backends,
        then registers them for request.user lazy loading.
        """
        registered = set()

        for _handler_id, metadata in self._handler_middleware.items():
            # Get stored backend instances (stored during route decoration)
            backend_instances = metadata.get('_auth_backend_instances', [])
            for backend_instance in backend_instances:
                backend_type = backend_instance.scheme_name
                if backend_type and backend_type not in registered:
                    registered.add(backend_type)
                    register_auth_backend(backend_type, backend_instance)

    def mount(self, path: str, app: BoltAPI) -> None:
        """
        Mount a sub-application at a given path (FastAPI-style).

        The mounted app's routes are copied to this app with the path prefix prepended.
        Each sub-app maintains its own middleware, auth, and configuration.

        Usage:
            # Create a sub-application with its own middleware
            middleware_app = BoltAPI(
                middleware=[RequestIdMiddleware, TenantMiddleware],
                django_middleware=True,
            )

            @middleware_app.get("/demo")
            async def demo_endpoint(request: Request):
                return {"status": "ok"}

            # Mount it at /middleware
            api = BoltAPI()
            api.mount("/middleware", middleware_app)

            # Results in: GET /middleware/demo

        Args:
            path: URL prefix for all routes in the sub-app (e.g., "/api/v2")
            app: BoltAPI instance to mount

        Note:
            Unlike include_router(), mount() preserves the sub-app's middleware
            and configuration independently. This is similar to FastAPI's mount()
            for sub-applications.
        """
        if not isinstance(app, BoltAPI):
            raise TypeError(
                f"mount() expects a BoltAPI instance, got {type(app).__name__}. "
                f"Use include_router() for Router instances."
            )

        # Normalize path prefix
        mount_path = path.rstrip("/")

        # Copy routes from sub-app to this app with path prefix
        for method, route_path, handler_id, handler in app._routes:
            # Compute new path with mount prefix
            new_path = mount_path + route_path

            # Create new handler ID in parent's namespace
            new_handler_id = self._next_handler_id
            self._next_handler_id += 1

            # Register route in parent
            self._routes.append((method, new_path, new_handler_id, handler))
            self._handlers[new_handler_id] = handler

            # Copy handler metadata (now keyed by handler_id for performance)
            if handler_id in app._handler_meta:
                self._handler_meta[new_handler_id] = app._handler_meta[handler_id]

            # Copy middleware metadata (with path updated)
            if handler_id in app._handler_middleware:
                middleware_meta = app._handler_middleware[handler_id].copy()
                middleware_meta['path'] = new_path
                self._handler_middleware[new_handler_id] = middleware_meta

            # Track which API owns this handler (for logging, etc.)
            # _handler_api_map is always initialized in __init__
            self._handler_api_map[new_handler_id] = app

        # Copy WebSocket routes
        for ws_path, handler_id, handler in app._websocket_routes:
            new_path = mount_path + ws_path
            new_handler_id = self._next_handler_id
            self._next_handler_id += 1

            self._websocket_routes.append((new_path, new_handler_id, handler))
            self._handlers[new_handler_id] = handler

            # Copy handler metadata (now keyed by handler_id for performance)
            if handler_id in app._handler_meta:
                self._handler_meta[new_handler_id] = app._handler_meta[handler_id]

            if handler_id in app._handler_middleware:
                middleware_meta = app._handler_middleware[handler_id].copy()
                middleware_meta['path'] = new_path
                self._handler_middleware[new_handler_id] = middleware_meta

            # Track which API owns this handler (for logging, etc.)
            # _handler_api_map is always initialized in __init__
            self._handler_api_map[new_handler_id] = app

        # Remove sub-app from global registry (parent handles its routes now)
        if app in _BOLT_API_REGISTRY:
            _BOLT_API_REGISTRY.remove(app)

    def include_router(self, router: Router, prefix: str = "") -> None:
        """
        Include a Router's routes into this API.

        This method copies all routes from the router to this API, applying
        the optional prefix. Router-level middleware, auth, and guards are
        merged with route-specific settings.

        Usage:
            from django_bolt import BoltAPI, Router

            users_router = Router(prefix="/users", tags=["users"])

            @users_router.get("")
            async def list_users():
                return []

            @users_router.get("/{user_id}")
            async def get_user(user_id: int):
                return {"id": user_id}

            api = BoltAPI()
            api.include_router(users_router)
            # Results in: GET /users, GET /users/{user_id}

            # With additional prefix
            api.include_router(users_router, prefix="/api/v1")
            # Results in: GET /api/v1/users, GET /api/v1/users/{user_id}

        Args:
            router: Router instance containing routes to include
            prefix: Additional URL prefix to prepend (combined with router's prefix)
        """
        if not isinstance(router, Router):
            raise TypeError(
                f"include_router() expects a Router instance, got {type(router).__name__}. "
                f"Use mount() for BoltAPI sub-applications."
            )

        # Get all routes from router (including nested routers)
        all_routes = router.get_all_routes()

        # Get router middleware chain (including parent routers)
        router.get_middleware_chain()

        for method, route_path, handler, meta in all_routes:
            # Compute full path with optional prefix
            full_path = prefix.rstrip("/") + route_path if prefix else route_path

            # Extract route-specific overrides from meta
            route_auth = meta.pop('auth', None)
            route_guards = meta.pop('guards', None)
            route_tags = meta.pop('tags', None)
            meta.pop('_router_middleware', [])

            # Get the appropriate decorator based on method
            decorator_method = getattr(self, method.lower(), None)
            if decorator_method is None:
                continue

            # Register route with merged settings
            decorator = decorator_method(
                full_path,
                auth=route_auth,
                guards=route_guards,
                tags=route_tags,
                **meta
            )

            # Apply decorator to register handler
            decorator(handler)


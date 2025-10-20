import inspect
import msgspec
import re
import time
from typing import Any, Callable, Dict, List, Tuple, Optional, get_origin, get_args, Annotated, get_type_hints

from .bootstrap import ensure_django_ready
from django_bolt import _core
from .responses import StreamingResponse
from .exceptions import HTTPException
from .params import Param, Depends as DependsMarker
from .typing import FieldDefinition

# Import modularized components
from .binding import (
    coerce_to_response_type,
    coerce_to_response_type_async,
    convert_primitive,
    create_extractor,
)
from .typing import is_msgspec_struct, is_optional
from .request_parsing import parse_form_data
from .dependencies import resolve_dependency
from .serialization import serialize_response
from .middleware.compiler import compile_middleware_meta

Request = Dict[str, Any]
Response = Tuple[int, List[Tuple[str, str]], bytes]

# Global registry for BoltAPI instances (used by autodiscovery)
_BOLT_API_REGISTRY = []


def _extract_path_params(path: str) -> set[str]:
    """
    Extract path parameter names from a route pattern.

    Examples:
        "/users/{user_id}" -> {"user_id"}
        "/posts/{post_id}/comments/{comment_id}" -> {"post_id", "comment_id"}
    """
    return set(re.findall(r'\{(\w+)\}', path))


def extract_parameter_value(
    param: Dict[str, Any],
    request: Dict[str, Any],
    params_map: Dict[str, Any],
    query_map: Dict[str, Any],
    headers_map: Dict[str, str],
    cookies_map: Dict[str, str],
    form_map: Dict[str, Any],
    files_map: Dict[str, Any],
    meta: Dict[str, Any],
    body_obj: Any,
    body_loaded: bool
) -> Tuple[Any, Any, bool]:
    """
    Extract value for a handler parameter (backward compatibility function).

    This function maintains backward compatibility while using the new
    extractor-based system internally.
    """
    name = param["name"]
    annotation = param["annotation"]
    default = param["default"]
    source = param["source"]
    alias = param.get("alias")
    key = alias or name

    # Handle different sources
    if source == "path":
        if key in params_map:
            return convert_primitive(str(params_map[key]), annotation), body_obj, body_loaded
        raise ValueError(f"Missing required path parameter: {key}")

    elif source == "query":
        if key in query_map:
            return convert_primitive(str(query_map[key]), annotation), body_obj, body_loaded
        elif default is not inspect.Parameter.empty or is_optional(annotation):
            return (None if default is inspect.Parameter.empty else default), body_obj, body_loaded
        raise ValueError(f"Missing required query parameter: {key}")

    elif source == "header":
        lower_key = key.lower()
        if lower_key in headers_map:
            return convert_primitive(str(headers_map[lower_key]), annotation), body_obj, body_loaded
        elif default is not inspect.Parameter.empty or is_optional(annotation):
            return (None if default is inspect.Parameter.empty else default), body_obj, body_loaded
        raise ValueError(f"Missing required header: {key}")

    elif source == "cookie":
        if key in cookies_map:
            return convert_primitive(str(cookies_map[key]), annotation), body_obj, body_loaded
        elif default is not inspect.Parameter.empty or is_optional(annotation):
            return (None if default is inspect.Parameter.empty else default), body_obj, body_loaded
        raise ValueError(f"Missing required cookie: {key}")

    elif source == "form":
        if key in form_map:
            return convert_primitive(str(form_map[key]), annotation), body_obj, body_loaded
        elif default is not inspect.Parameter.empty or is_optional(annotation):
            return (None if default is inspect.Parameter.empty else default), body_obj, body_loaded
        raise ValueError(f"Missing required form field: {key}")

    elif source == "file":
        if key in files_map:
            return files_map[key], body_obj, body_loaded
        elif default is not inspect.Parameter.empty or is_optional(annotation):
            return (None if default is inspect.Parameter.empty else default), body_obj, body_loaded
        raise ValueError(f"Missing required file: {key}")

    elif source == "body":
        # Handle body parameter
        if meta.get("body_struct_param") == name:
            if not body_loaded:
                body_bytes: bytes = request["body"]
                if is_msgspec_struct(meta["body_struct_type"]):
                    from .binding import get_msgspec_decoder
                    from .exceptions import RequestValidationError, parse_msgspec_decode_error
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
                    from .exceptions import RequestValidationError, parse_msgspec_decode_error
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
            if default is not inspect.Parameter.empty or is_optional(annotation):
                return (None if default is inspect.Parameter.empty else default), body_obj, body_loaded
            raise ValueError(f"Missing required parameter: {name}")

    else:
        # Unknown source
        if default is not inspect.Parameter.empty or is_optional(annotation):
            return (None if default is inspect.Parameter.empty else default), body_obj, body_loaded
        raise ValueError(f"Missing required parameter: {name}")

class BoltAPI:
    def __init__(
        self,
        prefix: str = "",
        middleware: Optional[List[Any]] = None,
        middleware_config: Optional[Dict[str, Any]] = None,
        enable_logging: bool = True,
        logging_config: Optional[Any] = None,
        compression: Optional[Any] = None,
        openapi_config: Optional[Any] = None,
    ) -> None:
        self._routes: List[Tuple[str, str, int, Callable]] = []
        self._handlers: Dict[int, Callable] = {}
        self._handler_meta: Dict[Callable, Dict[str, Any]] = {}
        self._handler_middleware: Dict[int, Dict[str, Any]] = {}  # Middleware metadata per handler
        self._next_handler_id = 0
        self.prefix = prefix.rstrip("/")  # Remove trailing slash

        # Global middleware configuration
        self.middleware = middleware or []
        self.middleware_config = middleware_config or {}

        # Logging configuration (opt-in, setup happens at server startup)
        self.enable_logging = enable_logging
        self._logging_middleware = None

        if self.enable_logging:
            # Create logging middleware (actual logging setup happens at server startup)
            if logging_config is not None:
                from .logging.middleware import LoggingMiddleware
                self._logging_middleware = LoggingMiddleware(logging_config)
            else:
                # Use default logging configuration
                from .logging.middleware import create_logging_middleware
                self._logging_middleware = create_logging_middleware()

        # Compression configuration
        # compression=None means disabled, not providing compression arg means default enabled
        if compression is False:
            # Explicitly disabled
            self.compression = None
        elif compression is None:
            # Not provided, use default
            from .compression import CompressionConfig
            self.compression = CompressionConfig()
        else:
            # Custom config provided
            self.compression = compression

        # OpenAPI configuration - enabled by default with sensible defaults
        if openapi_config is None:
            # Create default OpenAPI config
            from .openapi import OpenAPIConfig, SwaggerRenderPlugin, RedocRenderPlugin, ScalarRenderPlugin, RapidocRenderPlugin, StoplightRenderPlugin, JsonRenderPlugin, YamlRenderPlugin
            try:
                # Try to get Django project name from settings
                from django.conf import settings
                title = getattr(settings, 'PROJECT_NAME', None) or getattr(settings, 'SITE_NAME', None) or "API"
            except:
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

        self._openapi_schema: Optional[Dict[str, Any]] = None
        self._openapi_routes_registered = False

        # Django admin configuration (controlled by --no-admin flag)
        self._admin_routes_registered = False
        self._static_routes_registered = False
        self._asgi_handler = None

        # Register this instance globally for autodiscovery
        _BOLT_API_REGISTRY.append(self)

    def get(
        self,
        path: str,
        *,
        response_model: Optional[Any] = None,
        status_code: Optional[int] = None,
        guards: Optional[List[Any]] = None,
        auth: Optional[List[Any]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ):
        return self._route_decorator("GET", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth, tags=tags, summary=summary, description=description)

    def post(
        self,
        path: str,
        *,
        response_model: Optional[Any] = None,
        status_code: Optional[int] = None,
        guards: Optional[List[Any]] = None,
        auth: Optional[List[Any]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ):
        return self._route_decorator("POST", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth, tags=tags, summary=summary, description=description)

    def put(
        self,
        path: str,
        *,
        response_model: Optional[Any] = None,
        status_code: Optional[int] = None,
        guards: Optional[List[Any]] = None,
        auth: Optional[List[Any]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ):
        return self._route_decorator("PUT", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth, tags=tags, summary=summary, description=description)

    def patch(
        self,
        path: str,
        *,
        response_model: Optional[Any] = None,
        status_code: Optional[int] = None,
        guards: Optional[List[Any]] = None,
        auth: Optional[List[Any]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ):
        return self._route_decorator("PATCH", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth, tags=tags, summary=summary, description=description)

    def delete(
        self,
        path: str,
        *,
        response_model: Optional[Any] = None,
        status_code: Optional[int] = None,
        guards: Optional[List[Any]] = None,
        auth: Optional[List[Any]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ):
        return self._route_decorator("DELETE", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth, tags=tags, summary=summary, description=description)

    def head(
        self,
        path: str,
        *,
        response_model: Optional[Any] = None,
        status_code: Optional[int] = None,
        guards: Optional[List[Any]] = None,
        auth: Optional[List[Any]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ):
        return self._route_decorator("HEAD", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth, tags=tags, summary=summary, description=description)

    def options(
        self,
        path: str,
        *,
        response_model: Optional[Any] = None,
        status_code: Optional[int] = None,
        guards: Optional[List[Any]] = None,
        auth: Optional[List[Any]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ):
        return self._route_decorator("OPTIONS", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth, tags=tags, summary=summary, description=description)

    def view(
        self,
        path: str,
        *,
        methods: Optional[List[str]] = None,
        guards: Optional[List[Any]] = None,
        auth: Optional[List[Any]] = None,
        status_code: Optional[int] = None
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
        from .views import APIView

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
                    auth=merged_auth
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
        guards: Optional[List[Any]] = None,
        auth: Optional[List[Any]] = None,
        status_code: Optional[int] = None,
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
        from .views import ViewSet
        from .status_codes import HTTP_201_CREATED, HTTP_204_NO_CONTENT

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

    def _register_custom_actions(self, view_cls: type, base_path: Optional[str], lookup_field: Optional[str]):
        """
        Scan a ViewSet class for custom action methods and register them.

        Custom actions are methods decorated with @action decorator.

        Args:
            view_cls: The ViewSet class to scan
            base_path: Base path for the ViewSet (e.g., "/users")
            lookup_field: Lookup field name for detail actions (e.g., "id", "pk")
        """
        import inspect
        import types
        from .decorators import ActionHandler

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
        response_model: Optional[Any] = None,
        status_code: Optional[int] = None,
        guards: Optional[List[Any]] = None,
        auth: Optional[List[Any]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ):
        def decorator(fn: Callable):
            # Enforce async handlers
            if not inspect.iscoroutinefunction(fn):
                raise TypeError(f"Handler {fn.__name__} must be async. Use 'async def' instead of 'def'")

            handler_id = self._next_handler_id
            self._next_handler_id += 1

            # Apply prefix to path (conversion happens in Rust)
            full_path = self.prefix + path if self.prefix else path

            self._routes.append((method, full_path, handler_id, fn))
            self._handlers[handler_id] = fn

            # Pre-compile lightweight binder for this handler with HTTP method validation
            meta = self._compile_binder(fn, method, full_path)
            # Allow explicit response model override
            if response_model is not None:
                meta["response_type"] = response_model
            if status_code is not None:
                meta["default_status_code"] = int(status_code)
            # Store OpenAPI metadata
            if tags is not None:
                meta["openapi_tags"] = tags
            if summary is not None:
                meta["openapi_summary"] = summary
            if description is not None:
                meta["openapi_description"] = description
            self._handler_meta[fn] = meta

            # Compile middleware metadata for this handler (including guards and auth)
            middleware_meta = compile_middleware_meta(
                fn, method, full_path,
                self.middleware, self.middleware_config,
                guards=guards, auth=auth
            )
            if middleware_meta:
                self._handler_middleware[handler_id] = middleware_meta

            return fn
        return decorator

    def _compile_binder(self, fn: Callable, http_method: str = "", path: str = "") -> Dict[str, Any]:
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
        type_hints = get_type_hints(fn, include_extras=True)

        # Extract path parameters from route pattern
        path_params = _extract_path_params(path)

        meta: Dict[str, Any] = {
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
        field_definitions: List[FieldDefinition] = []

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

        # Convert FieldDefinitions to dict format for backward compatibility
        # (We'll optimize this away in Phase 4)
        for field in field_definitions:
            meta["fields"].append({
                "name": field.name,
                "annotation": field.annotation,
                "default": field.default,
                "kind": field.kind,
                "source": field.source,
                "alias": field.alias,
                "embed": field.embed,
                "dependency": field.dependency,
                "field_def": field,  # Store FieldDefinition for future use
            })

        # Detect single body parameter for fast path
        if len(body_fields) == 1:
            body_field = body_fields[0]
            if body_field.is_msgspec_struct:
                meta["body_struct_param"] = body_field.name
                meta["body_struct_type"] = body_field.annotation

        # Capture return type for response validation/serialization
        if sig.return_annotation is not inspect._empty:
            meta["response_type"] = sig.return_annotation

        meta["mode"] = "mixed"

        # Maintain backward compatibility with old "params" key
        meta["params"] = meta["fields"]

        # Performance: Check if handler needs form/file parsing
        # This allows us to skip expensive form parsing for 95% of endpoints
        needs_form_parsing = any(f.source in ("form", "file") for f in field_definitions)
        meta["needs_form_parsing"] = needs_form_parsing

        return meta

    async def _build_handler_arguments(self, meta: Dict[str, Any], request: Dict[str, Any]) -> Tuple[List[Any], Dict[str, Any]]:
        """Build arguments for handler invocation."""
        args: List[Any] = []
        kwargs: Dict[str, Any] = {}

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
        dep_cache: Dict[Any, Any] = {}

        for p in meta["params"]:
            name = p["name"]
            source = p["source"]
            depends_marker = p.get("dependency")

            if source == "request":
                value = request
            elif source == "dependency":
                dep_fn = depends_marker.dependency if depends_marker else None
                if dep_fn is None:
                    raise ValueError(f"Depends for parameter {name} requires a callable")
                value = await resolve_dependency(
                    dep_fn, depends_marker, request, dep_cache,
                    params_map, query_map, headers_map, cookies_map,
                    self._handler_meta, self._compile_binder,
                    meta.get("http_method", ""), meta.get("path", "")
                )
            else:
                value, body_obj, body_loaded = extract_parameter_value(
                    p, request, params_map, query_map, headers_map, cookies_map,
                    form_map, files_map, meta, body_obj, body_loaded
                )

            # Respect positional-only/keyword-only kinds
            if p["kind"] in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                args.append(value)
            else:
                kwargs[name] = value

        return args, kwargs


    def _handle_http_exception(self, he: HTTPException) -> Response:
        """Handle HTTPException and return response."""
        try:
            body = msgspec.json.encode({"detail": he.detail})
            headers = [("content-type", "application/json")]
        except Exception:
            body = str(he.detail).encode()
            headers = [("content-type", "text/plain; charset=utf-8")]

        if he.headers:
            headers.extend([(k.lower(), v) for k, v in he.headers.items()])

        return int(he.status_code), headers, body

    def _handle_generic_exception(self, e: Exception, request: Dict[str, Any] = None) -> Response:
        """Handle generic exception using error_handlers module."""
        from . import error_handlers
        # Use the error handler which respects Django DEBUG setting
        return error_handlers.handle_exception(e, debug=False, request=request)  # debug will be checked dynamically

    async def _dispatch(self, handler: Callable, request: Dict[str, Any], handler_id: int = None) -> Response:
        """Async dispatch that calls the handler and returns response tuple.

        Args:
            handler: The route handler function
            request: The request dictionary
            handler_id: Handler ID to lookup original API (for merged APIs)
        """
        # For merged APIs, use the original API's logging middleware
        # This preserves per-API logging, auth, and middleware config (Litestar-style)
        logging_middleware = self._logging_middleware
        if handler_id is not None and hasattr(self, '_handler_api_map'):
            original_api = self._handler_api_map.get(handler_id)
            if original_api and original_api._logging_middleware:
                logging_middleware = original_api._logging_middleware

        # Start timing only if we might log
        start_time = None
        if logging_middleware:
            # Determine if INFO logs are enabled or a slow-only threshold exists
            logger = logging_middleware.logger
            should_time = False
            try:
                if logger.isEnabledFor(__import__('logging').INFO):
                    should_time = True
            except Exception:
                pass
            if not should_time:
                # If slow-only is configured, we still need timing
                should_time = bool(getattr(logging_middleware.config, 'min_duration_ms', None))
            if should_time:
                start_time = time.time()

            # Log request if logging enabled (DEBUG-level guard happens inside)
            logging_middleware.log_request(request)

        try:
            meta = self._handler_meta.get(handler)
            if meta is None:
                meta = self._compile_binder(handler)
                self._handler_meta[handler] = meta

            # Fast path for request-only handlers
            if meta.get("mode") == "request_only":
                result = await handler(request)
            else:
                # Build handler arguments
                args, kwargs = await self._build_handler_arguments(meta, request)
                result = await handler(*args, **kwargs)

            # Serialize response
            response = await serialize_response(result, meta)

            # Log response if logging enabled
            if logging_middleware and start_time is not None:
                duration = time.time() - start_time
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

    def _get_openapi_schema(self) -> Dict[str, Any]:
        """Get or generate OpenAPI schema.

        Returns:
            OpenAPI schema as dictionary.
        """
        if self._openapi_schema is None:
            from .openapi.schema_generator import SchemaGenerator

            generator = SchemaGenerator(self, self.openapi_config)
            openapi = generator.generate()
            self._openapi_schema = openapi.to_schema()

        return self._openapi_schema

    def _register_openapi_routes(self) -> None:
        """Register OpenAPI documentation routes.

        Delegates to OpenAPIRouteRegistrar for cleaner separation of concerns.
        """
        from .openapi.routes import OpenAPIRouteRegistrar

        registrar = OpenAPIRouteRegistrar(self)
        registrar.register_routes()

    def _register_admin_routes(self, host: str = "localhost", port: int = 8000) -> None:
        """Register Django admin routes via ASGI bridge.

        Delegates to AdminRouteRegistrar for cleaner separation of concerns.

        Args:
            host: Server hostname for ASGI scope
            port: Server port for ASGI scope
        """
        from .admin.routes import AdminRouteRegistrar

        registrar = AdminRouteRegistrar(self)
        registrar.register_routes(host, port)

    def _register_static_routes(self) -> None:
        """Register static file serving routes for Django admin.

        Delegates to StaticRouteRegistrar for cleaner separation of concerns.
        """
        from .admin.static_routes import StaticRouteRegistrar

        registrar = StaticRouteRegistrar(self)
        registrar.register_routes()

    def serve(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Start the async server with registered routes"""
        info = ensure_django_ready()
        print(
            f"[django-bolt] Django setup: mode={info.get('mode')} debug={info.get('debug')}\n"
            f"[django-bolt] DB: {info.get('database')} name={info.get('database_name')}\n"
            f"[django-bolt] Settings: {info.get('settings_module') or 'embedded'}"
        )

        # Register Django admin routes if enabled
        if self.enable_admin:
            self._register_admin_routes(host, port)
            if self._admin_routes_registered:
                from .admin.admin_detection import detect_admin_url_prefix
                admin_prefix = detect_admin_url_prefix() or 'admin'
                print(f"[django-bolt] Django admin available at http://{host}:{port}/{admin_prefix}/")

                # Also register static file routes for admin
                self._register_static_routes()
                if self._static_routes_registered:
                    print(f"[django-bolt] Static files serving enabled")

        # Register OpenAPI routes if configured
        if self.openapi_config:
            self._register_openapi_routes()
            print(f"[django-bolt] OpenAPI docs available at http://{host}:{port}{self.openapi_config.path}")

        # Register all routes with Rust router
        rust_routes = [
            (method, path, handler_id, handler)
            for method, path, handler_id, handler in self._routes
        ]
        
        # Register routes in Rust
        _core.register_routes(rust_routes)
        
        # Register middleware metadata if any exists
        if self._handler_middleware:
            middleware_data = [
                (handler_id, meta)
                for handler_id, meta in self._handler_middleware.items()
            ]
            _core.register_middleware_metadata(middleware_data)
            print(f"[django-bolt] Registered middleware for {len(middleware_data)} handlers")
        
        print(f"[django-bolt] Registered {len(self._routes)} routes")
        print(f"[django-bolt] Starting async server on http://{host}:{port}")

        # Get compression config
        compression_config = None
        if self.compression is not None:
            compression_config = self.compression.to_rust_config()

        # Start async server
        _core.start_server_async(self._dispatch, host, port, compression_config)

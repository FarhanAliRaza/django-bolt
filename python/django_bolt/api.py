import inspect
import msgspec
from typing import Any, Callable, Dict, List, Tuple, Optional, get_origin, get_args, Annotated

from .bootstrap import ensure_django_ready
from django_bolt import _core
from .responses import StreamingResponse
from .exceptions import HTTPException
from .params import Param, Depends as DependsMarker

# Import modularized components
from .binding import (
    is_optional, is_msgspec_struct, extract_parameter_value
)
from .request_parsing import parse_form_data
from .dependencies import resolve_dependency
from .serialization import serialize_response
from .middleware.compiler import compile_middleware_meta

Request = Dict[str, Any]
Response = Tuple[int, List[Tuple[str, str]], bytes]
 
# Global registry for BoltAPI instances (used by autodiscovery)
_BOLT_API_REGISTRY = []

class BoltAPI:
    def __init__(
        self,
        prefix: str = "",
        middleware: Optional[List[Any]] = None,
        middleware_config: Optional[Dict[str, Any]] = None
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
        
        # Register this instance globally for autodiscovery
        _BOLT_API_REGISTRY.append(self)

    def get(self, path: str, *, response_model: Optional[Any] = None, status_code: Optional[int] = None, guards: Optional[List[Any]] = None, auth: Optional[List[Any]] = None):
        return self._route_decorator("GET", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth)

    def post(self, path: str, *, response_model: Optional[Any] = None, status_code: Optional[int] = None, guards: Optional[List[Any]] = None, auth: Optional[List[Any]] = None):
        return self._route_decorator("POST", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth)

    def put(self, path: str, *, response_model: Optional[Any] = None, status_code: Optional[int] = None, guards: Optional[List[Any]] = None, auth: Optional[List[Any]] = None):
        return self._route_decorator("PUT", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth)

    def patch(self, path: str, *, response_model: Optional[Any] = None, status_code: Optional[int] = None, guards: Optional[List[Any]] = None, auth: Optional[List[Any]] = None):
        return self._route_decorator("PATCH", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth)

    def delete(self, path: str, *, response_model: Optional[Any] = None, status_code: Optional[int] = None, guards: Optional[List[Any]] = None, auth: Optional[List[Any]] = None):
        return self._route_decorator("DELETE", path, response_model=response_model, status_code=status_code, guards=guards, auth=auth)

    def _route_decorator(self, method: str, path: str, *, response_model: Optional[Any] = None, status_code: Optional[int] = None, guards: Optional[List[Any]] = None, auth: Optional[List[Any]] = None):
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

            # Pre-compile lightweight binder for this handler
            meta = self._compile_binder(fn)
            # Allow explicit response model override
            if response_model is not None:
                meta["response_type"] = response_model
            if status_code is not None:
                meta["default_status_code"] = int(status_code)
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

    def _compile_binder(self, fn: Callable) -> Dict[str, Any]:
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())
        meta: Dict[str, Any] = {"sig": sig, "params": []}

        # Quick path: single parameter that looks like request
        if len(params) == 1 and params[0].name in {"request", "req"}:
            meta["mode"] = "request_only"
            return meta

        # Build per-parameter binding plan
        for p in params:
            name = p.name
            raw_annotation = p.annotation
            annotation = raw_annotation
            param_marker: Optional[Param] = None
            depends_marker: Optional[DependsMarker] = None

            # Unwrap Annotated[T, ...]
            origin = get_origin(raw_annotation)
            if origin is Annotated:
                args = get_args(raw_annotation)
                if args:
                    annotation = args[0]
                for meta_val in args[1:]:
                    if isinstance(meta_val, Param):
                        param_marker = meta_val
                    elif isinstance(meta_val, DependsMarker):
                        depends_marker = meta_val
            else:
                # If default is marker, detect it
                if isinstance(p.default, Param):
                    param_marker = p.default
                elif isinstance(p.default, DependsMarker):
                    depends_marker = p.default

            source: str
            alias: Optional[str] = None
            embed: Optional[bool] = None
            if name in {"request", "req"}:
                source = "request"
            elif param_marker is not None:
                source = param_marker.source
                alias = param_marker.alias
                embed = param_marker.embed
            elif depends_marker is not None:
                source = "dependency"
            else:
                # Prefer path param, then query, else body
                source = "auto"  # decide at call time using request mapping

            meta["params"].append({
                "name": name,
                "annotation": annotation,
                "default": p.default,
                "kind": p.kind,
                "source": source,
                "alias": alias,
                "embed": embed,
                "dependency": depends_marker,
            })

        # Detect single body parameter pattern (POST/PUT/PATCH) with msgspec.Struct
        body_params = [p for p in meta["params"] if p["source"] in {"auto", "body"} and is_msgspec_struct(p["annotation"])]
        if len(body_params) == 1:
            meta["body_struct_param"] = body_params[0]["name"]
            meta["body_struct_type"] = body_params[0]["annotation"]

        # Capture return type for response validation/serialization
        if sig.return_annotation is not inspect._empty:
            meta["response_type"] = sig.return_annotation

        meta["mode"] = "mixed"
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

        # Parse form/multipart data if needed
        form_map, files_map = parse_form_data(request, headers_map)

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
                    self._handler_meta, self._compile_binder
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

    def _handle_generic_exception(self, e: Exception) -> Response:
        """Handle generic exception and return error response."""
        error_msg = f"Handler error: {str(e)}"
        return 500, [("content-type", "text/plain; charset=utf-8")], error_msg.encode()

    async def _dispatch(self, handler: Callable, request: Dict[str, Any]) -> Response:
        """Async dispatch that calls the handler and returns response tuple"""
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
            return await serialize_response(result, meta)

        except HTTPException as he:
            return self._handle_http_exception(he)
        except Exception as e:
            return self._handle_generic_exception(e)
    
    def serve(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Start the async server with registered routes"""
        info = ensure_django_ready()
        print(
            f"[django-bolt] Django setup: mode={info.get('mode')} debug={info.get('debug')}\n"
            f"[django-bolt] DB: {info.get('database')} name={info.get('database_name')}\n"
            f"[django-bolt] Settings: {info.get('settings_module') or 'embedded'}"
        )
        
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
        
        # Start async server
        _core.start_server_async(self._dispatch, host, port)

import inspect
from typing import Any, Callable, Dict, List, Tuple, Optional, get_origin, get_args, Union, Type
import msgspec

from .bootstrap import ensure_django_ready
from django_bolt import _core
from .responses import JSON

Request = Dict[str, Any]
Response = Tuple[int, List[Tuple[str, str]], bytes]

# Global registry for BoltAPI instances (used by autodiscovery)
_BOLT_API_REGISTRY = []

class BoltAPI:
    def __init__(self, prefix: str = "") -> None:
        self._routes: List[Tuple[str, str, int, Callable]] = []
        self._handlers: Dict[int, Callable] = {}
        self._handler_meta: Dict[Callable, Dict[str, Any]] = {}
        self._next_handler_id = 0
        self.prefix = prefix.rstrip("/")  # Remove trailing slash
        
        # Register this instance globally for autodiscovery
        _BOLT_API_REGISTRY.append(self)

    def get(self, path: str, *, response_model: Optional[Any] = None):
        return self._route_decorator("GET", path, response_model=response_model)

    def post(self, path: str, *, response_model: Optional[Any] = None):
        return self._route_decorator("POST", path, response_model=response_model)

    def put(self, path: str, *, response_model: Optional[Any] = None):
        return self._route_decorator("PUT", path, response_model=response_model)

    def patch(self, path: str, *, response_model: Optional[Any] = None):
        return self._route_decorator("PATCH", path, response_model=response_model)

    def delete(self, path: str, *, response_model: Optional[Any] = None):
        return self._route_decorator("DELETE", path, response_model=response_model)

    def _route_decorator(self, method: str, path: str, *, response_model: Optional[Any] = None):
        def decorator(fn: Callable):
            # Enforce async handlers
            if not inspect.iscoroutinefunction(fn):
                raise TypeError(f"Handler {fn.__name__} must be async. Use 'async def' instead of 'def'")
            
            handler_id = self._next_handler_id
            self._next_handler_id += 1
            
            # Apply prefix to path
            full_path = self.prefix + path if self.prefix else path
            
            self._routes.append((method, full_path, handler_id, fn))
            self._handlers[handler_id] = fn
            
            # Pre-compile lightweight binder for this handler
            meta = self._compile_binder(fn)
            # Allow explicit response model override
            if response_model is not None:
                meta["response_type"] = response_model
            self._handler_meta[fn] = meta
            
            return fn
        return decorator

    def _is_optional(self, annotation: Any) -> bool:
        origin = get_origin(annotation)
        if origin is Union:
            args = get_args(annotation)
            return type(None) in args
        return False

    def _unwrap_optional(self, annotation: Any) -> Any:
        origin = get_origin(annotation)
        if origin is Union:
            args = tuple(a for a in get_args(annotation) if a is not type(None))
            return args[0] if len(args) == 1 else Union[args]  # type: ignore
        return annotation

    def _is_msgspec_struct(self, tp: Any) -> bool:
        try:
            return isinstance(tp, type) and issubclass(tp, msgspec.Struct)
        except Exception:
            return False

    def _coerce_to_response_type(self, value: Any, annotation: Any) -> Any:
        """Coerce arbitrary Python objects (including Django models) into the
        declared response type using msgspec. Supports:
          - msgspec.Struct: build mapping from attributes if needed
          - list[T]: recursively coerce elements
          - dict/primitive: defer to msgspec.convert
        """
        origin = get_origin(annotation)
        # Handle List[T]
        if origin in (list, List):
            args = get_args(annotation)
            elem_type = args[0] if args else Any
            return [self._coerce_to_response_type(elem, elem_type) for elem in (value or [])]

        # Handle Struct
        if self._is_msgspec_struct(annotation):
            if isinstance(value, annotation):
                return value
            if isinstance(value, dict):
                return msgspec.convert(value, annotation)
            # Build mapping from attributes based on struct annotations
            fields = getattr(annotation, "__annotations__", {})
            mapped = {name: getattr(value, name, None) for name in fields.keys()}
            return msgspec.convert(mapped, annotation)

        # Default convert path
        return msgspec.convert(value, annotation)

    def _convert_primitive(self, value: str, annotation: Any) -> Any:
        tp = self._unwrap_optional(annotation)
        if tp is str or tp is Any or tp is None or tp is inspect._empty:
            return value
        if tp is int:
            return int(value)
        if tp is float:
            return float(value)
        if tp is bool:
            v = value.lower()
            if v in ("1", "true", "t", "yes", "y", "on"): return True
            if v in ("0", "false", "f", "no", "n", "off"): return False
            # Fallback: non-empty -> True
            return bool(value)
        # Fallback: try msgspec decode for JSON in value
        try:
            return msgspec.json.decode(value.encode())
        except Exception:
            return value

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
            annotation = p.annotation
            source: str
            if name in {"request", "req"}:
                source = "request"
            else:
                # Prefer path param, then query, else body
                source = "auto"  # decide at call time using request mapping
            meta["params"].append({
                "name": name,
                "annotation": annotation,
                "default": p.default,
                "kind": p.kind,
                "source": source,
            })

        # Detect single body parameter pattern (POST/PUT/PATCH) with msgspec.Struct
        body_params = [p for p in meta["params"] if p["source"] == "auto" and self._is_msgspec_struct(p["annotation"])]
        if len(body_params) == 1:
            meta["body_struct_param"] = body_params[0]["name"]
            meta["body_struct_type"] = body_params[0]["annotation"]

        # Capture return type for response validation/serialization
        if sig.return_annotation is not inspect._empty:
            meta["response_type"] = sig.return_annotation

        meta["mode"] = "mixed"
        return meta

    async def _dispatch(self, handler: Callable, request: Dict[str, Any]) -> Response:
        """Async dispatch that calls the handler and returns response tuple"""
        try:
            meta = self._handler_meta.get(handler)
            if meta is None:
                meta = self._compile_binder(handler)
                self._handler_meta[handler] = meta

            # Fast path
            if meta.get("mode") == "request_only":
                result = await handler(request)
            else:
                # Collect args in order
                args: List[Any] = []
                kwargs: Dict[str, Any] = {}

                # Access PyRequest mappings lazily
                params_map = request["params"] if isinstance(request, dict) else request["params"]
                query_map = request["query"] if isinstance(request, dict) else request["query"]

                # Body decode cache
                body_obj: Any = None
                body_loaded: bool = False

                for p in meta["params"]:
                    name = p["name"]
                    annotation = p["annotation"]
                    default = p["default"]
                    source = p["source"]

                    if source == "request":
                        value = request
                    else:
                        if name in params_map:
                            raw = params_map[name]
                            value = self._convert_primitive(str(raw), annotation)
                        elif name in query_map:
                            raw = query_map[name]
                            value = self._convert_primitive(str(raw), annotation)
                        else:
                            # Maybe body param
                            if meta.get("body_struct_param") == name:
                                if not body_loaded:
                                    body_bytes: bytes = request["body"]
                                    value = msgspec.json.decode(body_bytes, type=meta["body_struct_type"])  # type: ignore
                                    body_obj = value
                                    body_loaded = True
                                else:
                                    value = body_obj
                            else:
                                if default is not inspect._empty or self._is_optional(annotation):
                                    value = None if default is inspect._empty else default
                                else:
                                    raise ValueError(f"Missing required parameter: {name}")

                    # Respect positional-only/keyword-only kinds; default to positional order
                    if p["kind"] in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                        args.append(value)
                    else:
                        kwargs[name] = value

                result = await handler(*args, **kwargs)
            
            # Apply optional response validation/serialization via msgspec
            response_tp = meta.get("response_type")

            # Handle different response types
            if isinstance(result, JSON):
                if response_tp is not None:
                    try:
                        validated = self._coerce_to_response_type(result.data, response_tp)
                        data_bytes = msgspec.json.encode(validated)
                    except Exception as e:
                        err = f"Response validation error: {e}"
                        return 500, [("content-type", "text/plain; charset=utf-8")], err.encode()
                    headers = [("content-type", "application/json")]
                    if result.headers:
                        headers.extend([(k.lower(), v) for k, v in result.headers.items()])
                    return int(result.status_code), headers, data_bytes
                headers = [("content-type", "application/json")]
                if result.headers:
                    headers.extend([(k.lower(), v) for k, v in result.headers.items()])
                return int(result.status_code), headers, result.to_bytes()
            elif isinstance(result, (bytes, bytearray)):
                return 200, [("content-type", "application/octet-stream")], bytes(result)
            elif isinstance(result, str):
                return 200, [("content-type", "text/plain; charset=utf-8")], result.encode()
            elif isinstance(result, (dict, list)):
                # Use msgspec for fast JSON encoding
                if response_tp is not None:
                    try:
                        validated = self._coerce_to_response_type(result, response_tp)
                        data = msgspec.json.encode(validated)
                    except Exception as e:
                        err = f"Response validation error: {e}"
                        return 500, [("content-type", "text/plain; charset=utf-8")], err.encode()
                else:
                    data = msgspec.json.encode(result)
                return 200, [("content-type", "application/json")], data
            else:
                # Fallback to msgspec encoding
                if response_tp is not None:
                    try:
                        validated = self._coerce_to_response_type(result, response_tp)
                        data = msgspec.json.encode(validated)
                    except Exception as e:
                        err = f"Response validation error: {e}"
                        return 500, [("content-type", "text/plain; charset=utf-8")], err.encode()
                else:
                    data = msgspec.json.encode(result)
                return 200, [("content-type", "application/json")], data
                
        except Exception as e:
            error_msg = f"Handler error: {str(e)}"
            return 500, [("content-type", "text/plain; charset=utf-8")], error_msg.encode()
    
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
        
        print(f"[django-bolt] Registered {len(self._routes)} routes")
        print(f"[django-bolt] Starting async server on http://{host}:{port}")
        
        # Start async server
        _core.start_server_async(self._dispatch, host, port)

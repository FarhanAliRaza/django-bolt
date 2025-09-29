import inspect
import re
import mimetypes
from typing import Any, Callable, Dict, List, Tuple, Optional, get_origin, get_args, Union, Type, Annotated
import msgspec

from .bootstrap import ensure_django_ready
from django_bolt import _core
from .responses import JSON, PlainText, HTML, Redirect, File, FileResponse, StreamingResponse
from .exceptions import HTTPException
from .params import Param, Depends as DependsMarker

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

    def get(self, path: str, *, response_model: Optional[Any] = None, status_code: Optional[int] = None):
        return self._route_decorator("GET", path, response_model=response_model, status_code=status_code)

    def post(self, path: str, *, response_model: Optional[Any] = None, status_code: Optional[int] = None):
        return self._route_decorator("POST", path, response_model=response_model, status_code=status_code)

    def put(self, path: str, *, response_model: Optional[Any] = None, status_code: Optional[int] = None):
        return self._route_decorator("PUT", path, response_model=response_model, status_code=status_code)

    def patch(self, path: str, *, response_model: Optional[Any] = None, status_code: Optional[int] = None):
        return self._route_decorator("PATCH", path, response_model=response_model, status_code=status_code)

    def delete(self, path: str, *, response_model: Optional[Any] = None, status_code: Optional[int] = None):
        return self._route_decorator("DELETE", path, response_model=response_model, status_code=status_code)

    def _route_decorator(self, method: str, path: str, *, response_model: Optional[Any] = None, status_code: Optional[int] = None):
        def decorator(fn: Callable):
            # Enforce async handlers
            if not inspect.iscoroutinefunction(fn):
                raise TypeError(f"Handler {fn.__name__} must be async. Use 'async def' instead of 'def'")
            
            handler_id = self._next_handler_id
            self._next_handler_id += 1
            
            # Apply prefix to path and convert FastAPI syntax to matchit
            full_path = self.prefix + path if self.prefix else path
            full_path = self._convert_path(full_path)
            
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
            
            # Compile middleware metadata for this handler
            middleware_meta = self._compile_middleware_meta(fn, method, full_path)
            if middleware_meta:
                self._handler_middleware[handler_id] = middleware_meta
            
            return fn
        return decorator

    def _convert_path(self, path: str) -> str:
        """Convert FastAPI-style paths like /items/{id} and /files/{path:path}
        Matchit uses the same {param} syntax as FastAPI, but uses *path for catch-all
        """
        def repl(m: re.Match[str]) -> str:
            name = m.group(1)
            type_ = m.group(2)
            if type_ == ":path":
                return f"*{name}"
            return f"{{{name}}}"

        return re.sub(r"\{([a-zA-Z_][a-zA-Z0-9_]*)(:[a-zA-Z_][a-zA-Z0-9_]*)?\}", repl, path)

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
        body_params = [p for p in meta["params"] if p["source"] in {"auto", "body"} and self._is_msgspec_struct(p["annotation"])]
        if len(body_params) == 1:
            meta["body_struct_param"] = body_params[0]["name"]
            meta["body_struct_type"] = body_params[0]["annotation"]

        # Capture return type for response validation/serialization
        if sig.return_annotation is not inspect._empty:
            meta["response_type"] = sig.return_annotation

        meta["mode"] = "mixed"
        return meta

    def _compile_middleware_meta(self, handler: Callable, method: str, path: str) -> Optional[Dict[str, Any]]:
        """Compile middleware metadata for a handler."""
        # Check for handler-specific middleware
        handler_middleware = []
        skip_middleware = set()
        
        if hasattr(handler, '__bolt_middleware__'):
            handler_middleware = handler.__bolt_middleware__
        
        if hasattr(handler, '__bolt_skip_middleware__'):
            skip_middleware = handler.__bolt_skip_middleware__
        
        # Merge global and handler middleware
        all_middleware = []
        
        # Add global middleware first
        for mw in self.middleware:
            mw_dict = self._middleware_to_dict(mw)
            if mw_dict and mw_dict.get('type') not in skip_middleware:
                all_middleware.append(mw_dict)
        
        # Add global config-based middleware
        if self.middleware_config:
            for mw_type, config in self.middleware_config.items():
                if mw_type not in skip_middleware:
                    mw_dict = {'type': mw_type}
                    mw_dict.update(config)
                    all_middleware.append(mw_dict)
        
        # Add handler-specific middleware
        for mw in handler_middleware:
            mw_dict = self._middleware_to_dict(mw)
            if mw_dict:
                all_middleware.append(mw_dict)
        
        if not all_middleware:
            return None
        
        return {
            'middleware': all_middleware,
            'skip': list(skip_middleware),
            'method': method,
            'path': path
        }
    
    def _middleware_to_dict(self, mw: Any) -> Optional[Dict[str, Any]]:
        """Convert middleware specification to dictionary."""
        if isinstance(mw, dict):
            return mw
        elif hasattr(mw, '__dict__'):
            # Convert middleware object to dict
            return {
                'type': mw.__class__.__name__.lower().replace('middleware', ''),
                **mw.__dict__
            }
        return None

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
                headers_map = request.get("headers", {})
                cookies_map = request.get("cookies", {})

                # Parse form/multipart data if needed
                form_map: Dict[str, Any] = {}
                files_map: Dict[str, Any] = {}
                content_type = headers_map.get("content-type", "")
                
                if content_type.startswith("application/x-www-form-urlencoded"):
                    from urllib.parse import parse_qs
                    body_bytes: bytes = request["body"]
                    form_data = parse_qs(body_bytes.decode("utf-8"))
                    # parse_qs returns lists, but for single values we want the value directly
                    form_map = {k: v[0] if len(v) == 1 else v for k, v in form_data.items()}
                elif content_type.startswith("multipart/form-data"):
                    # Parse multipart form data
                    boundary_idx = content_type.find("boundary=")
                    if boundary_idx >= 0:
                        boundary = content_type[boundary_idx + 9:].strip()
                        body_bytes: bytes = request["body"]
                        # Simple multipart parser
                        parts = body_bytes.split(f"--{boundary}".encode())
                        for part in parts[1:-1]:  # Skip first empty and last closing
                            if b"\r\n\r\n" in part:
                                header_section, content = part.split(b"\r\n\r\n", 1)
                                content = content.rstrip(b"\r\n")
                                headers_text = header_section.decode("utf-8", errors="ignore")
                                
                                # Parse Content-Disposition header
                                name = None
                                filename = None
                                for line in headers_text.split("\r\n"):
                                    if line.startswith("Content-Disposition:"):
                                        disp = line[20:].strip()
                                        for param in disp.split("; "):
                                            if param.startswith('name="'):
                                                name = param[6:-1]
                                            elif param.startswith('filename="'):
                                                filename = param[10:-1]
                                
                                if name:
                                    if filename:
                                        # It's a file
                                        file_info = {
                                            "filename": filename,
                                            "content": content,
                                            "size": len(content)
                                        }
                                        if name in files_map:
                                            if isinstance(files_map[name], list):
                                                files_map[name].append(file_info)
                                            else:
                                                files_map[name] = [files_map[name], file_info]
                                        else:
                                            files_map[name] = file_info
                                    else:
                                        # It's a form field
                                        value = content.decode("utf-8", errors="ignore")
                                        form_map[name] = value

                # Body decode cache
                body_obj: Any = None
                body_loaded: bool = False
                dep_cache: Dict[Any, Any] = {}

                for p in meta["params"]:
                    name = p["name"]
                    annotation = p["annotation"]
                    default = p["default"]
                    source = p["source"]
                    alias = p.get("alias")
                    depends_marker = p.get("dependency")

                    if source == "request":
                        value = request
                    elif source == "dependency":
                        dep_fn = depends_marker.dependency if depends_marker else None
                        if dep_fn is None:
                            raise ValueError(f"Depends for parameter {name} requires a callable")
                        if depends_marker.use_cache and dep_fn in dep_cache:
                            value = dep_cache[dep_fn]
                        else:
                            dep_meta = self._handler_meta.get(dep_fn)
                            if dep_meta is None:
                                dep_meta = self._compile_binder(dep_fn)
                                self._handler_meta[dep_fn] = dep_meta
                            if dep_meta.get("mode") == "request_only":
                                value = await dep_fn(request)
                            else:
                                dep_args: List[Any] = []
                                dep_kwargs: Dict[str, Any] = {}
                                for dp in dep_meta["params"]:
                                    dname = dp["name"]
                                    dan = dp["annotation"]
                                    dsrc = dp["source"]
                                    dalias = dp.get("alias")
                                    if dsrc == "request":
                                        dval = request
                                    else:
                                        key = dalias or dname
                                        if key in params_map:
                                            raw = params_map[key]
                                            dval = self._convert_primitive(str(raw), dan)
                                        elif key in query_map:
                                            raw = query_map[key]
                                            dval = self._convert_primitive(str(raw), dan)
                                        elif dsrc == "header":
                                            raw = headers_map.get(key.lower())
                                            if raw is None:
                                                raise ValueError(f"Missing required header: {key}")
                                            dval = self._convert_primitive(str(raw), dan)
                                        elif dsrc == "cookie":
                                            raw = cookies_map.get(key)
                                            if raw is None:
                                                raise ValueError(f"Missing required cookie: {key}")
                                            dval = self._convert_primitive(str(raw), dan)
                                        else:
                                            dval = None
                                    if dp["kind"] in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                                        dep_args.append(dval)
                                    else:
                                        dep_kwargs[dname] = dval
                                value = await dep_fn(*dep_args, **dep_kwargs)
                            if depends_marker.use_cache:
                                dep_cache[dep_fn] = value
                    else:
                        key = alias or name
                        if key in params_map:
                            raw = params_map[key]
                            value = self._convert_primitive(str(raw), annotation)
                        elif key in query_map:
                            raw = query_map[key]
                            value = self._convert_primitive(str(raw), annotation)
                        elif source == "header":
                            raw = headers_map.get(key.lower())
                            if raw is None:
                                if default is not inspect._empty or self._is_optional(annotation):
                                    value = None if default is inspect._empty else default
                                else:
                                    raise ValueError(f"Missing required header: {key}")
                            else:
                                value = self._convert_primitive(str(raw), annotation)
                        elif source == "cookie":
                            raw = cookies_map.get(key)
                            if raw is None:
                                if default is not inspect._empty or self._is_optional(annotation):
                                    value = None if default is inspect._empty else default
                                else:
                                    raise ValueError(f"Missing required cookie: {key}")
                            else:
                                value = self._convert_primitive(str(raw), annotation)
                        elif source == "form":
                            raw = form_map.get(key)
                            if raw is None:
                                if default is not inspect._empty or self._is_optional(annotation):
                                    value = None if default is inspect._empty else default
                                else:
                                    raise ValueError(f"Missing required form field: {key}")
                            else:
                                value = self._convert_primitive(str(raw), annotation)
                        elif source == "file":
                            raw = files_map.get(key)
                            if raw is None:
                                if default is not inspect._empty or self._is_optional(annotation):
                                    value = None if default is inspect._empty else default
                                else:
                                    raise ValueError(f"Missing required file: {key}")
                            else:
                                # For files, return the raw dict(s) containing filename and content
                                # If it's a list annotation, ensure we have a list
                                if hasattr(annotation, "__origin__") and annotation.__origin__ is list:
                                    value = raw if isinstance(raw, list) else [raw]
                                else:
                                    value = raw
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
            elif isinstance(result, PlainText):
                headers = [("content-type", "text/plain; charset=utf-8")]
                if result.headers:
                    headers.extend([(k.lower(), v) for k, v in result.headers.items()])
                return int(result.status_code), headers, result.to_bytes()
            elif isinstance(result, HTML):
                headers = [("content-type", "text/html; charset=utf-8")]
                if result.headers:
                    headers.extend([(k.lower(), v) for k, v in result.headers.items()])
                return int(result.status_code), headers, result.to_bytes()
            elif isinstance(result, Redirect):
                headers = [("location", result.url)]
                if result.headers:
                    headers.extend([(k.lower(), v) for k, v in result.headers.items()])
                return int(result.status_code), headers, b""
            elif isinstance(result, File):
                data = result.read_bytes()
                ctype = result.media_type or mimetypes.guess_type(result.path)[0] or "application/octet-stream"
                headers = [("content-type", ctype)]
                if result.filename:
                    headers.append(("content-disposition", f"attachment; filename=\"{result.filename}\""))
                if result.headers:
                    headers.extend([(k.lower(), v) for k, v in result.headers.items()])
                return int(result.status_code), headers, data
            elif isinstance(result, FileResponse):
                # Signal Rust/Actix to stream the file directly via NamedFile
                ctype = result.media_type or mimetypes.guess_type(result.path)[0] or "application/octet-stream"
                headers = [("x-bolt-file-path", result.path), ("content-type", ctype)]
                if result.filename:
                    headers.append(("content-disposition", f"attachment; filename=\"{result.filename}\""))
                if result.headers:
                    headers.extend([(k.lower(), v) for k, v in result.headers.items()])
                return int(result.status_code), headers, b""
            elif isinstance(result, StreamingResponse):
                # Pass through; Rust will detect and stream from the iterator/generator
                return result
            elif isinstance(result, (bytes, bytearray)):
                status = int(meta.get("default_status_code", 200))
                return status, [("content-type", "application/octet-stream")], bytes(result)
            elif isinstance(result, str):
                status = int(meta.get("default_status_code", 200))
                return status, [("content-type", "text/plain; charset=utf-8")], result.encode()
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
                status = int(meta.get("default_status_code", 200))
                return status, [("content-type", "application/json")], data
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
                status = int(meta.get("default_status_code", 200))
                return status, [("content-type", "application/json")], data
                
        except HTTPException as he:
            try:
                body = msgspec.json.encode({"detail": he.detail})
                headers = [("content-type", "application/json")]
            except Exception:
                body = str(he.detail).encode()
                headers = [("content-type", "text/plain; charset=utf-8")]
            if he.headers:
                headers.extend([(k.lower(), v) for k, v in he.headers.items()])
            return int(he.status_code), headers, body
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

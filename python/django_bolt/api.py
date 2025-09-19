import inspect
from typing import Any, Callable, Dict, List, Tuple
import msgspec

from .bootstrap import ensure_django_ready
from django_bolt import _core
from .responses import JSON

Request = Dict[str, Any]
Response = Tuple[int, List[Tuple[str, str]], bytes]

class BoltAPI:
    def __init__(self) -> None:
        self._routes: List[Tuple[str, str, int, Callable]] = []
        self._handlers: Dict[int, Callable] = {}
        self._next_handler_id = 0

    def get(self, path: str):
        return self._route_decorator("GET", path)

    def post(self, path: str):
        return self._route_decorator("POST", path)

    def put(self, path: str):
        return self._route_decorator("PUT", path)

    def patch(self, path: str):
        return self._route_decorator("PATCH", path)

    def delete(self, path: str):
        return self._route_decorator("DELETE", path)

    def _route_decorator(self, method: str, path: str):
        def decorator(fn: Callable):
            # Enforce async handlers
            if not inspect.iscoroutinefunction(fn):
                raise TypeError(f"Handler {fn.__name__} must be async. Use 'async def' instead of 'def'")
            
            handler_id = self._next_handler_id
            self._next_handler_id += 1
            
            self._routes.append((method, path, handler_id, fn))
            self._handlers[handler_id] = fn
            
            return fn
        return decorator

    async def _dispatch(self, handler: Callable, request: Dict[str, Any]) -> Response:
        """Async dispatch that calls the handler and returns response tuple"""
        try:
            # Extract path params to pass as kwargs
            path_params = request.get("params", {})
            
            # Call the async handler with request and path params
            result = await handler(request, **path_params)
            
            # Handle different response types
            if isinstance(result, JSON):
                return 200, [("content-type", "application/json")], result.to_bytes()
            elif isinstance(result, (bytes, bytearray)):
                return 200, [("content-type", "application/octet-stream")], bytes(result)
            elif isinstance(result, str):
                return 200, [("content-type", "text/plain; charset=utf-8")], result.encode()
            elif isinstance(result, (dict, list)):
                # Use msgspec for fast JSON encoding
                data = msgspec.json.encode(result)
                return 200, [("content-type", "application/json")], data
            else:
                # Fallback to msgspec encoding
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

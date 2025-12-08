"""
Django middleware adapter for Django-Bolt.

Provides the DjangoMiddleware class that wraps Django middleware classes
to work with Django-Bolt's async middleware chain.

Performance considerations:
- Middleware instance is created ONCE at registration time (not per-request)
- Uses contextvars to bridge async call_next without per-request instantiation
- Conversion between Bolt Request and Django HttpRequest is lazy where possible
- Django request attributes are synced back only when needed
- Uses sync_to_async for Django operations that may touch the database
"""
from __future__ import annotations

import asyncio
import contextvars
import inspect
import io
from typing import Any, Callable, Optional, Type, Union, TYPE_CHECKING

try:
    from django.http import HttpRequest, HttpResponse, QueryDict
    from django.utils.module_loading import import_string
    from asgiref.sync import sync_to_async
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    HttpRequest = None
    HttpResponse = None
    QueryDict = None
    import_string = None
    sync_to_async = None

if TYPE_CHECKING:
    from ..request import Request
    from ..responses import Response
    from .middleware import CallNext


# Context variable to hold per-request state for the get_response bridge
# This allows middleware instances to be created once at startup while
# still having access to the correct call_next at request time
_request_context: contextvars.ContextVar[dict] = contextvars.ContextVar(
    "_django_middleware_request_context"
)


class DjangoMiddleware:
    """
    Wraps a Django middleware class to work with Django-Bolt.

    Follows Django's middleware pattern:
    - __init__(get_response): Called ONCE when middleware chain is built
    - __call__(request): Called for each request

    Supports both old-style (process_request/process_response) and
    new-style (callable) Django middleware patterns.

    Performance:
        - Middleware instance is created when chain is built (not per-request)
        - Request conversion is done once per middleware in the chain
        - Uses sync_to_async for database operations

    Examples:
        # Wrap Django's built-in middleware
        from django.contrib.auth.middleware import AuthenticationMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware

        api = BoltAPI(
            middleware=[
                DjangoMiddleware(SessionMiddleware),
                DjangoMiddleware(AuthenticationMiddleware),
            ]
        )

        # Wrap by import path string
        api = BoltAPI(
            middleware=[
                DjangoMiddleware("django.contrib.sessions.middleware.SessionMiddleware"),
                DjangoMiddleware("myapp.middleware.CustomMiddleware"),
            ]
        )

    Note:
        Order matters! Django middlewares should be in the same order as
        they would be in Django's MIDDLEWARE setting.
    """

    __slots__ = (
        "middleware_class",
        "init_kwargs",
        "get_response",
        "_middleware_instance",
        "_is_old_style",
    )

    def __init__(
        self,
        middleware_class_or_get_response: Union[Type, str, Callable],
        **init_kwargs: Any
    ):
        """
        Initialize the Django middleware wrapper.

        This can be called in two ways:
        1. DjangoMiddleware(SomeMiddlewareClass) - stores the class for later instantiation
        2. DjangoMiddleware(get_response) - called by chain building, instantiates the middleware

        Args:
            middleware_class_or_get_response: Django middleware class, import path string,
                or get_response callable (when called during chain building)
            **init_kwargs: Additional kwargs passed to middleware __init__
        """
        if not DJANGO_AVAILABLE:
            raise ImportError(
                "Django is required to use DjangoMiddleware. "
                "Install Django with: pip install django"
            )

        # Check if this is chain building call (get_response is a callable)
        # vs initial configuration (middleware_class is a type or string)
        if callable(middleware_class_or_get_response) and not isinstance(middleware_class_or_get_response, type) and not isinstance(middleware_class_or_get_response, str):
            # This is being called during chain building: DjangoMiddleware(get_response)
            # We need to check if this instance was already configured with a middleware class
            # This happens when the middleware was pre-configured and is now being instantiated
            raise TypeError(
                "DjangoMiddleware must be configured with a middleware class before being used in a chain. "
                "Use DjangoMiddleware(SomeMiddlewareClass) to create a wrapper."
            )

        # Store middleware class for later instantiation
        if isinstance(middleware_class_or_get_response, str):
            self.middleware_class = import_string(middleware_class_or_get_response)
        else:
            self.middleware_class = middleware_class_or_get_response

        self.init_kwargs = init_kwargs
        self.get_response = None  # Set when chain is built
        self._middleware_instance = None  # Created when chain is built
        self._is_old_style = None  # Determined when instance is created

    def _create_middleware_instance(self, get_response: Callable) -> None:
        """
        Create the wrapped Django middleware instance.

        Called during chain building when get_response is available.
        """
        self.get_response = get_response

        # Create the get_response bridge that converts between Bolt and Django
        def get_response_bridge(django_request: HttpRequest) -> HttpResponse:
            """
            Synchronous get_response for Django middleware.
            Retrieves bolt_request from contextvar and calls get_response.
            """
            ctx = _request_context.get()
            bolt_request = ctx["bolt_request"]

            # Run the async get_response from sync context
            try:
                loop = asyncio.get_running_loop()
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(asyncio.run, get_response(bolt_request))
                    bolt_resp = future.result()
            except RuntimeError:
                bolt_resp = asyncio.run(get_response(bolt_request))

            ctx["bolt_response"] = bolt_resp
            self._sync_request_attributes(django_request, bolt_request)
            return self._to_django_response(bolt_resp)

        # Create middleware instance with the bridge
        self._middleware_instance = self.middleware_class(
            get_response_bridge, **self.init_kwargs
        )

        # Check if old-style middleware
        self._is_old_style = (
            hasattr(self._middleware_instance, 'process_request') or
            hasattr(self._middleware_instance, 'process_response') or
            hasattr(self._middleware_instance, 'process_view') or
            hasattr(self._middleware_instance, 'process_exception')
        )

    async def __call__(self, request: "Request") -> "Response":
        """
        Process request through the Django middleware.

        Follows Django's middleware pattern where __call__(request) processes
        the request and returns a response.
        """
        # Ensure middleware instance exists
        if self._middleware_instance is None:
            raise RuntimeError(
                "DjangoMiddleware was not properly initialized. "
                "The middleware chain must be built before processing requests."
            )

        # Check if we already have a Django request in context (from outer middleware)
        # This ensures session, user, etc. set by outer middleware are preserved
        existing_ctx = None
        try:
            existing_ctx = _request_context.get()
        except LookupError:
            pass

        if existing_ctx and "django_request" in existing_ctx:
            # Reuse existing Django request (preserves session, user, etc.)
            django_request = existing_ctx["django_request"]
            ctx = existing_ctx
            token = None  # Don't reset context
        else:
            # First Django middleware in chain - create new Django request
            django_request = self._to_django_request(request)

            # Set up per-request context for the get_response bridge
            ctx = {
                "bolt_request": request,
                "bolt_response": None,
                "django_request": django_request,  # Share across Django middleware chain
            }
            token = _request_context.set(ctx)

        try:
            if self._is_old_style:
                # Old-style middleware with process_* methods
                return await self._handle_old_style_middleware(
                    self._middleware_instance, django_request, request
                )
            else:
                # New-style callable middleware - run through sync_to_async
                django_response = await sync_to_async(
                    self._middleware_instance, thread_sensitive=True
                )(django_request)
                return self._to_bolt_response(django_response)
        finally:
            if token is not None:
                _request_context.reset(token)

    async def _handle_old_style_middleware(
        self,
        middleware: Any,
        django_request: HttpRequest,
        bolt_request: "Request",
    ) -> "Response":
        """Handle old-style Django middleware with process_request/process_response."""
        # Run process_request in thread pool
        if hasattr(middleware, 'process_request'):
            result = await sync_to_async(
                middleware.process_request, thread_sensitive=True
            )(django_request)
            if result is not None:
                # Middleware returned a response, short-circuit
                return self._to_bolt_response(result)

        # Run process_view if present
        if hasattr(middleware, 'process_view'):
            result = await sync_to_async(
                middleware.process_view, thread_sensitive=True
            )(django_request, None, (), {})
            if result is not None:
                return self._to_bolt_response(result)

        # Sync attributes BEFORE calling handler so handler can access them
        self._sync_request_attributes(django_request, bolt_request)

        # Call the next middleware/handler via get_response
        try:
            response = await self.get_response(bolt_request)
        except Exception as exc:
            # Run process_exception if present
            if hasattr(middleware, 'process_exception'):
                result = await sync_to_async(
                    middleware.process_exception, thread_sensitive=True
                )(django_request, exc)
                if result is not None:
                    return self._to_bolt_response(result)
            raise

        # Convert response for process_response
        django_response = self._to_django_response(response)

        # Run process_response
        if hasattr(middleware, 'process_response'):
            django_response = await sync_to_async(
                middleware.process_response, thread_sensitive=True
            )(django_request, django_response)

        # Convert back to Bolt response
        return self._to_bolt_response(django_response)

    def _to_django_request(self, request: "Request") -> HttpRequest:
        """Convert Bolt Request to Django HttpRequest."""
        django_request = HttpRequest()

        # Copy basic attributes
        django_request.method = request.method
        django_request.path = request.path
        django_request.path_info = request.path

        # Build META dict from headers
        django_request.META = self._build_meta(request)

        # Copy cookies directly
        django_request.COOKIES = dict(request.cookies) if request.cookies else {}

        # Create mutable QueryDicts and populate
        django_request.GET = QueryDict(mutable=True)
        if request.query:
            for key, value in request.query.items():
                django_request.GET[key] = value

        django_request.POST = QueryDict(mutable=True)

        # Store body for lazy parsing
        body = request.body if request.body else b""
        django_request._body = body
        django_request._stream = io.BytesIO(body)

        # Store reference to Bolt request for attribute sync
        django_request._bolt_request = request

        return django_request

    def _build_meta(self, request: "Request") -> dict:
        """Build Django META dict from Bolt request headers."""
        query_string = "&".join(
            f"{k}={v}" for k, v in request.query.items()
        ) if request.query else ""

        meta = {
            "REQUEST_METHOD": request.method,
            "PATH_INFO": request.path,
            "QUERY_STRING": query_string,
            "CONTENT_TYPE": request.headers.get("content-type", ""),
            "CONTENT_LENGTH": str(len(request.body)) if request.body else "",
            "SERVER_NAME": "localhost",
            "SERVER_PORT": "8000",
        }

        # Convert headers to META format
        for key, value in request.headers.items():
            # Skip content-type and content-length (already added)
            if key.lower() in ("content-type", "content-length"):
                continue
            meta_key = f"HTTP_{key.upper().replace('-', '_')}"
            meta[meta_key] = value

        return meta

    def _sync_request_attributes(
        self,
        django_request: HttpRequest,
        bolt_request: "Request"
    ) -> None:
        """
        Sync attributes added by Django middleware to Bolt request.

        Django middlewares commonly add:
        - request.user (AuthenticationMiddleware)
        - request.session (SessionMiddleware)
        - request.csrf_processing_done (CsrfViewMiddleware)
        """
        # Sync user - store in state dict for handler access
        if hasattr(django_request, 'user'):
            bolt_request.state["_django_user"] = django_request.user

        # Sync session
        if hasattr(django_request, 'session'):
            bolt_request.state["_django_session"] = django_request.session

        # Sync CSRF token
        if hasattr(django_request, 'META') and 'CSRF_COOKIE' in django_request.META:
            bolt_request.state["_csrf_token"] = django_request.META['CSRF_COOKIE']

        # Sync any other custom attributes (excluding standard Django attrs)
        standard_attrs = {
            'method', 'path', 'path_info', 'META', 'GET', 'POST',
            'COOKIES', 'FILES', 'resolver_match', '_body', '_stream',
            '_bolt_request', 'content_type', 'content_params',
            'encoding', 'upload_handlers', '_read_started', '_post_parse_error',
            'session', 'user',  # Already handled above
        }

        for attr in dir(django_request):
            if attr.startswith('_'):
                continue
            if attr in standard_attrs:
                continue
            try:
                value = getattr(django_request, attr, None)
                if value is not None and not callable(value):
                    bolt_request.state[f"_django_{attr}"] = value
            except Exception:
                # Skip attributes that raise exceptions
                pass

    def _to_django_response(self, response: "Response") -> HttpResponse:
        """Convert Bolt Response/MiddlewareResponse to Django HttpResponse."""
        # Handle different response types
        if hasattr(response, 'body'):
            # MiddlewareResponse has .body
            content = response.body if isinstance(response.body, bytes) else str(response.body).encode()
        elif hasattr(response, 'to_bytes'):
            content = response.to_bytes()
        elif hasattr(response, 'content'):
            content = response.content if isinstance(response.content, bytes) else str(response.content).encode()
        else:
            content = b""

        status_code = getattr(response, 'status_code', 200)
        headers = getattr(response, 'headers', {})

        django_response = HttpResponse(
            content=content,
            status=status_code,
            content_type=headers.get("content-type", headers.get("Content-Type", "application/json")),
        )

        for key, value in headers.items():
            if key.lower() not in ("content-type",):
                django_response[key] = value

        return django_response

    def _to_bolt_response(self, django_response: HttpResponse) -> "Response":
        """Convert Django HttpResponse to MiddlewareResponse for chain compatibility."""
        from ..api import MiddlewareResponse

        headers = dict(django_response.items())

        return MiddlewareResponse(
            status_code=django_response.status_code,
            headers=headers,
            body=django_response.content,
        )

    def __repr__(self) -> str:
        return f"DjangoMiddleware({self.middleware_class.__name__})"


__all__ = ["DjangoMiddleware"]

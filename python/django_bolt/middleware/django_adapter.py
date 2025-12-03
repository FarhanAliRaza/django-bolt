"""
Django middleware adapter for Django-Bolt.

Provides the DjangoMiddleware class that wraps Django middleware classes
to work with Django-Bolt's async middleware chain.

Performance considerations:
- Conversion between Bolt Request and Django HttpRequest is lazy where possible
- Django request attributes are synced back only when needed
- Uses sync_to_async for Django operations that may touch the database
"""
from __future__ import annotations

import asyncio
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


class DjangoMiddleware:
    """
    Wraps a Django middleware class to work with Django-Bolt.

    Supports both old-style (process_request/process_response) and
    new-style (callable) Django middleware patterns.

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

    Performance:
        - Request conversion is done once per middleware chain
        - Django request is cached and reused
        - Uses sync_to_async for database operations
    """

    __slots__ = (
        "middleware_class",
        "init_kwargs",
        "_middleware_instance",
    )

    def __init__(
        self,
        middleware_class: Union[Type, str],
        **init_kwargs: Any
    ):
        """
        Initialize the Django middleware wrapper.

        Args:
            middleware_class: Django middleware class or import path string
            **init_kwargs: Additional kwargs passed to middleware __init__
        """
        if not DJANGO_AVAILABLE:
            raise ImportError(
                "Django is required to use DjangoMiddleware. "
                "Install Django with: pip install django"
            )

        if isinstance(middleware_class, str):
            middleware_class = import_string(middleware_class)

        self.middleware_class = middleware_class
        self.init_kwargs = init_kwargs
        self._middleware_instance: Optional[Any] = None

    async def __call__(
        self,
        request: "Request",
        call_next: "CallNext"
    ) -> "Response":
        """Process request through the Django middleware."""
        from ..responses import Response

        # Convert Bolt request to Django HttpRequest
        django_request = self._to_django_request(request)

        # Run the Django middleware in a sync context using sync_to_async
        # This handles database operations properly
        bolt_response = await self._run_django_middleware(
            django_request, request, call_next
        )

        return bolt_response

    async def _run_django_middleware(
        self,
        django_request: HttpRequest,
        bolt_request: "Request",
        call_next: "CallNext"
    ) -> "Response":
        """Run Django middleware with proper sync/async handling."""
        from ..responses import Response

        # Create the middleware instance with a get_response that bridges
        # back to our async chain
        bolt_response_holder = {"response": None, "error": None}

        def get_response(django_req: HttpRequest) -> HttpResponse:
            """
            Synchronous get_response for Django middleware.
            This is called by new-style Django middleware.
            """
            # We need to call the async call_next from sync context
            # This will be handled by running the async chain in a new event loop
            try:
                # Get the bolt response by running async code
                bolt_resp = asyncio.get_event_loop().run_until_complete(
                    call_next(bolt_request)
                )
                bolt_response_holder["response"] = bolt_resp
                return self._to_django_response(bolt_resp)
            except RuntimeError:
                # No running event loop, create one
                bolt_resp = asyncio.run(call_next(bolt_request))
                bolt_response_holder["response"] = bolt_resp
                return self._to_django_response(bolt_resp)

        # Create middleware instance
        middleware = self.middleware_class(get_response, **self.init_kwargs)

        # Determine if this is old-style or new-style middleware
        # Old-style middleware has process_request, process_response, process_view, or process_exception
        has_process_request = hasattr(middleware, 'process_request')
        has_process_response = hasattr(middleware, 'process_response')
        has_process_view = hasattr(middleware, 'process_view')
        has_process_exception = hasattr(middleware, 'process_exception')

        if has_process_request or has_process_response or has_process_view or has_process_exception:
            # Old-style middleware with process_* methods
            return await self._handle_old_style_middleware(
                middleware, django_request, bolt_request, call_next
            )
        else:
            # New-style callable middleware
            return await self._handle_new_style_middleware(
                middleware, django_request, bolt_request, call_next
            )

    async def _handle_old_style_middleware(
        self,
        middleware: Any,
        django_request: HttpRequest,
        bolt_request: "Request",
        call_next: "CallNext"
    ) -> "Response":
        """Handle old-style Django middleware with process_request/process_response."""
        from ..responses import Response

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

        # Call the next middleware/handler
        try:
            response = await call_next(bolt_request)
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

    async def _handle_new_style_middleware(
        self,
        middleware: Any,
        django_request: HttpRequest,
        bolt_request: "Request",
        call_next: "CallNext"
    ) -> "Response":
        """Handle new-style callable Django middleware."""
        # For new-style middleware, we need to call it in a sync context
        # but capture the response properly

        response_holder = {"bolt_response": None}

        # Run the entire middleware chain synchronously
        async def run_middleware():
            # Wrap the async call in a sync function for Django
            def get_response_sync(django_req: HttpRequest) -> HttpResponse:
                # Run the async chain
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # We're in an async context, use run_in_executor
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                            future = pool.submit(asyncio.run, call_next(bolt_request))
                            bolt_resp = future.result()
                    else:
                        bolt_resp = loop.run_until_complete(call_next(bolt_request))
                except RuntimeError:
                    bolt_resp = asyncio.run(call_next(bolt_request))

                response_holder["bolt_response"] = bolt_resp
                # Sync attributes after call_next
                self._sync_request_attributes(django_req, bolt_request)
                return self._to_django_response(bolt_resp)

            # Create new middleware instance with proper get_response
            mw = self.middleware_class(get_response_sync, **self.init_kwargs)

            # Wrap the middleware __call__ in a function for sync_to_async
            def call_middleware(request):
                return mw(request)

            # Run the middleware synchronously using sync_to_async
            django_response = await sync_to_async(call_middleware, thread_sensitive=True)(django_request)

            return self._to_bolt_response(django_response)

        return await run_middleware()

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
        # Sync user
        if hasattr(django_request, 'user'):
            bolt_request._user = django_request.user

        # Sync session
        if hasattr(django_request, 'session'):
            bolt_request._state["_django_session"] = django_request.session

        # Sync CSRF token
        if hasattr(django_request, 'META') and 'CSRF_COOKIE' in django_request.META:
            bolt_request._state["_csrf_token"] = django_request.META['CSRF_COOKIE']

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
                    bolt_request._state[f"_django_{attr}"] = value
            except Exception:
                # Skip attributes that raise exceptions
                pass

    def _to_django_response(self, response: "Response") -> HttpResponse:
        """Convert Bolt Response to Django HttpResponse."""
        # Handle different response types
        if hasattr(response, 'to_bytes'):
            content = response.to_bytes()
        elif hasattr(response, 'body'):
            content = response.body if isinstance(response.body, bytes) else str(response.body).encode()
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
        """Convert Django HttpResponse to Bolt Response."""
        from ..responses import Response

        headers = dict(django_response.items())

        return Response(
            content=django_response.content,
            status_code=django_response.status_code,
            headers=headers,
        )

    def __repr__(self) -> str:
        return f"DjangoMiddleware({self.middleware_class.__name__})"


__all__ = ["DjangoMiddleware"]

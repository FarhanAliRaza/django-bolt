"""
Django middleware adapter for Django-Bolt.

Provides the DjangoMiddleware class that wraps Django middleware classes
to work with Django-Bolt's async middleware chain.

Performance considerations:
- Conversion between Bolt Request and Django HttpRequest is lazy where possible
- Django request attributes are synced back only when needed
- Async Django middleware is supported without blocking
"""
from __future__ import annotations

import asyncio
import inspect
import io
from typing import Any, Callable, Optional, Type, Union, TYPE_CHECKING

try:
    from django.http import HttpRequest, HttpResponse, QueryDict
    from django.utils.module_loading import import_string
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    HttpRequest = None
    HttpResponse = None
    QueryDict = None
    import_string = None

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
        - Attribute sync is minimal (only when needed)
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

        # Create or get middleware instance
        middleware = self._get_middleware_instance(call_next, request)

        # Check for old-style process_request
        if hasattr(middleware, 'process_request'):
            result = await self._maybe_await(
                middleware.process_request(django_request)
            )
            if result is not None:
                # Middleware returned a response, short-circuit
                return self._to_bolt_response(result)

        # Check for process_view (called right before view)
        if hasattr(middleware, 'process_view'):
            result = await self._maybe_await(
                middleware.process_view(django_request, None, (), {})
            )
            if result is not None:
                return self._to_bolt_response(result)

        # Call the next middleware/handler
        try:
            response = await call_next(request)
        except Exception as exc:
            # Check for process_exception
            if hasattr(middleware, 'process_exception'):
                result = await self._maybe_await(
                    middleware.process_exception(django_request, exc)
                )
                if result is not None:
                    return self._to_bolt_response(result)
            raise

        # Sync any attributes Django middleware added to request
        self._sync_request_attributes(django_request, request)

        # Convert response to Django HttpResponse for process_response
        django_response = self._to_django_response(response)

        # Check for process_response
        if hasattr(middleware, 'process_response'):
            django_response = await self._maybe_await(
                middleware.process_response(django_request, django_response)
            )

        # Convert back to Bolt response
        return self._to_bolt_response(django_response)

    def _get_middleware_instance(
        self,
        call_next: "CallNext",
        request: "Request"
    ) -> Any:
        """Get or create middleware instance with get_response callable."""

        # Create a synchronous get_response for Django middleware
        def get_response(django_request: HttpRequest) -> HttpResponse:
            # This is called by new-style middleware
            # We need to run the async chain synchronously
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop is not None and loop.is_running():
                # Create a future and run in executor
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(
                        asyncio.run,
                        call_next(request)
                    )
                    bolt_response = future.result()
            else:
                bolt_response = asyncio.run(call_next(request))

            return self._to_django_response(bolt_response)

        # Create middleware instance
        return self.middleware_class(get_response, **self.init_kwargs)

    def _to_django_request(self, request: "Request") -> HttpRequest:
        """Convert Bolt Request to Django HttpRequest."""
        django_request = HttpRequest()

        # Copy basic attributes
        django_request.method = request.method
        django_request.path = request.path
        django_request.path_info = request.path

        # Build META dict from headers
        django_request.META = self._build_meta(request)

        # Copy cookies
        django_request.COOKIES = dict(request.cookies) if request.cookies else {}

        # Create mutable QueryDicts
        django_request.GET = QueryDict(mutable=True)
        django_request.POST = QueryDict(mutable=True)

        # Populate GET params
        if request.query:
            for key, value in request.query.items():
                django_request.GET[key] = value

        # Store body for lazy parsing
        django_request._body = request.body
        django_request._stream = io.BytesIO(request.body)

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
            "CONTENT_LENGTH": request.headers.get("content-length", ""),
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
            bolt_request.user = django_request.user

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
            content_type=headers.get("content-type", "application/json"),
        )

        for key, value in headers.items():
            if key.lower() != "content-type":
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

    async def _maybe_await(self, result: Any) -> Any:
        """Await result if it's a coroutine."""
        if inspect.iscoroutine(result):
            return await result
        return result

    def __repr__(self) -> str:
        return f"DjangoMiddleware({self.middleware_class.__name__})"


__all__ = ["DjangoMiddleware"]

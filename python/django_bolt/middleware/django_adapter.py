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

import contextlib
import contextvars
import io
import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from asgiref.sync import async_to_sync

from ..middleware_response import MiddlewareResponse

# Use "django_bolt" logger directly (not "django_bolt.middleware") because
# Django's LOGGING config often sets propagate=False on "django_bolt",
# preventing child loggers from inheriting handlers
logger = logging.getLogger("django_bolt")

try:
    from asgiref.sync import iscoroutinefunction, markcoroutinefunction, sync_to_async
    from django.http import HttpRequest, HttpResponse, QueryDict
    from django.utils.module_loading import import_string
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    HttpRequest = None
    HttpResponse = None
    QueryDict = None
    import_string = None
    sync_to_async = None
    iscoroutinefunction = None
    markcoroutinefunction = None

if TYPE_CHECKING:
    from ..request import Request
    from ..responses import Response


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
        "_middleware_is_async",
    )

    def __init__(
        self,
        middleware_class_or_get_response: type | str | Callable,
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
        self._middleware_is_async = None  # Whether middleware supports async

    def _create_middleware_instance(self, get_response: Callable) -> None:
        """
        Create the wrapped Django middleware instance.

        Called during chain building when get_response is available.

        Key insight: Django's MiddlewareMixin (used by most middleware) detects
        whether get_response is async and adapts accordingly. By providing an
        async get_response, we enable the middleware to run in async mode,
        avoiding the need for sync_to_async/async_to_sync bridging.
        """
        self.get_response = get_response

        # Create an ASYNC get_response bridge that converts between Bolt and Django
        # This allows Django middleware using MiddlewareMixin to run in async mode
        async def get_response_bridge(django_request: HttpRequest) -> HttpResponse:
            """
            Async get_response for Django middleware.

            Django's MiddlewareMixin detects this is async and uses __acall__,
            which simply awaits get_response - no thread pool overhead.
            """
            try:
                try:
                    ctx = _request_context.get()
                except LookupError as e:
                    raise RuntimeError(
                        "Request context not set. This usually means the middleware chain "
                        "was not properly initialized or a request is being processed outside "
                        "the normal request flow."
                    ) from e

                bolt_request = ctx["bolt_request"]

                # Await the async get_response directly - no bridging needed!
                bolt_resp = await self.get_response(bolt_request)

                ctx["bolt_response"] = bolt_resp
                self._sync_request_attributes(django_request, bolt_request)
                return self._to_django_response(bolt_resp)
            except Exception as e:
                logger.error(
                    "get_response_bridge error: %s",
                    e,
                    exc_info=True,
                )
                raise

        # Mark the bridge as a coroutine function so Django's MiddlewareMixin
        # detects it as async and enables async_mode
        markcoroutinefunction(get_response_bridge)

        # Create middleware instance with the async bridge
        self._middleware_instance = self.middleware_class(
            get_response_bridge, **self.init_kwargs
        )

        # Check if the middleware instance is async-capable
        # MiddlewareMixin sets this when get_response is async
        # NOTE: We no longer check for "old-style" (process_request/process_response)
        # because MiddlewareMixin already handles these methods correctly in __acall__
        # by wrapping them in sync_to_async. Doing it ourselves causes double-wrapping
        # and severe performance degradation.
        self._middleware_is_async = iscoroutinefunction(self._middleware_instance)

    async def __call__(self, request: Request) -> Response:
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
        with contextlib.suppress(LookupError):
            existing_ctx = _request_context.get()

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
            if self._middleware_is_async:
                # Async-capable middleware (e.g., using MiddlewareMixin with async get_response)
                # MiddlewareMixin.__acall__ handles process_request/process_response internally
                # by wrapping them in sync_to_async - we don't need to do it ourselves
                django_response = await self._middleware_instance(django_request)
                return self._to_bolt_response(django_response)
            else:
                # Sync middleware without async support - run in thread pool
                django_response = await sync_to_async(
                    self._middleware_instance, thread_sensitive=True
                )(django_request)
                return self._to_bolt_response(django_response)
        except Exception as e:
            logger.error(
                "DjangoMiddleware error processing %s %s: %s",
                request.method,
                request.path,
                e,
                exc_info=True,
            )
            raise
        finally:
            if token is not None:
                _request_context.reset(token)

    def _to_django_request(self, request: Request) -> HttpRequest:
        """Convert Bolt Request to Django HttpRequest.

        Performance optimizations:
        - Reuse empty dicts/QueryDicts where possible
        - Skip BytesIO creation for empty bodies
        - Use direct attribute assignment (faster than setattr)
        """
        django_request = HttpRequest()

        # Copy basic attributes (direct assignment is faster)
        django_request.method = request.method
        django_request.path = request.path
        django_request.path_info = request.path

        # Build META dict from headers
        django_request.META = self._build_meta(request)

        # Copy cookies - use empty dict directly if no cookies
        django_request.COOKIES = dict(request.cookies) if request.cookies else {}

        # Query params - only create mutable QueryDict if we have params
        if request.query:
            django_request.GET = QueryDict(mutable=True)
            for key, value in request.query.items():
                django_request.GET[key] = value
        else:
            django_request.GET = QueryDict()  # Immutable empty (faster)

        django_request.POST = QueryDict()  # Immutable empty by default

        # Store body - skip BytesIO for empty bodies (common case for GET)
        body = request.body if request.body else b""
        django_request._body = body
        if body:
            django_request._stream = io.BytesIO(body)
        # Skip _stream for empty body - Django handles this lazily

        # Store reference to Bolt request for attribute sync
        django_request._bolt_request = request

        return django_request

    def _build_meta(self, request: Request) -> dict:
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
        bolt_request: Request
    ) -> None:
        """
        Sync attributes added by Django middleware to Bolt request.

        Django middlewares commonly add:
        - request.user (AuthenticationMiddleware)
        - request.session (SessionMiddleware)
        - request.csrf_processing_done (CsrfViewMiddleware)

        Custom middleware can add arbitrary attributes which are synced to request.state
        since PyRequest is a Rust object with fixed attributes.
        """
        # Sync user directly to bolt_request.user (same as Django) - this is writable
        if hasattr(django_request, 'user'):
            bolt_request.user = django_request.user

        # Sync auser to state
        if hasattr(django_request, 'auser'):
            bolt_request.state["auser"] = django_request.auser

        # Sync session to state
        if hasattr(django_request, 'session'):
            bolt_request.state["session"] = django_request.session

        # Sync _messages for Django's messages framework
        # This enables {% for message in messages %} in templates when using MessageMiddleware
        # Uses state dict - reading works via __getattr__ (request._messages)
        if hasattr(django_request, '_messages'):
            bolt_request.state["_messages"] = django_request._messages

        # Sync CSRF token
        if hasattr(django_request, 'META') and 'CSRF_COOKIE' in django_request.META:
            bolt_request.state["_csrf_token"] = django_request.META['CSRF_COOKIE']

        # Sync other common middleware attributes to state
        for attr in ('csrf_processing_done', 'csrf_cookie_needs_reset'):
            try:
                value = getattr(django_request, attr, None)
                if value is not None:
                    bolt_request.state[attr] = value
            except (AttributeError, TypeError):
                continue


    def _to_django_response(self, response: Response) -> HttpResponse:
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

    def _to_bolt_response(self, django_response: HttpResponse) -> MiddlewareResponse:
        """Convert Django HttpResponse to MiddlewareResponse for chain compatibility."""
        headers = dict(django_response.items())

        return MiddlewareResponse(
            status_code=django_response.status_code,
            headers=headers,
            body=django_response.content,
        )

    def __repr__(self) -> str:
        return f"DjangoMiddleware({self.middleware_class.__name__})"


class DjangoMiddlewareStack:
    """
    Wraps MULTIPLE Django middleware classes into a SINGLE Bolt middleware.

    PERFORMANCE CRITICAL: Uses a hybrid approach based on middleware type:

    Hook-based middleware (process_request/process_response):
        - Called DIRECTLY without any chain or bridging
        - Zero async/sync conversion overhead
        - ~0.01ms per request → 50,000+ RPS

    __call__-based middleware (wraps get_response):
        - Runs in thread pool with sync_to_async/async_to_sync bridging
        - Necessary to preserve wrapping semantics (short-circuit, exception handling)
        - ~0.5ms per request → ~2,000 RPS

    Most Django built-in middleware (Session, Auth, Security, etc.) use hooks,
    so they get the fast path. Custom middleware using only __call__ works but
    is slower due to required bridging.

    Request flow:
        1. Run all process_request hooks (sync, in order)
        2. Run handler (async await) OR __call__ chain (thread pool if needed)
        3. Run all process_response hooks (sync, reverse order)

    Usage:
        api = BoltAPI(django_middleware=True)
    """

    __slots__ = (
        "middleware_classes",
        "get_response",
        "_hook_middleware",
        "_call_middleware",
    )

    def __init__(self, middleware_classes: list):
        if not DJANGO_AVAILABLE:
            raise ImportError(
                "Django is required to use DjangoMiddlewareStack. "
                "Install Django with: pip install django"
            )

        self.middleware_classes = middleware_classes
        self.get_response = None
        self._hook_middleware = None  # Middleware with process_request/process_response
        self._call_middleware = None  # Middleware that only uses __call__

    def _create_middleware_instance(self, get_response: Callable) -> None:
        """
        Create middleware instances, separating hook-based from __call__-based.

        Hook-based middleware: Has process_request and/or process_response
        Call-based middleware: Only has __call__ (wraps get_response)
        """
        self.get_response = get_response

        self._hook_middleware = []
        self._call_middleware = []

        for middleware_class in self.middleware_classes:
            # Create test instance to check for hooks
            test_instance = middleware_class(lambda r: None)

            has_process_request = hasattr(test_instance, "process_request")
            has_process_response = hasattr(test_instance, "process_response")

            if has_process_request or has_process_response:
                # Hook-based middleware - we'll call hooks directly
                self._hook_middleware.append(test_instance)
            else:
                # Call-based middleware - needs to wrap get_response
                # Store the class, we'll instantiate with real get_response later
                self._call_middleware.append(middleware_class)

    async def __call__(self, request: Request) -> Response:
        """
        Process request with BROKEN CHAIN approach.

        For hook-based middleware: Call hooks directly (no chain)
        For call-based middleware: Build sync chain around handler
        """
        if self._hook_middleware is None:
            raise RuntimeError("DjangoMiddlewareStack was not properly initialized.")

        django_request = _to_django_request(request)

        # =====================================================================
        # 1. Run all process_request hooks (SYNC, in order)
        # =====================================================================
        for middleware in self._hook_middleware:
            if hasattr(middleware, "process_request"):
                response = middleware.process_request(django_request)
                if response is not None:
                    # Middleware short-circuited - return early response
                    return _to_bolt_response(response)

        # Sync attributes after all process_request hooks
        _sync_request_attributes(django_request, request)

        # =====================================================================
        # 2. Run handler (with __call__-based middleware wrapped around it)
        # =====================================================================
        if self._call_middleware:
            # __call__-based middleware needs to WRAP the handler to:
            # - Short-circuit (return early without calling handler)
            # - Catch exceptions from handler
            # - Modify request before handler runs
            #
            # We must run the sync chain in a thread pool because:
            # 1. We're in an async context (can't call sync middleware directly)
            # 2. Sync middleware expects sync get_response
            # 3. Inside thread pool, we can use async_to_sync to call async handler
            get_response = self.get_response  # Capture for closure

            def run_sync_chain():
                # Build sync chain where innermost calls async handler via async_to_sync
                def innermost_get_response(django_req):
                    bolt_resp = async_to_sync(get_response)(request)
                    return _to_django_response(bolt_resp)

                chain = innermost_get_response
                for middleware_class in reversed(self._call_middleware):
                    chain = middleware_class(chain)

                return chain(django_request)

            # Run sync chain in thread pool
            django_response = await sync_to_async(run_sync_chain, thread_sensitive=True)()
        else:
            # No __call__-based middleware - direct await (fast path!)
            bolt_response = await self.get_response(request)
            django_response = _to_django_response(bolt_response)

        # =====================================================================
        # 4. Run all process_response hooks (SYNC, reverse order)
        # =====================================================================
        for middleware in reversed(self._hook_middleware):
            if hasattr(middleware, "process_response"):
                django_response = middleware.process_response(django_request, django_response)

        # Sync attributes after all process_response hooks
        _sync_request_attributes(django_request, request)

        return _to_bolt_response(django_response)

    def __repr__(self) -> str:
        names = [cls.__name__ for cls in self.middleware_classes]
        return f"DjangoMiddlewareStack([{', '.join(names)}])"


# ============================================================================
# Module-level helper functions (shared by DjangoMiddleware and DjangoMiddlewareStack)
# ============================================================================

def _to_django_request(request: Request) -> HttpRequest:
    """Convert Bolt Request to Django HttpRequest.

    Performance optimizations:
    - Reuse empty dicts/QueryDicts where possible
    - Skip BytesIO creation for empty bodies
    - Use direct attribute assignment (faster than setattr)
    """
    django_request = HttpRequest()

    # Copy basic attributes (direct assignment is faster)
    django_request.method = request.method
    django_request.path = request.path
    django_request.path_info = request.path

    # Build META dict from headers
    django_request.META = _build_meta(request)

    # Copy cookies - use empty dict directly if no cookies
    django_request.COOKIES = dict(request.cookies) if request.cookies else {}

    # Query params - only create mutable QueryDict if we have params
    if request.query:
        django_request.GET = QueryDict(mutable=True)
        for key, value in request.query.items():
            django_request.GET[key] = value
    else:
        django_request.GET = QueryDict()  # Immutable empty (faster)

    django_request.POST = QueryDict()  # Immutable empty by default

    # Store body - skip BytesIO for empty bodies (common case for GET)
    body = request.body if request.body else b""
    django_request._body = body
    if body:
        django_request._stream = io.BytesIO(body)

    # Store reference to Bolt request for attribute sync
    django_request._bolt_request = request

    return django_request


def _build_meta(request: Request) -> dict:
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
    django_request: HttpRequest,
    bolt_request: Request
) -> None:
    """
    Sync attributes added by Django middleware to Bolt request.

    Django middlewares commonly add:
    - request.user (AuthenticationMiddleware) - SimpleLazyObject for sync access
    - request.auser (AuthenticationMiddleware) - async callable for async access
    - request.session (SessionMiddleware)
    - request.csrf_processing_done (CsrfViewMiddleware)

    Custom middleware can add arbitrary attributes which are synced to request.state
    since PyRequest is a Rust object with fixed attributes.
    """
    # Sync user (SimpleLazyObject) for sync access - this is a writable attribute on PyRequest
    if hasattr(django_request, 'user'):
        bolt_request.user = django_request.user

    # Sync auser (async callable) for async access via `await request.state["auser"]()`
    if hasattr(django_request, 'auser'):
        bolt_request.state["auser"] = django_request.auser

    # Sync session to state
    if hasattr(django_request, 'session'):
        bolt_request.state["session"] = django_request.session

    # Sync _messages for Django's messages framework
    # This enables {% for message in messages %} in templates when using MessageMiddleware
    # Uses state dict - reading works via __getattr__ (request._messages)
    if hasattr(django_request, '_messages'):
        bolt_request.state["_messages"] = django_request._messages

    # Sync CSRF token
    if hasattr(django_request, 'META') and 'CSRF_COOKIE' in django_request.META:
        bolt_request.state["_csrf_token"] = django_request.META['CSRF_COOKIE']

    # Sync other common middleware attributes to state
    for attr in ('csrf_processing_done', 'csrf_cookie_needs_reset'):
        try:
            value = getattr(django_request, attr, None)
            if value is not None:
                bolt_request.state[attr] = value
        except (AttributeError, TypeError):
            continue


def _to_django_response(response: Response) -> HttpResponse:
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


def _to_bolt_response(django_response: HttpResponse) -> MiddlewareResponse:
    """Convert Django HttpResponse to MiddlewareResponse for chain compatibility."""
    headers = dict(django_response.items())

    return MiddlewareResponse(
        status_code=django_response.status_code,
        headers=headers,
        body=django_response.content,
    )


__all__ = ["DjangoMiddleware", "DjangoMiddlewareStack"]

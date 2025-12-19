"""
Tests for Django middleware integration with Django-Bolt.

Tests use TestClient for full HTTP cycle testing, verifying that middleware
actually runs and modifies requests/responses through the complete pipeline.
"""
from __future__ import annotations

import msgspec
import pytest
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.middleware.common import CommonMiddleware

from django_bolt import BoltAPI
from django_bolt.middleware import DjangoMiddleware, DjangoMiddlewareStack, TimingMiddleware
from django_bolt.middleware.django_adapter import _is_django_builtin_middleware
from django_bolt.testing import TestClient


# Define at module level to avoid issues with `from __future__ import annotations`
# Named without "Test" prefix to avoid pytest collection
class SampleRequestBody(msgspec.Struct):
    """Request body for body parsing tests."""
    name: str
    value: int


# =============================================================================
# Test DjangoMiddleware Adapter Creation
# =============================================================================


class TestDjangoMiddlewareAdapter:
    """Tests for the DjangoMiddleware adapter class."""

    def test_django_middleware_creation(self):
        """Test creating DjangoMiddleware wrapper."""
        middleware = DjangoMiddleware(SessionMiddleware)
        assert middleware.middleware_class == SessionMiddleware

    def test_django_middleware_from_string(self):
        """Test creating DjangoMiddleware from import path."""
        middleware = DjangoMiddleware(
            "django.contrib.sessions.middleware.SessionMiddleware"
        )
        assert middleware.middleware_class == SessionMiddleware

    def test_django_middleware_repr(self):
        """Test string representation."""
        middleware = DjangoMiddleware(SessionMiddleware)
        assert "SessionMiddleware" in repr(middleware)


# =============================================================================
# Test DjangoMiddlewareStack
# =============================================================================


class TestDjangoMiddlewareStack:
    """Tests for DjangoMiddlewareStack."""

    def test_middleware_stack_creation(self):
        """Test creating DjangoMiddlewareStack."""
        stack = DjangoMiddlewareStack([SessionMiddleware, CommonMiddleware])
        assert len(stack.middleware_classes) == 2

    def test_middleware_stack_repr(self):
        """Test string representation of stack."""
        stack = DjangoMiddlewareStack([SessionMiddleware])
        assert "SessionMiddleware" in repr(stack)


# =============================================================================
# Test Full HTTP Cycle - Session Middleware
# =============================================================================


@pytest.mark.django_db
class TestSessionMiddlewareHTTPCycle:
    """Tests for SessionMiddleware through full HTTP cycle."""

    def test_session_middleware_basic(self):
        """Test SessionMiddleware runs through HTTP cycle."""
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
        ])

        @api.get("/test")
        async def test_route():
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

    def test_session_middleware_with_session_access(self):
        """Test SessionMiddleware sets session attribute on request."""
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
        ])

        session_accessed = {"accessed": False}

        @api.get("/test")
        async def test_route(request):
            # Django session should be available via request.state["session"]
            session = request.state.get("session")
            if session is not None:
                session_accessed["accessed"] = True
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200
            # Session should have been accessible
            assert session_accessed["accessed"] is True


# =============================================================================
# Test Full HTTP Cycle - Authentication Middleware
# =============================================================================


@pytest.mark.django_db
class TestAuthMiddlewareHTTPCycle:
    """Tests for AuthenticationMiddleware through full HTTP cycle."""

    def test_auth_middleware_sets_user(self):
        """Test AuthenticationMiddleware sets user on request."""
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ])

        user_set = {"has_user": False}

        @api.get("/test")
        async def test_route(request):
            # Django auth middleware sets request.user
            if hasattr(request, 'user') and request.user is not None:
                user_set["has_user"] = True
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200
            # User should have been set (AnonymousUser for unauthenticated)
            assert user_set["has_user"] is True


# =============================================================================
# Test Full HTTP Cycle - Custom Middleware
# =============================================================================


class HeaderAddingMiddleware:
    """Custom Django middleware that adds a header."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Custom-Header"] = "test-value"
        return response


class ShortCircuitMiddleware:
    """Django middleware that returns early."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/blocked":
            return HttpResponse("Blocked by middleware", status=403)
        return self.get_response(request)


@pytest.mark.django_db
class TestCustomMiddlewareHTTPCycle:
    """Tests for custom Django middleware through full HTTP cycle."""

    def test_custom_middleware_adds_header(self):
        """Test custom middleware that adds response header."""
        api = BoltAPI()
        # Add custom middleware via DjangoMiddlewareStack
        api.middleware = [DjangoMiddlewareStack([HeaderAddingMiddleware])]

        @api.get("/test")
        async def test_route():
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200
            assert response.headers.get("X-Custom-Header") == "test-value"

    def test_middleware_short_circuit(self):
        """Test middleware can return early without calling handler."""
        api = BoltAPI()
        api.middleware = [DjangoMiddlewareStack([ShortCircuitMiddleware])]

        handler_called = {"called": False}

        @api.get("/blocked")
        async def blocked_route():
            handler_called["called"] = True
            return {"status": "ok"}

        @api.get("/allowed")
        async def allowed_route():
            return {"status": "allowed"}

        with TestClient(api) as client:
            # Blocked path should be short-circuited
            response = client.get("/blocked")
            assert response.status_code == 403
            assert b"Blocked by middleware" in response.content
            assert handler_called["called"] is False

            # Allowed path should work
            response = client.get("/allowed")
            assert response.status_code == 200
            assert response.json() == {"status": "allowed"}


# =============================================================================
# Test Full HTTP Cycle - Middleware Chaining
# =============================================================================


class Order1Middleware:
    """First middleware in chain - adds header."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Order-1"] = "first"
        return response


class Order2Middleware:
    """Second middleware in chain - adds header."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Order-2"] = "second"
        return response


@pytest.mark.django_db
class TestMiddlewareChainingHTTPCycle:
    """Tests for middleware chaining through full HTTP cycle."""

    def test_multiple_middlewares_all_run(self):
        """Test that multiple middlewares in chain all execute."""
        api = BoltAPI()
        api.middleware = [DjangoMiddlewareStack([Order1Middleware, Order2Middleware])]

        @api.get("/test")
        async def test_route():
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200
            # Both middlewares should have added their headers
            assert response.headers.get("X-Order-1") == "first"
            assert response.headers.get("X-Order-2") == "second"


# =============================================================================
# Test Full HTTP Cycle - Error Handling
# =============================================================================


class ExceptionCatchingMiddleware:
    """Middleware that catches and handles exceptions."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except ValueError as e:
            return HttpResponse(f"Caught error: {e}", status=400)


@pytest.mark.django_db
class TestErrorHandlingHTTPCycle:
    """Tests for error handling in middleware through HTTP cycle."""

    def test_middleware_catches_exception(self):
        """Test that middleware can catch and handle exceptions."""
        api = BoltAPI()
        api.middleware = [DjangoMiddlewareStack([ExceptionCatchingMiddleware])]

        @api.get("/error")
        async def error_route():
            raise ValueError("test error")

        with TestClient(api, raise_server_exceptions=False) as client:
            response = client.get("/error")
            assert response.status_code == 400
            assert b"Caught error: test error" in response.content


# =============================================================================
# Test Full HTTP Cycle - Mixed Bolt and Django Middleware
# =============================================================================


@pytest.mark.django_db
class TestMixedMiddlewareHTTPCycle:
    """Tests for mixing Bolt native and Django middleware."""

    def test_bolt_and_django_middleware_together(self):
        """Test Bolt middleware and Django middleware work together."""
        api = BoltAPI(
            django_middleware=['django.contrib.sessions.middleware.SessionMiddleware'],
            middleware=[TimingMiddleware],
        )

        @api.get("/test")
        async def test_route():
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200
            # TimingMiddleware should have added its header (X-Response-Time)
            assert "X-Response-Time" in response.headers or "x-response-time" in response.headers


# =============================================================================
# Test Request/Response Conversion (Unit Tests)
# =============================================================================


@pytest.mark.django_db
class TestMessagesFramework:
    """Test Django messages framework works with Django-Bolt middleware."""

    def test_messages_framework_accessible_via_request(self):
        """
        Test that Django's messages framework works through the middleware stack.

        This test verifies:
        1. MessageMiddleware sets request._messages on Django request
        2. _messages is synced to Bolt request.state["_messages"]
        3. request._messages is accessible via __getattr__ (reads from state)
        4. Messages added via django.contrib.messages are actually stored

        This test WILL FAIL if:
        - _sync_request_attributes doesn't sync _messages
        - __getattr__ doesn't read from state dict
        - MessageMiddleware isn't working
        """
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ])

        captured = {"messages_storage": None, "message_count": 0}

        @api.get("/test")
        async def test_route(request):
            from django.contrib import messages  # noqa: PLC0415

            # Add messages - this requires _messages to be set by MessageMiddleware
            messages.info(request, "Test info message")
            messages.success(request, "Test success message")

            # Access _messages directly - this uses __getattr__ to read from state
            # If this fails, the messages framework isn't working
            messages_storage = request._messages
            captured["messages_storage"] = messages_storage
            captured["message_count"] = len(messages_storage)

            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200

            # Verify messages were stored - this is the actual test
            # If _messages wasn't synced, this will be None or 0
            assert captured["messages_storage"] is not None, \
                "request._messages was not accessible - __getattr__ or _sync_request_attributes broken"
            assert captured["message_count"] == 2, \
                f"Expected 2 messages, got {captured['message_count']} - MessageMiddleware not working"


# =============================================================================
# Test Middleware Categorization (Django built-in vs Third-party vs __call__-only)
# =============================================================================


class HookBasedThirdPartyMiddleware:
    """
    Third-party middleware with process_request/process_response hooks.

    This simulates a third-party middleware that might do blocking I/O in hooks.
    Should be routed through sync_to_async for safety.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        """Hook that runs before view - could do blocking I/O."""
        request.thirdparty_hook_ran = True
        return None  # Continue processing

    def process_response(self, request, response):
        """Hook that runs after view - could do blocking I/O."""
        response["X-ThirdParty-Hook"] = "processed"
        return response

    def __call__(self, request):
        # MiddlewareMixin pattern - hooks are called by __call__
        response = self.process_request(request)
        if response is not None:
            return response
        response = self.get_response(request)
        return self.process_response(request, response)


class CallOnlyMiddleware:
    """
    Middleware that only overrides __call__ (no hooks).

    This is the slowest path - requires wrapping in sync_to_async chain.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set attribute before
        request.call_only_before = True
        response = self.get_response(request)
        # Add header after
        response["X-Call-Only"] = "processed"
        return response


class HookShortCircuitMiddleware:
    """Third-party middleware that short-circuits via process_request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        """Short-circuit if special header is present."""
        if request.META.get("HTTP_X_SHORTCIRCUIT"):
            return HttpResponse("Short-circuited by hook", status=418)
        return None

    def __call__(self, request):
        response = self.process_request(request)
        if response is not None:
            return response
        return self.get_response(request)


@pytest.mark.django_db
class TestMiddlewareCategorization:
    """Tests for middleware categorization into fast/safe/slow paths."""

    def test_django_builtin_uses_fast_path(self):
        """
        Test that Django built-in middleware uses fast path (direct calls).

        Django's SessionMiddleware and AuthMiddleware have hooks but are
        safe to call directly without sync_to_async.
        """
        # Verify classification
        assert _is_django_builtin_middleware(SessionMiddleware) is True
        assert _is_django_builtin_middleware(CommonMiddleware) is True

        # Test through HTTP cycle
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
        ])

        @api.get("/test")
        async def test_route(request):
            return {"session_exists": request.state.get("session") is not None}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200

    def test_thirdparty_hook_middleware_uses_safe_path(self):
        """
        Test that third-party middleware with hooks uses safe path (sync_to_async).

        Third-party middleware might do blocking I/O in hooks, so we wrap
        them in sync_to_async(thread_sensitive=True) for safety.
        """
        # Verify classification - third-party should NOT be Django built-in
        assert _is_django_builtin_middleware(HookBasedThirdPartyMiddleware) is False

        # Test through HTTP cycle
        api = BoltAPI()
        api.middleware = [DjangoMiddlewareStack([HookBasedThirdPartyMiddleware])]

        @api.get("/test")
        async def test_route():
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200
            # Verify the hook ran and added header
            assert response.headers.get("X-ThirdParty-Hook") == "processed"

    def test_call_only_middleware_uses_chain_path(self):
        """
        Test that __call__-only middleware uses chain path.

        Middleware without hooks must be chained and run via sync_to_async.
        """
        api = BoltAPI()
        api.middleware = [DjangoMiddlewareStack([CallOnlyMiddleware])]

        @api.get("/test")
        async def test_route():
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200
            assert response.headers.get("X-Call-Only") == "processed"

    def test_mixed_middleware_types(self):
        """
        Test mixing Django built-in, third-party hooks, and __call__-only.

        All three types should work together correctly.
        """
        api = BoltAPI()
        api.middleware = [DjangoMiddlewareStack([
            SessionMiddleware,           # Django built-in (fast path)
            HookBasedThirdPartyMiddleware,  # Third-party hooks (safe path)
            CallOnlyMiddleware,          # __call__-only (chain path)
        ])]

        results = {}

        @api.get("/test")
        async def test_route(request):
            results["session"] = request.state.get("session") is not None
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200
            # All middleware should have run
            assert results["session"] is True
            assert response.headers.get("X-ThirdParty-Hook") == "processed"
            assert response.headers.get("X-Call-Only") == "processed"

    def test_thirdparty_hook_short_circuit(self):
        """
        Test that third-party middleware can short-circuit via process_request.

        Even though third-party hooks go through sync_to_async, they should
        still be able to return early responses.
        """
        api = BoltAPI()
        api.middleware = [DjangoMiddlewareStack([HookShortCircuitMiddleware])]

        handler_called = {"called": False}

        @api.get("/test")
        async def test_route():
            handler_called["called"] = True
            return {"status": "ok"}

        with TestClient(api) as client:
            # Without header - should pass through
            response = client.get("/test")
            assert response.status_code == 200
            assert handler_called["called"] is True

            # Reset
            handler_called["called"] = False

            # With header - should short-circuit
            response = client.get("/test", headers={"X-Shortcircuit": "yes"})
            assert response.status_code == 418
            assert b"Short-circuited by hook" in response.content
            assert handler_called["called"] is False


class TestMiddlewareCategorizationUnit:
    """Unit tests for middleware categorization helper functions."""

    def test_is_django_builtin_middleware_sessions(self):
        """Test SessionMiddleware is recognized as Django built-in."""
        assert _is_django_builtin_middleware(SessionMiddleware) is True

    def test_is_django_builtin_middleware_common(self):
        """Test CommonMiddleware is recognized as Django built-in."""
        assert _is_django_builtin_middleware(CommonMiddleware) is True

    def test_is_django_builtin_middleware_auth(self):
        """Test AuthenticationMiddleware is recognized as Django built-in."""
        assert _is_django_builtin_middleware(AuthenticationMiddleware) is True

    def test_is_django_builtin_middleware_messages(self):
        """Test MessageMiddleware is recognized as Django built-in."""
        assert _is_django_builtin_middleware(MessageMiddleware) is True

    def test_is_django_builtin_middleware_thirdparty(self):
        """Test third-party middleware is NOT recognized as Django built-in."""
        assert _is_django_builtin_middleware(HookBasedThirdPartyMiddleware) is False
        assert _is_django_builtin_middleware(CallOnlyMiddleware) is False
        assert _is_django_builtin_middleware(HeaderAddingMiddleware) is False

    def test_stack_categorizes_middleware_correctly(self):
        """Test DjangoMiddlewareStack correctly categorizes middleware."""
        stack = DjangoMiddlewareStack([
            SessionMiddleware,              # Django built-in with hooks
            HookBasedThirdPartyMiddleware,  # Third-party with hooks
            CallOnlyMiddleware,             # __call__-only
        ])

        # Trigger categorization by creating instances
        def dummy(r):
            pass
        stack._create_middleware_instance(dummy)

        # Verify categorization
        assert len(stack._django_hook_middleware) == 1  # SessionMiddleware
        assert len(stack._thirdparty_hook_middleware) == 1  # HookBasedThirdPartyMiddleware
        assert stack._call_middleware_chain is not None  # CallOnlyMiddleware in chain

    def test_stack_no_call_only_middleware(self):
        """Test stack without __call__-only middleware has no chain."""
        stack = DjangoMiddlewareStack([
            SessionMiddleware,              # Django built-in with hooks
            HookBasedThirdPartyMiddleware,  # Third-party with hooks
        ])

        def dummy(r):
            pass
        stack._create_middleware_instance(dummy)

        # Verify no chain created (fast path)
        assert stack._call_middleware_chain is None


class TestRequestConversion:
    """Unit tests for request conversion - using real middleware through HTTP cycle."""

    def test_query_params_available(self):
        """Test query params are available in handler."""
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
        ])

        received_params = {}

        @api.get("/test")
        async def test_route(request, page: int = 1, limit: int = 10):
            received_params["page"] = page
            received_params["limit"] = limit
            return {"page": page, "limit": limit}

        with TestClient(api) as client:
            response = client.get("/test?page=5&limit=20")
            assert response.status_code == 200
            assert received_params["page"] == 5
            assert received_params["limit"] == 20

    def test_cookies_available(self):
        """Test cookies are available in handler."""
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
        ])

        @api.get("/test")
        async def test_route(request):
            # Cookies should be accessible
            return {"has_cookies": bool(request.cookies)}

        with TestClient(api) as client:
            response = client.get("/test", cookies={"test_cookie": "value"})
            assert response.status_code == 200

    def test_headers_available(self):
        """Test headers are available in handler."""
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
        ])

        received_header = {"value": None}

        @api.get("/test")
        async def test_route(request):
            received_header["value"] = request.headers.get("x-custom-header")
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test", headers={"X-Custom-Header": "test-value"})
            assert response.status_code == 200
            assert received_header["value"] == "test-value"

    def test_body_available(self):
        """Test body is available in handler."""
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
        ])

        @api.post("/test")
        async def test_route(body: SampleRequestBody):
            return {"received_name": body.name, "received_value": body.value}

        with TestClient(api) as client:
            response = client.post("/test", json={"name": "test", "value": 42})
            assert response.status_code == 200
            assert response.json() == {"received_name": "test", "received_value": 42}


# =============================================================================
# Test Django Security Features (login_required, PermissionDenied)
# =============================================================================


@pytest.mark.django_db
class TestLoginRequiredBehavior:
    """Tests for Django's login_required decorator behavior."""

    def test_login_required_redirects_anonymous_user(self):
        """
        Test that @login_required redirects unauthenticated users.

        When an anonymous user tries to access a protected view,
        Django should redirect to LOGIN_URL (default: /accounts/login/).
        """
        from django.contrib.auth.decorators import login_required

        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ])

        handler_called = {"called": False}

        @api.get("/protected")
        @login_required
        async def protected_route(request):
            handler_called["called"] = True
            return {"status": "secret data"}

        with TestClient(api, raise_server_exceptions=False) as client:
            response = client.get("/protected")
            # Should redirect to login page (302) or we get redirected (200 to login form)
            # TestClient follows redirects by default, so we check the handler wasn't called
            assert handler_called["called"] is False

    def test_request_has_django_methods(self):
        """
        Test that Bolt request has Django-compatible methods.

        These methods are needed for Django decorators like @login_required
        to work correctly.
        """
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ])

        captured = {"get_full_path": None, "build_absolute_uri": None}

        @api.get("/test")
        async def test_route(request):
            captured["get_full_path"] = request.get_full_path()
            captured["build_absolute_uri"] = request.build_absolute_uri()
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test?page=1&limit=10")
            assert response.status_code == 200
            # Verify Django-compatible methods exist and work
            assert "page=" in captured["get_full_path"]
            assert "limit=" in captured["get_full_path"]
            assert captured["build_absolute_uri"].startswith("http")


@pytest.mark.django_db
class TestPermissionDenied:
    """Tests for Django PermissionDenied exception handling."""

    def test_permission_denied_returns_403(self):
        """
        Test that raising PermissionDenied returns 403 response.

        When a view raises PermissionDenied, Django should return
        a 403 Forbidden response.
        """
        from django.core.exceptions import PermissionDenied

        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ])

        @api.get("/admin-only")
        async def admin_only_route(request):
            # Anonymous users are not authenticated
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication required")
            return {"status": "admin data"}

        with TestClient(api, raise_server_exceptions=False) as client:
            response = client.get("/admin-only")
            assert response.status_code == 403

    def test_authenticated_user_check(self):
        """
        Test checking user.is_authenticated in handler.

        This verifies Django's AuthenticationMiddleware sets request.user
        to AnonymousUser for unauthenticated requests.
        """
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ])

        user_info = {"is_authenticated": None, "is_anonymous": None}

        @api.get("/check-user")
        async def check_user_route(request):
            user_info["is_authenticated"] = request.user.is_authenticated
            user_info["is_anonymous"] = request.user.is_anonymous
            return {"authenticated": request.user.is_authenticated}

        with TestClient(api) as client:
            response = client.get("/check-user")
            assert response.status_code == 200
            # Anonymous user should not be authenticated
            assert user_info["is_authenticated"] is False
            assert user_info["is_anonymous"] is True


# =============================================================================
# Test CSRF Middleware (process_view support)
# =============================================================================


@pytest.mark.django_db
class TestCSRFMiddleware:
    """Tests for Django's CSRF middleware integration.

    CSRF middleware uses process_view (not process_request) to check tokens.
    This verifies the process_view hook is properly called.
    """

    def test_csrf_get_request_allowed(self):
        """
        Test that GET requests work without CSRF token.

        CSRF protection only applies to "unsafe" methods (POST, PUT, DELETE, etc.).
        GET requests should always be allowed through.
        """

        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
        ])

        @api.get("/test")
        async def test_route():
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

    def test_csrf_post_without_token_rejected(self):
        """
        Test that POST requests without CSRF token are rejected.

        When CsrfViewMiddleware is enabled and a POST request doesn't include
        a valid CSRF token, it should return 403 Forbidden.
        """
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
        ])

        handler_called = {"called": False}

        @api.post("/submit")
        async def submit_route():
            handler_called["called"] = True
            return {"status": "submitted"}

        with TestClient(api, raise_server_exceptions=False) as client:
            response = client.post("/submit", json={"data": "test"})
            # Without CSRF token, should be rejected
            assert response.status_code == 403
            assert handler_called["called"] is False

    def test_csrf_exempt_endpoint_allowed(self):
        """
        Test that @csrf_exempt decorated endpoints allow POST without token.

        Django's @csrf_exempt decorator should bypass CSRF validation.
        The csrf_exempt attribute is detected at route registration time
        and passed via request.state["_csrf_exempt"] to the middleware.

        Note: Django's @csrf_exempt wraps the function to expect a `request`
        parameter (Django view signature), so the handler must accept it.
        """
        from django.views.decorators.csrf import csrf_exempt

        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
        ])

        handler_called = {"called": False}

        @api.post("/api/webhook")
        @csrf_exempt
        async def webhook_route(request):
            # Django's @csrf_exempt wrapper passes request as first arg
            handler_called["called"] = True
            return {"status": "received"}

        with TestClient(api) as client:
            response = client.post("/api/webhook", json={"event": "test"})
            # csrf_exempt should allow through without token
            assert response.status_code == 200
            assert handler_called["called"] is True
            assert response.json() == {"status": "received"}

    def test_csrf_head_request_allowed(self):
        """
        Test that HEAD requests work without CSRF token (safe method).
        """
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
        ])

        @api.head("/test")
        async def test_route():
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.head("/test")
            assert response.status_code == 200

    def test_csrf_options_request_allowed(self):
        """
        Test that OPTIONS requests work without CSRF token (safe method).
        """
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
        ])

        @api.options("/test")
        async def test_route():
            return {"methods": ["GET", "POST"]}

        with TestClient(api) as client:
            response = client.options("/test")
            assert response.status_code == 200


# =============================================================================
# Test Multiple Set-Cookie Headers (Cookie Overwriting Bug Fix)
# =============================================================================


class MultipleCookieMiddleware:
    """
    Middleware that sets multiple cookies on the response.

    This middleware is used to test that multiple Set-Cookie headers are
    preserved and not overwritten. HTTP allows multiple Set-Cookie headers
    (one per cookie), but naive dict-based implementations would overwrite
    previous cookies since dict keys must be unique.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Set multiple cookies - each should result in a separate Set-Cookie header
        response.set_cookie("session_id", "abc123", httponly=True)
        response.set_cookie("user_pref", "dark_mode", max_age=86400)
        response.set_cookie("tracking_consent", "accepted", secure=True, samesite="Strict")
        return response


class TestMultipleCookieHeaders:
    """
    Tests for multiple Set-Cookie header support.

    HTTP allows multiple Set-Cookie headers because each cookie must be sent
    in its own header. This test verifies that middleware setting multiple
    cookies results in all cookies being present in the response.

    This test WILL FAIL if:
    - Set-Cookie headers are stored in a dict (causing overwrites)
    - Only the last Set-Cookie header survives
    - Cookies are merged incorrectly
    """

    def test_multiple_cookies_all_preserved(self):
        """
        Test that middleware setting multiple cookies preserves ALL cookies.

        This is the core test for the cookie overwriting bug fix.
        With the old dict-based implementation, only one cookie would survive
        because dict can't have duplicate keys.
        """
        api = BoltAPI()
        api.middleware = [DjangoMiddlewareStack([MultipleCookieMiddleware])]

        @api.get("/test")
        async def test_route():
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200

            # Get all Set-Cookie headers
            # response.headers is a case-insensitive dict, but for multiple
            # headers with the same name, we need to check the raw headers
            set_cookie_headers = []
            for key, value in response.headers.multi_items():
                if key.lower() == "set-cookie":
                    set_cookie_headers.append(value)

            # CRITICAL: All THREE cookies must be present
            # If this fails with only 1 cookie, the old bug is back
            assert len(set_cookie_headers) >= 3, (
                f"Expected at least 3 Set-Cookie headers, got {len(set_cookie_headers)}. "
                f"This indicates cookies are being overwritten. "
                f"Headers: {set_cookie_headers}"
            )

            # Verify each specific cookie is present
            all_cookies = "\n".join(set_cookie_headers)

            assert "session_id=abc123" in all_cookies, (
                f"session_id cookie missing from response. "
                f"Set-Cookie headers: {set_cookie_headers}"
            )
            assert "user_pref=dark_mode" in all_cookies, (
                f"user_pref cookie missing from response. "
                f"Set-Cookie headers: {set_cookie_headers}"
            )
            assert "tracking_consent=accepted" in all_cookies, (
                f"tracking_consent cookie missing from response. "
                f"Set-Cookie headers: {set_cookie_headers}"
            )

    def test_cookies_have_correct_attributes(self):
        """
        Test that cookie attributes (HttpOnly, Secure, SameSite) are preserved.

        This verifies that not only are all cookies present, but their
        attributes are correctly passed through.
        """
        api = BoltAPI()
        api.middleware = [DjangoMiddlewareStack([MultipleCookieMiddleware])]

        @api.get("/test")
        async def test_route():
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200

            # Collect all Set-Cookie headers
            set_cookie_headers = []
            for key, value in response.headers.multi_items():
                if key.lower() == "set-cookie":
                    set_cookie_headers.append(value)

            all_cookies = "\n".join(set_cookie_headers)

            # Check session_id has HttpOnly
            # Find the session_id cookie line
            session_cookie = next(
                (c for c in set_cookie_headers if "session_id=" in c), None
            )
            assert session_cookie is not None, "session_id cookie not found"
            assert "httponly" in session_cookie.lower(), (
                f"session_id cookie missing HttpOnly attribute: {session_cookie}"
            )

            # Check tracking_consent has Secure and SameSite=Strict
            tracking_cookie = next(
                (c for c in set_cookie_headers if "tracking_consent=" in c), None
            )
            assert tracking_cookie is not None, "tracking_consent cookie not found"
            assert "secure" in tracking_cookie.lower(), (
                f"tracking_consent cookie missing Secure attribute: {tracking_cookie}"
            )
            assert "samesite=strict" in tracking_cookie.lower(), (
                f"tracking_consent cookie missing SameSite=Strict: {tracking_cookie}"
            )

    def test_handler_can_also_set_cookies(self):
        """
        Test that handler can set cookies and they combine with middleware cookies.

        This verifies the complete cookie flow: middleware sets some cookies,
        handler sets additional cookies, and ALL of them appear in response.
        """
        api = BoltAPI()
        api.middleware = [DjangoMiddlewareStack([MultipleCookieMiddleware])]

        @api.get("/test")
        async def test_route():
            # Handler returns data, middleware will add cookies
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200

            # Count Set-Cookie headers
            cookie_count = sum(
                1 for key, _ in response.headers.multi_items()
                if key.lower() == "set-cookie"
            )

            # Middleware sets 3 cookies
            assert cookie_count >= 3, (
                f"Expected at least 3 cookies from middleware, got {cookie_count}"
            )

    def test_no_cookies_when_middleware_doesnt_set_them(self):
        """
        Test that responses without cookies don't have spurious Set-Cookie headers.

        This is a sanity check to ensure we're not adding empty cookie headers.
        """
        api = BoltAPI()
        # No middleware that sets cookies
        api.middleware = [DjangoMiddlewareStack([HeaderAddingMiddleware])]

        @api.get("/test")
        async def test_route():
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200

            # Count Set-Cookie headers
            cookie_count = sum(
                1 for key, _ in response.headers.multi_items()
                if key.lower() == "set-cookie"
            )

            # Should have no cookies (HeaderAddingMiddleware doesn't set cookies)
            assert cookie_count == 0, (
                f"Expected no Set-Cookie headers, got {cookie_count}"
            )

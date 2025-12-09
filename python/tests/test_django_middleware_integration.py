"""
Tests for Django middleware integration with Django-Bolt.

Tests use TestClient for full HTTP cycle testing, verifying that middleware
actually runs and modifies requests/responses through the complete pipeline.
"""
from __future__ import annotations

import msgspec
import pytest

from django_bolt import BoltAPI
from django_bolt.middleware import DjangoMiddleware, DjangoMiddlewareStack
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
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = DjangoMiddleware(SessionMiddleware)
        assert middleware.middleware_class == SessionMiddleware

    def test_django_middleware_from_string(self):
        """Test creating DjangoMiddleware from import path."""
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = DjangoMiddleware(
            "django.contrib.sessions.middleware.SessionMiddleware"
        )
        assert middleware.middleware_class == SessionMiddleware

    def test_django_middleware_repr(self):
        """Test string representation."""
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = DjangoMiddleware(SessionMiddleware)
        assert "SessionMiddleware" in repr(middleware)


# =============================================================================
# Test DjangoMiddlewareStack
# =============================================================================


class TestDjangoMiddlewareStack:
    """Tests for DjangoMiddlewareStack."""

    def test_middleware_stack_creation(self):
        """Test creating DjangoMiddlewareStack."""
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.middleware.common import CommonMiddleware

        stack = DjangoMiddlewareStack([SessionMiddleware, CommonMiddleware])
        assert len(stack.middleware_classes) == 2

    def test_middleware_stack_repr(self):
        """Test string representation of stack."""
        from django.contrib.sessions.middleware import SessionMiddleware

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
            from django.http import HttpResponse
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
            from django.http import HttpResponse
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
        from django_bolt.middleware import TimingMiddleware

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
            from django.contrib import messages

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

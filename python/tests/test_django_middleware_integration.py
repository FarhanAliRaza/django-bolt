"""
Tests for Django middleware integration with Django-Bolt.

Tests the DjangoMiddleware adapter with:
- Request/Response conversion
- Custom Django middleware
- Basic middleware functionality
"""
from __future__ import annotations

import pytest
from typing import Any
from unittest.mock import Mock, patch

from django.http import HttpRequest, HttpResponse

from django_bolt.request import Request, State
from django_bolt.middleware import DjangoMiddleware, BaseMiddleware, CallNext
from django_bolt.responses import Response


# ═══════════════════════════════════════════════════════════════════════════
# Test DjangoMiddleware Adapter Creation
# ═══════════════════════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════════════════════
# Test Request Conversion
# ═══════════════════════════════════════════════════════════════════════════


class TestRequestConversion:
    """Tests for converting Bolt Request to Django HttpRequest."""

    def test_basic_conversion(self):
        """Test basic request conversion."""
        from django.contrib.sessions.middleware import SessionMiddleware
        mw = DjangoMiddleware(SessionMiddleware)

        bolt_request = Request(
            method="POST",
            path="/api/test",
            body=b'{"key": "value"}',
            headers={"content-type": "application/json"},
            query={"page": "1"},
            cookies={"session": "abc123"},
        )

        django_request = mw._to_django_request(bolt_request)

        assert django_request.method == "POST"
        assert django_request.path == "/api/test"
        assert django_request.path_info == "/api/test"
        assert django_request._body == b'{"key": "value"}'
        assert django_request.GET.get("page") == "1"
        assert django_request.COOKIES.get("session") == "abc123"

    def test_headers_to_meta(self):
        """Test headers converted to Django META format."""
        from django.contrib.sessions.middleware import SessionMiddleware
        mw = DjangoMiddleware(SessionMiddleware)

        bolt_request = Request(
            method="GET",
            path="/test",
            headers={
                "authorization": "Bearer token123",
                "x-custom-header": "custom-value",
                "content-type": "application/json",
            },
        )

        django_request = mw._to_django_request(bolt_request)

        assert django_request.META["HTTP_AUTHORIZATION"] == "Bearer token123"
        assert django_request.META["HTTP_X_CUSTOM_HEADER"] == "custom-value"
        assert django_request.META["CONTENT_TYPE"] == "application/json"
        assert django_request.META["REQUEST_METHOD"] == "GET"

    def test_query_params_conversion(self):
        """Test query params are properly converted."""
        from django.contrib.sessions.middleware import SessionMiddleware
        mw = DjangoMiddleware(SessionMiddleware)

        bolt_request = Request(
            method="GET",
            path="/search",
            query={"q": "test", "page": "2", "limit": "10"},
        )

        django_request = mw._to_django_request(bolt_request)

        assert django_request.GET.get("q") == "test"
        assert django_request.GET.get("page") == "2"
        assert django_request.GET.get("limit") == "10"

    def test_cookies_conversion(self):
        """Test cookies are properly converted."""
        from django.contrib.sessions.middleware import SessionMiddleware
        mw = DjangoMiddleware(SessionMiddleware)

        bolt_request = Request(
            method="GET",
            path="/test",
            cookies={"session": "abc123", "preference": "dark"},
        )

        django_request = mw._to_django_request(bolt_request)

        assert django_request.COOKIES.get("session") == "abc123"
        assert django_request.COOKIES.get("preference") == "dark"

    def test_body_conversion(self):
        """Test body is properly available."""
        from django.contrib.sessions.middleware import SessionMiddleware
        mw = DjangoMiddleware(SessionMiddleware)

        body = b'{"name": "test", "value": 123}'
        bolt_request = Request(
            method="POST",
            path="/submit",
            body=body,
            headers={"content-type": "application/json"},
        )

        django_request = mw._to_django_request(bolt_request)

        assert django_request._body == body
        assert django_request.body == body


# ═══════════════════════════════════════════════════════════════════════════
# Test Response Conversion
# ═══════════════════════════════════════════════════════════════════════════


class TestResponseConversion:
    """Tests for converting between Bolt and Django responses."""

    def test_bolt_to_django_response(self):
        """Test converting Bolt Response to Django HttpResponse."""
        from django.contrib.sessions.middleware import SessionMiddleware
        mw = DjangoMiddleware(SessionMiddleware)

        bolt_response = Response(
            content={"status": "ok"},
            status_code=200,
            headers={"X-Custom": "value"},
        )

        django_response = mw._to_django_response(bolt_response)

        assert django_response.status_code == 200
        assert django_response["X-Custom"] == "value"

    def test_django_to_bolt_response(self):
        """Test converting Django HttpResponse to Bolt Response."""
        from django.contrib.sessions.middleware import SessionMiddleware
        mw = DjangoMiddleware(SessionMiddleware)

        django_response = HttpResponse(
            content=b'{"result": "success"}',
            status=201,
            content_type="application/json",
        )
        django_response["X-Request-ID"] = "12345"

        bolt_response = mw._to_bolt_response(django_response)

        assert bolt_response.status_code == 201
        assert bolt_response.headers.get("X-Request-ID") == "12345"
        assert bolt_response.content == b'{"result": "success"}'


# ═══════════════════════════════════════════════════════════════════════════
# Test Custom Django Middleware
# ═══════════════════════════════════════════════════════════════════════════


class SimpleOldStyleMiddleware:
    """Old-style Django middleware with process_request/process_response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        request.custom_attr = "from_process_request"
        return None  # Continue processing

    def process_response(self, request, response):
        response["X-Old-Style"] = "processed"
        return response


class SimpleNewStyleMiddleware:
    """New-style callable Django middleware."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Before view
        request.new_style_ran = True

        response = self.get_response(request)

        # After view
        response["X-New-Style"] = "processed"
        return response


class ShortCircuitMiddleware:
    """Middleware that returns early without calling get_response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        if request.path == "/blocked":
            return HttpResponse("Blocked", status=403)
        return None


class TestCustomMiddleware:
    """Tests for custom Django middleware integration."""

    @pytest.mark.asyncio
    async def test_old_style_middleware_process_request(self):
        """Test old-style middleware process_request is called."""
        mw = DjangoMiddleware(SimpleOldStyleMiddleware)

        request = Request(method="GET", path="/test")
        request_attrs = {}

        async def handler(req: Request) -> Response:
            # Check if custom attr was synced
            request_attrs["custom"] = req._state.get("_django_custom_attr")
            return Response(content={"status": "ok"}, status_code=200)

        response = await mw(request, handler)

        assert response.status_code == 200
        assert response.headers.get("X-Old-Style") == "processed"

    @pytest.mark.asyncio
    async def test_new_style_middleware_callable(self):
        """Test new-style callable middleware."""
        mw = DjangoMiddleware(SimpleNewStyleMiddleware)

        request = Request(method="GET", path="/test")

        async def handler(req: Request) -> Response:
            return Response(content={"status": "ok"}, status_code=200)

        response = await mw(request, handler)

        assert response.status_code == 200
        assert response.headers.get("X-New-Style") == "processed"

    @pytest.mark.asyncio
    async def test_middleware_short_circuit(self):
        """Test middleware can return early without calling handler."""
        mw = DjangoMiddleware(ShortCircuitMiddleware)

        request = Request(method="GET", path="/blocked")
        handler_called = False

        async def handler(req: Request) -> Response:
            nonlocal handler_called
            handler_called = True
            return Response(content={"status": "ok"}, status_code=200)

        response = await mw(request, handler)

        assert response.status_code == 403
        assert response.content == b"Blocked"
        assert handler_called is False


# ═══════════════════════════════════════════════════════════════════════════
# Test Attribute Syncing
# ═══════════════════════════════════════════════════════════════════════════


class AttributeSettingMiddleware:
    """Middleware that sets custom attributes on request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        request.tracking_id = "track-123"
        request.feature_flags = ["flag1", "flag2"]
        return None

    def process_response(self, request, response):
        return response


class TestAttributeSyncing:
    """Tests for syncing attributes between Django and Bolt requests."""

    @pytest.mark.asyncio
    async def test_custom_attributes_synced(self):
        """Test custom attributes are synced to Bolt request state."""
        mw = DjangoMiddleware(AttributeSettingMiddleware)

        request = Request(method="GET", path="/test")
        synced_attrs = {}

        async def handler(req: Request) -> Response:
            synced_attrs["tracking_id"] = req._state.get("_django_tracking_id")
            synced_attrs["feature_flags"] = req._state.get("_django_feature_flags")
            return Response(content={"status": "ok"}, status_code=200)

        await mw(request, handler)

        assert synced_attrs.get("tracking_id") == "track-123"
        assert synced_attrs.get("feature_flags") == ["flag1", "flag2"]


# ═══════════════════════════════════════════════════════════════════════════
# Test Middleware Chaining
# ═══════════════════════════════════════════════════════════════════════════


class HeaderMiddleware1:
    """First middleware in chain."""

    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        request.chain_order = ["mw1_request"]
        return None

    def process_response(self, request, response):
        response["X-Chain-1"] = "yes"
        return response


class HeaderMiddleware2:
    """Second middleware in chain."""

    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        if hasattr(request, 'chain_order'):
            request.chain_order.append("mw2_request")
        return None

    def process_response(self, request, response):
        response["X-Chain-2"] = "yes"
        return response


class TestMiddlewareChaining:
    """Tests for chaining multiple Django middlewares."""

    @pytest.mark.asyncio
    async def test_two_middlewares_chained(self):
        """Test two Django middlewares can be chained."""
        mw1 = DjangoMiddleware(HeaderMiddleware1)
        mw2 = DjangoMiddleware(HeaderMiddleware2)

        request = Request(method="GET", path="/test")

        async def handler(req: Request) -> Response:
            return Response(content={"status": "ok"}, status_code=200)

        # Chain: mw1 -> mw2 -> handler
        async def mw2_chain(req: Request) -> Response:
            return await mw2(req, handler)

        response = await mw1(request, mw2_chain)

        assert response.status_code == 200
        # Both middlewares should have added their headers
        assert response.headers.get("X-Chain-1") == "yes"
        assert response.headers.get("X-Chain-2") == "yes"


# ═══════════════════════════════════════════════════════════════════════════
# Test Mixed Bolt and Django Middleware
# ═══════════════════════════════════════════════════════════════════════════


class TrackingBoltMiddleware(BaseMiddleware):
    """A Bolt native middleware for testing."""

    def __init__(self):
        super().__init__()
        self.requests_seen = 0

    async def handle(self, request: Request, call_next: CallNext) -> Response:
        self.requests_seen += 1
        request.state["bolt_tracked"] = True
        request.state["request_number"] = self.requests_seen

        response = await call_next(request)

        response.headers["X-Bolt-Tracked"] = "yes"
        return response


class TestMixedMiddleware:
    """Tests for mixing Bolt and Django middleware."""

    @pytest.mark.asyncio
    async def test_bolt_then_django_middleware(self):
        """Test Bolt middleware before Django middleware."""
        bolt_mw = TrackingBoltMiddleware()
        django_mw = DjangoMiddleware(HeaderMiddleware1)

        request = Request(method="GET", path="/test")

        async def handler(req: Request) -> Response:
            assert req.state.get("bolt_tracked") is True
            return Response(content={"status": "ok"}, status_code=200)

        # Chain: Bolt -> Django -> handler
        async def django_chain(req: Request) -> Response:
            return await django_mw(req, handler)

        response = await bolt_mw(request, django_chain)

        assert response.status_code == 200
        assert response.headers.get("X-Bolt-Tracked") == "yes"
        assert response.headers.get("X-Chain-1") == "yes"
        assert bolt_mw.requests_seen == 1

    @pytest.mark.asyncio
    async def test_django_then_bolt_middleware(self):
        """Test Django middleware before Bolt middleware."""
        django_mw = DjangoMiddleware(HeaderMiddleware1)
        bolt_mw = TrackingBoltMiddleware()

        request = Request(method="GET", path="/test")

        async def handler(req: Request) -> Response:
            return Response(content={"status": "ok"}, status_code=200)

        # Chain: Django -> Bolt -> handler
        async def bolt_chain(req: Request) -> Response:
            return await bolt_mw(req, handler)

        response = await django_mw(request, bolt_chain)

        assert response.status_code == 200
        assert response.headers.get("X-Bolt-Tracked") == "yes"
        assert response.headers.get("X-Chain-1") == "yes"


# ═══════════════════════════════════════════════════════════════════════════
# Test Error Handling
# ═══════════════════════════════════════════════════════════════════════════


class ExceptionHandlingMiddleware:
    """Middleware that handles exceptions."""

    def __init__(self, get_response):
        self.get_response = get_response

    def process_exception(self, request, exception):
        if isinstance(exception, ValueError):
            return HttpResponse(
                f"Caught: {exception}",
                status=400
            )
        return None  # Let other exceptions propagate


class TestErrorHandling:
    """Tests for error handling in middleware chain."""

    @pytest.mark.asyncio
    async def test_handler_exception_propagates(self):
        """Test that unhandled handler exceptions propagate."""
        mw = DjangoMiddleware(HeaderMiddleware1)

        request = Request(method="GET", path="/test")

        async def handler(req: Request) -> Response:
            raise RuntimeError("Handler error")

        with pytest.raises(RuntimeError, match="Handler error"):
            await mw(request, handler)

    @pytest.mark.asyncio
    async def test_middleware_catches_exception(self):
        """Test that middleware can catch and handle exceptions."""
        mw = DjangoMiddleware(ExceptionHandlingMiddleware)

        request = Request(method="GET", path="/test")

        async def handler(req: Request) -> Response:
            raise ValueError("Invalid input")

        response = await mw(request, handler)

        assert response.status_code == 400
        assert b"Caught: Invalid input" in response.content


# ═══════════════════════════════════════════════════════════════════════════
# Test State Object
# ═══════════════════════════════════════════════════════════════════════════


class TestStateWithDjangoMiddleware:
    """Tests for State object usage with Django middleware."""

    @pytest.mark.asyncio
    async def test_state_preserved_through_middleware(self):
        """Test that Bolt request state is preserved through Django middleware."""
        django_mw = DjangoMiddleware(HeaderMiddleware1)

        request = Request(method="GET", path="/test")
        request.state["initial_value"] = "preserved"

        async def handler(req: Request) -> Response:
            assert req.state.get("initial_value") == "preserved"
            req.state["handler_value"] = "from_handler"
            return Response(content={"status": "ok"}, status_code=200)

        await django_mw(request, handler)

        # State should still be accessible after middleware
        assert request.state.get("initial_value") == "preserved"
        assert request.state.get("handler_value") == "from_handler"

    @pytest.mark.asyncio
    async def test_django_attrs_in_state(self):
        """Test that Django middleware attributes are stored in state."""
        mw = DjangoMiddleware(AttributeSettingMiddleware)

        request = Request(method="GET", path="/test")

        async def handler(req: Request) -> Response:
            # Django middleware should have set these in state
            assert "_django_tracking_id" in req._state
            return Response(content={"status": "ok"}, status_code=200)

        await mw(request, handler)

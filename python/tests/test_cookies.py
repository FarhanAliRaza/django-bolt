"""Tests for cookie functionality in django-bolt responses."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from django_bolt import JSON, Cookie, Response, StreamingResponse
from django_bolt.cookies import make_delete_cookie
from django_bolt.responses import HTML, PlainText, Redirect
from django_bolt.serialization import (
    response_meta_to_headers,
    serialize_html_response,
    serialize_plaintext_response,
    serialize_redirect_response,
)


class TestCookieSerialization:
    """Tests for Cookie.to_header_value() serialization."""

    def test_basic_cookie(self):
        """Test basic cookie with just name and value."""
        cookie = Cookie("session", "abc123")
        header = cookie.to_header_value()
        assert "session=abc123" in header
        assert "Path=/" in header
        assert "SameSite=Lax" in header

    def test_cookie_with_max_age(self):
        """Test cookie with max_age attribute."""
        cookie = Cookie("session", "abc123", max_age=3600)
        header = cookie.to_header_value()
        assert "Max-Age=3600" in header

    def test_cookie_with_expires_datetime(self):
        """Test cookie with expires as datetime object."""
        expires = datetime(2025, 12, 31, 23, 59, 59, tzinfo=UTC)
        cookie = Cookie("session", "abc123", expires=expires)
        header = cookie.to_header_value()
        assert "expires=Wed, 31 Dec 2025 23:59:59 GMT" in header

    def test_cookie_with_expires_string(self):
        """Test cookie with expires as string."""
        cookie = Cookie("session", "abc123", expires="Thu, 01 Jan 2026 00:00:00 GMT")
        header = cookie.to_header_value()
        assert "expires=Thu, 01 Jan 2026 00:00:00 GMT" in header

    def test_cookie_with_domain(self):
        """Test cookie with domain attribute."""
        cookie = Cookie("session", "abc123", domain=".example.com")
        header = cookie.to_header_value()
        assert "Domain=.example.com" in header

    def test_cookie_with_custom_path(self):
        """Test cookie with custom path."""
        cookie = Cookie("session", "abc123", path="/api")
        header = cookie.to_header_value()
        assert "Path=/api" in header

    def test_cookie_secure_flag(self):
        """Test cookie with secure flag."""
        cookie = Cookie("session", "abc123", secure=True)
        header = cookie.to_header_value()
        assert "Secure" in header

    def test_cookie_httponly_flag(self):
        """Test cookie with httponly flag."""
        cookie = Cookie("session", "abc123", httponly=True)
        header = cookie.to_header_value()
        assert "HttpOnly" in header

    def test_cookie_samesite_strict(self):
        """Test cookie with SameSite=Strict."""
        cookie = Cookie("session", "abc123", samesite="Strict")
        header = cookie.to_header_value()
        assert "SameSite=Strict" in header

    def test_cookie_samesite_none(self):
        """Test cookie with SameSite=None (requires Secure)."""
        cookie = Cookie("session", "abc123", samesite="None", secure=True)
        header = cookie.to_header_value()
        assert "SameSite=None" in header
        assert "Secure" in header

    def test_cookie_samesite_disabled(self):
        """Test cookie with SameSite disabled (False)."""
        cookie = Cookie("session", "abc123", samesite=False)
        header = cookie.to_header_value()
        assert "SameSite" not in header

    def test_cookie_all_attributes(self):
        """Test cookie with all attributes set."""
        cookie = Cookie(
            name="session",
            value="abc123",
            max_age=3600,
            expires="Thu, 01 Jan 2026 00:00:00 GMT",
            path="/api",
            domain=".example.com",
            secure=True,
            httponly=True,
            samesite="Strict",
        )
        header = cookie.to_header_value()
        assert "session=abc123" in header
        assert "Max-Age=3600" in header
        assert "expires=Thu, 01 Jan 2026 00:00:00 GMT" in header
        assert "Path=/api" in header
        assert "Domain=.example.com" in header
        assert "Secure" in header
        assert "HttpOnly" in header
        assert "SameSite=Strict" in header

    def test_cookie_value_escaping(self):
        """Test that special characters in cookie values are properly escaped."""
        cookie = Cookie("data", "hello world")
        header = cookie.to_header_value()
        # SimpleCookie should properly quote values with spaces
        assert "data=" in header


class TestMakeDeleteCookie:
    """Tests for make_delete_cookie helper function."""

    def test_delete_cookie_basic(self):
        """Test basic delete cookie creation."""
        cookie = make_delete_cookie("session")
        assert cookie.name == "session"
        assert cookie.value == ""
        assert cookie.max_age == 0
        assert cookie.expires == "Thu, 01 Jan 1970 00:00:00 GMT"
        assert cookie.path == "/"
        assert cookie.domain is None

    def test_delete_cookie_with_path(self):
        """Test delete cookie with custom path."""
        cookie = make_delete_cookie("session", path="/api")
        assert cookie.path == "/api"

    def test_delete_cookie_with_domain(self):
        """Test delete cookie with domain."""
        cookie = make_delete_cookie("session", domain=".example.com")
        assert cookie.domain == ".example.com"

    def test_delete_cookie_header_value(self):
        """Test delete cookie serializes correctly."""
        cookie = make_delete_cookie("session")
        header = cookie.to_header_value()
        assert "session=" in header
        assert "Max-Age=0" in header
        assert "expires=Thu, 01 Jan 1970 00:00:00 GMT" in header


class TestResponseSetCookie:
    """Tests for set_cookie() method on response classes."""

    def test_response_set_cookie_returns_self(self):
        """Test that set_cookie returns self for method chaining."""
        response = Response({"ok": True})
        result = response.set_cookie("session", "abc123")
        assert result is response

    def test_response_method_chaining(self):
        """Test multiple set_cookie calls can be chained."""
        response = Response({"ok": True}).set_cookie("session", "abc123").set_cookie("prefs", "dark")
        assert hasattr(response, "_cookies")
        assert len(response._cookies) == 2
        assert response._cookies[0].name == "session"
        assert response._cookies[1].name == "prefs"

    def test_json_set_cookie(self):
        """Test set_cookie on JSON response."""
        response = JSON({"user": "john"}).set_cookie("token", "xyz", httponly=True)
        assert len(response._cookies) == 1
        assert response._cookies[0].name == "token"
        assert response._cookies[0].httponly is True

    def test_plaintext_set_cookie(self):
        """Test set_cookie on PlainText response."""
        response = PlainText("Hello").set_cookie("visit", "1")
        assert len(response._cookies) == 1
        assert response._cookies[0].name == "visit"

    def test_html_set_cookie(self):
        """Test set_cookie on HTML response."""
        response = HTML("<h1>Hi</h1>").set_cookie("theme", "light")
        assert len(response._cookies) == 1
        assert response._cookies[0].name == "theme"

    def test_redirect_set_cookie(self):
        """Test set_cookie on Redirect response."""
        response = Redirect("/dashboard").set_cookie("logged_in", "true")
        assert len(response._cookies) == 1
        assert response._cookies[0].name == "logged_in"

    def test_streaming_response_set_cookie(self):
        """Test set_cookie on StreamingResponse."""

        def gen():
            yield b"chunk1"
            yield b"chunk2"

        response = StreamingResponse(gen()).set_cookie("stream_id", "12345")
        assert len(response._cookies) == 1
        assert response._cookies[0].name == "stream_id"

    def test_set_cookie_all_parameters(self):
        """Test set_cookie with all parameters."""
        response = Response({"ok": True}).set_cookie(
            name="session",
            value="abc123",
            max_age=3600,
            expires="Thu, 01 Jan 2026 00:00:00 GMT",
            path="/api",
            domain=".example.com",
            secure=True,
            httponly=True,
            samesite="Strict",
        )
        cookie = response._cookies[0]
        assert cookie.name == "session"
        assert cookie.value == "abc123"
        assert cookie.max_age == 3600
        assert cookie.expires == "Thu, 01 Jan 2026 00:00:00 GMT"
        assert cookie.path == "/api"
        assert cookie.domain == ".example.com"
        assert cookie.secure is True
        assert cookie.httponly is True
        assert cookie.samesite == "Strict"


class TestResponseDeleteCookie:
    """Tests for delete_cookie() method on response classes."""

    def test_response_delete_cookie_returns_self(self):
        """Test that delete_cookie returns self for method chaining."""
        response = Response({"ok": True})
        result = response.delete_cookie("session")
        assert result is response

    def test_delete_cookie_creates_expired_cookie(self):
        """Test delete_cookie creates a cookie that expires immediately."""
        response = Response({"ok": True}).delete_cookie("old_session")
        assert len(response._cookies) == 1
        cookie = response._cookies[0]
        assert cookie.name == "old_session"
        assert cookie.value == ""
        assert cookie.max_age == 0

    def test_delete_cookie_with_path(self):
        """Test delete_cookie with custom path."""
        response = Response({"ok": True}).delete_cookie("session", path="/api")
        cookie = response._cookies[0]
        assert cookie.path == "/api"

    def test_delete_cookie_with_domain(self):
        """Test delete_cookie with domain."""
        response = Response({"ok": True}).delete_cookie("session", domain=".example.com")
        cookie = response._cookies[0]
        assert cookie.domain == ".example.com"

    def test_combined_set_and_delete(self):
        """Test setting new cookies while deleting old ones."""
        response = Response({"ok": True}).set_cookie("new_session", "xyz").delete_cookie("old_session")
        assert len(response._cookies) == 2
        assert response._cookies[0].name == "new_session"
        assert response._cookies[0].value == "xyz"
        assert response._cookies[1].name == "old_session"
        assert response._cookies[1].max_age == 0


class TestSerializationWithCookies:
    """Tests for cookie header inclusion in serialized responses."""

    def test_plaintext_serialization_includes_cookies(self):
        """Test that PlainText serialization includes Set-Cookie headers."""
        response = PlainText("Hello").set_cookie("greeting", "sent")
        status, meta_or_headers, body = serialize_plaintext_response(response)
        # Convert ResponseMeta tuple to headers list if needed
        headers = response_meta_to_headers(meta_or_headers) if isinstance(meta_or_headers, tuple) else meta_or_headers
        # Check that set-cookie is in headers
        set_cookie_headers = [h for h in headers if h[0] == "set-cookie"]
        assert len(set_cookie_headers) == 1
        assert "greeting=sent" in set_cookie_headers[0][1]

    def test_html_serialization_includes_cookies(self):
        """Test that HTML serialization includes Set-Cookie headers."""
        response = HTML("<h1>Hi</h1>").set_cookie("page", "home")
        status, meta_or_headers, body = serialize_html_response(response)
        headers = response_meta_to_headers(meta_or_headers) if isinstance(meta_or_headers, tuple) else meta_or_headers
        set_cookie_headers = [h for h in headers if h[0] == "set-cookie"]
        assert len(set_cookie_headers) == 1
        assert "page=home" in set_cookie_headers[0][1]

    def test_redirect_serialization_includes_cookies(self):
        """Test that Redirect serialization includes Set-Cookie headers."""
        response = Redirect("/dashboard").set_cookie("redirected", "true")
        status, meta_or_headers, body = serialize_redirect_response(response)
        headers = response_meta_to_headers(meta_or_headers) if isinstance(meta_or_headers, tuple) else meta_or_headers
        set_cookie_headers = [h for h in headers if h[0] == "set-cookie"]
        assert len(set_cookie_headers) == 1
        assert "redirected=true" in set_cookie_headers[0][1]

    def test_multiple_cookies_in_serialization(self):
        """Test that multiple cookies create multiple Set-Cookie headers."""
        response = PlainText("OK").set_cookie("a", "1").set_cookie("b", "2").set_cookie("c", "3")
        status, meta_or_headers, body = serialize_plaintext_response(response)
        headers = response_meta_to_headers(meta_or_headers) if isinstance(meta_or_headers, tuple) else meta_or_headers
        set_cookie_headers = [h for h in headers if h[0] == "set-cookie"]
        assert len(set_cookie_headers) == 3


class TestCookieImport:
    """Tests for Cookie class import from django_bolt."""

    def test_cookie_import(self):
        """Test that Cookie can be imported from django_bolt."""
        from django_bolt import Cookie

        cookie = Cookie("test", "value")
        assert cookie.name == "test"
        assert cookie.value == "value"


@pytest.mark.asyncio
class TestAsyncSerializationWithCookies:
    """Tests for cookie header inclusion in async serialized responses."""

    async def test_json_async_serialization_includes_cookies(self):
        """Test that JSON async serialization includes Set-Cookie headers."""
        from django_bolt.serialization import serialize_json_response

        response = JSON({"ok": True}).set_cookie("api_token", "secret123", httponly=True)
        status, meta_or_headers, body = await serialize_json_response(response, None, None)
        headers = response_meta_to_headers(meta_or_headers) if isinstance(meta_or_headers, tuple) else meta_or_headers
        set_cookie_headers = [h for h in headers if h[0] == "set-cookie"]
        assert len(set_cookie_headers) == 1
        assert "api_token=secret123" in set_cookie_headers[0][1]
        assert "HttpOnly" in set_cookie_headers[0][1]

    async def test_response_async_serialization_includes_cookies(self):
        """Test that Response async serialization includes Set-Cookie headers."""
        from django_bolt.serialization import serialize_generic_response

        response = Response({"status": "logged_in"}).set_cookie("session", "xyz", secure=True)
        status, meta_or_headers, body = await serialize_generic_response(response, None, None)
        headers = response_meta_to_headers(meta_or_headers) if isinstance(meta_or_headers, tuple) else meta_or_headers
        set_cookie_headers = [h for h in headers if h[0] == "set-cookie"]
        assert len(set_cookie_headers) == 1
        assert "session=xyz" in set_cookie_headers[0][1]
        assert "Secure" in set_cookie_headers[0][1]

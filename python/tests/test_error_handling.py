"""Tests for Django-Bolt error handling system.

Every error response must follow the Litestar-style envelope:
``{status_code: int, detail: str, extra: list|dict|null}``
"""

import json
from unittest.mock import patch

import django
import msgspec
import pytest
from django.conf import settings  # noqa: PLC0415

from django_bolt.error_handlers import (
    _normalize_validation_error,
    format_error_response,
    generic_exception_handler,
    handle_exception,
    http_exception_handler,
    msgspec_validation_error_to_dict,
    request_validation_error_handler,
    response_validation_error_handler,
)
from django_bolt.exceptions import (
    BadRequest,
    Forbidden,
    HTTPException,
    InternalServerError,
    NotFound,
    RequestValidationError,
    ResponseValidationError,
    ServiceUnavailable,
    TooManyRequests,
    Unauthorized,
    UnprocessableEntity,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _assert_envelope(data: dict, expected_status: int) -> None:
    """Assert that *data* conforms to the {status_code, detail, extra} envelope."""
    assert "status_code" in data, "Response must include status_code"
    assert "detail" in data, "Response must include detail"
    assert "extra" in data, "Response must include extra (even if null)"
    assert data["status_code"] == expected_status


# ---------------------------------------------------------------------------
# Exception classes
# ---------------------------------------------------------------------------

class TestExceptions:
    """Test exception classes."""

    def test_http_exception_basic(self):
        """Test basic HTTPException."""
        exc = HTTPException(status_code=400, detail="Bad request")
        assert exc.status_code == 400
        assert exc.detail == "Bad request"
        assert exc.headers == {}
        assert exc.extra is None

    def test_http_exception_with_headers(self):
        """Test HTTPException with custom headers."""
        exc = HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Bearer"})
        assert exc.status_code == 401
        assert exc.headers == {"WWW-Authenticate": "Bearer"}

    def test_http_exception_with_extra(self):
        """Test HTTPException with extra data."""
        exc = HTTPException(status_code=422, detail="Validation failed", extra={"errors": ["field1", "field2"]})
        assert exc.extra == {"errors": ["field1", "field2"]}

    def test_http_exception_default_message(self):
        """Test HTTPException uses HTTP status phrase as default."""
        exc = HTTPException(status_code=404)
        assert exc.detail == "Not Found"

    def test_specialized_exceptions(self):
        """Test specialized exception classes."""
        assert BadRequest().status_code == 400
        assert Unauthorized().status_code == 401
        assert Forbidden().status_code == 403
        assert NotFound().status_code == 404
        assert UnprocessableEntity().status_code == 422
        assert TooManyRequests().status_code == 429
        assert InternalServerError().status_code == 500
        assert ServiceUnavailable().status_code == 503

    def test_exception_repr(self):
        """Test exception __repr__."""
        exc = NotFound(detail="User not found")
        assert "404" in repr(exc)
        assert "NotFound" in repr(exc)
        assert "User not found" in repr(exc)

    def test_validation_exception(self):
        """Test ValidationException."""
        errors = [{"loc": ["body", "name"], "msg": "Field required", "type": "missing"}]
        exc = RequestValidationError(errors)
        assert exc.errors() == errors

    def test_request_validation_error_with_body(self):
        """Test RequestValidationError stores body."""
        errors = [{"loc": ["body"], "msg": "Invalid", "type": "value_error"}]
        body = {"test": "data"}
        exc = RequestValidationError(errors, body=body)
        assert exc.body == body


# ---------------------------------------------------------------------------
# Standardized error envelope
# ---------------------------------------------------------------------------

class TestStandardizedErrorEnvelope:
    """Every error response MUST have {status_code, detail, extra}."""

    def test_format_error_response_envelope(self):
        """format_error_response always returns the 3-key envelope."""
        status, headers, body = format_error_response(status_code=404, detail="Not found")
        assert status == 404
        assert ("content-type", "application/json") in headers

        data = json.loads(body)
        _assert_envelope(data, 404)
        assert data["detail"] == "Not found"
        assert data["extra"] is None

    def test_format_error_response_with_extra(self):
        """Extra data is included in the envelope."""
        status, headers, body = format_error_response(
            status_code=400, detail="Validation failed", extra=[{"message": "bad", "key": "x", "source": "body"}]
        )
        data = json.loads(body)
        _assert_envelope(data, 400)
        assert data["detail"] == "Validation failed"
        assert isinstance(data["extra"], list)
        assert data["extra"][0]["message"] == "bad"

    def test_http_exception_handler_envelope(self):
        """HTTPException handler returns the standardized envelope."""
        exc = NotFound(detail="User not found")
        status, headers, body = http_exception_handler(exc)
        assert status == 404

        data = json.loads(body)
        _assert_envelope(data, 404)
        assert data["detail"] == "User not found"
        assert data["extra"] is None

    def test_http_exception_handler_with_extra_envelope(self):
        """HTTPException with extra data preserves it in the envelope."""
        exc = BadRequest(detail="Invalid input", extra={"field": "email", "value": "bad"})
        status, headers, body = http_exception_handler(exc)

        data = json.loads(body)
        _assert_envelope(data, 400)
        assert data["detail"] == "Invalid input"
        assert data["extra"]["field"] == "email"

    def test_http_exception_handler_with_headers(self):
        """Custom headers are preserved alongside the envelope."""
        exc = Unauthorized(detail="Auth required", headers={"WWW-Authenticate": "Bearer"})
        status, headers, body = http_exception_handler(exc)

        assert status == 401
        assert ("WWW-Authenticate", "Bearer") in headers
        data = json.loads(body)
        _assert_envelope(data, 401)

    def test_request_validation_error_returns_400(self):
        """Validation errors return 400 (like Litestar), not 422."""
        errors = [{"loc": ["body", "email"], "msg": "Invalid email", "type": "value_error"}]
        exc = RequestValidationError(errors)
        status, headers, body = request_validation_error_handler(exc)

        assert status == 400
        data = json.loads(body)
        _assert_envelope(data, 400)
        assert data["detail"] == "Validation failed"

    def test_request_validation_error_extra_format(self):
        """Validation extra uses Litestar-style {message, key, source}."""
        errors = [{"loc": ["body", "email"], "msg": "Invalid email", "type": "value_error"}]
        exc = RequestValidationError(errors)
        _, _, body = request_validation_error_handler(exc)

        data = json.loads(body)
        assert isinstance(data["extra"], list)
        assert len(data["extra"]) == 1
        err = data["extra"][0]
        assert err["message"] == "Invalid email"
        assert err["key"] == "email"
        assert err["source"] == "body"

    def test_response_validation_error_envelope(self):
        """Response validation errors return the standard envelope."""
        errors = [{"loc": ["response", "id"], "msg": "Field required", "type": "missing"}]
        exc = ResponseValidationError(errors)
        status, headers, body = response_validation_error_handler(exc)

        assert status == 500
        data = json.loads(body)
        _assert_envelope(data, 500)
        assert data["detail"] == "Response validation error"
        assert isinstance(data["extra"], list)
        assert data["extra"][0]["message"] == "Field required"
        assert data["extra"][0]["source"] == "response"

    def test_generic_exception_production_envelope(self):
        """500 in production mode uses the envelope with null extra."""
        exc = ValueError("Something went wrong")
        status, headers, body = generic_exception_handler(exc, debug=False)

        assert status == 500
        data = json.loads(body)
        _assert_envelope(data, 500)
        assert data["detail"] == "Internal Server Error"
        assert data["extra"] is None

    def test_handle_exception_generic_envelope(self):
        """handle_exception for generic errors returns the envelope."""
        exc = RuntimeError("Unexpected error")
        status, headers, body = handle_exception(exc, debug=False)

        assert status == 500
        data = json.loads(body)
        _assert_envelope(data, 500)
        assert data["detail"] == "Internal Server Error"

    def test_handle_exception_http_exception_envelope(self):
        """handle_exception for HTTPException returns the envelope."""
        exc = NotFound(detail="Resource not found")
        status, headers, body = handle_exception(exc)

        assert status == 404
        data = json.loads(body)
        _assert_envelope(data, 404)
        assert data["detail"] == "Resource not found"

    def test_handle_exception_validation_error_envelope(self):
        """handle_exception for RequestValidationError returns 400 with envelope."""
        errors = [{"loc": ["body"], "msg": "Invalid", "type": "value_error"}]
        exc = RequestValidationError(errors)
        status, headers, body = handle_exception(exc)

        assert status == 400
        data = json.loads(body)
        _assert_envelope(data, 400)
        assert data["detail"] == "Validation failed"
        assert isinstance(data["extra"], list)

    def test_handle_exception_msgspec_validation_error_envelope(self):
        """handle_exception for direct msgspec.ValidationError uses 400 envelope."""

        class TestStruct(msgspec.Struct):
            name: str
            age: int

        try:
            msgspec.json.decode(b'{"age": "invalid"}', type=TestStruct)
        except msgspec.ValidationError as exc:
            status, headers, body = handle_exception(exc, debug=False)

            assert status == 400
            data = json.loads(body)
            _assert_envelope(data, 400)
            assert data["detail"] == "Validation failed"
            assert isinstance(data["extra"], list)
            assert data["extra"][0]["source"] == "body"

    def test_file_not_found_exception_envelope(self):
        """FileNotFoundError returns 404 envelope."""
        exc = FileNotFoundError("image.png not found")
        status, _, body = handle_exception(exc, debug=False)

        assert status == 404
        data = json.loads(body)
        _assert_envelope(data, 404)

    def test_permission_error_exception_envelope(self):
        """PermissionError returns 403 envelope."""
        exc = PermissionError("Access denied")
        status, _, body = handle_exception(exc, debug=False)

        assert status == 403
        data = json.loads(body)
        _assert_envelope(data, 403)


# ---------------------------------------------------------------------------
# _normalize_validation_error
# ---------------------------------------------------------------------------

class TestNormalizeValidationError:
    """Test the loc/msg/type → message/key/source normalizer."""

    def test_converts_loc_msg_type(self):
        err = _normalize_validation_error({"loc": ["body", "email"], "msg": "required", "type": "missing"})
        assert err == {"message": "required", "key": "email", "source": "body"}

    def test_single_loc(self):
        err = _normalize_validation_error({"loc": ["body"], "msg": "bad json", "type": "json_invalid"})
        assert err == {"message": "bad json", "key": "", "source": "body"}

    def test_empty_loc(self):
        err = _normalize_validation_error({"msg": "unknown error", "type": "validation_error"})
        assert err == {"message": "unknown error", "key": "", "source": "body"}

    def test_already_normalized(self):
        err = {"message": "hello", "key": "x", "source": "query"}
        assert _normalize_validation_error(err) is err

    def test_query_source(self):
        err = _normalize_validation_error({"loc": ["query", "page"], "msg": "not int", "type": "type_error"})
        assert err == {"message": "not int", "key": "page", "source": "query"}


# ---------------------------------------------------------------------------
# Multiple validation errors
# ---------------------------------------------------------------------------

class TestMultipleValidationErrors:
    """Test handling multiple validation errors in a single response."""

    def test_multiple_errors_in_extra(self):
        errors = [
            {"loc": ["body", "name"], "msg": "Field required", "type": "missing"},
            {"loc": ["body", "email"], "msg": "Invalid format", "type": "value_error"},
            {"loc": ["body", "age"], "msg": "Must be positive", "type": "value_error"},
        ]
        exc = RequestValidationError(errors)
        status, headers, body = request_validation_error_handler(exc)

        data = json.loads(body)
        _assert_envelope(data, 400)
        assert len(data["extra"]) == 3
        keys = [e["key"] for e in data["extra"]]
        assert keys == ["name", "email", "age"]

    def test_frontend_mapping_pattern(self):
        """Verify the Litestar frontend mapping pattern works."""
        errors = [
            {"loc": ["body", "name"], "msg": "Field required", "type": "missing"},
            {"loc": ["body", "email"], "msg": "Invalid format", "type": "value_error"},
        ]
        exc = RequestValidationError(errors)
        _, _, body = request_validation_error_handler(exc)

        data = json.loads(body)
        # Simulate the Litestar frontend pattern:
        # for (const err of response.extra) { setFieldError(err.key, err.message); }
        field_errors = {}
        for err in data["extra"]:
            field_errors[err["key"]] = err["message"]

        assert field_errors == {"name": "Field required", "email": "Invalid format"}


# ---------------------------------------------------------------------------
# Debug mode
# ---------------------------------------------------------------------------

class TestDebugMode:
    """Test debug-mode error handling (HTML + JSON fallback)."""

    def test_generic_exception_handler_debug(self):
        """Test generic exception handler in debug mode returns HTML."""
        if not settings.configured:
            settings.configure(
                DEBUG=True,
                SECRET_KEY="test-secret-key",
                INSTALLED_APPS=[],
                ROOT_URLCONF="",
            )
            django.setup()

        exc = ValueError("Something went wrong")
        request_dict = {"method": "GET", "path": "/test", "headers": {"user-agent": "test"}, "query_params": {}}

        status, headers, body = generic_exception_handler(exc, debug=True, request=request_dict)

        assert status == 500
        headers_dict = dict(headers)
        assert headers_dict.get("content-type") == "text/html; charset=utf-8"
        html_content = body.decode("utf-8")
        assert "<!DOCTYPE html>" in html_content or "<html>" in html_content
        assert "ValueError" in html_content
        assert "Something went wrong" in html_content

    def test_generic_exception_handler_debug_without_request(self):
        """Test debug mode works without request."""
        if not settings.configured:
            settings.configure(
                DEBUG=True,
                SECRET_KEY="test-secret-key",
                INSTALLED_APPS=[],
                ROOT_URLCONF="",
            )
            django.setup()

        exc = RuntimeError("Error without request context")
        status, headers, body = generic_exception_handler(exc, debug=True, request=None)

        assert status == 500
        headers_dict = dict(headers)
        assert headers_dict.get("content-type") == "text/html; charset=utf-8"
        html_content = body.decode("utf-8")
        assert "RuntimeError" in html_content

    def test_generic_exception_handler_debug_fallback_to_json(self):
        """Test fallback to JSON envelope if HTML generation fails."""
        exc = ValueError("Test exception")

        with patch("django_bolt.error_handlers.ExceptionReporter", side_effect=Exception("HTML failed")):
            status, headers, body = generic_exception_handler(exc, debug=True, request=None)

        assert status == 500
        headers_dict = dict(headers)
        assert headers_dict.get("content-type") == "application/json"

        data = json.loads(body)
        _assert_envelope(data, 500)
        assert "ValueError" in data["detail"]
        assert "traceback" in data["extra"]
        assert "exception_type" in data["extra"]
        assert data["extra"]["exception_type"] == "ValueError"

    def test_generic_exception_handler_preserves_traceback(self):
        """Test that exception traceback is properly preserved."""

        def inner_function():
            raise ValueError("Inner error")

        def outer_function():
            inner_function()

        try:
            outer_function()
        except ValueError as exc:
            status, headers, body = generic_exception_handler(exc, debug=True, request=None)

            headers_dict = dict(headers)
            if headers_dict.get("content-type") == "text/html; charset=utf-8":
                html_content = body.decode("utf-8")
                assert "inner_function" in html_content or "outer_function" in html_content
            else:
                data = json.loads(body)
                _assert_envelope(data, 500)
                traceback_str = "".join(data["extra"]["traceback"])
                assert "inner_function" in traceback_str
                assert "outer_function" in traceback_str

    def test_handle_exception_with_request_parameter(self):
        """Test handle_exception passes request to generic_exception_handler."""
        if not settings.configured:
            settings.configure(
                DEBUG=True,
                SECRET_KEY="test-secret-key",
                INSTALLED_APPS=[],
                ROOT_URLCONF="",
            )
            django.setup()

        exc = ValueError("Test with request")
        request_dict = {
            "method": "POST",
            "path": "/api/users",
            "headers": {"content-type": "application/json"},
        }

        status, headers, body = handle_exception(exc, debug=True, request=request_dict)

        assert status == 500
        headers_dict = dict(headers)
        assert headers_dict.get("content-type") == "text/html; charset=utf-8"
        html_content = body.decode("utf-8")
        assert "ValueError" in html_content

    def test_handle_exception_respects_django_debug_setting(self):
        """Test that handle_exception uses Django DEBUG setting."""
        original_debug = settings.DEBUG
        settings.DEBUG = True

        try:
            exc = ValueError("Should use Django DEBUG")
            status, headers, _ = handle_exception(exc)

            headers_dict = dict(headers)
            assert headers_dict.get("content-type") == "text/html; charset=utf-8"
            assert status == 500
        finally:
            settings.DEBUG = original_debug

    def test_handle_exception_debug_overrides_django_setting(self):
        """Test that explicit debug=True overrides Django DEBUG=False."""
        exc = ValueError("Explicit debug override")
        status, _, _ = handle_exception(exc, debug=True)
        assert status == 500


# ---------------------------------------------------------------------------
# msgspec ValidationError conversion
# ---------------------------------------------------------------------------

class TestMsgspecConversion:
    def test_msgspec_validation_error_conversion(self):
        """Test msgspec ValidationError to dict conversion."""

        class TestStruct(msgspec.Struct):
            name: str
            age: int

        try:
            msgspec.json.decode(b'{"age": "invalid"}', type=TestStruct)
        except msgspec.ValidationError as e:
            errors = msgspec_validation_error_to_dict(e)
            assert isinstance(errors, list)
            assert len(errors) > 0
            assert "loc" in errors[0]
            assert "msg" in errors[0]
            assert "type" in errors[0]


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

class TestExceptionIntegration:
    """Integration tests for exception handling."""

    def test_exception_chain(self):
        """Test that exceptions can be chained properly."""
        try:
            raise ValueError("Original error")
        except ValueError as e:
            exc = InternalServerError(detail=str(e))
            assert exc.status_code == 500
            assert "Original error" in exc.detail

    def test_exception_context_preservation(self):
        """Test that exception context is preserved in the envelope."""
        exc = BadRequest(detail="Invalid input", extra={"field": "email", "value": "invalid@"})

        status, headers, body = http_exception_handler(exc)
        data = json.loads(body)

        _assert_envelope(data, 400)
        assert data["detail"] == "Invalid input"
        assert data["extra"]["field"] == "email"
        assert data["extra"]["value"] == "invalid@"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""Response serialization utilities."""
from __future__ import annotations

import mimetypes
from typing import TYPE_CHECKING, Any

import msgspec
from asgiref.sync import sync_to_async
from django.db.models import QuerySet
from django.http import HttpResponse as DjangoHttpResponse
from django.http import HttpResponseRedirect as DjangoHttpResponseRedirect

from . import _json
from .binding import coerce_to_response_type, coerce_to_response_type_async
from .responses import HTML, JSON, File, FileResponse, PlainText, Redirect, StreamingResponse
from .responses import Response as ResponseClass

if TYPE_CHECKING:
    from .typing import HandlerMetadata

ResponseTuple = tuple[int, list[tuple[str, str]], bytes]


def _convert_serializers(result: Any) -> Any:
    """
    Convert Serializer instances to dicts using dump().

    This ensures write_only fields are excluded and computed_field values are included.
    Uses a unique marker (__is_bolt_serializer__) to identify Serializers, avoiding
    false positives from duck typing with random objects that happen to have dump().

    Args:
        result: The handler result to potentially convert

    Returns:
        Converted result (dict/list if Serializer, original otherwise)
    """
    # Check for Serializer instance using unique marker (not duck typing)
    # __is_bolt_serializer__ is defined on the Serializer base class
    if getattr(result.__class__, "__is_bolt_serializer__", False) and hasattr(result, "dump"):
        return result.dump()

    # Handle list of Serializers
    if isinstance(result, list) and len(result) > 0:
        first = result[0]
        if getattr(first.__class__, "__is_bolt_serializer__", False) and hasattr(first, "dump"):
            return [item.dump() for item in result]

    return result


async def serialize_response(result: Any, meta: HandlerMetadata) -> ResponseTuple:
    """Serialize handler result to HTTP response."""
    # Extract status code once (used in multiple branches)
    status_code = meta.get("default_status_code", 200)

    # Handle 204 No Content - allow None return value
    if result is None and status_code == 204:
        return 204, [], b""

    # Fast path: dict/list are the most common response types (90%+ of handlers)
    # Check these first before any other processing
    if isinstance(result, dict):
        return await serialize_json_data(result, meta.get("response_type"), meta)
    if isinstance(result, list):
        # Only convert Serializers for lists (single Serializer handled by dict path)
        result = _convert_serializers(result)
        return await serialize_json_data(result, meta.get("response_type"), meta)

    response_tp = meta.get("response_type")

    # Convert Serializer instances to dicts (handles write_only, computed_field)
    # Only called for non-dict/list types now
    result = _convert_serializers(result)

    # After Serializer conversion, result may now be a dict/list - handle that case
    if isinstance(result, (dict, list)):
        return await serialize_json_data(result, response_tp, meta)

    # Check if result is already a raw response tuple (status, headers, body)
    # This is used by ASGI bridge and other low-level handlers
    if isinstance(result, tuple) and len(result) == 3:
        status, headers, body = result
        # Validate it looks like a response tuple
        if isinstance(status, int) and isinstance(headers, list) and isinstance(body, (bytes, bytearray)):
            return status, headers, bytes(body)

    # Handle different response types (ordered by frequency for performance)
    # Common: JSON wrapper
    if isinstance(result, JSON):
        return await serialize_json_response(result, response_tp, meta)
    # Common: Streaming responses
    if isinstance(result, StreamingResponse):
        return result
    # Less common: Other response types
    if isinstance(result, PlainText):
        return serialize_plaintext_response(result)
    if isinstance(result, HTML):
        return serialize_html_response(result)
    if isinstance(result, (bytes, bytearray)):
        return int(status_code), [("content-type", "application/octet-stream")], bytes(result)
    if isinstance(result, str):
        return int(status_code), [("content-type", "text/plain; charset=utf-8")], result.encode()
    if isinstance(result, Redirect):
        return serialize_redirect_response(result)
    if isinstance(result, File):
        return serialize_file_response(result)
    if isinstance(result, FileResponse):
        return serialize_file_streaming_response(result)
    if isinstance(result, ResponseClass):
        return await serialize_generic_response(result, response_tp, meta)
    if isinstance(result, msgspec.Struct):
        # Handle msgspec.Struct instances (e.g., PaginatedResponse)
        return await serialize_json_data(result, response_tp, meta)
    if isinstance(result, QuerySet):
        # Handle Django QuerySets - convert to list for JSON serialization
        # Use sync_to_async since QuerySet iteration is sync-only
        result_list = await sync_to_async(list, thread_sensitive=True)(result)
        return await serialize_json_data(result_list, response_tp, meta)
    if isinstance(result, DjangoHttpResponse):
        # Handle Django HttpResponse types (e.g., from @login_required decorator)
        return serialize_django_response(result)

    # Unknown type - raise clear error instead of failing in JSON serialization
    raise TypeError(
        f"Handler returned unsupported type {type(result).__name__!r}. "
        f"Return dict, list, or a Bolt response type (JSON, PlainText, HTML, Redirect, etc.)"
    )


def serialize_response_sync(result: Any, meta: HandlerMetadata) -> ResponseTuple:
    """Serialize handler result to HTTP response (sync version for sync handlers)."""
    # Extract status code once (used in multiple branches)
    status_code = meta.get("default_status_code", 200)

    # Handle 204 No Content - allow None return value
    if result is None and status_code == 204:
        return 204, [], b""

    # Fast path: dict/list are the most common response types (90%+ of handlers)
    # Check these first before any other processing
    if isinstance(result, dict):
        return serialize_json_data_sync(result, meta.get("response_type"), meta)
    if isinstance(result, list):
        # Only convert Serializers for lists (single Serializer handled by dict path)
        result = _convert_serializers(result)
        return serialize_json_data_sync(result, meta.get("response_type"), meta)

    response_tp = meta.get("response_type")

    # Convert Serializer instances to dicts (handles write_only, computed_field)
    # Only called for non-dict/list types now
    result = _convert_serializers(result)

    # After Serializer conversion, result may now be a dict/list - handle that case
    if isinstance(result, (dict, list)):
        return serialize_json_data_sync(result, response_tp, meta)

    # Check if result is already a raw response tuple (status, headers, body)
    if isinstance(result, tuple) and len(result) == 3:
        status, headers, body = result
        if isinstance(status, int) and isinstance(headers, list) and isinstance(body, (bytes, bytearray)):
            return status, headers, bytes(body)

    # Handle different response types (ordered by frequency for performance)
    # Common: JSON wrapper
    if isinstance(result, JSON):
        # Sync version of serialize_json_response
        has_custom_content_type = result.headers and any(k.lower() == "content-type" for k in result.headers)
        if has_custom_content_type:
            headers = [(k.lower(), v) for k, v in result.headers.items()]
        else:
            headers = [("content-type", "application/json")]
            if result.headers:
                headers.extend([(k.lower(), v) for k, v in result.headers.items()])

        if response_tp is not None:
            try:
                validated = coerce_to_response_type(result.data, response_tp, meta=meta)
                data_bytes = _json.encode(validated)
            except Exception as e:
                err = f"Response validation error: {e}"
                return 500, [("content-type", "text/plain; charset=utf-8")], err.encode()
        else:
            data_bytes = result.to_bytes()
        return int(result.status_code), headers, data_bytes
    # Less common: Other response types
    elif isinstance(result, PlainText):
        return serialize_plaintext_response(result)
    elif isinstance(result, HTML):
        return serialize_html_response(result)
    elif isinstance(result, (bytes, bytearray)):
        return int(status_code), [("content-type", "application/octet-stream")], bytes(result)
    elif isinstance(result, str):
        return int(status_code), [("content-type", "text/plain; charset=utf-8")], result.encode()
    elif isinstance(result, Redirect):
        return serialize_redirect_response(result)
    elif isinstance(result, File):
        return serialize_file_response(result)
    elif isinstance(result, FileResponse):
        return serialize_file_streaming_response(result)
    elif isinstance(result, ResponseClass):
        # Sync version of serialize_generic_response
        has_custom_content_type = result.headers and any(k.lower() == "content-type" for k in result.headers)
        if has_custom_content_type:
            headers = [(k.lower(), v) for k, v in result.headers.items()]
        else:
            headers = [("content-type", result.media_type)]
            if result.headers:
                headers.extend([(k.lower(), v) for k, v in result.headers.items()])

        if response_tp is not None:
            try:
                validated = coerce_to_response_type(result.content, response_tp, meta=meta)
                data_bytes = _json.encode(validated) if result.media_type == "application/json" else result.to_bytes()
            except Exception as e:
                err = f"Response validation error: {e}"
                return 500, [("content-type", "text/plain; charset=utf-8")], err.encode()
        else:
            data_bytes = result.to_bytes()
        return int(result.status_code), headers, data_bytes
    elif isinstance(result, msgspec.Struct):
        # Handle msgspec.Struct instances (e.g., PaginatedResponse)
        return serialize_json_data_sync(result, response_tp, meta)
    elif isinstance(result, QuerySet):
        # Handle Django QuerySets - convert to list for JSON serialization
        return serialize_json_data_sync(list(result), response_tp, meta)
    elif isinstance(result, DjangoHttpResponse):
        # Handle Django HttpResponse types (e.g., from @login_required decorator)
        return serialize_django_response(result)
    else:
        # Unknown type - raise clear error instead of failing in JSON serialization
        raise TypeError(
            f"Handler returned unsupported type {type(result).__name__!r}. "
            f"Return dict, list, or a Bolt response type (JSON, PlainText, HTML, Redirect, etc.)"
        )


async def serialize_generic_response(result: ResponseClass, response_tp: Any | None, meta: HandlerMetadata | None = None) -> ResponseTuple:
    """Serialize generic Response object with custom headers."""
    # Check if content-type is already provided in custom headers
    has_custom_content_type = result.headers and any(k.lower() == "content-type" for k in result.headers)

    if has_custom_content_type:
        # Use only custom headers (including custom content-type)
        headers = [(k.lower(), v) for k, v in result.headers.items()]
    else:
        # Use media_type as content-type and extend with custom headers
        headers = [("content-type", result.media_type)]
        if result.headers:
            headers.extend([(k.lower(), v) for k, v in result.headers.items()])

    if response_tp is not None:
        try:
            validated = await coerce_to_response_type_async(result.content, response_tp, meta=meta)
            data_bytes = _json.encode(validated) if result.media_type == "application/json" else result.to_bytes()
        except Exception as e:
            err = f"Response validation error: {e}"
            return 500, [("content-type", "text/plain; charset=utf-8")], err.encode()
    else:
        data_bytes = result.to_bytes()

    return int(result.status_code), headers, data_bytes


async def serialize_json_response(result: JSON, response_tp: Any | None, meta: HandlerMetadata | None = None) -> ResponseTuple:
    """Serialize JSON response object."""
    # Check if content-type is already provided in custom headers
    has_custom_content_type = result.headers and any(k.lower() == "content-type" for k in result.headers)

    if has_custom_content_type:
        # Use only custom headers (including custom content-type)
        headers = [(k.lower(), v) for k, v in result.headers.items()]
    else:
        # Use default content-type and extend with custom headers
        headers = [("content-type", "application/json")]
        if result.headers:
            headers.extend([(k.lower(), v) for k, v in result.headers.items()])

    if response_tp is not None:
        try:
            validated = await coerce_to_response_type_async(result.data, response_tp, meta=meta)
            data_bytes = _json.encode(validated)
        except Exception as e:
            err = f"Response validation error: {e}"
            return 500, [("content-type", "text/plain; charset=utf-8")], err.encode()
    else:
        data_bytes = result.to_bytes()

    return int(result.status_code), headers, data_bytes


def serialize_plaintext_response(result: PlainText) -> ResponseTuple:
    """Serialize plain text response."""
    # Check if content-type is already provided in custom headers
    has_custom_content_type = result.headers and any(k.lower() == "content-type" for k in result.headers)

    if has_custom_content_type:
        # Use only custom headers (including custom content-type)
        headers = [(k.lower(), v) for k, v in result.headers.items()]
    else:
        # Use default content-type and extend with custom headers
        headers = [("content-type", "text/plain; charset=utf-8")]
        if result.headers:
            headers.extend([(k.lower(), v) for k, v in result.headers.items()])

    return int(result.status_code), headers, result.to_bytes()


def serialize_html_response(result: HTML) -> ResponseTuple:
    """Serialize HTML response."""
    # Check if content-type is already provided in custom headers
    has_custom_content_type = result.headers and any(k.lower() == "content-type" for k in result.headers)

    if has_custom_content_type:
        # Use only custom headers (including custom content-type)
        headers = [(k.lower(), v) for k, v in result.headers.items()]
    else:
        # Use default content-type and extend with custom headers
        headers = [("content-type", "text/html; charset=utf-8")]
        if result.headers:
            headers.extend([(k.lower(), v) for k, v in result.headers.items()])

    return int(result.status_code), headers, result.to_bytes()


def serialize_redirect_response(result: Redirect) -> ResponseTuple:
    """Serialize redirect response."""
    headers = [("location", result.url)]
    if result.headers:
        headers.extend([(k.lower(), v) for k, v in result.headers.items()])
    return int(result.status_code), headers, b""


def serialize_django_response(result: DjangoHttpResponse) -> ResponseTuple:
    """Serialize Django HttpResponse types (e.g., from @login_required decorator).

    Only called in fallback path - no overhead for normal Bolt responses.
    """
    # Handle redirects specially (HttpResponseRedirect, HttpResponsePermanentRedirect)
    if isinstance(result, DjangoHttpResponseRedirect):
        headers = [("location", result.url)]
        # Copy other headers from Django response
        for key, value in result.items():
            if key.lower() != "location":
                headers.append((key.lower(), value))
        return result.status_code, headers, b""

    # Generic Django HttpResponse - extract content and headers
    headers = [(key.lower(), value) for key, value in result.items()]
    content = result.content if isinstance(result.content, bytes) else result.content.encode()
    return result.status_code, headers, content


def serialize_file_response(result: File) -> ResponseTuple:
    """Serialize file response."""
    data = result.read_bytes()
    ctype = result.media_type or mimetypes.guess_type(result.path)[0] or "application/octet-stream"
    headers = [("content-type", ctype)]

    if result.filename:
        headers.append(("content-disposition", f"attachment; filename=\"{result.filename}\""))
    if result.headers:
        headers.extend([(k.lower(), v) for k, v in result.headers.items()])

    return int(result.status_code), headers, data


def serialize_file_streaming_response(result: FileResponse) -> ResponseTuple:
    """Serialize file streaming response."""
    ctype = result.media_type or mimetypes.guess_type(result.path)[0] or "application/octet-stream"
    headers = [("x-bolt-file-path", result.path), ("content-type", ctype)]

    if result.filename:
        headers.append(("content-disposition", f"attachment; filename=\"{result.filename}\""))
    if result.headers:
        headers.extend([(k.lower(), v) for k, v in result.headers.items()])

    return int(result.status_code), headers, b""


async def serialize_json_data(result: Any, response_tp: Any | None, meta: HandlerMetadata) -> ResponseTuple:
    """Serialize dict/list/other data as JSON."""
    if response_tp is not None:
        try:
            validated = await coerce_to_response_type_async(result, response_tp, meta=meta)
            data = _json.encode(validated)
        except Exception as e:
            err = f"Response validation error: {e}"
            return 500, [("content-type", "text/plain; charset=utf-8")], err.encode()
    else:
        data = _json.encode(result)

    status = int(meta.get("default_status_code", 200))
    return status, [("content-type", "application/json")], data


def serialize_json_data_sync(result: Any, response_tp: Any | None, meta: HandlerMetadata) -> ResponseTuple:
    """Serialize dict/list/other data as JSON (sync version for sync handlers)."""
    if response_tp is not None:
        try:
            validated = coerce_to_response_type(result, response_tp, meta=meta)
            data = _json.encode(validated)
        except Exception as e:
            err = f"Response validation error: {e}"
            return 500, [("content-type", "text/plain; charset=utf-8")], err.encode()
    else:
        data = _json.encode(result)

    status = int(meta.get("default_status_code", 200))
    return status, [("content-type", "application/json")], data

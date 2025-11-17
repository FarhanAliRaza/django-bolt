"""Response serialization utilities."""
from __future__ import annotations
import mimetypes
import msgspec
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
from .responses import Response as ResponseClass, JSON, PlainText, HTML, Redirect, File, FileResponse, StreamingResponse
from .binding import coerce_to_response_type_async
from . import _json

if TYPE_CHECKING:
    from .typing import HandlerMetadata

ResponseTuple = Tuple[int, List[Tuple[str, str]], bytes]


async def serialize_response(result: Any, meta: HandlerMetadata) -> ResponseTuple:
    """Serialize handler result to HTTP response."""
    response_tp = meta.get("response_type")

    # Check if result is already a raw response tuple (status, headers, body)
    # This is used by ASGI bridge and other low-level handlers
    if isinstance(result, tuple) and len(result) == 3:
        status, headers, body = result
        # Validate it looks like a response tuple
        if isinstance(status, int) and isinstance(headers, list) and isinstance(body, (bytes, bytearray)):
            return status, headers, bytes(body)

    # Handle different response types (ordered by frequency for performance)
    # Most common: plain dict/list JSON responses
    if isinstance(result, (dict, list)):
        return await serialize_json_data(result, response_tp, meta)
    # Common: JSON wrapper
    elif isinstance(result, JSON):
        return await serialize_json_response(result, response_tp, meta)
    # Common: Streaming responses
    elif isinstance(result, StreamingResponse):
        return result
    # Less common: Other response types
    elif isinstance(result, PlainText):
        return serialize_plaintext_response(result)
    elif isinstance(result, HTML):
        return serialize_html_response(result)
    elif isinstance(result, (bytes, bytearray)):
        status = int(meta.get("default_status_code", 200))
        return status, [("content-type", "application/octet-stream")], bytes(result)
    elif isinstance(result, str):
        status = int(meta.get("default_status_code", 200))
        return status, [("content-type", "text/plain; charset=utf-8")], result.encode()
    elif isinstance(result, Redirect):
        return serialize_redirect_response(result)
    elif isinstance(result, File):
        return serialize_file_response(result)
    elif isinstance(result, FileResponse):
        return serialize_file_streaming_response(result)
    elif isinstance(result, ResponseClass):
        return await serialize_generic_response(result, response_tp, meta)
    else:
        # Fallback to msgspec encoding
        return await serialize_json_data(result, response_tp, meta)


def serialize_response_sync(result: Any, meta: HandlerMetadata) -> ResponseTuple:
    """Serialize handler result to HTTP response (sync version for sync handlers)."""
    from .binding import coerce_to_response_type

    response_tp = meta.get("response_type")

    # Check if result is already a raw response tuple (status, headers, body)
    if isinstance(result, tuple) and len(result) == 3:
        status, headers, body = result
        if isinstance(status, int) and isinstance(headers, list) and isinstance(body, (bytes, bytearray)):
            return status, headers, bytes(body)

    # Handle different response types (ordered by frequency for performance)
    # Most common: plain dict/list JSON responses
    if isinstance(result, (dict, list)):
        return serialize_json_data_sync(result, response_tp, meta)
    # Common: JSON wrapper
    elif isinstance(result, JSON):
        # Sync version of serialize_json_response
        has_custom_content_type = result.headers and any(k.lower() == "content-type" for k in result.headers.keys())
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
        status = int(meta.get("default_status_code", 200))
        return status, [("content-type", "application/octet-stream")], bytes(result)
    elif isinstance(result, str):
        status = int(meta.get("default_status_code", 200))
        return status, [("content-type", "text/plain; charset=utf-8")], result.encode()
    elif isinstance(result, Redirect):
        return serialize_redirect_response(result)
    elif isinstance(result, File):
        return serialize_file_response(result)
    elif isinstance(result, FileResponse):
        return serialize_file_streaming_response(result)
    elif isinstance(result, ResponseClass):
        # Sync version of serialize_generic_response
        has_custom_content_type = result.headers and any(k.lower() == "content-type" for k in result.headers.keys())
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
    else:
        # Fallback to msgspec encoding
        return serialize_json_data_sync(result, response_tp, meta)


async def serialize_generic_response(result: ResponseClass, response_tp: Optional[Any], meta: "Optional[HandlerMetadata]" = None) -> ResponseTuple:
    """Serialize generic Response object with custom headers."""
    # Check if content-type is already provided in custom headers
    has_custom_content_type = result.headers and any(k.lower() == "content-type" for k in result.headers.keys())

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


async def serialize_json_response(result: JSON, response_tp: Optional[Any], meta: "Optional[HandlerMetadata]" = None) -> ResponseTuple:
    """Serialize JSON response object."""
    # Check if content-type is already provided in custom headers
    has_custom_content_type = result.headers and any(k.lower() == "content-type" for k in result.headers.keys())

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
    has_custom_content_type = result.headers and any(k.lower() == "content-type" for k in result.headers.keys())

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
    has_custom_content_type = result.headers and any(k.lower() == "content-type" for k in result.headers.keys())

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


async def serialize_json_data(result: Any, response_tp: Optional[Any], meta: "HandlerMetadata") -> ResponseTuple:
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


def serialize_json_data_sync(result: Any, response_tp: Optional[Any], meta: "HandlerMetadata") -> ResponseTuple:
    """Serialize dict/list/other data as JSON (sync version for sync handlers)."""
    from .binding import coerce_to_response_type

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

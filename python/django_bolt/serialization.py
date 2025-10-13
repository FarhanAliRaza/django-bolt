"""Response serialization utilities."""
import mimetypes
import msgspec
from typing import Any, Dict, List, Optional, Tuple
from .responses import JSON, PlainText, HTML, Redirect, File, FileResponse, StreamingResponse
from .binding import coerce_to_response_type_async

Response = Tuple[int, List[Tuple[str, str]], bytes]


async def serialize_response(result: Any, meta: Dict[str, Any]) -> Response:
    """Serialize handler result to HTTP response."""
    response_tp = meta.get("response_type")

    # Check if result is already a raw response tuple (status, headers, body)
    # This is used by ASGI bridge and other low-level handlers
    if isinstance(result, tuple) and len(result) == 3:
        status, headers, body = result
        # Validate it looks like a response tuple
        if isinstance(status, int) and isinstance(headers, list) and isinstance(body, (bytes, bytearray)):
            return status, headers, bytes(body)

    # Handle different response types
    if isinstance(result, JSON):
        return await serialize_json_response(result, response_tp)
    elif isinstance(result, PlainText):
        return serialize_plaintext_response(result)
    elif isinstance(result, HTML):
        return serialize_html_response(result)
    elif isinstance(result, Redirect):
        return serialize_redirect_response(result)
    elif isinstance(result, File):
        return serialize_file_response(result)
    elif isinstance(result, FileResponse):
        return serialize_file_streaming_response(result)
    elif isinstance(result, StreamingResponse):
        return result
    elif isinstance(result, (bytes, bytearray)):
        status = int(meta.get("default_status_code", 200))
        return status, [("content-type", "application/octet-stream")], bytes(result)
    elif isinstance(result, str):
        status = int(meta.get("default_status_code", 200))
        return status, [("content-type", "text/plain; charset=utf-8")], result.encode()
    elif isinstance(result, (dict, list)):
        return await serialize_json_data(result, response_tp, meta)
    else:
        # Fallback to msgspec encoding
        return await serialize_json_data(result, response_tp, meta)


async def serialize_json_response(result: JSON, response_tp: Optional[Any]) -> Response:
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
            validated = await coerce_to_response_type_async(result.data, response_tp)
            data_bytes = msgspec.json.encode(validated)
        except Exception as e:
            err = f"Response validation error: {e}"
            return 500, [("content-type", "text/plain; charset=utf-8")], err.encode()
    else:
        data_bytes = result.to_bytes()

    return int(result.status_code), headers, data_bytes


def serialize_plaintext_response(result: PlainText) -> Response:
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


def serialize_html_response(result: HTML) -> Response:
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


def serialize_redirect_response(result: Redirect) -> Response:
    """Serialize redirect response."""
    headers = [("location", result.url)]
    if result.headers:
        headers.extend([(k.lower(), v) for k, v in result.headers.items()])
    return int(result.status_code), headers, b""


def serialize_file_response(result: File) -> Response:
    """Serialize file response."""
    data = result.read_bytes()
    ctype = result.media_type or mimetypes.guess_type(result.path)[0] or "application/octet-stream"
    headers = [("content-type", ctype)]

    if result.filename:
        headers.append(("content-disposition", f"attachment; filename=\"{result.filename}\""))
    if result.headers:
        headers.extend([(k.lower(), v) for k, v in result.headers.items()])

    return int(result.status_code), headers, data


def serialize_file_streaming_response(result: FileResponse) -> Response:
    """Serialize file streaming response."""
    ctype = result.media_type or mimetypes.guess_type(result.path)[0] or "application/octet-stream"
    headers = [("x-bolt-file-path", result.path), ("content-type", ctype)]

    if result.filename:
        headers.append(("content-disposition", f"attachment; filename=\"{result.filename}\""))
    if result.headers:
        headers.extend([(k.lower(), v) for k, v in result.headers.items()])

    return int(result.status_code), headers, b""


async def serialize_json_data(result: Any, response_tp: Optional[Any], meta: Dict[str, Any]) -> Response:
    """Serialize dict/list/other data as JSON."""
    if response_tp is not None:
        try:
            validated = await coerce_to_response_type_async(result, response_tp)
            data = msgspec.json.encode(validated)
        except Exception as e:
            err = f"Response validation error: {e}"
            return 500, [("content-type", "text/plain; charset=utf-8")], err.encode()
    else:
        data = msgspec.json.encode(result)

    status = int(meta.get("default_status_code", 200))
    return status, [("content-type", "application/json")], data

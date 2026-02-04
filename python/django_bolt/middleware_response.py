"""
MiddlewareResponse class for middleware compatibility.

This is in a separate module to avoid circular imports:
- api.py imports from middleware
- middleware imports from django_adapter
- django_adapter needs MiddlewareResponse
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .responses import StreamingResponse

# Response tuple body can be bytes (normal) or StreamingResponse (for streaming)
# Rust handler.rs detects StreamingResponse in the body and handles streaming
Response = tuple[int, list[tuple[str, str]], "bytes | StreamingResponse"]

# Content-type mapping for response types (used when converting ResponseMeta)
_CONTENT_TYPE_MAP = {
    "json": "application/json",
    "html": "text/html; charset=utf-8",
    "plaintext": "text/plain; charset=utf-8",
    "octetstream": "application/octet-stream",
}


class MiddlewareResponse:
    """
    Response wrapper for middleware compatibility.

    Middleware expects response.status_code and response.headers attributes,
    but our internal response format is a tuple (status_code, headers, body).
    This class bridges the gap, allowing middleware to modify responses.

    Note: set_cookies is a separate list to support multiple Set-Cookie headers.
    HTTP allows multiple Set-Cookie headers, but dict can't have duplicate keys.
    """

    __slots__ = ("status_code", "headers", "body", "set_cookies")

    def __init__(
        self,
        status_code: int,
        headers: dict[str, str],
        body: bytes | StreamingResponse,
        set_cookies: list[str] | None = None,
    ):
        self.status_code = status_code
        self.headers = headers  # Dict for easy middleware modification
        self.body = body
        self.set_cookies = set_cookies or []  # List for multiple Set-Cookie headers

    @classmethod
    def from_tuple(cls, response: Response) -> MiddlewareResponse:
        """Create from internal tuple format.

        Handles both legacy format (status, headers_list, body) and new
        ResponseMeta format (status, meta_tuple, body).
        """
        status_code, headers_or_meta, body = response

        # Check if this is the new ResponseMeta format (tuple) vs legacy format (list)
        if isinstance(headers_or_meta, tuple) and len(headers_or_meta) == 4:
            # New ResponseMeta format: (response_type, custom_ct, custom_headers, cookies)
            response_type, custom_ct, custom_headers, cookies = headers_or_meta
            headers: dict[str, str] = {}
            set_cookies: list[str] = []

            # Add content-type
            if custom_ct:
                headers["content-type"] = custom_ct
            elif response_type in _CONTENT_TYPE_MAP:
                headers["content-type"] = _CONTENT_TYPE_MAP[response_type]

            # Add custom headers
            if custom_headers:
                for k, v in custom_headers:
                    headers[k.lower()] = v

            # Convert cookie tuples to Set-Cookie header values
            if cookies:
                for cookie_tuple in cookies:
                    name, value, path, max_age, expires, domain, secure, httponly, samesite = cookie_tuple
                    parts = [f"{name}={value}", f"Path={path}"]
                    if max_age is not None:
                        parts.append(f"Max-Age={max_age}")
                    if expires:
                        parts.append(f"Expires={expires}")
                    if domain:
                        parts.append(f"Domain={domain}")
                    if secure:
                        parts.append("Secure")
                    if httponly:
                        parts.append("HttpOnly")
                    if samesite:
                        parts.append(f"SameSite={samesite}")
                    set_cookies.append("; ".join(parts))

            return cls(status_code, headers, body, set_cookies)
        else:
            # Legacy format: list of (header_name, header_value) tuples
            headers = dict(headers_or_meta)
            return cls(status_code, headers, body)

    def to_tuple(self) -> Response:
        """Convert back to internal tuple format."""
        headers_list = [(k, v) for k, v in self.headers.items()]
        # Append Set-Cookie headers from dedicated list (supports multiple cookies)
        if self.set_cookies:
            headers_list.extend([("Set-Cookie", cookie) for cookie in self.set_cookies])
        return (self.status_code, headers_list, self.body)

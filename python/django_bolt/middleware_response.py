"""
MiddlewareResponse class for middleware compatibility.

This is in a separate module to avoid circular imports:
- api.py imports from middleware
- middleware imports from django_adapter
- django_adapter needs MiddlewareResponse
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .responses import StreamingResponse

# Response tuple body can be bytes (normal) or StreamingResponse (for streaming)
# Rust handler.rs detects StreamingResponse in the body and handles streaming
Response = tuple[int, list[tuple[str, str]], "bytes | StreamingResponse"]

# Raw cookie tuple type (matches serialization.py CookieTuple)
CookieTuple = tuple[str, str, str, int | None, str | None, str | None, bool, bool, str | None]

# ResponseMeta tuple type for Rust-side header building
ResponseMetaTuple = tuple[
    str,  # response_type
    str | None,  # custom_content_type
    list[tuple[str, str]] | None,  # custom_headers
    list[CookieTuple] | None,  # cookies (raw tuples, NOT serialized)
]


class MiddlewareResponse:
    """
    Response wrapper for middleware compatibility.

    Middleware expects response.status_code and response.headers attributes,
    but our internal response format is a tuple (status_code, headers/meta, body).
    This class bridges the gap, allowing middleware to modify responses.

    IMPORTANT: Cookie serialization happens in Rust, not Python.
    This class stores raw cookie tuples and returns ResponseMeta format
    so Rust can handle all header/cookie serialization.
    """

    __slots__ = ("status_code", "headers", "body", "_response_type", "_raw_cookies")

    def __init__(
        self,
        status_code: int,
        headers: dict[str, str],
        body: bytes | StreamingResponse,
        response_type: str = "json",
        raw_cookies: list[CookieTuple] | None = None,
    ):
        self.status_code = status_code
        self.headers = headers  # Dict for easy middleware modification
        self.body = body
        self._response_type = response_type  # Preserve for Rust content-type
        self._raw_cookies = raw_cookies or []  # Raw tuples, Rust serializes

    @classmethod
    def from_tuple(cls, response: Response) -> MiddlewareResponse:
        """Create from internal tuple format.

        Handles both legacy format (status, headers_list, body) and new
        ResponseMeta format (status, meta_tuple, body).

        IMPORTANT: Does NOT serialize cookies - preserves raw tuples for Rust.
        """
        status_code, headers_or_meta, body = response

        # Check if this is the new ResponseMeta format (tuple) vs legacy format (list)
        if isinstance(headers_or_meta, tuple) and len(headers_or_meta) == 4:
            # New ResponseMeta format: (response_type, custom_ct, custom_headers, cookies)
            response_type, custom_ct, custom_headers, cookies = headers_or_meta
            headers: dict[str, str] = {}

            # Add content-type to headers dict for middleware access
            if custom_ct:
                headers["content-type"] = custom_ct

            # Add custom headers for middleware access
            if custom_headers:
                for k, v in custom_headers:
                    headers[k.lower()] = v

            # Store raw cookie tuples - Rust will serialize them
            return cls(status_code, headers, body, response_type, cookies)
        else:
            # Legacy format: list of (header_name, header_value) tuples
            headers = dict(headers_or_meta)
            return cls(status_code, headers, body)

    def to_tuple(self) -> Any:
        """Convert back to internal tuple format.

        Returns ResponseMeta format so Rust handles all header/cookie serialization.
        """
        # Extract content-type if middleware set it
        custom_ct = self.headers.pop("content-type", None)

        # Build custom headers list (excluding content-type which is handled separately)
        custom_headers: list[tuple[str, str]] | None = None
        if self.headers:
            custom_headers = [(k, v) for k, v in self.headers.items()]

        # Return ResponseMeta format - Rust serializes headers and cookies
        meta: ResponseMetaTuple = (
            self._response_type,
            custom_ct,
            custom_headers,
            self._raw_cookies if self._raw_cookies else None,
        )
        return (self.status_code, meta, self.body)

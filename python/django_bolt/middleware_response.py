"""
MiddlewareResponse class for middleware compatibility.

This is in a separate module to avoid circular imports:
- api.py imports from middleware
- middleware imports from django_adapter
- django_adapter needs MiddlewareResponse
"""
from __future__ import annotations

Response = tuple[int, list[tuple[str, str]], bytes]


class MiddlewareResponse:
    """
    Response wrapper for middleware compatibility.

    Middleware expects response.status_code and response.headers attributes,
    but our internal response format is a tuple (status_code, headers, body).
    This class bridges the gap, allowing middleware to modify responses.
    """
    __slots__ = ('status_code', 'headers', 'body')

    def __init__(self, status_code: int, headers: dict[str, str], body: bytes):
        self.status_code = status_code
        self.headers = headers  # Dict for easy middleware modification
        self.body = body

    @classmethod
    def from_tuple(cls, response: Response) -> MiddlewareResponse:
        """Create from internal tuple format."""
        status_code, headers_list, body = response
        # Convert list of tuples to dict for middleware
        headers = dict(headers_list)
        return cls(status_code, headers, body)

    def to_tuple(self) -> Response:
        """Convert back to internal tuple format."""
        headers_list = [(k, v) for k, v in self.headers.items()]
        return (self.status_code, headers_list, self.body)

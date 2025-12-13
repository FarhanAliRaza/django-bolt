"""
Request Protocol for Django-Bolt.

Defines the interface for request objects. At runtime, handlers receive
PyRequest from Rust (src/request.rs). This Protocol provides type hints
and IDE autocomplete.
"""
from typing import (
    Any,
    Protocol,
    runtime_checkable,
)


@runtime_checkable
class Request(Protocol):
    """
    Request protocol - the interface for request objects.

    At runtime, handlers receive PyRequest from Rust (src/request.rs).
    This Protocol defines the interface for type checking and IDE support.

    Examples:
        @api.get("/profile")
        async def profile(request: Request) -> dict:
            return {"user": request.user.username}
    """

    @property
    def method(self) -> str:
        """HTTP method (GET, POST, etc.)"""
        ...

    @property
    def path(self) -> str:
        """Request path"""
        ...

    @property
    def body(self) -> bytes:
        """Request body as bytes"""
        ...

    @property
    def headers(self) -> dict[str, str]:
        """Request headers"""
        ...

    @property
    def cookies(self) -> dict[str, str]:
        """Request cookies"""
        ...

    @property
    def query(self) -> dict[str, str]:
        """Query parameters"""
        ...

    @property
    def user(self) -> Any:
        """Authenticated user (set by middleware)"""
        ...

    @user.setter
    def user(self, value: Any) -> None:
        ...

    @property
    def context(self) -> Any:
        """Auth context (JWT claims, API key info, etc.)"""
        ...

    @property
    def state(self) -> dict[str, Any]:
        """Middleware state dict"""
        ...

    @property
    def auser(self) -> Any:
        """Async user getter (Django-style)"""
        ...


__all__ = [
    "Request",

]

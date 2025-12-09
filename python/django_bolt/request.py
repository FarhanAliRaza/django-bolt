"""
Request Protocol for Django-Bolt.

Defines the interface for request objects. At runtime, handlers receive
PyRequest from Rust (src/request.rs). This Protocol provides type hints
and IDE autocomplete.
"""
from collections.abc import Iterator
from typing import (
    Any,
    Generic,
    Protocol,
    TypeVar,
    runtime_checkable,
)

# Type variables for generic typing
UserT = TypeVar("UserT")
AuthT = TypeVar("AuthT")
StateT = TypeVar("StateT", bound=dict[str, Any])


class State(Generic[StateT]):
    """
    Type-safe state container with attribute and dict access.

    Wraps a dictionary to provide both `state.key` and `state["key"]` access.
    """

    __slots__ = ("_data",)

    def __init__(self, data: dict[str, Any]) -> None:
        object.__setattr__(self, "_data", data)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def pop(self, key: str, *args) -> Any:
        return self._data.pop(key, *args)

    def update(self, other: dict[str, Any] = None, **kwargs) -> None:
        if other:
            self._data.update(other)
        if kwargs:
            self._data.update(kwargs)

    def setdefault(self, key: str, default: Any = None) -> Any:
        return self._data.setdefault(key, default)

    def clear(self) -> None:
        self._data.clear()

    def __getattr__(self, key: str) -> Any:
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            )

    def __setattr__(self, key: str, value: Any) -> None:
        if key == "_data":
            object.__setattr__(self, key, value)
        else:
            self._data[key] = value

    def __delattr__(self, key: str) -> None:
        try:
            del self._data[key]
        except KeyError:
            raise AttributeError(key)

    def __repr__(self) -> str:
        return f"State({self._data!r})"

    def __bool__(self) -> bool:
        return bool(self._data)


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


# Type alias for call_next function used in middleware
CallNext = Any  # Callable[[Request], Awaitable[Response]]


__all__ = [
    "Request",
    "State",
    "UserT",
    "AuthT",
    "StateT",
    "CallNext",
]

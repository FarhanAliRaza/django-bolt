from __future__ import annotations

from collections.abc import Callable
from typing import Any


class APIRouter:
    def __init__(
        self,
        prefix: str = "",
        tags: list[str] | None = None,
        dependencies: list[Any] | None = None,
    ):
        self.prefix = prefix.rstrip("/")
        self.tags = tags or []
        self.dependencies = dependencies or []
        self._routes: list[tuple[str, str, Callable, dict[str, Any]]] = []

    def _add(self, method: str, path: str, handler: Callable, **meta: Any) -> None:
        full = (self.prefix + path) if self.prefix else path
        self._routes.append((method, full, handler, meta))

    def get(self, path: str, **kwargs: Any):
        def dec(fn: Callable):
            self._add("GET", path, fn, **kwargs)
            return fn

        return dec

    def post(self, path: str, **kwargs: Any):
        def dec(fn: Callable):
            self._add("POST", path, fn, **kwargs)
            return fn

        return dec

    def put(self, path: str, **kwargs: Any):
        def dec(fn: Callable):
            self._add("PUT", path, fn, **kwargs)
            return fn

        return dec

    def patch(self, path: str, **kwargs: Any):
        def dec(fn: Callable):
            self._add("PATCH", path, fn, **kwargs)
            return fn

        return dec

    def delete(self, path: str, **kwargs: Any):
        def dec(fn: Callable):
            self._add("DELETE", path, fn, **kwargs)
            return fn

        return dec

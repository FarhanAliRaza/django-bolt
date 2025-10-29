"""
Public, editor-focused typing helpers for Django-Bolt.

These are intentionally minimal runtime types that provide better static
type information in editors and CI when used by generated .pyi stubs.

At runtime, Django's own QuerySet/Manager classes are used. These classes
exist only to give type checkers a stable, importable symbol to reference
from generated stubs (e.g., TypedQuerySet[User]).
"""
from __future__ import annotations

from typing import Any, Generic, Iterable, Iterator, Optional, TypeVar, overload


ModelT = TypeVar("ModelT")


class TypedQuerySet(Generic[ModelT]):
    """
    A typing-only stand-in for Django QuerySet with a model type parameter.

    Generated stubs will create per-model subclasses (e.g., UserQuerySet)
    that inherit from this to provide model-specific, typed method signatures.
    """

    # Iteration yields model instances
    def __iter__(self) -> Iterator[ModelT]:  # pragma: no cover - typing surface only
        ...

    # Indexing and slicing
    @overload
    def __getitem__(self, __index: int) -> ModelT:  # pragma: no cover - typing surface only
        ...

    @overload
    def __getitem__(self, __s: slice) -> list[ModelT]:  # pragma: no cover - typing surface only
        ...

    def __getitem__(self, __key: Any) -> Any:  # pragma: no cover - typing surface only
        ...

    def __len__(self) -> int:  # pragma: no cover - typing surface only
        ...

    # Basic operations
    def all(self) -> "TypedQuerySet[ModelT]":  # pragma: no cover - typing surface only
        ...

    def first(self) -> Optional[ModelT]:  # pragma: no cover - typing surface only
        ...

    def last(self) -> Optional[ModelT]:  # pragma: no cover - typing surface only
        ...

    def get(self, **kwargs: Any) -> ModelT:  # pragma: no cover - typing surface only
        ...

    def filter(self, **kwargs: Any) -> "TypedQuerySet[ModelT]":  # pragma: no cover - typing surface only
        ...

    def exclude(self, **kwargs: Any) -> "TypedQuerySet[ModelT]":  # pragma: no cover - typing surface only
        ...

    def count(self) -> int:  # pragma: no cover - typing surface only
        ...

    def exists(self) -> bool:  # pragma: no cover - typing surface only
        ...

    def create(self, **kwargs: Any) -> ModelT:  # pragma: no cover - typing surface only
        ...

    def update(self, **kwargs: Any) -> int:  # pragma: no cover - typing surface only
        ...

    def delete(self) -> tuple[int, dict[str, int]]:  # pragma: no cover - typing surface only
        ...

    def order_by(self, *fields: str) -> "TypedQuerySet[ModelT]":  # pragma: no cover - typing surface only
        ...

    def distinct(self, *fields: str) -> "TypedQuerySet[ModelT]":  # pragma: no cover - typing surface only
        ...

    def select_related(self, *fields: str) -> "TypedQuerySet[ModelT]":  # pragma: no cover - typing surface only
        ...

    def prefetch_related(self, *fields: str) -> "TypedQuerySet[ModelT]":  # pragma: no cover - typing surface only
        ...

    # Convenience collection conversions
    def to_list(self) -> list[ModelT]:  # pragma: no cover - typing surface only
        ...

    # Async methods (Django 4.1+)
    def __aiter__(self) -> Iterator[ModelT]:  # pragma: no cover - typing surface only
        ...

    async def aget(self, **kwargs: Any) -> ModelT:  # pragma: no cover - typing surface only
        ...

    async def acreate(self, **kwargs: Any) -> ModelT:  # pragma: no cover - typing surface only
        ...

    async def aupdate(self, **kwargs: Any) -> int:  # pragma: no cover - typing surface only
        ...

    async def adelete(self) -> tuple[int, dict[str, int]]:  # pragma: no cover - typing surface only
        ...

    async def afirst(self) -> Optional[ModelT]:  # pragma: no cover - typing surface only
        ...

    async def alast(self) -> Optional[ModelT]:  # pragma: no cover - typing surface only
        ...

    async def acount(self) -> int:  # pragma: no cover - typing surface only
        ...

    async def aexists(self) -> bool:  # pragma: no cover - typing surface only
        ...

    def aiterator(self) -> Iterator[ModelT]:  # pragma: no cover - typing surface only
        ...


class TypedManager(Generic[ModelT]):
    """
    A typing-only stand-in for Django Manager with a model type parameter.

    Generated stubs will create per-model manager subclasses that return
    model-specific typed querysets and instances.
    """

    def get_queryset(self) -> TypedQuerySet[ModelT]:  # pragma: no cover - typing surface only
        ...

    def all(self) -> list[ModelT]:  # pragma: no cover - typing surface only
        ...

    def first(self) -> Optional[ModelT]:  # pragma: no cover - typing surface only
        ...

    def last(self) -> Optional[ModelT]:  # pragma: no cover - typing surface only
        ...

    def get(self, **kwargs: Any) -> ModelT:  # pragma: no cover - typing surface only
        ...

    def filter(self, **kwargs: Any) -> TypedQuerySet[ModelT]:  # pragma: no cover - typing surface only
        ...

    def create(self, **kwargs: Any) -> ModelT:  # pragma: no cover - typing surface only
        ...

    # Async methods (Django 4.1+)
    async def aget(self, **kwargs: Any) -> ModelT:  # pragma: no cover - typing surface only
        ...

    async def acreate(self, **kwargs: Any) -> ModelT:  # pragma: no cover - typing surface only
        ...

    async def aget_or_create(self, **kwargs: Any) -> tuple[ModelT, bool]:  # pragma: no cover - typing surface only
        ...

    async def aupdate_or_create(self, **kwargs: Any) -> tuple[ModelT, bool]:  # pragma: no cover - typing surface only
        ...

    async def abulk_create(self, objs: list[ModelT], **kwargs: Any) -> list[ModelT]:  # pragma: no cover - typing surface only
        ...

    async def abulk_update(self, objs: list[ModelT], fields: list[str], **kwargs: Any) -> int:  # pragma: no cover - typing surface only
        ...

    async def acount(self) -> int:  # pragma: no cover - typing surface only
        ...

    async def afirst(self) -> Optional[ModelT]:  # pragma: no cover - typing surface only
        ...

    async def alast(self) -> Optional[ModelT]:  # pragma: no cover - typing surface only
        ...

    async def aexists(self) -> bool:  # pragma: no cover - typing surface only
        ...

    def aiterator(self) -> Iterator[ModelT]:  # pragma: no cover - typing surface only
        ...


__all__ = [
    "TypedQuerySet",
    "TypedManager",
]




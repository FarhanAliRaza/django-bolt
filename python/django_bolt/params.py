from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class Param:
    source: str
    alias: Optional[str] = None
    embed: Optional[bool] = None


def Query(default: Any = ... , *, alias: Optional[str] = None) -> Any:
    return Param(source="query", alias=alias)


def Path(default: Any = ... , *, alias: Optional[str] = None) -> Any:
    return Param(source="path", alias=alias)


def Body(default: Any = ... , *, alias: Optional[str] = None, embed: Optional[bool] = None) -> Any:
    return Param(source="body", alias=alias, embed=embed)


def Header(default: Any = ... , *, alias: Optional[str] = None) -> Any:
    return Param(source="header", alias=alias)


def Cookie(default: Any = ... , *, alias: Optional[str] = None) -> Any:
    return Param(source="cookie", alias=alias)


def Form(default: Any = ... , *, alias: Optional[str] = None) -> Any:  # noqa: N802
    return Param(source="form", alias=alias)


def File(default: Any = ... , *, alias: Optional[str] = None) -> Any:  # noqa: N802
    return Param(source="file", alias=alias)


@dataclass
class Depends:
    dependency: Optional[Callable[..., Any]] = None
    use_cache: bool = True



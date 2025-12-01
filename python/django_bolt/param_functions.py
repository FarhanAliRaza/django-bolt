from typing import Any

from .params import (
    Body as _Body,
    Cookie as _Cookie,
    Depends as _Depends,
    File as _File,
    Form as _Form,
    Header as _Header,
    Path as _Path,
    Query as _Query,
)


def Query(*args: Any, **kwargs: Any) -> Any:  # noqa: N802
    return _Query(*args, **kwargs)


def Path(*args: Any, **kwargs: Any) -> Any:  # noqa: N802
    return _Path(*args, **kwargs)


def Body(*args: Any, **kwargs: Any) -> Any:  # noqa: N802
    return _Body(*args, **kwargs)


def Header(*args: Any, **kwargs: Any) -> Any:  # noqa: N802
    return _Header(*args, **kwargs)


def Cookie(*args: Any, **kwargs: Any) -> Any:  # noqa: N802
    return _Cookie(*args, **kwargs)


def Depends(*args: Any, **kwargs: Any) -> Any:  # noqa: N802
    return _Depends(*args, **kwargs)


def Form(*args: Any, **kwargs: Any) -> Any:  # noqa: N802
    return _Form(*args, **kwargs)


def File(*args: Any, **kwargs: Any) -> Any:  # noqa: N802
    return _File(*args, **kwargs)


__all__ = ["Body", "Cookie", "Depends", "File", "Form", "Header", "Path", "Query"]

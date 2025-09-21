from typing import Any

from .params import (
    Query as _Query,
    Path as _Path,
    Body as _Body,
    Header as _Header,
    Cookie as _Cookie,
    Depends as _Depends,
    Form as _Form,
    File as _File,
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


__all__ = ["Query", "Path", "Body", "Header", "Cookie", "Depends", "Form", "File"]



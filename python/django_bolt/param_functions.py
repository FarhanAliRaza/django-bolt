from typing import Any

from .params import (
    Body as _Body,
)
from .params import (
    Cookie as _Cookie,
)
from .params import (
    Depends as _Depends,
)
from .params import (
    File as _File,
)
from .params import (
    Form as _Form,
)
from .params import (
    Header as _Header,
)
from .params import (
    Path as _Path,
)
from .params import (
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


__all__ = ["Query", "Path", "Body", "Header", "Cookie", "Depends", "Form", "File"]



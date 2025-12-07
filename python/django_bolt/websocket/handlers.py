"""WebSocket handler utilities."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .types import WebSocket


def is_websocket_handler(func: Callable[..., Any]) -> bool:
    """Check if a function is a WebSocket handler."""
    return getattr(func, "_is_websocket_handler", False)


def mark_websocket_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a function as a WebSocket handler."""
    func._is_websocket_handler = True
    return func


def get_websocket_param_name(func: Callable[..., Any]) -> str | None:
    """
    Get the parameter name that expects a WebSocket object.

    Looks for parameter with WebSocket type annotation.
    """
    sig = inspect.signature(func)
    hints = {}

    try:
        hints = func.__annotations__.copy() if hasattr(func, "__annotations__") else {}
    except Exception:
        pass

    for param_name, param in sig.parameters.items():
        # Check annotation
        annotation = hints.get(param_name) or param.annotation
        if annotation is inspect.Parameter.empty:
            continue

        # Handle string annotations and actual types
        annotation_name = (
            annotation if isinstance(annotation, str)
            else getattr(annotation, "__name__", str(annotation))
        )

        if "WebSocket" in annotation_name:
            return param_name

    # Default to 'websocket' if no annotation found
    if "websocket" in sig.parameters:
        return "websocket"

    # Return first parameter as fallback
    params = list(sig.parameters.keys())
    return params[0] if params else None


async def run_websocket_handler(
    handler: Callable[..., Any],
    websocket: "WebSocket",
    path_params: dict[str, str] | None = None,
    **extra_kwargs: Any,
) -> None:
    """
    Run a WebSocket handler with proper parameter injection.

    Args:
        handler: The WebSocket handler function
        websocket: The WebSocket connection object
        path_params: Path parameters from URL matching
        extra_kwargs: Additional keyword arguments
    """
    kwargs: dict[str, Any] = {}

    # Find the WebSocket parameter name
    ws_param = get_websocket_param_name(handler)
    if ws_param:
        kwargs[ws_param] = websocket

    # Add path parameters
    if path_params:
        sig = inspect.signature(handler)
        for name, value in path_params.items():
            if name in sig.parameters and name != ws_param:
                kwargs[name] = value

    # Add extra kwargs
    kwargs.update(extra_kwargs)

    # Call the handler
    result = handler(**kwargs)
    if inspect.iscoroutine(result):
        await result

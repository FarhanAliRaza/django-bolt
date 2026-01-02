"""Middleware compilation utilities."""

from __future__ import annotations

import datetime
import decimal
import logging
import uuid
from collections.abc import Callable
from typing import Any, get_origin

from ..auth.backends import get_default_authentication_classes
from ..auth.guards import get_default_permission_classes
from ..typing import unwrap_optional

logger = logging.getLogger(__name__)

# Type hint constants - MUST match src/type_coercion.rs
TYPE_INT = 1
TYPE_FLOAT = 2
TYPE_BOOL = 3
TYPE_STRING = 4
TYPE_UUID = 5
TYPE_DATETIME = 6
TYPE_DECIMAL = 7
TYPE_DATE = 8
TYPE_TIME = 9


def get_type_hint_id(annotation: Any) -> int:
    """
    Map Python type annotations to Rust type hint IDs.

    These IDs are used by Rust's type_coercion module to convert
    string parameters to typed values before passing to Python.

    Args:
        annotation: Python type annotation (e.g., int, str, uuid.UUID)

    Returns:
        Type hint ID constant (TYPE_INT, TYPE_STRING, etc.)
    """
    # Unwrap Optional[T] or T | None
    unwrapped = unwrap_optional(annotation)

    # Get base type if it's a generic
    origin = get_origin(unwrapped)
    if origin is not None:
        # For generic types like list[int], we can't coerce in Rust
        return TYPE_STRING

    # Direct type mapping
    if unwrapped is int:
        return TYPE_INT
    elif unwrapped is float:
        return TYPE_FLOAT
    elif unwrapped is bool:
        return TYPE_BOOL
    elif unwrapped is str:
        return TYPE_STRING
    elif unwrapped is uuid.UUID:
        return TYPE_UUID
    elif unwrapped is datetime.datetime:
        return TYPE_DATETIME
    elif unwrapped is datetime.date:
        return TYPE_DATE
    elif unwrapped is datetime.time:
        return TYPE_TIME
    elif unwrapped is decimal.Decimal:
        return TYPE_DECIMAL
    else:
        # Complex types (structs, dicts, etc.) - keep as string
        return TYPE_STRING


def compile_middleware_meta(
    handler: Callable,
    method: str,
    path: str,
    global_middleware: list[Any],
    global_middleware_config: dict[str, Any],
    guards: list[Any] | None = None,
    auth: list[Any] | None = None,
) -> dict[str, Any] | None:
    """Compile middleware metadata for a handler, including guards and auth."""
    # Check for handler-specific middleware
    handler_middleware = []
    skip_middleware: set[str] = set()

    if hasattr(handler, "__bolt_middleware__"):
        handler_middleware = handler.__bolt_middleware__

    if hasattr(handler, "__bolt_skip_middleware__"):
        skip_middleware = handler.__bolt_skip_middleware__

    # Merge global and handler middleware
    all_middleware = []

    # Add global middleware first
    for mw in global_middleware:
        mw_dict = middleware_to_dict(mw)
        if mw_dict and mw_dict.get("type") not in skip_middleware:
            all_middleware.append(mw_dict)

    # Add global config-based middleware
    if global_middleware_config:
        for mw_type, config in global_middleware_config.items():
            if mw_type not in skip_middleware:
                mw_dict = {"type": mw_type}
                mw_dict.update(config)
                all_middleware.append(mw_dict)

    # Add handler-specific middleware
    for mw in handler_middleware:
        mw_dict = middleware_to_dict(mw)
        if mw_dict:
            all_middleware.append(mw_dict)

    # Compile authentication backends
    auth_backends = []
    if auth is not None:
        # Per-route auth override
        for auth_backend in auth:
            if hasattr(auth_backend, "to_metadata"):
                auth_backends.append(auth_backend.to_metadata())
    else:
        # Use global default authentication classes
        for auth_backend in get_default_authentication_classes():
            if hasattr(auth_backend, "to_metadata"):
                auth_backends.append(auth_backend.to_metadata())

    # Compile guards/permissions
    guard_list = []
    if guards is not None:
        # Per-route guards override
        for guard in guards:
            # Check if it's an instance with to_metadata method
            if hasattr(guard, "to_metadata") and callable(getattr(guard, "to_metadata", None)):
                try:
                    # Try calling as instance method
                    guard_list.append(guard.to_metadata())
                except TypeError:
                    # If it fails, might be a class, try instantiating
                    try:
                        instance = guard()
                        guard_list.append(instance.to_metadata())
                    except Exception as e:
                        logger.warning(
                            "Failed to instantiate guard class %s for metadata compilation. "
                            "Guard will be skipped. Error: %s",
                            guard.__class__.__name__ if hasattr(guard, "__class__") else type(guard).__name__,
                            e,
                        )
            elif isinstance(guard, type):
                # It's a class reference, instantiate it
                try:
                    instance = guard()
                    if hasattr(instance, "to_metadata"):
                        guard_list.append(instance.to_metadata())
                except Exception as e:
                    logger.warning(
                        "Failed to instantiate guard class %s for metadata compilation. "
                        "Guard will be skipped. Error: %s",
                        guard.__name__ if hasattr(guard, "__name__") else str(guard),
                        e,
                    )
    else:
        # Use global default permission classes
        for guard in get_default_permission_classes():
            if hasattr(guard, "to_metadata"):
                guard_list.append(guard.to_metadata())

    # Only include metadata if something is configured
    # Note: include result even when only skip flags are present so Rust can
    #       honor route-level skips like `compression`.
    if not all_middleware and not auth_backends and not guard_list and not skip_middleware:
        return None

    result = {"method": method, "path": path}

    if all_middleware:
        result["middleware"] = all_middleware

    # Always include skip flags if present (even without middleware/auth/guards)
    if skip_middleware:
        result["skip"] = list(skip_middleware)

    if auth_backends:
        result["auth_backends"] = auth_backends

    if guard_list:
        result["guards"] = guard_list

    return result


def add_optimization_flags_to_metadata(metadata: dict[str, Any] | None, handler_meta: dict[str, Any]) -> dict[str, Any]:
    """
    Add optimization flags to middleware metadata.

    These flags indicate which request components the handler actually needs,
    allowing Rust to skip parsing unused data.

    Also extracts type hints for path and query parameters to enable
    Rust-side type coercion (avoiding Python's convert_primitive overhead).

    Args:
        metadata: Existing middleware metadata dict (or None to create new)
        handler_meta: Handler metadata containing the optimization flags

    Returns:
        Updated metadata dict with optimization flags and param_types
    """
    if metadata is None:
        metadata = {}

    # Copy optimization flags from handler metadata to middleware metadata
    # These will be parsed by Rust's RouteMetadata::from_python()
    metadata["needs_query"] = handler_meta.get("needs_query", True)
    metadata["needs_headers"] = handler_meta.get("needs_headers", True)
    metadata["needs_cookies"] = handler_meta.get("needs_cookies", True)
    metadata["needs_path_params"] = handler_meta.get("needs_path_params", True)
    metadata["is_static_route"] = handler_meta.get("is_static_route", False)

    # Extract type hints for all parameter sources
    # This enables Rust-side type coercion, eliminating Python overhead
    # Format: {"param_name": type_hint_id, ...}
    param_types: dict[str, int] = {}

    fields = handler_meta.get("fields", [])
    for field in fields:
        # Include type hints for path, query, header, cookie, and form
        # Body and file have complex handling in Python
        if field.source in ("path", "query", "header", "cookie", "form"):
            type_hint = get_type_hint_id(field.annotation)
            # Only include non-string types (string is the default, no coercion needed)
            if type_hint != TYPE_STRING:
                param_types[field.name] = type_hint

    if param_types:
        metadata["param_types"] = param_types

    return metadata


def middleware_to_dict(mw: Any) -> dict[str, Any] | None:
    """
    Convert middleware specification to dictionary for Rust metadata.

    Only dict-based middleware configs (from @cors, @rate_limit decorators)
    need to be converted. Python middleware classes/instances are handled
    entirely in Python and don't need serialization to Rust.

    Args:
        mw: Middleware specification (dict from decorators, or Python class/instance)

    Returns:
        Dict if it's a Rust-handled middleware type (cors, rate_limit), None otherwise
    """
    if isinstance(mw, dict):
        # Dict-based config from decorators like @cors() or @rate_limit()
        # These are the only ones Rust needs to know about
        return mw

    # Python middleware classes/instances are handled in Python
    # They don't need to be serialized to Rust metadata
    return None

"""
Parameter binding and extraction with pre-compiled extractors.

This module provides high-performance parameter extraction using pre-compiled
extractor functions that avoid runtime type checking.
"""
import inspect
import msgspec
from typing import Any, Dict, List, Tuple, Callable, Optional
from functools import lru_cache

from .typing import is_msgspec_struct, is_optional, unwrap_optional

__all__ = [
    "convert_primitive",
    "create_extractor",
    "coerce_to_response_type",
    "coerce_to_response_type_async",
]


# Cache for msgspec decoders (performance optimization)
_DECODER_CACHE: Dict[Any, msgspec.json.Decoder] = {}


def get_msgspec_decoder(type_: Any) -> msgspec.json.Decoder:
    """Get or create a cached msgspec decoder for a type."""
    if type_ not in _DECODER_CACHE:
        _DECODER_CACHE[type_] = msgspec.json.Decoder(type_)
    return _DECODER_CACHE[type_]


def convert_primitive(value: str, annotation: Any) -> Any:
    """
    Convert string value to the appropriate type based on annotation.

    Args:
        value: Raw string value from request
        annotation: Target type annotation

    Returns:
        Converted value
    """
    tp = unwrap_optional(annotation)

    if tp is str or tp is Any or tp is None or tp is inspect._empty:
        return value

    if tp is int:
        return int(value)

    if tp is float:
        return float(value)

    if tp is bool:
        v = value.lower()
        if v in ("1", "true", "t", "yes", "y", "on"):
            return True
        if v in ("0", "false", "f", "no", "n", "off"):
            return False
        return bool(value)

    # Fallback: try msgspec decode for JSON in value
    try:
        return msgspec.json.decode(value.encode())
    except Exception:
        return value


def create_path_extractor(name: str, annotation: Any, alias: Optional[str] = None) -> Callable:
    """Create a pre-compiled extractor for path parameters."""
    key = alias or name
    converter = lambda v: convert_primitive(str(v), annotation)

    def extract(params_map: Dict[str, Any]) -> Any:
        if key not in params_map:
            raise ValueError(f"Missing required path parameter: {key}")
        return converter(params_map[key])

    return extract


def create_query_extractor(
    name: str,
    annotation: Any,
    default: Any,
    alias: Optional[str] = None
) -> Callable:
    """Create a pre-compiled extractor for query parameters."""
    key = alias or name
    optional = default is not inspect.Parameter.empty or is_optional(annotation)
    converter = lambda v: convert_primitive(str(v), annotation)

    if optional:
        default_value = None if default is inspect.Parameter.empty else default
        def extract(query_map: Dict[str, Any]) -> Any:
            return converter(query_map[key]) if key in query_map else default_value
    else:
        def extract(query_map: Dict[str, Any]) -> Any:
            if key not in query_map:
                raise ValueError(f"Missing required query parameter: {key}")
            return converter(query_map[key])

    return extract


def create_header_extractor(
    name: str,
    annotation: Any,
    default: Any,
    alias: Optional[str] = None
) -> Callable:
    """Create a pre-compiled extractor for HTTP headers."""
    key = (alias or name).lower()
    optional = default is not inspect.Parameter.empty or is_optional(annotation)
    converter = lambda v: convert_primitive(str(v), annotation)

    if optional:
        default_value = None if default is inspect.Parameter.empty else default
        def extract(headers_map: Dict[str, str]) -> Any:
            return converter(headers_map[key]) if key in headers_map else default_value
    else:
        def extract(headers_map: Dict[str, str]) -> Any:
            if key not in headers_map:
                raise ValueError(f"Missing required header: {key}")
            return converter(headers_map[key])

    return extract


def create_cookie_extractor(
    name: str,
    annotation: Any,
    default: Any,
    alias: Optional[str] = None
) -> Callable:
    """Create a pre-compiled extractor for cookies."""
    key = alias or name
    optional = default is not inspect.Parameter.empty or is_optional(annotation)
    converter = lambda v: convert_primitive(str(v), annotation)

    if optional:
        default_value = None if default is inspect.Parameter.empty else default
        def extract(cookies_map: Dict[str, str]) -> Any:
            return converter(cookies_map[key]) if key in cookies_map else default_value
    else:
        def extract(cookies_map: Dict[str, str]) -> Any:
            if key not in cookies_map:
                raise ValueError(f"Missing required cookie: {key}")
            return converter(cookies_map[key])

    return extract


def create_form_extractor(
    name: str,
    annotation: Any,
    default: Any,
    alias: Optional[str] = None
) -> Callable:
    """Create a pre-compiled extractor for form fields."""
    key = alias or name
    optional = default is not inspect.Parameter.empty or is_optional(annotation)
    converter = lambda v: convert_primitive(str(v), annotation)

    if optional:
        default_value = None if default is inspect.Parameter.empty else default
        def extract(form_map: Dict[str, Any]) -> Any:
            return converter(form_map[key]) if key in form_map else default_value
    else:
        def extract(form_map: Dict[str, Any]) -> Any:
            if key not in form_map:
                raise ValueError(f"Missing required form field: {key}")
            return converter(form_map[key])

    return extract


def create_file_extractor(
    name: str,
    annotation: Any,
    default: Any,
    alias: Optional[str] = None
) -> Callable:
    """Create a pre-compiled extractor for file uploads."""
    key = alias or name
    optional = default is not inspect.Parameter.empty or is_optional(annotation)

    if optional:
        default_value = None if default is inspect.Parameter.empty else default
        def extract(files_map: Dict[str, Any]) -> Any:
            return files_map.get(key, default_value)
    else:
        def extract(files_map: Dict[str, Any]) -> Any:
            if key not in files_map:
                raise ValueError(f"Missing required file: {key}")
            return files_map[key]

    return extract


def create_body_extractor(name: str, annotation: Any) -> Callable:
    """
    Create a pre-compiled extractor for request body.

    Uses cached msgspec decoder for maximum performance.
    """
    if is_msgspec_struct(annotation):
        decoder = get_msgspec_decoder(annotation)
        def extract(body_bytes: bytes) -> Any:
            return decoder.decode(body_bytes)
    else:
        # Fallback to generic msgspec decode
        def extract(body_bytes: bytes) -> Any:
            return msgspec.json.decode(body_bytes, type=annotation)

    return extract


def create_extractor(field: Dict[str, Any]) -> Callable:
    """
    Create an optimized extractor function for a parameter field.

    This is a factory that returns a specialized extractor based on the
    parameter source. The returned function is optimized to avoid runtime
    type checking.

    Args:
        field: Field metadata dictionary

    Returns:
        Extractor function that takes request data and returns parameter value
    """
    source = field["source"]
    name = field["name"]
    annotation = field["annotation"]
    default = field["default"]
    alias = field.get("alias")

    # Return appropriate extractor based on source
    if source == "path":
        return create_path_extractor(name, annotation, alias)
    elif source == "query":
        return create_query_extractor(name, annotation, default, alias)
    elif source == "header":
        return create_header_extractor(name, annotation, default, alias)
    elif source == "cookie":
        return create_cookie_extractor(name, annotation, default, alias)
    elif source == "form":
        return create_form_extractor(name, annotation, default, alias)
    elif source == "file":
        return create_file_extractor(name, annotation, default, alias)
    elif source == "body":
        return create_body_extractor(name, annotation)
    elif source == "request":
        # Request object is passed through directly
        return lambda request: request
    else:
        # Fallback for unknown sources
        def extract(*args, **kwargs):
            if default is not inspect.Parameter.empty:
                return default
            raise ValueError(f"Cannot extract parameter {name} with source {source}")
        return extract


async def coerce_to_response_type_async(value: Any, annotation: Any) -> Any:
    """
    Async version that handles Django QuerySets.

    Args:
        value: Value to coerce
        annotation: Target type annotation

    Returns:
        Coerced value
    """
    # Check if value is a Django QuerySet
    if hasattr(value, '_iterable_class') and hasattr(value, 'model'):
        # It's a QuerySet - convert to list asynchronously
        result = []
        async for item in value:
            result.append(item)
        value = result

    return coerce_to_response_type(value, annotation)


def coerce_to_response_type(value: Any, annotation: Any) -> Any:
    """
    Coerce arbitrary Python objects (including Django models) into the
    declared response type using msgspec.

    Supports:
      - msgspec.Struct: build mapping from attributes if needed
      - list[T]: recursively coerce elements
      - dict/primitive: defer to msgspec.convert

    Args:
        value: Value to coerce
        annotation: Target type annotation

    Returns:
        Coerced value
    """
    from typing import get_origin, get_args, List

    origin = get_origin(annotation)

    # Handle List[T]
    if origin in (list, List):
        args = get_args(annotation)
        elem_type = args[0] if args else Any
        return [coerce_to_response_type(elem, elem_type) for elem in (value or [])]

    # Handle Struct
    if is_msgspec_struct(annotation):
        if isinstance(value, annotation):
            return value
        if isinstance(value, dict):
            return msgspec.convert(value, annotation)
        # Build mapping from attributes based on struct annotations
        fields = getattr(annotation, "__annotations__", {})
        mapped = {name: getattr(value, name, None) for name in fields.keys()}
        return msgspec.convert(mapped, annotation)

    # Default convert path
    return msgspec.convert(value, annotation)

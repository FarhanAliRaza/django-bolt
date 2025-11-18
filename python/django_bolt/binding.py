"""
Parameter binding and extraction with pre-compiled extractors.

This module provides high-performance parameter extraction using pre-compiled
extractor functions that avoid runtime type checking.
"""
from __future__ import annotations


import inspect
import msgspec
from typing import Any, Dict, List, Tuple, Callable, Optional, TYPE_CHECKING, get_origin, get_args
from asgiref.sync import sync_to_async

from .typing import is_msgspec_struct, is_optional, unwrap_optional
from .typing import HandlerMetadata
from .concurrency import sync_to_thread

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
        try:
            return int(value)
        except ValueError:
            from .exceptions import HTTPException
            raise HTTPException(422, detail=f"Invalid integer value: '{value}'")

    if tp is float:
        try:
            return float(value)
        except ValueError:
            from .exceptions import HTTPException
            raise HTTPException(422, detail=f"Invalid float value: '{value}'")

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
    Converts msgspec.DecodeError (JSON parsing errors) to RequestValidationError for proper 422 responses.
    """
    from .exceptions import RequestValidationError, parse_msgspec_decode_error

    if is_msgspec_struct(annotation):
        decoder = get_msgspec_decoder(annotation)
        def extract(body_bytes: bytes) -> Any:
            try:
                return decoder.decode(body_bytes)
            except msgspec.ValidationError:
                # Re-raise ValidationError as-is (field validation errors handled by error_handlers.py)
                # IMPORTANT: Must catch ValidationError BEFORE DecodeError since ValidationError subclasses DecodeError
                raise
            except msgspec.DecodeError as e:
                # JSON parsing error (malformed JSON) - return 422 with error details including line/column
                error_detail = parse_msgspec_decode_error(e, body_bytes)
                raise RequestValidationError(
                    errors=[error_detail],
                    body=body_bytes,
                ) from e
    else:
        # Fallback to generic msgspec decode
        def extract(body_bytes: bytes) -> Any:
            try:
                return msgspec.json.decode(body_bytes, type=annotation)
            except msgspec.ValidationError:
                # Re-raise ValidationError as-is (field validation errors handled by error_handlers.py)
                # IMPORTANT: Must catch ValidationError BEFORE DecodeError since ValidationError subclasses DecodeError
                raise
            except msgspec.DecodeError as e:
                # JSON parsing error (malformed JSON) - return 422 with error details including line/column
                error_detail = parse_msgspec_decode_error(e, body_bytes)
                raise RequestValidationError(
                    errors=[error_detail],
                    body=body_bytes,
                ) from e

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


async def coerce_to_response_type_async(value: Any, annotation: Any, meta: HandlerMetadata | None = None) -> Any:
    """
    Async version that handles Django QuerySets.

    Args:
        value: Value to coerce
        annotation: Target type annotation
        meta: Handler metadata with pre-computed serialization info

    Returns:
        Coerced value
    """
    # Check if value is a QuerySet AND we have pre-computed field names
    if meta and "response_field_names" in meta and hasattr(value, '_iterable_class') and hasattr(value, 'model'):
        # Use pre-computed field names (computed at route registration time)
        field_names = meta["response_field_names"]

        # Call .values() to get a ValuesQuerySet
        values_qs = value.values(*field_names)

        # Convert QuerySet to list (this triggers SQL execution)
        # Using sync_to_thread(list) is MUCH faster than async for iteration
        #
        # Django's async for implementation (django/db/models/query.py:54-68):
        #   - Uses GET_ITERATOR_CHUNK_SIZE = 100 (django/db/models/sql/constants.py:7)
        #   - Calls sync_to_async for EACH chunk: `await sync_to_async(next_slice)(sync_generator)`
        #   - For 10,000 items: 100 sync_to_async calls (~30-50ms overhead)
        #   - For 100,000 items: 1000 sync_to_async calls (~300-500ms overhead)
        #
        # Our approach: 1 sync_to_thread call total (minimal overhead)
        # Performance gain: 100-1000x fewer context switches
        #
        # Memory tradeoff:
        #   - Paginated APIs (20-100 items/page): Trivial memory usage (~20-100KB)
        #   - Small lists (<10K items): Acceptable memory usage (<10MB)
        #   - Large unpaginated lists: Should use pagination or StreamingResponse + .iterator()
        items = await sync_to_async(list)(values_qs)

        # Let msgspec validate and convert entire list in one batch (much faster than N individual conversions)
        result = msgspec.convert(items, annotation)

        return result

    return coerce_to_response_type(value, annotation, meta)


def coerce_to_response_type(value: Any, annotation: Any, meta: HandlerMetadata | None = None) -> Any:
    """
    Coerce arbitrary Python objects (including Django models) into the
    declared response type using msgspec.

    Supports:
      - msgspec.Struct: build mapping from attributes if needed
      - list[T]: recursively coerce elements
      - dict/primitive: defer to msgspec.convert
      - Django QuerySet: convert to list using .values()

    Args:
        value: Value to coerce
        annotation: Target type annotation
        meta: Handler metadata with pre-computed type info

    Returns:
        Coerced value
    """
    # Handle Django QuerySets - convert to list using .values()
    # Works for both sync and async handlers (sync handlers run in thread pool)
    if meta and "response_field_names" in meta and hasattr(value, '_iterable_class') and hasattr(value, 'model'):
        # Use pre-computed field names (computed at route registration time)
        field_names = meta["response_field_names"]

        # Call .values() to get a ValuesQuerySet
        values_qs = value.values(*field_names)

        # Convert QuerySet to list (this triggers SQL execution)
        items = list(values_qs)

        # Let msgspec validate and convert entire list in one batch
        result = msgspec.convert(items, annotation)

        return result

    # Fast path: if annotation is a primitive type (dict, list, str, int, etc.),
    # just return the value without validation. Validation only makes sense for
    # structured types like msgspec.Struct or parameterized generics.
    # Handle both the actual type AND string annotations (PEP 563)
    if annotation in (dict, list, str, int, float, bool, bytes, bytearray, type(None)) or \
       annotation in ('dict', 'list', 'str', 'int', 'float', 'bool', 'bytes', 'bytearray', 'None'):
        # These are primitive types - no validation needed, return as-is
        return value

    # Use pre-computed type information if available
    if meta and "response_field_names" in meta:
        # This is a list[Struct] response - use pre-computed field names
        origin = get_origin(annotation)

        # Handle List[T]
        if origin in (list, List):
            # Check if value is actually a list/iterable
            if not isinstance(value, (list, tuple)) and value is not None:
                args = get_args(annotation)
                elem_name = args[0].__name__ if args else 'Any'
                raise TypeError(
                    f"Response type mismatch: expected list[{elem_name}], "
                    f"but handler returned {type(value).__name__}. "
                    f"Make sure your handler returns a list."
                )

            # Convert objects to dicts if needed (for custom objects that aren't dicts/structs)
            # Check first item to determine if conversion is needed
            if value and len(value) > 0:
                first_item = value[0]
                # If it's not a dict or a msgspec.Struct, convert objects to dicts
                if not isinstance(first_item, (dict, msgspec.Struct)):
                    field_names = meta["response_field_names"]
                    value = [
                        {name: getattr(item, name, None) for name in field_names}
                        for item in value
                    ]

            # For list of structs, we can use batch conversion with msgspec
            # This is much faster than iterating and converting one by one
            return msgspec.convert(value or [], annotation)

    # Fast path: if value is already the right type, return it
    # Cannot use isinstance() with parameterized generics (list[Item], dict[str, int], etc.)
    # Only check for non-generic types
    try:
        if isinstance(value, annotation):
            return value
    except TypeError:
        # annotation is a parameterized generic, skip the fast path
        pass

    # Handle Struct without metadata (single object, not list)
    if is_msgspec_struct(annotation):
        # Check for common type mismatches before msgspec validation
        if isinstance(value, (list, tuple)):
            raise TypeError(
                f"Response type mismatch: expected a single {annotation.__name__}, "
                f"but handler returned a list. Did you mean to annotate with list[{annotation.__name__}]?"
            )

        if isinstance(value, dict):
            try:
                return msgspec.convert(value, annotation)
            except msgspec.ValidationError as e:
                raise TypeError(
                    f"Response validation failed for {annotation.__name__}: {e}"
                ) from e

        # Build mapping from attributes - use pre-computed field names if available
        if meta and "response_field_names" in meta:
            field_names = meta["response_field_names"]
        else:
            # Fallback: runtime introspection (slower)
            field_names = list(getattr(annotation, "__annotations__", {}).keys())

        mapped = {name: getattr(value, name, None) for name in field_names}
        try:
            return msgspec.convert(mapped, annotation)
        except msgspec.ValidationError as e:
            raise TypeError(
                f"Response validation failed for {annotation.__name__}: {e}"
            ) from e

    # Fallback: Check if it's a list without metadata
    origin = get_origin(annotation)
    if origin in (list, List):
        if not isinstance(value, (list, tuple)) and value is not None:
            args = get_args(annotation)
            elem_name = args[0].__name__ if args else 'Any'
            raise TypeError(
                f"Response type mismatch: expected list[{elem_name}], "
                f"but handler returned {type(value).__name__}. "
                f"Make sure your handler returns a list."
            )
        # Use msgspec batch conversion
        return msgspec.convert(value or [], annotation)

    # Default convert path
    try:
        return msgspec.convert(value, annotation)
    except msgspec.ValidationError as e:
        raise TypeError(
            f"Response validation failed: {e}"
        ) from e

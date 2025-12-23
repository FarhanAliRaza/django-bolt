"""
Parameter binding and extraction with pre-compiled extractors.

This module provides high-performance parameter extraction using pre-compiled
extractor functions that avoid runtime type checking.
"""
from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any, get_args, get_origin

import msgspec
from asgiref.sync import sync_to_async

from .exceptions import HTTPException, RequestValidationError, parse_msgspec_decode_error
from .typing import FieldDefinition, HandlerMetadata, is_msgspec_struct, is_optional, unwrap_optional

__all__ = [
    "convert_primitive",
    "create_extractor",
    "create_extractor_for_field",
    "create_path_extractor",
    "create_query_extractor",
    "create_header_extractor",
    "create_cookie_extractor",
    "create_form_extractor",
    "create_file_extractor",
    "create_body_extractor",
    "coerce_to_response_type",
    "coerce_to_response_type_async",
    "get_msgspec_decoder",
]


# Cache for msgspec decoders (performance optimization)
_DECODER_CACHE: dict[Any, msgspec.json.Decoder] = {}


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
        except ValueError as e:
            raise HTTPException(422, detail=f"Invalid integer value: '{value}'") from e

    if tp is float:
        try:
            return float(value)
        except ValueError as e:
            raise HTTPException(422, detail=f"Invalid float value: '{value}'") from e

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


def create_path_extractor(name: str, annotation: Any, alias: str | None = None) -> Callable:
    """Create a pre-compiled extractor for path parameters."""
    key = alias or name
    def converter(v):
        return convert_primitive(str(v), annotation)

    def extract(params_map: dict[str, Any]) -> Any:
        if key not in params_map:
            raise HTTPException(status_code=422, detail=f"Missing required path parameter: {key}")
        return converter(params_map[key])

    return extract


def create_query_extractor(
    name: str,
    annotation: Any,
    default: Any,
    alias: str | None = None
) -> Callable:
    """Create a pre-compiled extractor for query parameters.

    Supports both individual fields and Struct/Serializer types.
    When annotation is a msgspec.Struct or Serializer, extracts all struct
    fields from the query parameters and constructs the struct instance.
    """
    # Check if annotation is a Struct/Serializer type
    unwrapped = unwrap_optional(annotation)
    if is_msgspec_struct(unwrapped):
        return _create_param_struct_extractor(unwrapped, default, "query parameter")

    # Individual field extraction (original behavior)
    key = alias or name
    optional = default is not inspect.Parameter.empty or is_optional(annotation)
    def converter(v):
        return convert_primitive(str(v), annotation)

    if optional:
        default_value = None if default is inspect.Parameter.empty else default
        def extract(query_map: dict[str, Any]) -> Any:
            return converter(query_map[key]) if key in query_map else default_value
    else:
        def extract(query_map: dict[str, Any]) -> Any:
            if key not in query_map:
                raise HTTPException(status_code=422, detail=f"Missing required query parameter: {key}")
            return converter(query_map[key])

    return extract


def create_header_extractor(
    name: str,
    annotation: Any,
    default: Any,
    alias: str | None = None
) -> Callable:
    """Create a pre-compiled extractor for HTTP headers.

    Supports both individual fields and Struct/Serializer types.
    When annotation is a msgspec.Struct or Serializer, extracts all struct
    fields from the headers and constructs the struct instance.
    """
    # Check if annotation is a Struct/Serializer type
    unwrapped = unwrap_optional(annotation)
    if is_msgspec_struct(unwrapped):
        return _create_header_struct_extractor(unwrapped, default)

    # Individual field extraction (original behavior)
    # Convert underscores to hyphens for HTTP header lookup
    # e.g., x_custom -> x-custom, content_type -> content-type
    key = (alias or name).lower().replace("_", "-")
    optional = default is not inspect.Parameter.empty or is_optional(annotation)
    def converter(v):
        return convert_primitive(str(v), annotation)

    if optional:
        default_value = None if default is inspect.Parameter.empty else default
        def extract(headers_map: dict[str, str]) -> Any:
            return converter(headers_map[key]) if key in headers_map else default_value
    else:
        def extract(headers_map: dict[str, str]) -> Any:
            if key not in headers_map:
                raise HTTPException(status_code=422, detail=f"Missing required header: {key}")
            return converter(headers_map[key])

    return extract


def create_cookie_extractor(
    name: str,
    annotation: Any,
    default: Any,
    alias: str | None = None
) -> Callable:
    """Create a pre-compiled extractor for cookies.

    Supports both individual fields and Struct/Serializer types.
    When annotation is a msgspec.Struct or Serializer, extracts all struct
    fields from the cookies and constructs the struct instance.
    """
    # Check if annotation is a Struct/Serializer type
    unwrapped = unwrap_optional(annotation)
    if is_msgspec_struct(unwrapped):
        return _create_param_struct_extractor(unwrapped, default, "cookie")

    # Individual field extraction (original behavior)
    key = alias or name
    optional = default is not inspect.Parameter.empty or is_optional(annotation)
    def converter(v):
        return convert_primitive(str(v), annotation)

    if optional:
        default_value = None if default is inspect.Parameter.empty else default
        def extract(cookies_map: dict[str, str]) -> Any:
            return converter(cookies_map[key]) if key in cookies_map else default_value
    else:
        def extract(cookies_map: dict[str, str]) -> Any:
            if key not in cookies_map:
                raise HTTPException(status_code=422, detail=f"Missing required cookie: {key}")
            return converter(cookies_map[key])

    return extract


def create_form_extractor(
    name: str,
    annotation: Any,
    default: Any,
    alias: str | None = None
) -> Callable:
    """Create a pre-compiled extractor for form fields.

    Supports both individual fields and Struct/Serializer types.
    When annotation is a msgspec.Struct or Serializer, extracts all struct
    fields from the form data and constructs the struct instance.
    """
    # Check if annotation is a Struct/Serializer type
    unwrapped = unwrap_optional(annotation)
    if is_msgspec_struct(unwrapped):
        return _create_param_struct_extractor(unwrapped, default, "form field")

    # Individual field extraction (original behavior)
    key = alias or name
    optional = default is not inspect.Parameter.empty or is_optional(annotation)
    def converter(v):
        return convert_primitive(str(v), annotation)

    if optional:
        default_value = None if default is inspect.Parameter.empty else default
        def extract(form_map: dict[str, Any]) -> Any:
            return converter(form_map[key]) if key in form_map else default_value
    else:
        def extract(form_map: dict[str, Any]) -> Any:
            if key not in form_map:
                raise HTTPException(status_code=422, detail=f"Missing required form field: {key}")
            return converter(form_map[key])

    return extract


def _create_param_struct_extractor(struct_type: type, default: Any, param_type: str) -> Callable:
    """Create an extractor that builds a Struct/Serializer from parameter data.

    Generic helper used by Form(), Query(), and Cookie() extractors.

    Args:
        struct_type: The msgspec.Struct or Serializer class
        default: Default value if the entire struct is optional
        param_type: Type name for error messages (e.g., "form field", "query parameter")

    Returns:
        Extractor function that takes param_map and returns struct instance
    """
    # Pre-compute field info at registration time
    fields_info = []
    for field in msgspec.structs.fields(struct_type):
        fields_info.append({
            'name': field.name,
            'type': field.type,
            'required': field.required,
            'default': field.default,
        })

    def extract(param_map: dict[str, Any]) -> Any:
        # Convert param values to appropriate types
        converted = {}
        for field_info in fields_info:
            field_name = field_info['name']
            field_type = field_info['type']

            if field_name in param_map:
                # Convert string value to appropriate type
                value = param_map[field_name]
                if isinstance(value, str):
                    converted[field_name] = convert_primitive(value, field_type)
                else:
                    converted[field_name] = value
            elif field_info['required']:
                raise HTTPException(
                    status_code=422,
                    detail=f"Missing required {param_type}: {field_name}"
                )
            # If not in param_map and not required, let msgspec use the default

        # Use msgspec.convert to create and validate the struct
        # This runs @field_validator decorators for Serializer types
        try:
            return msgspec.convert(converted, struct_type)
        except msgspec.ValidationError:
            raise  # Let error_handlers.py handle validation errors

    return extract


def _create_header_struct_extractor(struct_type: type, default: Any) -> Callable:
    """Create an extractor that builds a Struct/Serializer from HTTP headers.

    Similar to _create_param_struct_extractor but converts field names from
    snake_case to kebab-case for HTTP header lookup.

    Args:
        struct_type: The msgspec.Struct or Serializer class
        default: Default value if the entire struct is optional

    Returns:
        Extractor function that takes headers_map and returns struct instance
    """
    # Pre-compute field info at registration time
    # Include the kebab-case header name for lookup
    fields_info = []
    for field in msgspec.structs.fields(struct_type):
        fields_info.append({
            'name': field.name,
            'header_name': field.name.lower().replace("_", "-"),
            'type': field.type,
            'required': field.required,
            'default': field.default,
        })

    def extract(headers_map: dict[str, str]) -> Any:
        # Convert header values to appropriate types
        converted = {}
        for field_info in fields_info:
            field_name = field_info['name']
            header_name = field_info['header_name']
            field_type = field_info['type']

            if header_name in headers_map:
                # Convert string value to appropriate type
                value = headers_map[header_name]
                converted[field_name] = convert_primitive(value, field_type)
            elif field_info['required']:
                raise HTTPException(
                    status_code=422,
                    detail=f"Missing required header: {header_name}"
                )
            # If not in headers_map and not required, let msgspec use the default

        # Use msgspec.convert to create and validate the struct
        try:
            return msgspec.convert(converted, struct_type)
        except msgspec.ValidationError:
            raise

    return extract


def create_file_extractor(
    name: str,
    annotation: Any,
    default: Any,
    alias: str | None = None
) -> Callable:
    """Create a pre-compiled extractor for file uploads."""
    key = alias or name
    optional = default is not inspect.Parameter.empty or is_optional(annotation)

    # Check if the annotation expects a list (e.g., list[dict], list[bytes])
    # This handles both single file and multiple file uploads correctly
    origin = getattr(annotation, "__origin__", None)
    expects_list = origin is list

    if optional:
        default_value = None if default is inspect.Parameter.empty else default
        def extract(files_map: dict[str, Any]) -> Any:
            value = files_map.get(key, default_value)
            # Wrap single file in list if annotation expects list
            if expects_list and value is not None and not isinstance(value, list):
                return [value]
            return value
    else:
        def extract(files_map: dict[str, Any]) -> Any:
            if key not in files_map:
                raise HTTPException(status_code=422, detail=f"Missing required file: {key}")
            value = files_map[key]
            # Wrap single file in list if annotation expects list
            if expects_list and not isinstance(value, list):
                return [value]
            return value

    return extract


def create_body_extractor(name: str, annotation: Any) -> Callable:
    """
    Create a pre-compiled extractor for request body.

    Uses cached msgspec decoder for maximum performance.
    Converts msgspec.DecodeError (JSON parsing errors) to RequestValidationError for proper 422 responses.
    """
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


def create_extractor_for_field(field: FieldDefinition) -> Callable | None:
    """
    Create a pre-compiled extractor function for a FieldDefinition.

    This is the preferred factory that works with FieldDefinition objects.
    The returned function is specialized based on the parameter source,
    eliminating runtime type checking.

    Args:
        field: FieldDefinition object

    Returns:
        Extractor function, or None for 'request' and 'dependency' sources
        (which are handled specially by the injector)
    """
    # Import here to avoid circular imports

    source = field.source
    name = field.name
    annotation = field.annotation
    default = field.default
    alias = field.alias

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
        # Request source is handled directly in the injector
        return None
    elif source == "dependency":
        # Dependencies are handled specially in the injector
        return None
    else:
        # Fallback for unknown sources
        if default is not inspect.Parameter.empty:
            return lambda *_args, **_kwargs: default
        return None


def create_extractor(field: dict[str, Any]) -> Callable:
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
        if origin in (list, list):
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
    if origin in (list, list):
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

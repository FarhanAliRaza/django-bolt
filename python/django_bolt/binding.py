"""Parameter binding and type coercion utilities."""
import inspect
import msgspec
from typing import Any, Dict, List, Tuple, Union, get_origin, get_args, Annotated


def is_optional(annotation: Any) -> bool:
    """Check if annotation is Optional[T]."""
    origin = get_origin(annotation)
    if origin is Union:
        args = get_args(annotation)
        return type(None) in args
    return False


def unwrap_optional(annotation: Any) -> Any:
    """Unwrap Optional[T] to get T."""
    origin = get_origin(annotation)
    if origin is Union:
        args = tuple(a for a in get_args(annotation) if a is not type(None))
        return args[0] if len(args) == 1 else Union[args]  # type: ignore
    return annotation


def is_msgspec_struct(tp: Any) -> bool:
    """Check if type is a msgspec.Struct."""
    try:
        return isinstance(tp, type) and issubclass(tp, msgspec.Struct)
    except Exception:
        return False


def convert_primitive(value: str, annotation: Any) -> Any:
    """Convert string value to the appropriate type based on annotation."""
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
        # Fallback: non-empty -> True
        return bool(value)
    # Fallback: try msgspec decode for JSON in value
    try:
        return msgspec.json.decode(value.encode())
    except Exception:
        return value


async def coerce_to_response_type_async(value: Any, annotation: Any) -> Any:
    """Async version that handles Django QuerySets."""
    # Check if value is a Django QuerySet
    if hasattr(value, '_iterable_class') and hasattr(value, 'model'):
        # It's a QuerySet - convert to list asynchronously
        result = []
        async for item in value:
            result.append(item)
        value = result

    return coerce_to_response_type(value, annotation)


def coerce_to_response_type(value: Any, annotation: Any) -> Any:
    """Coerce arbitrary Python objects (including Django models) into the
    declared response type using msgspec. Supports:
      - msgspec.Struct: build mapping from attributes if needed
      - list[T]: recursively coerce elements
      - dict/primitive: defer to msgspec.convert
    """
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


def extract_header_value(key: str, annotation: Any, default: Any, headers_map: Dict[str, str]) -> Any:
    """Extract value from headers."""
    raw = headers_map.get(key.lower())
    if raw is None:
        if default is not inspect._empty or is_optional(annotation):
            return None if default is inspect._empty else default
        else:
            raise ValueError(f"Missing required header: {key}")
    return convert_primitive(str(raw), annotation)


def extract_cookie_value(key: str, annotation: Any, default: Any, cookies_map: Dict[str, str]) -> Any:
    """Extract value from cookies."""
    raw = cookies_map.get(key)
    if raw is None:
        if default is not inspect._empty or is_optional(annotation):
            return None if default is inspect._empty else default
        else:
            raise ValueError(f"Missing required cookie: {key}")
    return convert_primitive(str(raw), annotation)


def extract_form_value(key: str, annotation: Any, default: Any, form_map: Dict[str, Any]) -> Any:
    """Extract value from form data."""
    raw = form_map.get(key)
    if raw is None:
        if default is not inspect._empty or is_optional(annotation):
            return None if default is inspect._empty else default
        else:
            raise ValueError(f"Missing required form field: {key}")
    return convert_primitive(str(raw), annotation)


def extract_file_value(key: str, annotation: Any, default: Any, files_map: Dict[str, Any]) -> Any:
    """Extract value from uploaded files."""
    raw = files_map.get(key)
    if raw is None:
        if default is not inspect._empty or is_optional(annotation):
            return None if default is inspect._empty else default
        else:
            raise ValueError(f"Missing required file: {key}")

    # For files, return the raw dict(s) containing filename and content
    # If it's a list annotation, ensure we have a list
    if hasattr(annotation, "__origin__") and annotation.__origin__ is list:
        return raw if isinstance(raw, list) else [raw]
    else:
        return raw


def extract_parameter_value(
    param: Dict[str, Any],
    request: Dict[str, Any],
    params_map: Dict[str, Any],
    query_map: Dict[str, Any],
    headers_map: Dict[str, str],
    cookies_map: Dict[str, str],
    form_map: Dict[str, Any],
    files_map: Dict[str, Any],
    meta: Dict[str, Any],
    body_obj: Any,
    body_loaded: bool
) -> Tuple[Any, Any, bool]:
    """Extract value for a handler parameter."""
    name = param["name"]
    annotation = param["annotation"]
    default = param["default"]
    source = param["source"]
    alias = param.get("alias")
    key = alias or name

    if key in params_map:
        return convert_primitive(str(params_map[key]), annotation), body_obj, body_loaded
    elif key in query_map:
        return convert_primitive(str(query_map[key]), annotation), body_obj, body_loaded
    elif source == "header":
        return extract_header_value(key, annotation, default, headers_map), body_obj, body_loaded
    elif source == "cookie":
        return extract_cookie_value(key, annotation, default, cookies_map), body_obj, body_loaded
    elif source == "form":
        return extract_form_value(key, annotation, default, form_map), body_obj, body_loaded
    elif source == "file":
        return extract_file_value(key, annotation, default, files_map), body_obj, body_loaded
    else:
        # Maybe body param
        if meta.get("body_struct_param") == name:
            if not body_loaded:
                body_bytes: bytes = request["body"]
                value = msgspec.json.decode(body_bytes, type=meta["body_struct_type"])  # type: ignore
                return value, value, True
            else:
                return body_obj, body_obj, body_loaded
        else:
            if default is not inspect._empty or is_optional(annotation):
                return (None if default is inspect._empty else default), body_obj, body_loaded
            else:
                raise ValueError(f"Missing required parameter: {name}")

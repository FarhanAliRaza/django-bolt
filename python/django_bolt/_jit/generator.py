"""
JIT dispatch code generator.

Generates specialized dispatch functions for each handler at registration time.
This eliminates runtime branching by baking all decisions into generated code.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable

from .. import _json
from ..serialization import serialize_response, serialize_response_sync
from ..typing import HandlerMetadata, HandlerPattern

if TYPE_CHECKING:
    pass

# Global registry of JIT-compiled dispatchers indexed by handler_id
JIT_DISPATCHERS: dict[int, Callable] = {}


def _build_param_extraction_code(meta: HandlerMetadata, indent: str = "    ") -> tuple[str, list[str]]:
    """
    Generate inline parameter extraction code.

    Returns:
        Tuple of (extraction_code, arg_names) where:
        - extraction_code: Python code string for extracting parameters
        - arg_names: List of variable names to pass to handler
    """
    fields = meta.get("fields", [])
    mode = meta.get("mode", "mixed")
    pattern = meta.get("handler_pattern", HandlerPattern.FULL)

    # Fast path: request-only mode
    if mode == "request_only":
        return f"{indent}# Request-only mode\n", ["request"], []

    # Fast path: no parameters
    if not fields or pattern is HandlerPattern.NO_PARAMS:
        return f"{indent}# No parameters\n", [], []

    lines = []
    arg_names = []
    kwarg_items = []

    for field in fields:
        name = field.name
        source = field.source
        alias = field.alias or name
        key = repr(alias)  # Quoted string for dict access
        default = field.default
        is_optional = field.is_optional

        # Generate extraction code based on source
        if source == "request":
            lines.append(f"{indent}{name} = request")
        elif source == "path":
            lines.append(f"{indent}{name} = request['params'][{key}]")
        elif source == "query":
            if is_optional:
                if default is inspect.Parameter.empty:
                    lines.append(f"{indent}{name} = request['query'].get({key})")
                else:
                    lines.append(f"{indent}{name} = request['query'].get({key}, {repr(default)})")
            else:
                lines.append(f"{indent}{name} = request['query'][{key}]")
        elif source == "header":
            lower_key = repr(alias.lower())
            if is_optional:
                if default is inspect.Parameter.empty:
                    lines.append(f"{indent}{name} = request.get('headers', {{}}).get({lower_key})")
                else:
                    lines.append(f"{indent}{name} = request.get('headers', {{}}).get({lower_key}, {repr(default)})")
            else:
                lines.append(f"{indent}{name} = request['headers'][{lower_key}]")
        elif source == "cookie":
            if is_optional:
                if default is inspect.Parameter.empty:
                    lines.append(f"{indent}{name} = request.get('cookies', {{}}).get({key})")
                else:
                    lines.append(f"{indent}{name} = request.get('cookies', {{}}).get({key}, {repr(default)})")
            else:
                lines.append(f"{indent}{name} = request['cookies'][{key}]")
        elif source == "body":
            # Body extraction requires the extractor (msgspec decoder)
            # We'll use a captured reference
            lines.append(f"{indent}{name} = _body_extractor_{name}(request['body'])")
        elif source == "form":
            if is_optional:
                lines.append(f"{indent}{name} = request.form.get({key})")
            else:
                lines.append(f"{indent}{name} = request.form[{key}]")
        elif source == "file":
            if is_optional:
                lines.append(f"{indent}{name} = request.files.get({key})")
            else:
                lines.append(f"{indent}{name} = request.files[{key}]")
        elif source == "dependency":
            # Dependencies require async resolution - fall back to captured injector
            return None, None  # Signal to use fallback path
        else:
            # Unknown source, fall back
            return None, None

        # Track args vs kwargs based on parameter kind
        if field.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
            arg_names.append(name)
        else:
            kwarg_items.append((name, name))

    extraction_code = "\n".join(lines) + "\n" if lines else ""
    return extraction_code, arg_names, kwarg_items


def _build_handler_call_code(
    meta: HandlerMetadata,
    arg_names: list[str],
    kwarg_items: list[tuple[str, str]],
    indent: str = "    "
) -> str:
    """Generate handler invocation code."""
    is_async = meta.get("is_async", True)
    is_blocking = meta.get("is_blocking", False)

    # Build call arguments
    args_str = ", ".join(arg_names)
    kwargs_str = ", ".join(f"{k}={v}" for k, v in kwarg_items)

    if args_str and kwargs_str:
        call_args = f"{args_str}, {kwargs_str}"
    else:
        call_args = args_str or kwargs_str

    if is_async:
        return f"{indent}result = await handler({call_args})\n"
    elif is_blocking:
        return f"{indent}result = await _sync_to_thread(handler, {call_args})\n"
    else:
        return f"{indent}result = handler({call_args})\n"


def compile_jit_dispatcher(
    handler_id: int,
    handler: Callable,
    meta: HandlerMetadata,
) -> Callable | None:
    """
    Compile a JIT-specialized dispatch function for a handler.

    This generates Python code that:
    1. Extracts parameters inline (no function calls)
    2. Handles auth context inline (if needed)
    3. Calls handler directly (async/sync baked in)
    4. Serializes response inline (common cases)

    Args:
        handler_id: Unique handler identifier
        handler: The handler function
        meta: Handler metadata from compile_binder

    Returns:
        Specialized dispatch function or None if fallback is needed
    """
    mode = meta.get("mode", "mixed")
    pattern = meta.get("handler_pattern", HandlerPattern.FULL)
    is_async = meta.get("is_async", True)
    is_blocking = meta.get("is_blocking", False)
    has_deps = pattern is HandlerPattern.WITH_DEPS

    # For now, skip JIT for complex cases
    # - Handlers with dependencies (need async resolution with caching)
    # - Handlers with middleware
    # - Handlers with file uploads (need cleanup)
    if has_deps or meta.get("has_file_uploads", False):
        return None

    # Try to build parameter extraction code
    result = _build_param_extraction_code(meta)
    if result[0] is None:
        return None  # Fallback needed

    extraction_code, arg_names, kwarg_items = result

    # Build handler call code
    call_code = _build_handler_call_code(meta, arg_names, kwarg_items)

    # Build the complete function
    func_name = f"_jit_dispatch_{handler_id}"

    # Determine if we need async
    needs_await = is_async or is_blocking

    if needs_await:
        func_def = f"async def {func_name}(handler, request, meta):\n"
    else:
        # Sync handler with sync serialization
        func_def = f"def {func_name}(handler, request, meta):\n"

    # Build function body
    body_lines = []

    # Parameter extraction
    if extraction_code.strip():
        body_lines.append(extraction_code)

    # Handler call
    body_lines.append(call_code)

    # Response serialization
    # For common dict/list returns, we can inline the fast path
    # But for now, use the existing serialize_response for correctness
    if needs_await:
        body_lines.append("    return await _serialize_response(result, meta)\n")
    else:
        body_lines.append("    return _serialize_response_sync(result, meta)\n")

    func_code = func_def + "".join(body_lines)

    # Build namespace with required imports/references
    namespace = {
        "_json": _json,
        "_serialize_response": serialize_response,
        "_serialize_response_sync": serialize_response_sync,
    }

    # Add body extractors if needed
    fields = meta.get("fields", [])
    for field in fields:
        if field.source == "body" and hasattr(field, "extractor") and field.extractor is not None:
            namespace[f"_body_extractor_{field.name}"] = field.extractor

    # Add sync_to_thread if needed
    if is_blocking and not is_async:
        from asgiref.sync import sync_to_async
        namespace["_sync_to_thread"] = sync_to_async(thread_sensitive=True)

    try:
        exec(func_code, namespace)
        jit_func = namespace[func_name]

        # Store in global registry
        JIT_DISPATCHERS[handler_id] = jit_func

        return jit_func
    except Exception as e:
        # If code generation fails, return None to use fallback
        import sys
        print(f"JIT compilation failed for handler {handler_id}: {e}", file=sys.stderr)
        return None


def get_jit_dispatcher(handler_id: int) -> Callable | None:
    """Get the JIT-compiled dispatcher for a handler, if available."""
    return JIT_DISPATCHERS.get(handler_id)

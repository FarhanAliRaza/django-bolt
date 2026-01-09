"""
Registration-time compilation functions.

This module contains functions called once per route at startup.
Moving this out reduces api.py size without impacting runtime performance.
"""

from __future__ import annotations

import inspect
import sys
from collections.abc import Callable
from typing import Annotated, Any, get_args, get_origin, get_type_hints

import msgspec

from ..dependencies import resolve_dependency
from ..params import Depends as DependsMarker
from ..params import Param
from ..typing import (
    FieldDefinition,
    HandlerMetadata,
    HandlerPattern,
    is_msgspec_struct,
    is_upload_file_type,
    unwrap_optional,
)
from ..websocket import WebSocket as WebSocketType
from .extractors import create_extractor_for_field
from .runtime import extract_parameter_value, extract_path_params


def extract_response_metadata(response_type: Any) -> dict[str, Any]:
    """
    Extract serialization metadata from response type annotation.

    Pre-computes field names for QuerySet.values() optimization.
    This method is called once at route registration time, not per-request.

    Args:
        response_type: Type annotation (e.g., list[UserMini], User, dict, etc.)

    Returns:
        Metadata dictionary with optional 'response_field_names' key

    Example:
        meta = extract_response_metadata(list[UserMini])
        # Returns: {"response_field_names": ["id", "username"]}
    """
    metadata = {}

    # Check if response type is list[Struct] for QuerySet optimization
    origin = get_origin(response_type)
    if origin in (list, list):
        args = get_args(response_type)
        if args:
            elem_type = args[0]
            if is_msgspec_struct(elem_type):
                # Extract field names for QuerySet.values() optimization
                # This allows us to do: queryset.values("id", "username")
                # instead of loading all fields and converting to dict
                fields = getattr(elem_type, "__annotations__", {})
                metadata["response_field_names"] = list(fields.keys())

    return metadata


def field_has_upload_file(field: FieldDefinition) -> bool:
    """Check if a field contains UploadFile types (for auto-cleanup detection)."""
    if field.source != "form":
        return False

    # Check if annotation is a struct with UploadFile fields
    annotation = unwrap_optional(field.annotation)
    if is_msgspec_struct(annotation):
        for struct_field in msgspec.structs.fields(annotation):
            if is_upload_file_type(struct_field.type):
                return True
    return False


def classify_handler_pattern(
    fields: list[FieldDefinition], meta: HandlerMetadata, needs_form_parsing: bool
) -> HandlerPattern:
    """
    Classify handler into a pattern for specialized injector selection.

    This enables optimized fast paths for common handler patterns,
    eliminating unnecessary checks at request time.

    Returns:
        HandlerPattern enum value for specialized injector selection
    """
    # Check field sources once
    sources = {f.source for f in fields}
    has_deps = "dependency" in sources
    has_request = "request" in sources
    has_headers = "header" in sources

    # Get flags from metadata
    has_path = meta["needs_path_params"]
    has_query = meta["needs_query"]
    has_body = meta["needs_body"]
    has_cookies = meta["needs_cookies"]

    # Priority-ordered pattern matching
    if has_deps:
        return HandlerPattern.WITH_DEPS
    if not fields:
        return HandlerPattern.NO_PARAMS
    if has_request or needs_form_parsing:
        return HandlerPattern.FULL

    # Check for simple patterns (no headers/cookies)
    if has_headers or has_cookies:
        return HandlerPattern.FULL

    # Single-source patterns
    if has_body and not has_path and not has_query:
        return HandlerPattern.BODY_ONLY
    if has_path and not has_query and not has_body:
        return HandlerPattern.PATH_ONLY
    if has_query and not has_path and not has_body:
        return HandlerPattern.QUERY_ONLY
    if (has_path or has_query) and not has_body:
        return HandlerPattern.SIMPLE

    return HandlerPattern.FULL


def compile_binder(fn: Callable, http_method: str, path: str) -> HandlerMetadata:
    """
    Compile parameter binding metadata for a handler function.

    This function:
    1. Parses function signature and type hints
    2. Creates FieldDefinition for each parameter
    3. Infers parameter sources (path, query, body, etc.)
    4. Validates HTTP method compatibility
    5. Pre-compiles extractors for performance

    Args:
        fn: Handler function
        http_method: HTTP method (GET, POST, etc.)
        path: Route path pattern

    Returns:
        Metadata dictionary for parameter binding

    Raises:
        TypeError: If GET/HEAD/DELETE/OPTIONS handlers have body parameters
    """
    sig = inspect.signature(fn)
    # Get the correct namespace for resolving string annotations (from __future__ import annotations)
    # Use fn.__module__ to get the module where annotations were defined (especially important for
    # class-based views where the handler wrapper is created in views.py but annotations come from user's module)
    globalns = sys.modules.get(fn.__module__, {}).__dict__ if fn.__module__ else {}
    type_hints = get_type_hints(fn, globalns=globalns, include_extras=True)

    # Extract path parameters from route pattern
    path_params = extract_path_params(path)

    meta: HandlerMetadata = {
        "sig": sig,
        "fields": [],
        "path_params": path_params,
        "http_method": http_method,
    }

    # Quick path: single parameter that looks like request
    params = list(sig.parameters.values())
    if len(params) == 1 and params[0].name in {"request", "req"}:
        meta["mode"] = "request_only"
        return meta

    # Parse each parameter into FieldDefinition
    field_definitions: list[FieldDefinition] = []

    for param in params:
        name = param.name
        annotation = type_hints.get(name, param.annotation)

        # Extract explicit markers from Annotated or default
        explicit_marker = None

        # Check Annotated[T, ...]
        origin = get_origin(annotation)
        if origin is Annotated:
            args = get_args(annotation)
            annotation = args[0] if args else annotation  # Unwrap to get actual type
            for meta_val in args[1:]:
                if isinstance(meta_val, (Param, DependsMarker)):
                    explicit_marker = meta_val
                    break

        # Check default value for marker
        if explicit_marker is None and isinstance(param.default, (Param, DependsMarker)):
            explicit_marker = param.default

        # Create FieldDefinition with inference
        field = FieldDefinition.from_parameter(
            parameter=param,
            annotation=annotation,
            path_params=path_params,
            http_method=http_method,
            explicit_marker=explicit_marker,
        )

        # Attach pre-compiled extractor to field (performance optimization)
        # This allows the injector to call the extractor directly without source checking
        extractor = create_extractor_for_field(field)
        if extractor is not None:
            # Use object.__setattr__ since FieldDefinition is frozen
            object.__setattr__(field, "extractor", extractor)

        field_definitions.append(field)

    # HTTP Method Validation: Ensure GET/HEAD/DELETE/OPTIONS don't have body params
    body_fields = [f for f in field_definitions if f.source == "body"]
    if http_method in ("GET", "HEAD", "DELETE", "OPTIONS") and body_fields:
        param_names = [f.name for f in body_fields]
        raise TypeError(
            f"Handler {fn.__name__} for {http_method} {path} cannot have body parameters.\n"
            f"Found body parameters: {param_names}\n"
            f"Solutions:\n"
            f"  1. Change HTTP method to POST/PUT/PATCH\n"
            f"  2. Use Query() marker for query parameters\n"
            f"  3. Use simple types (str, int) which auto-infer as query params"
        )

    # Store FieldDefinition objects directly (Phase 4: completed migration)
    meta["fields"] = field_definitions

    # Detect single body parameter for fast path
    if len(body_fields) == 1:
        body_field = body_fields[0]
        if body_field.is_msgspec_struct:
            meta["body_struct_param"] = body_field.name
            meta["body_struct_type"] = body_field.annotation

    # Response type handling is done in _route_decorator() after priority resolution
    # This keeps compile_binder() focused on parameter binding only

    meta["mode"] = "mixed"

    # Performance: Check if handler needs form/file parsing
    # This allows us to skip expensive form parsing for 95% of endpoints
    needs_form_parsing = any(f.source in ("form", "file") for f in field_definitions)
    meta["needs_form_parsing"] = needs_form_parsing

    # Track if handler has file uploads (for auto-cleanup optimization)
    # Check both direct File() params and Form() structs with UploadFile fields
    meta["has_file_uploads"] = any(f.source == "file" or field_has_upload_file(f) for f in field_definitions)

    # Static analysis: Determine which request components are actually used
    # This allows skipping unused parsing at request time
    meta["needs_body"] = any(f.source in ("body", "form", "file") for f in field_definitions)
    meta["needs_query"] = any(f.source == "query" for f in field_definitions)
    # Note: Form/File parsing depends on Content-Type header, so needs_headers must include form handlers
    meta["needs_headers"] = any(f.source == "header" for f in field_definitions) or needs_form_parsing
    meta["needs_cookies"] = any(f.source == "cookie" for f in field_definitions)
    meta["needs_path_params"] = any(f.source == "path" for f in field_definitions)

    # Static route detection: routes without path params can use O(1) lookup
    meta["is_static_route"] = len(path_params) == 0

    # Classify handler pattern for specialized injector selection
    meta["handler_pattern"] = classify_handler_pattern(field_definitions, meta, needs_form_parsing)

    return meta


def compile_websocket_binder(fn: Callable, path: str) -> HandlerMetadata:
    """
    Compile parameter binding metadata for a WebSocket handler.

    Similar to compile_binder but:
    1. Skips the first parameter if it's a WebSocket type (it's injected separately)
    2. No body/form/file parameters (WebSocket doesn't have request body at connect time)
    3. Supports path, query, header, cookie injection

    Args:
        fn: WebSocket handler function
        path: Route path pattern

    Returns:
        Metadata dictionary for parameter binding
    """
    sig = inspect.signature(fn)
    globalns = sys.modules.get(fn.__module__, {}).__dict__ if fn.__module__ else {}
    type_hints = get_type_hints(fn, globalns=globalns, include_extras=True)

    # Extract path parameters from route pattern
    path_params = extract_path_params(path)

    meta: HandlerMetadata = {
        "sig": sig,
        "fields": [],
        "path_params": path_params,
        "http_method": "WEBSOCKET",
    }

    params = list(sig.parameters.values())

    # If no params or just websocket param, return empty fields
    if not params:
        meta["mode"] = "websocket_only"
        meta["needs_body"] = False
        meta["needs_query"] = False
        meta["needs_headers"] = False
        meta["needs_cookies"] = False
        meta["needs_path_params"] = False
        meta["needs_form_parsing"] = False
        meta["handler_pattern"] = HandlerPattern.NO_PARAMS
        return meta

    # Parse each parameter into FieldDefinition, skipping WebSocket param
    field_definitions: list[FieldDefinition] = []

    for param in params:
        name = param.name
        annotation = type_hints.get(name, param.annotation)

        # Unwrap Annotated to get the base type
        base_annotation = annotation
        origin = get_origin(annotation)
        if origin is Annotated:
            args = get_args(annotation)
            base_annotation = args[0] if args else annotation

        # Skip WebSocket parameter - it's injected by Rust
        if base_annotation is WebSocketType or (
            isinstance(base_annotation, type) and issubclass(base_annotation, WebSocketType)
        ):
            continue

        # Also skip if param name is 'websocket' or 'ws' with no annotation
        if name in ("websocket", "ws") and annotation is inspect.Parameter.empty:
            continue

        # Extract explicit markers from Annotated or default
        explicit_marker = None

        if origin is Annotated:
            args = get_args(annotation)
            annotation = args[0] if args else annotation
            for meta_val in args[1:]:
                if isinstance(meta_val, (Param, DependsMarker)):
                    explicit_marker = meta_val
                    break

        if explicit_marker is None and isinstance(param.default, (Param, DependsMarker)):
            explicit_marker = param.default

        # Create FieldDefinition with inference
        # WebSocket doesn't have body, so primitives should default to query
        field = FieldDefinition.from_parameter(
            parameter=param,
            annotation=annotation,
            path_params=path_params,
            http_method="GET",  # Use GET-like inference (no body)
            explicit_marker=explicit_marker,
        )

        # Attach pre-compiled extractor to field
        extractor = create_extractor_for_field(field)
        if extractor is not None:
            object.__setattr__(field, "extractor", extractor)

        field_definitions.append(field)

    meta["fields"] = field_definitions

    if not field_definitions:
        meta["mode"] = "websocket_only"
        meta["needs_body"] = False
        meta["needs_query"] = False
        meta["needs_headers"] = False
        meta["needs_cookies"] = False
        meta["needs_path_params"] = False
        meta["needs_form_parsing"] = False
        meta["handler_pattern"] = HandlerPattern.NO_PARAMS
        return meta

    meta["mode"] = "mixed"
    meta["needs_form_parsing"] = False  # WebSocket doesn't have form data
    meta["needs_body"] = False  # WebSocket doesn't have body at connect
    meta["needs_query"] = any(f.source == "query" for f in field_definitions)
    meta["needs_headers"] = any(f.source == "header" for f in field_definitions)
    meta["needs_cookies"] = any(f.source == "cookie" for f in field_definitions)
    meta["needs_path_params"] = any(f.source == "path" for f in field_definitions)
    meta["is_static_route"] = len(path_params) == 0

    # Classify pattern for injector optimization
    meta["handler_pattern"] = classify_handler_pattern(field_definitions, meta, False)

    return meta


async def build_handler_arguments(
    meta: HandlerMetadata,
    request: dict[str, Any],
    handler_meta_dict: dict[int, HandlerMetadata],
    compile_binder_fn: Callable,
) -> tuple[list[Any], dict[str, Any]]:
    """Build arguments for handler invocation."""
    args: list[Any] = []
    kwargs: dict[str, Any] = {}

    # Access PyRequest mappings
    params_map = request["params"]
    query_map = request["query"]
    headers_map = request.get("headers", {})
    cookies_map = request.get("cookies", {})

    # Form/multipart data is pre-parsed by Rust (type coerced and validated)
    # Use request.form and request.files for pre-typed values
    if meta.get("needs_form_parsing", False):
        form_map = request.form
        files_map = request.files
    else:
        form_map, files_map = {}, {}

    # Body decode cache
    body_obj: Any = None
    body_loaded: bool = False
    dep_cache: dict[Any, Any] = {}

    # Use FieldDefinition objects directly
    fields = meta["fields"]
    for field in fields:
        if field.source == "request":
            value = request
        elif field.source == "dependency":
            if field.dependency is None:
                raise ValueError(f"Depends for parameter {field.name} requires a callable")
            value = await resolve_dependency(
                field.dependency.dependency,
                field.dependency,
                request,
                dep_cache,
                params_map,
                query_map,
                headers_map,
                cookies_map,
                handler_meta_dict,
                compile_binder_fn,
                meta.get("http_method", ""),
                meta.get("path", ""),
            )
        else:
            value, body_obj, body_loaded = extract_parameter_value(
                field,
                request,
                params_map,
                query_map,
                headers_map,
                cookies_map,
                form_map,
                files_map,
                meta,
                body_obj,
                body_loaded,
            )

        # Respect positional-only/keyword-only kinds
        if field.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
            args.append(value)
        else:
            kwargs[field.name] = value

    return args, kwargs


def compile_argument_injector(
    meta: HandlerMetadata,
    handler_meta_dict: dict[int, HandlerMetadata],
    compile_binder_fn: Callable,
) -> Callable[[dict[str, Any]], tuple[list[Any], dict[str, Any]]]:
    """
    Compile a specialized argument injector function for a handler.

    This function creates a closure that captures all parameter extraction logic
    at route registration time, eliminating the overhead of build_handler_arguments()
    at request time.

    The compiled injector is stored in meta["injector"] and returns a tuple of
    (args, kwargs) ready for handler invocation.

    Args:
        meta: Handler metadata containing field definitions
        handler_meta_dict: Dictionary of handler metadata for dependency resolution
        compile_binder_fn: Function to compile binder for dependencies

    Returns:
        Injector function that takes request dict and returns (args, kwargs)

    Performance benefits:
        - Eliminates function call overhead (build_handler_arguments)
        - Pre-compiles all parameter extraction logic
        - Reduces branching with specialized paths for common cases
        - Better CPU cache locality with single inline function
        - Skips unused request data access based on static analysis
        - Uses pre-compiled extractors (eliminates source type checking)
    """
    fields = meta.get("fields", [])
    mode = meta.get("mode", "mixed")
    pattern = meta.get("handler_pattern", HandlerPattern.FULL)

    # Fast path 1: Request-only mode (single request parameter)
    if mode == "request_only":

        def injector_request_only(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
            return ([request], {})

        return injector_request_only

    # Fast path 2: No parameters
    if not fields or pattern is HandlerPattern.NO_PARAMS:

        def injector_no_params(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
            return ([], {})

        return injector_no_params

    # Fast path 3: Path-only parameters (e.g., GET /users/{id})
    # Uses pre-compiled extractors directly on params_map
    if pattern is HandlerPattern.PATH_ONLY:
        # Pre-compute extractors list for direct access
        extractors = [(f.extractor, f.kind, f.name) for f in fields]

        def injector_path_only(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
            params_map = request["params"]
            args: list[Any] = []
            kwargs: dict[str, Any] = {}
            for extractor, kind, name in extractors:
                value = extractor(params_map)
                if kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                    args.append(value)
                else:
                    kwargs[name] = value
            return args, kwargs

        return injector_path_only

    # Fast path 4: Query-only parameters (e.g., GET /search?q=...)
    if pattern is HandlerPattern.QUERY_ONLY:
        extractors = [(f.extractor, f.kind, f.name) for f in fields]

        def injector_query_only(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
            query_map = request["query"]
            args: list[Any] = []
            kwargs: dict[str, Any] = {}
            for extractor, kind, name in extractors:
                value = extractor(query_map)
                if kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                    args.append(value)
                else:
                    kwargs[name] = value
            return args, kwargs

        return injector_query_only

    # Fast path 5: Body-only parameters (e.g., POST with single JSON struct)
    if pattern is HandlerPattern.BODY_ONLY and len(fields) == 1:
        field = fields[0]
        body_extractor = field.extractor
        is_positional = field.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        field_name = field.name

        if is_positional:

            def injector_body_only_positional(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
                body_bytes = request["body"]
                return ([body_extractor(body_bytes)], {})

            return injector_body_only_positional
        else:

            def injector_body_only_kwarg(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
                body_bytes = request["body"]
                return ([], {field_name: body_extractor(body_bytes)})

            return injector_body_only_kwarg

    # Fast path 6: Simple pattern (path + query, no body/headers/cookies)
    if pattern is HandlerPattern.SIMPLE:
        # Pre-categorize fields by source for direct access
        path_fields = [(f.extractor, f.kind, f.name) for f in fields if f.source == "path"]
        query_fields = [(f.extractor, f.kind, f.name) for f in fields if f.source == "query"]
        # Maintain original field order for args
        field_order = [(f.source, i) for i, f in enumerate(fields)]

        def injector_simple(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
            params_map = request["params"]
            query_map = request["query"]
            args: list[Any] = []
            kwargs: dict[str, Any] = {}

            # Extract in original field order
            path_idx = 0
            query_idx = 0
            for source, _ in field_order:
                if source == "path":
                    extractor, kind, name = path_fields[path_idx]
                    value = extractor(params_map)
                    path_idx += 1
                else:  # query
                    extractor, kind, name = query_fields[query_idx]
                    value = extractor(query_map)
                    query_idx += 1

                if kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                    args.append(value)
                else:
                    kwargs[name] = value
            return args, kwargs

        return injector_simple

    # Dependency injection path (async required)
    if pattern is HandlerPattern.WITH_DEPS:
        needs_form = meta.get("needs_form_parsing", False)
        needs_query = meta.get("needs_query", True)
        needs_headers = meta.get("needs_headers", True)
        needs_cookies = meta.get("needs_cookies", True)
        needs_path_params = meta.get("needs_path_params", True)
        has_file_uploads = meta.get("has_file_uploads", False)

        async def injector_with_deps(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
            """Optimized argument injector with dependency support."""
            args: list[Any] = []
            kwargs: dict[str, Any] = {}

            params_map = request["params"] if needs_path_params else {}
            query_map = request["query"] if needs_query else {}
            headers_map = request.get("headers", {}) if needs_headers else {}
            cookies_map = request.get("cookies", {}) if needs_cookies else {}

            if needs_form:
                form_map = request.form
                files_map = request.files
            else:
                form_map, files_map = {}, {}

            body_obj: Any = None
            body_loaded: bool = False
            dep_cache: dict[Any, Any] = {}

            for field in fields:
                if field.source == "request":
                    value = request
                elif field.source == "dependency":
                    if field.dependency is None:
                        raise ValueError(f"Depends for parameter {field.name} requires a callable")
                    value = await resolve_dependency(
                        field.dependency.dependency,
                        field.dependency,
                        request,
                        dep_cache,
                        params_map,
                        query_map,
                        headers_map,
                        cookies_map,
                        handler_meta_dict,
                        compile_binder_fn,
                        meta.get("http_method", ""),
                        meta.get("path", ""),
                    )
                elif field.extractor is not None:
                    # Use pre-compiled extractor
                    source = field.source
                    if source == "path":
                        value = field.extractor(params_map)
                    elif source == "query":
                        value = field.extractor(query_map)
                    elif source == "header":
                        value = field.extractor(headers_map)
                    elif source == "cookie":
                        value = field.extractor(cookies_map)
                    elif source == "form":
                        # Check if extractor needs files_map (for structs with UploadFile fields)
                        if getattr(field.extractor, "needs_files_map", False):
                            value = field.extractor(form_map, files_map)
                        else:
                            value = field.extractor(form_map)
                    elif source == "file":
                        value = field.extractor(files_map)
                    elif source == "body":
                        if not body_loaded:
                            body_obj = field.extractor(request["body"])
                            body_loaded = True
                        value = body_obj
                    else:
                        value, body_obj, body_loaded = extract_parameter_value(
                            field,
                            request,
                            params_map,
                            query_map,
                            headers_map,
                            cookies_map,
                            form_map,
                            files_map,
                            meta,
                            body_obj,
                            body_loaded,
                        )
                else:
                    value, body_obj, body_loaded = extract_parameter_value(
                        field,
                        request,
                        params_map,
                        query_map,
                        headers_map,
                        cookies_map,
                        form_map,
                        files_map,
                        meta,
                        body_obj,
                        body_loaded,
                    )

                if field.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                    args.append(value)
                else:
                    kwargs[field.name] = value

            # Track UploadFiles for auto-cleanup (only when handler has file params)
            if has_file_uploads and "_upload_files" in files_map:
                request.state["_upload_files"] = files_map["_upload_files"]

            return args, kwargs

        return injector_with_deps

    # Full pattern (form, headers, cookies, or complex combinations)
    # Uses pre-compiled extractors with source-based dispatch
    needs_form = meta.get("needs_form_parsing", False)
    needs_query = meta.get("needs_query", True)
    needs_headers = meta.get("needs_headers", True)
    needs_cookies = meta.get("needs_cookies", True)
    needs_path_params = meta.get("needs_path_params", True)
    has_file_uploads = meta.get("has_file_uploads", False)

    def injector_full(request: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
        """Full injector with pre-compiled extractors."""
        args: list[Any] = []
        kwargs: dict[str, Any] = {}

        params_map = request["params"] if needs_path_params else {}
        query_map = request["query"] if needs_query else {}
        headers_map = request.get("headers", {}) if needs_headers else {}
        cookies_map = request.get("cookies", {}) if needs_cookies else {}

        if needs_form:
            form_map = request.form
            files_map = request.files
        else:
            form_map, files_map = {}, {}

        body_obj: Any = None
        body_loaded: bool = False

        for field in fields:
            if field.source == "request":
                value = request
            elif field.extractor is not None:
                # Use pre-compiled extractor based on source
                source = field.source
                if source == "path":
                    value = field.extractor(params_map)
                elif source == "query":
                    value = field.extractor(query_map)
                elif source == "header":
                    value = field.extractor(headers_map)
                elif source == "cookie":
                    value = field.extractor(cookies_map)
                elif source == "form":
                    # Check if extractor needs files_map (for structs with UploadFile fields)
                    if getattr(field.extractor, "needs_files_map", False):
                        value = field.extractor(form_map, files_map)
                    else:
                        value = field.extractor(form_map)
                elif source == "file":
                    value = field.extractor(files_map)
                elif source == "body":
                    if not body_loaded:
                        body_obj = field.extractor(request["body"])
                        body_loaded = True
                    value = body_obj
                else:
                    # Fallback for unknown sources
                    value, body_obj, body_loaded = extract_parameter_value(
                        field,
                        request,
                        params_map,
                        query_map,
                        headers_map,
                        cookies_map,
                        form_map,
                        files_map,
                        meta,
                        body_obj,
                        body_loaded,
                    )
            else:
                # No pre-compiled extractor, use generic extraction
                value, body_obj, body_loaded = extract_parameter_value(
                    field,
                    request,
                    params_map,
                    query_map,
                    headers_map,
                    cookies_map,
                    form_map,
                    files_map,
                    meta,
                    body_obj,
                    body_loaded,
                )

            if field.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                args.append(value)
            else:
                kwargs[field.name] = value

        # Track UploadFiles for auto-cleanup (only when handler has file params)
        if has_file_uploads and "_upload_files" in files_map:
            request.state["_upload_files"] = files_map["_upload_files"]

        return args, kwargs

    return injector_full

"""Dependency injection utilities."""
from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any

from .binding import convert_primitive
from .params import Depends as DependsMarker
from .typing import FieldDefinition


async def resolve_dependency(
    dep_fn: Callable,
    depends_marker: DependsMarker,
    request: dict[str, Any],
    dep_cache: dict[Any, Any],
    params_map: dict[str, Any],
    query_map: dict[str, Any],
    headers_map: dict[str, str],
    cookies_map: dict[str, str],
    handler_meta: dict[Callable, dict[str, Any]],
    compile_binder: Callable,
    http_method: str,
    path: str
) -> Any:
    """
    Resolve a dependency injection.

    Args:
        dep_fn: Dependency function to resolve
        depends_marker: Depends marker with cache settings
        request: Request dict
        dep_cache: Cache for resolved dependencies
        params_map: Path parameters
        query_map: Query parameters
        headers_map: Request headers
        cookies_map: Request cookies
        handler_meta: Metadata cache for handlers
        compile_binder: Function to compile parameter binding metadata
        http_method: HTTP method of the handler using this dependency
        path: Path of the handler using this dependency

    Returns:
        Resolved dependency value
    """
    if depends_marker.use_cache and dep_fn in dep_cache:
        return dep_cache[dep_fn]

    dep_meta = handler_meta.get(dep_fn)
    if dep_meta is None:
        # Compile dependency metadata with the actual HTTP method and path
        # Dependencies MUST be validated against HTTP method constraints
        # e.g., a dependency with Body() can't be used in GET handlers
        dep_meta = compile_binder(dep_fn, http_method, path)
        handler_meta[dep_fn] = dep_meta

    # Check if dependency is async or sync
    is_async = inspect.iscoroutinefunction(dep_fn)

    if dep_meta.get("mode") == "request_only":
        if is_async:
            value = await dep_fn(request)
        else:
            value = dep_fn(request)
    else:
        if is_async:
            value = await call_dependency(
                dep_fn, dep_meta, request, params_map,
                query_map, headers_map, cookies_map
            )
        else:
            value = call_dependency_sync(
                dep_fn, dep_meta, request, params_map,
                query_map, headers_map, cookies_map
            )

    if depends_marker.use_cache:
        dep_cache[dep_fn] = value

    return value


async def call_dependency(
    dep_fn: Callable,
    dep_meta: dict[str, Any],
    request: dict[str, Any],
    params_map: dict[str, Any],
    query_map: dict[str, Any],
    headers_map: dict[str, str],
    cookies_map: dict[str, str]
) -> Any:
    """Call an async dependency function with resolved parameters."""
    dep_args: list[Any] = []
    dep_kwargs: dict[str, Any] = {}

    # Use FieldDefinition objects directly
    for field in dep_meta["fields"]:
        if field.source == "request":
            dval = request
        else:
            dval = extract_dependency_value(field, params_map, query_map, headers_map, cookies_map)

        if field.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
            dep_args.append(dval)
        else:
            dep_kwargs[field.name] = dval

    return await dep_fn(*dep_args, **dep_kwargs)


def call_dependency_sync(
    dep_fn: Callable,
    dep_meta: dict[str, Any],
    request: dict[str, Any],
    params_map: dict[str, Any],
    query_map: dict[str, Any],
    headers_map: dict[str, str],
    cookies_map: dict[str, str]
) -> Any:
    """Call a sync dependency function with resolved parameters."""
    dep_args: list[Any] = []
    dep_kwargs: dict[str, Any] = {}

    # Use FieldDefinition objects directly
    for field in dep_meta["fields"]:
        if field.source == "request":
            dval = request
        else:
            dval = extract_dependency_value(field, params_map, query_map, headers_map, cookies_map)

        if field.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
            dep_args.append(dval)
        else:
            dep_kwargs[field.name] = dval

    return dep_fn(*dep_args, **dep_kwargs)


def extract_dependency_value(
    field: FieldDefinition,
    params_map: dict[str, Any],
    query_map: dict[str, Any],
    headers_map: dict[str, str],
    cookies_map: dict[str, str]
) -> Any:
    """Extract value for a dependency parameter using FieldDefinition.

    Args:
        field: FieldDefinition object describing the parameter
        params_map: Path parameters
        query_map: Query parameters
        headers_map: Request headers
        cookies_map: Request cookies

    Returns:
        Extracted and converted parameter value
    """
    key = field.alias or field.name

    if key in params_map:
        return convert_primitive(str(params_map[key]), field.annotation)
    elif key in query_map:
        return convert_primitive(str(query_map[key]), field.annotation)
    elif field.source == "header":
        raw = headers_map.get(key.lower())
        if raw is None:
            raise ValueError(f"Missing required header: {key}")
        return convert_primitive(str(raw), field.annotation)
    elif field.source == "cookie":
        raw = cookies_map.get(key)
        if raw is None:
            raise ValueError(f"Missing required cookie: {key}")
        return convert_primitive(str(raw), field.annotation)
    else:
        return None

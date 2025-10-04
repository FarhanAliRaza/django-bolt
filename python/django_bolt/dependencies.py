"""Dependency injection utilities."""
import inspect
from typing import Any, Callable, Dict, List
from .params import Depends as DependsMarker
from .binding import convert_primitive


async def resolve_dependency(
    dep_fn: Callable,
    depends_marker: DependsMarker,
    request: Dict[str, Any],
    dep_cache: Dict[Any, Any],
    params_map: Dict[str, Any],
    query_map: Dict[str, Any],
    headers_map: Dict[str, str],
    cookies_map: Dict[str, str],
    handler_meta: Dict[Callable, Dict[str, Any]],
    compile_binder: Callable
) -> Any:
    """Resolve a dependency injection."""
    if depends_marker.use_cache and dep_fn in dep_cache:
        return dep_cache[dep_fn]

    dep_meta = handler_meta.get(dep_fn)
    if dep_meta is None:
        dep_meta = compile_binder(dep_fn)
        handler_meta[dep_fn] = dep_meta

    if dep_meta.get("mode") == "request_only":
        value = await dep_fn(request)
    else:
        value = await call_dependency(
            dep_fn, dep_meta, request, params_map,
            query_map, headers_map, cookies_map
        )

    if depends_marker.use_cache:
        dep_cache[dep_fn] = value

    return value


async def call_dependency(
    dep_fn: Callable,
    dep_meta: Dict[str, Any],
    request: Dict[str, Any],
    params_map: Dict[str, Any],
    query_map: Dict[str, Any],
    headers_map: Dict[str, str],
    cookies_map: Dict[str, str]
) -> Any:
    """Call a dependency function with resolved parameters."""
    dep_args: List[Any] = []
    dep_kwargs: Dict[str, Any] = {}

    for dp in dep_meta["params"]:
        dname = dp["name"]
        dan = dp["annotation"]
        dsrc = dp["source"]
        dalias = dp.get("alias")

        if dsrc == "request":
            dval = request
        else:
            dval = extract_dependency_value(dp, params_map, query_map, headers_map, cookies_map)

        if dp["kind"] in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
            dep_args.append(dval)
        else:
            dep_kwargs[dname] = dval

    return await dep_fn(*dep_args, **dep_kwargs)


def extract_dependency_value(
    param: Dict[str, Any],
    params_map: Dict[str, Any],
    query_map: Dict[str, Any],
    headers_map: Dict[str, str],
    cookies_map: Dict[str, str]
) -> Any:
    """Extract value for a dependency parameter."""
    dname = param["name"]
    dan = param["annotation"]
    dsrc = param["source"]
    dalias = param.get("alias")
    key = dalias or dname

    if key in params_map:
        return convert_primitive(str(params_map[key]), dan)
    elif key in query_map:
        return convert_primitive(str(query_map[key]), dan)
    elif dsrc == "header":
        raw = headers_map.get(key.lower())
        if raw is None:
            raise ValueError(f"Missing required header: {key}")
        return convert_primitive(str(raw), dan)
    elif dsrc == "cookie":
        raw = cookies_map.get(key)
        if raw is None:
            raise ValueError(f"Missing required cookie: {key}")
        return convert_primitive(str(raw), dan)
    else:
        return None

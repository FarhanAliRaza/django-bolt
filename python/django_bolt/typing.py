"""
Type introspection and field definition system for parameter binding.

Inspired by Litestar's architecture but built from scratch for Django-Bolt's
msgspec-first, async-only design with focus on performance.
"""
from __future__ import annotations

import inspect
import msgspec
from dataclasses import dataclass
from typing import Any, get_origin, get_args, Union, Optional, List, Dict, Annotated, TypedDict

__all__ = [
    "FieldDefinition",
    "HandlerMetadata",
    "is_msgspec_struct",
    "is_simple_type",
    "is_sequence_type",
    "is_optional",
    "unwrap_optional",
    "infer_param_source",
]


class HandlerMetadata(TypedDict, total=False):
    """
    Type-safe metadata dictionary for handler functions.

    This structure is compiled once at route registration time and
    contains all information needed for parameter binding, response
    serialization, and OpenAPI documentation generation.
    """

    # Core function metadata
    sig: inspect.Signature
    """Function signature"""

    fields: List[FieldDefinition]
    """List of parameter field definitions"""

    path_params: set[str]
    """Set of path parameter names extracted from route pattern"""

    http_method: str
    """HTTP method (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)"""

    mode: str
    """Handler mode: 'request_only' or 'mixed'"""

    # Body parameter metadata (for fast path optimization)
    body_struct_param: str
    """Name of the single body struct parameter (if present)"""

    body_struct_type: Any
    """Type of the body struct parameter"""

    # Response metadata
    response_type: Any
    """Return type annotation from function signature"""

    default_status_code: int
    """Default HTTP status code for successful responses"""

    # QuerySet serialization optimization (pre-computed at registration)
    response_field_names: List[str]
    """Pre-computed field names for QuerySet.values() call"""

    # Performance optimizations
    needs_form_parsing: bool
    """Whether this handler needs form/multipart parsing (Form/File params)"""

    # OpenAPI documentation metadata
    openapi_tags: List[str]
    """OpenAPI tags for grouping endpoints"""

    openapi_summary: str
    """Short summary for OpenAPI docs"""

    openapi_description: str
    """Detailed description for OpenAPI docs"""


# Simple scalar types that map to query parameters
SIMPLE_TYPES = (str, int, float, bool, bytes)


def is_msgspec_struct(annotation: Any) -> bool:
    """Check if type is a msgspec.Struct."""
    try:
        return isinstance(annotation, type) and issubclass(annotation, msgspec.Struct)
    except (TypeError, AttributeError):
        return False


def is_simple_type(annotation: Any) -> bool:
    """Check if annotation is a simple scalar type (str, int, float, bool, bytes)."""
    origin = get_origin(annotation)
    if origin is not None:
        # Unwrap Optional, List, etc.
        return False
    return annotation in SIMPLE_TYPES or annotation is Any


def is_sequence_type(annotation: Any) -> bool:
    """Check if annotation is a sequence type like List[T]."""
    origin = get_origin(annotation)
    return origin in (list, List, tuple, set, frozenset)


def is_optional(annotation: Any) -> bool:
    """Check if annotation is Optional[T] or T | None."""
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


def is_dataclass_type(annotation: Any) -> bool:
    """Check if annotation is a dataclass."""
    try:
        from dataclasses import is_dataclass
        return is_dataclass(annotation)
    except (TypeError, AttributeError):
        return False


def infer_param_source(
    name: str,
    annotation: Any,
    path_params: set[str],
    http_method: str
) -> str:
    """
    Infer parameter source based on type and context.

    Inference rules (in priority order):
    1. If name matches path parameter -> "path"
    2. If special name (request, req) -> "request"
    3. If simple type (str, int, float, bool) -> "query"
    4. If msgspec.Struct or dataclass -> "body" (if method allows body)
    5. Default -> "query"

    Args:
        name: Parameter name
        annotation: Type annotation
        path_params: Set of path parameter names from route pattern
        http_method: HTTP method (GET, POST, etc.)

    Returns:
        Source string: "path", "query", "body", "request", etc.
    """
    # 1. Path parameters
    if name in path_params:
        return "path"

    # 2. Special request parameter
    if name in {"request", "req"}:
        return "request"

    # Unwrap Optional if present
    unwrapped = unwrap_optional(annotation)

    # 3. Simple types -> query params
    if is_simple_type(unwrapped):
        return "query"

    # 4. Sequence of simple types -> query (for list params)
    if is_sequence_type(unwrapped):
        args = get_args(unwrapped)
        if args and is_simple_type(args[0]):
            return "query"

    # 5. Complex types (msgspec.Struct, dataclass) -> body (if allowed)
    if is_msgspec_struct(unwrapped) or is_dataclass_type(unwrapped):
        if http_method in {"POST", "PUT", "PATCH"}:
            return "body"
        # For GET/DELETE/HEAD, this will trigger validation error later
        return "body"

    # 6. Default to query
    return "query"


@dataclass(frozen=True)
class FieldDefinition:
    """
    Represents a parsed function parameter with type metadata.

    This is the core data structure for parameter binding, containing
    all information needed to extract and validate a parameter value
    from an HTTP request.
    """

    name: str
    """Parameter name"""

    annotation: Any
    """Raw type annotation"""

    default: Any
    """Default value (inspect.Parameter.empty if required)"""

    source: str
    """Parameter source: 'path', 'query', 'body', 'header', 'cookie', 'form', 'file', 'request', 'dependency'"""

    alias: Optional[str] = None
    """Alternative name for the parameter (e.g., 'user-id' for 'user_id')"""

    embed: Optional[bool] = None
    """For body params: whether to embed in a wrapper object"""

    dependency: Any = None
    """Depends marker for dependency injection"""

    kind: inspect._ParameterKind = inspect.Parameter.POSITIONAL_OR_KEYWORD
    """Parameter kind (positional, keyword-only, etc.)"""

    # Cached type properties for performance
    _is_optional: Optional[bool] = None
    _is_simple: Optional[bool] = None
    _is_struct: Optional[bool] = None
    _unwrapped: Optional[Any] = None
    _origin: Optional[Any] = None

    @property
    def is_optional(self) -> bool:
        """Check if parameter is optional (has default or Optional type)."""
        if self._is_optional is None:
            object.__setattr__(
                self,
                "_is_optional",
                self.default is not inspect.Parameter.empty or is_optional(self.annotation)
            )
        return self._is_optional  # type: ignore

    @property
    def is_required(self) -> bool:
        """Check if parameter is required."""
        return not self.is_optional

    @property
    def is_simple_type(self) -> bool:
        """Check if parameter type is simple (str, int, etc.)."""
        if self._is_simple is None:
            unwrapped = self.unwrapped_annotation
            object.__setattr__(self, "_is_simple", is_simple_type(unwrapped))
        return self._is_simple  # type: ignore

    @property
    def is_msgspec_struct(self) -> bool:
        """Check if parameter type is a msgspec.Struct."""
        if self._is_struct is None:
            unwrapped = self.unwrapped_annotation
            object.__setattr__(self, "_is_struct", is_msgspec_struct(unwrapped))
        return self._is_struct  # type: ignore

    @property
    def unwrapped_annotation(self) -> Any:
        """Get annotation with Optional unwrapped."""
        if self._unwrapped is None:
            object.__setattr__(self, "_unwrapped", unwrap_optional(self.annotation))
        return self._unwrapped

    @property
    def origin(self) -> Any:
        """Get the origin type (list, dict, etc.) of the unwrapped annotation."""
        if self._origin is None:
            object.__setattr__(self, "_origin", get_origin(self.unwrapped_annotation))
        return self._origin

    @property
    def field_alias(self) -> str:
        """Get the alias or name."""
        return self.alias or self.name

    @classmethod
    def from_parameter(
        cls,
        parameter: inspect.Parameter,
        annotation: Any,
        path_params: set[str],
        http_method: str,
        explicit_marker: Any = None
    ) -> "FieldDefinition":
        """
        Create FieldDefinition from inspect.Parameter.

        Args:
            parameter: The inspect.Parameter object
            annotation: Type annotation from type hints
            path_params: Set of path parameter names
            http_method: HTTP method for inference
            explicit_marker: Explicit Param or Depends marker if present

        Returns:
            FieldDefinition instance
        """
        from .params import Param, Depends as DependsMarker

        name = parameter.name
        default = parameter.default

        # Handle explicit markers
        source: str
        alias: Optional[str] = None
        embed: Optional[bool] = None
        dependency: Any = None

        if isinstance(explicit_marker, Param):
            source = explicit_marker.source
            alias = explicit_marker.alias
            embed = explicit_marker.embed
        elif isinstance(explicit_marker, DependsMarker):
            source = "dependency"
            dependency = explicit_marker
        else:
            # Infer source from type and context
            source = infer_param_source(name, annotation, path_params, http_method)

        return cls(
            name=name,
            annotation=annotation,
            default=default,
            source=source,
            alias=alias,
            embed=embed,
            dependency=dependency,
            kind=parameter.kind,
        )

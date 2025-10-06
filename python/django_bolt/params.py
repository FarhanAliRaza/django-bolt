"""
Parameter markers and validation constraints for Django-Bolt.

Provides explicit parameter source annotations and validation metadata.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Pattern

__all__ = [
    "Param",
    "Query",
    "Path",
    "Body",
    "Header",
    "Cookie",
    "Form",
    "File",
    "Depends",
]


@dataclass(frozen=True)
class Param:
    """
    Base parameter marker with validation constraints.

    Used internally by Query, Path, Body, etc. markers.
    """

    source: str
    """Parameter source: 'query', 'path', 'body', 'header', 'cookie', 'form', 'file'"""

    alias: Optional[str] = None
    """Alternative name for the parameter in the request"""

    embed: Optional[bool] = None
    """Whether to embed body parameter in wrapper object"""

    # Numeric constraints
    gt: Optional[float] = None
    """Greater than (exclusive minimum)"""

    ge: Optional[float] = None
    """Greater than or equal (inclusive minimum)"""

    lt: Optional[float] = None
    """Less than (exclusive maximum)"""

    le: Optional[float] = None
    """Less than or equal (inclusive maximum)"""

    multiple_of: Optional[float] = None
    """Value must be multiple of this number"""

    # String/collection constraints
    min_length: Optional[int] = None
    """Minimum length for strings or collections"""

    max_length: Optional[int] = None
    """Maximum length for strings or collections"""

    pattern: Optional[str] = None
    """Regex pattern for string validation"""

    # Metadata
    description: Optional[str] = None
    """Parameter description for documentation"""

    example: Any = None
    """Example value for documentation"""

    deprecated: bool = False
    """Mark parameter as deprecated"""


def Query(
    default: Any = ...,
    *,
    alias: Optional[str] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    description: Optional[str] = None,
    example: Any = None,
    deprecated: bool = False,
) -> Any:
    """
    Mark parameter as query parameter.

    Args:
        default: Default value (... for required)
        alias: Alternative parameter name in URL
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        min_length: Minimum string/collection length
        max_length: Maximum string/collection length
        pattern: Regex pattern to match
        description: Parameter description
        example: Example value
        deprecated: Mark as deprecated

    Returns:
        Param marker instance
    """
    return Param(
        source="query",
        alias=alias,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        pattern=pattern,
        description=description,
        example=example,
        deprecated=deprecated,
    )


def Path(
    default: Any = ...,
    *,
    alias: Optional[str] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    description: Optional[str] = None,
    example: Any = None,
    deprecated: bool = False,
) -> Any:
    """
    Mark parameter as path parameter.

    Args:
        default: Must be ... (path params are always required)
        alias: Alternative parameter name
        gt: Value must be greater than this
        ge: Value must be greater than or equal to this
        lt: Value must be less than this
        le: Value must be less than or equal to this
        min_length: Minimum string length
        max_length: Maximum string length
        pattern: Regex pattern to match
        description: Parameter description
        example: Example value
        deprecated: Mark as deprecated

    Returns:
        Param marker instance
    """
    if default is not ...:
        raise ValueError("Path parameters cannot have default values")

    return Param(
        source="path",
        alias=alias,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        pattern=pattern,
        description=description,
        example=example,
        deprecated=deprecated,
    )


def Body(
    default: Any = ...,
    *,
    alias: Optional[str] = None,
    embed: bool = False,
    description: Optional[str] = None,
    example: Any = None,
) -> Any:
    """
    Mark parameter as request body.

    Args:
        default: Default value (... for required)
        alias: Alternative parameter name
        embed: Whether to wrap in {<alias>: <value>}
        description: Parameter description
        example: Example value

    Returns:
        Param marker instance
    """
    return Param(
        source="body",
        alias=alias,
        embed=embed,
        description=description,
        example=example,
    )


def Header(
    default: Any = ...,
    *,
    alias: Optional[str] = None,
    description: Optional[str] = None,
    example: Any = None,
    deprecated: bool = False,
) -> Any:
    """
    Mark parameter as HTTP header.

    Args:
        default: Default value (... for required)
        alias: Alternative header name
        description: Parameter description
        example: Example value
        deprecated: Mark as deprecated

    Returns:
        Param marker instance
    """
    return Param(
        source="header",
        alias=alias,
        description=description,
        example=example,
        deprecated=deprecated,
    )


def Cookie(
    default: Any = ...,
    *,
    alias: Optional[str] = None,
    description: Optional[str] = None,
    example: Any = None,
    deprecated: bool = False,
) -> Any:
    """
    Mark parameter as cookie value.

    Args:
        default: Default value (... for required)
        alias: Alternative cookie name
        description: Parameter description
        example: Example value
        deprecated: Mark as deprecated

    Returns:
        Param marker instance
    """
    return Param(
        source="cookie",
        alias=alias,
        description=description,
        example=example,
        deprecated=deprecated,
    )


def Form(
    default: Any = ...,
    *,
    alias: Optional[str] = None,
    description: Optional[str] = None,
    example: Any = None,
) -> Any:
    """
    Mark parameter as form data field.

    Args:
        default: Default value (... for required)
        alias: Alternative form field name
        description: Parameter description
        example: Example value

    Returns:
        Param marker instance
    """
    return Param(
        source="form",
        alias=alias,
        description=description,
        example=example,
    )


def File(
    default: Any = ...,
    *,
    alias: Optional[str] = None,
    description: Optional[str] = None,
) -> Any:
    """
    Mark parameter as file upload.

    Args:
        default: Default value (... for required)
        alias: Alternative form field name
        description: Parameter description

    Returns:
        Param marker instance
    """
    return Param(
        source="file",
        alias=alias,
        description=description,
    )


@dataclass(frozen=True)
class Depends:
    """
    Dependency injection marker.

    Marks a parameter as a dependency that will be resolved
    by calling the specified function.
    """

    dependency: Optional[Callable[..., Any]] = None
    """Function to call for dependency resolution"""

    use_cache: bool = True
    """Whether to cache the dependency result per request"""

"""
Runtime validation for parameter constraints.

Provides performant validation for numeric constraints (gt, ge, lt, le),
string constraints (min_length, max_length, pattern), and other validators.
"""
from __future__ import annotations

import re
from typing import Any, Optional, Pattern
from .exceptions import HTTPException

__all__ = [
    "ValidationError",
    "validate_constraints",
    "validate_numeric_constraints",
    "validate_string_constraints",
    "validate_pattern",
]


class ValidationError(HTTPException):
    """Validation error with 422 status code."""

    def __init__(self, field: str, message: str):
        # Format detail as a string for consistent error handling
        detail_str = f"Validation error for '{field}': {message}"
        super().__init__(
            status_code=422,
            detail=detail_str
        )
        self.field = field
        self.message = message


def validate_numeric_constraints(
    value: Any,
    field_name: str,
    *,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
) -> None:
    """
    Validate numeric constraints.

    Args:
        value: Value to validate (must be numeric)
        field_name: Name of the field (for error messages)
        gt: Greater than (exclusive minimum)
        ge: Greater than or equal (inclusive minimum)
        lt: Less than (exclusive maximum)
        le: Less than or equal (inclusive maximum)
        multiple_of: Value must be multiple of this number

    Raises:
        ValidationError: If validation fails
    """
    # Only validate if value is numeric
    if not isinstance(value, (int, float)):
        return

    if gt is not None and value <= gt:
        raise ValidationError(
            field_name,
            f"Value must be greater than {gt}, got {value}"
        )

    if ge is not None and value < ge:
        raise ValidationError(
            field_name,
            f"Value must be greater than or equal to {ge}, got {value}"
        )

    if lt is not None and value >= lt:
        raise ValidationError(
            field_name,
            f"Value must be less than {lt}, got {value}"
        )

    if le is not None and value > le:
        raise ValidationError(
            field_name,
            f"Value must be less than or equal to {le}, got {value}"
        )

    if multiple_of is not None:
        if value % multiple_of != 0:
            raise ValidationError(
                field_name,
                f"Value must be a multiple of {multiple_of}, got {value}"
            )


def validate_string_constraints(
    value: Any,
    field_name: str,
    *,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
) -> None:
    """
    Validate string/collection length constraints.

    Args:
        value: Value to validate (string or collection)
        field_name: Name of the field (for error messages)
        min_length: Minimum length
        max_length: Maximum length

    Raises:
        ValidationError: If validation fails
    """
    # Get length - works for strings, lists, tuples, etc.
    try:
        length = len(value)
    except TypeError:
        # Value doesn't have a length (e.g., int, float)
        return

    if min_length is not None and length < min_length:
        raise ValidationError(
            field_name,
            f"Length must be at least {min_length}, got {length}"
        )

    if max_length is not None and length > max_length:
        raise ValidationError(
            field_name,
            f"Length must be at most {max_length}, got {length}"
        )


def validate_pattern(
    value: Any,
    field_name: str,
    pattern: str,
    compiled_pattern: Optional[Pattern] = None,
) -> None:
    """
    Validate string against regex pattern.

    Args:
        value: Value to validate (must be string)
        field_name: Name of the field (for error messages)
        pattern: Regex pattern string
        compiled_pattern: Pre-compiled pattern for performance

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        return

    # Use pre-compiled pattern if available, otherwise compile on the fly
    regex = compiled_pattern if compiled_pattern else re.compile(pattern)

    if not regex.match(value):
        raise ValidationError(
            field_name,
            f"Value does not match pattern '{pattern}'"
        )


def validate_constraints(
    value: Any,
    field_name: str,
    *,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    compiled_pattern: Optional[Pattern] = None,
) -> None:
    """
    Validate value against all applicable constraints.

    This is the main entry point for constraint validation.
    It intelligently applies only relevant validators based on value type.

    Args:
        value: Value to validate
        field_name: Name of the field (for error messages)
        gt: Greater than (exclusive minimum)
        ge: Greater than or equal (inclusive minimum)
        lt: Less than (exclusive maximum)
        le: Less than or equal (inclusive maximum)
        multiple_of: Value must be multiple of this number
        min_length: Minimum string/collection length
        max_length: Maximum string/collection length
        pattern: Regex pattern for string validation
        compiled_pattern: Pre-compiled regex pattern

    Raises:
        ValidationError: If any validation fails
    """
    # Numeric constraints
    if any(c is not None for c in [gt, ge, lt, le, multiple_of]):
        validate_numeric_constraints(
            value, field_name,
            gt=gt, ge=ge, lt=lt, le=le, multiple_of=multiple_of
        )

    # String/collection length constraints
    if min_length is not None or max_length is not None:
        validate_string_constraints(
            value, field_name,
            min_length=min_length, max_length=max_length
        )

    # Pattern validation
    if pattern is not None:
        validate_pattern(value, field_name, pattern, compiled_pattern)

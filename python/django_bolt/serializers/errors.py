from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldError:
    """A single validation error for a field."""

    message: str
    """Human-readable error message."""

    code: str = "invalid"
    """Machine-readable error code for programmatic handling."""

    params: dict[str, Any] = field(default_factory=dict)
    """Additional parameters for error message formatting."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        result = {"message": self.message, "code": self.code}
        if self.params:
            result["params"] = self.params
        return result


@dataclass
class ValidationError(Exception):
    """
    Structured validation error with field paths and multiple errors.

    This exception provides a DRF-compatible error format that includes:
    - Field-level errors with path tracking (e.g., "author.email")
    - Multiple errors per field
    - Error codes for programmatic handling
    - Rich error context

    Example:
        raise ValidationError(
            errors={
                "email": [FieldError("Invalid email format", code="invalid_email")],
                "author.name": [FieldError("Name is required", code="required")],
            }
        )

    Produces:
        {
            "detail": "Validation error",
            "errors": {
                "email": [{"message": "Invalid email format", "code": "invalid_email"}],
                "author.name": [{"message": "Name is required", "code": "required"}]
            }
        }
    """

    errors: dict[str, list[FieldError]] = field(default_factory=dict)
    """Dict mapping field paths to lists of errors."""

    detail: str = "Validation error"
    """Top-level error message."""

    def __post_init__(self):
        # Ensure errors is a dict
        if self.errors is None:
            self.errors = {}

    def __str__(self) -> str:
        """Return a string representation of the errors."""
        if not self.errors:
            return self.detail

        parts = []
        for field_path, field_errors in self.errors.items():
            for err in field_errors:
                parts.append(f"{field_path}: {err.message}")

        return "; ".join(parts) if parts else self.detail

    def add_error(self, field_path: str, message: str, code: str = "invalid", **params: Any) -> None:
        """
        Add an error for a field.

        Args:
            field_path: Dot-notation path to the field (e.g., "author.email")
            message: Human-readable error message
            code: Machine-readable error code
            **params: Additional parameters for the error
        """
        if field_path not in self.errors:
            self.errors[field_path] = []

        self.errors[field_path].append(FieldError(message=message, code=code, params=params))

    def add_field_errors(self, field_path: str, errors: list[FieldError]) -> None:
        """
        Add multiple errors for a field.

        Args:
            field_path: Dot-notation path to the field
            errors: List of FieldError objects
        """
        if field_path not in self.errors:
            self.errors[field_path] = []

        self.errors[field_path].extend(errors)

    def merge(self, other: ValidationError, prefix: str = "") -> None:
        """
        Merge errors from another ValidationError.

        Args:
            other: Another ValidationError to merge
            prefix: Optional prefix to add to field paths (for nesting)
        """
        for field_path, field_errors in other.errors.items():
            full_path = f"{prefix}.{field_path}" if prefix else field_path
            self.add_field_errors(full_path, field_errors)

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return bool(self.errors)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to DRF-compatible dictionary format.

        Returns:
            Dict with 'detail' and 'errors' keys
        """
        return {
            "detail": self.detail,
            "errors": {
                field_path: [err.to_dict() for err in field_errors]
                for field_path, field_errors in self.errors.items()
            },
        }

    def to_flat_dict(self) -> dict[str, list[str]]:
        """
        Convert to a flat dictionary format (just field -> messages).

        Returns:
            Dict mapping field paths to lists of error messages
        """
        return {
            field_path: [err.message for err in field_errors]
            for field_path, field_errors in self.errors.items()
        }

    def to_list(self) -> list[dict[str, Any]]:
        """
        Convert to a list of error objects.

        Returns:
            List of dicts with 'field' and 'errors' keys
        """
        return [
            {
                "field": field_path,
                "errors": [err.to_dict() for err in field_errors],
            }
            for field_path, field_errors in self.errors.items()
        ]


class ErrorCollector:
    """
    Collect multiple validation errors before raising.

    Use this to collect all validation errors instead of failing on the first one.

    Example:
        collector = ErrorCollector()

        if not email:
            collector.add_error("email", "Email is required", code="required")

        if password and len(password) < 8:
            collector.add_error("password", "Password must be at least 8 characters", code="min_length")

        collector.raise_if_errors()
    """

    def __init__(self):
        self._errors: dict[str, list[FieldError]] = {}

    def add_error(self, field_path: str, message: str, code: str = "invalid", **params: Any) -> None:
        """
        Add an error for a field.

        Args:
            field_path: Dot-notation path to the field
            message: Human-readable error message
            code: Machine-readable error code
            **params: Additional parameters
        """
        if field_path not in self._errors:
            self._errors[field_path] = []

        self._errors[field_path].append(FieldError(message=message, code=code, params=params))

    def add_validation_error(self, field_path: str, error: ValueError | Exception) -> None:
        """
        Add an error from a ValueError or other exception.

        Args:
            field_path: Dot-notation path to the field
            error: The exception that was raised
        """
        self.add_error(field_path, str(error))

    def merge(self, other: ValidationError | ErrorCollector, prefix: str = "") -> None:
        """
        Merge errors from another ValidationError or ErrorCollector.

        Args:
            other: ValidationError or ErrorCollector to merge
            prefix: Optional prefix for field paths
        """
        errors = other.errors if isinstance(other, ValidationError) else other._errors

        for field_path, field_errors in errors.items():
            full_path = f"{prefix}.{field_path}" if prefix else field_path
            if full_path not in self._errors:
                self._errors[full_path] = []
            self._errors[full_path].extend(field_errors)

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return bool(self._errors)

    @property
    def errors(self) -> dict[str, list[FieldError]]:
        """Get the collected errors."""
        return self._errors

    def raise_if_errors(self, detail: str = "Validation error") -> None:
        """
        Raise ValidationError if there are any errors.

        Args:
            detail: Top-level error message

        Raises:
            ValidationError: If any errors were collected
        """
        if self._errors:
            raise ValidationError(errors=dict(self._errors), detail=detail)

    def to_validation_error(self, detail: str = "Validation error") -> ValidationError:
        """
        Convert to a ValidationError.

        Args:
            detail: Top-level error message

        Returns:
            ValidationError with collected errors
        """
        return ValidationError(errors=self._errors, detail=detail)


def format_field_path(*parts: str) -> str:
    """
    Format a field path from parts.

    Args:
        *parts: Path components

    Returns:
        Dot-notation path string

    Example:
        format_field_path("author", "address", "city")
        # Returns: "author.address.city"
    """
    return ".".join(p for p in parts if p)


def parse_field_path(path: str) -> list[str]:
    """
    Parse a field path into components.

    Args:
        path: Dot-notation path string

    Returns:
        List of path components

    Example:
        parse_field_path("author.address.city")
        # Returns: ["author", "address", "city"]
    """
    return path.split(".") if path else []


# Export all
__all__ = [
    "FieldError",
    "ValidationError",
    "ErrorCollector",
    "format_field_path",
    "parse_field_path",
]

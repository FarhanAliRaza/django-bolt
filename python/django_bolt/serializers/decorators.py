"""Validation decorators for Serializer classes."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, TypeVar, get_type_hints

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .base import Serializer

T = TypeVar("T")

# Marker attributes for storing validators on classes
FIELD_VALIDATORS_ATTR = "__field_validators__"
MODEL_VALIDATORS_ATTR = "__model_validators__"
COMPUTED_FIELDS_ATTR = "__computed_fields__"


@dataclass(frozen=True, slots=True)
class ComputedFieldConfig:
    """Configuration for a computed field."""

    method_name: str
    """Name of the method that computes the value."""

    return_type: Any
    """Return type of the computed field."""

    description: str | None = None
    """Description for OpenAPI documentation."""

    alias: str | None = None
    """Alternative name for this field in JSON output."""

    deprecated: bool = False
    """Mark this field as deprecated."""

    include_in_schema: bool = True
    """Whether to include this field in OpenAPI schema."""


def computed_field(
    func: Callable[[Any], Any] | None = None,
    *,
    alias: str | None = None,
    description: str | None = None,
    deprecated: bool = False,
    include_in_schema: bool = True,
) -> Any:
    """
    Mark a method as a computed field for serialization output.

    Computed fields are calculated during serialization (dump) and are NOT
    stored as struct fields. They are similar to DRF's SerializerMethodField
    or Pydantic's @computed_field.

    Args:
        func: The method to use for computing the value (if used without parentheses)
        alias: Alternative name for this field in JSON output.
        description: Description for OpenAPI documentation.
        deprecated: Mark this field as deprecated.
        include_in_schema: Whether to include this field in OpenAPI schema.

    Returns:
        The decorated method with computed field metadata.

    Example:
        class UserSerializer(Serializer):
            first_name: str
            last_name: str

            @computed_field
            def full_name(self) -> str:
                return f"{self.first_name} {self.last_name}"

            @computed_field(alias="displayName")
            def display_name(self) -> str:
                return self.full_name.upper()

        # When dumped:
        # {"first_name": "John", "last_name": "Doe", "full_name": "John Doe", "display_name": "JOHN DOE"}

    Note:
        - Computed fields are OUTPUT ONLY - they don't exist during parsing/loading
        - They are calculated fresh on each dump() call
        - They can access other struct fields and computed fields
        - Method name becomes the field name (unless alias is specified)
    """

    def decorator(method: Callable[[Any], Any]) -> Callable[[Any], Any]:
        # Try to get return type from method annotations
        return_type = Any
        try:
            hints = get_type_hints(method)
            return_type = hints.get("return", Any)
        except Exception as e:
            logger.debug(
                "Failed to get return type hints for computed field method %s. "
                "Using Any as return type. Error: %s",
                method.__name__ if hasattr(method, '__name__') else str(method),
                e
            )

        # Store computed field metadata on the method
        method.__computed_field__ = ComputedFieldConfig(
            method_name=method.__name__,
            return_type=return_type,
            description=description,
            alias=alias,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
        )
        return method

    if func is None:
        # Called with parentheses: @computed_field() or @computed_field(alias="...")
        return decorator
    else:
        # Called without parentheses: @computed_field
        return decorator(func)


def field_validator(
    field_name: str,
    mode: Literal["before", "after"] = "after",
) -> Callable[[Callable[[type[Serializer], Any], Any]], Callable[[type[Serializer], Any], Any]]:
    """
    Decorator to validate a specific field in a Serializer.

    Args:
        field_name: Name of the field to validate
        mode: When to run the validator ('before' or 'after' other validators)

    Example:
        class UserCreate(Serializer):
            email: str

            @field_validator('email')
            def validate_email(cls, value):
                if '@' not in value:
                    raise ValueError('Invalid email')
                return value.lower()
    """

    def decorator(
        func: Callable[[type[Serializer], Any], Any],
    ) -> Callable[[type[Serializer], Any], Any]:
        # Store validator metadata on the function
        func.__validator_field__ = field_name
        func.__validator_mode__ = mode
        return func

    return decorator


def model_validator(
    func: Callable[[Serializer], Serializer] | None = None,
    mode: Literal["before", "after"] = "after",
) -> Callable[[Callable[[Serializer], Serializer]], Callable[[Serializer], Serializer]]:
    """
    Decorator to validate an entire Serializer after all fields are set.

    Args:
        func: The validator function (if used without parentheses)
        mode: When to run the validator ('before' or 'after' field validators)

    Example:
        class UserCreate(Serializer):
            password: str
            password_confirm: str

            @model_validator
            def validate_passwords(self):
                if self.password != self.password_confirm:
                    raise ValueError('Passwords must match')
    """

    def decorator(
        validator_func: Callable[[Serializer], Serializer],
    ) -> Callable[[Serializer], Serializer]:
        # Store validator metadata on the function
        validator_func.__model_validator__ = True
        validator_func.__validator_mode__ = mode
        return validator_func

    if func is None:
        # Called with parentheses: @model_validator()
        return decorator
    else:
        # Called without parentheses: @model_validator
        func.__model_validator__ = True
        func.__validator_mode__ = mode
        return func


def collect_field_validators(cls: type[Serializer]) -> dict[str, list[Callable[[Any], Any]]]:
    """
    Collect all field validators from a class and its bases.

    Returns a dict mapping field names to lists of validator functions.
    """
    validators: dict[str, list[Callable[[Any], Any]]] = {}

    # Walk through MRO to collect validators
    for base in cls.__mro__:
        if not hasattr(base, "__dict__"):
            continue

        for _name, value in base.__dict__.items():
            if callable(value) and hasattr(value, "__validator_field__"):
                field_name = value.__validator_field__
                if field_name not in validators:
                    validators[field_name] = []
                validators[field_name].append(value)

    return validators


def collect_model_validators(cls: type[Serializer]) -> list[Callable[[Serializer], Serializer]]:
    """
    Collect all model validators from a class and its bases.

    Returns a list of validator functions in MRO order.
    """
    validators: list[Callable[[Serializer], Serializer]] = []

    # Walk through MRO to collect validators
    for base in cls.__mro__:
        if not hasattr(base, "__dict__"):
            continue

        for _name, value in base.__dict__.items():
            if callable(value) and hasattr(value, "__model_validator__"):
                validators.append(value)

    return validators


def collect_computed_fields(cls: type[Serializer]) -> dict[str, ComputedFieldConfig]:
    """
    Collect all computed fields from a class and its bases.

    Returns a dict mapping field names to their ComputedFieldConfig.
    """
    computed: dict[str, ComputedFieldConfig] = {}

    # Walk through MRO to collect computed fields (reverse order so subclass overrides parent)
    for base in reversed(cls.__mro__):
        if not hasattr(base, "__dict__"):
            continue

        for _name, value in base.__dict__.items():
            if callable(value) and hasattr(value, "__computed_field__"):
                config: ComputedFieldConfig = value.__computed_field__
                # Use alias if provided, otherwise use method name
                field_name = config.alias or config.method_name
                computed[field_name] = config

    return computed

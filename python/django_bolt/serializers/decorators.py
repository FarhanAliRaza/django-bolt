"""Validation decorators for Serializer classes."""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any, Callable, Literal, TypeVar

if TYPE_CHECKING:
    from .base import Serializer

T = TypeVar("T")

# Marker attributes for storing validators on classes
FIELD_VALIDATORS_ATTR = "__field_validators__"
MODEL_VALIDATORS_ATTR = "__model_validators__"


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

        for name, value in base.__dict__.items():
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

        for name, value in base.__dict__.items():
            if callable(value) and hasattr(value, "__model_validator__"):
                validators.append(value)

    return validators

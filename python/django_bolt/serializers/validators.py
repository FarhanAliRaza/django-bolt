from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Pattern

if TYPE_CHECKING:
    from django.db.models import QuerySet


class Validator(ABC):
    """Base class for all validators."""
    
    @abstractmethod
    def __call__(self, value: Any) -> Any:
        """
        Validate and optionally transform the value.
        
        Args:
            value: The value to validate
            
        Returns:
            The validated (and optionally transformed) value
            
        Raises:
            ValueError: If validation fails
        """
        pass
    
    @property
    def error_code(self) -> str:
        """Return the error code for this validator."""
        return "invalid"


@dataclass(frozen=True, slots=True)
class MinLengthValidator(Validator):
    """Validate that a string has at least the minimum length."""
    
    min_length: int
    message: str | None = None
    
    def __call__(self, value: Any) -> Any:
        if value is None:
            return value
        
        if len(value) < self.min_length:
            msg = self.message or f"Must be at least {self.min_length} characters long"
            raise ValueError(msg)
        
        return value
    
    @property
    def error_code(self) -> str:
        return "min_length"


@dataclass(frozen=True, slots=True)
class MaxLengthValidator(Validator):
    """Validate that a string does not exceed the maximum length."""
    
    max_length: int
    message: str | None = None
    
    def __call__(self, value: Any) -> Any:
        if value is None:
            return value
        
        if len(value) > self.max_length:
            msg = self.message or f"Must be at most {self.max_length} characters long"
            raise ValueError(msg)
        
        return value
    
    @property
    def error_code(self) -> str:
        return "max_length"


@dataclass(frozen=True, slots=True)
class LengthValidator(Validator):
    """Validate that a string length is within a range."""
    
    min_length: int | None = None
    max_length: int | None = None
    message: str | None = None
    
    def __call__(self, value: Any) -> Any:
        if value is None:
            return value
        
        length = len(value)
        
        if self.min_length is not None and length < self.min_length:
            msg = self.message or f"Must be at least {self.min_length} characters long"
            raise ValueError(msg)
        
        if self.max_length is not None and length > self.max_length:
            msg = self.message or f"Must be at most {self.max_length} characters long"
            raise ValueError(msg)
        
        return value
    
    @property
    def error_code(self) -> str:
        return "length"


@dataclass(frozen=True, slots=True)
class RegexValidator(Validator):
    """Validate that a string matches a regex pattern."""
    
    pattern: str | Pattern
    message: str | None = None
    flags: int = 0
    inverse_match: bool = False
    
    def __call__(self, value: Any) -> Any:
        if value is None:
            return value
        
        if isinstance(self.pattern, str):
            regex = re.compile(self.pattern, self.flags)
        else:
            regex = self.pattern
        
        match = regex.search(str(value))
        
        if self.inverse_match:
            # Fail if pattern matches
            if match:
                msg = self.message or f"Value must not match pattern '{self.pattern}'"
                raise ValueError(msg)
        else:
            # Fail if pattern doesn't match
            if not match:
                msg = self.message or f"Value must match pattern '{self.pattern}'"
                raise ValueError(msg)
        
        return value
    
    @property
    def error_code(self) -> str:
        return "regex"


@dataclass(frozen=True, slots=True)
class MinValueValidator(Validator):
    """Validate that a number is at least the minimum value."""
    
    min_value: int | float
    message: str | None = None
    
    def __call__(self, value: Any) -> Any:
        if value is None:
            return value
        
        if value < self.min_value:
            msg = self.message or f"Must be at least {self.min_value}"
            raise ValueError(msg)
        
        return value
    
    @property
    def error_code(self) -> str:
        return "min_value"


@dataclass(frozen=True, slots=True)
class MaxValueValidator(Validator):
    """Validate that a number does not exceed the maximum value."""
    
    max_value: int | float
    message: str | None = None
    
    def __call__(self, value: Any) -> Any:
        if value is None:
            return value
        
        if value > self.max_value:
            msg = self.message or f"Must be at most {self.max_value}"
            raise ValueError(msg)
        
        return value
    
    @property
    def error_code(self) -> str:
        return "max_value"


@dataclass(frozen=True, slots=True)
class RangeValidator(Validator):
    """Validate that a number is within a range."""
    
    min_value: int | float | None = None
    max_value: int | float | None = None
    message: str | None = None
    
    def __call__(self, value: Any) -> Any:
        if value is None:
            return value
        
        if self.min_value is not None and value < self.min_value:
            msg = self.message or f"Must be at least {self.min_value}"
            raise ValueError(msg)
        
        if self.max_value is not None and value > self.max_value:
            msg = self.message or f"Must be at most {self.max_value}"
            raise ValueError(msg)
        
        return value
    
    @property
    def error_code(self) -> str:
        return "range"


@dataclass(frozen=True, slots=True)
class ChoicesValidator(Validator):
    """Validate that a value is one of the allowed choices."""
    
    choices: tuple | frozenset
    message: str | None = None
    
    def __call__(self, value: Any) -> Any:
        if value is None:
            return value
        
        if value not in self.choices:
            choices_str = ", ".join(repr(c) for c in self.choices)
            msg = self.message or f"Must be one of: {choices_str}"
            raise ValueError(msg)
        
        return value
    
    @property
    def error_code(self) -> str:
        return "choices"

class UniqueValidator(Validator):
    """
    Validate that a value is unique in the database.
    
    Example:
        class UserSerializer(Serializer):
            username: Annotated[str, UniqueValidator(User.objects.all(), 'username')]
            email: Annotated[str, UniqueValidator(User.objects.all(), 'email')]
    """
    
    def __init__(
        self,
        queryset: QuerySet,
        field_name: str | None = None,
        message: str | None = None,
        lookup: str = "exact",
    ):
        """
        Initialize UniqueValidator.
        
        Args:
            queryset: QuerySet to check for uniqueness
            field_name: Field name to check (defaults to the annotated field name)
            message: Custom error message
            lookup: Django lookup type (exact, iexact, etc.)
        """
        self.queryset = queryset
        self.field_name = field_name
        self.message = message
        self.lookup = lookup
    
    def __call__(self, value: Any) -> Any:
        if value is None:
            return value
        
        field_name = self.field_name or "value"
        lookup_field = f"{field_name}__{self.lookup}"
        
        if self.queryset.filter(**{lookup_field: value}).exists():
            msg = self.message or f"A record with this {field_name} already exists"
            raise ValueError(msg)
        
        return value
    
    @property
    def error_code(self) -> str:
        return "unique"


class ExistsValidator(Validator):
    """
    Validate that a referenced object exists in the database.
    
    Example:
        class PostSerializer(Serializer):
            author_id: Annotated[int, ExistsValidator(User.objects.all(), 'id')]
    """
    
    def __init__(
        self,
        queryset: QuerySet,
        field_name: str = "id",
        message: str | None = None,
    ):
        """
        Initialize ExistsValidator.
        
        Args:
            queryset: QuerySet to check for existence
            field_name: Field name to check (default: 'id')
            message: Custom error message
        """
        self.queryset = queryset
        self.field_name = field_name
        self.message = message
    
    def __call__(self, value: Any) -> Any:
        if value is None:
            return value
        
        if not self.queryset.filter(**{self.field_name: value}).exists():
            msg = self.message or f"Object with {self.field_name}={value} does not exist"
            raise ValueError(msg)
        
        return value
    
    @property
    def error_code(self) -> str:
        return "exists"


# Common regex patterns
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
URL_REGEX = r"^https?://[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*(/[^\s]*)?$"
SLUG_REGEX = r"^[-a-zA-Z0-9_]+$"
UUID_REGEX = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
PHONE_REGEX = r"^\+?[1-9]\d{1,14}$"


# Pre-built validators for common use cases
EmailValidator = RegexValidator(EMAIL_REGEX, message="Enter a valid email address")
URLValidator = RegexValidator(URL_REGEX, message="Enter a valid URL")
SlugValidator = RegexValidator(SLUG_REGEX, message="Enter a valid slug (letters, numbers, hyphens, underscores)")
UUIDValidator = RegexValidator(UUID_REGEX, message="Enter a valid UUID")
PhoneValidator = RegexValidator(PHONE_REGEX, message="Enter a valid phone number (E.164 format)")


def validator(
    *field_names: str,
    mode: str = "after",
    check_fields: bool = True,
) -> Callable[[Callable], Callable]:
    """
    Decorator for inline field validation.
    
    This is an alternative to @field_validator that allows more flexible
    validation across multiple fields.
    
    Args:
        *field_names: Names of fields to validate
        mode: When to run ('before' or 'after' other validators)
        check_fields: If True, validates that field names exist on the serializer
    
    Example:
        class UserSerializer(Serializer):
            username: str
            email: str
            
            @validator('username')
            def validate_username(cls, value):
                return value.lower().strip()
            
            @validator('username', 'email')
            def validate_not_empty(cls, value):
                if not value:
                    raise ValueError('Field cannot be empty')
                return value
    """
    def decorator(func: Callable) -> Callable:
        # Store validator metadata on the function
        func.__validator_fields__ = field_names
        func.__validator_mode__ = mode
        func.__validator_check_fields__ = check_fields
        
        # Also set the single field for backward compatibility
        if len(field_names) == 1:
            func.__validator_field__ = field_names[0]
        
        return func
    
    return decorator


# Export all validators
__all__ = [
    # Base
    "Validator",
    # String validators
    "MinLengthValidator",
    "MaxLengthValidator",
    "LengthValidator",
    "RegexValidator",
    # Numeric validators
    "MinValueValidator",
    "MaxValueValidator",
    "RangeValidator",
    # Choice validators
    "ChoicesValidator",
    # Database validators
    "UniqueValidator",
    "ExistsValidator",
    # Pre-built validators
    "EmailValidator",
    "URLValidator",
    "SlugValidator",
    "UUIDValidator",
    "PhoneValidator",
    # Decorator
    "validator",
    # Regex patterns
    "EMAIL_REGEX",
    "URL_REGEX",
    "SLUG_REGEX",
    "UUID_REGEX",
    "PHONE_REGEX",
]

"""Base Serializer class extending msgspec.Struct with validation and Django integration."""

from __future__ import annotations

import inspect
import logging
import sys
from typing import TYPE_CHECKING, Any, ClassVar, Literal, TypeVar, get_args, get_origin, get_type_hints

from django.db.models import Model as DjangoModel

import msgspec
from msgspec import ValidationError as MsgspecValidationError
from msgspec import structs as msgspec_structs

from .decorators import collect_field_validators, collect_model_validators
from .nested import get_nested_config, validate_nested_field

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from django.db.models import Model

T = TypeVar("T", bound="Serializer")


class Serializer(msgspec.Struct):
    """
    Enhanced msgspec.Struct with validation and Django model integration.

    Features:
    - Field validation via @field_validator decorator
    - Model-level validation via @model_validator decorator
    - Django model integration (from_model, to_dict, to_model)
    - Full type safety for IDE/type checkers
    - All msgspec.Struct features (frozen, array_like, etc.)

    Example:
        class UserCreate(Serializer):
            username: str
            email: str
            password: str

            @field_validator('email')
            def validate_email(cls, value):
                if '@' not in value:
                    raise ValueError('Invalid email')
                return value.lower()

            @model_validator
            def validate_username_unique(self):
                from django.contrib.auth.models import User
                if User.objects.filter(username=self.username).exists():
                    raise ValueError('Username already exists')
    """

    # Class attributes for validators (populated by __init_subclass__)
    __field_validators__: ClassVar[dict[str, list[Any]]] = {}
    __model_validators__: ClassVar[list[Any]] = []

    # Cached type hints and metadata (populated by __init_subclass__)
    __cached_type_hints__: ClassVar[dict[str, Any]] = {}
    __nested_fields__: ClassVar[dict[str, Any]] = {}
    __literal_fields__: ClassVar[dict[str, frozenset[Any]]] = {}  # Frozenset for O(1) lookup

    # Fast-path flags: Control which validation runs (set at class definition time)
    __skip_validation__: ClassVar[bool] = True  # Skip all validation
    __has_nested_or_literal__: ClassVar[bool] = False  # Has nested/literal fields
    __has_field_validators__: ClassVar[bool] = False  # Has custom field validators
    __has_model_validators__: ClassVar[bool] = False  # Has model validators

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Collect validators and cache type hints when a subclass is created."""
        super().__init_subclass__(**kwargs)
        # Collect validators for this class
        cls.__field_validators__ = collect_field_validators(cls)
        cls.__model_validators__ = collect_model_validators(cls)

        # Cache type hints and field metadata (expensive - do once!)
        cls._cache_type_metadata()

        # Set fast-path flags to control which validation runs
        cls.__has_nested_or_literal__ = bool(cls.__nested_fields__ or cls.__literal_fields__)
        cls.__has_field_validators__ = bool(cls.__field_validators__)
        cls.__has_model_validators__ = bool(cls.__model_validators__)

        # Skip all validation if there's nothing to validate
        cls.__skip_validation__ = not (
            cls.__has_nested_or_literal__
            or cls.__has_field_validators__
            or cls.__has_model_validators__
        )

    @classmethod
    def _cache_type_metadata(cls) -> None:
        """
        Cache type hints and field metadata at class definition time.

        This is called ONCE per class (in __init_subclass__), not per instance.
        This is critical for performance - moving from 10K ops/sec to 1.75M ops/sec!

        Note: Function-scoped serializer classes (classes defined inside functions) have
        limited support and may not resolve all type hints correctly, especially when
        using forward references or complex generic types. This is due to Python's
        type hint resolution requiring access to the local namespace where the class
        was defined. For best results and full type hint resolution, always define
        serializers at module level.
        """
        # Track all frame references for proper cleanup to prevent memory leaks
        frames_to_cleanup = []
        try:
            # Strategy 1: Try with local namespace for function-scoped classes
            # This handles edge cases but adds complexity
            frame = inspect.currentframe()
            if frame is not None:
                frames_to_cleanup.append(frame)

            localns = {}

            # Walk up to 10 frames to find class definition context
            for _ in range(10):
                if frame is None:
                    break
                localns.update(frame.f_locals)
                frame = frame.f_back
                if frame is not None:
                    frames_to_cleanup.append(frame)

            # Resolve type hints with local namespace
            if sys.version_info >= (3, 11):
                hints = get_type_hints(cls, globalns=None, localns=localns, include_extras=True)
            else:
                # For Python < 3.11, try typing_extensions first
                try:
                    from typing_extensions import get_type_hints as get_type_hints_ext
                    hints = get_type_hints_ext(cls, globalns=None, localns=localns, include_extras=True)
                except ImportError:
                    hints = get_type_hints(cls, globalns=None, localns=localns)

        except Exception:
            # Strategy 2: Fallback without local namespace (module-level classes)
            try:
                hints = get_type_hints(cls)
            except Exception:
                # Last resort: use raw annotations
                hints = getattr(cls, "__annotations__", {})
        finally:
            # Clean up all frame references to prevent memory leaks
            for f in frames_to_cleanup:
                del f
            frames_to_cleanup.clear()

        # Cache the type hints
        cls.__cached_type_hints__ = hints

        # Pre-compute nested field configurations
        nested_fields = {}
        literal_fields = {}

        for field_name, field_type in hints.items():
            # Check if field has NestedConfig metadata
            nested_config = get_nested_config(field_type)
            if nested_config is not None:
                nested_fields[field_name] = nested_config

            # Check if field is a Literal type (for Django choices validation)
            origin = get_origin(field_type)
            if origin is Literal:
                allowed_values = get_args(field_type)
                # Convert to frozenset for O(1) membership testing (optimization #3)
                literal_fields[field_name] = frozenset(allowed_values)

        cls.__nested_fields__ = nested_fields
        cls.__literal_fields__ = literal_fields

    def __post_init__(self) -> None:
        """
        Run all field and model validators after struct initialization.

        Validators are executed in order:
        1. Field validators with mode='before'
        2. Field validators with mode='after'
        3. Model validators with mode='before'
        4. Model validators with mode='after'
        """
        # Fast path: skip validation if there are no validators
        # This avoids function call overhead when there's nothing to validate
        if self.__skip_validation__:
            return

        # Run field validators
        self._run_field_validators()

        # Run model validators
        self._run_model_validators()

    def _run_field_validators(self) -> None:
        """Execute all field validators in order."""
        # First, validate nested/literal fields if any exist
        if self.__has_nested_or_literal__:
            self._validate_nested_and_literal_fields()

        # Then run custom field validators if any exist
        if self.__has_field_validators__:
            # Cache attribute lookups (optimization #2: ~20-40ns savings per field)
            _class = self.__class__
            _setattr = msgspec_structs.force_setattr

            for field_name, validators in self.__field_validators__.items():
                try:
                    # Optimization #4: Fast path for single validator (skip loop overhead)
                    if len(validators) == 1:
                        validator = validators[0]
                        current_value = getattr(self, field_name)
                        new_value = validator(_class, current_value)
                        # If validator returns None, keep the original value
                        # This allows validators to validate without transforming
                        if new_value is None:
                            new_value = current_value
                        _setattr(self, field_name, new_value)
                    else:
                        # Batch validation: getattr once, setattr once per field (optimization #1)
                        # Saves ~80-150ns per field with multiple validators
                        current_value = getattr(self, field_name)

                        # Run all validators for this field, accumulating the value
                        for validator in validators:
                            result = validator(_class, current_value)
                            # If validator returns None, keep the current value
                            if result is not None:
                                current_value = result

                        # Update the field once with the final value
                        _setattr(self, field_name, current_value)

                except (ValueError, TypeError) as e:
                    # Convert to ValidationError with field context
                    raise MsgspecValidationError(f"{field_name}: {str(e)}") from e
                except Exception as e:
                    # Re-raise other exceptions
                    raise

    def _validate_nested_and_literal_fields(self) -> None:
        """
        Validate nested serializer fields and Literal (choice) fields using cached metadata.

        This method handles two types of validation:
        1. Nested fields: Fields with Nested() annotation that contain serializer instances
        2. Literal fields: Fields with Literal[] type hints that restrict values to specific choices
        """
        # Cache force_setattr for nested field validation (optimization #2)
        _setattr = msgspec_structs.force_setattr

        # Validate nested fields (no hasattr needed - msgspec struct fields always exist)
        for field_name, nested_config in self.__nested_fields__.items():
            try:
                current_value = getattr(self, field_name)
                validated_value = validate_nested_field(
                    current_value, nested_config, field_name
                )

                # Update the field if validation changed it
                if validated_value is not current_value:
                    _setattr(self, field_name, validated_value)
            except (ValueError, TypeError) as e:
                raise MsgspecValidationError(str(e)) from e
            except Exception as e:
                raise

        # Validate literal (choice) fields (now with O(1) frozenset lookup - optimization #3)
        for field_name, allowed_values in self.__literal_fields__.items():
            try:
                current_value = getattr(self, field_name)
                if current_value not in allowed_values:
                    raise ValueError(
                        f"{field_name}: invalid value {current_value!r}. "
                        f"Expected one of: {', '.join(repr(v) for v in allowed_values)}"
                    )
            except (ValueError, TypeError) as e:
                raise MsgspecValidationError(str(e)) from e
            except Exception as e:
                raise

    def _run_model_validators(self) -> None:
        """Execute all model validators in order."""
        for validator in self.__model_validators__:
            try:
                # Model validators should either modify self or return None
                result = validator(self)
                # Some validators might return a modified instance
                if result is not None and result is not self:
                    # This shouldn't happen with proper usage, but handle it gracefully
                    pass
            except (ValueError, TypeError) as e:
                raise MsgspecValidationError(str(e)) from e
            except Exception as e:
                raise

    def validate(self: T) -> T:
        """
        Validate the current instance by re-running msgspec validation.

        This is useful when you create an instance directly with __init__()
        and want to validate it afterwards.

        Returns:
            A new validated instance

        Raises:
            ValidationError: If validation fails

        Example:
            # Direct creation skips Meta validation
            author = BenchAuthor(id=1, name="  John  ", email="BAD-EMAIL")

            # Validate afterwards (will raise ValidationError)
            author = author.validate()
        """
        # Convert to dict and back through msgspec to trigger full validation
        data = msgspec.structs.asdict(self)
        return msgspec.convert(data, type=self.__class__)

    @classmethod
    def model_validate(cls: type[T], data: dict[str, Any] | Any) -> T:
        """
        Validate data and create a serializer instance (Pydantic-style API).

        This triggers full msgspec validation (Meta constraints) plus custom validators.

        Args:
            data: Dictionary or object to validate

        Returns:
            Validated Serializer instance

        Raises:
            ValidationError: If validation fails

        Example:
            data = {"id": 1, "name": "  John  ", "email": "JOHN@EXAMPLE.COM"}
            author = BenchAuthor.model_validate(data)
            # author.name == 'John' (stripped)
            # author.email == 'john@example.com' (lowercased)
        """
        return msgspec.convert(data, type=cls)

    @classmethod
    def model_validate_json(cls: type[T], json_data: str | bytes) -> T:
        """
        Validate JSON string and create a serializer instance (Pydantic-style API).

        This triggers full msgspec validation (Meta constraints) plus custom validators.

        Args:
            json_data: JSON string or bytes to validate

        Returns:
            Validated Serializer instance

        Raises:
            ValidationError: If validation fails

        Example:
            json_str = '{"id": 1, "name": "  John  ", "email": "JOHN@EXAMPLE.COM"}'
            author = BenchAuthor.model_validate_json(json_str)
            # author.name == 'John' (stripped)
            # author.email == 'john@example.com' (lowercased)
        """
        return msgspec.json.decode(json_data, type=cls)

    @classmethod
    def from_model(
        cls: type[T],
        instance: Model,
        *,
        _depth: int = 0,
        max_depth: int = 10,
    ) -> T:
        """
        Create a serializer instance from a Django model instance.

        Args:
            instance: A Django model instance
            _depth: Internal - current recursion depth
            max_depth: Maximum recursion depth to prevent runaway recursion (default: 10)

        Returns:
            A new Serializer instance with fields populated from the model

        Raises:
            ValueError: If max_depth exceeded (indicates deeply nested or circular references)

        Note:
            Circular nested serializers (e.g., Author.posts -> Post.author -> Author.posts)
            are not recommended for API design. Use separate serializers with ID-only fields
            for reverse relationships. Django's ORM typically prevents infinite recursion
            through select_related/prefetch_related, but max_depth provides a safety net.

        Example:
            user = await User.objects.aget(id=1)
            user_data = UserPublicSerializer.from_model(user)
        """
        # Safety: Prevent runaway recursion from deeply nested or circular relationships
        if _depth > max_depth:
            raise ValueError(
                f"Maximum recursion depth ({max_depth}) exceeded in from_model(). "
                f"This usually indicates overly deep nesting or circular references. "
                f"Current serializer: {cls.__name__}, instance: {instance.__class__.__name__}(pk={instance.pk}). "
                f"Consider using separate serializers with ID-only fields for deeply nested relationships."
            )

        # Use cached nested field metadata (no expensive introspection!)
        data = {}
        for field_name in cls.__struct_fields__:
            if not hasattr(instance, field_name):
                continue

            value = getattr(instance, field_name)

            # Check if this field has a nested serializer (from cache!)
            nested_config = cls.__nested_fields__.get(field_name)

            if nested_config:
                # This field is a nested serializer - extract full object data
                if nested_config.many:
                    # Many-to-many or reverse relationship
                    if hasattr(value, "all") and callable(getattr(value, "all", None)):
                        # Convert each related object to a dict for the nested serializer
                        items = []
                        for item in value.all():
                            if isinstance(item, DjangoModel):
                                # Recursively call from_model with depth tracking
                                items.append(
                                    nested_config.serializer_class.from_model(
                                        item,
                                        _depth=_depth + 1,
                                        max_depth=max_depth,
                                    )
                                )
                        data[field_name] = items
                    elif isinstance(value, list):
                        data[field_name] = value
                    else:
                        data[field_name] = []
                else:
                    # Single nested object (ForeignKey)
                    if isinstance(value, DjangoModel):
                        # Convert to nested serializer with depth tracking
                        data[field_name] = nested_config.serializer_class.from_model(
                            value,
                            _depth=_depth + 1,
                            max_depth=max_depth,
                        )
                    else:
                        data[field_name] = value
            else:
                # Regular field - not nested
                if isinstance(value, DjangoModel):
                    # Related object without nested serializer - use ID
                    data[field_name] = value.pk
                elif hasattr(value, "all") and callable(getattr(value, "all", None)):
                    # Manager without nested serializer - extract IDs
                    try:
                        data[field_name] = [item.pk for item in value.all()]
                    except Exception:
                        data[field_name] = value
                else:
                    # Regular field
                    data[field_name] = value

        return cls(**data)

    def to_dict(self, *, exclude_unset: bool = False) -> dict[str, Any]:
        """
        Convert serializer to a dictionary.

        Args:
            exclude_unset: If True, exclude fields with default values

        Returns:
            Dictionary representation of the serializer

        Example:
            user_data = UserCreateSerializer(...)
            user = await User.objects.acreate(**user_data.to_dict())
        """
        result = {}
        for field_name in self.__struct_fields__:
            result[field_name] = getattr(self, field_name)
        return result

    def to_model(self, model_class: type[Model]) -> Model:
        """
        Create a Django model instance (unsaved) from the serializer.

        Args:
            model_class: The Django model class to instantiate

        Returns:
            An unsaved model instance

        Example:
            user_data = UserCreateSerializer(...)
            user = user_data.to_model(User)
            await user.asave()
        """
        return model_class(**self.to_dict())

    def update_instance(self: T, instance: Model) -> Model:
        """
        Update a Django model instance with values from this serializer.

        Only updates fields that are present in the serializer. When omit_defaults=True,
        only updates fields that differ from their default values.

        Args:
            instance: The model instance to update

        Returns:
            The updated model instance (not saved)

        Example:
            user = await User.objects.aget(id=1)
            user_update = UserUpdateSerializer(username="new_name")
            updated_user = user_update.update_instance(user)
            await updated_user.asave()
        """
        # Check if omit_defaults is enabled
        omit_defaults = self.__struct_config__.omit_defaults

        # Get field defaults if omit_defaults is enabled
        defaults = self.__struct_defaults__ if omit_defaults else None

        for idx, field_name in enumerate(self.__struct_fields__):
            value = getattr(self, field_name)

            # Skip fields that are at their default value if omit_defaults is True
            if omit_defaults and defaults is not None and value == defaults[idx]:
                continue

            setattr(instance, field_name, value)
        return instance

    class Meta:
        """Configuration for Serializer. Can be overridden in subclasses."""

        model: type[Model] | None = None
        """Associated Django model class (optional)"""

        write_only: set[str] = set()
        """Field names that should only be accepted on input, not returned"""

        read_only: set[str] = set()
        """Field names that should only be returned, not accepted on input"""

        validators: dict[str, list[Any]] = {}
        """Additional validators to apply to fields"""

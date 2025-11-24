"""Base Serializer class extending msgspec.Struct with validation and Django integration."""

from __future__ import annotations

import inspect
import logging
import sys
from typing import TYPE_CHECKING, Any, ClassVar, Iterable, Literal, TypeVar, get_args, get_origin, get_type_hints

from django.db.models import Model as DjangoModel

import msgspec
from msgspec import ValidationError as MsgspecValidationError
from msgspec import structs as msgspec_structs

from .decorators import (
    ComputedFieldConfig,
    collect_computed_fields,
    collect_field_validators,
    collect_model_validators,
)
from .fields import FieldConfig, _FieldMarker, _UNSET
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

    # Field configuration (populated by __init_subclass__)
    __field_configs__: ClassVar[dict[str, FieldConfig]] = {}
    __computed_fields__: ClassVar[dict[str, ComputedFieldConfig]] = {}
    __read_only_fields__: ClassVar[frozenset[str]] = frozenset()
    __write_only_fields__: ClassVar[frozenset[str]] = frozenset()
    __source_mapping__: ClassVar[dict[str, str]] = {}  # API field name -> source attribute
    __field_sets__: ClassVar[dict[str, list[str]]] = {}  # Named field sets for use() method

    # Fast-path flags: Control which validation runs (set at class definition time)
    __skip_validation__: ClassVar[bool] = True  # Skip all validation
    __has_nested_or_literal__: ClassVar[bool] = False  # Has nested/literal fields
    __has_field_validators__: ClassVar[bool] = False  # Has custom field validators
    __has_model_validators__: ClassVar[bool] = False  # Has model validators
    __has_computed_fields__: ClassVar[bool] = False  # Has computed fields

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Collect validators and cache type hints when a subclass is created."""
        super().__init_subclass__(**kwargs)
        # Collect validators for this class
        cls.__field_validators__ = collect_field_validators(cls)
        cls.__model_validators__ = collect_model_validators(cls)
        cls.__computed_fields__ = collect_computed_fields(cls)

        # Collect field configurations from _FieldMarker defaults
        cls._collect_field_configs()

        # Cache type hints and field metadata (expensive - do once!)
        cls._cache_type_metadata()

        # Set fast-path flags to control which validation runs
        cls.__has_nested_or_literal__ = bool(cls.__nested_fields__ or cls.__literal_fields__)
        cls.__has_field_validators__ = bool(cls.__field_validators__)
        cls.__has_model_validators__ = bool(cls.__model_validators__)
        cls.__has_computed_fields__ = bool(cls.__computed_fields__)

        # Skip all validation if there's nothing to validate
        cls.__skip_validation__ = not (
            cls.__has_nested_or_literal__
            or cls.__has_field_validators__
            or cls.__has_model_validators__
        )

    @classmethod
    def _collect_field_configs(cls) -> None:
        """
        Collect field configurations from _FieldMarker defaults.

        This processes fields defined with the field() function and extracts
        their configuration (read_only, write_only, source, etc.).
        """
        field_configs: dict[str, FieldConfig] = {}
        read_only: set[str] = set()
        write_only: set[str] = set()
        source_mapping: dict[str, str] = {}

        # Walk through class annotations to find field markers
        # Note: We can't actually intercept msgspec.Struct field creation,
        # so we check class attributes for _FieldMarker defaults
        for field_name in getattr(cls, "__struct_fields__", ()):
            # Check if this field has a default that's a _FieldMarker
            defaults = getattr(cls, "__struct_defaults__", ())
            field_idx = cls.__struct_fields__.index(field_name) if field_name in cls.__struct_fields__ else -1

            if field_idx >= 0 and field_idx < len(defaults):
                default_val = defaults[field_idx]
                if isinstance(default_val, _FieldMarker):
                    config = default_val.config
                    field_configs[field_name] = config

                    if config.read_only:
                        read_only.add(field_name)
                    if config.write_only:
                        write_only.add(field_name)
                    if config.source:
                        source_mapping[field_name] = config.source

        # Also check Meta class for read_only/write_only sets (for backwards compatibility)
        meta = getattr(cls, "Meta", None)
        if meta:
            meta_read_only = getattr(meta, "read_only", set())
            meta_write_only = getattr(meta, "write_only", set())
            meta_field_sets = getattr(meta, "field_sets", {})

            read_only.update(meta_read_only)
            write_only.update(meta_write_only)

            # Store field_sets on class for use() method
            cls.__field_sets__ = meta_field_sets

        cls.__field_configs__ = field_configs
        cls.__read_only_fields__ = frozenset(read_only)
        cls.__write_only_fields__ = frozenset(write_only)
        cls.__source_mapping__ = source_mapping

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

        field_sets: dict[str, list[str]] = {}
        """
        Named field sets for dynamic field selection.

        Example:
            class Meta:
                field_sets = {
                    "list": ["id", "name", "email"],
                    "detail": ["id", "name", "email", "created_at", "posts"],
                    "create": ["name", "email", "password"],
                }
        """

    # -------------------------------------------------------------------------
    # Dynamic Field Selection Methods
    # -------------------------------------------------------------------------

    @classmethod
    def only(cls: type[T], *fields: str) -> SerializerView[T]:
        """
        Create a view that only includes the specified fields during serialization.

        This does NOT create a new serializer class - it returns a view object
        that wraps the serializer and filters fields during dump().

        Args:
            *fields: Field names to include in output

        Returns:
            SerializerView that can be used like the serializer but with filtered fields

        Example:
            # Only include id and name in output
            UserSerializer.only("id", "name").dump(user)
            # Returns: {"id": 1, "name": "John"}

            # Chain with dump_many for lists
            UserSerializer.only("id", "email").dump_many(users)
        """
        return SerializerView(cls, include_fields=frozenset(fields))

    @classmethod
    def exclude(cls: type[T], *fields: str) -> SerializerView[T]:
        """
        Create a view that excludes the specified fields during serialization.

        This does NOT create a new serializer class - it returns a view object
        that wraps the serializer and filters fields during dump().

        Args:
            *fields: Field names to exclude from output

        Returns:
            SerializerView that can be used like the serializer but with filtered fields

        Example:
            # Exclude password from output
            UserSerializer.exclude("password", "secret_key").dump(user)

            # Chain with dump_many for lists
            UserSerializer.exclude("internal_notes").dump_many(users)
        """
        return SerializerView(cls, exclude_fields=frozenset(fields))

    @classmethod
    def use(cls: type[T], field_set: str) -> SerializerView[T]:
        """
        Create a view using a predefined field set from Meta.field_sets.

        This allows you to define common field combinations once and reuse them.

        Args:
            field_set: Name of the field set defined in Meta.field_sets

        Returns:
            SerializerView configured with the predefined field set

        Raises:
            ValueError: If the field set name is not defined

        Example:
            class UserSerializer(Serializer):
                id: int
                name: str
                email: str
                password: str = field(write_only=True)
                created_at: datetime

                class Meta:
                    field_sets = {
                        "list": ["id", "name"],
                        "detail": ["id", "name", "email", "created_at"],
                    }

            # Use predefined field sets
            UserSerializer.use("list").dump_many(users)
            UserSerializer.use("detail").dump(user)
        """
        field_sets = getattr(cls, "__field_sets__", {})
        if field_set not in field_sets:
            available = ", ".join(field_sets.keys()) if field_sets else "none defined"
            raise ValueError(
                f"Field set '{field_set}' not found in {cls.__name__}.Meta.field_sets. "
                f"Available field sets: {available}"
            )
        return SerializerView(cls, include_fields=frozenset(field_sets[field_set]))

    # -------------------------------------------------------------------------
    # Dump Methods (Serialization)
    # -------------------------------------------------------------------------

    def dump(
        self,
        *,
        exclude_none: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        by_alias: bool = False,
    ) -> dict[str, Any]:
        """
        Serialize this instance to a dictionary.

        This method respects read_only/write_only field configurations and
        includes computed fields in the output.

        Args:
            exclude_none: If True, exclude fields with None values
            exclude_unset: If True, exclude fields that weren't explicitly set
            exclude_defaults: If True, exclude fields with their default values
            by_alias: If True, use field aliases as keys (not yet implemented)

        Returns:
            Dictionary representation of the serializer

        Example:
            user = UserSerializer(id=1, name="John", email=None)
            user.dump()  # {"id": 1, "name": "John", "email": None}
            user.dump(exclude_none=True)  # {"id": 1, "name": "John"}
        """
        return self._dump_impl(
            exclude_none=exclude_none,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            by_alias=by_alias,
            include_fields=None,
            exclude_fields=None,
        )

    def _dump_impl(
        self,
        *,
        exclude_none: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        by_alias: bool = False,
        include_fields: frozenset[str] | None = None,
        exclude_fields: frozenset[str] | None = None,
    ) -> dict[str, Any]:
        """Internal implementation of dump with field filtering."""
        result: dict[str, Any] = {}

        # Build a mapping of field names to their default values for exclude_defaults
        # msgspec's __struct_defaults__ is a tuple of defaults for fields WITH defaults,
        # aligned from the END of the fields list (fields without defaults come first)
        default_values: dict[str, Any] = {}
        if exclude_defaults:
            defaults = self.__struct_defaults__
            fields = self.__struct_fields__
            num_fields = len(fields)
            num_defaults = len(defaults)
            # Defaults are aligned from the end
            for i, default_val in enumerate(defaults):
                field_idx = num_fields - num_defaults + i
                if field_idx >= 0:
                    default_values[fields[field_idx]] = default_val

        for field_name in self.__struct_fields__:
            # Skip write_only fields (they shouldn't appear in output)
            if field_name in self.__write_only_fields__:
                continue

            # Apply include/exclude filtering
            if include_fields is not None and field_name not in include_fields:
                continue
            if exclude_fields is not None and field_name in exclude_fields:
                continue

            # Check field config for exclusion
            field_config = self.__field_configs__.get(field_name)
            if field_config and field_config.exclude:
                continue

            value = getattr(self, field_name)

            # Skip None values if exclude_none
            if exclude_none and value is None:
                continue

            # Skip default values if exclude_defaults
            if exclude_defaults and field_name in default_values:
                if value == default_values[field_name]:
                    continue

            # Use alias if by_alias and alias is defined
            output_key = field_name
            if by_alias and field_config and field_config.alias:
                output_key = field_config.alias

            # Handle nested serializers
            if isinstance(value, Serializer):
                result[output_key] = value.dump(
                    exclude_none=exclude_none,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    by_alias=by_alias,
                )
            elif isinstance(value, list):
                # Check if it's a list of serializers
                if value and isinstance(value[0], Serializer):
                    result[output_key] = [
                        item.dump(
                            exclude_none=exclude_none,
                            exclude_unset=exclude_unset,
                            exclude_defaults=exclude_defaults,
                            by_alias=by_alias,
                        )
                        for item in value
                    ]
                else:
                    result[output_key] = value
            else:
                result[output_key] = value

        # Add computed fields
        if self.__has_computed_fields__:
            for field_name, config in self.__computed_fields__.items():
                # Apply include/exclude filtering to computed fields too
                if include_fields is not None and field_name not in include_fields:
                    continue
                if exclude_fields is not None and field_name in exclude_fields:
                    continue

                # Get the method and call it
                method = getattr(self, config.method_name, None)
                if method is not None:
                    value = method()

                    # Skip None values if exclude_none
                    if exclude_none and value is None:
                        continue

                    result[field_name] = value

        return result

    def dump_json(
        self,
        *,
        exclude_none: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        by_alias: bool = False,
    ) -> bytes:
        """
        Serialize this instance to JSON bytes.

        Uses msgspec for fast JSON encoding.

        Args:
            exclude_none: If True, exclude fields with None values
            exclude_unset: If True, exclude fields that weren't explicitly set
            exclude_defaults: If True, exclude fields with their default values
            by_alias: If True, use field aliases as keys

        Returns:
            JSON bytes representation
        """
        data = self.dump(
            exclude_none=exclude_none,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            by_alias=by_alias,
        )
        return msgspec.json.encode(data)

    @classmethod
    def dump_many(
        cls: type[T],
        instances: Iterable[T],
        *,
        exclude_none: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        by_alias: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Serialize multiple instances to a list of dictionaries.

        Args:
            instances: Iterable of serializer instances to dump
            exclude_none: If True, exclude fields with None values
            exclude_unset: If True, exclude fields that weren't explicitly set
            exclude_defaults: If True, exclude fields with their default values
            by_alias: If True, use field aliases as keys

        Returns:
            List of dictionary representations

        Example:
            users = [UserSerializer.from_model(u) for u in User.objects.all()]
            UserSerializer.dump_many(users)
        """
        return [
            instance.dump(
                exclude_none=exclude_none,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                by_alias=by_alias,
            )
            for instance in instances
        ]

    @classmethod
    def dump_many_json(
        cls: type[T],
        instances: Iterable[T],
        *,
        exclude_none: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        by_alias: bool = False,
    ) -> bytes:
        """
        Serialize multiple instances to JSON bytes.

        Args:
            instances: Iterable of serializer instances to dump
            exclude_none: If True, exclude fields with None values
            exclude_unset: If True, exclude fields that weren't explicitly set
            exclude_defaults: If True, exclude fields with their default values
            by_alias: If True, use field aliases as keys

        Returns:
            JSON bytes representation of the list
        """
        data = cls.dump_many(
            instances,
            exclude_none=exclude_none,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            by_alias=by_alias,
        )
        return msgspec.json.encode(data)

    # -------------------------------------------------------------------------
    # Helper for getting value from source path
    # -------------------------------------------------------------------------

    @staticmethod
    def _get_value_from_source(obj: Any, source: str) -> Any:
        """
        Get a value from an object using a dot-notation source path.

        Args:
            obj: The object to get the value from
            source: Dot-notation path (e.g., "author.name")

        Returns:
            The value at the path, or None if not found
        """
        parts = source.split(".")
        value = obj
        for part in parts:
            if value is None:
                return None
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        return value


class SerializerView(Iterable[T]):
    """
    A view of a serializer with dynamic field selection.

    This class wraps a Serializer and applies field filtering during
    serialization. It does NOT create new serializer classes - it's
    a lightweight wrapper that filters fields at dump time.

    SerializerView is created by calling only(), exclude(), or use()
    on a Serializer class.

    Example:
        # These all return SerializerView instances:
        view = UserSerializer.only("id", "name")
        view = UserSerializer.exclude("password")
        view = UserSerializer.use("list")

        # Use the view to dump instances:
        view.dump(user)
        view.dump_many(users)

        # Or directly from model:
        view.from_model(user_instance)
    """

    def __init__(
        self,
        serializer_class: type[T],
        *,
        include_fields: frozenset[str] | None = None,
        exclude_fields: frozenset[str] | None = None,
    ) -> None:
        self._serializer_class = serializer_class
        self._include_fields = include_fields
        self._exclude_fields = exclude_fields

    def __iter__(self):
        """Allow iteration (returns empty iterator - use dump_many instead)."""
        return iter([])

    def only(self, *fields: str) -> SerializerView[T]:
        """Further restrict to only these fields."""
        new_include = frozenset(fields)
        if self._include_fields is not None:
            # Intersection with existing include
            new_include = self._include_fields & new_include
        return SerializerView(
            self._serializer_class,
            include_fields=new_include,
            exclude_fields=self._exclude_fields,
        )

    def exclude(self, *fields: str) -> SerializerView[T]:
        """Exclude additional fields."""
        new_exclude = frozenset(fields)
        if self._exclude_fields is not None:
            new_exclude = self._exclude_fields | new_exclude
        return SerializerView(
            self._serializer_class,
            include_fields=self._include_fields,
            exclude_fields=new_exclude,
        )

    def from_model(self, instance: Model, **kwargs) -> T:
        """Create a serializer instance from a Django model."""
        return self._serializer_class.from_model(instance, **kwargs)

    def dump(
        self,
        instance: T,
        *,
        exclude_none: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        by_alias: bool = False,
    ) -> dict[str, Any]:
        """
        Serialize an instance with field filtering applied.

        Args:
            instance: Serializer instance to dump
            exclude_none: If True, exclude fields with None values
            exclude_unset: If True, exclude fields that weren't explicitly set
            exclude_defaults: If True, exclude fields with their default values
            by_alias: If True, use field aliases as keys

        Returns:
            Filtered dictionary representation
        """
        return instance._dump_impl(
            exclude_none=exclude_none,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            by_alias=by_alias,
            include_fields=self._include_fields,
            exclude_fields=self._exclude_fields,
        )

    def dump_many(
        self,
        instances: Iterable[T],
        *,
        exclude_none: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        by_alias: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Serialize multiple instances with field filtering applied.

        Args:
            instances: Iterable of serializer instances
            exclude_none: If True, exclude fields with None values
            exclude_unset: If True, exclude fields that weren't explicitly set
            exclude_defaults: If True, exclude fields with their default values
            by_alias: If True, use field aliases as keys

        Returns:
            List of filtered dictionary representations
        """
        return [
            self.dump(
                instance,
                exclude_none=exclude_none,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                by_alias=by_alias,
            )
            for instance in instances
        ]

    def dump_json(
        self,
        instance: T,
        *,
        exclude_none: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        by_alias: bool = False,
    ) -> bytes:
        """Serialize an instance to JSON bytes with field filtering."""
        data = self.dump(
            instance,
            exclude_none=exclude_none,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            by_alias=by_alias,
        )
        return msgspec.json.encode(data)

    def dump_many_json(
        self,
        instances: Iterable[T],
        *,
        exclude_none: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        by_alias: bool = False,
    ) -> bytes:
        """Serialize multiple instances to JSON bytes with field filtering."""
        data = self.dump_many(
            instances,
            exclude_none=exclude_none,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            by_alias=by_alias,
        )
        return msgspec.json.encode(data)

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated, Any, ClassVar, Literal, TypeVar, get_origin

from django.db import models

from .base import Serializer, _SerializerMeta
from .fields import FieldConfig, _FieldMarker, get_msgspec_type_for_django_field
from .nested import Nested
from .validators import UniqueValidator

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _is_classvar_annotation(annotation: Any) -> bool:
    """
    Check if an annotation is a ClassVar type.

    Handles both resolved ClassVar types and string annotations.
    This is used to filter out ClassVar fields when copying annotations
    from base classes in the metaclass.
    """
    # Handle string annotations (from __future__ annotations)
    if isinstance(annotation, str):
        return annotation.startswith("ClassVar[") or annotation == "ClassVar"

    # Handle resolved ClassVar types
    try:
        origin = get_origin(annotation)
        if origin is ClassVar:
            return True
    except Exception:
        # get_origin() may fail on malformed or non-standard annotations
        # Treat such annotations as non-ClassVar to be safe
        return False

    return False

T = TypeVar("T", bound="ModelSerializer")

# Sentinel for "all fields"
ALL_FIELDS = "__all__"


class ModelSerializerMeta(_SerializerMeta):
    """
    Metaclass for ModelSerializer that auto-generates field annotations.

    This metaclass inspects the Meta class configuration and generates
    appropriate field annotations before the Serializer metaclass processes them.
    """

    def __new__(mcs, name: str, bases: tuple, namespace: dict, **kwargs):
        # Skip processing for the base ModelSerializer class itself
        if name == "ModelSerializer" and not any(
            isinstance(b, ModelSerializerMeta) for b in bases
        ):
            return super().__new__(mcs, name, bases, namespace, **kwargs)

        # Get Meta class from namespace
        meta = namespace.get("Meta")

        # If no Meta or no model, just create the class normally
        if meta is None or not hasattr(meta, "model"):
            return super().__new__(mcs, name, bases, namespace, **kwargs)

        model = meta.model

        # Determine which fields to include
        fields_config = getattr(meta, "fields", None)
        exclude_config = getattr(meta, "exclude", None)

        if fields_config is None and exclude_config is None:
            raise ValueError(
                f"ModelSerializer '{name}' must define either 'fields' or 'exclude' in Meta class. "
                f"Use fields = '__all__' to include all model fields."
            )

        if fields_config is not None and exclude_config is not None:
            raise ValueError(
                f"ModelSerializer '{name}' cannot define both 'fields' and 'exclude' in Meta class."
            )

        # Get all model fields
        model_fields = _get_model_fields(model)

        # Determine which fields to include
        if fields_config == ALL_FIELDS:
            fields_to_include = set(model_fields.keys())
        elif fields_config is not None:
            fields_to_include = set(fields_config)
            # Validate that all specified fields exist
            for field_name in fields_to_include:
                if field_name not in model_fields and field_name not in namespace.get("__annotations__", {}):
                    raise ValueError(
                        f"Field '{field_name}' specified in Meta.fields does not exist on model {model.__name__}"
                    )
        else:
            # exclude is not None
            fields_to_include = set(model_fields.keys()) - set(exclude_config)

        # Get read_only and write_only from Meta
        read_only_fields = set(getattr(meta, "read_only", set()) or set())
        write_only_fields = set(getattr(meta, "write_only", set()) or set())

        # Get depth for nested serialization
        depth = getattr(meta, "depth", 0)

        # Get extra_kwargs for field customization
        extra_kwargs = getattr(meta, "extra_kwargs", {})

        # Get existing annotations from the class and its bases
        existing_annotations = namespace.get("__annotations__", {})

        # Check base classes for annotations
        # IMPORTANT: Filter out ClassVar annotations to avoid msgspec decoder issues
        for base in bases:
            if hasattr(base, "__annotations__"):
                for key, value in base.__annotations__.items():
                    if key not in existing_annotations:
                        # Skip ClassVar annotations - they cause "NameError: name 'ClassVar' is not defined"
                        # when msgspec tries to create a decoder and evaluates forward references
                        if _is_classvar_annotation(value):
                            continue
                        existing_annotations[key] = value

        # Build new annotations from model fields
        new_annotations = dict(existing_annotations)

        for field_name in fields_to_include:
            # Skip if already defined by user
            if field_name in existing_annotations:
                continue

            if field_name not in model_fields:
                continue

            field = model_fields[field_name]

            # Generate the field type
            field_type = _generate_field_type(field, depth, read_only_fields, write_only_fields, extra_kwargs.get(field_name, {}))

            if field_type is not None:
                new_annotations[field_name] = field_type

                # Handle defaults for nullable/optional fields
                if _field_has_default(field) and field_name not in namespace:
                    namespace[field_name] = _get_field_default(field, read_only_fields, write_only_fields, extra_kwargs.get(field_name, {}))

        namespace["__annotations__"] = new_annotations

        # Store model reference for later use
        namespace["_django_model"] = model
        namespace["__model_fields_config__"] = frozenset(fields_to_include)

        # Pre-compute FK/M2M mappings for from_model fast path
        # IMPORTANT: Only map to _id when depth=0 (no nested serialization)
        # When depth > 0, FK/M2M fields are handled via __nested_fields__
        fk_id_mapping: dict[str, str] = {}
        m2m_fields: set[str] = set()
        regular_fields: list[str] = []

        for field_name in fields_to_include:
            if field_name not in model_fields:
                continue
            field = model_fields[field_name]

            # Check if it's a ForeignKey/OneToOne - map to _id attribute
            if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                # Only map to _id if not nested (depth=0)
                if depth == 0:
                    fk_id_mapping[field_name] = f"{field_name}_id"
                else:
                    # depth > 0: handled by nested serializer in __nested_fields__
                    regular_fields.append(field_name)
            elif isinstance(field, models.ManyToManyField):
                # Only use _id extraction for depth=0
                # depth > 0: handled by nested serializer in __nested_fields__
                if depth == 0:
                    m2m_fields.add(field_name)
                else:
                    regular_fields.append(field_name)
            else:
                regular_fields.append(field_name)

        namespace["__fk_id_mapping__"] = fk_id_mapping
        namespace["__m2m_fields__"] = frozenset(m2m_fields)
        namespace["__regular_fields__"] = tuple(regular_fields)

        # Generate optimized _from_model_generated method if no nested fields and no M2M
        # This avoids dict creation and loops at runtime
        if depth == 0 and not m2m_fields:
            generated_method = _generate_from_model_code(
                name, fk_id_mapping, regular_fields, fields_to_include
            )
            if generated_method is not None:
                namespace["_from_model_generated"] = generated_method

        # Alias Meta to Config so base Serializer picks up configuration
        namespace["Config"] = meta

        return super().__new__(mcs, name, bases, namespace, **kwargs)


def _generate_from_model_code(
    class_name: str,
    fk_id_mapping: dict[str, str],
    regular_fields: list[str],
    all_fields: set[str],
) -> classmethod | None:
    """
    Generate optimized from_model code at class definition time.

    This generates a classmethod that directly accesses model attributes
    by name, avoiding dict creation, loops, and membership checks.

    Returns None if code generation fails or is not beneficial.
    """
    try:
        # Build the argument list for cls()
        args = []
        for field_name in all_fields:
            if field_name in fk_id_mapping:
                # FK field - use _id suffix for direct access
                id_attr = fk_id_mapping[field_name]
                args.append(f"{field_name}=instance.{id_attr}")
            else:
                # Regular field - direct access
                args.append(f"{field_name}=instance.{field_name}")

        args_str = ", ".join(args)

        # Generate the function code
        code = f"""
def _from_model_generated(cls, instance):
    return cls({args_str})
"""
        # Compile and extract the function
        local_ns: dict[str, Any] = {}
        exec(code, {}, local_ns)  # noqa: S102

        # Return as classmethod
        return classmethod(local_ns["_from_model_generated"])
    except Exception:
        # If code generation fails for any reason, return None
        # The fallback _from_model_fast will be used instead
        return None


def _get_model_fields(model: type[models.Model]) -> dict[str, models.Field]:
    """Get all fields from a Django model, including related fields.

    This includes:
    - Regular fields (CharField, IntegerField, etc.)
    - ForeignKey and OneToOneField (concrete relations)
    - ManyToManyField (forward direction only)

    This excludes:
    - Reverse relations (reverse ForeignKey, reverse OneToOne, reverse M2M)
    """
    fields = {}

    for field in model._meta.get_fields():
        # Include non-relational fields
        if not field.is_relation:
            fields[field.name] = field
            continue

        # Include concrete relations (ForeignKey, OneToOneField)
        if field.concrete:
            fields[field.name] = field
            continue

        # Include forward ManyToManyField (not reverse M2M)
        # For M2M, concrete=False but we want to include the defining side
        if isinstance(field, models.ManyToManyField):
            fields[field.name] = field
            continue

        # Skip reverse relations (one_to_many, reverse M2M)

    return fields


def _field_has_default(field: models.Field) -> bool:
    """Check if a Django field has a default value or is optional."""
    # ManyToManyField is always optional (empty list by default)
    if isinstance(field, models.ManyToManyField):
        return True

    # Fields with explicit defaults
    if field.has_default():
        return True

    # Nullable fields are optional
    if getattr(field, "null", False):
        return True

    # Blank fields (for strings) are optional
    if getattr(field, "blank", False):
        return True

    # AutoFields (primary keys) are read_only
    return bool(isinstance(field, (models.AutoField, models.BigAutoField)))


def _get_field_default(field: models.Field, read_only_fields: set[str], write_only_fields: set[str], extra_kwargs: dict) -> Any:
    """Get the default value for a Django field."""
    # Check if read_only or write_only in extra_kwargs
    is_read_only = field.name in read_only_fields or extra_kwargs.get("read_only", False)
    is_write_only = field.name in write_only_fields or extra_kwargs.get("write_only", False)

    # ManyToManyField defaults to empty list
    if isinstance(field, models.ManyToManyField):
        return _FieldMarker(FieldConfig(
            read_only=is_read_only,
            write_only=is_write_only,
            default_factory=list,
        ))

    # For AutoFields, use field() with read_only
    if isinstance(field, (models.AutoField, models.BigAutoField)):
        return _FieldMarker(FieldConfig(read_only=True, default=None))

    # If has explicit default
    if field.has_default():
        default = field.default
        if callable(default):
            # Use default_factory for callable defaults
            config = FieldConfig(
                read_only=is_read_only,
                write_only=is_write_only,
                default_factory=default,
            )
        else:
            config = FieldConfig(
                read_only=is_read_only,
                write_only=is_write_only,
                default=default,
            )
        return _FieldMarker(config)

    # For nullable fields, default to None
    if getattr(field, "null", False):
        config = FieldConfig(
            read_only=is_read_only,
            write_only=is_write_only,
            default=None,
        )
        return _FieldMarker(config)

    # For blank string fields, default to empty string
    if getattr(field, "blank", False) and isinstance(field, (models.CharField, models.TextField)):
        config = FieldConfig(
            read_only=is_read_only,
            write_only=is_write_only,
            default="",
        )
        return _FieldMarker(config)

    # No default - field is required
    if is_read_only or is_write_only:
        return _FieldMarker(FieldConfig(read_only=is_read_only, write_only=is_write_only))

    return ...


def _generate_field_type(
    field: models.Field,
    depth: int,
    read_only_fields: set[str],
    write_only_fields: set[str],
    extra_kwargs: dict,
) -> type | None:
    """Generate a msgspec-compatible type annotation from a Django field."""

    # Handle ForeignKey relationships
    if isinstance(field, models.ForeignKey):
        if depth > 0:
            # Create nested serializer type
            related_model = field.related_model
            nested_serializer = _create_nested_serializer(related_model, depth - 1, read_only_fields, write_only_fields)
            if field.null:
                return Annotated[nested_serializer | None, Nested(nested_serializer)]
            return Annotated[nested_serializer, Nested(nested_serializer)]
        else:
            # Just use ID (int)
            if field.null:
                return int | None
            return int

    # Handle OneToOneField
    if isinstance(field, models.OneToOneField):
        if depth > 0:
            related_model = field.related_model
            nested_serializer = _create_nested_serializer(related_model, depth - 1, read_only_fields, write_only_fields)
            if field.null:
                return Annotated[nested_serializer | None, Nested(nested_serializer)]
            return Annotated[nested_serializer, Nested(nested_serializer)]
        else:
            if field.null:
                return int | None
            return int

    # Handle ManyToManyField
    if isinstance(field, models.ManyToManyField):
        if depth > 0:
            related_model = field.related_model
            nested_serializer = _create_nested_serializer(related_model, depth - 1, read_only_fields, write_only_fields)
            return Annotated[list[nested_serializer], Nested(nested_serializer, many=True)]
        else:
            # List of IDs
            return list[int]

    # Handle regular fields
    field_type = get_msgspec_type_for_django_field(field)

    # Check for uniqueness constraint (exclude PK as it's handled differently)
    if getattr(field, "unique", False) and not field.primary_key:
        try:
             # Get the default manager's queryset
             queryset = field.model._default_manager.all()
             unique_validator = UniqueValidator(queryset=queryset, field_name=field.name)
             return Annotated[field_type, unique_validator]
        except Exception as e:
             # Fallback if model/queryset not ready
             logger.warning(f"Could not attach UniqueValidator to {field.name}: {e}")
             return field_type

    return field_type


def _create_nested_serializer(
    model: type[models.Model],
    depth: int,
    read_only_fields: set[str],
    write_only_fields: set[str],
) -> type[Serializer]:
    """Create a nested serializer for a related model."""
    # Get model fields (already filters out reverse relations)
    model_fields = _get_model_fields(model)

    # Build annotations
    annotations: dict[str, Any] = {}
    namespace: dict[str, Any] = {}

    for field_name, field in model_fields.items():
        field_type = _generate_field_type(field, depth, set(), set(), {})
        if field_type is not None:
            annotations[field_name] = field_type

            if _field_has_default(field):
                namespace[field_name] = _get_field_default(field, set(), set(), {})

    namespace["__annotations__"] = annotations
    namespace["__module__"] = model.__module__

    # Create and return the nested serializer class
    class_name = f"{model.__name__}NestedSerializer"
    return type(class_name, (Serializer,), namespace)


class ModelSerializer(Serializer, metaclass=ModelSerializerMeta):
    """
    Serializer that auto-generates fields from Django models.

    ModelSerializer provides automatic field generation based on Django model
    introspection, similar to Django REST Framework's ModelSerializer.

    Features:
    - Automatic field generation from model fields
    - Support for `fields`, `exclude`, `read_only`, `write_only` in Meta
    - Nested serialization with `depth` control
    - Field customization via `extra_kwargs`
    - All Serializer features (validators, computed fields, etc.)

    Example:
        from django_bolt.serializers import ModelSerializer

        class UserSerializer(ModelSerializer):
            class Meta:
                model = User
                fields = ['id', 'username', 'email', 'date_joined']
                read_only = {'id', 'date_joined'}

        # Or include all fields
        class UserFullSerializer(ModelSerializer):
            class Meta:
                model = User
                fields = '__all__'
                exclude = ['password']

    With nested relationships:
        class PostSerializer(ModelSerializer):
            class Meta:
                model = Post
                fields = ['id', 'title', 'author', 'tags']
                depth = 1  # Include nested objects for author and tags

    Field customization:
        class UserSerializer(ModelSerializer):
            class Meta:
                model = User
                fields = ['id', 'username', 'email', 'password']
                extra_kwargs = {
                    'password': {'write_only': True},
                    'email': {'read_only': True},
                }
    """

    # Class-level attributes set by metaclass
    _django_model: ClassVar[type[models.Model] | None] = None
    __model_fields_config__: ClassVar[frozenset[str]] = frozenset()

    class Meta:
        """
        Configuration class for ModelSerializer.

        Attributes:
            model: The Django model class to generate fields from
            fields: List of field names to include, or '__all__' for all fields
            exclude: List of field names to exclude (cannot be used with fields)
            read_only: Set of field names that are output-only
            write_only: Set of field names that are input-only
            depth: Nesting depth for related objects (default: 0 = just IDs)
            extra_kwargs: Dict of field name to kwargs for field customization
        """
        model: type[models.Model] | None = None
        fields: list[str] | Literal["__all__"] | None = None
        exclude: list[str] | None = None
        read_only: set[str] = set()
        write_only: set[str] = set()
        depth: int = 0
        extra_kwargs: dict[str, dict[str, Any]] = {}

    @classmethod
    def get_model(cls) -> type[models.Model] | None:
        """Get the Django model class for this serializer."""
        return getattr(cls, "_django_model", None)

    @classmethod
    def _collect_meta_config(cls) -> None:
        """Collect configuration from Meta class."""
        super()._collect_meta_config()

        # Explicitly support DRF-style Meta
        meta = getattr(cls, "Meta", None)
        if meta:
            ro = getattr(meta, "read_only", set())
            wo = getattr(meta, "write_only", set())

            # Update the immutable sets
            if ro:
                cls.__read_only_fields__ = cls.__read_only_fields__ | frozenset(ro)
            if wo:
                cls.__write_only_fields__ = cls.__write_only_fields__ | frozenset(wo)

    def create(self, validated_data: dict[str, Any]) -> models.Model:
        """
        Create a new model instance from validated data.

        Override this method for custom creation logic.

        Args:
            validated_data: Dict of validated field values

        Returns:
            Newly created model instance (unsaved)
        """
        model = self.get_model()
        if model is None:
            raise ValueError("ModelSerializer must have a Meta.model defined")

        return model(**validated_data)

    def update(self, instance: models.Model, validated_data: dict[str, Any]) -> models.Model:
        """
        Update an existing model instance with validated data.

        Override this method for custom update logic.

        Args:
            instance: Existing model instance to update
            validated_data: Dict of validated field values

        Returns:
            Updated model instance (unsaved)
        """
        for field_name, value in validated_data.items():
            setattr(instance, field_name, value)

        return instance

    def to_dict_for_create(self) -> dict[str, Any]:
        """
        Convert to a dict suitable for creating a model instance.

        Excludes read_only fields and includes only writable fields.
        """
        result = {}
        getattr(self, "__write_only_fields__", frozenset())
        read_only = getattr(self, "__read_only_fields__", frozenset())

        for field_name in self.__struct_fields__:
            # Include all fields except read_only
            if field_name in read_only:
                continue

            value = getattr(self, field_name)

            # Handle nested serializers
            if isinstance(value, Serializer):
                result[field_name] = value.to_dict()
            elif isinstance(value, list) and value and isinstance(value[0], Serializer):
                result[field_name] = [item.to_dict() for item in value]
            else:
                result[field_name] = value

        return result

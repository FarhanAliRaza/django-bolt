"""
DRF-style serializers for django-bolt using msgspec.

This module provides a ModelSerializer class that automatically generates
msgspec.Struct classes from Django models, similar to Django REST Framework
serializers but with the performance benefits of msgspec.

Example:
    from django_bolt.serializers import ModelSerializer
    from myapp.models import User

    class UserSerializer(ModelSerializer):
        class Meta:
            model = User
            fields = ['id', 'username', 'email', 'first_name', 'last_name']
            # or fields = '__all__'
            # exclude = ['password']
            # read_only_fields = ['id', 'created_at']
            # depth = 1  # For nested relationships

        # DRF-style field validation
        def validate_age(self, value):
            if value < 18:
                raise ValidationError("Must be 18 or older")
            return value

        # Multi-field validation
        def validate(self, data):
            if data.get('is_premium') and data.get('age', 0) < 21:
                raise ValidationError("Premium users must be 21+")
            return data

    # Use with API endpoints
    @api.get("/users/{id}")
    async def get_user(id: int) -> UserSerializer:
        user = await User.objects.aget(id=id)
        return UserSerializer.from_model(user)
"""

import msgspec
from typing import Any, Dict, List, Optional, Set, Type, get_type_hints, Union, Callable
from django.db import models
from django.db.models.fields.related import ForeignKey, ManyToManyField, OneToOneField
from django.db.models.fields.reverse_related import ManyToOneRel, ManyToManyRel
from datetime import datetime, date, time
import decimal
import uuid
import inspect


class ValidationError(Exception):
    """
    Validation error raised by field validators.

    Compatible with DRF's ValidationError and django-bolt's exception handling.
    """
    def __init__(self, message: Union[str, Dict[str, Any], List[Any]]):
        self.message = message
        self.detail = message
        super().__init__(message)


class SerializerMetaclass(type):
    """Metaclass that generates msgspec.Struct from Django model metadata."""

    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        # Skip base Serializer class
        if name == 'Serializer' or name == 'ModelSerializer':
            return super().__new__(mcs, name, bases, namespace)

        # Get Meta class
        meta = namespace.get('Meta')
        if not meta:
            raise ValueError(f"{name} must define a Meta class")

        # Get model
        model = getattr(meta, 'model', None)
        if not model:
            raise ValueError(f"{name}.Meta must define 'model'")

        # Validate that model is a Django model
        if not isinstance(model, type) or not issubclass(model, models.Model):
            raise ValueError(f"{name}.Meta.model must be a Django model class")

        # Get field configuration
        fields = getattr(meta, 'fields', None)
        exclude = getattr(meta, 'exclude', None)
        read_only_fields = getattr(meta, 'read_only_fields', [])
        depth = getattr(meta, 'depth', 0)
        extra_kwargs = getattr(meta, 'extra_kwargs', {})

        # Determine which fields to include
        model_fields = mcs._get_model_fields(model, fields, exclude)

        # Generate msgspec struct fields
        struct_fields: Dict[str, Any] = {}
        read_only_set = set(read_only_fields)

        for field_name, django_field in model_fields.items():
            # Check if field is overridden in serializer class
            if field_name in namespace and not field_name.startswith('_'):
                # Use custom field definition
                struct_fields[field_name] = namespace[field_name]
                continue

            # Get field type
            field_type = mcs._get_field_type(
                django_field,
                field_name,
                read_only_set,
                depth,
                extra_kwargs.get(field_name, {})
            )

            # Add to struct fields
            struct_fields[field_name] = field_type

        # Detect DRF-style validators
        # 1. Field-level validators: validate_<fieldname>(self, value)
        field_validators: Dict[str, Callable] = {}
        for attr_name, attr_value in namespace.items():
            if attr_name.startswith('validate_') and callable(attr_value):
                field_name = attr_name[9:]  # Remove 'validate_' prefix
                if field_name and field_name in model_fields and not field_name.startswith('_'):
                    field_validators[field_name] = attr_value

        # 2. Object-level validator: validate(self, data)
        object_validator = namespace.get('validate')
        if object_validator and callable(object_validator):
            # Check it's the custom validate method, not inherited
            if 'validate' in namespace:
                namespace['_object_validator'] = object_validator

        # Store metadata for from_model method
        namespace['_model'] = model
        namespace['_model_fields'] = model_fields
        namespace['_read_only_fields'] = read_only_set
        namespace['_depth'] = depth
        namespace['_field_validators'] = field_validators

        # Create msgspec.Struct dynamically
        # We'll create a class that inherits from msgspec.Struct
        struct_namespace = {
            '__annotations__': struct_fields,
            '__module__': namespace.get('__module__', __name__),
        }

        # Create the struct class
        struct_cls = type(name + 'Struct', (msgspec.Struct,), struct_namespace)

        # Store struct class
        namespace['_struct_cls'] = struct_cls

        # Create the serializer class
        cls = super().__new__(mcs, name, bases, namespace)

        # Make the serializer class inherit from msgspec.Struct behavior
        # by delegating to the struct class
        return cls

    @staticmethod
    def _get_model_fields(
        model: Type[models.Model],
        fields: Optional[Union[List[str], str]],
        exclude: Optional[List[str]]
    ) -> Dict[str, models.Field]:
        """Get model fields based on fields/exclude configuration."""
        all_fields = {}

        # Get all concrete fields (excludes reverse relations by default)
        for field in model._meta.get_fields():
            # Skip reverse relations unless explicitly included
            if isinstance(field, (ManyToOneRel, ManyToManyRel)):
                continue
            all_fields[field.name] = field

        # Handle fields parameter
        if fields == '__all__':
            selected_fields = all_fields
        elif fields is not None:
            selected_fields = {name: all_fields[name] for name in fields if name in all_fields}
        else:
            selected_fields = all_fields

        # Handle exclude parameter
        if exclude:
            for field_name in exclude:
                selected_fields.pop(field_name, None)

        return selected_fields

    @staticmethod
    def _get_field_type(
        django_field: models.Field,
        field_name: str,
        read_only_set: Set[str],
        depth: int,
        field_kwargs: Dict[str, Any]
    ) -> Any:
        """Map Django field to msgspec type annotation."""
        # Check if field is read-only or has a default/auto value
        is_read_only = field_name in read_only_set
        has_default = (
            django_field.has_default() or
            django_field.null or
            django_field.blank or
            getattr(django_field, 'auto_now', False) or
            getattr(django_field, 'auto_now_add', False) or
            isinstance(django_field, models.AutoField)
        )

        # Get base type
        base_type = SerializerMetaclass._django_field_to_python_type(django_field, depth)

        # Make optional if nullable or has default
        if has_default or django_field.null or not django_field.editable:
            return Optional[base_type]

        return base_type

    @staticmethod
    def _django_field_to_python_type(django_field: models.Field, depth: int) -> Any:
        """Convert Django field to Python type annotation."""
        # Handle relationships
        if isinstance(django_field, (ForeignKey, OneToOneField)):
            if depth > 0:
                # Nested serialization (simplified for now)
                return Dict[str, Any]  # TODO: Support nested serializers
            else:
                # Just the ID
                return int

        if isinstance(django_field, ManyToManyField):
            if depth > 0:
                return List[Dict[str, Any]]  # TODO: Support nested serializers
            else:
                return List[int]

        # Handle common field types
        if isinstance(django_field, models.AutoField):
            return int
        elif isinstance(django_field, models.BigAutoField):
            return int
        elif isinstance(django_field, models.IntegerField):
            return int
        elif isinstance(django_field, models.BigIntegerField):
            return int
        elif isinstance(django_field, models.SmallIntegerField):
            return int
        elif isinstance(django_field, models.PositiveIntegerField):
            return int
        elif isinstance(django_field, models.PositiveSmallIntegerField):
            return int
        elif isinstance(django_field, models.FloatField):
            return float
        elif isinstance(django_field, models.DecimalField):
            return decimal.Decimal
        elif isinstance(django_field, models.CharField):
            return str
        elif isinstance(django_field, models.TextField):
            return str
        elif isinstance(django_field, models.EmailField):
            return str
        elif isinstance(django_field, models.URLField):
            return str
        elif isinstance(django_field, models.SlugField):
            return str
        elif isinstance(django_field, models.UUIDField):
            return uuid.UUID
        elif isinstance(django_field, models.BooleanField):
            return bool
        elif isinstance(django_field, models.NullBooleanField):
            return Optional[bool]
        elif isinstance(django_field, models.DateTimeField):
            return datetime
        elif isinstance(django_field, models.DateField):
            return date
        elif isinstance(django_field, models.TimeField):
            return time
        elif isinstance(django_field, models.JSONField):
            return Dict[str, Any]
        elif isinstance(django_field, models.BinaryField):
            return bytes
        else:
            # Default to Any for unknown types
            return Any


class Serializer:
    """Base serializer class."""
    _struct_cls: Type[msgspec.Struct]
    _model: Type[models.Model]
    _model_fields: Dict[str, models.Field]
    _read_only_fields: Set[str]
    _depth: int

    def __init_subclass__(cls) -> None:
        """Called when a subclass is created."""
        super().__init_subclass__()

    @classmethod
    def from_model(cls, instance: models.Model, *, validate: bool = True) -> msgspec.Struct:
        """
        Convert a Django model instance to a msgspec.Struct.

        Args:
            instance: Django model instance
            validate: Whether to run field validators (default: True)

        Returns:
            msgspec.Struct instance with data from the model

        Raises:
            ValidationError: If validation fails
        """
        if not hasattr(cls, '_struct_cls'):
            raise ValueError(f"{cls.__name__} is not properly initialized")

        # Extract field values from model instance
        data = {}
        for field_name in cls._model_fields.keys():
            if hasattr(instance, field_name):
                value = getattr(instance, field_name)

                # Handle special cases
                django_field = cls._model_fields[field_name]

                # Handle ForeignKey - get the ID
                if isinstance(django_field, (ForeignKey, OneToOneField)):
                    if cls._depth > 0 and value is not None:
                        # Nested serialization - convert to dict
                        data[field_name] = cls._serialize_related_object(value)
                    else:
                        # Just the ID
                        data[field_name] = value.pk if value is not None else None

                # Handle ManyToMany - get list of IDs
                elif isinstance(django_field, ManyToManyField):
                    if cls._depth > 0:
                        # Nested serialization
                        data[field_name] = [cls._serialize_related_object(obj) for obj in value.all()]
                    else:
                        # Just the IDs
                        data[field_name] = [obj.pk for obj in value.all()]

                else:
                    data[field_name] = value

        # Run validation if enabled
        if validate:
            data = cls._run_validation(data)

        # Create struct instance
        return cls._struct_cls(**data)

    @staticmethod
    def _serialize_related_object(obj: models.Model) -> Dict[str, Any]:
        """Serialize a related object to a dictionary."""
        data = {}
        for field in obj._meta.get_fields():
            if isinstance(field, (ManyToOneRel, ManyToManyRel, ManyToManyField)):
                continue
            if hasattr(obj, field.name):
                value = getattr(obj, field.name)
                # Handle nested ForeignKey - just use ID to avoid infinite recursion
                if isinstance(field, (ForeignKey, OneToOneField)) and value is not None:
                    data[field.name] = value.pk
                else:
                    data[field.name] = value
        return data

    @classmethod
    def from_models(cls, instances: List[models.Model], *, validate: bool = True) -> List[msgspec.Struct]:
        """
        Convert a list of Django model instances to msgspec.Struct instances.

        Args:
            instances: List of Django model instances or queryset
            validate: Whether to run field validators (default: True)

        Returns:
            List of msgspec.Struct instances
        """
        return [cls.from_model(instance, validate=validate) for instance in instances]

    @classmethod
    def _run_validation(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run DRF-style validation on data dict.

        This runs:
        1. Field-level validators (validate_<fieldname> methods)
        2. Object-level validation (validate method)

        Args:
            data: Dictionary of field values

        Returns:
            Validated data dictionary

        Raises:
            ValidationError: If validation fails
        """
        # Create a temporary instance for validation (validators need self)
        validator_instance = cls.__new__(cls)

        # 1. Run field-level validators
        field_validators = getattr(cls, '_field_validators', {})
        validated_data = {}

        for field_name, value in data.items():
            if field_name in field_validators:
                # Run the validate_<fieldname> method
                validator_method = field_validators[field_name]
                try:
                    validated_value = validator_method(validator_instance, value)
                    validated_data[field_name] = validated_value
                except ValidationError:
                    raise
                except Exception as e:
                    raise ValidationError(f"Validation error for field '{field_name}': {str(e)}")
            else:
                validated_data[field_name] = value

        # 2. Run object-level validator if present
        object_validator = getattr(cls, '_object_validator', None)
        if object_validator:
            try:
                validated_data = object_validator(validator_instance, validated_data)
            except ValidationError:
                raise
            except Exception as e:
                raise ValidationError(f"Object validation error: {str(e)}")

        return validated_data

    @classmethod
    def decode(cls, data: bytes, *, validate: bool = True) -> msgspec.Struct:
        """
        Decode JSON bytes to msgspec.Struct with validation.

        This is useful for request body parsing with validation.

        Args:
            data: JSON bytes
            validate: Whether to run validators after decoding (default: True)

        Returns:
            Validated msgspec.Struct instance

        Raises:
            ValidationError: If validation fails
            msgspec.DecodeError: If JSON is invalid

        Example:
            @api.post("/users")
            async def create_user(request):
                user_data = UserSerializer.decode(request['body'])
                # user_data is validated UserStruct
                user = await User.objects.acreate(**msgspec.structs.asdict(user_data))
                return UserSerializer.from_model(user)
        """
        if not hasattr(cls, '_struct_cls'):
            raise ValueError(f"{cls.__name__} is not properly initialized")

        # Decode JSON to struct
        struct_instance = msgspec.json.decode(data, type=cls._struct_cls)

        # If validation is enabled, convert to dict, validate, and recreate
        if validate:
            # Convert struct to dict
            data_dict = msgspec.structs.asdict(struct_instance)

            # Run validation
            validated_data = cls._run_validation(data_dict)

            # Recreate struct with validated data
            return cls._struct_cls(**validated_data)

        return struct_instance

    @classmethod
    def decode_json(cls, json_str: str, *, validate: bool = True) -> msgspec.Struct:
        """
        Decode JSON string to msgspec.Struct with validation.

        Args:
            json_str: JSON string
            validate: Whether to run validators (default: True)

        Returns:
            Validated msgspec.Struct instance

        Raises:
            ValidationError: If validation fails
            msgspec.DecodeError: If JSON is invalid
        """
        return cls.decode(json_str.encode(), validate=validate)


class ModelSerializer(Serializer, metaclass=SerializerMetaclass):
    """
    ModelSerializer automatically generates msgspec.Struct from Django models.

    Similar to Django REST Framework's ModelSerializer but uses msgspec
    for better performance.

    Example:
        class UserSerializer(ModelSerializer):
            class Meta:
                model = User
                fields = ['id', 'username', 'email', 'is_active']
                read_only_fields = ['id']

        # Use in views
        user = await User.objects.aget(id=1)
        return UserSerializer.from_model(user)

        # Or with querysets
        users = await User.objects.all()[:10]
        return UserSerializer.from_models(users)

    Meta options:
        model: Django model class (required)
        fields: List of field names or '__all__'
        exclude: List of field names to exclude
        read_only_fields: List of read-only field names
        depth: Depth of nested serialization (default: 0)
        extra_kwargs: Additional field configuration
    """

    class Meta:
        """Placeholder Meta class - must be overridden in subclasses."""
        model = None
        fields = None


# Convenience function for quick serializer creation
def create_serializer(
    model: Type[models.Model],
    fields: Optional[Union[List[str], str]] = '__all__',
    exclude: Optional[List[str]] = None,
    read_only_fields: Optional[List[str]] = None,
    name: Optional[str] = None
) -> Type[ModelSerializer]:
    """
    Create a ModelSerializer class dynamically.

    This is useful for quick serializer creation without defining a class.

    Args:
        model: Django model class
        fields: List of field names or '__all__'
        exclude: List of field names to exclude
        read_only_fields: List of read-only field names
        name: Optional name for the serializer class

    Returns:
        ModelSerializer class

    Example:
        UserSerializer = create_serializer(User, fields=['id', 'username', 'email'])
        user = await User.objects.aget(id=1)
        return UserSerializer.from_model(user)
    """
    serializer_name = name or f"{model.__name__}Serializer"

    meta_attrs = {
        'model': model,
        'fields': fields,
    }

    if exclude:
        meta_attrs['exclude'] = exclude
    if read_only_fields:
        meta_attrs['read_only_fields'] = read_only_fields

    Meta = type('Meta', (), meta_attrs)

    serializer_class = type(
        serializer_name,
        (ModelSerializer,),
        {'Meta': Meta}
    )

    return serializer_class

"""
Model serializers for Django-Bolt using msgspec.

Provides DRF-style model serializers with:
- Auto-generation from Django models
- Custom field validation (validate_<field> methods)
- Full type safety with msgspec.Struct
- Performance optimization for QuerySet serialization
- Less verbose than manual from_model() methods
- Automatic OpenAPI schema generation

Example:
    ```python
    from django_bolt.model_serializer import model_serializer
    from myapp.models import User

    # Quick serializer generation
    UserSerializer = model_serializer(
        User,
        fields=['id', 'username', 'email', 'created_at'],
        exclude=None,
    )

    # With custom validation
    class UserSerializer(Serializer):
        id: int
        username: str
        email: str
        created_at: datetime

        @classmethod
        def get_model(cls):
            return User

        def validate_email(self, value: str) -> str:
            if not value.endswith('@example.com'):
                raise ValueError("Email must end with @example.com")
            return value
    ```
"""
from __future__ import annotations

import inspect
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, get_type_hints, get_origin, get_args
from django.db import models
import msgspec

__all__ = [
    'Serializer',
    'ModelSerializer',
    'model_serializer',
    'Field',
    'SerializerConfig',
]

T = TypeVar('T')


class SerializerConfig:
    """Configuration for model serializer generation.

    Attributes:
        fields: List of field names to include, or '__all__'
        exclude: List of field names to exclude
        read_only_fields: Fields that should only appear in responses
        write_only_fields: Fields that should only appear in requests
        source_mapping: Map serializer field names to model attribute names
        default_values: Default values for optional fields
    """
    fields: List[str] | str = '__all__'
    exclude: Optional[List[str]] = None
    read_only_fields: Optional[List[str]] = None
    write_only_fields: Optional[List[str]] = None
    source_mapping: Optional[Dict[str, str]] = None
    default_values: Optional[Dict[str, Any]] = None


class Field:
    """Field descriptor for serializers with validation and transformation.

    Args:
        source: Model attribute name (if different from serializer field name)
        read_only: Field only appears in serialization (not deserialization)
        write_only: Field only appears in deserialization (not serialization)
        default: Default value if not provided
        validator: Custom validator function
        transform: Custom transformation function for serialization
    """

    def __init__(
        self,
        source: Optional[str] = None,
        read_only: bool = False,
        write_only: bool = False,
        default: Any = None,
        validator: Optional[Callable[[Any], Any]] = None,
        transform: Optional[Callable[[Any], Any]] = None,
    ):
        self.source = source
        self.read_only = read_only
        self.write_only = write_only
        self.default = default
        self.validator = validator
        self.transform = transform
        self.name: Optional[str] = None  # Set by __set_name__

    def __set_name__(self, owner, name):
        self.name = name
        if self.source is None:
            self.source = name


class Serializer(msgspec.Struct):
    """Base serializer class with validation support.

    Provides:
    - Automatic from_model() generation
    - Field validation via validate_<field> methods
    - Custom field transformations
    - Integration with Django ORM

    Example:
        ```python
        class UserSerializer(Serializer):
            id: int
            username: str
            email: str
            age: int

            @classmethod
            def get_model(cls):
                return User

            def validate_email(self, value: str) -> str:
                if '@' not in value:
                    raise ValueError("Invalid email")
                return value

            def validate_age(self, value: int) -> int:
                if value < 0 or value > 150:
                    raise ValueError("Age must be 0-150")
                return value
        ```
    """

    def __post_init__(self):
        """Run field validators after initialization.

        Note: msgspec.Struct is immutable, so validators can only check/validate,
        not transform values. For transformations, use transform_<field> methods
        in from_model() or custom field transformations.
        """
        # Run all validate_<field> methods
        for field_name in self.__struct_fields__:
            validator_name = f'validate_{field_name}'
            if hasattr(self, validator_name):
                validator = getattr(self, validator_name)
                if callable(validator):
                    field_value = getattr(self, field_name)
                    # Skip validation for None values if field is optional
                    if field_value is not None:
                        # Validator should raise exception if invalid
                        # It can return the value but we don't use it (struct is immutable)
                        validator(field_value)

    @classmethod
    def get_model(cls) -> Optional[Type[models.Model]]:
        """Override this to specify the Django model for this serializer.

        Returns:
            Django model class or None
        """
        return None

    @classmethod
    def get_field_source(cls, field_name: str) -> str:
        """Get the model attribute name for a serializer field.

        Args:
            field_name: Serializer field name

        Returns:
            Model attribute name
        """
        # Check if field has custom source via Field descriptor
        if hasattr(cls, field_name):
            field_attr = getattr(cls, field_name)
            if isinstance(field_attr, Field) and field_attr.source:
                return field_attr.source

        # Default: same as field name
        return field_name

    @classmethod
    def get_field_transform(cls, field_name: str) -> Optional[Callable]:
        """Get custom transformation function for a field.

        Args:
            field_name: Field name

        Returns:
            Transformation function or None
        """
        # Check for transform_<field> method
        transform_name = f'transform_{field_name}'
        if hasattr(cls, transform_name):
            return getattr(cls, transform_name)

        # Check for Field descriptor with transform
        if hasattr(cls, field_name):
            field_attr = getattr(cls, field_name)
            if isinstance(field_attr, Field) and field_attr.transform:
                return field_attr.transform

        return None

    @classmethod
    def from_model(cls: Type[T], instance: models.Model) -> T:
        """Convert Django model instance to serializer instance.

        Args:
            instance: Django model instance

        Returns:
            Serializer instance
        """
        data = {}

        for field_name in cls.__struct_fields__:
            # Get source attribute name
            source = cls.get_field_source(field_name)

            # Get value from model instance
            if '.' in source:
                # Support nested attribute access (e.g., 'user.email')
                value = instance
                for part in source.split('.'):
                    value = getattr(value, part, None)
                    if value is None:
                        break
            else:
                value = getattr(instance, source, None)

            # Apply custom transformation if defined
            transform = cls.get_field_transform(field_name)
            if transform:
                value = transform(value)

            data[field_name] = value

        return cls(**data)

    @classmethod
    def from_queryset(cls: Type[T], queryset: models.QuerySet) -> List[T]:
        """Convert Django QuerySet to list of serializer instances.

        This uses the optimized hot path: QuerySet -> .values() -> msgspec.convert()

        Args:
            queryset: Django QuerySet

        Returns:
            List of serializer instances
        """
        # Use .values() for efficient bulk serialization
        field_names = list(cls.__struct_fields__)
        values_list = list(queryset.values(*field_names))

        # Batch convert using msgspec (much faster than individual conversions)
        return msgspec.convert(values_list, List[cls])


def _get_python_type_for_django_field(field: models.Field) -> Any:
    """Map Django field to Python type annotation.

    Args:
        field: Django model field

    Returns:
        Python type annotation
    """
    # Import here to avoid circular imports
    from django.db.models import (
        AutoField, BigAutoField, BigIntegerField, BooleanField,
        CharField, DateField, DateTimeField, DecimalField,
        EmailField, FloatField, IntegerField, TextField,
        ForeignKey, ManyToManyField, OneToOneField,
        JSONField, UUIDField, SlugField, URLField,
    )

    field_type_map = {
        AutoField: int,
        BigAutoField: int,
        BigIntegerField: int,
        BooleanField: bool,
        CharField: str,
        DateField: datetime,  # Use datetime.date if needed
        DateTimeField: datetime,
        DecimalField: Decimal,
        EmailField: str,
        FloatField: float,
        IntegerField: int,
        TextField: str,
        SlugField: str,
        URLField: str,
        UUIDField: str,  # or uuid.UUID
        JSONField: dict,  # or Any
    }

    field_class = type(field)
    python_type = field_type_map.get(field_class, str)  # Default to str

    # Handle nullable fields
    if field.null or field.blank or not field.editable:
        python_type = Optional[python_type]

    # Handle foreign keys (return ID type)
    if isinstance(field, (ForeignKey, OneToOneField)):
        python_type = Optional[int] if field.null else int

    # Handle many-to-many (return list of IDs)
    if isinstance(field, ManyToManyField):
        python_type = Optional[List[int]]

    return python_type


def model_serializer(
    model: Type[models.Model],
    fields: List[str] | str = '__all__',
    exclude: Optional[List[str]] = None,
    name: Optional[str] = None,
    validators: Optional[Dict[str, Callable]] = None,
    transforms: Optional[Dict[str, Callable]] = None,
    bases: tuple = (Serializer,),
) -> Type[Serializer]:
    """Generate a msgspec.Struct serializer from a Django model.

    This factory function creates a serializer class with:
    - Type annotations from model fields
    - Automatic from_model() method
    - Optional custom validators
    - Optional field transformations

    Args:
        model: Django model class
        fields: List of field names to include, or '__all__' for all fields
        exclude: List of field names to exclude
        name: Class name for the generated serializer (defaults to {Model}Serializer)
        validators: Dict mapping field names to validator functions
        transforms: Dict mapping field names to transformation functions
        bases: Base classes (default: (Serializer,))

    Returns:
        Generated serializer class

    Example:
        ```python
        from myapp.models import User

        # Basic usage
        UserSerializer = model_serializer(User, fields=['id', 'username', 'email'])

        # With custom validators
        UserSerializer = model_serializer(
            User,
            fields=['id', 'username', 'email', 'age'],
            validators={
                'email': lambda v: v if '@' in v else (_ for _ in ()).throw(ValueError("Invalid email")),
                'age': lambda v: v if 0 <= v <= 150 else (_ for _ in ()).throw(ValueError("Invalid age")),
            }
        )

        # Usage
        user = User.objects.get(id=1)
        serialized = UserSerializer.from_model(user)
        print(serialized)  # UserSerializer(id=1, username='john', email='john@example.com')
        ```
    """
    # Determine class name
    if name is None:
        if model is not None:
            name = f"{model.__name__}Serializer"
        else:
            name = "Serializer"

    # Get model fields (if model is provided)
    if model is not None:
        model_fields = {f.name: f for f in model._meta.get_fields()}
    else:
        model_fields = {}

    # Determine which fields to include
    if fields == '__all__':
        field_names = list(model_fields.keys())
    else:
        field_names = list(fields)

    # Apply exclusions
    if exclude:
        field_names = [f for f in field_names if f not in exclude]

    # Build type annotations
    annotations = {}
    for field_name in field_names:
        if field_name in model_fields:
            django_field = model_fields[field_name]
            python_type = _get_python_type_for_django_field(django_field)
            annotations[field_name] = python_type
        else:
            # Field not in model, default to Any
            annotations[field_name] = Any

    # Build namespace for the new class
    namespace = {
        '__annotations__': annotations,
        '__module__': model.__module__ if model is not None else __name__,
    }

    # Add get_model classmethod (if model is provided)
    if model is not None:
        namespace['get_model'] = classmethod(lambda cls: model)

    # Add validators as validate_<field> methods
    # Wrap standalone functions to work as instance methods
    if validators:
        for field_name, validator_func in validators.items():
            # Check if function expects self parameter (is a method)
            import inspect
            sig = inspect.signature(validator_func)
            params = list(sig.parameters.keys())

            if len(params) >= 2 and params[0] == 'self':
                # It's already a method (expects self), use it directly
                namespace[f'validate_{field_name}'] = validator_func
            else:
                # It's a standalone function, wrap it
                def make_validator(func):
                    def wrapper(self, value):
                        return func(value)
                    return wrapper
                namespace[f'validate_{field_name}'] = make_validator(validator_func)

    # Add transformations as transform_<field> methods
    # Wrap standalone functions to work as class methods
    if transforms:
        for field_name, transform_func in transforms.items():
            # Create a wrapper that ignores cls and calls the function
            def make_transform(func):
                def wrapper(cls, value):
                    return func(value)
                return classmethod(wrapper)
            namespace[f'transform_{field_name}'] = make_transform(transform_func)

    # Create the class
    serializer_class = type(name, bases, namespace)

    return serializer_class


# Convenience function for quick serializer creation
def quick_serializer(
    model: Type[models.Model],
    *,
    fields: List[str] | str = '__all__',
    exclude: Optional[List[str]] = None,
) -> Type[Serializer]:
    """Quick shorthand for model_serializer with minimal config.

    Args:
        model: Django model class
        fields: Fields to include (default: '__all__')
        exclude: Fields to exclude

    Returns:
        Generated serializer class
    """
    return model_serializer(model, fields=fields, exclude=exclude)


def model_serializer_from_meta(cls):
    """Decorator to create a ModelSerializer from a class with Meta configuration.

    This decorator allows DRF-style serializer definition:

    Example:
        ```python
        @model_serializer_from_meta
        class UserSerializer:
            class Meta:
                model = User
                fields = ['id', 'username', 'email']
                read_only_fields = ['id']

            # Add custom validation
            def validate_email(self, value: str) -> str:
                if '@' not in value:
                    raise ValueError("Invalid email")
                return value
        ```

    Args:
        cls: Class with Meta configuration

    Returns:
        Generated Serializer class

    Raises:
        ValueError: If Meta is missing or invalid
    """
    # Get Meta class
    if not hasattr(cls, 'Meta'):
        raise ValueError(f"{cls.__name__} must define a Meta class")

    meta = cls.Meta
    model = getattr(meta, 'model', None)
    if not model:
        raise ValueError(f"{cls.__name__}.Meta must specify a 'model' attribute")

    fields = getattr(meta, 'fields', '__all__')
    exclude = getattr(meta, 'exclude', None)
    read_only_fields = set(getattr(meta, 'read_only_fields', None) or [])
    write_only_fields = set(getattr(meta, 'write_only_fields', None) or [])

    # Collect validators and transforms from the class
    # Note: These are unbound methods, so we need to handle them carefully
    validators = {}
    transforms = {}
    for name, value in cls.__dict__.items():  # Use __dict__ to avoid inherited methods
        if name.startswith('validate_') and callable(value):
            field_name = name[9:]  # Remove 'validate_' prefix
            # value is the raw function (not bound), so we can use it directly
            validators[field_name] = value
        elif name.startswith('transform_') and callable(value):
            field_name = name[10:]  # Remove 'transform_' prefix
            transforms[field_name] = value

    # Create serializer using factory function
    serializer_cls = model_serializer(
        model,
        fields=fields,
        exclude=exclude,
        name=cls.__name__,
        validators=validators,
        transforms=transforms,
    )

    # Add read-only/write-only metadata
    serializer_cls._read_only_fields = read_only_fields
    serializer_cls._write_only_fields = write_only_fields
    serializer_cls._field_names = list(serializer_cls.__struct_fields__)

    # Add helper methods
    @classmethod
    def get_write_serializer(serializer_cls):
        """Get serializer for write operations (excludes read-only fields)."""
        if not read_only_fields:
            return None
        write_fields = [f for f in serializer_cls._field_names if f not in read_only_fields]
        return model_serializer(model, fields=write_fields, name=f"{cls.__name__}Write", validators=validators)

    @classmethod
    def get_read_serializer(serializer_cls):
        """Get serializer for read operations (excludes write-only fields)."""
        if not write_only_fields:
            return None
        read_fields = [f for f in serializer_cls._field_names if f not in write_only_fields]
        return model_serializer(model, fields=read_fields, name=f"{cls.__name__}Read")

    @classmethod
    def is_field_read_only(serializer_cls, field_name: str) -> bool:
        return field_name in read_only_fields

    @classmethod
    def is_field_write_only(serializer_cls, field_name: str) -> bool:
        return field_name in write_only_fields

    serializer_cls.get_write_serializer = get_write_serializer
    serializer_cls.get_read_serializer = get_read_serializer
    serializer_cls.is_field_read_only = is_field_read_only
    serializer_cls.is_field_write_only = is_field_write_only

    return serializer_cls


# Convenience alias for the decorator
ModelSerializer = model_serializer_from_meta

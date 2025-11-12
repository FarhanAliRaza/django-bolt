"""
Model Serializers for Django-Bolt.

Provides DRF-style ModelSerializer with msgspec-powered performance.
Automatically generates serializer fields from Django models.

Example:
    from django_bolt.serializers import create_model_serializer
    from myapp.models import User

    UserSerializer = create_model_serializer(
        User,
        fields=['id', 'username', 'email'],
        read_only_fields=['id']
    )

    # Usage:
    user = await User.objects.aget(id=1)
    data = UserSerializer.from_model(user)
    return data  # Auto-serialized to JSON
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, get_origin, get_args
from datetime import datetime, date, time
from decimal import Decimal
import msgspec

if TYPE_CHECKING:
    from django.db.models import Model, Field

T = TypeVar('T')


def _get_python_type_for_django_field(field: Field) -> type:
    """
    Map Django field type to Python type annotation.

    Args:
        field: Django model field

    Returns:
        Python type for annotation
    """
    from django.db import models

    # Map Django fields to Python types
    field_type_map = {
        models.IntegerField: int,
        models.BigIntegerField: int,
        models.SmallIntegerField: int,
        models.PositiveIntegerField: int,
        models.PositiveSmallIntegerField: int,
        models.PositiveBigIntegerField: int,
        models.AutoField: int,
        models.BigAutoField: int,
        models.SmallAutoField: int,
        models.CharField: str,
        models.TextField: str,
        models.EmailField: str,
        models.URLField: str,
        models.SlugField: str,
        models.UUIDField: str,
        models.BooleanField: bool,
        models.FloatField: float,
        models.DecimalField: Decimal,
        models.DateTimeField: datetime,
        models.DateField: date,
        models.TimeField: time,
        models.JSONField: dict,
        models.BinaryField: bytes,
    }

    # Get base type by checking field class hierarchy
    python_type = Any
    for field_class, py_type in field_type_map.items():
        if isinstance(field, field_class):
            python_type = py_type
            break

    # Handle relationships
    if isinstance(field, models.ForeignKey):
        # Return int (pk) for serialization by default
        python_type = int
    elif isinstance(field, models.ManyToManyField):
        # Return list of ints (pks)
        python_type = list[int]
    elif isinstance(field, models.OneToOneField):
        python_type = int

    # Handle nullable/optional fields
    if field.null or (hasattr(field, 'blank') and field.blank and not isinstance(field, models.BooleanField)):
        # Make type optional
        python_type = python_type | None

    return python_type


def create_model_serializer(
    model: type[Model],
    *,
    name: str | None = None,
    fields: list[str] | str = '__all__',
    exclude: list[str] | None = None,
    read_only_fields: list[str] | None = None,
    extra_fields: dict[str, tuple[type, Any]] | None = None,
) -> type[msgspec.Struct]:
    """
    Create a ModelSerializer dynamically from a Django model.

    This function generates a msgspec.Struct class with fields from the Django model.

    Args:
        model: Django model class to serialize
        name: Name for the serializer class (defaults to <Model>Serializer)
        fields: List of field names or '__all__' to include all fields
        exclude: List of field names to exclude
        read_only_fields: List of read-only field names (informational only)
        extra_fields: Additional custom fields as {name: (type, default)}

    Returns:
        msgspec.Struct subclass with generated fields and from_model() classmethod

    Example:
        UserSerializer = create_model_serializer(
            User,
            fields=['id', 'username', 'email'],
            read_only_fields=['id']
        )

        user = await User.objects.aget(id=1)
        data = UserSerializer.from_model(user)
    """
    if name is None:
        name = f"{model.__name__}Serializer"

    # Get fields to include
    if fields == '__all__':
        field_names = [f.name for f in model._meta.get_fields()
                      if not f.many_to_many or not f.auto_created]
    else:
        field_names = list(fields)

    # Exclude fields
    if exclude:
        field_names = [f for f in field_names if f not in exclude]

    # Build field annotations
    annotations = {}
    defaults = {}

    for field_name in field_names:
        try:
            model_field = model._meta.get_field(field_name)
            python_type = _get_python_type_for_django_field(model_field)
            annotations[field_name] = python_type

            # Set default if field has one or is nullable
            if model_field.null or (hasattr(model_field, 'blank') and model_field.blank):
                defaults[field_name] = None
        except Exception:
            # Field doesn't exist on model, skip
            continue

    # Add extra custom fields
    if extra_fields:
        for field_name, (field_type, default_value) in extra_fields.items():
            annotations[field_name] = field_type
            if default_value is not msgspec.NODEFAULT:
                defaults[field_name] = default_value

    # Create struct using msgspec.defstruct
    field_list = [(fname, ftype, defaults.get(fname, msgspec.NODEFAULT))
                  for fname, ftype in annotations.items()]

    serializer_cls = msgspec.defstruct(
        name,
        field_list,
        kw_only=True,
        omit_defaults=True
    )

    # Add from_model classmethod
    def from_model(cls, instance: Model):
        """Create serializer instance from Django model instance."""
        if instance is None:
            raise ValueError("Cannot serialize None instance")

        data = {}
        for field_name in annotations.keys():
            try:
                value = getattr(instance, field_name, None)

                if value is None:
                    data[field_name] = None
                elif hasattr(value, 'all'):
                    # ManyToMany - get PKs
                    data[field_name] = [obj.pk for obj in value.all()]
                elif hasattr(value, '_meta'):
                    # ForeignKey - get PK
                    data[field_name] = value.pk if value else None
                else:
                    data[field_name] = value
            except AttributeError:
                data[field_name] = None

        return cls(**data)

    # Add to_model method
    def to_model(self, instance: Model | None = None) -> Model:
        """Update or create model instance from serializer data."""
        if instance is None:
            instance = model()

        read_only = set(read_only_fields or [])

        for field_name in annotations.keys():
            if field_name in read_only:
                continue

            if not hasattr(instance, field_name):
                continue

            value = getattr(self, field_name, None)
            if value is None:
                continue

            try:
                setattr(instance, field_name, value)
            except Exception:
                # Skip fields that can't be set directly
                continue

        return instance

    # Add async save
    async def asave(self, instance: Model | None = None) -> Model:
        """Async save to database."""
        instance = self.to_model(instance)
        await instance.asave()
        return instance

    # Attach methods to class
    serializer_cls.from_model = classmethod(from_model)
    serializer_cls.to_model = to_model
    serializer_cls.asave = asave
    serializer_cls._model = model
    serializer_cls._read_only_fields = set(read_only_fields or [])

    return serializer_cls


# Convenience alias
ModelSerializer = create_model_serializer

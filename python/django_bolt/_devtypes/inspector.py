from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass
class FieldInfo:
    name: str
    py_type: str
    optional: bool
    filter_names: list[str]


@dataclass
class RelationInfo:
    name: str
    target: str
    kind: str  # "fk" | "m2m" | "o2o"


@dataclass
class ModelInfo:
    app_label: str
    module: str
    name: str
    full_name: str  # dotted path
    fields: List[FieldInfo]
    relations: List[RelationInfo]


DJANGO_TO_PY: Dict[str, str] = {
    "AutoField": "int",
    "BigAutoField": "int",
    "IntegerField": "int",
    "BigIntegerField": "int",
    "SmallIntegerField": "int",
    "FloatField": "float",
    "DecimalField": "float",
    "BooleanField": "bool",
    "CharField": "str",
    "TextField": "str",
    "EmailField": "str",
    "URLField": "str",
    "SlugField": "str",
    "UUIDField": "str",
    "DateField": "datetime.date",
    "DateTimeField": "datetime.datetime",
    "TimeField": "datetime.time",
    "JSONField": "dict[str, Any]",
    "BinaryField": "bytes",
}


def _python_type_for_field(field: Any) -> Tuple[str, bool]:
    """Map a Django field to a Python type string and optional flag."""
    from django.db import models

    # Relations handled elsewhere
    if isinstance(field, (models.ForeignKey, models.OneToOneField, models.ManyToManyField)):
        return ("int", bool(getattr(field, "null", False)))  # FKs → pk type approx

    cls_name = field.__class__.__name__
    py = DJANGO_TO_PY.get(cls_name, "Any")
    # Nullability → Optional
    optional = bool(getattr(field, "null", False))
    return (py, optional)


def collect_model_metadata() -> List[ModelInfo]:
    """Load Django apps and collect minimal model metadata for stub emission."""
    from django.apps import apps as django_apps

    model_infos: List[ModelInfo] = []
    for model in django_apps.get_models():
        app_label = model._meta.app_label
        module = model.__module__
        name = model.__name__
        full_name = f"{module}.{name}"

        # Fields
        fields: List[FieldInfo] = []
        relations: List[RelationInfo] = []

        for f in model._meta.get_fields():
            # Relations (collect first to build filter aliases)
            if getattr(f, "is_relation", False):
                if f.many_to_many:
                    target = f.related_model.__name__ if f.related_model else "Any"
                    relations.append(RelationInfo(name=f.name, target=target, kind="m2m"))
                elif f.one_to_one:
                    target = f.related_model.__name__ if f.related_model else "Any"
                    relations.append(RelationInfo(name=f.name, target=target, kind="o2o"))
                elif f.many_to_one:
                    target = f.related_model.__name__ if f.related_model else "Any"
                    relations.append(RelationInfo(name=f.name, target=target, kind="fk"))

        for f in model._meta.get_fields():
            # Concrete database-backed fields (skip auto-created relation accessors)
            if hasattr(f, "attname") and not (getattr(f, "auto_created", False) and not getattr(f, "primary_key", False)):
                py, optional = _python_type_for_field(f)
                # Default filter name is the attribute name
                filters = [f.name]
                # For FK, also expose `<name>_id` as an alternate filter
                if getattr(f, "is_relation", False) and getattr(f, "many_to_one", False):
                    filters.append(f"{f.name}_id")
                fields.append(FieldInfo(name=f.name, py_type=py, optional=optional, filter_names=filters))

        # Ensure primary key filter aliases are present (id/pk)
        try:
            pk_field = model._meta.pk  # type: ignore[attr-defined]
        except Exception:
            pk_field = None
        if pk_field is not None:
            py, optional = _python_type_for_field(pk_field)
            # Find existing entry for pk field name if present
            existing = next((fi for fi in fields if fi.name == pk_field.name), None)
            if existing is None:
                fields.append(
                    FieldInfo(
                        name=pk_field.name,
                        py_type=py,
                        optional=optional,
                        filter_names=[pk_field.name, "pk", "id"],
                    )
                )
            else:
                # Merge aliases
                for alias in ("pk", "id"):
                    if alias not in existing.filter_names:
                        existing.filter_names.append(alias)

        model_infos.append(
            ModelInfo(
                app_label=app_label,
                module=module,
                name=name,
                full_name=full_name,
                fields=fields,
                relations=relations,
            )
        )

    return model_infos



"""
Model introspection utilities for extracting field information from Django models.

This module provides utilities similar to Django REST Framework's model_meta module,
enabling comprehensive introspection of Django model fields and relationships.

Usage:
    from django_bolt.serializers.model_meta import get_field_info

    info = get_field_info(MyModel)
    print(info.pk)  # Primary key field
    print(info.fields)  # Regular fields
    print(info.forward_relations)  # ForeignKey, OneToOne, M2M
    print(info.reverse_relations)  # Reverse relations
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, NamedTuple

from django.db import models

if TYPE_CHECKING:
    pass


class RelationInfo(NamedTuple):
    """
    Information about a model relationship field.

    Attributes:
        model_field: The Django model field instance (None for reverse relations)
        related_model: The related model class
        to_many: True if this is a many-to-many or reverse many relation
        to_field: The field on the related model (for to_field FK)
        has_through_model: True if M2M has explicit through model
        reverse: True if this is a reverse relation
    """

    model_field: models.Field | None
    related_model: type[models.Model]
    to_many: bool
    to_field: str | None
    has_through_model: bool
    reverse: bool


class FieldInfo(NamedTuple):
    """
    Comprehensive information about a model's fields.

    Attributes:
        pk: The primary key field
        fields: Dict of regular field name -> field instance
        forward_relations: Dict of forward relation name -> RelationInfo
        reverse_relations: Dict of reverse relation name -> RelationInfo
        fields_and_pk: Combined dict of pk + fields
        relations: Combined dict of forward + reverse relations
    """

    pk: models.Field
    fields: dict[str, models.Field]
    forward_relations: dict[str, RelationInfo]
    reverse_relations: dict[str, RelationInfo]
    fields_and_pk: dict[str, models.Field]
    relations: dict[str, RelationInfo]


def get_field_info(model: type[models.Model]) -> FieldInfo:
    """
    Given a model class, returns a FieldInfo instance containing metadata
    about all field types on the model including relationships.

    Args:
        model: Django model class

    Returns:
        FieldInfo namedtuple with comprehensive field information

    Example:
        >>> from django.contrib.auth.models import User
        >>> info = get_field_info(User)
        >>> info.pk.name
        'id'
        >>> 'username' in info.fields
        True
    """
    # Get concrete model options
    opts = model._meta.concrete_model._meta

    pk = _get_pk(opts)
    fields = _get_fields(opts)
    forward_relations = _get_forward_relationships(opts)
    reverse_relations = _get_reverse_relationships(opts)
    fields_and_pk = _merge_fields_and_pk(pk, fields)
    relations = _merge_relationships(forward_relations, reverse_relations)

    return FieldInfo(
        pk=pk,
        fields=fields,
        forward_relations=forward_relations,
        reverse_relations=reverse_relations,
        fields_and_pk=fields_and_pk,
        relations=relations,
    )


def _get_pk(opts: Any) -> models.Field:
    """
    Get the primary key field, handling multi-table inheritance.

    For models with multi-table inheritance, traverses to the parent's PK.
    """
    pk = opts.pk
    rel = pk.remote_field

    while rel and rel.parent_link:
        # If model is a child via multi-table inheritance, use parent's pk
        pk = pk.remote_field.model._meta.pk
        rel = pk.remote_field

    return pk


def _get_fields(opts: Any) -> dict[str, models.Field]:
    """
    Get all regular (non-relational) fields from model.

    Returns dict of field_name -> field_instance for fields that:
    - Have serialize=True
    - Are not relations (no remote_field)
    """
    fields = {}
    for field in opts.fields:
        if field.serialize and not field.remote_field:
            fields[field.name] = field
    return fields


def _get_to_field(field: models.Field) -> str | None:
    """Get the to_field for a relation, if specified."""
    to_fields = getattr(field, "to_fields", None)
    if to_fields:
        return to_fields[0]
    return None


def _get_forward_relationships(opts: Any) -> dict[str, RelationInfo]:
    """
    Get all forward relationships (ForeignKey, OneToOne, ManyToMany).

    Returns dict of field_name -> RelationInfo.
    """
    forward_relations = {}

    # ForeignKey and OneToOneField
    for field in opts.fields:
        if field.serialize and field.remote_field:
            forward_relations[field.name] = RelationInfo(
                model_field=field,
                related_model=field.remote_field.model,
                to_many=False,
                to_field=_get_to_field(field),
                has_through_model=False,
                reverse=False,
            )

    # ManyToManyField
    for field in opts.many_to_many:
        if field.serialize:
            forward_relations[field.name] = RelationInfo(
                model_field=field,
                related_model=field.remote_field.model,
                to_many=True,
                to_field=None,  # M2M doesn't have to_field
                has_through_model=(
                    not field.remote_field.through._meta.auto_created
                ),
                reverse=False,
            )

    return forward_relations


def _get_reverse_relationships(opts: Any) -> dict[str, RelationInfo]:
    """
    Get all reverse relationships.

    Returns dict of accessor_name -> RelationInfo.
    """
    reverse_relations = {}

    # Reverse ForeignKey and OneToOneField
    all_related_objects = [
        r for r in opts.related_objects if not r.field.many_to_many
    ]
    for relation in all_related_objects:
        accessor_name = relation.get_accessor_name()
        reverse_relations[accessor_name] = RelationInfo(
            model_field=None,
            related_model=relation.related_model,
            to_many=relation.field.remote_field.multiple,
            to_field=_get_to_field(relation.field),
            has_through_model=False,
            reverse=True,
        )

    # Reverse ManyToManyField
    all_related_many_to_many = [
        r for r in opts.related_objects if r.field.many_to_many
    ]
    for relation in all_related_many_to_many:
        accessor_name = relation.get_accessor_name()
        through = getattr(relation.field.remote_field, "through", None)
        reverse_relations[accessor_name] = RelationInfo(
            model_field=None,
            related_model=relation.related_model,
            to_many=True,
            to_field=None,
            has_through_model=(
                through is not None and not through._meta.auto_created
            ),
            reverse=True,
        )

    return reverse_relations


def _merge_fields_and_pk(
    pk: models.Field, fields: dict[str, models.Field]
) -> dict[str, models.Field]:
    """Merge pk and fields into a single dict."""
    fields_and_pk = {"pk": pk, pk.name: pk}
    fields_and_pk.update(fields)
    return fields_and_pk


def _merge_relationships(
    forward: dict[str, RelationInfo], reverse: dict[str, RelationInfo]
) -> dict[str, RelationInfo]:
    """Merge forward and reverse relations into a single dict."""
    return {**forward, **reverse}


def is_abstract_model(model: type[models.Model]) -> bool:
    """
    Check if a model is abstract.

    Args:
        model: Django model class

    Returns:
        True if the model is abstract, False otherwise
    """
    return (
        hasattr(model, "_meta")
        and hasattr(model._meta, "abstract")
        and model._meta.abstract
    )


def get_all_field_names(model: type[models.Model]) -> list[str]:
    """
    Get all field names for a model including relations.

    Args:
        model: Django model class

    Returns:
        List of all field names
    """
    info = get_field_info(model)
    return (
        [info.pk.name]
        + list(info.fields.keys())
        + list(info.forward_relations.keys())
    )


def get_unique_together_constraints(
    model: type[models.Model],
) -> list[tuple[tuple[str, ...], Any, list[str], Any]]:
    """
    Get all unique together constraints for a model.

    Includes both Meta.unique_together and UniqueConstraint with multiple fields.

    Args:
        model: Django model class

    Returns:
        List of tuples: (fields, queryset, condition_fields, condition)
    """
    constraints = []

    for parent_class in [model] + list(model._meta.parents):
        # Handle Meta.unique_together
        for unique_together in parent_class._meta.unique_together:
            constraints.append(
                (tuple(unique_together), model._default_manager, [], None)
            )

        # Handle UniqueConstraint
        for constraint in parent_class._meta.constraints:
            if (
                isinstance(constraint, models.UniqueConstraint)
                and len(constraint.fields) > 1
            ):
                condition_fields = []
                if constraint.condition is not None:
                    # Extract field names from Q object
                    condition_fields = _get_fields_from_q(constraint.condition)
                constraints.append(
                    (
                        tuple(constraint.fields),
                        model._default_manager,
                        condition_fields,
                        constraint.condition,
                    )
                )

    return constraints


def _get_fields_from_q(q_object: Any) -> list[str]:
    """
    Extract field names referenced in a Q object.

    Args:
        q_object: Django Q object

    Returns:
        List of field names referenced in the Q object
    """
    fields = []

    # Handle children of Q object
    for child in getattr(q_object, "children", []):
        if isinstance(child, tuple):
            # Leaf node: (field__lookup, value)
            field_lookup = child[0]
            field_name = field_lookup.split("__")[0]
            fields.append(field_name)
        else:
            # Nested Q object
            fields.extend(_get_fields_from_q(child))

    return fields


def get_unique_field_names(model: type[models.Model]) -> set[str]:
    """
    Get all field names that have unique=True.

    Args:
        model: Django model class

    Returns:
        Set of field names with unique constraint
    """
    unique_fields = set()
    for field in model._meta.get_fields():
        if getattr(field, "unique", False):
            unique_fields.add(field.name)
    return unique_fields


__all__ = [
    "FieldInfo",
    "RelationInfo",
    "get_field_info",
    "is_abstract_model",
    "get_all_field_names",
    "get_unique_together_constraints",
    "get_unique_field_names",
]

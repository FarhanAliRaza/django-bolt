from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .base import BaseSchemaObject

if TYPE_CHECKING:
    from .encoding import Encoding
    from .example import Example
    from .reference import Reference
    from .schema import Schema

__all__ = ("OpenAPIMediaType",)


@dataclass
class OpenAPIMediaType(BaseSchemaObject):
    """Each Media Type Object provides schema and examples for the media type identified by its key."""

    schema: Reference | Schema | None = None
    """The schema defining the content of the request, response, or parameter."""

    example: Any | None = None
    """Example of the media type.

    The example object SHOULD be in the correct format as specified by the media type.

    The ``example`` field is mutually exclusive of the ``examples`` field.

    Furthermore, if referencing a ``schema`` which contains an example, the ``example`` value SHALL _override_ the
    example provided by the schema.
    """

    examples: dict[str, Example | Reference] | None = None
    """Examples of the media type.

    Each example object SHOULD match the media type and specified schema if present.

    The ``examples`` field is mutually exclusive of the ``example`` field.

    Furthermore, if referencing a ``schema`` which contains an example, the ``examples`` value SHALL _override_ the
    example provided by the schema.
    """

    encoding: dict[str, Encoding] | None = None
    """A map between a property name and its encoding information.

    The key, being the property name, MUST exist in the schema as a property. The encoding object SHALL only apply to
    ``requestBody`` objects when the media type is ``multipart`` or ``application/x-www-form-urlencoded``.
    """

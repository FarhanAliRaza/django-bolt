from __future__ import annotations

from enum import Enum

__all__ = ("MediaType",)


class MediaType(str, Enum):
    """Content-Type header values."""

    JSON = "application/json"
    HTML = "text/html"
    TEXT = "text/plain"
    CSS = "text/css"
    XML = "application/xml"
    MESSAGEPACK = "application/vnd.msgpack"

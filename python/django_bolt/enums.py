from __future__ import annotations

from enum import Enum

__all__ = ("MediaType", "FileSize")


class MediaType(str, Enum):
    """Content-Type header values."""

    JSON = "application/json"
    HTML = "text/html"
    TEXT = "text/plain"
    CSS = "text/css"
    XML = "application/xml"
    MESSAGEPACK = "application/vnd.msgpack"


class FileSize(int, Enum):
    """Common file size limits in bytes for upload validation (binary units)."""

    MB_1 = 1 * 1024 * 1024  # 1 MiB = 1,048,576 bytes
    MB_2 = 2 * 1024 * 1024
    MB_3 = 3 * 1024 * 1024
    MB_4 = 4 * 1024 * 1024
    MB_5 = 5 * 1024 * 1024
    MB_6 = 6 * 1024 * 1024
    MB_7 = 7 * 1024 * 1024
    MB_8 = 8 * 1024 * 1024
    MB_9 = 9 * 1024 * 1024
    MB_10 = 10 * 1024 * 1024
    MB_20 = 20 * 1024 * 1024
    MB_30 = 30 * 1024 * 1024
    MB_40 = 40 * 1024 * 1024
    MB_50 = 50 * 1024 * 1024
    MB_60 = 60 * 1024 * 1024
    MB_70 = 70 * 1024 * 1024
    MB_80 = 80 * 1024 * 1024
    MB_90 = 90 * 1024 * 1024
    MB_100 = 100 * 1024 * 1024

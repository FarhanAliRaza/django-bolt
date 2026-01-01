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
    """Common file size limits in bytes for upload validation."""

    MB_1 = 1_000_000
    MB_2 = 2_000_000
    MB_3 = 3_000_000
    MB_4 = 4_000_000
    MB_5 = 5_000_000
    MB_6 = 6_000_000
    MB_7 = 7_000_000
    MB_8 = 8_000_000
    MB_9 = 9_000_000
    MB_10 = 10_000_000
    MB_20 = 20_000_000
    MB_30 = 30_000_000
    MB_40 = 40_000_000
    MB_50 = 50_000_000
    MB_60 = 60_000_000
    MB_70 = 70_000_000
    MB_80 = 80_000_000
    MB_90 = 90_000_000
    MB_100 = 100_000_000

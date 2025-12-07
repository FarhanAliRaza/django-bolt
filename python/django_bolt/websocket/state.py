"""WebSocket connection state."""

from __future__ import annotations

from enum import IntEnum, auto


class WebSocketState(IntEnum):
    """Connection state of a WebSocket."""

    CONNECTING = auto()
    CONNECTED = auto()
    DISCONNECTED = auto()

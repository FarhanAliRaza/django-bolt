import msgspec
from typing import Any


class JSON:
    def __init__(self, data: Any):
        self.data = data

    def to_bytes(self) -> bytes:
        return msgspec.json.encode(self.data)




import msgspec
from typing import Any, Dict, Optional


class JSON:
    def __init__(self, data: Any, status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        self.data = data
        self.status_code = status_code
        self.headers = headers or {}

    def to_bytes(self) -> bytes:
        return msgspec.json.encode(self.data)





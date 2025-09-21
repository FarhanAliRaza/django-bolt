from typing import Any, Dict, Optional


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: Any | None = None, headers: Optional[Dict[str, str]] = None):
        super().__init__(detail)
        self.status_code = int(status_code)
        self.detail = detail
        self.headers = headers or {}



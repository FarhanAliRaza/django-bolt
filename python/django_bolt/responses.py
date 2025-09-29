import msgspec
from typing import Any, Dict, Optional


class JSON:
    def __init__(self, data: Any, status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        self.data = data
        self.status_code = status_code
        self.headers = headers or {}

    def to_bytes(self) -> bytes:
        return msgspec.json.encode(self.data)



class PlainText:
    def __init__(self, text: str, status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        self.text = text
        self.status_code = status_code
        self.headers = headers or {}

    def to_bytes(self) -> bytes:
        return self.text.encode()


class HTML:
    def __init__(self, html: str, status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        self.html = html
        self.status_code = status_code
        self.headers = headers or {}

    def to_bytes(self) -> bytes:
        return self.html.encode()


class Redirect:
    def __init__(self, url: str, status_code: int = 307, headers: Optional[Dict[str, str]] = None):
        self.url = url
        self.status_code = status_code
        self.headers = headers or {}


class File:
    def __init__(self, path: str, *, media_type: Optional[str] = None, filename: Optional[str] = None, status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        self.path = path
        self.media_type = media_type
        self.filename = filename
        self.status_code = status_code
        self.headers = headers or {}

    def read_bytes(self) -> bytes:
        with open(self.path, "rb") as f:
            return f.read()


class UploadFile:
    def __init__(self, name: str, filename: Optional[str], content_type: Optional[str], path: str):
        self.name = name
        self.filename = filename
        self.content_type = content_type
        self.path = path

    def read(self) -> bytes:
        with open(self.path, "rb") as f:
            return f.read()



class FileResponse:
    def __init__(
        self,
        path: str,
        *,
        media_type: Optional[str] = None,
        filename: Optional[str] = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.path = path
        self.media_type = media_type
        self.filename = filename
        self.status_code = status_code
        self.headers = headers or {}



class StreamingResponse:
    def __init__(
        self,
        content: Any,
        *,
        status_code: int = 200,
        media_type: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        # content can be an iterator/generator, iterable, or a callable returning an iterator
        self.content = content
        self.status_code = status_code
        self.media_type = media_type or "application/octet-stream"
        self.headers = headers or {}
        # do not enforce type of content here; Rust side will adapt common iterator/callable patterns


import msgspec
from typing import Any, Dict, Optional, List
from pathlib import Path

# Cache for BOLT_ALLOWED_FILE_PATHS - loaded once at server startup
_ALLOWED_FILE_PATHS_CACHE: Optional[List[Path]] = None
_ALLOWED_FILE_PATHS_INITIALIZED = False


def initialize_file_response_settings():
    """
    Initialize FileResponse settings cache at server startup.
    This should be called once when the server starts to cache BOLT_ALLOWED_FILE_PATHS.
    """
    global _ALLOWED_FILE_PATHS_CACHE, _ALLOWED_FILE_PATHS_INITIALIZED

    if _ALLOWED_FILE_PATHS_INITIALIZED:
        return

    try:
        from django.conf import settings
        if hasattr(settings, 'BOLT_ALLOWED_FILE_PATHS'):
            allowed_paths = settings.BOLT_ALLOWED_FILE_PATHS
            if allowed_paths:
                # Resolve all paths once at startup
                _ALLOWED_FILE_PATHS_CACHE = [Path(p).resolve() for p in allowed_paths]
            else:
                _ALLOWED_FILE_PATHS_CACHE = None
        else:
            _ALLOWED_FILE_PATHS_CACHE = None
    except ImportError:
        # Django not configured, allow any path (development mode)
        _ALLOWED_FILE_PATHS_CACHE = None

    _ALLOWED_FILE_PATHS_INITIALIZED = True


class Response:
    """
    Generic HTTP response with custom headers.

    Use this when you need to return a response with custom headers (like Allow for OPTIONS).

    Examples:
        # OPTIONS handler with Allow header
        @api.options("/items")
        async def options_items():
            return Response({}, headers={"Allow": "GET, POST, PUT, DELETE"})

        # Custom response with additional headers
        @api.get("/data")
        async def get_data():
            return Response(
                {"result": "data"},
                status_code=200,
                headers={"X-Custom-Header": "value"}
            )
    """
    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: str = "application/json"
    ):
        self.content = content if content is not None else {}
        self.status_code = status_code
        self.headers = headers or {}
        self.media_type = media_type

    def to_bytes(self) -> bytes:
        if self.media_type == "application/json":
            return msgspec.json.encode(self.content)
        elif isinstance(self.content, str):
            return self.content.encode()
        elif isinstance(self.content, bytes):
            return self.content
        else:
            return str(self.content).encode()


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
        # SECURITY: Validate and canonicalize path to prevent traversal

        # Convert to absolute path and resolve any .. or symlinks
        try:
            resolved_path = Path(path).resolve()
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid file path: {e}")

        # Check if the file exists and is a regular file (not a directory or special file)
        if not resolved_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not resolved_path.is_file():
            raise ValueError(f"Path is not a regular file: {path}")

        # Check against allowed directories if configured (using cached value)
        if _ALLOWED_FILE_PATHS_CACHE is not None:
            # Ensure the resolved path is within one of the allowed directories
            is_allowed = False
            for allowed_path in _ALLOWED_FILE_PATHS_CACHE:
                try:
                    # Check if resolved_path is relative to allowed_path
                    resolved_path.relative_to(allowed_path)
                    is_allowed = True
                    break
                except ValueError:
                    # Not a subpath, continue checking
                    continue

            if not is_allowed:
                raise PermissionError(
                    f"File path '{path}' is not within allowed directories. "
                    f"Configure BOLT_ALLOWED_FILE_PATHS in Django settings."
                )

        self.path = str(resolved_path)
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


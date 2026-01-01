# Response Handling in Django-Bolt

## Overview

Django-Bolt provides a flexible response system that supports multiple content types, streaming, and automatic serialization. Responses are optimized for performance using msgspec for JSON serialization (5-10x faster than stdlib) and Rust-powered file streaming.

## Table of Contents

- [Quick Start](#quick-start)
- [Response Types](#response-types)
  - [JSON (Default)](#json-default)
  - [PlainText](#plaintext)
  - [HTML](#html)
  - [Redirect](#redirect)
  - [File](#file)
  - [FileResponse](#fileresponse)
  - [StreamingResponse](#streamingresponse)
  - [Response (Generic)](#response-generic)
- [Automatic Serialization](#automatic-serialization)
- [Response Model Validation](#response-model-validation)
- [Streaming Responses](#streaming-responses)
  - [Sync Generators](#sync-generators)
  - [Async Generators](#async-generators)
  - [Server-Sent Events (SSE)](#server-sent-events-sse)
- [File Serving](#file-serving)
  - [File vs FileResponse](#file-vs-fileresponse)
  - [Security and Path Validation](#security-and-path-validation)
- [Custom Headers and Status Codes](#custom-headers-and-status-codes)
- [Content-Type Handling](#content-type-handling)
- [Best Practices](#best-practices)

## Quick Start

```python
from django_bolt import BoltAPI
from django_bolt.responses import PlainText, HTML, Redirect, File, FileResponse, StreamingResponse
import msgspec

api = BoltAPI()

# JSON (default) - just return dict/list
@api.get("/users")
async def list_users():
    return {"users": [{"id": 1, "name": "Alice"}]}

# Plain text
@api.get("/health")
async def health():
    return PlainText("OK")

# HTML
@api.get("/home")
async def home():
    return HTML("<h1>Welcome</h1>")

# Redirect
@api.get("/old")
async def old_endpoint():
    return Redirect("/new", status_code=301)

# File download
@api.get("/download")
async def download():
    return FileResponse("/path/to/file.pdf", filename="document.pdf")

# Streaming
@api.get("/stream")
async def stream():
    async def generate():
        for i in range(10):
            yield f"chunk {i}\n"
    return StreamingResponse(generate(), media_type="text/plain")
```

## Response Types

### JSON (Default)

Return a dict, list, or msgspec.Struct to automatically serialize as JSON.

```python
# Simple dict
@api.get("/data")
async def get_data():
    return {"status": "success", "value": 42}

# List
@api.get("/items")
async def list_items():
    return [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]

# msgspec.Struct
class User(msgspec.Struct):
    id: int
    name: str

@api.get("/user")
async def get_user():
    return User(id=1, name="Alice")
```

**Default behavior:**
- Content-Type: `application/json`
- Status code: `200`
- Serialization: msgspec (5-10x faster than stdlib json)

**Custom status code and headers:**

```python
from django_bolt import JSON

@api.post("/items")
async def create_item():
    return JSON(
        {"id": 123, "created": True},
        status_code=201,
        headers={"X-Resource-Id": "123"}
    )
```

### PlainText

Return plain text content.

```python
from django_bolt.responses import PlainText

@api.get("/health")
async def health():
    return PlainText("OK")

@api.get("/data")
async def get_data():
    return PlainText(
        "Status: Running\nUptime: 3600s",
        status_code=200,
        headers={"X-Server": "bolt"}
    )
```

**Parameters:**
- `text` (str): The text content (required)
- `status_code` (int): HTTP status code (default: 200)
- `headers` (dict): Additional HTTP headers (optional)

**Content-Type:** `text/plain; charset=utf-8`

### HTML

Return HTML content.

```python
from django_bolt.responses import HTML

@api.get("/page")
async def get_page():
    return HTML("<h1>Hello, World!</h1>")

@api.get("/dashboard")
async def dashboard():
    html = """
    <!DOCTYPE html>
    <html>
        <head><title>Dashboard</title></head>
        <body><h1>Welcome</h1></body>
    </html>
    """
    return HTML(html, status_code=200)
```

**Parameters:**
- `html` (str): The HTML content (required)
- `status_code` (int): HTTP status code (default: 200)
- `headers` (dict): Additional HTTP headers (optional)

**Content-Type:** `text/html; charset=utf-8`

### Redirect

Redirect to another URL.

```python
from django_bolt.responses import Redirect

@api.get("/old-path")
async def old_endpoint():
    return Redirect("/new-path", status_code=301)  # Permanent redirect

@api.get("/login")
async def login_redirect():
    return Redirect("/auth/login", status_code=307)  # Temporary redirect (default)
```

**Parameters:**
- `url` (str): The URL to redirect to (required)
- `status_code` (int): HTTP status code (default: 307 - Temporary Redirect)
- `headers` (dict): Additional HTTP headers (optional)

**Common redirect status codes:**
- `301` - Permanent redirect (cached by browsers)
- `302` - Temporary redirect (older HTTP/1.0 style)
- `307` - Temporary redirect (preserves request method)
- `308` - Permanent redirect (preserves request method)

### File

Load file content into memory and return it.

```python
from django_bolt.responses import File

@api.get("/download")
async def download_file():
    return File(
        "/path/to/document.pdf",
        filename="report.pdf",
        media_type="application/pdf"
    )

@api.get("/image")
async def get_image():
    return File("/path/to/image.png", filename="photo.png")
```

**Parameters:**
- `path` (str): Path to the file (required)
- `media_type` (str): MIME type (optional, auto-detected from extension if not provided)
- `filename` (str): Filename for Content-Disposition header (optional)
- `status_code` (int): HTTP status code (default: 200)
- `headers` (dict): Additional HTTP headers (optional)

**Behavior:**
- Entire file is read into memory
- Suitable for small to medium files
- Content-Type is auto-detected using Python's mimetypes module
- If `filename` is provided, sets `Content-Disposition: attachment; filename="..."`

**Use File when:**
- Files are small (< 10MB)
- You need to modify file content before sending
- File content needs to be loaded for processing

### FileResponse

Stream file content directly from disk (zero-copy in Rust).

```python
from django_bolt.responses import FileResponse

@api.get("/video")
async def stream_video():
    return FileResponse(
        "/var/media/video.mp4",
        filename="movie.mp4",
        media_type="video/mp4"
    )

@api.get("/download/{file_id}")
async def download_by_id(file_id: int):
    file_path = get_file_path(file_id)  # Get path from database
    return FileResponse(file_path, filename=f"file_{file_id}.pdf")
```

**Parameters:**
- `path` (str): Path to the file (required)
- `media_type` (str): MIME type (optional, auto-detected from extension if not provided)
- `filename` (str): Filename for Content-Disposition header (optional)
- `status_code` (int): HTTP status code (default: 200)
- `headers` (dict): Additional HTTP headers (optional)

**Behavior:**
- File is streamed directly from disk (handled in Rust layer)
- Zero-copy file serving for maximum performance
- Suitable for large files (videos, archives, etc.)
- Path validation and security checks are performed
- Content-Type is auto-detected using Python's mimetypes module
- If `filename` is provided, sets `Content-Disposition: attachment; filename="..."`

**Security features:**
- Resolves symlinks and relative paths (`..`)
- Validates file exists and is a regular file (not directory)
- Optional whitelist via `BOLT_ALLOWED_FILE_PATHS` setting

**Use FileResponse when:**
- Files are large (> 10MB)
- You need streaming performance
- Serving static files or user uploads

### StreamingResponse

Stream content using generators (sync or async).

```python
from django_bolt.responses import StreamingResponse

# Sync generator
@api.get("/stream")
async def stream_data():
    def generate():
        for i in range(10):
            yield f"Line {i}\n"
    return StreamingResponse(generate, media_type="text/plain")

# Async generator
@api.get("/async-stream")
async def async_stream():
    async def generate():
        for i in range(10):
            await asyncio.sleep(0.1)
            yield f"Chunk {i}\n"
    return StreamingResponse(generate(), media_type="text/plain")

# Server-Sent Events
@api.get("/events")
async def sse_events():
    async def generate():
        for i in range(5):
            yield f"data: Event {i}\n\n"
            await asyncio.sleep(1)
    return StreamingResponse(generate(), media_type="text/event-stream")
```

**Parameters:**
- `content` (callable or generator): Generator function or generator instance (required)
- `status_code` (int): HTTP status code (default: 200)
- `media_type` (str): MIME type (default: "application/octet-stream")
- `headers` (dict): Additional HTTP headers (optional)

**Supported content types:**
- Sync generators: `def gen(): yield ...`
- Async generators: `async def gen(): yield ...`
- Callables returning generators: `lambda: (x for x in range(10))`

**Yielded data types:**
- `bytes` - sent as-is
- `str` - encoded to UTF-8
- `bytearray` - converted to bytes
- `memoryview` - converted to bytes

### Response (Generic)

Generic response with custom headers and content type.

```python
from django_bolt import Response

# OPTIONS handler with Allow header
@api.options("/items")
async def options_items():
    return Response(
        {},
        headers={"Allow": "GET, POST, PUT, DELETE"}
    )

# Custom response with specific content type
@api.get("/xml")
async def get_xml():
    xml_content = '<?xml version="1.0"?><root><item>data</item></root>'
    return Response(
        xml_content,
        media_type="application/xml",
        headers={"X-Custom": "value"}
    )

# Empty response with custom status
@api.delete("/items/{item_id}")
async def delete_item(item_id: int):
    # Delete item...
    return Response({}, status_code=204)  # No Content
```

**Parameters:**
- `content` (Any): Response content (default: {})
- `status_code` (int): HTTP status code (default: 200)
- `headers` (dict): HTTP headers (optional)
- `media_type` (str): MIME type (default: "application/json")

**Use Response when:**
- You need custom headers (OPTIONS, CORS, etc.)
- Working with non-standard content types
- Need explicit control over serialization

## Automatic Serialization

Django-Bolt automatically serializes return values based on type:

```python
# Dict/list → JSON (msgspec)
@api.get("/data")
async def get_data():
    return {"key": "value"}  # Automatically serialized as JSON

# str → Plain text
@api.get("/text")
async def get_text():
    return "Hello"  # Content-Type: text/plain

# bytes → Binary
@api.get("/binary")
async def get_binary():
    return b"binary data"  # Content-Type: application/octet-stream

# msgspec.Struct → JSON
class User(msgspec.Struct):
    id: int
    name: str

@api.get("/user")
async def get_user():
    return User(id=1, name="Alice")  # Serialized with msgspec
```

**Serialization priority:**
1. dict/list → JSON via msgspec
2. Response objects (JSON, PlainText, etc.) → Use object's serialization
3. str → Plain text (UTF-8)
4. bytes/bytearray → Binary (application/octet-stream)
5. StreamingResponse → Streaming
6. Other types → Fallback to msgspec encoding

## Response Model Validation

Validate response data against a schema before returning.

```python
import msgspec

class UserResponse(msgspec.Struct):
    id: int
    name: str
    email: str

# Using response_model parameter
@api.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = await User.objects.aget(id=user_id)
    # Return dict, will be validated and coerced to UserResponse
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }

# Using return type annotation
@api.get("/users/{user_id}")
async def get_user_annotated(user_id: int) -> UserResponse:
    user = await User.objects.aget(id=user_id)
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email
    )

# List responses
@api.get("/users", response_model=list[UserResponse])
async def list_users():
    users = await User.objects.all().avalues('id', 'name', 'email')
    return list(users)  # Each dict is validated against UserResponse
```

**Validation behavior:**
- If validation fails, returns `500 Internal Server Error` with "Response validation error"
- Automatically coerces compatible types (e.g., Django model → msgspec.Struct)
- `response_model` parameter takes precedence over return type annotation

**Response model vs return annotation:**

```python
# response_model takes precedence
@api.get("/data", response_model=list[int])
async def get_data() -> list[str]:  # Ignored
    return [1, 2, 3]  # Validated as list[int]

# Use return annotation only
@api.get("/data")
async def get_data() -> list[int]:
    return [1, 2, 3]  # Validated as list[int]

# No validation
@api.get("/data")
async def get_data():
    return {"anything": "goes"}  # No validation
```

## Streaming Responses

### Sync Generators

Use regular Python generators for synchronous streaming:

```python
from django_bolt.responses import StreamingResponse

@api.get("/stream-lines")
async def stream_lines():
    def generate():
        for i in range(100):
            yield f"Line {i}\n"
    return StreamingResponse(generate, media_type="text/plain")

@api.get("/stream-csv")
async def stream_csv():
    def generate():
        yield "id,name,email\n"  # Header
        for user in users:
            yield f"{user.id},{user.name},{user.email}\n"
    return StreamingResponse(generate, media_type="text/csv")
```

**Note:** Sync generators are executed in the async runtime. For I/O operations, prefer async generators.

### Async Generators

Use async generators for async I/O operations:

```python
import asyncio
from django_bolt.responses import StreamingResponse

@api.get("/async-stream")
async def async_stream():
    async def generate():
        # Fetch data from database
        async for user in User.objects.all():
            yield f"{user.id}: {user.name}\n".encode()
            await asyncio.sleep(0)  # Allow other tasks to run

    return StreamingResponse(generate(), media_type="text/plain")

@api.get("/large-export")
async def large_export():
    async def generate():
        # Stream large dataset without loading into memory
        chunk_size = 1000
        offset = 0
        while True:
            users = await User.objects.all()[offset:offset+chunk_size].avalues('id', 'name')
            if not users:
                break
            for user in users:
                yield f"{user['id']},{user['name']}\n".encode()
            offset += chunk_size

    return StreamingResponse(generate(), media_type="text/csv")
```

### Server-Sent Events (SSE)

Stream real-time events to clients:

```python
import asyncio
import json
from django_bolt.responses import StreamingResponse

@api.get("/events")
async def sse_endpoint():
    async def event_stream():
        # SSE format: "data: message\n\n"
        yield "data: Connected\n\n"

        for i in range(10):
            # Send event with data
            yield f"data: Event {i}\n\n"
            await asyncio.sleep(1)

        # Send structured data as JSON
        data = {"type": "update", "value": 42}
        yield f"data: {json.dumps(data)}\n\n"

        # Named events
        yield "event: custom\ndata: Custom event data\n\n"

        # Comments (ignored by client)
        yield ": keepalive\n\n"

        # Event with ID (for reconnection)
        yield f"id: {event_id}\ndata: Event data\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

**SSE format:**
- Each message ends with double newline `\n\n`
- Data line: `data: message\n\n`
- Named event: `event: eventname\ndata: message\n\n`
- Event ID: `id: 123\ndata: message\n\n`
- Comment: `: comment text\n\n`

**Client-side JavaScript:**

```javascript
const eventSource = new EventSource('/events');

eventSource.onmessage = (event) => {
    console.log('Message:', event.data);
};

eventSource.addEventListener('custom', (event) => {
    console.log('Custom event:', event.data);
});

eventSource.onerror = (error) => {
    console.error('SSE error:', error);
    eventSource.close();
};
```

**SSE headers automatically set:**
- `Content-Type: text/event-stream`
- `X-Accel-Buffering: no` (disables buffering in nginx/proxies)
- `Cache-Control: no-cache` (prevents caching)

## File Serving

### File vs FileResponse

**Use `File` for:**
- Small files (< 10MB)
- Files that need processing before sending
- When you need the file content in Python

**Use `FileResponse` for:**
- Large files (> 10MB)
- Direct file streaming (zero-copy)
- Maximum performance
- Serving user uploads, videos, archives

**Performance comparison:**

```python
# File - Loads into memory
@api.get("/small")
async def small_file():
    return File("/path/to/small.pdf")  # Entire file loaded into Python memory

# FileResponse - Streamed from Rust
@api.get("/large")
async def large_file():
    return FileResponse("/path/to/large.mp4")  # Zero-copy streaming from Rust
```

### Security and Path Validation

FileResponse performs strict security validation:

**1. Path Resolution**
- Resolves symlinks: `/path/to/symlink` → `/real/path/to/file`
- Resolves relative paths: `../../etc/passwd` → `/etc/passwd`
- Prevents directory traversal attacks

**2. File Validation**
- Checks file exists
- Ensures it's a regular file (not directory, socket, etc.)
- Validates file is readable

**3. Optional Whitelist**

Configure allowed directories in Django settings:

```python
# settings.py
BOLT_ALLOWED_FILE_PATHS = [
    '/var/www/media',
    '/var/www/static',
    '/home/user/uploads',
]
```

With whitelist configured, FileResponse will only serve files within allowed directories:

```python
@api.get("/download/{file_id}")
async def download(file_id: int):
    # Get file path from database
    file_path = await File.objects.aget(id=file_id).values_list('path', flat=True)

    # This will raise PermissionError if file_path is not under BOLT_ALLOWED_FILE_PATHS
    return FileResponse(file_path, filename=f"file_{file_id}.pdf")
```

**Error handling:**

```python
from django_bolt.responses import FileResponse
from django_bolt.exceptions import NotFound, InternalServerError

@api.get("/files/{file_id}")
async def serve_file(file_id: int):
    try:
        file_path = get_file_path(file_id)
        return FileResponse(file_path)
    except FileNotFoundError:
        raise NotFound(detail="File not found")
    except PermissionError as e:
        # Not in allowed directories
        raise InternalServerError(detail="File access denied")
    except ValueError as e:
        # Invalid path
        raise InternalServerError(detail="Invalid file path")
```

**Best practices:**
- Always use absolute paths
- Configure `BOLT_ALLOWED_FILE_PATHS` in production
- Validate file_id/file_path from user input
- Use database to map IDs to file paths
- Never construct paths directly from user input

## Custom Headers and Status Codes

All response types support custom headers and status codes:

```python
from django_bolt.responses import PlainText, HTML, File, FileResponse
from django_bolt import JSON, Response

# JSON with custom status and headers
@api.post("/items")
async def create_item():
    return JSON(
        {"id": 123},
        status_code=201,
        headers={
            "Location": "/items/123",
            "X-Resource-Id": "123"
        }
    )

# PlainText with custom status
@api.get("/maintenance")
async def maintenance():
    return PlainText(
        "Service under maintenance",
        status_code=503,
        headers={"Retry-After": "3600"}
    )

# HTML with caching headers
@api.get("/page")
async def cached_page():
    return HTML(
        "<h1>Cached Page</h1>",
        headers={
            "Cache-Control": "public, max-age=3600",
            "ETag": "abc123"
        }
    )

# File with content disposition
@api.get("/download")
async def download():
    return FileResponse(
        "/path/to/file.pdf",
        filename="report.pdf",
        headers={
            "X-Download-Source": "generated",
            "X-File-Version": "1.0"
        }
    )

# Generic response with multiple headers
@api.options("/api/items")
async def options():
    return Response(
        {},
        headers={
            "Allow": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
            "Access-Control-Max-Age": "3600"
        }
    )
```

**Common headers:**
- `Location` - Redirect or created resource location
- `Cache-Control` - Caching directives
- `ETag` - Resource version for caching
- `Retry-After` - Retry delay for 429/503 responses
- `Content-Disposition` - Filename for downloads
- `X-*` - Custom application headers

## Content-Type Handling

Content-Type is automatically set based on response type:

| Response Type | Default Content-Type |
|---------------|---------------------|
| dict/list | `application/json` |
| JSON | `application/json` |
| PlainText | `text/plain; charset=utf-8` |
| HTML | `text/html; charset=utf-8` |
| str | `text/plain; charset=utf-8` |
| bytes | `application/octet-stream` |
| File | Auto-detected from extension |
| FileResponse | Auto-detected from extension |
| StreamingResponse | `application/octet-stream` (unless specified) |
| Response | `application/json` (unless specified) |

**Override Content-Type:**

```python
# Using media_type parameter
@api.get("/xml")
async def get_xml():
    from django_bolt import Response
    return Response(
        '<?xml version="1.0"?><root/>',
        media_type="application/xml"
    )

# Using custom header (takes precedence)
@api.get("/custom")
async def custom():
    return JSON(
        {"data": "value"},
        headers={"Content-Type": "application/vnd.api+json"}
    )
```

**Auto-detection for files:**

```python
# .pdf → application/pdf
@api.get("/doc")
async def doc():
    return FileResponse("/path/to/file.pdf")

# .jpg → image/jpeg
@api.get("/image")
async def image():
    return File("/path/to/photo.jpg")

# .mp4 → video/mp4
@api.get("/video")
async def video():
    return FileResponse("/path/to/video.mp4")

# Override auto-detection
@api.get("/custom")
async def custom():
    return File("/path/to/file.bin", media_type="application/x-custom")
```

## Best Practices

### 1. Use Appropriate Response Types

```python
# Good - Use specific response type
@api.get("/health")
async def health():
    return PlainText("OK")

# Bad - Return dict for plain text
@api.get("/health")
async def health():
    return {"message": "OK"}  # Unnecessarily complex
```

### 2. Validate Responses with response_model

```python
# Good - Validate response structure
class UserResponse(msgspec.Struct):
    id: int
    name: str
    email: str

@api.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = await User.objects.aget(id=user_id)
    return {"id": user.id, "name": user.name, "email": user.email}

# Bad - No validation, typos can slip through
@api.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await User.objects.aget(id=user_id)
    return {"id": user.id, "nmae": user.name}  # Typo in 'name'
```

### 3. Use FileResponse for Large Files

```python
# Good - Stream large files
@api.get("/video/{video_id}")
async def get_video(video_id: int):
    path = get_video_path(video_id)
    return FileResponse(path, media_type="video/mp4")

# Bad - Load large file into memory
@api.get("/video/{video_id}")
async def get_video(video_id: int):
    path = get_video_path(video_id)
    return File(path)  # Loads entire video into RAM
```

### 4. Stream Large Datasets

```python
# Good - Stream data incrementally
@api.get("/export")
async def export_users():
    async def generate():
        async for user in User.objects.all():
            yield f"{user.id},{user.name}\n".encode()
    return StreamingResponse(generate(), media_type="text/csv")

# Bad - Load everything into memory
@api.get("/export")
async def export_users():
    users = await User.objects.all().avalues('id', 'name')
    csv = "\n".join([f"{u['id']},{u['name']}" for u in users])
    return PlainText(csv)  # All data in memory
```

### 5. Set Appropriate Status Codes

```python
# Good - Use correct status codes
@api.post("/users")
async def create_user(user: UserRequest):
    new_user = await User.objects.acreate(**user.__dict__)
    return JSON(
        {"id": new_user.id},
        status_code=201,  # Created
        headers={"Location": f"/users/{new_user.id}"}
    )

@api.delete("/users/{user_id}")
async def delete_user(user_id: int):
    await User.objects.filter(id=user_id).adelete()
    return Response({}, status_code=204)  # No Content

# Bad - Always return 200
@api.post("/users")
async def create_user(user: UserRequest):
    new_user = await User.objects.acreate(**user.__dict__)
    return {"id": new_user.id}  # Returns 200 instead of 201
```

### 6. Use Custom Headers for Metadata

```python
# Good - Provide metadata in headers
@api.get("/users")
async def list_users(page: int = 1):
    users = await get_users_page(page)
    total = await User.objects.acount()
    return JSON(
        [{"id": u.id, "name": u.name} for u in users],
        headers={
            "X-Total-Count": str(total),
            "X-Page": str(page),
            "X-Per-Page": "20"
        }
    )

# Bad - Include metadata in response body (makes pagination harder)
@api.get("/users")
async def list_users(page: int = 1):
    users = await get_users_page(page)
    return {
        "data": [{"id": u.id, "name": u.name} for u in users],
        "meta": {"total": total, "page": page}  # Mixed with data
    }
```

### 7. Handle Errors Gracefully in Streaming

```python
from django_bolt.exceptions import InternalServerError

@api.get("/stream")
async def stream_data():
    async def generate():
        try:
            async for item in get_items():
                yield f"data: {item}\n\n"
        except Exception as e:
            # Log error and send error event
            logger.error(f"Streaming error: {e}")
            yield f"event: error\ndata: Stream failed\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

### 8. Configure File Serving Security

```python
# settings.py - Always configure in production
BOLT_ALLOWED_FILE_PATHS = [
    '/var/www/media',
    '/var/www/uploads',
]

# Handler - Validate file access
@api.get("/files/{file_id}")
async def serve_file(file_id: int):
    # Validate file_id belongs to current user
    file_obj = await File.objects.filter(
        id=file_id,
        owner=current_user
    ).afirst()

    if not file_obj:
        raise NotFound(detail="File not found")

    try:
        return FileResponse(file_obj.path, filename=file_obj.name)
    except PermissionError:
        raise InternalServerError(detail="File access denied")
```

### 9. Use Appropriate Media Types for SSE

```python
# Good - Use text/event-stream for SSE
@api.get("/events")
async def events():
    async def generate():
        for i in range(10):
            yield f"data: Event {i}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")

# Bad - Wrong content type
@api.get("/events")
async def events():
    async def generate():
        for i in range(10):
            yield f"data: Event {i}\n\n"
    return StreamingResponse(generate(), media_type="text/plain")  # Won't work with EventSource
```

### 10. Leverage msgspec for Performance

```python
# Good - Let msgspec handle serialization
class User(msgspec.Struct):
    id: int
    name: str
    tags: list[str]

@api.get("/users")
async def list_users():
    users = await User.objects.all()
    return [User(id=u.id, name=u.name, tags=u.tags) for u in users]
    # msgspec serializes 5-10x faster than stdlib json

# Bad - Manual JSON serialization
import json

@api.get("/users")
async def list_users():
    users = await User.objects.all()
    data = [{"id": u.id, "name": u.name} for u in users]
    return PlainText(json.dumps(data))  # Slower, wrong content-type
```

## See Also

- [EXCEPTIONS.md](EXCEPTIONS.md) - Error handling and HTTP exceptions
- [MIDDLEWARE.md](MIDDLEWARE.md) - Request/response middleware
- [SECURITY.md](SECURITY.md) - Security best practices including file serving
- [ASYNC_DJANGO.md](ASYNC_DJANGO.md) - Async Django ORM usage in handlers

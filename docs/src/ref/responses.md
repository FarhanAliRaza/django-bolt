---
icon: lucide/send
---

# Responses Reference

This page documents all response types available in Django-Bolt.

## Response

Generic response with custom headers.

```python
from django_bolt import Response

return Response(
    {"data": "value"},
    status_code=200,
    headers={"X-Custom": "header"}
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `content` | `Any` | `{}` | Response content |
| `status_code` | `int` | `200` | HTTP status code |
| `headers` | `dict` | `None` | Response headers |
| `media_type` | `str` | `"application/json"` | Content type |

## JSON

Explicit JSON response with status and headers.

```python
from django_bolt import JSON

return JSON(
    {"id": 1, "name": "Item"},
    status_code=201,
    headers={"X-Created": "true"}
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `Any` | required | JSON-serializable data |
| `status_code` | `int` | `200` | HTTP status code |
| `headers` | `dict` | `None` | Response headers |

## PlainText

Plain text response.

```python
from django_bolt.responses import PlainText

return PlainText("Hello, World!")
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | required | Text content |
| `status_code` | `int` | `200` | HTTP status code |
| `headers` | `dict` | `None` | Response headers |

## HTML

HTML response.

```python
from django_bolt.responses import HTML

return HTML("<h1>Hello</h1>")
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `html` | `str` | required | HTML content |
| `status_code` | `int` | `200` | HTTP status code |
| `headers` | `dict` | `None` | Response headers |

## Redirect

HTTP redirect response.

```python
from django_bolt.responses import Redirect

return Redirect("/new-location")
return Redirect("/new-location", status_code=301)  # Permanent
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | required | Redirect URL |
| `status_code` | `int` | `307` | Redirect status code |
| `headers` | `dict` | `None` | Response headers |

### Status codes

| Code | Description |
|------|-------------|
| `301` | Permanent redirect |
| `302` | Found (temporary) |
| `303` | See Other |
| `307` | Temporary redirect (preserves method) |
| `308` | Permanent redirect (preserves method) |

## File

In-memory file download.

```python
from django_bolt.responses import File

return File(
    "/path/to/file.pdf",
    filename="document.pdf",
    media_type="application/pdf"
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str` | required | File path |
| `filename` | `str` | `None` | Download filename |
| `media_type` | `str` | `None` | Content type |
| `status_code` | `int` | `200` | HTTP status code |
| `headers` | `dict` | `None` | Response headers |

## FileResponse

Streaming file response for large files.

```python
from django_bolt.responses import FileResponse

return FileResponse(
    "/path/to/large-video.mp4",
    filename="video.mp4"
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str` | required | File path |
| `filename` | `str` | `None` | Download filename |
| `media_type` | `str` | `None` | Content type (auto-detected) |
| `status_code` | `int` | `200` | HTTP status code |
| `headers` | `dict` | `None` | Response headers |

### Security

Configure allowed directories in `settings.py`:

```python
BOLT_ALLOWED_FILE_PATHS = [
    "/var/app/uploads",
]
```

## StreamingResponse

Streaming response for generators.

```python
from django_bolt import StreamingResponse

def generate():
    for i in range(100):
        yield f"chunk {i}\n"

return StreamingResponse(generate(), media_type="text/plain")
```

### Async generators

```python
async def async_generate():
    for i in range(100):
        await asyncio.sleep(0.1)
        yield f"data: {i}\n\n"

return StreamingResponse(async_generate(), media_type="text/event-stream")
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `content` | generator | required | Generator instance |
| `status_code` | `int` | `200` | HTTP status code |
| `media_type` | `str` | `"application/octet-stream"` | Content type |
| `headers` | `dict` | `None` | Response headers |

### Common media types

| Type | Use case |
|------|----------|
| `text/plain` | Plain text streaming |
| `text/event-stream` | Server-Sent Events (SSE) |
| `application/octet-stream` | Binary data |
| `application/json` | JSON streaming (NDJSON) |

## Implicit responses

### Dict/list

Returns JSON with status 200.

```python
return {"message": "Hello"}
return [{"id": 1}, {"id": 2}]
```

### String

Returns plain text with status 200.

```python
return "Hello, World!"
```

### Bytes

Returns binary with `application/octet-stream`.

```python
return b"\x00\x01\x02\x03"
```

### msgspec.Struct

Returns JSON with automatic serialization.

```python
import msgspec

class User(msgspec.Struct):
    id: int
    name: str

return User(id=1, name="John")
```

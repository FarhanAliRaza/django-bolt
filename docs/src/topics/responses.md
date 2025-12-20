# Responses

This guide covers all the response types available in Django-Bolt and how to use them.

## JSON responses

Returning a dict, list, or `msgspec.Struct` automatically creates a JSON response:

```python
@api.get("/data")
async def get_data():
    return {"message": "Hello", "count": 42}

@api.get("/items")
async def get_items():
    return [{"id": 1}, {"id": 2}]
```

### Custom status codes and headers

Use the `JSON` class for more control:

```python
from django_bolt import JSON

@api.post("/users")
async def create_user():
    return JSON(
        {"id": 1, "username": "john"},
        status_code=201,
        headers={"X-Created-By": "django-bolt"}
    )
```

## Plain text

Return plain text responses:

```python
from django_bolt.responses import PlainText

@api.get("/hello")
async def hello():
    return PlainText("Hello, World!")

@api.get("/status")
async def status():
    return PlainText("OK", status_code=200, headers={"X-Status": "healthy"})
```

## HTML

Return HTML content:

```python
from django_bolt.responses import HTML

@api.get("/page")
async def page():
    return HTML("<h1>Welcome</h1><p>This is HTML content.</p>")

@api.get("/template")
async def template():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>My Page</title></head>
    <body><h1>Hello</h1></body>
    </html>
    """
    return HTML(html)
```

## Redirects

Redirect to another URL:

```python
from django_bolt.responses import Redirect

@api.get("/old-page")
async def old_page():
    return Redirect("/new-page")

@api.get("/external")
async def external():
    return Redirect("https://example.com", status_code=302)
```

Redirect status codes:

- `301` - Permanent redirect
- `302` - Temporary redirect (Found)
- `303` - See Other
- `307` - Temporary redirect (default, preserves method)
- `308` - Permanent redirect (preserves method)

## File downloads

### In-memory files

Use `File` for small files that can be loaded into memory:

```python
from django_bolt.responses import File

@api.get("/download")
async def download():
    return File(
        "/path/to/file.pdf",
        filename="document.pdf",
        media_type="application/pdf"
    )
```

### Streaming files

Use `FileResponse` for larger files that should be streamed:

```python
from django_bolt.responses import FileResponse

@api.get("/video")
async def video():
    return FileResponse(
        "/path/to/video.mp4",
        filename="video.mp4",
        media_type="video/mp4"
    )
```

`FileResponse` streams the file directly without loading it entirely into memory.

### File security

Configure allowed directories in `settings.py`:

```python
BOLT_ALLOWED_FILE_PATHS = [
    "/var/app/uploads",
    "/var/app/public",
]
```

When configured, `FileResponse` only serves files within these directories, preventing path traversal attacks.

## Streaming responses

Stream data incrementally using generators:

```python
from django_bolt import StreamingResponse

@api.get("/stream")
async def stream():
    def generate():
        for i in range(100):
            yield f"chunk {i}\n"

    return StreamingResponse(generate(), media_type="text/plain")
```

### Async generators

For async operations, use async generators:

```python
import asyncio

@api.get("/async-stream")
async def async_stream():
    async def generate():
        for i in range(10):
            await asyncio.sleep(0.1)
            yield f"data: {i}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

### Server-Sent Events (SSE)

Create SSE endpoints for real-time updates:

```python
import asyncio
import time

@api.get("/events")
async def events():
    async def generate():
        while True:
            yield f"data: {time.time()}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(generate(), media_type="text/event-stream")
```

SSE format:

- `data: content\n\n` - Send data
- `event: eventname\ndata: content\n\n` - Named event
- `: comment\n\n` - Comment (ignored by clients)

### Disabling compression for streams

Streaming responses should not be compressed. Use `@no_compress`:

```python
from django_bolt.middleware import no_compress

@api.get("/sse")
@no_compress
async def sse():
    async def generate():
        for i in range(10):
            yield f"data: {i}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(generate(), media_type="text/event-stream")
```

## Response with custom headers

Use the `Response` class for complete control:

```python
from django_bolt import Response

@api.options("/items")
async def options_items():
    return Response(
        {},
        status_code=204,
        headers={"Allow": "GET, POST, PUT, DELETE"}
    )
```

## Response validation

Validate response data against a schema using `response_model`:

```python
import msgspec

class User(msgspec.Struct):
    id: int
    username: str
    email: str

@api.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    return {"id": user_id, "username": "john", "email": "john@example.com"}
```

If the response doesn't match the schema, a 500 error is returned.

You can also use return type annotations:

```python
@api.get("/users/{user_id}")
async def get_user(user_id: int) -> User:
    return {"id": user_id, "username": "john", "email": "john@example.com"}
```

## Setting default status codes

Set a default status code for an endpoint:

```python
@api.post("/users", status_code=201)
async def create_user():
    return {"id": 1, "username": "john"}
```

## Returning strings and bytes

Returning a string creates a plain text response:

```python
@api.get("/text")
async def text():
    return "Hello"  # Content-Type: text/plain
```

Returning bytes creates an octet-stream response:

```python
@api.get("/bytes")
async def bytes_response():
    return b"binary data"  # Content-Type: application/octet-stream
```

## Empty responses

For 204 No Content responses:

```python
from django_bolt import Response

@api.delete("/items/{item_id}")
async def delete_item(item_id: int):
    # ... delete the item ...
    return Response(status_code=204)
```

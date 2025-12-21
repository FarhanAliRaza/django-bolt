---
icon: lucide/arrow-up-from-line
---

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

### Django templates

Use the `render()` function to render Django templates. It works like [Django's `render()` shortcut](https://docs.djangoproject.com/en/dev/topics/http/shortcuts/#render):

```python
from django_bolt import Request
from django_bolt.shortcuts import render

@api.get("/page")
async def show_page(request: Request):
    return render(request, "myapp/page.html", {
        "title": "My Page",
        "items": ["item1", "item2"],
    })
```

Use standard Django templates - nothing special required:

```html
<!-- templates/myapp/page.html -->
<!DOCTYPE html>
<html>
<head><title>{{ title }}</title></head>
<body>
    <h1>{{ title }}</h1>
    <ul>
    {% for item in items %}
        <li>{{ item }}</li>
    {% endfor %}
    </ul>
</body>
</html>
```

Parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `request` | `Request` | required | The request object |
| `template_name` | `str` | required | Path to the template file |
| `context` | `dict` | `None` | Template context variables |
| `content_type` | `str` | `None` | Response content type |
| `status` | `int` | `200` | HTTP status code |
| `using` | `str` | `None` | Template engine to use |

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

Create SSE endpoints for real-time updates. SSE is a standard for pushing events from server to browser over HTTP.

#### Basic SSE

```python
import asyncio

@api.get("/events")
async def events():
    async def generate():
        for i in range(10):
            yield f"data: message-{i}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(generate(), media_type="text/event-stream")
```

#### SSE format

Each event is terminated by a double newline (`\n\n`). Fields:

| Field | Description |
|-------|-------------|
| `data:` | Event data (required) |
| `event:` | Event type (optional, default: "message") |
| `id:` | Event ID for reconnection (optional) |
| `retry:` | Reconnection time in ms (optional) |

#### Full SSE event format

```python
@api.get("/sse-events")
async def sse_events():
    async def generate():
        for i in range(5):
            # Full SSE event with all fields
            yield f"event: update\nid: {i}\ndata: {{\"count\": {i}}}\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(generate(), media_type="text/event-stream")
```

Client receives:
```
event: update
id: 0
data: {"count": 0}

event: update
id: 1
data: {"count": 1}
```

#### Sync generators for SSE

You can use sync generators for CPU-bound operations:

```python
import time

@api.get("/sync-sse")
async def sync_sse():
    def generate():
        for i in range(5):
            yield f"data: sync-message-{i}\n\n"
            time.sleep(0.1)

    return StreamingResponse(generate(), media_type="text/event-stream")
```

#### Mixed data types

Generators can yield both strings and bytes:

```python
@api.get("/mixed-sse")
async def mixed_sse():
    async def generate():
        yield "data: string message\n\n"
        yield b"data: bytes message\n\n"  # Also works

    return StreamingResponse(generate(), media_type="text/event-stream")
```

#### SSE with cleanup

Use try/finally for resource cleanup when clients disconnect:

```python
@api.get("/sse-with-cleanup")
async def sse_with_cleanup():
    async def generate():
        try:
            yield "data: START\n\n"
            for i in range(100):
                yield f"data: chunk-{i}\n\n"
                await asyncio.sleep(0.1)
            yield "data: END\n\n"
        finally:
            # This runs when client disconnects
            print("Client disconnected, cleaning up")

    return StreamingResponse(generate(), media_type="text/event-stream")
```

#### SSE headers

SSE endpoints should include these headers for proper behavior:

```python
@api.get("/sse")
async def sse():
    async def generate():
        for i in range(10):
            yield f"data: {i}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
```

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

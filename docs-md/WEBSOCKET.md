# WebSocket Guide

Django-Bolt provides full WebSocket support with a FastAPI-like interface, running on the same high-performance Rust infrastructure as HTTP endpoints.

## Overview

WebSocket support includes:

- **FastAPI-like Interface** - Familiar `@api.websocket()` decorator and `WebSocket` class
- **Path Parameters** - Dynamic routes with automatic type coercion
- **Authentication & Guards** - Reuse the same auth system as HTTP endpoints
- **Origin Validation** - CORS-based origin checking for security
- **Rate Limiting** - Token bucket rate limiting on connection
- **Testing Utilities** - `WebSocketTestClient` for unit testing

## Quick Start

```python
from django_bolt import BoltAPI, WebSocket

api = BoltAPI()

@api.websocket("/ws/echo")
async def echo_handler(websocket: WebSocket):
    await websocket.accept()
    async for message in websocket.iter_text():
        await websocket.send_text(f"Echo: {message}")
```

## WebSocket Decorator

The `@api.websocket()` decorator registers a WebSocket handler:

```python
@api.websocket(
    "/ws/chat/{room_id}",
    auth=[JWTAuthentication(secret="your-secret")],
    guards=[IsAuthenticated()],
)
async def chat_handler(websocket: WebSocket, room_id: str):
    await websocket.accept()
    # Handle WebSocket messages
```

### Parameters

| Parameter | Type   | Description                            |
| --------- | ------ | -------------------------------------- |
| `path`    | `str`  | URL path with optional path parameters |
| `auth`    | `list` | Authentication backends (same as HTTP) |
| `guards`  | `list` | Permission guards (same as HTTP)       |

## WebSocket Class

The `WebSocket` class provides the interface for handling WebSocket connections.

### Connection Lifecycle

```python
@api.websocket("/ws/example")
async def handler(websocket: WebSocket):
    # 1. Accept the connection
    await websocket.accept()

    try:
        # 2. Handle messages
        async for message in websocket.iter_text():
            await websocket.send_text(f"Received: {message}")
    except WebSocketDisconnect:
        # 3. Handle client disconnect
        pass
    finally:
        # 4. Close (optional - auto-closed on handler exit)
        await websocket.close()
```

### Accepting Connections

```python
await websocket.accept()
```

### Receiving Messages

#### Text Messages

```python
# Single message
message = await websocket.receive_text()

# Iterate over all messages
async for message in websocket.iter_text():
    print(message)
```

#### Binary Messages

```python
# Single message
data = await websocket.receive_bytes()

# Iterate over all messages
async for data in websocket.iter_bytes():
    process(data)
```

#### JSON Messages

```python
# Single message
data = await websocket.receive_json()

# Iterate over all messages
async for data in websocket.iter_json():
    handle_command(data)
```

### Sending Messages

```python
# Text
await websocket.send_text("Hello, World!")

# Binary
await websocket.send_bytes(b"\x00\x01\x02")

# JSON (automatically serialized)
await websocket.send_json({"status": "ok", "count": 42})
```

### Closing Connections

```python
from django_bolt.websocket import CloseCode

# Normal close
await websocket.close()
await websocket.close(code=CloseCode.NORMAL, reason="Done")

# Error close
await websocket.close(code=CloseCode.INTERNAL_ERROR, reason="Server error")
```

### Accessing Request Data

```python
@api.websocket("/ws/info")
async def info_handler(websocket: WebSocket):
    await websocket.accept()

    # Path
    path = websocket.path  # "/ws/info"

    # Query parameters
    token = websocket.query_params.get("token")

    # Headers
    user_agent = websocket.headers.get("user-agent")
    auth_header = websocket.headers.get("authorization")

    # Cookies
    session = websocket.cookies.get("sessionid")

    # Client info (tuple of host, port)
    client_host, client_port = websocket.client if websocket.client else (None, None)

    await websocket.send_json({
        "path": path,
        "token": token,
        "user_agent": user_agent,
        "client": client_host,
    })
```

## Path Parameters

WebSocket routes support path parameters with automatic type coercion:

```python
# String parameter (default)
@api.websocket("/ws/chat/{room_id}")
async def chat(websocket: WebSocket, room_id: str):
    await websocket.accept()
    await websocket.send_text(f"Joined room: {room_id}")

# Integer parameter
@api.websocket("/ws/user/{user_id}")
async def user_ws(websocket: WebSocket, user_id: int):
    await websocket.accept()
    await websocket.send_json({"user_id": user_id, "type": type(user_id).__name__})

# Float parameter
@api.websocket("/ws/price/{price}")
async def price_ws(websocket: WebSocket, price: float):
    await websocket.accept()
    # price is automatically converted to float

# Boolean parameter
@api.websocket("/ws/feature/{enabled}")
async def feature_ws(websocket: WebSocket, enabled: bool):
    await websocket.accept()
    # "true"/"false" strings converted to bool

# Multiple parameters
@api.websocket("/ws/user/{user_id}/channel/{channel_id}")
async def multi_param(websocket: WebSocket, user_id: int, channel_id: str):
    await websocket.accept()
    await websocket.send_json({
        "user_id": user_id,
        "channel_id": channel_id,
    })
```

## Close Codes

Django-Bolt provides RFC 6455 standard close codes:

```python
from django_bolt.websocket import CloseCode

CloseCode.NORMAL                    # 1000 - Normal closure
CloseCode.GOING_AWAY                # 1001 - Server/client going away
CloseCode.PROTOCOL_ERROR            # 1002 - Protocol error
CloseCode.UNSUPPORTED_DATA          # 1003 - Unsupported data type
CloseCode.NO_STATUS_RECEIVED        # 1005 - No status received
CloseCode.ABNORMAL_CLOSURE          # 1006 - Abnormal closure
CloseCode.INVALID_FRAME_PAYLOAD_DATA # 1007 - Invalid frame payload
CloseCode.POLICY_VIOLATION          # 1008 - Policy violation
CloseCode.MESSAGE_TOO_BIG           # 1009 - Message too big
CloseCode.MANDATORY_EXTENSION       # 1010 - Missing extension
CloseCode.INTERNAL_ERROR            # 1011 - Internal server error
CloseCode.SERVICE_RESTART           # 1012 - Service restart
CloseCode.TRY_AGAIN_LATER           # 1013 - Try again later
CloseCode.BAD_GATEWAY               # 1014 - Bad gateway
CloseCode.TLS_HANDSHAKE             # 1015 - TLS handshake failure
```

## Exceptions

### WebSocketDisconnect

Raised when the client disconnects:

```python
from django_bolt.websocket import WebSocketDisconnect

@api.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    try:
        async for message in websocket.iter_text():
            await websocket.send_text(message)
    except WebSocketDisconnect as e:
        print(f"Client disconnected: code={e.code}, reason={e.reason}")
```

### WebSocketClose

Raised to close a connection with a specific code:

```python
from django_bolt.websocket import WebSocketClose, CloseCode

@api.websocket("/ws/auth-required")
async def auth_ws(websocket: WebSocket):
    await websocket.accept()

    auth_msg = await websocket.receive_json()
    if not auth_msg.get("token"):
        raise WebSocketClose(
            code=CloseCode.POLICY_VIOLATION,
            reason="Authentication required"
        )

    # Continue with authenticated session
```

## Authentication & Guards

WebSocket routes use the same authentication and guard system as HTTP endpoints:

```python
from django_bolt.auth import (
    JWTAuthentication,
    IsAuthenticated,
    IsAdminUser,
    HasPermission,
)

# Require authentication
@api.websocket(
    "/ws/protected",
    auth=[JWTAuthentication(secret="your-secret")],
    guards=[IsAuthenticated()],
)
async def protected_ws(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("You are authenticated!")

# Require admin
@api.websocket(
    "/ws/admin",
    auth=[JWTAuthentication(secret="your-secret")],
    guards=[IsAdminUser()],
)
async def admin_ws(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Welcome, admin!")

# Require specific permission
@api.websocket(
    "/ws/data",
    auth=[JWTAuthentication(secret="your-secret")],
    guards=[HasPermission("api.view_data")],
)
async def data_ws(websocket: WebSocket):
    await websocket.accept()
    # Stream data to authorized users
```

Authentication is performed during the WebSocket handshake. If authentication fails, the connection is rejected with a `PermissionError` before the handler is called.

## Security Features

### Origin Validation

WebSocket connections validate the `Origin` header against your CORS configuration:

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://app.example.com",
]
```

- Connections from allowed origins succeed
- Connections from disallowed origins are rejected with "Origin not allowed"
- Same-origin requests (no Origin header) are allowed
- Wildcard `*` allows all origins

### Rate Limiting

Apply rate limiting to WebSocket connections using the same decorator as HTTP:

```python
from django_bolt.middleware import rate_limit

@api.websocket("/ws/limited")
@rate_limit(rps=10, burst=20)  # 10 connections/sec, burst of 20
async def limited_ws(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Connected!")
```

Rate limiting is applied during the connection handshake. If the rate limit is exceeded, the connection is rejected with "Rate limit exceeded".

### Security Order

Security checks are applied in this order:

1. **Origin validation** - Checked first (fail-secure)
2. **Rate limiting** - Applied after origin check
3. **Authentication** - JWT/API key validation
4. **Guards** - Permission checks

This ensures that invalid origins don't consume rate limit tokens.

## Testing WebSocket Endpoints

Use `WebSocketTestClient` for testing without network overhead:

```python
import pytest
from django_bolt import BoltAPI, WebSocket
from django_bolt.testing import WebSocketTestClient, ConnectionClosed

@pytest.mark.asyncio
async def test_echo():
    api = BoltAPI()

    @api.websocket("/ws/echo")
    async def echo(websocket: WebSocket):
        await websocket.accept()
        async for msg in websocket.iter_text():
            await websocket.send_text(f"Echo: {msg}")

    async with WebSocketTestClient(api, "/ws/echo") as ws:
        await ws.send_text("hello")
        response = await ws.receive_text()
        assert response == "Echo: hello"
```

### WebSocketTestClient Parameters

```python
WebSocketTestClient(
    api,                          # BoltAPI instance
    path,                         # WebSocket path
    headers=None,                 # Optional headers dict
    query_string="",              # Optional query string (without ?)
    cors_allowed_origins=None,    # Override CORS origins for test
    read_django_settings=True,    # Read CORS from Django settings
)
```

### Testing Authentication

```python
import jwt
import time

def create_test_jwt(user_id: int, secret: str) -> str:
    return jwt.encode({
        "sub": str(user_id),
        "user_id": str(user_id),
        "exp": int(time.time()) + 3600,
    }, secret, algorithm="HS256")

@pytest.mark.asyncio
async def test_protected_websocket():
    api = BoltAPI()
    secret = "test-secret"

    @api.websocket(
        "/ws/protected",
        auth=[JWTAuthentication(secret=secret)],
        guards=[IsAuthenticated()],
    )
    async def protected(websocket: WebSocket):
        await websocket.accept()
        await websocket.send_text("authenticated")

    # Without auth - should fail
    with pytest.raises(PermissionError) as exc:
        async with WebSocketTestClient(api, "/ws/protected"):
            pass
    assert "Authentication required" in str(exc.value)

    # With auth - should succeed
    token = create_test_jwt(123, secret)
    headers = {"Authorization": f"Bearer {token}"}
    async with WebSocketTestClient(api, "/ws/protected", headers=headers) as ws:
        msg = await ws.receive_text()
        assert msg == "authenticated"
```

### Testing Origin Validation

```python
@pytest.mark.asyncio
async def test_origin_denied():
    api = BoltAPI()

    @api.websocket("/ws/echo")
    async def echo(websocket: WebSocket):
        await websocket.accept()

    with pytest.raises(PermissionError) as exc:
        async with WebSocketTestClient(
            api,
            "/ws/echo",
            headers={"Origin": "https://evil.com"},
            cors_allowed_origins=["https://example.com"],
            read_django_settings=False,
        ):
            pass

    assert "Origin not allowed" in str(exc.value)
```

### Testing Close Handling

```python
from django_bolt.testing import ConnectionClosed
from django_bolt.websocket import CloseCode

@pytest.mark.asyncio
async def test_server_close():
    api = BoltAPI()

    @api.websocket("/ws/close")
    async def close_handler(websocket: WebSocket):
        await websocket.accept()
        await websocket.send_text("goodbye")
        await websocket.close(code=CloseCode.NORMAL, reason="done")

    async with WebSocketTestClient(api, "/ws/close") as ws:
        msg = await ws.receive_text()
        assert msg == "goodbye"

        with pytest.raises(ConnectionClosed) as exc:
            await ws.receive_text()

        assert exc.value.code == CloseCode.NORMAL
```

### Receive Timeout

```python
@pytest.mark.asyncio
async def test_timeout():
    api = BoltAPI()

    @api.websocket("/ws/slow")
    async def slow(websocket: WebSocket):
        await websocket.accept()
        # Don't send anything

    async with WebSocketTestClient(api, "/ws/slow") as ws:
        with pytest.raises(TimeoutError):
            await ws.receive_text(timeout=0.1)
```

## Limitations

The following WebSocket features are not yet implemented:

- **Subprotocol negotiation** - `accept(subprotocol=...)` exists but is untested
- **Connection manager** - No built-in manager for tracking active connections
- **Broadcasting** - No built-in support for sending messages to multiple clients
- **Channels/Rooms** - No pub/sub or room-based messaging system

For now, you'll need to implement connection tracking and broadcasting manually if needed.

## API Reference

### WebSocket Class

| Method/Property                  | Description                                      |
| -------------------------------- | ------------------------------------------------ |
| `await accept(subprotocol=None)` | Accept the WebSocket connection                  |
| `await receive_text()`           | Receive a text message                           |
| `await receive_bytes()`          | Receive a binary message                         |
| `await receive_json()`           | Receive and parse a JSON message                 |
| `async for msg in iter_text()`   | Iterate over text messages                       |
| `async for msg in iter_bytes()`  | Iterate over binary messages                     |
| `async for msg in iter_json()`   | Iterate over JSON messages                       |
| `await send_text(data)`          | Send a text message                              |
| `await send_bytes(data)`         | Send a binary message                            |
| `await send_json(data)`          | Send a JSON message                              |
| `await close(code, reason)`      | Close the connection                             |
| `.path`                          | Request path                                     |
| `.query_params`                  | Query parameters dict                            |
| `.headers`                       | Request headers                                  |
| `.cookies`                       | Request cookies                                  |
| `.path_params`                   | Extracted path parameters                        |
| `.client`                        | Client address as `(host, port)` tuple or `None` |

### WebSocketTestClient

| Method/Property                | Description                         |
| ------------------------------ | ----------------------------------- |
| `async with client:`           | Context manager for connection      |
| `await send_text(data)`        | Send a text message                 |
| `await send_bytes(data)`       | Send a binary message               |
| `await send_json(data)`        | Send a JSON message                 |
| `await receive_text(timeout)`  | Receive text with optional timeout  |
| `await receive_bytes(timeout)` | Receive bytes with optional timeout |
| `await receive_json(timeout)`  | Receive JSON with optional timeout  |
| `await close(code)`            | Close the connection                |
| `.accepted`                    | Whether connection was accepted     |
| `.closed`                      | Whether connection is closed        |
| `.close_code`                  | Close code if closed                |

## 💡 Suggestions for Future Enhancements

    Connection Manager: Built-in support for tracking active connections by room/channel
    Broadcasting: Helper for sending messages to multiple clients
    Pub/Sub Integration: Redis or in-memory pub/sub for multi-process WebSocket coordination
    Compression: Per-message deflate extension support

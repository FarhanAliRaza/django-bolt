# Django-Bolt Middleware System

## Overview

Django-Bolt provides a high-performance middleware pipeline that executes primarily in Rust for minimal overhead. Middleware can be applied globally or per-route, with zero cost when not used.

## Quick Start

```python
from django_bolt import BoltAPI
from django_bolt.middleware import rate_limit, cors, auth_required

# Global middleware via config
api = BoltAPI(
    middleware_config={
        'cors': {
            'origins': ['http://localhost:3000'],
            'credentials': True
        }
    }
)

# Per-route middleware via decorators
@api.get("/limited")
@rate_limit(rps=100, burst=200)
async def limited_endpoint():
    return {"status": "ok"}

@api.get("/protected")
@auth_required(mode="api_key", api_keys={"secret-key"})
async def protected_endpoint(request: dict):
    # Access middleware context
    context = request.get("context", {})
    return {"authenticated": True}
```

## Built-in Middleware

### Rate Limiting
```python
@rate_limit(rps=100, burst=200, key="ip")
```
- `rps`: Requests per second limit
- `burst`: Burst capacity (default: 2x rps)
- `key`: Rate limit key ("ip", "user", "api_key", or header name)

### CORS
```python
@cors(
    origins=["https://example.com"],
    methods=["GET", "POST"],
    headers=["Content-Type"],
    credentials=True,
    max_age=3600
)
```

### Authentication
```python
@auth_required(
    mode="jwt",  # or "api_key", "session"
    algorithms=["HS256"],
    secret="your-secret",  # Optional - uses Django SECRET_KEY if not provided
    api_keys={"key1", "key2"},
    header="Authorization"
)
```

**JWT Secret Handling:**
- If `secret` is not provided, Django's `SECRET_KEY` is used automatically
- If neither is available, an error is returned (500) 
- For production, always use a strong secret

## Middleware Context

Middleware can share data via `request.context`:

```python
@api.get("/context-aware")
async def handler(request: dict):
    context = request.get("context", {})
    # Context contains middleware data like auth claims
    user_id = context.get("user_id")
    return {"user": user_id}
```

## Skipping Global Middleware

```python
from django_bolt.middleware import skip_middleware

@api.get("/no-cors")
@skip_middleware("cors", "rate_limit")
async def no_middleware():
    return {"unrestricted": True}
```

## Custom Middleware (Python)

```python
from django_bolt.middleware import Middleware

class LoggingMiddleware(Middleware):
    async def process_request(self, request, call_next):
        print(f"Request: {request['method']} {request['path']}")
        response = await call_next(request)
        return response

api = BoltAPI(middleware=[LoggingMiddleware()])
```

## Performance Notes

- **Zero-cost abstraction**: No performance impact when middleware isn't used
- **Rust execution**: Hot-path middleware (auth, rate limit, CORS) execute in Rust
- **Early exit**: Middleware can return responses without Python GIL
- **Shared context**: `PyRequest.context` enables efficient data sharing

## Architecture

1. **Request arrives** → Rust server
2. **Check middleware metadata** → O(1) lookup by handler_id
3. **Execute Rust middleware** → Rate limit, CORS preflight, auth
4. **Build PyRequest** → Include context dict if middleware present
5. **Execute Python handler** → Access context data
6. **Apply response middleware** → CORS headers, compression

The middleware system maintains Django-Bolt's 60k+ RPS performance for routes without middleware, while enabling powerful request processing capabilities when needed.
# Middleware

Django-Bolt provides middleware for cross-cutting concerns like CORS and rate limiting. This guide covers the built-in middleware and how to use it.

## CORS middleware

### Per-route CORS

Apply CORS to specific endpoints:

```python
from django_bolt.middleware import cors

@api.get("/api/data")
@cors(origins=["https://example.com"], credentials=True)
async def get_data():
    return {"data": "value"}
```

### CORS options

```python
@cors(
    origins=["https://example.com", "https://app.example.com"],
    methods=["GET", "POST", "PUT", "DELETE"],
    headers=["Content-Type", "Authorization"],
    credentials=True,
    max_age=3600,  # Preflight cache duration
)
```

### Global CORS

Configure CORS for all endpoints in `settings.py`:

```python
# Allow specific origins
BOLT_CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://app.example.com",
]

# Allow all origins (development only!)
BOLT_CORS_ALLOW_ALL_ORIGINS = True

# Additional settings
BOLT_CORS_ALLOW_CREDENTIALS = True
BOLT_CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
BOLT_CORS_ALLOW_HEADERS = ["Content-Type", "Authorization", "X-Requested-With"]
BOLT_CORS_EXPOSE_HEADERS = ["X-Total-Count", "X-Page-Count"]
BOLT_CORS_MAX_AGE = 86400  # 24 hours
```

## Rate limiting

### Per-route rate limiting

```python
from django_bolt.middleware import rate_limit

@api.get("/api/search")
@rate_limit(rps=10, burst=20)
async def search(q: str):
    return {"results": []}
```

Parameters:

- `rps` - Requests per second allowed
- `burst` - Maximum burst size (allows short spikes)

### How it works

Django-Bolt uses a token bucket algorithm:

- Tokens are added at `rps` per second
- Each request consumes one token
- The bucket holds up to `burst` tokens
- If no tokens are available, the request is rejected with 429 Too Many Requests

### Rate limit response

When rate limited, the response includes:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 1
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640000000
```

## Skipping middleware

Disable specific middleware for an endpoint:

```python
from django_bolt.middleware import skip_middleware

@api.get("/health")
@skip_middleware("cors", "rate_limit")
async def health():
    return {"status": "ok"}
```

Or skip all middleware:

```python
@api.get("/internal")
@skip_middleware("*")
async def internal():
    return {"internal": True}
```

## Compression

Django-Bolt automatically compresses responses. Disable for specific endpoints:

```python
from django_bolt.middleware import no_compress

@api.get("/stream")
@no_compress
async def stream():
    # Streaming responses should not be compressed
    return StreamingResponse(generate())
```

### Compression settings

Configure in `settings.py`:

```python
from django_bolt import CompressionConfig

# In your api.py
api = BoltAPI(
    compression=CompressionConfig(
        backend="brotli",     # "brotli", "gzip", or "zstd"
        minimum_size=1000,    # Only compress responses > 1KB
        gzip_fallback=True,   # Fall back to gzip if client doesn't support brotli
    )
)
```

## Custom middleware

Create custom middleware by defining a middleware function:

```python
from django_bolt.middleware import middleware

@middleware
async def timing_middleware(request, call_next):
    import time
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    return response

@api.get("/timed")
@timing_middleware
async def timed_endpoint():
    return {"status": "ok"}
```

## Django middleware integration

Use existing Django middleware with Django-Bolt:

```python
from django_bolt import DjangoMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

api = BoltAPI(
    middleware=[
        DjangoMiddleware(SessionMiddleware),
        DjangoMiddleware(AuthenticationMiddleware),
    ]
)
```

## Middleware order

Middleware is executed in the order specified:

1. CORS (handles preflight requests)
2. Rate limiting
3. Authentication (via `auth=` parameter)
4. Guards (via `guards=` parameter)
5. Your handler

For responses, the order is reversed.

## Performance

Django-Bolt's middleware runs in Rust where possible:

- CORS preflight handling
- Rate limiting with token bucket
- Response compression

This means these operations don't acquire the Python GIL, enabling higher throughput.

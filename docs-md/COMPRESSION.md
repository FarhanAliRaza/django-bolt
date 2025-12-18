### Compression

Django-Bolt supports transparent HTTP response compression. By default, the server negotiates compression with the client based on the `Accept-Encoding` header and only compresses responses that are large and compressible.

### Defaults

- **Algorithms**: brotli (br), gzip, zstd
- **Compression levels**: Optimized defaults from Actix Web (not configurable)
- **Negotiation**: automatic via `Accept-Encoding`
- **Minimum size**: 500 bytes (configurable)
- **Performance**: implemented in Rust with zero Python overhead

### How it works

When a request comes in with an `Accept-Encoding` header (e.g., `Accept-Encoding: gzip, br`):

1. **Route check**: If the route has `@no_compress`, compression is skipped entirely
2. **Backend selection**: Server selects the best compression algorithm:
   - If client supports the configured `backend` → use it
   - If not and `gzip_fallback=True` → use gzip
   - If client doesn't support any → no compression (identity)
3. **Size check**: Response must be ≥ `minimum_size` bytes
4. **Compression**: Response is compressed in Rust (zero Python overhead)
5. **Headers**: Sets `Content-Encoding` header (e.g., `Content-Encoding: br`)

### Quick test

- **Compressed response**:

```bash
curl -I -H "Accept-Encoding: gzip, br" http://127.0.0.1:8000/compression-test
# expect: Content-Encoding: gzip (or br)
```

- **Compression disabled per-route**:

```bash
curl -I -H "Accept-Encoding: gzip, br" http://127.0.0.1:8000/no-compression-test
# expect: Content-Encoding: identity
```

### Global configuration

You can configure compression behavior globally using `CompressionConfig`:

```python
from django_bolt.compression import CompressionConfig

# Default configuration (brotli with gzip fallback)
api = BoltAPI()  # compression enabled by default

# Custom configuration
api = BoltAPI(
    compression=CompressionConfig(
        backend="brotli",      # Primary algorithm: "brotli", "gzip", or "zstd"
        minimum_size=500,      # Only compress responses >= 500 bytes
        gzip_fallback=True,    # Fall back to gzip if client doesn't support backend
    )
)

# Disable compression globally
api = BoltAPI(compression=False)
```

**Configuration options:**

- `backend` (default: `"brotli"`): Primary compression algorithm
  - `"brotli"` - Best compression ratio (recommended)
  - `"gzip"` - Universal compatibility
  - `"zstd"` - Fastest compression

- `minimum_size` (default: `500`): Minimum response size in bytes to compress
  - Responses smaller than this are not compressed
  - Set higher for better performance, lower for more compression

- `gzip_fallback` (default: `True`): Fall back to gzip if client doesn't support the primary backend
  - Ensures maximum compatibility
  - Set to `False` for strict backend-only compression

**Note on compression levels:** Django-Bolt uses Actix Web's optimized default compression levels for each algorithm. Custom compression levels (e.g., gzip level 9, brotli quality 11) are not currently configurable due to limitations in the underlying Actix Web framework. See [actix-web#2928](https://github.com/actix/actix-web/issues/2928) for tracking.

### Per-route compression control

Use `@no_compress` to disable compression for specific routes. This is ideal for:
- Streaming responses (SSE, chunked data)
- Already-compressed content (images, videos)
- Debugging

```python
from django_bolt.middleware import no_compress

@api.get("/stream")
@no_compress
async def stream_plain():
    def gen():
        yield "hello\n"
        yield "world\n"
    return StreamingResponse(gen(), media_type="text/plain")
```

**Alternative syntax:** `@skip_middleware("compression")`

Under the hood, routes marked with `@no_compress` will emit `Content-Encoding: identity`, ensuring intermediaries and the server's compression layer do not compress the response.

### Examples

**Example 1: Maximum compatibility (gzip only)**

```python
api = BoltAPI(
    compression=CompressionConfig(
        backend="gzip",
        gzip_fallback=False  # No fallback needed
    )
)
```

**Example 2: Best compression (brotli with fallback)**

```python
api = BoltAPI(
    compression=CompressionConfig(
        backend="brotli",     # Best ratio
        gzip_fallback=True,   # Fallback for older clients
        minimum_size=1000     # Only compress larger responses
    )
)
```

**Example 3: Fastest compression (zstd)**

```python
api = BoltAPI(
    compression=CompressionConfig(
        backend="zstd",       # Fastest algorithm
        gzip_fallback=True,   # Fallback for compatibility
        minimum_size=2000     # Higher threshold for speed
    )
)
```

### Best practices

1. **Use brotli by default** - It provides the best compression ratio and is widely supported by modern browsers
2. **Keep gzip_fallback=True** - Ensures compatibility with older clients
3. **Adjust minimum_size** based on your use case:
   - Lower (256-500) for bandwidth-constrained environments
   - Higher (1000-2000) for CPU-constrained or high-throughput scenarios
4. **Always use @no_compress for streaming** - SSE, WebSocket upgrades, and chunked responses should not be compressed
5. **Don't compress already-compressed content** - Images, videos, and pre-compressed files should use `@no_compress`

### Performance considerations

- **Zero Python overhead**: Compression runs entirely in Rust
- **Automatic negotiation**: No manual header inspection needed
- **Streaming-friendly**: Routes can opt-out without global config changes
- **Size-aware**: Small responses aren't compressed (saves CPU)
- **Optimal defaults**: Actix Web uses well-tuned compression levels for production

### Compression

Django-Bolt supports transparent HTTP response compression. By default, the server negotiates compression with the client based on the `Accept-Encoding` header and only compresses responses that are large and compressible.

### Defaults

- **Algorithms**: brotli (br), gzip, zstd
- **Negotiation**: automatic via `Accept-Encoding`
- **Heuristics**: compresses large, compressible payloads
- **Performance**: implemented in Rust

### Disable compression per route

Use `@no_compress` to turn off compression for a specific handler. This is ideal for streaming responses (SSE, chunked data), already-compressed content, and debugging.

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

Equivalent: `@skip_middleware("compression")`.

Under the hood, routes marked with `@no_compress` will emit `Content-Encoding: identity`, ensuring intermediaries and the server's compression layer do not compress the response.

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

### Global configuration (note)

A `CompressionConfig` exists in Python for future tuning (algorithm, quality/level, minimum size, gzip fallback). The Rust server currently performs automatic negotiation with sensible defaults; route-level disabling via `@no_compress` is supported and recommended for streaming use-cases.

```python
from django_bolt.compression import CompressionConfig

api = BoltAPI(
    compression=CompressionConfig(
        backend="brotli",  # or "gzip", "zstd"
        minimum_size=500,
    )
)
```

If you need a route to bypass compression, prefer `@no_compress`.

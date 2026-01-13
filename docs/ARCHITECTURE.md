# Django-Bolt Architecture Deep Dive

This document explains the complete architecture of Django-Bolt, from server orchestration to request handling.

## Table of Contents

1. [Server Orchestration](#1-server-orchestration-how-it-all-starts)
2. [Actix Server Parameters](#2-actix-server-parameters-explained)
3. [Scaling Architecture](#3-scaling-architecture)
4. [Complete Request Hot Path](#4-the-complete-request-hot-path)
5. [Why Django ORM Just Works](#5-why-django-orm-just-works)
6. [Key Data Structures](#6-key-data-structures)

---

## 1. Server Orchestration: How It All Starts

### Python Entry Point (`runbolt` management command)

When you run `python manage.py runbolt`, the flow begins in `python/django_bolt/management/commands/runbolt.py`:

```
runbolt.handle()
    |
    +-- Single Process Mode (default)
    |       +-- start_single_process()
    |
    +-- Multi-Process Mode (--processes N)
            +-- start_multiprocess()
                    +-- os.fork() x N times
                            +-- Each child calls start_single_process()
```

**Key startup sequence in `start_single_process()`:**

1. **Autodiscovery** (`autodiscover_apis()`): Scans Django apps for `api.py` files containing `BoltAPI` instances
2. **API Merging** (`merge_apis()`): Combines all discovered APIs into one merged router with unique handler IDs
3. **Route Registration** (`_core.register_routes()`): Passes routes to Rust
4. **Middleware Registration** (`_core.register_middleware_metadata()`): Compiles Python middleware config to Rust metadata
5. **Server Start** (`_core.start_server_async()`): Launches Actix Web server

### Rust Server Initialization (`src/server.rs`)

```rust
#[pyfunction]
pub fn start_server_async(
    py: Python<'_>,
    dispatch: Py<PyAny>,      // Python _dispatch function
    host: String,
    port: u16,
    compression_config: Option<Py<PyAny>>,
) -> PyResult<()>
```

**What happens inside:**

1. **Tokio Runtime Configuration**:
   ```rust
   let mut runtime_builder = tokio::runtime::Builder::new_multi_thread();
   runtime_builder.max_blocking_threads(blocking_threads); // Default: 1024
   pyo3_async_runtimes::tokio::init(runtime_builder);
   ```

2. **Python Event Loop Creation**:
   - Tries uvloop first (2-4x faster than asyncio)
   - Falls back to standard asyncio if uvloop unavailable
   - Spawns a dedicated thread running `loop.run_forever()`

3. **Django Settings Read**:
   - `DEBUG`, `BOLT_MAX_HEADER_SIZE`, `BOLT_MAX_UPLOAD_SIZE`
   - All `CORS_*` settings (django-cors-headers compatible)

4. **CORS Configuration Compilation**:
   - Regex patterns compiled at startup (zero runtime overhead)
   - Global CORS config injected into routes without explicit config

5. **Actix HttpServer Creation**:
   ```rust
   HttpServer::new(move || {
       App::new()
           .app_data(web::Data::new(app_state.clone()))
           .app_data(web::PayloadConfig::new(max_payload_size))
           .wrap(NormalizePath::new(TrailingSlash::MergeOnly))
           .wrap(CorsMiddleware::new())
           .wrap(CompressionMiddleware::new())
           .default_service(web::to(handle_request))
   })
   .keep_alive(keep_alive)
   .client_request_timeout(std::time::Duration::from_secs(0))
   .workers(workers)
   ```

---

## 2. Actix Server Parameters Explained

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `workers` | `DJANGO_BOLT_WORKERS` or 1 | Number of Actix worker threads per process |
| `keep_alive` | `DJANGO_BOLT_KEEP_ALIVE` or OS default | HTTP keep-alive timeout |
| `client_request_timeout` | 0 (disabled) | Disables client request timeout |
| `max_payload_size` | `BOLT_MAX_UPLOAD_SIZE` or 1MB | Max request body size |
| `backlog` | `DJANGO_BOLT_BACKLOG` or 1024 | TCP listen queue size |

### Socket Configuration

```rust
let socket = Socket::new(domain, Type::STREAM, Some(Protocol::TCP))?;
socket.set_reuse_address(true)?;

// Only set when DJANGO_BOLT_REUSE_PORT=1 (multi-process mode)
#[cfg(not(target_os = "windows"))]
if use_reuse_port {
    socket.set_reuse_port(true)?;  // SO_REUSEPORT for kernel load balancing
}

socket.bind(&addr.into())?;
socket.listen(backlog)?;
```

**SO_REUSEPORT**: Allows multiple processes to bind to the same port. The kernel distributes incoming connections across all processes - this is how multi-process scaling works.

---

## 3. Scaling Architecture

### Single Process (default)

```
                     +-----------------------------+
                     |       Actix HttpServer      |
HTTP Request ------->|  +----------------------+  |
                     |  |   Worker Thread 1    |  |
                     |  |   (Tokio Runtime)    |  |
                     |  +----------------------+  |
                     |         |                  |
                     |   Python GIL + Handler     |
                     +-----------------------------+
```

### Multi-Process (`--processes N`)

```
                           Kernel SO_REUSEPORT Load Balancer
                                      |
        +-----------------------------+-----------------------------+
        |                             |                             |
        v                             v                             v
+------------------+        +------------------+        +------------------+
|   Process 0      |        |   Process 1      |        |   Process N      |
|  +------------+  |        |  +------------+  |        |  +------------+  |
|  |Actix Server|  |        |  |Actix Server|  |        |  |Actix Server|  |
|  | 1 Worker   |  |        |  | 1 Worker   |  |        |  | 1 Worker   |  |
|  +------------+  |        |  +------------+  |        |  +------------+  |
|  Own Python GIL  |        |  Own Python GIL  |        |  Own Python GIL  |
|  Own Django      |        |  Own Django      |        |  Own Django      |
+------------------+        +------------------+        +------------------+
```

**Why this design?**

- **Each process has its own Python interpreter** - No GIL contention across processes
- **1 Actix worker per process** - Tokio handles async concurrency within that worker
- **SO_REUSEPORT** - Kernel-level load balancing (no userspace proxy needed)

### Thread Model

Actix workers use **threads**, but Django-Bolt runs with 1 worker per process because:

1. **Python GIL**: Multiple Actix worker threads would contend for the single GIL
2. **Process isolation**: Each process has independent GIL, enabling true parallelism
3. **Memory efficiency**: Each process has separate Django ORM connections

The Tokio runtime provides async concurrency within each process via:
- **Core threads**: Handle async I/O (HTTP, database, etc.)
- **Blocking threads** (default 1024): For `sync_to_thread()` operations

---

## 4. The Complete Request Hot Path

Here's every function a request touches, from TCP accept to HTTP response:

### Phase 1: Actix Receives Request

```
TCP Connection
    |
    v
Actix HttpServer (Rust)
    |
    v
NormalizePath Middleware
    | (merges // -> /, no trailing slash changes)
    v
CorsMiddleware (src/middleware/cors.rs)
    | (adds CORS headers to response)
    v
CompressionMiddleware (src/middleware/compression.rs)
    | (gzip/brotli/zstd based on Accept-Encoding)
    v
default_service -> handle_request()
```

### Phase 2: Route Matching (`src/handler.rs`)

```rust
pub async fn handle_request(
    req: HttpRequest,
    mut payload: web::Payload,
    state: web::Data<Arc<AppState>>,
) -> HttpResponse
```

**Step 1: Route Lookup**
```rust
let router = GLOBAL_ROUTER.get().expect("Router not initialized");

// Elysia-style two-phase lookup:
// 1. O(1) HashMap for static routes (/users, /health)
// 2. Radix tree for dynamic routes (/users/{id})
let (path_params, handler_id) = {
    if let Some(route_match) = router.find(method, path) {
        let handler_id = route_match.handler_id();
        let raw_params = route_match.path_params();
        // URL-decode path parameters
        (path_params, handler_id)
    } else {
        // 404 handling, trailing slash redirect, automatic OPTIONS
        return responses::error_404();
    }
};
```

### Phase 3: Pre-Handler Validation (Rust-native, no GIL)

**Step 2: Route Metadata Lookup**
```rust
let route_metadata = ROUTE_METADATA
    .get()
    .and_then(|meta_map| meta_map.get(&handler_id).cloned());
```

**Step 3: Query String Parsing**
```rust
// Optimization: Skip if handler doesn't need query params
let needs_query = route_metadata.as_ref().map(|m| m.needs_query).unwrap_or(true);
let query_params = if needs_query {
    parse_query_string(req.uri().query().unwrap_or(""))
} else {
    AHashMap::new()
};
```

**Step 4: Type Validation**
```rust
// Rust-native type checking (no Python needed)
if let Some(ref route_meta) = route_metadata {
    if let Some(response) = validate_typed_params(
        &path_params, &query_params, &route_meta.param_types
    ) {
        return response;  // 422 for invalid types
    }
}
```

**Step 5: Rate Limiting**
```rust
if let Some(ref rate_config) = route_meta.rate_limit_config {
    if let Some(response) = middleware::rate_limit::check_rate_limit(...) {
        return response;  // 429 Too Many Requests
    }
}
```

**Step 6: Authentication & Guards**
```rust
let auth_ctx = match validate_auth_and_guards(
    &headers,
    &route_meta.auth_backends,
    &route_meta.guards
) {
    AuthGuardResult::Allow(ctx) => ctx,
    AuthGuardResult::Unauthorized => return responses::error_401(),
    AuthGuardResult::Forbidden => return responses::error_403(),
};
```

### Phase 4: Python Handler Dispatch

**Step 7: GIL Acquisition & Handler Call**
```rust
let fut = match Python::attach(|py| -> PyResult<_> {
    // Get handler from router
    let handler = router.find(&method_owned, &path_owned)
        .map(|rm| rm.route().handler.clone_ref(py))?;

    // Build PyRequest object
    let request = PyRequest {
        method, path, body,
        path_params, query_params, headers, cookies,
        context: auth_ctx,
        form_map, files_map,
        ...
    };

    // Call Python dispatch coroutine
    let coroutine = dispatch.call1(py, (handler, request_obj, handler_id))?;
    pyo3_async_runtimes::into_future_with_locals(locals, coroutine.into_bound(py))
}) {
    Ok(f) => f,
    Err(e) => return handle_python_error(...),
};
```

### Phase 5: Python Execution (`python/django_bolt/api.py`)

```python
async def _dispatch(self, handler, request, handler_id):
    # 1. Get handler metadata
    meta = self._handler_meta[handler_id]

    # 2. Lazy user loading (only loads from DB if request.user accessed)
    if auth_context and auth_context.get("user_id"):
        request["user"] = SimpleLazyObject(
            partial(load_user_sync, user_id, backend_name, ...)
        )

    # 3. Check for Python middleware
    if api_with_middleware:
        response = await self._dispatch_with_middleware(...)
    else:
        # 4. Fast path: Use pre-compiled argument injector
        if meta.get("injector_is_async", False):
            args, kwargs = await meta["injector"](request)
        else:
            args, kwargs = meta["injector"](request)

        # 5. Execute handler
        if is_async:
            result = await handler(*args, **kwargs)
        else:
            if is_blocking:  # ORM detected at registration time
                result = await sync_to_thread(handler, *args, **kwargs)
            else:
                result = handler(*args, **kwargs)

        # 6. Serialize response (msgspec for JSON - 5-10x faster)
        response = await serialize_response(result, meta)

    return response
```

### Phase 6: Response Building (`src/handler.rs`)

```rust
match fut.await {
    Ok(result_obj) => {
        // Fast-path: extract tuple (status, headers, body) in single GIL acquisition
        let fast_tuple: Option<(u16, Vec<(String, String)>, Vec<u8>)> =
            Python::attach(|py| {
                // Extract status code, headers, and body bytes
                Some((status_code, resp_headers, body_vec))
            });

        if let Some((status_code, resp_headers, body_bytes)) = fast_tuple {
            // Build Actix HttpResponse
            return response_builder::build_response_with_headers(
                status, headers, skip_compression, response_body
            );
        }
    }
    Err(e) => handle_python_error(...)
}
```

---

## 5. Why Django ORM Just Works

### The Magic of `sync_to_thread()`

Django ORM is synchronous, but Django-Bolt handlers are async. The bridge:

```python
# python/django_bolt/concurrency.py
async def sync_to_thread(func, *args, **kwargs):
    """Run sync function in thread pool without blocking event loop."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))
```

### Static ORM Detection

At **registration time**, Django-Bolt analyzes handlers:

```python
# python/django_bolt/analysis.py
def analyze_handler(fn) -> HandlerAnalysis:
    """Detect blocking operations via AST analysis."""
    # Looks for: Model.objects.*, queryset methods, file I/O, etc.
    return HandlerAnalysis(is_blocking=True/False)
```

If `is_blocking=True`, the handler automatically runs in thread pool:

```python
# In _dispatch():
if is_blocking:
    result = await sync_to_thread(handler, *args, **kwargs)
else:
    result = handler(*args, **kwargs)  # Pure CPU work - no thread pool overhead
```

### Async ORM Support

Django 4.1+ provides async ORM methods (`aget`, `afilter`, etc.):

```python
@api.get("/users/{user_id}")
async def get_user(user_id: int):
    # Uses async ORM - runs directly on event loop
    return await User.objects.aget(pk=user_id)
```

---

## 6. Key Data Structures

### Global State (`src/state.rs`)

```rust
pub static GLOBAL_ROUTER: OnceCell<Arc<Router>> = OnceCell::new();
pub static GLOBAL_WEBSOCKET_ROUTER: OnceCell<Arc<WebSocketRouter>> = OnceCell::new();
pub static TASK_LOCALS: OnceCell<TaskLocals> = OnceCell::new();  // Python event loop
pub static ROUTE_METADATA: OnceCell<Arc<AHashMap<usize, RouteMetadata>>> = OnceCell::new();
```

### Router (`src/router.rs`)

```rust
struct MethodRouter {
    /// O(1) HashMap for static routes (/users, /health)
    static_routes: AHashMap<String, Route>,

    /// Radix tree (matchit) for dynamic routes (/users/{id})
    dynamic_router: MatchRouter<Route>,
}

pub struct Router {
    get: MethodRouter,
    post: MethodRouter,
    put: MethodRouter,
    // ... one per HTTP method
}
```

### Route Metadata (`src/metadata.rs`)

```rust
pub struct RouteMetadata {
    pub auth_backends: Vec<AuthBackendConfig>,
    pub guards: Vec<GuardConfig>,
    pub cors_config: Option<CorsConfig>,
    pub rate_limit_config: Option<RateLimitConfig>,
    pub param_types: AHashMap<String, String>,  // For Rust-side type coercion
    pub needs_query: bool,      // Optimization flag
    pub needs_headers: bool,    // Optimization flag
    pub needs_cookies: bool,    // Optimization flag
    pub skip: AHashSet<String>, // @skip_middleware("cors", "compression")
    // ...
}
```

---

## Summary: The Hot Path Timeline

```
                                              TIME -->
-------------------------------------------------------------------------------
RUST (no GIL)                          | PYTHON (holds GIL)
-------------------------------------------------------------------------------
TCP Accept                             |
    |                                  |
NormalizePath                          |
    |                                  |
CorsMiddleware (adds headers)          |
    |                                  |
CompressionMiddleware                  |
    |                                  |
Route Matching (O(1) or radix tree)    |
    |                                  |
Query String Parsing                   |
    |                                  |
Type Validation (returns 422)          |
    |                                  |
Rate Limiting (returns 429)            |
    |                                  |
Auth + Guards (returns 401/403)        |
    |                                  |
Header/Cookie Parsing                  |
    |                                  |
Form/File Parsing                      |
    |                                  |
GIL Acquire ---------------------------+--> Build PyRequest
                                       |        |
                                       |    Argument Injection
                                       |        |
                                       |    Handler Execution
                                       |        | (ORM -> thread pool)
                                       |        |
                                       |    Response Serialization
                                       |        |
GIL Release <--------------------------+--------+
    |                                  |
Build HttpResponse                     |
    |                                  |
Compression (if enabled)               |
    |                                  |
Send Response                          |
-------------------------------------------------------------------------------
```

**Key insight**: All validation, routing, auth, and rate limiting happen in Rust without touching Python's GIL. Python is only invoked for the actual handler business logic.

---
icon: lucide/play
---

# Lifecycle hooks

Django-Bolt provides startup and shutdown lifecycle hooks for running code before the server starts accepting requests and after it stops.

## Quick start

Register lifecycle hooks using decorators:

```python
from django_bolt import BoltAPI

api = BoltAPI()

@api.on_startup
async def startup():
    print("Server starting...")
    # Initialize resources, load models, etc.

@api.on_shutdown
async def shutdown():
    print("Server stopping...")
    # Close connections, cleanup resources, etc.
```

## When hooks run

### Startup hooks

Startup hooks run:

- After route registration
- After middleware compilation
- After authentication backends are registered
- **Before** the server starts accepting HTTP requests

Use startup hooks for initialization that must complete before handling requests.

### Shutdown hooks

Shutdown hooks run:

- When the server receives a shutdown signal (SIGINT/SIGTERM)
- Via `atexit` when the process exits

Use shutdown hooks for cleanup that should happen when the server stops.

## Async and sync handlers

Both async and sync handlers are supported:

```python
# Async handler
@api.on_startup
async def async_startup():
    await database.connect()

# Sync handler
@api.on_startup
def sync_startup():
    load_config_from_file()
```

Async handlers are awaited. Sync handlers are called directly in the async context.

## Multiple handlers

Register multiple handlers - they run in registration order:

```python
@api.on_startup
async def load_config():
    print("1. Loading config...")

@api.on_startup
async def connect_database():
    print("2. Connecting to database...")

@api.on_startup
async def warm_cache():
    print("3. Warming cache...")
```

Output:
```
1. Loading config...
2. Connecting to database...
3. Warming cache...
```

## Error handling

### Startup errors

Startup handler exceptions **propagate** and prevent server startup:

```python
@api.on_startup
async def required_service():
    connection = await connect_to_required_service()
    if not connection:
        raise RuntimeError("Required service unavailable")
```

If this fails, the server won't start. This is intentional - fail fast for required initialization.

### Shutdown errors

Shutdown handler exceptions are **logged but don't propagate**:

```python
@api.on_shutdown
async def close_database():
    await db.close()  # If this fails...

@api.on_shutdown
async def close_cache():
    await cache.close()  # ...this still runs
```

All shutdown handlers run even if some fail. This ensures best-effort cleanup.

## Main API only

**Important:** Only lifecycle hooks on the main API are executed.

The main API is the project-level `api.py` file (in the same directory as `settings.py`). Hooks on sub-apps or autodiscovered app APIs are ignored.

```python
# project/api.py - Main API, hooks ARE executed
from django_bolt import BoltAPI

api = BoltAPI()

@api.on_startup
async def main_startup():
    print("This runs!")

# myapp/api.py - Sub-app, hooks are NOT executed
from django_bolt import BoltAPI

api = BoltAPI()

@api.on_startup
async def app_startup():
    print("This does NOT run!")
```

This prevents duplicate initialization when multiple APIs are autodiscovered.

## Common patterns

### Database connection pool

```python
from django_bolt import BoltAPI
import asyncpg

api = BoltAPI()
db_pool = None

@api.on_startup
async def create_pool():
    global db_pool
    db_pool = await asyncpg.create_pool(
        "postgresql://user:pass@localhost/db",
        min_size=5,
        max_size=20
    )

@api.on_shutdown
async def close_pool():
    global db_pool
    if db_pool:
        await db_pool.close()
```

### ML model loading

```python
from django_bolt import BoltAPI

api = BoltAPI()
model = None

@api.on_startup
async def load_model():
    global model
    print("Loading ML model...")
    model = await load_heavy_model("path/to/model")
    print("Model loaded!")

@api.get("/predict")
async def predict(data: PredictRequest):
    return {"result": model.predict(data.features)}
```

### External service connections

```python
from django_bolt import BoltAPI
import aioredis

api = BoltAPI()
redis = None

@api.on_startup
async def connect_redis():
    global redis
    redis = await aioredis.from_url("redis://localhost")

@api.on_shutdown
async def disconnect_redis():
    global redis
    if redis:
        await redis.close()
```

### Configuration loading

```python
from django_bolt import BoltAPI

api = BoltAPI()
config = {}

@api.on_startup
def load_config():
    global config
    with open("/etc/myapp/config.yaml") as f:
        config = yaml.safe_load(f)
```

## Direct registration

You can also register handlers directly without decorators:

```python
async def my_startup():
    print("Starting...")

async def my_shutdown():
    print("Stopping...")

api.on_startup(my_startup)
api.on_shutdown(my_shutdown)
```

## Multi-process considerations

In multi-process mode (`--processes N`), each process:

- Has its own Python interpreter
- Runs startup hooks independently
- Maintains separate resource instances

```python
@api.on_startup
async def startup():
    # This runs once per process, not once total
    print(f"Process {os.getpid()} starting...")
```

For shared state across processes, use external stores (Redis, database, etc.).

## Comparison with FastAPI

Django-Bolt lifecycle hooks follow FastAPI's pattern:

| FastAPI | Django-Bolt |
|---------|-------------|
| `@app.on_event("startup")` | `@api.on_startup` |
| `@app.on_event("shutdown")` | `@api.on_shutdown` |

FastAPI's `lifespan` context manager is not currently supported.

## Example: Complete setup

```python
from django_bolt import BoltAPI
import asyncpg
import aioredis

api = BoltAPI()

# Global resources
db_pool = None
redis_client = None

@api.on_startup
async def init_database():
    """Initialize database connection pool."""
    global db_pool
    db_pool = await asyncpg.create_pool(
        "postgresql://localhost/myapp",
        min_size=10,
        max_size=50
    )
    print("Database pool initialized")

@api.on_startup
async def init_redis():
    """Initialize Redis connection."""
    global redis_client
    redis_client = await aioredis.from_url(
        "redis://localhost",
        encoding="utf-8",
        decode_responses=True
    )
    print("Redis connected")

@api.on_startup
async def warm_cache():
    """Pre-populate frequently accessed data."""
    users = await db_pool.fetch("SELECT * FROM users LIMIT 1000")
    for user in users:
        await redis_client.set(f"user:{user['id']}", user['email'])
    print(f"Cache warmed with {len(users)} users")

@api.on_shutdown
async def cleanup_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        print("Redis disconnected")

@api.on_shutdown
async def cleanup_database():
    """Close database pool."""
    global db_pool
    if db_pool:
        await db_pool.close()
        print("Database pool closed")

# Your API routes
@api.get("/users/{user_id}")
async def get_user(user_id: int):
    cached = await redis_client.get(f"user:{user_id}")
    if cached:
        return {"email": cached, "source": "cache"}

    user = await db_pool.fetchrow(
        "SELECT * FROM users WHERE id = $1", user_id
    )
    return {"email": user["email"], "source": "database"}
```

## See also

- [Health checks](health-checks.md) - For readiness/liveness probes
- [Middleware](middleware.md) - For per-request lifecycle
- [Signals](signals.md) - For Django signal integration

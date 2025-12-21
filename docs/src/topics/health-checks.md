---
icon: lucide/heart-pulse
---

# Health checks

Django-Bolt provides a built-in health check system for Kubernetes readiness/liveness probes and load balancer health checks.

## Quick start

Register health check endpoints on your API:

```python
from django_bolt import BoltAPI
from django_bolt.health import register_health_checks

api = BoltAPI()
register_health_checks(api)
```

This adds two endpoints:

- `GET /health` - Simple liveness probe
- `GET /ready` - Readiness probe with service checks

## Endpoints

### Liveness probe (/health)

Returns immediately with status `ok`:

```json
{"status": "ok"}
```

Use this for Kubernetes liveness probes. It confirms the application is running.

### Readiness probe (/ready)

Runs all registered health checks and returns aggregate status:

```json
{
    "status": "healthy",
    "checks": {
        "check_database": {
            "healthy": true,
            "message": "Database OK"
        },
        "check_redis": {
            "healthy": true,
            "message": "Redis OK"
        }
    }
}
```

If any check fails:

```json
{
    "status": "unhealthy",
    "checks": {
        "check_database": {
            "healthy": true,
            "message": "Database OK"
        },
        "check_redis": {
            "healthy": false,
            "message": "Redis connection timeout"
        }
    }
}
```

## Built-in checks

### Database check

Django-Bolt includes a database check:

```python
from django_bolt.health import check_database

# Runs: await connection.ensure_connection()
healthy, message = await check_database()
```

This check is not automatically registered. Add it manually if needed.

## Custom health checks

### Adding global checks

Add checks that run on every `/ready` request:

```python
from django_bolt.health import add_health_check

async def check_redis():
    """Check Redis connectivity."""
    try:
        # Your Redis check logic
        redis_client.ping()
        return True, "Redis OK"
    except Exception as e:
        return False, f"Redis error: {e}"

async def check_external_api():
    """Check external API availability."""
    try:
        # Your API check logic
        return True, "API OK"
    except Exception as e:
        return False, f"API unavailable: {e}"

add_health_check(check_redis)
add_health_check(check_external_api)
```

### Health check function signature

Health check functions must:

1. Be async (`async def`)
2. Take no arguments
3. Return a tuple of `(bool, str)` - (healthy, message)

```python
async def my_check() -> tuple[bool, str]:
    # Your check logic
    return True, "Check passed"
```

### Using HealthCheck class directly

For more control, use the `HealthCheck` class:

```python
from django_bolt.health import HealthCheck

health_check = HealthCheck()

async def check_database():
    return True, "Database OK"

async def check_cache():
    return True, "Cache OK"

health_check.add_check(check_database)
health_check.add_check(check_cache)

# Run all checks
results = await health_check.run_checks()
# {
#     "status": "healthy",
#     "checks": {
#         "check_database": {"healthy": True, "message": "Database OK"},
#         "check_cache": {"healthy": True, "message": "Cache OK"}
#     }
# }
```

## Exception handling

Health checks catch exceptions automatically:

```python
async def failing_check():
    raise RuntimeError("Something broke")

health_check.add_check(failing_check)
results = await health_check.run_checks()
# {
#     "status": "unhealthy",
#     "checks": {
#         "failing_check": {
#             "healthy": False,
#             "message": "Something broke"
#         }
#     }
# }
```

## Kubernetes configuration

### Liveness probe

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Readiness probe

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 3
```

## Example: Complete setup

```python
from django_bolt import BoltAPI
from django_bolt.health import register_health_checks, add_health_check

api = BoltAPI()

# Register health endpoints
register_health_checks(api)

# Add database check
async def check_database():
    try:
        from django.db import connection
        await connection.ensure_connection()
        return True, "Database OK"
    except Exception as e:
        return False, f"Database error: {e}"

# Add Redis check
async def check_redis():
    try:
        import redis
        r = redis.Redis()
        r.ping()
        return True, "Redis OK"
    except Exception as e:
        return False, f"Redis error: {e}"

# Add message queue check
async def check_celery():
    try:
        from celery import current_app
        current_app.control.ping(timeout=1)
        return True, "Celery OK"
    except Exception as e:
        return False, f"Celery error: {e}"

add_health_check(check_database)
add_health_check(check_redis)
add_health_check(check_celery)
```

## Excluding from logs

By default, health check paths are excluded from logging:

```python
from django_bolt.logging import LoggingConfig

config = LoggingConfig()
print(config.skip_paths)
# {'/health', '/ready', '/metrics'}
```

See the [Logging](logging.md) guide for more details.

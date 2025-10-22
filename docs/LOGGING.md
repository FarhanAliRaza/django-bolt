# Logging in Django-Bolt

## Overview

Django-Bolt provides a comprehensive, production-ready logging system with a queue-based, non-blocking architecture inspired by Litestar. The logging system automatically integrates with Django's logging configuration and provides structured logging for HTTP requests, responses, and exceptions with minimal performance overhead.

**Key Features:**
- **Non-blocking queue-based logging** - Log records are enqueued instantly and processed in a background thread
- **Automatic Django integration** - Seamlessly works with Django's `LOGGING` configuration
- **Smart filtering** - Sample rates, slow-query logging, and path/status code filtering
- **Security-first** - Automatic obfuscation of sensitive headers and cookies
- **Adaptive log levels** - INFO for successful requests, WARNING for 4xx, ERROR for 5xx
- **Zero overhead when disabled** - Respects logger levels for minimal performance impact

## Default Behavior

When your Django project does **not** define a custom `LOGGING` setting, Django-Bolt automatically configures a shared queue-based logging pipeline:

- **Queue logging** - Root, `django`, `django.server`, and `django_bolt` loggers are wired to a `QueueHandler`/`QueueListener` pair
- **Background processing** - All log formatting and I/O happens off the request thread
- **Production defaults** - With `DEBUG=False`, the framework logs successful 2xx/3xx responses only when they are "slow" (default: ≥250 ms)
- **Error logging** - 4xx errors log at `WARNING` level, 5xx errors log at `ERROR` level
- **Request logging** - All incoming requests are logged at `DEBUG` level
- **Zero overhead** - Each request/response logging call is guarded by `logger.isEnabledFor(...)`, so if your logger level is `ERROR`, there is effectively zero overhead

## LoggingConfig Class

The `LoggingConfig` class controls all aspects of request/response logging:

```python
from django_bolt.logging import LoggingConfig

logging_config = LoggingConfig(
    # Logger name (defaults to Django's logger)
    logger_name="django.server",

    # Request logging fields
    request_log_fields={
        "method",       # HTTP method (GET, POST, etc.)
        "path",         # Request path
        "query",        # Query string
        "headers",      # Request headers (obfuscated)
        "body",         # Request body (if log_request_body=True)
        "client_ip",    # Client IP address
        "user_agent",   # User agent string
        "request_id",   # Request ID (if available)
    },

    # Response logging fields
    response_log_fields={
        "status_code",  # HTTP status code
        "headers",      # Response headers
        "body",         # Response body (if log_response_body=True)
        "duration",     # Response time in seconds
        "size",         # Response size in bytes
    },

    # Security: Headers to obfuscate in logs
    obfuscate_headers={
        "authorization",
        "cookie",
        "x-api-key",
        "x-auth-token",
    },

    # Security: Cookies to obfuscate in logs
    obfuscate_cookies={
        "sessionid",
        "csrftoken",
    },

    # Body logging (use with caution)
    log_request_body=False,          # Log request body
    log_response_body=False,         # Log response body
    max_body_log_size=1024,          # Maximum body size to log (bytes)

    # Performance: Sampling and filtering
    sample_rate=None,                # Sample 2xx/3xx logs (0.0-1.0, None=all)
    min_duration_ms=None,            # Only log slow requests (None=all)

    # Skip logging for specific paths/status codes
    skip_paths={"/health", "/ready", "/metrics"},
    skip_status_codes=set(),         # e.g., {404, 403}

    # Exception logging
    error_log_level="ERROR",         # Log level for exceptions
    exception_logging_handler=None,  # Custom exception handler (Callable)
)
```

### Available Request Log Fields

The `request_log_fields` parameter accepts any combination of:

| Field | Description | Example Value |
|-------|-------------|---------------|
| `method` | HTTP method | `"GET"`, `"POST"` |
| `path` | Request path | `"/api/users/123"` |
| `query` | Query string parameters | `{"page": "1", "limit": "10"}` |
| `headers` | Request headers (obfuscated) | `{"content-type": "application/json"}` |
| `body` | Request body (requires `log_request_body=True`) | `{"email": "user@example.com"}` |
| `client_ip` | Client IP address | `"192.168.1.100"` |
| `user_agent` | User agent string | `"Mozilla/5.0..."` |
| `request_id` | Request ID (if available) | `"req-abc123"` |

### Available Response Log Fields

The `response_log_fields` parameter accepts any combination of:

| Field | Description | Example Value |
|-------|-------------|---------------|
| `status_code` | HTTP status code | `200`, `404`, `500` |
| `headers` | Response headers | `{"content-type": "application/json"}` |
| `body` | Response body (requires `log_response_body=True`) | `{"id": 123, "name": "John"}` |
| `duration` | Response time in seconds | `0.123` (logged as `duration_ms`) |
| `size` | Response size in bytes | `1024` |

## Queue-Based Non-Blocking Architecture

Django-Bolt uses Python's `QueueHandler` and `QueueListener` for non-blocking logging:

```
HTTP Request → Handler Execution
                    ↓
            Log Record Created
                    ↓
         Enqueued to Queue (instant, no blocking)
                    ↓
    Background QueueListener Thread
                    ↓
      Formatting & I/O (console output)
```

**Benefits:**
- **Zero blocking** - Request handling never waits for log I/O
- **Production-safe** - Can enable verbose logging without impacting throughput
- **Automatic cleanup** - Listener is stopped on shutdown via `atexit`

### Implementation Details

```python
from queue import Queue
from logging.handlers import QueueHandler, QueueListener

# Global queue and listener (singleton)
_QUEUE = Queue(-1)  # Unlimited queue size
_QUEUE_LISTENER = QueueListener(
    _QUEUE,
    logging.StreamHandler(),  # Console output
)
_QUEUE_LISTENER.start()

# All loggers use the QueueHandler
queue_handler = QueueHandler(_QUEUE)
logger.addHandler(queue_handler)
```

The queue and listener are created once during server startup and shared across all requests. The background thread continuously processes log records and writes them to stderr.

## Field Selection

You can customize which fields are logged for requests and responses:

### Minimal Logging (Production)

```python
from django_bolt.logging import LoggingConfig

# Only log essentials
logging_config = LoggingConfig(
    request_log_fields={"method", "path"},
    response_log_fields={"status_code", "duration"},
)
```

**Output:**
```
INFO - 2025-10-22 15:30:45 - django.server - GET /api/users 200 (45.23ms)
```

### Verbose Logging (Development)

```python
# Log everything
logging_config = LoggingConfig(
    request_log_fields={
        "method", "path", "query", "headers",
        "client_ip", "user_agent"
    },
    response_log_fields={
        "status_code", "duration", "size"
    },
)
```

**Output:**
```
DEBUG - 2025-10-22 15:30:45 - django.server - GET /api/users
INFO - 2025-10-22 15:30:45 - django.server - GET /api/users 200 (45.23ms)
```

### Body Logging (Debugging)

```python
# Log request/response bodies (use with caution)
logging_config = LoggingConfig(
    request_log_fields={"method", "path", "body"},
    response_log_fields={"status_code", "body"},
    log_request_body=True,
    log_response_body=True,
    max_body_log_size=2048,  # Limit body size
)
```

**Warning:** Body logging can expose sensitive data and increase log volume. Only enable in development or for specific debugging scenarios.

## Security Features

### Obfuscating Headers

Django-Bolt automatically obfuscates sensitive headers to prevent credential leakage in logs:

```python
logging_config = LoggingConfig(
    obfuscate_headers={
        "authorization",     # JWT tokens, Basic auth
        "cookie",            # Session cookies
        "x-api-key",         # API keys
        "x-auth-token",      # Custom auth tokens
    },
)
```

**Example:**
```python
# Request headers
{
    "content-type": "application/json",
    "authorization": "Bearer eyJ..."  # Sensitive!
}

# Logged as
{
    "content-type": "application/json",
    "authorization": "***"  # Obfuscated
}
```

### Obfuscating Cookies

Similarly, sensitive cookies are obfuscated:

```python
logging_config = LoggingConfig(
    obfuscate_cookies={
        "sessionid",   # Django session ID
        "csrftoken",   # CSRF token
    },
)
```

**Best Practice:** Add any custom authentication cookies to `obfuscate_cookies` to prevent session hijacking via log access.

## Performance Features

### Sample Rate

For high-traffic applications, you can sample successful responses (2xx/3xx) to reduce log volume:

```python
logging_config = LoggingConfig(
    sample_rate=0.05,  # Log only 5% of successful responses
)
```

**Behavior:**
- **Successful responses (2xx/3xx)**: Only logged with probability `sample_rate`
- **Error responses (4xx/5xx)**: **Always logged** (not subject to sampling)
- **Implementation**: Uses `random.random()` for probabilistic sampling

**Use Cases:**
- Production environments with 50k+ RPS
- Health check endpoints that generate excessive logs
- Observability systems that aggregate metrics separately

### Minimum Duration (Slow-Only Logging)

Log only slow requests that exceed a threshold:

```python
logging_config = LoggingConfig(
    min_duration_ms=250,  # Only log requests slower than 250ms
)
```

**Behavior:**
- **Successful responses (2xx/3xx)**: Only logged if `duration >= min_duration_ms`
- **Error responses (4xx/5xx)**: **Always logged** (not subject to threshold)
- **Default in production**: `min_duration_ms=250` when `DEBUG=False`

**Use Cases:**
- Identifying slow database queries
- Detecting N+1 query problems
- Monitoring API performance degradation

**Example Output:**
```
# Fast request (50ms) - not logged
GET /api/health 200 (50ms)

# Slow request (300ms) - logged
INFO - 2025-10-22 15:30:45 - django.server - GET /api/users 200 (300.45ms)
```

## Skip Paths and Status Codes

### Skip Paths

Exclude noisy endpoints from logging:

```python
logging_config = LoggingConfig(
    skip_paths={
        "/health",     # Health check
        "/ready",      # Readiness probe
        "/metrics",    # Prometheus metrics
        "/favicon.ico",
    },
)
```

**Use Case:** Health check endpoints that are polled every second can generate millions of log entries per day.

### Skip Status Codes

Exclude specific status codes:

```python
logging_config = LoggingConfig(
    skip_status_codes={404, 403},  # Don't log not found or forbidden
)
```

**Use Case:** If your application intentionally returns 404 for certain endpoints (e.g., feature detection), you may want to exclude them from logs.

## Log Levels by Status Code

Django-Bolt automatically assigns log levels based on HTTP status codes:

| Status Code Range | Log Level | Rationale |
|-------------------|-----------|-----------|
| **Requests** | `DEBUG` | Requests are less important than responses |
| **2xx Success** | `INFO` | Normal operation |
| **3xx Redirect** | `INFO` | Normal operation |
| **4xx Client Error** | `WARNING` | Client issue, may require attention |
| **5xx Server Error** | `ERROR` | Server issue, requires immediate attention |

**Implementation:**
```python
# From middleware.py
if status_code >= 500:
    log_level = logging.ERROR
elif status_code >= 400:
    log_level = logging.WARNING
else:
    log_level = logging.INFO
```

**Filtering by Level:**
```python
# In Django settings.py
LOGGING = {
    "loggers": {
        "django_bolt": {
            "level": "INFO",  # Show INFO, WARNING, ERROR (hide DEBUG requests)
        },
    },
}
```

This configuration will:
- **Hide** incoming request logs (DEBUG level)
- **Show** successful responses (INFO level)
- **Show** client errors (WARNING level)
- **Show** server errors (ERROR level)

## Integration with Django's Logging System

### Automatic Configuration

If your Django project **does not** define `LOGGING`, Django-Bolt automatically configures logging:

```python
# From config.py - setup_django_logging()
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

# Create queue and listener
queue = Queue(-1)
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter(
        fmt="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)
listener = QueueListener(queue, console_handler)
listener.start()

# Configure loggers
queue_handler = QueueHandler(queue)
for logger_name in ("django", "django.server", "django_bolt"):
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()
    logger.addHandler(queue_handler)
    logger.setLevel("DEBUG" if DEBUG else "WARNING")
```

### Manual Configuration

If you prefer explicit control, define `LOGGING` in your Django settings:

```python
# settings.py
import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

LOG_QUEUE = Queue(-1)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(levelname)s - %(asctime)s - %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "queue": {
            "class": "logging.handlers.QueueHandler",
            "queue": LOG_QUEUE,
            "level": "DEBUG",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["queue"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.server": {
            "handlers": ["queue"],
            "level": "ERROR",
            "propagate": False,
        },
        "django_bolt": {
            "handlers": ["queue"],
            "level": "INFO",  # Show INFO and above
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["queue"],
        "level": "WARNING",
    },
}

# Start the queue listener
listener = QueueListener(
    LOG_QUEUE,
    logging.StreamHandler(),
)
listener.start()

# Remember to stop the listener on shutdown
import atexit
atexit.register(listener.stop)
```

**Important:** When you define `LOGGING`, Django-Bolt **defers entirely** to your configuration. You must manually set up the queue listener if you want non-blocking logging.

## Production vs Development Defaults

Django-Bolt adapts its logging behavior based on Django's `DEBUG` setting:

### Development (`DEBUG=True`)

```python
# Automatic configuration
LoggingConfig(
    log_level="DEBUG",        # Log everything
    sample_rate=None,         # No sampling
    min_duration_ms=None,     # Log all requests
)

# Logger level
logger.setLevel("DEBUG")
```

**Result:**
- All requests logged at DEBUG level
- All responses logged (2xx=INFO, 4xx=WARNING, 5xx=ERROR)
- Full visibility into application behavior

### Production (`DEBUG=False`)

```python
# Automatic configuration
LoggingConfig(
    log_level="WARNING",      # Only warnings and errors
    sample_rate=None,         # No sampling (but see min_duration_ms)
    min_duration_ms=250,      # Only log slow requests (≥250ms)
)

# Logger level
logger.setLevel("WARNING")
```

**Result:**
- Requests not logged (DEBUG level, but logger is WARNING)
- Successful responses only logged if slow (≥250ms)
- Client errors (4xx) always logged at WARNING
- Server errors (5xx) always logged at ERROR

**Override via Django Settings:**

```python
# settings.py
DJANGO_BOLT_LOG_LEVEL = "INFO"      # Override base log level
DJANGO_BOLT_LOG_SLOW_MS = 100       # Log requests slower than 100ms
DJANGO_BOLT_LOG_SAMPLE = 0.10       # Sample 10% of successful responses
```

These settings are read by `get_default_logging_config()` and override the defaults.

## Configuration Examples

### Example 1: Minimal Production Logging

Only log errors and slow requests:

```python
from django_bolt import BoltAPI
from django_bolt.logging import LoggingConfig

logging_config = LoggingConfig(
    request_log_fields={"method", "path"},
    response_log_fields={"status_code", "duration"},
    skip_paths={"/health", "/ready"},
    min_duration_ms=500,  # Only log very slow requests
)

api = BoltAPI(logging_config=logging_config)
```

**Django settings:**
```python
# settings.py
LOGGING = {
    "loggers": {
        "django_bolt": {"level": "WARNING"},  # Only warnings and errors
    },
}
```

### Example 2: High-Traffic Application with Sampling

Sample successful responses to reduce log volume:

```python
from django_bolt.logging import LoggingConfig

logging_config = LoggingConfig(
    request_log_fields={"method", "path"},
    response_log_fields={"status_code", "duration"},
    sample_rate=0.01,         # Sample 1% of successful responses
    min_duration_ms=250,      # Always log slow requests
    skip_paths={"/health"},
)

api = BoltAPI(logging_config=logging_config)
```

**Result:**
- 99% of fast successful responses are not logged
- 100% of slow successful responses (≥250ms) are logged
- 100% of error responses (4xx/5xx) are logged
- Reduces log volume by ~99% for high-traffic endpoints

### Example 3: Verbose Development Logging

Log everything with full details:

```python
from django_bolt.logging import LoggingConfig

logging_config = LoggingConfig(
    request_log_fields={
        "method", "path", "query", "headers",
        "client_ip", "user_agent"
    },
    response_log_fields={
        "status_code", "duration", "size"
    },
    log_request_body=True,
    log_response_body=True,
    max_body_log_size=4096,
    skip_paths=set(),  # Don't skip anything
)

api = BoltAPI(logging_config=logging_config)
```

**Django settings:**
```python
# settings.py
LOGGING = {
    "loggers": {
        "django_bolt": {"level": "DEBUG"},  # Show everything
    },
}
```

### Example 4: Security-Focused Logging

Obfuscate all sensitive data:

```python
from django_bolt.logging import LoggingConfig

logging_config = LoggingConfig(
    request_log_fields={"method", "path", "headers"},
    response_log_fields={"status_code", "duration"},
    obfuscate_headers={
        "authorization",
        "cookie",
        "x-api-key",
        "x-auth-token",
        "x-custom-secret",  # Custom headers
    },
    obfuscate_cookies={
        "sessionid",
        "csrftoken",
        "auth_token",  # Custom cookies
    },
    log_request_body=False,   # Never log request bodies
    log_response_body=False,  # Never log response bodies
)

api = BoltAPI(logging_config=logging_config)
```

### Example 5: Custom Logger Name

Use a custom logger for separation:

```python
from django_bolt.logging import LoggingConfig

logging_config = LoggingConfig(
    logger_name="myapp.api",  # Custom logger
)

api = BoltAPI(logging_config=logging_config)
```

**Django settings:**
```python
# settings.py
LOGGING = {
    "loggers": {
        "myapp.api": {
            "level": "INFO",
            "handlers": ["console", "file"],  # Multiple handlers
        },
    },
}
```

### Example 6: Custom Exception Handler

Implement custom exception logging:

```python
from django_bolt.logging import LoggingConfig

def custom_exception_handler(logger, request, exc, exc_info):
    # Custom logic (e.g., send to Sentry, log to file)
    logger.error(
        f"API Exception: {type(exc).__name__}",
        extra={
            "method": request.get("method"),
            "path": request.get("path"),
            "exception": str(exc),
            "user_id": request.get("auth", {}).get("user_id"),
        },
        exc_info=exc_info,
    )

logging_config = LoggingConfig(
    exception_logging_handler=custom_exception_handler,
)

api = BoltAPI(logging_config=logging_config)
```

## Best Practices

### 1. Use Appropriate Log Levels

Set logger levels based on environment:

```python
# Development
LOGGING = {"loggers": {"django_bolt": {"level": "DEBUG"}}}

# Staging
LOGGING = {"loggers": {"django_bolt": {"level": "INFO"}}}

# Production
LOGGING = {"loggers": {"django_bolt": {"level": "WARNING"}}}
```

### 2. Skip Health Check Endpoints

Always exclude health check endpoints to reduce noise:

```python
logging_config = LoggingConfig(
    skip_paths={"/health", "/ready", "/metrics", "/favicon.ico"},
)
```

### 3. Use Slow-Only Logging in Production

Combine `min_duration_ms` with `WARNING` level for production:

```python
# Only log slow requests and errors
logging_config = LoggingConfig(
    min_duration_ms=250,  # 250ms threshold
)

LOGGING = {
    "loggers": {
        "django_bolt": {"level": "WARNING"},  # Errors only
    },
}
```

**Result:**
- Fast successful requests: not logged
- Slow successful requests: logged at INFO (but hidden by WARNING level)
- Client errors (4xx): logged at WARNING
- Server errors (5xx): logged at ERROR

To also see slow requests, set level to `INFO`:

```python
LOGGING = {
    "loggers": {
        "django_bolt": {"level": "INFO"},  # Show slow requests + errors
    },
}
```

### 4. Combine Sampling and Slow-Only Logging

For extreme high-traffic scenarios:

```python
logging_config = LoggingConfig(
    sample_rate=0.05,      # Sample 5% of responses
    min_duration_ms=100,   # Only sample if slower than 100ms
)
```

**Result:**
- Fast requests (<100ms): not logged
- Slow requests (≥100ms): 5% sampled
- Errors (4xx/5xx): always logged (not sampled)

### 5. Obfuscate All Sensitive Data

Always obfuscate authentication data:

```python
logging_config = LoggingConfig(
    obfuscate_headers={
        "authorization", "cookie", "x-api-key",
        # Add your custom headers
    },
    obfuscate_cookies={
        "sessionid", "csrftoken",
        # Add your custom cookies
    },
    log_request_body=False,  # Avoid logging sensitive payloads
)
```

### 6. Use Queue-Based Logging

Always use queue-based logging in production for non-blocking I/O:

```python
# Automatic with Django-Bolt if no LOGGING defined
# Or manually configure:
LOGGING = {
    "handlers": {
        "queue": {
            "class": "logging.handlers.QueueHandler",
            "queue": Queue(-1),
        },
    },
}
```

### 7. Monitor Log Volume

Use sampling to control log volume in production:

```python
# Before
# 100k requests/day × 2 log lines/request = 200k log lines/day

# After (5% sampling)
logging_config = LoggingConfig(sample_rate=0.05)
# 100k requests/day × 5% × 2 log lines/request = 10k log lines/day
# (Plus 100% of errors)
```

### 8. Test Logging Configuration

Verify logging behavior in tests:

```python
import logging

def test_logging_config():
    from django_bolt.logging import LoggingConfig

    config = LoggingConfig(
        skip_paths={"/health"},
        min_duration_ms=100,
    )

    # Test skip path
    assert not config.should_log_request("/health")
    assert config.should_log_request("/api/users")

    # Test logger
    logger = config.get_logger()
    assert logger.name == "django.server"
```

## Enabling Observability

To increase verbosity without changing code, use Django settings:

```python
# settings.py

# Override default log level
DJANGO_BOLT_LOG_LEVEL = "INFO"

# Adjust slow-only threshold (milliseconds)
DJANGO_BOLT_LOG_SLOW_MS = 250

# Adjust sampling rate (0.0-1.0)
DJANGO_BOLT_LOG_SAMPLE = 0.02  # 2%

# These are read by get_default_logging_config()
```

Or use environment variables:

```bash
# .env or environment
export DJANGO_BOLT_LOG_LEVEL=INFO
export DJANGO_BOLT_LOG_SLOW_MS=250
export DJANGO_BOLT_LOG_SAMPLE=0.02
```

Then read them in settings:

```python
# settings.py
import os

DJANGO_BOLT_LOG_LEVEL = os.getenv("DJANGO_BOLT_LOG_LEVEL", "WARNING")
DJANGO_BOLT_LOG_SLOW_MS = int(os.getenv("DJANGO_BOLT_LOG_SLOW_MS", "250"))
DJANGO_BOLT_LOG_SAMPLE = float(os.getenv("DJANGO_BOLT_LOG_SAMPLE", "0.0"))
```

## Troubleshooting

### No Logs When `DEBUG=False`

**Problem:** Logs are not appearing in production.

**Solution:** Check your Django `LOGGING` level:

```python
# settings.py
LOGGING = {
    "loggers": {
        "django_bolt": {
            "level": "ERROR",  # Only errors
            # Change to "INFO" to see successful responses
            # Change to "WARNING" to see client errors + server errors
        },
    },
}
```

The middleware respects the logger level. If the logger level is `CRITICAL`, nothing will log.

### Duplicate Logs

**Problem:** Seeing multiple log entries for the same request.

**Solution:** Check for duplicate handlers or propagation:

```python
LOGGING = {
    "loggers": {
        "django_bolt": {
            "handlers": ["queue"],  # Only one handler
            "propagate": False,      # Don't propagate to root
        },
    },
}
```

### Logs Not Showing Request Bodies

**Problem:** Request bodies are not logged even with `"body"` in `request_log_fields`.

**Solution:** Enable body logging explicitly:

```python
logging_config = LoggingConfig(
    request_log_fields={"method", "path", "body"},
    log_request_body=True,  # Must be True!
    max_body_log_size=2048,
)
```

**Warning:** Body logging can expose sensitive data (passwords, tokens, personal information). Only enable in development.

### Headers Still Showing Sensitive Data

**Problem:** Authorization headers are not obfuscated.

**Solution:** Ensure header names are lowercase in `obfuscate_headers`:

```python
logging_config = LoggingConfig(
    obfuscate_headers={
        "authorization",  # lowercase!
        "x-api-key",      # lowercase!
    },
)
```

Header comparison is case-insensitive in the middleware (`key.lower() in self.config.obfuscate_headers`).

### Want JSON Logs?

**Problem:** Default logs are text format, but you want structured JSON for log aggregation.

**Solution:** Swap the queue listener's handler for a JSON formatter:

```python
# settings.py
import logging
import json
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "__dict__"):
            log_obj.update({
                k: v for k, v in record.__dict__.items()
                if k not in ("name", "msg", "args", "created", "levelname", "levelno")
            })
        return json.dumps(log_obj)

LOG_QUEUE = Queue(-1)
json_handler = logging.StreamHandler()
json_handler.setFormatter(JSONFormatter())

listener = QueueListener(LOG_QUEUE, json_handler)
listener.start()
```

**Output:**
```json
{"timestamp": "2025-10-22 15:30:45", "level": "INFO", "logger": "django_bolt", "message": "GET /api/users 200 (45.23ms)", "method": "GET", "path": "/api/users", "status_code": 200, "duration_ms": 45.23}
```

### Logs Blocking Request Handling

**Problem:** Logging is slowing down request handling.

**Solution:** Ensure you're using queue-based logging:

```python
# Verify queue handler is being used
logger = logging.getLogger("django_bolt")
print(logger.handlers)
# Should show: [<QueueHandler ...>]
```

If not using queue handler, Django-Bolt's automatic configuration may not have run. Manually configure as shown in "Manual Configuration" section.

### Seeing "Too Many Logs" in Production

**Problem:** Log volume is overwhelming your log aggregation system.

**Solution:** Use sampling and slow-only logging:

```python
logging_config = LoggingConfig(
    sample_rate=0.01,       # Sample 1% of successful responses
    min_duration_ms=500,    # Only log very slow requests
    skip_paths={"/health", "/ready"},
)

# And set logger level to WARNING
LOGGING = {
    "loggers": {
        "django_bolt": {"level": "WARNING"},  # Only errors
    },
}
```

**Result:**
- Fast successful requests: not logged
- Slow successful requests: 1% sampled
- Errors: always logged

## Advanced: Custom Logging Middleware

For advanced use cases, you can subclass `LoggingMiddleware`:

```python
from django_bolt.logging import LoggingMiddleware, LoggingConfig

class CustomLoggingMiddleware(LoggingMiddleware):
    def extract_request_data(self, request):
        # Call parent implementation
        data = super().extract_request_data(request)

        # Add custom fields
        data["tenant_id"] = request.get("tenant_id")
        data["request_id"] = request.get("headers", {}).get("x-request-id")

        return data

    def log_response(self, request, status_code, duration, response_size=None):
        # Add custom logic before logging
        if status_code >= 500:
            # Send alert to monitoring system
            self.send_alert(request, status_code)

        # Call parent implementation
        super().log_response(request, status_code, duration, response_size)

    def send_alert(self, request, status_code):
        # Custom alerting logic
        print(f"ALERT: {status_code} on {request.get('path')}")

# Use custom middleware
config = LoggingConfig()
custom_middleware = CustomLoggingMiddleware(config)
```

## Production Guide

### Recommended Production Configuration

```python
# settings.py

# Django settings
DEBUG = False

# Django-Bolt logging settings
DJANGO_BOLT_LOG_LEVEL = "WARNING"     # Only warnings and errors
DJANGO_BOLT_LOG_SLOW_MS = 500         # Log very slow requests
DJANGO_BOLT_LOG_SAMPLE = 0.05         # Sample 5% of successful responses

# Django logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "django_bolt": {
            "level": "WARNING",  # Only warnings and errors
            "handlers": ["queue"],
            "propagate": False,
        },
    },
}

# LoggingConfig in api.py
from django_bolt.logging import LoggingConfig

logging_config = LoggingConfig(
    request_log_fields={"method", "path"},
    response_log_fields={"status_code", "duration"},
    skip_paths={"/health", "/ready", "/metrics"},
    obfuscate_headers={
        "authorization", "cookie", "x-api-key",
    },
    obfuscate_cookies={
        "sessionid", "csrftoken",
    },
)
```

**Characteristics:**
- **Minimal overhead** - Queue-based, non-blocking
- **Error visibility** - Always logs 4xx/5xx
- **Performance monitoring** - Logs slow requests (≥500ms)
- **Reduced volume** - Sampling + slow-only filtering
- **Secure** - Obfuscates sensitive headers/cookies

### Benchmarking with Logging Disabled

For maximum performance during benchmarks, disable logging entirely:

```python
# settings.py
LOGGING = {
    "loggers": {
        "django_bolt": {"level": "CRITICAL"},  # Effectively disabled
    },
}
```

Or remove the logging middleware:

```python
from django_bolt import BoltAPI

# No logging_config = no logging middleware
api = BoltAPI()
```

**Result:** Zero logging overhead, maximum throughput.

## See Also

- [EXCEPTIONS.md](EXCEPTIONS.md) - Exception handling and error logging
- [MIDDLEWARE.md](MIDDLEWARE.md) - Middleware system and custom middleware
- [SECURITY.md](SECURITY.md) - Security features including authentication
- [Class-Based Views](CLASS_BASED_VIEWS.md) - Class-based API views with logging

---
icon: lucide/settings
---

# Settings Reference

Django-Bolt settings are configured in your Django `settings.py` file.

## CORS settings

### BOLT_CORS_ALLOWED_ORIGINS

List of allowed origins for CORS.

```python
BOLT_CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://app.example.com",
]
```

### BOLT_CORS_ALLOW_ALL_ORIGINS

Allow all origins (development only).

```python
BOLT_CORS_ALLOW_ALL_ORIGINS = True
```

### BOLT_CORS_ALLOW_CREDENTIALS

Allow credentials in CORS requests.

```python
BOLT_CORS_ALLOW_CREDENTIALS = True
```

### BOLT_CORS_ALLOW_METHODS

Allowed HTTP methods for CORS.

```python
BOLT_CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
```

### BOLT_CORS_ALLOW_HEADERS

Allowed headers in CORS requests.

```python
BOLT_CORS_ALLOW_HEADERS = ["Content-Type", "Authorization", "X-Requested-With"]
```

### BOLT_CORS_EXPOSE_HEADERS

Headers exposed to the browser.

```python
BOLT_CORS_EXPOSE_HEADERS = ["X-Total-Count", "X-Page-Count"]
```

### BOLT_CORS_MAX_AGE

Preflight cache duration in seconds.

```python
BOLT_CORS_MAX_AGE = 86400  # 24 hours
```

## File serving settings

### BOLT_ALLOWED_FILE_PATHS

Whitelist of directories for FileResponse.

```python
BOLT_ALLOWED_FILE_PATHS = [
    "/var/app/uploads",
    "/var/app/public",
]
```

When set, `FileResponse` only serves files within these directories.

## Authentication settings

Django-Bolt uses Django's `SECRET_KEY` for JWT signing by default.

```python
SECRET_KEY = "your-secret-key"
```

Override per-backend:

```python
JWTAuthentication(secret="custom-jwt-secret")
```

## Logging settings

Django-Bolt integrates with Django's logging system.

```python
LOGGING = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django_bolt": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
```

## runbolt command options

The `runbolt` management command accepts these options:

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `0.0.0.0` | Bind address |
| `--port` | `8000` | Bind port |
| `--workers` | `1` | Workers per process |
| `--processes` | `1` | Number of processes |
| `--dev` | off | Enable auto-reload |
| `--no-admin` | off | Disable admin integration |
| `--backlog` | `1024` | Socket listen backlog |
| `--keep-alive` | OS default | HTTP keep-alive timeout |

### Examples

```bash
# Development with auto-reload
python manage.py runbolt --dev

# Production with scaling
python manage.py runbolt --processes 4 --workers 2

# Custom bind address
python manage.py runbolt --host 127.0.0.1 --port 3000
```

## OpenAPI settings

Configure via `OpenAPIConfig` in your api.py:

```python
from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        description="API description",
        enabled=True,
        docs_url="/docs",
        openapi_url="/openapi.json",
        django_auth=False,
    )
)
```

## Compression settings

Configure via `CompressionConfig`:

```python
from django_bolt import BoltAPI, CompressionConfig

api = BoltAPI(
    compression=CompressionConfig(
        backend="brotli",      # "brotli", "gzip", or "zstd"
        minimum_size=1000,     # Minimum size to compress (bytes)
        gzip_fallback=True,    # Fall back to gzip
    )
)
```

## All settings reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `BOLT_CORS_ALLOWED_ORIGINS` | `list[str]` | `[]` | Allowed CORS origins |
| `BOLT_CORS_ALLOW_ALL_ORIGINS` | `bool` | `False` | Allow all origins |
| `BOLT_CORS_ALLOW_CREDENTIALS` | `bool` | `False` | Allow credentials |
| `BOLT_CORS_ALLOW_METHODS` | `list[str]` | All methods | Allowed methods |
| `BOLT_CORS_ALLOW_HEADERS` | `list[str]` | `[]` | Allowed headers |
| `BOLT_CORS_EXPOSE_HEADERS` | `list[str]` | `[]` | Exposed headers |
| `BOLT_CORS_MAX_AGE` | `int` | `600` | Preflight cache (seconds) |
| `BOLT_ALLOWED_FILE_PATHS` | `list[str]` | `None` | File serving whitelist |

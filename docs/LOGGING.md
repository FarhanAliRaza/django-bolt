# Logging in Django-Bolt

## Overview

Django-Bolt ships with a non-blocking logging pipeline inspired by Litestar. When your project does **not** define a custom `LOGGING` setting, `manage.py runbolt` automatically configures a shared `QueueHandler` / `QueueListener` pair so that request logging never blocks the hot path. All log records are enqueued instantly and flushed to stderr by the background listener.

If your project already declares `LOGGING`, Django-Bolt defers entirely to that configuration. You can copy the queue-based setup shown below into your own settings if you want identical behaviour.

## Default Behaviour

- **Queue logging** – Root, `django`, `django.server`, and `django_bolt` loggers are wired to a shared queue-based handler; formatting happens off the request thread.
- **Production defaults** – With `DEBUG=False`, the framework logs successful 2xx/3xx responses only when they are “slow” (default: ≥250 ms). Errors (4xx/5xx) always log at `WARNING` / `ERROR`.
- **Request logging** – `BoltAPI` attaches the logging middleware by default. Each request/response run is guarded by `logger.isEnabledFor(...)`, so if your logger level is `ERROR`, there is effectively zero overhead.

## Integrating with Django `LOGGING`

If you supply `LOGGING` yourself, Django-Bolt leaves it untouched. To reuse the queue setup, add a handler and listener similar to:

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
            "format": "%(levelname)s %(asctime)s %(name)s %(message)s",
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
        "django": {"handlers": ["queue"], "level": "ERROR"},
        "django.server": {"handlers": ["queue"], "level": "ERROR", "propagate": False},
        "django_bolt": {"handlers": ["queue"], "level": "ERROR", "propagate": False},
    },
    "root": {"handlers": ["queue"], "level": "WARNING"},
}

listener = QueueListener(LOG_QUEUE, logging.StreamHandler())
listener.start()
```

Remember to stop the listener on shutdown if you manage it manually (e.g., via `atexit.register(listener.stop)`).

## Tuning Request Logging

`LoggingConfig` controls the behaviour of the middleware:

```python
from django_bolt.logging import LoggingConfig

logging_config = LoggingConfig(
    logger_name="django_bolt",
    response_log_fields={"status_code", "duration"},
    sample_rate=None,            # Only sample 2xx logs if you set a value 0.0–1.0
    min_duration_ms=250,         # Log slow requests (defaults to 250ms when DEBUG=False)
    skip_paths={"/health", "/ready"},
)

api = BoltAPI(logging_config=logging_config)
```

Key fields:

- `sample_rate`: If set (e.g., `0.05`), only that fraction of successful responses are logged.
- `min_duration_ms`: Successful responses faster than the threshold are ignored. Errors are never skipped.
- `skip_paths` / `skip_status_codes`: Exclude noisy endpoints such as health checks.

## Enabling Observability

To increase verbosity without changing code:

```python
# settings.py
DJANGO_BOLT_LOG_LEVEL = "INFO"      # Optional: overrides base level before queue setup
DJANGO_BOLT_LOG_SLOW_MS = 250        # Optional: adjust slow-only threshold
DJANGO_BOLT_LOG_SAMPLE = 0.02        # Optional: sample 2% of successful responses
```

Set these in your settings module (or environment) and they automatically flow into `LoggingConfig`. Lower the logger level in Django `LOGGING` to surface additional records (e.g., `INFO` for request logs, `DEBUG` for request bodies).

## Production Guide

- Keep request logging attached so errors are always recorded, even with `DEBUG=False`.
- Leave your logger levels at `ERROR` during benchmarks for zero overhead; raise to `INFO` only when you need observability.
- Because logs are offloaded to a queue, you can safely enable verbose logging in production without tanking throughput. Combine `sample_rate` and `min_duration_ms` to constrain volume.

## Troubleshooting

- **No logs when `DEBUG=False`** – Ensure your Django `LOGGING` level for `django_bolt` is ≤`ERROR`. The middleware respects the logger level; if it’s set to `CRITICAL`, nothing prints.
- **Want JSON logs?** Swap the queue listener’s handler for a JSON formatter or structlog sink. The queue is transport-agnostic.
- **Seeing duplicate logs?** Remove additional handlers from `django_bolt` or `root` that also propagate to stdout; the queue handler should be the only one attached.

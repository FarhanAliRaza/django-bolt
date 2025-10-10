"""Logging configuration for Django-Bolt.

Integrates with Django's logging configuration and provides structured logging
for HTTP requests, responses, and exceptions.

Adopts Litestar's queue-based logging approach so request logging stays
non-blocking and fully controlled by application logging config.
"""

import sys
import os
import atexit
from queue import Queue
from logging.handlers import QueueHandler, QueueListener
import logging
import logging.config
from abc import ABC, abstractmethod
from typing import Callable, Optional, Set, List, Dict, Any
from dataclasses import dataclass, field


# Global flag to prevent multiple logging reconfigurations
_LOGGING_CONFIGURED = False
_QUEUE_LISTENER: Optional[QueueListener] = None
_QUEUE: Optional[Queue] = None


@dataclass
class LoggingConfig:
    """Configuration for request/response logging.

    Integrates with Django's logging system and uses the configured logger.
    """

    # Logger name - defaults to Django's logger
    logger_name: str = "django.server"

    # Request logging fields
    request_log_fields: Set[str] = field(default_factory=lambda: {
        "method", "path", "status_code"
    })

    # Response logging fields
    response_log_fields: Set[str] = field(default_factory=lambda: {
        "status_code"
    })

    # Headers to obfuscate in logs (for security)
    obfuscate_headers: Set[str] = field(default_factory=lambda: {
        "authorization", "cookie", "x-api-key", "x-auth-token"
    })

    # Cookies to obfuscate in logs
    obfuscate_cookies: Set[str] = field(default_factory=lambda: {
        "sessionid", "csrftoken"
    })

    # Log request body (be careful with sensitive data)
    log_request_body: bool = False

    # Log response body (be careful with large responses)
    log_response_body: bool = False

    # Maximum body size to log (in bytes)
    max_body_log_size: int = 1024

    # Note: Individual log levels are determined automatically:
    # - Requests: DEBUG
    # - Successful responses (2xx/3xx): INFO
    # - Client errors (4xx): WARNING
    # - Server errors (5xx): ERROR
    #
    # To control which logs appear, configure Django's LOGGING in settings.py:
    # LOGGING = {
    #     "loggers": {
    #         "django_bolt": {"level": "INFO"},  # Show INFO and above
    #     }
    # }

    # Deprecated: log_level is no longer used (kept for backward compatibility)
    log_level: str = "INFO"

    # Log level for exceptions (used by log_exception method)
    error_log_level: str = "ERROR"

    # Custom exception logging handler
    exception_logging_handler: Optional[Callable] = None

    # Skip logging for specific paths (e.g., health checks)
    skip_paths: Set[str] = field(default_factory=lambda: {
        "/health", "/ready", "/metrics"
    })

    # Skip logging for specific status codes
    skip_status_codes: Set[int] = field(default_factory=set)

    # Optional sampling of logs (0.0-1.0). When set, successful responses (2xx/3xx)
    # will only be logged with this probability. Errors (4xx/5xx) are not sampled.
    sample_rate: Optional[float] = None

    # Only log successful responses slower than this threshold (milliseconds).
    # Errors (4xx/5xx) are not subject to the slow-only threshold.
    min_duration_ms: Optional[int] = None

    def get_logger(self) -> logging.Logger:
        """Get the configured logger.

        Uses Django's logging configuration if available.
        """
        return logging.getLogger(self.logger_name)

    def should_log_request(self, path: str, status_code: Optional[int] = None) -> bool:
        """Check if a request should be logged.

        Args:
            path: Request path
            status_code: Response status code (optional)

        Returns:
            True if request should be logged
        """
        if path in self.skip_paths:
            return False

        if status_code and status_code in self.skip_status_codes:
            return False

        return True


@dataclass
class RequestLogFields:
    """Available fields for request logging."""

    # HTTP method (GET, POST, etc.)
    method: str = "method"

    # Request path
    path: str = "path"

    # Query string
    query: str = "query"

    # Request headers
    headers: str = "headers"

    # Request body
    body: str = "body"

    # Client IP address
    client_ip: str = "client_ip"

    # User agent
    user_agent: str = "user_agent"

    # Request ID (if available)
    request_id: str = "request_id"


@dataclass
class ResponseLogFields:
    """Available fields for response logging."""

    # HTTP status code
    status_code: str = "status_code"

    # Response headers
    headers: str = "headers"

    # Response body
    body: str = "body"

    # Response time (in seconds)
    duration: str = "duration"

    # Response size (in bytes)
    size: str = "size"


def get_default_logging_config() -> LoggingConfig:
    """Get default logging configuration.

    Uses Django's DEBUG setting to determine log level.
    """
    log_level = "INFO"
    debug = False
    settings_level = None
    settings_sample = None
    settings_slow_ms = None
    try:
        from django.conf import settings
        if settings.configured:
            debug = settings.DEBUG
            # Optional overrides from Django settings
            settings_level = getattr(settings, "DJANGO_BOLT_LOG_LEVEL", None)
            settings_sample = getattr(settings, "DJANGO_BOLT_LOG_SAMPLE", None)
            settings_slow_ms = getattr(settings, "DJANGO_BOLT_LOG_SLOW_MS", None)
            # Default base level by DEBUG
            log_level = "DEBUG" if debug else "WARNING"
    except (ImportError, AttributeError, Exception):
        # Django not available or not configured, use default
        pass

    # Choose log level: Django settings override > default determined by DEBUG
    if settings_level:
        log_level = str(settings_level).upper()

    sample_rate: Optional[float] = None
    if settings_sample is not None:
        try:
            sr = float(settings_sample)
            if 0.0 <= sr <= 1.0:
                sample_rate = sr
        except Exception:
            sample_rate = None

    min_duration_ms: Optional[int] = None
    if settings_slow_ms is not None:
        try:
            min_duration_ms = max(0, int(settings_slow_ms))
        except Exception:
            min_duration_ms = None
    else:
        # Default to slow-only logging in production
        if not debug:
            min_duration_ms = 250

    return LoggingConfig(
        log_level=log_level,
        sample_rate=sample_rate,
        min_duration_ms=min_duration_ms,
    )


def _ensure_queue_logging(base_level: str) -> QueueHandler:
    """Create or reuse a queue-based logging setup.

    Returns a QueueHandler that enqueues log records. A singleton QueueListener
    forwards records to a console StreamHandler in the background. Inspired by
    Litestar's standard logging implementation.
    """

    global _QUEUE_LISTENER, _QUEUE  # noqa: PLW0603

    if _QUEUE is None:
        _QUEUE = Queue(-1)

    queue_handler = QueueHandler(_QUEUE)
    queue_handler.setLevel(logging.DEBUG)

    if _QUEUE_LISTENER is None:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(base_level)
        console_handler.setFormatter(
            logging.Formatter(
                fmt="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

        listener = QueueListener(_QUEUE, console_handler)
        listener.start()
        atexit.register(listener.stop)
        _QUEUE_LISTENER = listener

    return queue_handler


def setup_django_logging(force: bool = False) -> None:
    """Setup Django logging configuration with console output.

    Configures Django's logging system to output to console/terminal.
    Based on Litestar's logging configuration pattern.

    This should be called once during application startup. Subsequent calls
    are no-ops unless force=True.

    Args:
        force: If True, reconfigure even if already configured
    """
    global _LOGGING_CONFIGURED, _QUEUE_LISTENER, _QUEUE

    # Guard against multiple reconfigurations (Litestar pattern)
    if _LOGGING_CONFIGURED and not force:
        return

    if force and _QUEUE_LISTENER is not None:
        try:
            _QUEUE_LISTENER.stop()
        except Exception:
            pass
        _QUEUE_LISTENER = None

    try:
        from django.conf import settings

        # Check if Django is configured
        if not settings.configured:
            return

        # Check if LOGGING is explicitly configured in Django settings
        # Note: Django's default settings may have LOGGING, but we want to check
        # if the user explicitly set it in their settings.py
        has_explicit_logging = False
        try:
            # Try to import the actual settings module to check if LOGGING is defined
            import importlib
            settings_module = importlib.import_module(settings.SETTINGS_MODULE)
            has_explicit_logging = hasattr(settings_module, 'LOGGING')
        except (AttributeError, ImportError):
            # Fall back to checking settings object
            has_explicit_logging = hasattr(settings, 'LOGGING') and settings.LOGGING

        if has_explicit_logging:
            # User has explicitly configured logging, respect it
            _LOGGING_CONFIGURED = True
            return

        # Get appropriate handlers for Python version
        base_level = "DEBUG" if getattr(settings, "DEBUG", False) else "WARNING"

        queue_handler = _ensure_queue_logging(base_level)

        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.addHandler(queue_handler)
        root_logger.setLevel(base_level)

        for logger_name in ("django", "django.server", "django_bolt"):
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()
            logger.addHandler(queue_handler)
            # App-level logging config remains source of truth; use base_level if unset
            current_level = logger.level or logging.getLevelName(base_level)
            logger.setLevel(current_level)
            logger.propagate = logger_name == "django"

        _LOGGING_CONFIGURED = True

    except (ImportError, AttributeError, Exception) as e:
        # If Django not available or configuration fails, use basic config
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s - %(asctime)s - %(name)s - %(message)s',
        )
        _LOGGING_CONFIGURED = True

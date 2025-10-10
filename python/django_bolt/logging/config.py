"""Logging configuration for Django-Bolt.

Integrates with Django's logging configuration and provides structured logging
for HTTP requests, responses, and exceptions.

Based on Litestar's logging configuration patterns.
"""

import sys
import logging
import logging.config
from abc import ABC, abstractmethod
from typing import Callable, Optional, Set, List, Dict, Any
from dataclasses import dataclass, field


# Global flag to prevent multiple logging reconfigurations
_LOGGING_CONFIGURED = False


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
    try:
        from django.conf import settings
        if settings.configured:
            log_level = "DEBUG" if settings.DEBUG else "INFO"
    except (ImportError, AttributeError, Exception):
        # Django not available or not configured, use default
        pass

    return LoggingConfig(log_level=log_level)


def get_default_handlers() -> Dict[str, Dict[str, Any]]:
    """Get default logging handlers.

    Returns StreamHandler for direct console output.
    Based on Litestar's default_handlers pattern.

    Note: QueueHandler support for non-blocking logging will be added
    in a future version with proper QueueListener lifecycle management.
    """
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "stream": "ext://sys.stderr",
        }
    }

    return handlers


def setup_django_logging(force: bool = False) -> None:
    """Setup Django logging configuration with console output.

    Configures Django's logging system to output to console/terminal.
    Based on Litestar's logging configuration pattern.

    This should be called once during application startup. Subsequent calls
    are no-ops unless force=True.

    Args:
        force: If True, reconfigure even if already configured
    """
    global _LOGGING_CONFIGURED

    # Guard against multiple reconfigurations (Litestar pattern)
    if _LOGGING_CONFIGURED and not force:
        return

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
        handlers = get_default_handlers()

        # Configure Django logging with console output
        # Based on Litestar's default_handlers pattern
        #
        # Note: Logger levels are set to DEBUG to allow all messages through.
        # The actual log level filtering happens in the middleware via LoggingConfig.log_level
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(levelname)s - %(asctime)s - %(name)s - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S',
                },
            },
            'handlers': handlers,
            'loggers': {
                'django.server': {
                    'handlers': ['console'],
                    'level': 'DEBUG',  # Set to DEBUG to allow middleware to control filtering
                    'propagate': False,
                },
                'django_bolt': {
                    'handlers': ['console'],
                    'level': 'DEBUG',  # Set to DEBUG to allow middleware to control filtering
                    'propagate': False,
                },
            },
            'root': {
                'handlers': ['console'],
                'level': 'DEBUG',  # Set to DEBUG to allow middleware to control filtering
            },
        }

        # Apply logging configuration
        logging.config.dictConfig(logging_config)
        _LOGGING_CONFIGURED = True

    except (ImportError, AttributeError, Exception) as e:
        # If Django not available or configuration fails, use basic config
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s - %(asctime)s - %(name)s - %(message)s',
        )
        _LOGGING_CONFIGURED = True

"""Tests for Django-Bolt logging system."""

import pytest
import logging
from django_bolt.logging import LoggingConfig, LoggingMiddleware, create_logging_middleware


class TestLoggingConfig:
    """Test logging configuration."""

    def test_default_config(self):
        """Test default logging configuration."""
        config = LoggingConfig()
        assert config.logger_name == "django.server"
        assert "method" in config.request_log_fields
        assert "path" in config.request_log_fields
        assert "status_code" in config.response_log_fields

    def test_custom_config(self):
        """Test custom logging configuration."""
        config = LoggingConfig(
            logger_name="custom.logger",
            log_level="DEBUG",
            request_log_fields={"method", "path", "body"},
        )
        assert config.logger_name == "custom.logger"
        assert config.log_level == "DEBUG"
        assert "body" in config.request_log_fields

    def test_obfuscation_config(self):
        """Test header/cookie obfuscation configuration."""
        config = LoggingConfig(
            obfuscate_headers={"authorization", "x-api-key"},
            obfuscate_cookies={"session", "token"},
        )
        assert "authorization" in config.obfuscate_headers
        assert "session" in config.obfuscate_cookies

    def test_skip_paths_config(self):
        """Test skip paths configuration."""
        config = LoggingConfig(
            skip_paths={"/health", "/metrics", "/admin"}
        )
        assert "/health" in config.skip_paths
        assert "/metrics" in config.skip_paths

    def test_should_log_request(self):
        """Test should_log_request logic."""
        config = LoggingConfig(
            skip_paths={"/health"},
            skip_status_codes={204, 304}
        )

        # Should log normal requests
        assert config.should_log_request("/api/users")
        assert config.should_log_request("/api/users", 200)

        # Should skip health checks
        assert not config.should_log_request("/health")

        # Should skip configured status codes
        assert not config.should_log_request("/api/users", 204)
        assert not config.should_log_request("/api/users", 304)

    def test_get_logger(self):
        """Test logger retrieval."""
        config = LoggingConfig(logger_name="test.logger")
        logger = config.get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.logger"


class TestLoggingMiddleware:
    """Test logging middleware."""

    def test_middleware_initialization(self):
        """Test middleware initialization."""
        config = LoggingConfig()
        middleware = LoggingMiddleware(config)
        assert middleware.config == config
        assert middleware.logger is not None

    def test_middleware_default_config(self):
        """Test middleware with default configuration."""
        middleware = LoggingMiddleware()
        assert middleware.config is not None
        assert middleware.logger is not None

    def test_obfuscate_headers(self):
        """Test header obfuscation."""
        config = LoggingConfig(
            obfuscate_headers={"authorization", "x-api-key"}
        )
        middleware = LoggingMiddleware(config)

        headers = {
            "content-type": "application/json",
            "authorization": "Bearer secret-token",
            "x-api-key": "my-secret-key",
            "user-agent": "test-agent",
        }

        obfuscated = middleware.obfuscate_headers(headers)
        assert obfuscated["content-type"] == "application/json"
        assert obfuscated["authorization"] == "***"
        assert obfuscated["x-api-key"] == "***"
        assert obfuscated["user-agent"] == "test-agent"

    def test_obfuscate_cookies(self):
        """Test cookie obfuscation."""
        config = LoggingConfig(
            obfuscate_cookies={"sessionid", "csrftoken"}
        )
        middleware = LoggingMiddleware(config)

        cookies = {
            "sessionid": "abc123xyz",
            "csrftoken": "token456",
            "preferences": "dark-mode",
        }

        obfuscated = middleware.obfuscate_cookies(cookies)
        assert obfuscated["sessionid"] == "***"
        assert obfuscated["csrftoken"] == "***"
        assert obfuscated["preferences"] == "dark-mode"

    def test_extract_request_data(self):
        """Test request data extraction."""
        config = LoggingConfig(
            request_log_fields={"method", "path", "query", "headers"}
        )
        middleware = LoggingMiddleware(config)

        request = {
            "method": "POST",
            "path": "/api/users",
            "query_params": {"page": "1", "limit": "10"},
            "headers": {
                "content-type": "application/json",
                "authorization": "Bearer token",
            }
        }

        data = middleware.extract_request_data(request)
        assert data["method"] == "POST"
        assert data["path"] == "/api/users"
        assert data["query"] == {"page": "1", "limit": "10"}
        assert "headers" in data
        # Authorization should be obfuscated
        assert data["headers"]["authorization"] == "***"

    def test_extract_request_data_with_body(self):
        """Test request data extraction with body."""
        config = LoggingConfig(
            request_log_fields={"method", "path", "body"},
            log_request_body=True,
            max_body_log_size=100,
        )
        middleware = LoggingMiddleware(config)

        request = {
            "method": "POST",
            "path": "/api/users",
            "body": b'{"name": "test", "email": "test@example.com"}',
        }

        data = middleware.extract_request_data(request)
        assert "body" in data
        assert "test@example.com" in data["body"]

    def test_extract_request_data_body_too_large(self):
        """Test request body not logged when too large."""
        config = LoggingConfig(
            request_log_fields={"method", "path", "body"},
            log_request_body=True,
            max_body_log_size=10,  # Very small limit
        )
        middleware = LoggingMiddleware(config)

        request = {
            "method": "POST",
            "path": "/api/users",
            "body": b'{"name": "test", "email": "test@example.com"}',  # >10 bytes
        }

        data = middleware.extract_request_data(request)
        # Body should not be included because it's too large
        assert "body" not in data

    def test_extract_client_ip(self):
        """Test client IP extraction."""
        config = LoggingConfig(
            request_log_fields={"method", "path", "client_ip"}
        )
        middleware = LoggingMiddleware(config)

        # Test X-Forwarded-For header
        request = {
            "method": "GET",
            "path": "/api/users",
            "headers": {"x-forwarded-for": "192.168.1.1, 10.0.0.1"},
        }
        data = middleware.extract_request_data(request)
        assert data["client_ip"] == "192.168.1.1"

        # Test X-Real-IP header
        request = {
            "method": "GET",
            "path": "/api/users",
            "headers": {"x-real-ip": "192.168.1.2"},
        }
        data = middleware.extract_request_data(request)
        assert data["client_ip"] == "192.168.1.2"

    def test_log_request(self):
        """Test request logging doesn't raise errors."""
        config = LoggingConfig(
            request_log_fields={"method", "path"},
            log_level="INFO",
        )
        middleware = LoggingMiddleware(config)

        request = {
            "method": "GET",
            "path": "/api/users",
        }

        # Just ensure it doesn't raise
        middleware.log_request(request)

    def test_log_request_skipped(self, caplog):
        """Test request logging skipped for health checks."""
        config = LoggingConfig(
            request_log_fields={"method", "path"},
            skip_paths={"/health"},
        )
        middleware = LoggingMiddleware(config)

        request = {
            "method": "GET",
            "path": "/health",
        }

        with caplog.at_level(logging.INFO, logger=config.logger_name):
            middleware.log_request(request)

        # Should not log health checks
        assert len(caplog.records) == 0

    def test_log_response(self):
        """Test response logging doesn't raise errors."""
        config = LoggingConfig(
            request_log_fields={"method", "path"},
            response_log_fields={"status_code", "duration"},
            log_level="INFO",
        )
        middleware = LoggingMiddleware(config)

        request = {
            "method": "POST",
            "path": "/api/users",
        }

        # Just ensure it doesn't raise
        middleware.log_response(request, 201, 0.123)

    def test_log_response_error_level(self):
        """Test response logging works for 5xx."""
        config = LoggingConfig()
        middleware = LoggingMiddleware(config)

        request = {
            "method": "GET",
            "path": "/api/error",
        }

        # Just ensure it doesn't raise
        middleware.log_response(request, 500, 0.1)

    def test_log_response_warning_level(self):
        """Test response logging works for 4xx."""
        config = LoggingConfig()
        middleware = LoggingMiddleware(config)

        request = {
            "method": "GET",
            "path": "/api/notfound",
        }

        # Just ensure it doesn't raise
        middleware.log_response(request, 404, 0.05)

    def test_log_exception(self):
        """Test exception logging doesn't raise errors."""
        config = LoggingConfig()
        middleware = LoggingMiddleware(config)

        request = {
            "method": "GET",
            "path": "/api/error",
        }

        exc = ValueError("Something went wrong")

        # Just ensure it doesn't raise
        middleware.log_exception(request, exc, exc_info=False)


class TestLoggingHelpers:
    """Test logging helper functions."""

    def test_create_logging_middleware(self):
        """Test create_logging_middleware helper."""
        middleware = create_logging_middleware(
            logger_name="test.logger",
            log_level="DEBUG",
        )
        assert isinstance(middleware, LoggingMiddleware)
        assert middleware.config.logger_name == "test.logger"
        assert middleware.config.log_level == "DEBUG"

    def test_create_logging_middleware_defaults(self):
        """Test create_logging_middleware with defaults."""
        middleware = create_logging_middleware()
        assert isinstance(middleware, LoggingMiddleware)
        assert middleware.config is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

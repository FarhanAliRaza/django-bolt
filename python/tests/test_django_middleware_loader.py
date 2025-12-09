"""
Tests for Django middleware loader.

Tests verify the middleware loader API works correctly. Full HTTP cycle tests
are limited because TestClient doesn't currently execute Python middleware
(middleware runs in production server).
"""
from __future__ import annotations

import pytest

from django_bolt import BoltAPI
from django_bolt.middleware import DjangoMiddlewareStack, TimingMiddleware
from django_bolt.middleware.django_loader import (
    DEFAULT_EXCLUDED_MIDDLEWARE,
    get_django_middleware_setting,
    load_django_middleware,
)
from django_bolt.testing import TestClient

# =============================================================================
# Test Default Exclusions
# =============================================================================


class TestDefaultExclusions:
    """Tests for default middleware exclusions (now empty by default)."""

    def test_no_default_exclusions(self):
        """Test that there are no default exclusions - all middleware loaded."""
        # We now load ALL middleware from settings.MIDDLEWARE by default
        # Users can exclude specific middleware if needed via the exclude config
        assert set() == DEFAULT_EXCLUDED_MIDDLEWARE

    def test_csrf_not_excluded_by_default(self):
        """Test that CSRF middleware is NOT excluded by default."""
        assert "django.middleware.csrf.CsrfViewMiddleware" not in DEFAULT_EXCLUDED_MIDDLEWARE

    def test_clickjacking_not_excluded_by_default(self):
        """Test that clickjacking middleware is NOT excluded by default."""
        assert "django.middleware.clickjacking.XFrameOptionsMiddleware" not in DEFAULT_EXCLUDED_MIDDLEWARE

    def test_messages_not_excluded_by_default(self):
        """Test that messages middleware is NOT excluded by default."""
        assert "django.contrib.messages.middleware.MessageMiddleware" not in DEFAULT_EXCLUDED_MIDDLEWARE


# =============================================================================
# Test load_django_middleware
# =============================================================================


class TestLoadDjangoMiddleware:
    """Tests for load_django_middleware function."""

    def test_returns_empty_list_when_false(self):
        """Test that False returns empty list."""
        result = load_django_middleware(False)
        assert result == []

    def test_returns_empty_list_when_none(self):
        """Test that None returns empty list."""
        result = load_django_middleware(None)
        assert result == []

    def test_returns_middleware_stack_for_list(self):
        """Test that list config returns a DjangoMiddlewareStack."""
        result = load_django_middleware([
            'django.contrib.sessions.middleware.SessionMiddleware',
        ])
        assert len(result) == 1
        assert isinstance(result[0], DjangoMiddlewareStack)

    def test_returns_middleware_stack_for_true(self):
        """Test that True returns a DjangoMiddlewareStack (if MIDDLEWARE setting exists)."""
        result = load_django_middleware(True)
        # Should return either empty list (no middleware) or single stack
        assert isinstance(result, list)
        if result:
            assert len(result) == 1
            assert isinstance(result[0], DjangoMiddlewareStack)

    def test_exclude_config_filters_middleware(self):
        """Test that exclude configuration filters out middleware."""
        result = load_django_middleware({
            "include": [
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
            ],
            "exclude": ['django.middleware.common.CommonMiddleware']
        })

        # Only SessionMiddleware should be loaded (as a stack)
        assert len(result) == 1
        assert isinstance(result[0], DjangoMiddlewareStack)
        # The stack should only contain SessionMiddleware
        assert len(result[0].middleware_classes) == 1

    def test_handles_invalid_middleware_gracefully(self):
        """Test that invalid middleware paths are skipped gracefully."""
        # load_django_middleware should skip invalid paths and not crash
        result = load_django_middleware([
            'django.contrib.sessions.middleware.SessionMiddleware',
            'nonexistent.middleware.BrokenMiddleware',
        ])

        # Only valid middleware should be loaded (as a stack)
        assert len(result) == 1
        assert isinstance(result[0], DjangoMiddlewareStack)
        # The stack should only contain SessionMiddleware
        assert len(result[0].middleware_classes) == 1


# =============================================================================
# Test get_django_middleware_setting
# =============================================================================


class TestGetDjangoMiddlewareSetting:
    """Tests for get_django_middleware_setting function."""

    def test_returns_list(self):
        """Test that it returns a list."""
        result = get_django_middleware_setting()
        assert isinstance(result, list)


# =============================================================================
# Test BoltAPI Integration
# =============================================================================


class TestBoltAPIIntegration:
    """Tests for BoltAPI django_middleware parameter."""

    def test_boltapi_no_django_middleware(self):
        """Test BoltAPI without django_middleware."""
        api = BoltAPI()
        assert api.middleware == []

    def test_boltapi_django_middleware_false(self):
        """Test BoltAPI with django_middleware=False."""
        api = BoltAPI(django_middleware=False)
        assert api.middleware == []

    def test_boltapi_django_middleware_list_creates_stack(self):
        """Test BoltAPI with middleware list creates DjangoMiddlewareStack."""
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
        ])

        assert len(api.middleware) == 1
        assert isinstance(api.middleware[0], DjangoMiddlewareStack)

    def test_boltapi_combines_django_and_custom_middleware(self):
        """Test BoltAPI stores both Django and custom middleware."""
        api = BoltAPI(
            django_middleware=['django.contrib.sessions.middleware.SessionMiddleware'],
            middleware=[TimingMiddleware],
        )

        # Should have 2 middleware entries
        assert len(api.middleware) == 2
        # First should be DjangoMiddlewareStack
        assert isinstance(api.middleware[0], DjangoMiddlewareStack)
        # Second should be the custom middleware class
        assert api.middleware[1] is TimingMiddleware


# =============================================================================
# Test Full HTTP Cycle - Basic Handler Works
# =============================================================================


@pytest.mark.django_db
class TestBasicHTTPCycle:
    """Tests that verify basic HTTP cycle works with middleware configured."""

    def test_handler_works_with_django_middleware_configured(self):
        """Test that handlers work when django_middleware is configured."""
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
        ])

        @api.get("/test")
        async def test_route():
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

    def test_handler_works_with_multiple_middleware(self):
        """Test that handlers work with multiple Django middleware configured."""
        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
        ])

        @api.get("/test")
        async def test_route():
            return {"status": "ok"}

        with TestClient(api) as client:
            response = client.get("/test")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

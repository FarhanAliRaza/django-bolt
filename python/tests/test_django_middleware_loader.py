"""
Tests for Django middleware loader.

Tests the automatic loading of middleware from Django's settings.MIDDLEWARE.
"""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from django_bolt.middleware.django_loader import (
    load_django_middleware,
    get_django_middleware_setting,
    DEFAULT_EXCLUDED_MIDDLEWARE,
)
from django_bolt.middleware import DjangoMiddleware


# ═══════════════════════════════════════════════════════════════════════════
# Test Default Exclusions
# ═══════════════════════════════════════════════════════════════════════════


class TestDefaultExclusions:
    """Tests for default middleware exclusions."""

    def test_csrf_excluded_by_default(self):
        """Test that CSRF middleware is in default exclusions."""
        assert "django.middleware.csrf.CsrfViewMiddleware" in DEFAULT_EXCLUDED_MIDDLEWARE

    def test_clickjacking_excluded_by_default(self):
        """Test that clickjacking middleware is in default exclusions."""
        assert "django.middleware.clickjacking.XFrameOptionsMiddleware" in DEFAULT_EXCLUDED_MIDDLEWARE

    def test_messages_excluded_by_default(self):
        """Test that messages middleware is in default exclusions."""
        assert "django.contrib.messages.middleware.MessageMiddleware" in DEFAULT_EXCLUDED_MIDDLEWARE


# ═══════════════════════════════════════════════════════════════════════════
# Test load_django_middleware
# ═══════════════════════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════════════════════
# Test get_django_middleware_setting
# ═══════════════════════════════════════════════════════════════════════════


class TestGetDjangoMiddlewareSetting:
    """Tests for get_django_middleware_setting function."""

    def test_returns_list(self):
        """Test that it returns a list."""
        result = get_django_middleware_setting()
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════════════════════
# Test BoltAPI Integration
# ═══════════════════════════════════════════════════════════════════════════


class TestBoltAPIIntegration:
    """Tests for BoltAPI django_middleware parameter."""

    def test_boltapi_no_django_middleware(self):
        """Test BoltAPI without django_middleware."""
        from django_bolt import BoltAPI

        api = BoltAPI()

        assert api.middleware == []

    def test_boltapi_django_middleware_false(self):
        """Test BoltAPI with django_middleware=False."""
        from django_bolt import BoltAPI

        api = BoltAPI(django_middleware=False)

        assert api.middleware == []


# ═══════════════════════════════════════════════════════════════════════════
# Test Real Django Middleware Loading
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestRealDjangoMiddleware:
    """Tests with real Django middleware classes."""

    def test_loads_real_session_middleware(self):
        """Test loading real SessionMiddleware."""
        result = load_django_middleware([
            'django.contrib.sessions.middleware.SessionMiddleware',
        ])

        assert len(result) == 1
        assert isinstance(result[0], DjangoMiddleware)

    def test_loads_real_auth_middleware(self):
        """Test loading real AuthenticationMiddleware."""
        result = load_django_middleware([
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ])

        assert len(result) == 1
        assert isinstance(result[0], DjangoMiddleware)

    def test_loads_multiple_real_middleware(self):
        """Test loading multiple real middleware."""
        result = load_django_middleware([
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ])

        assert len(result) == 3
        assert all(isinstance(mw, DjangoMiddleware) for mw in result)

    def test_loads_from_settings_middleware(self):
        """Test loading from Django settings.MIDDLEWARE."""
        # This test uses the actual Django settings
        result = load_django_middleware(True)

        # Should load at least some middleware (minus excluded ones)
        # The exact count depends on Django settings
        assert isinstance(result, list)
        assert all(isinstance(mw, DjangoMiddleware) for mw in result)

    def test_exclude_config_works(self):
        """Test exclude configuration."""
        result = load_django_middleware({
            "include": [
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
            ],
            "exclude": ['django.middleware.common.CommonMiddleware']
        })

        # Only SessionMiddleware should be loaded
        assert len(result) == 1

    def test_include_overrides_settings(self):
        """Test that include list overrides settings.MIDDLEWARE."""
        result = load_django_middleware([
            'django.contrib.sessions.middleware.SessionMiddleware',
        ])

        # Should only load what we specified
        assert len(result) == 1

    def test_exclude_defaults_false_includes_csrf(self):
        """Test that exclude_defaults=False includes CSRF."""
        result = load_django_middleware(
            ['django.middleware.csrf.CsrfViewMiddleware'],
            exclude_defaults=False
        )

        # CSRF should be included
        assert len(result) == 1

    def test_boltapi_with_django_middleware_list(self):
        """Test BoltAPI with specific middleware list."""
        from django_bolt import BoltAPI

        api = BoltAPI(django_middleware=[
            'django.contrib.sessions.middleware.SessionMiddleware',
        ])

        assert len(api.middleware) == 1
        assert isinstance(api.middleware[0], DjangoMiddleware)

    def test_boltapi_combines_django_and_custom(self):
        """Test BoltAPI combines Django and custom middleware."""
        from django_bolt import BoltAPI
        from django_bolt.middleware import TimingMiddleware

        timing = TimingMiddleware()
        api = BoltAPI(
            django_middleware=['django.contrib.sessions.middleware.SessionMiddleware'],
            middleware=[timing],
        )

        assert len(api.middleware) == 2
        assert isinstance(api.middleware[0], DjangoMiddleware)  # Django first
        assert api.middleware[1] is timing  # Custom second

    def test_handles_invalid_middleware_path(self):
        """Test that invalid middleware paths are skipped gracefully."""
        result = load_django_middleware([
            'django.contrib.sessions.middleware.SessionMiddleware',
            'nonexistent.middleware.BrokenMiddleware',
        ])

        # Only valid middleware should be loaded
        assert len(result) == 1

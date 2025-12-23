"""Pytest configuration for example project tests."""
import os

import django
from django.conf import settings


def pytest_configure(config):
    """Configure Django settings for pytest."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testproject.settings")

    if not settings.configured:
        django.setup()

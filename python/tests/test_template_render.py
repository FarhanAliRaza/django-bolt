"""
Tests for Django template rendering via the render shortcut.

Issue: render() defaults content_type=None, which creates a header tuple with None value.
Rust fails to extract Vec<(String, String)> and returns 500 error.

Fix: render() should default content_type to "text/html".
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from django_bolt import BoltAPI
from django_bolt.shortcuts import render
from django_bolt.testing import TestClient


@pytest.fixture(scope="module")
def api():
    # Create a temp template
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    template_file = templates_dir / "test_dashboard.html"
    template_file.write_text("<html><body><h1>{{ title }}</h1></body></html>")

    # Configure Django templates
    from django.conf import settings
    if templates_dir not in settings.TEMPLATES[0].get("DIRS", []):
        settings.TEMPLATES[0]["DIRS"] = [str(templates_dir)] + list(settings.TEMPLATES[0].get("DIRS", []))
        from django.template import engines
        engines._engines = {}

    api = BoltAPI()

    @api.get("/dashboard")
    async def dashboard(req):
        return render(req, "test_dashboard.html", {"title": "Dashboard"})

    yield api

    # Cleanup
    template_file.unlink(missing_ok=True)
    templates_dir.rmdir()


@pytest.fixture(scope="module")
def client(api):
    return TestClient(api)


class TestRenderShortcut:

    def test_render_returns_200(self, client):
        response = client.get("/dashboard")
        assert response.status_code == 200

    def test_render_returns_html_content(self, client):
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert "<h1>Dashboard</h1>" in response.text

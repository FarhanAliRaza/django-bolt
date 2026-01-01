"""
Tests for Django template rendering via the render shortcut.

Issue: render() defaults content_type=None, which creates a header tuple with None value.
Rust fails to extract Vec<(String, String)> and returns 500 error.

Fix: render() should default content_type to "text/html".
"""

from __future__ import annotations

import pytest
from django.test import override_settings

from django_bolt import BoltAPI
from django_bolt.shortcuts import render
from django_bolt.testing import TestClient

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            "loaders": [
                (
                    "django.template.loaders.locmem.Loader",
                    {
                        "test_dashboard.html": "<html><body><h1>{{ title }}</h1></body></html>",
                    },
                ),
            ],
        },
    },
]


@pytest.fixture(scope="module")
def api():
    api = BoltAPI()

    @api.get("/dashboard")
    async def dashboard(req):
        return render(req, "test_dashboard.html", {"title": "Dashboard"})

    return api


@pytest.fixture(scope="module")
def client(api):
    return TestClient(api)


class TestRenderShortcut:
    def test_render_returns_200(self, client):
        with override_settings(TEMPLATES=TEMPLATES):
            response = client.get("/dashboard")
            assert response.status_code == 200

    def test_render_returns_html_content(self, client):
        with override_settings(TEMPLATES=TEMPLATES):
            response = client.get("/dashboard")
            assert response.status_code == 200
            assert "<h1>Dashboard</h1>" in response.text

    def test_render_returns_html_content_type(self, client):
        with override_settings(TEMPLATES=TEMPLATES):
            response = client.get("/dashboard")
            assert response.status_code == 200
            content_type = response.headers.get("content-type", "")
            assert "text/html" in content_type

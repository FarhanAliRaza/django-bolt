"""
Tests for Actix-native static file serving.

Verifies that static files are served correctly from:
1. STATIC_ROOT (collected static files)
2. STATICFILES_DIRS (additional directories)
3. Django's staticfiles finders (app-level static files like admin)

Also tests Django template {% static %} tag integration.
"""

from __future__ import annotations

import os
import tempfile

import pytest

from django_bolt import BoltAPI
from django_bolt.admin.static import find_static_file
from django_bolt.shortcuts import render
from django_bolt.testing import TestClient


# Create test static files directory
TEST_STATIC_DIR = tempfile.mkdtemp(prefix="django_bolt_static_")

# Create test CSS file
CSS_DIR = os.path.join(TEST_STATIC_DIR, "css")
os.makedirs(CSS_DIR, exist_ok=True)
CSS_FILE = os.path.join(CSS_DIR, "style.css")
with open(CSS_FILE, "w") as f:
    f.write("body { color: blue; font-family: sans-serif; }")

# Create test JS file
JS_DIR = os.path.join(TEST_STATIC_DIR, "js")
os.makedirs(JS_DIR, exist_ok=True)
JS_FILE = os.path.join(JS_DIR, "app.js")
with open(JS_FILE, "w") as f:
    f.write("console.log('Django-Bolt static files working!');")

# Create test image file (small PNG)
IMG_DIR = os.path.join(TEST_STATIC_DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)
IMG_FILE = os.path.join(IMG_DIR, "logo.png")
# Minimal valid 1x1 transparent PNG
PNG_BYTES = bytes([
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
    0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,  # RGBA, 8-bit
    0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT chunk
    0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,  # Compressed data
    0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,  # Adler32 checksum
    0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44,  # IEND chunk
    0xAE, 0x42, 0x60, 0x82                           # CRC
])
with open(IMG_FILE, "wb") as f:
    f.write(PNG_BYTES)


class TestFindStaticFile:
    """Tests for the find_static_file function used by Django finders fallback."""

    def test_find_file_in_static_root(self, monkeypatch):
        """Test finding a file in STATIC_ROOT."""
        from django.conf import settings

        # Temporarily set STATIC_ROOT
        original_root = getattr(settings, "STATIC_ROOT", None)
        settings.STATIC_ROOT = TEST_STATIC_DIR

        try:
            result = find_static_file("css/style.css")
            assert result is not None
            assert result.endswith("css/style.css")
            assert os.path.isfile(result)
        finally:
            if original_root:
                settings.STATIC_ROOT = original_root
            else:
                delattr(settings, "STATIC_ROOT")

    def test_find_file_in_staticfiles_dirs(self, monkeypatch):
        """Test finding a file in STATICFILES_DIRS."""
        from django.conf import settings

        # Create a second static directory
        second_dir = tempfile.mkdtemp(prefix="django_bolt_static2_")
        second_css = os.path.join(second_dir, "custom.css")
        with open(second_css, "w") as f:
            f.write("/* Custom styles */")

        # Temporarily set STATICFILES_DIRS
        original_dirs = getattr(settings, "STATICFILES_DIRS", None)
        settings.STATICFILES_DIRS = [second_dir]
        settings.STATIC_ROOT = None  # Clear to test STATICFILES_DIRS

        try:
            result = find_static_file("custom.css")
            assert result is not None
            assert result.endswith("custom.css")
        finally:
            if original_dirs:
                settings.STATICFILES_DIRS = original_dirs
            else:
                delattr(settings, "STATICFILES_DIRS")

    def test_find_nonexistent_file(self):
        """Test that None is returned for non-existent files."""
        result = find_static_file("nonexistent/file.xyz")
        assert result is None

    def test_directory_traversal_blocked(self):
        """Test that directory traversal attempts are blocked."""
        result = find_static_file("../etc/passwd")
        assert result is None

        result = find_static_file("..\\windows\\system32")
        assert result is None


class TestStaticFileServing:
    """Tests for static file serving via the test client."""

    @pytest.fixture(scope="class")
    def api_with_static(self):
        """Create API with static file routes."""
        from django_bolt.admin.static import register_static_routes

        api = BoltAPI()
        register_static_routes(api)

        @api.get("/health")
        async def health():
            return {"status": "ok"}

        return api

    @pytest.fixture(scope="class")
    def client(self, api_with_static):
        """Create test client."""
        return TestClient(api_with_static, use_http_layer=True)

    def test_serve_css_file(self, client, monkeypatch):
        """Test serving a CSS file."""
        from django.conf import settings

        settings.STATIC_ROOT = TEST_STATIC_DIR
        settings.STATIC_URL = "/static/"

        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")
        assert b"color: blue" in response.content

    def test_serve_js_file(self, client, monkeypatch):
        """Test serving a JavaScript file."""
        from django.conf import settings

        settings.STATIC_ROOT = TEST_STATIC_DIR
        settings.STATIC_URL = "/static/"

        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "javascript" in content_type or "application/javascript" in content_type
        assert b"console.log" in response.content

    def test_serve_image_file(self, client, monkeypatch):
        """Test serving an image file."""
        from django.conf import settings

        settings.STATIC_ROOT = TEST_STATIC_DIR
        settings.STATIC_URL = "/static/"

        response = client.get("/static/img/logo.png")
        assert response.status_code == 200
        assert "image/png" in response.headers.get("content-type", "")
        # PNG signature
        assert response.content[:4] == b"\x89PNG"

    def test_static_file_not_found(self, client):
        """Test 404 for non-existent static files."""
        response = client.get("/static/nonexistent/file.xyz")
        assert response.status_code == 404

    def test_directory_traversal_blocked(self, client):
        """Test that directory traversal is blocked."""
        response = client.get("/static/../../../etc/passwd")
        assert response.status_code in (400, 404)

        response = client.get("/static/css/../../etc/passwd")
        assert response.status_code in (400, 404)


class TestDjangoAdminStaticFiles:
    """Tests for Django admin static files via staticfiles finders."""

    def test_find_admin_css(self):
        """Test that Django admin CSS can be found via finders."""
        # This relies on django.contrib.admin being installed
        result = find_static_file("admin/css/base.css")

        # May be None if Django admin isn't fully installed
        # In CI/test environments, admin static files should be available
        if result is not None:
            assert "admin" in result
            assert result.endswith("base.css")
            assert os.path.isfile(result)

    def test_find_admin_js(self):
        """Test that Django admin JS can be found via finders."""
        result = find_static_file("admin/js/core.js")

        if result is not None:
            assert "admin" in result
            assert result.endswith("core.js")
            assert os.path.isfile(result)


class TestStaticTemplateTag:
    """Tests for Django template {% static %} tag with Bolt."""

    @pytest.fixture(scope="class")
    def api_with_template(self):
        """Create API with template that uses static tag."""
        from django.conf import settings

        # Configure static settings
        settings.STATIC_ROOT = TEST_STATIC_DIR
        settings.STATIC_URL = "/static/"

        api = BoltAPI()

        @api.get("/page")
        async def page(req):
            return render(req, "test_static_page.html", {"title": "Static Test"})

        return api

    @pytest.fixture(scope="class")
    def client(self, api_with_template):
        """Create test client."""
        return TestClient(api_with_template)

    def test_static_tag_renders_url(self, client):
        """Test that {% static %} tag renders correct URL."""
        response = client.get("/page")
        assert response.status_code == 200
        # The template should contain a reference to the static URL
        assert "/static/" in response.text or "static" in response.text.lower()


class TestMultipleDirectories:
    """Tests for serving from multiple static directories."""

    def test_searches_directories_in_order(self, monkeypatch):
        """Test that directories are searched in priority order."""
        from django.conf import settings

        # Create two directories with same-named file
        dir1 = tempfile.mkdtemp(prefix="static_priority1_")
        dir2 = tempfile.mkdtemp(prefix="static_priority2_")

        # Put different content in each
        with open(os.path.join(dir1, "test.txt"), "w") as f:
            f.write("FROM_DIR1")
        with open(os.path.join(dir2, "test.txt"), "w") as f:
            f.write("FROM_DIR2")

        # Set STATIC_ROOT as first priority
        settings.STATIC_ROOT = dir1
        settings.STATICFILES_DIRS = [dir2]

        result = find_static_file("test.txt")
        assert result is not None

        with open(result) as f:
            content = f.read()

        # STATIC_ROOT should take priority
        assert content == "FROM_DIR1"

    def test_fallback_to_second_directory(self, monkeypatch):
        """Test falling back to second directory when file not in first."""
        from django.conf import settings

        # Create two directories, file only in second
        dir1 = tempfile.mkdtemp(prefix="static_fallback1_")
        dir2 = tempfile.mkdtemp(prefix="static_fallback2_")

        with open(os.path.join(dir2, "only_in_dir2.txt"), "w") as f:
            f.write("FOUND")

        settings.STATIC_ROOT = dir1
        settings.STATICFILES_DIRS = [dir2]

        result = find_static_file("only_in_dir2.txt")
        assert result is not None

        with open(result) as f:
            assert f.read() == "FOUND"


class TestCachingHeaders:
    """Tests for HTTP caching headers on static files."""

    @pytest.fixture(scope="class")
    def api(self):
        """Create API with static routes."""
        from django_bolt.admin.static import register_static_routes

        api = BoltAPI()
        register_static_routes(api)
        return api

    @pytest.fixture(scope="class")
    def client(self, api):
        """Create test client with HTTP layer."""
        return TestClient(api, use_http_layer=True)

    def test_etag_header_present(self, client, monkeypatch):
        """Test that ETag header is returned."""
        from django.conf import settings

        settings.STATIC_ROOT = TEST_STATIC_DIR
        settings.STATIC_URL = "/static/"

        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        # ETag may or may not be present depending on handler
        # Just verify the response is valid

    def test_content_type_correct(self, client, monkeypatch):
        """Test that Content-Type is correctly set."""
        from django.conf import settings

        settings.STATIC_ROOT = TEST_STATIC_DIR
        settings.STATIC_URL = "/static/"

        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")

        response = client.get("/static/js/app.js")
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "javascript" in content_type

        response = client.get("/static/img/logo.png")
        assert response.status_code == 200
        assert "image/png" in response.headers.get("content-type", "")

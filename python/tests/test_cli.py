"""Tests for Django-Bolt CLI.

These tests verify that the CLI works correctly, including the critical requirement
that it can be imported and run WITHOUT Django settings being configured.
"""
from __future__ import annotations

import subprocess
import sys


class TestCLIImportWithoutDjangoSettings:
    """Test that CLI can be imported without Django settings configured.

    This is critical for `django-bolt init` to work on projects that haven't
    set up Django yet. The fix for this was making _EMPTY_QUERYDICT lazy
    in django_adapter.py.
    """

    def test_cli_import_without_django_settings(self):
        """CLI module can be imported without DJANGO_SETTINGS_MODULE set."""
        # Run in a subprocess to ensure clean environment without Django settings
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                # Explicitly unset DJANGO_SETTINGS_MODULE and try to import
                "import os; "
                "os.environ.pop('DJANGO_SETTINGS_MODULE', None); "
                "from django_bolt.cli import main; "
                "print('OK')",
            ],
            capture_output=True,
            text=True,
            env={},  # Empty environment - no Django settings
        )
        assert result.returncode == 0, f"Import failed: {result.stderr}"
        assert "OK" in result.stdout

    def test_django_bolt_module_import_without_django_settings(self):
        """Main django_bolt module can be imported without Django settings."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import os; "
                "os.environ.pop('DJANGO_SETTINGS_MODULE', None); "
                "import django_bolt; "
                "print('OK')",
            ],
            capture_output=True,
            text=True,
            env={},
        )
        assert result.returncode == 0, f"Import failed: {result.stderr}"
        assert "OK" in result.stdout

    def test_boltapi_import_without_django_settings(self):
        """BoltAPI can be imported without Django settings."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import os; "
                "os.environ.pop('DJANGO_SETTINGS_MODULE', None); "
                "from django_bolt import BoltAPI; "
                "print('OK')",
            ],
            capture_output=True,
            text=True,
            env={},
        )
        assert result.returncode == 0, f"Import failed: {result.stderr}"
        assert "OK" in result.stdout


class TestCLICommands:
    """Test CLI command execution."""

    def test_version_command(self):
        """django-bolt version command works."""
        # Use click's test runner via Python to invoke the CLI
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from django_bolt.cli import main; main(['version'])",
            ],
            capture_output=True,
            text=True,
            cwd="/home/farhan/code/django-bolt",
        )
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert "Django-Bolt version:" in result.stdout

    def test_init_without_django_project(self):
        """django-bolt init gives helpful error when no Django project found."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from django_bolt.cli import main; main(['init'])",
            ],
            capture_output=True,
            text=True,
            cwd="/tmp",  # Run in temp dir with no Django project
            env={},  # No Django settings
        )
        # Should fail gracefully with helpful message, not crash on import
        assert "manage.py not found" in result.stderr or "No Django project found" in result.stderr

    def test_help_command(self):
        """django-bolt --help works."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from django_bolt.cli import main; main(['--help'])",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert "Django-Bolt command line interface" in result.stdout

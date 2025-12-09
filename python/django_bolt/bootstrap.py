import importlib
import os
from pathlib import Path

# Django imports - may fail if Django not configured
try:
    import django
    from django.conf import settings

    # Import with alias for use in _info() function
    from django.conf import settings as dj_settings
except ImportError:
    settings = None
    django = None
    dj_settings = None


def ensure_django_ready() -> dict:
    """Ensure Django is properly configured using the project's settings module."""
    if settings and settings.configured:
        return _info()

    settings_module = os.getenv("DJANGO_SETTINGS_MODULE")
    if not settings_module:
        # Try to detect settings module from manage.py location
        settings_module = _detect_settings_module()
        if settings_module:
            os.environ["DJANGO_SETTINGS_MODULE"] = settings_module

    if not settings_module:
        raise RuntimeError(
            "Django settings module not found. Please ensure:\n"
            "1. You are running from a Django project directory (with manage.py)\n"
            "2. DJANGO_SETTINGS_MODULE environment variable is set\n"
            "3. Your project has a valid settings.py file"
        )

    try:
        importlib.import_module(settings_module)
        django.setup()
        return _info()
    except ImportError as e:
        raise RuntimeError(
            f"Failed to import Django settings module '{settings_module}': {e}\n"
            "Please check that your settings module exists and is valid."
        ) from e


def _detect_settings_module() -> str | None:
    """Try to auto-detect Django settings module from project structure."""
    # Look for manage.py in current directory or parent directories
    current = Path.cwd()
    for path in [current] + list(current.parents)[:3]:  # Check up to 3 levels up
        manage_py = path / "manage.py"
        if manage_py.exists():
            # Read manage.py to find settings module
            content = manage_py.read_text()
            if "DJANGO_SETTINGS_MODULE" in content:
                # Extract the settings module from manage.py
                for line in content.split('\n'):
                    if "DJANGO_SETTINGS_MODULE" in line and "setdefault" in line:
                        # Parse line like: os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
                        parts = line.split("'")
                        if len(parts) >= 4:
                            return parts[3]  # Return the settings module string
                        parts = line.split('"')
                        if len(parts) >= 4:
                            return parts[3]
    return None


def _info() -> dict:
    """Get information about the current Django configuration."""
    db = dj_settings.DATABASES.get("default", {})
    return {
        "mode": "django_project",
        "debug": bool(getattr(dj_settings, "DEBUG", False)),
        "database": db.get("ENGINE"),
        "database_name": db.get("NAME"),
        "settings_module": os.getenv("DJANGO_SETTINGS_MODULE"),
        "base_dir": str(getattr(dj_settings, "BASE_DIR", "")),
    }



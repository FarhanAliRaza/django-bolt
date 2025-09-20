import importlib
import os
import sys
from pathlib import Path

from django.conf import settings


def ensure_django_ready() -> dict:
    if settings.configured:
        # Best-effort detection when already configured
        mode = "attached" if os.getenv("DJANGO_SETTINGS_MODULE") else "embedded"
        return _info(mode)

    settings_module = os.getenv("DJANGO_SETTINGS_MODULE")
    if settings_module:
        try:
            importlib.import_module(settings_module)
        except Exception:
            _configure_embedded()
            return _info("embedded")
        else:
            # Attached (full Django project) mode
            import django
            django.setup()
            return _info("attached")
    else:
        _configure_embedded()
        return _info("embedded")


def _configure_embedded() -> None:
    from django.conf import settings as dj_settings

    # Determine base directory: env override, else directory of entry script, else CWD
    base_env = os.getenv("DJANGO_BOLT_BASE_DIR")
    if base_env:
        base_dir = Path(base_env).resolve()
    else:
        main_file = getattr(sys.modules.get("__main__"), "__file__", None)
        if main_file:
            base_dir = Path(main_file).resolve().parent
        else:
            base_dir = Path.cwd()

    # Determine database path: env override, else BASE_DIR/db.sqlite3
    db_path_env = os.getenv("DJANGO_BOLT_DB_PATH")
    db_path = Path(db_path_env).resolve() if db_path_env else (base_dir / "db.sqlite3")

    # Optional extra apps (comma-separated dotted paths)
    extra_apps = [a.strip() for a in os.getenv("DJANGO_BOLT_APPS", "").split(",") if a.strip()]

    # Optionally toggle admin (enabled by default)
    enable_admin = os.getenv("DJANGO_BOLT_ENABLE_ADMIN", "1").lower() in {"1", "true", "yes"}

    installed = [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]
    if enable_admin:
        installed.insert(0, "django.contrib.admin")

    installed.extend(extra_apps)

    dj_settings.configure(
        SECRET_KEY="dev-secret",
        DEBUG=bool(os.getenv("DJANGO_DEBUG", "1") != "0"),
        BASE_DIR=str(base_dir),
        ROOT_URLCONF="django_bolt.embedded_urls",
        ALLOWED_HOSTS=["*"],
        INSTALLED_APPS=installed,
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ]
                },
            }
        ],
        STATIC_URL="/static",
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": str(db_path),
            }
        },
        USE_TZ=True,
        TIME_ZONE=os.getenv("TIME_ZONE", "UTC"),
    )

    import django
    django.setup()

    # Auto-migrate so ORM is usable immediately in embedded mode
    from django.core.management import call_command

    call_command("migrate", interactive=False, run_syncdb=True, verbosity=0)


def _info(mode: str) -> dict:
    from django.conf import settings as dj_settings
    db = dj_settings.DATABASES.get("default", {})
    return {
        "mode": mode,
        "debug": bool(getattr(dj_settings, "DEBUG", False)),
        "database": db.get("ENGINE"),
        "database_name": db.get("NAME"),
        "settings_module": os.getenv("DJANGO_SETTINGS_MODULE"),
        "base_dir": str(getattr(dj_settings, "BASE_DIR", "")),
    }



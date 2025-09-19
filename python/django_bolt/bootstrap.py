import importlib
import os
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
            # Attached mode
            import django
            django.setup()
            return _info("attached")
    else:
        _configure_embedded()
        return _info("embedded")


def _configure_embedded() -> None:
    from django.conf import settings as dj_settings

    BASE_DIR = Path.cwd()
    db_path = BASE_DIR / "db.sqlite3"

    dj_settings.configure(
        SECRET_KEY="dev-secret",
        DEBUG=True,
        BASE_DIR=str(BASE_DIR),
        ROOT_URLCONF="django_bolt.embedded_urls",
        ALLOWED_HOSTS=["*"],
        INSTALLED_APPS=[
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
        ],
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
        TIME_ZONE="UTC",
    )

    import django
    django.setup()

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
    }



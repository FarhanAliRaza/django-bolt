"""
Pytest configuration for Django-Bolt tests.

Ensures Django settings are properly reset between tests.
Provides utilities for subprocess-based testing.
"""
import os
import pathlib
import signal
import socket
import subprocess
import sys
import time
import logging
import pytest

# Suppress httpx INFO logs during tests
logging.getLogger("httpx").setLevel(logging.WARNING)


def pytest_configure(config):
    """Configure Django settings for pytest-django."""
    import django
    from django.conf import settings

    # Skip configuration if DJANGO_SETTINGS_MODULE is already set
    # This allows specific test modules to use their own Django settings
    if os.getenv("DJANGO_SETTINGS_MODULE"):
        return

    if not settings.configured:
        # Configure with all apps including admin to support all tests
        # The admin apps don't significantly impact non-admin tests
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test-secret-key-global',
            ALLOWED_HOSTS=['*'],
            INSTALLED_APPS=[
                'django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'django_bolt',
            ],
            MIDDLEWARE=[
                'django.middleware.security.SecurityMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'django.middleware.clickjacking.XFrameOptionsMiddleware',
            ],
            ROOT_URLCONF='django_bolt.tests.admin_tests.urls',
            TEMPLATES=[
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': [],
                    'APP_DIRS': True,
                    'OPTIONS': {
                        'context_processors': [
                            'django.template.context_processors.debug',
                            'django.template.context_processors.request',
                            'django.contrib.auth.context_processors.auth',
                            'django.contrib.messages.context_processors.messages',
                        ],
                    },
                },
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            USE_TZ=True,
            LANGUAGE_CODE='en-us',
            TIME_ZONE='UTC',
            USE_I18N=True,
            STATIC_URL='/static/',
            DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
        )
        # Setup Django apps so ExceptionReporter works
        django.setup()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Ensure database migrations are run before any tests that use the database.
    This creates the auth_user table and other Django core tables.
    Also creates test model tables (Article, etc.).
    """
    from django.core.management import call_command
    from django.db import connection

    with django_db_blocker.unblock():
        # Run migrations to create all necessary tables
        call_command('migrate', '--run-syncdb', verbosity=0)

        # Create test model tables manually since they're not in migrations
        with connection.schema_editor() as schema_editor:
            from django_bolt.tests.test_models import Article
            schema_editor.create_model(Article)


def spawn_process(command):
    """Spawn a subprocess in a new process group"""
    import platform
    if platform.system() == "Windows":
        process = subprocess.Popen(
            command,
            shell=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    else:
        process = subprocess.Popen(
            command,
            preexec_fn=os.setsid,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    return process


def kill_process(process):
    """Kill a subprocess and its process group"""
    import platform
    if platform.system() == "Windows":
        try:
            process.send_signal(signal.CTRL_BREAK_EVENT)
        except:
            pass
        try:
            process.kill()
        except:
            pass
    else:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        except:
            pass


def wait_for_server(host, port, timeout=15):
    """Wait for server to be reachable"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.create_connection((host, port), timeout=2)
            sock.close()
            return True
        except Exception:
            time.sleep(0.5)
    return False


# Django configuration is now handled by pytest-django
# via pytest_configure above

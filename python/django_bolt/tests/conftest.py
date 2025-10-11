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


@pytest.fixture(autouse=True)
def reset_django_settings(request):
    """Reset Django settings after each test to prevent cross-test pollution"""
    from django.conf import settings, empty
    import django

    # Remember if auth was installed before test
    auth_was_installed = False
    if settings.configured:
        try:
            from django.apps import apps
            auth_was_installed = apps.is_installed('django.contrib.auth')
        except Exception:
            pass

    yield

    # Don't reset if we're in test_jwt_auth.py module (it has module-scoped auth setup)
    test_module = request.node.module.__name__
    if 'test_jwt_auth' in test_module:
        return

    # Only reset if auth wasn't installed (to allow auth tests to keep running)
    # Auth tests use module-scoped fixture so we don't want to reset between them
    if not auth_was_installed:
        # Reset settings wrapper after each test
        settings._wrapped = empty

        # Reset apps registry to allow reconfiguration
        try:
            django.apps.apps = django.apps.Apps(installed_apps=None)
        except Exception:
            pass

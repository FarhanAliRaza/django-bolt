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
import pytest


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
def reset_django_settings():
    """Reset Django settings after each test to prevent cross-test pollution"""
    from django.conf import settings, empty

    yield

    # Reset settings wrapper after each test
    settings._wrapped = empty
#!/usr/bin/env python
"""Test script to verify /blog endpoint works with --django-views."""

import subprocess
import time
import sys
import requests

def test_blog_endpoint():
    """Start server and test /blog endpoint."""
    print("Starting django-bolt server with --django-views...")

    # Start server using shell (so uv run works)
    cmd = "uv run python manage.py runbolt --host 127.0.0.1 --port 7782 --django-views"
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Wait for server to start and print startup messages
    import threading
    def read_output():
        for line in iter(proc.stdout.readline, ''):
            if line:
                print(f"[SERVER] {line.rstrip()}")

    output_thread = threading.Thread(target=read_output, daemon=True)
    output_thread.start()

    time.sleep(8)  # Wait longer for server to fully start

    try:
        # Test /blog endpoint (without trailing slash)
        print("\nTesting GET /blog endpoint (no slash)...")
        response = requests.get("http://127.0.0.1:7782/blog", timeout=5)
        print(f"Status: {response.status_code}")

        if response.status_code != 404:
            print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"Content length: {len(response.text)} bytes")
            if response.status_code == 200:
                print(f"\n✓ SUCCESS! /blog endpoint is working!")
                print(f"Response preview (first 500 chars):\n{response.text[:500]}")
                return True
        else:
            print(f"  Got 404 (expected if trailing slash is required)")

        # Test /blog/ endpoint (with trailing slash)
        print("\nTesting GET /blog/ endpoint (with slash)...")
        response = requests.get("http://127.0.0.1:7782/blog/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Content length: {len(response.text)} bytes")

        if response.status_code == 200:
            # Show first 500 chars of response
            print(f"\n✓ SUCCESS! /blog/ endpoint is working!")
            print(f"Response preview (first 500 chars):\n{response.text[:500]}")
            return True
        else:
            print(f"\n✗ ERROR: Got status code {response.status_code}")
            print(f"Response:\n{response.text}")
            return False

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False
    finally:
        print("\nShutting down server...")
        proc.terminate()
        proc.wait(timeout=5)

if __name__ == "__main__":
    success = test_blog_endpoint()
    sys.exit(0 if success else 1)

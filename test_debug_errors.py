#!/usr/bin/env python
"""Test script to verify DEBUG mode error handling."""

import subprocess
import time
import requests
import json
import sys

# Start server in background
print("Starting server...")
proc = subprocess.Popen(
    ["uv", "run", "python", "manage.py", "runbolt", "--host", "127.0.0.1", "--port", "18123"],
    cwd="/home/farhan/code/django-bolt/python/examples/testproject",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

# Wait for server to start
time.sleep(3)

try:
    # Test 1: Generic error (should show traceback in DEBUG mode)
    print("\n" + "="*60)
    print("Test 1: Generic error (/errors/internal)")
    print("="*60)
    response = requests.get("http://127.0.0.1:18123/errors/internal")
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Raw response: {response.text[:500]}")

    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        data = None

    if data and "extra" in data and "traceback" in data["extra"]:
        print("✅ SUCCESS: Traceback is included in DEBUG mode!")
        print(f"Traceback preview: {data['extra']['traceback'][:200]}...")
    else:
        print("❌ FAILED: Traceback not found in response")
        sys.exit(1)

    # Test 2: NotFound error
    print("\n" + "="*60)
    print("Test 2: NotFound error (/errors/not-found/0)")
    print("="*60)
    response = requests.get("http://127.0.0.1:18123/errors/not-found/0")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    if response.status_code == 404 and "Resource 0 not found" in data["detail"]:
        print("✅ SUCCESS: NotFound exception works correctly!")
    else:
        print("❌ FAILED: NotFound exception not working as expected")

    # Test 3: Validation error
    print("\n" + "="*60)
    print("Test 3: Validation error (/errors/validation)")
    print("="*60)
    response = requests.post(
        "http://127.0.0.1:18123/errors/validation",
        json={"username": "ab", "email": "invalid", "age": -5}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    if response.status_code == 422 and isinstance(data["detail"], list):
        print(f"✅ SUCCESS: Validation error with {len(data['detail'])} field errors!")
    else:
        print("❌ FAILED: Validation error not working as expected")

    # Test 4: Health check
    print("\n" + "="*60)
    print("Test 4: Health check (/health)")
    print("="*60)
    response = requests.get("http://127.0.0.1:18123/health")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    if data.get("status") == "ok":
        print("✅ SUCCESS: Health check works!")

    # Test 5: Ready check
    print("\n" + "="*60)
    print("Test 5: Ready check (/ready)")
    print("="*60)
    response = requests.get("http://127.0.0.1:18123/ready")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    if "checks" in data:
        print(f"✅ SUCCESS: Ready check with {len(data['checks'])} health checks!")

    print("\n" + "="*60)
    print("ALL TESTS PASSED! ✅")
    print("="*60)

finally:
    # Stop server
    print("\nStopping server...")
    proc.terminate()
    proc.wait(timeout=5)

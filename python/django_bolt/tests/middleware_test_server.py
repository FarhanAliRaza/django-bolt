#!/usr/bin/env python3
"""
Standalone server for middleware integration tests.
Runs in a subprocess to avoid router initialization conflicts.
"""
import sys
import os

# Ensure we can import from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

if __name__ == "__main__":
    from test_middleware_server import create_test_api

    # Get port from command line or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    host = "127.0.0.1"

    # Create and serve API
    api = create_test_api()
    print(f"Starting middleware test server on {host}:{port}", flush=True)
    api.serve(host=host, port=port)
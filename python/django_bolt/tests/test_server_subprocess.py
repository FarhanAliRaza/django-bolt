"""
Server script for running test server in subprocess.
This avoids the "Router already initialized" issue.
"""
import sys
import os

# Make sure we can import from the tests directory
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    # Import after path is set
    from test_syntax import create_test_api_for_subprocess

    # Get host and port from command line
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080

    # Create and serve
    api = create_test_api_for_subprocess()
    api.serve(host=host, port=port)
"""Test that checks if the Rust FFI is working."""
import sys
print("Testing Rust FFI...", flush=True)

from django_bolt import _core, BoltAPI

print("Creating API...", flush=True)
api = BoltAPI()

@api.get("/hello")
async def hello():
    return {"message": "world"}

print("Creating test app...", flush=True)
try:
    app_id = _core.create_test_app(api._dispatch, False)
    print(f"Created test app: {app_id}", flush=True)
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Registering routes...", flush=True)
try:
    routes = [(method, path, hid, handler) for method, path, hid, handler in api._routes]
    _core.register_test_routes(app_id, routes)
    print("Routes registered", flush=True)
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Ensuring runtime...", flush=True)
try:
    _core.ensure_test_runtime(app_id)
    print("Runtime ensured", flush=True)
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Making test request...", flush=True)
try:
    status, headers, body = _core.handle_test_request_for(
        app_id,
        "GET",
        "/hello",
        [],
        b"",
        None,
    )
    print(f"Response: {status}", flush=True)
    print(f"Body: {body}", flush=True)
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Destroying app...", flush=True)
_core.destroy_test_app(app_id)
print("Done!", flush=True)



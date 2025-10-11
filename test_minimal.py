"""Minimal test to debug hanging issue."""
import sys
print("1. Starting test", flush=True)

from django_bolt import BoltAPI
print("2. Imported BoltAPI", flush=True)

from django_bolt.testing import TestClient
print("3. Imported TestClient", flush=True)

api = BoltAPI()
print("4. Created API", flush=True)

@api.get("/hello")
async def hello():
    return {"message": "world"}

print("5. Registered route", flush=True)

print("6. About to create TestClient...", flush=True)
try:
    client = TestClient(api)
    print("7. Created TestClient", flush=True)
except Exception as e:
    print(f"ERROR creating client: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("8. About to make request...", flush=True)
try:
    response = client.get("/hello")
    print(f"9. Got response: {response.status_code}", flush=True)
    print(f"10. Response body: {response.json()}", flush=True)
except Exception as e:
    print(f"ERROR making request: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("11. Closing client...", flush=True)
client.close()
print("12. Done!", flush=True)



#!/usr/bin/env python
"""
Test server with middleware enabled
"""
from django_bolt import BoltAPI
from django_bolt.middleware import cors

# Create API with middleware
api = BoltAPI()

@api.get("/")
async def root():
    return {"message": "Hello from middleware-enabled server"}

@api.get("/with-context")
async def with_context(request: dict):
    """Access the middleware context"""
    return {
        "message": "Context test",
        "has_context": request.get("context") is not None
    }

@api.get("/cors-test")
@cors(origins=["http://localhost:3000"], credentials=True)
async def cors_test():
    return {"cors": "enabled"}

if __name__ == "__main__":
    print("Starting server with middleware support...")
    print("Test endpoints:")
    print("  GET http://127.0.0.1:8000/")
    print("  GET http://127.0.0.1:8000/with-context")
    print("  GET http://127.0.0.1:8000/cors-test")
    api.serve(host="127.0.0.1", port=8000)
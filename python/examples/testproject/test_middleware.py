#!/usr/bin/env python
"""
Test middleware functionality in Django-Bolt
"""
import asyncio
from django_bolt import BoltAPI
from django_bolt.middleware import rate_limit, cors, auth_required, skip_middleware

# Create API with global middleware config
api = BoltAPI(
    middleware_config={
        'cors': {
            'origins': ['http://localhost:3000'],
            'credentials': True
        }
    }
)

# Route with rate limiting
@api.get("/rate-limited")
@rate_limit(rps=10, burst=20)
async def rate_limited_endpoint():
    return {"message": "This endpoint is rate limited"}

# Route with CORS override
@api.get("/custom-cors")
@cors(origins=["https://example.com"], credentials=False)
async def custom_cors_endpoint():
    return {"message": "Custom CORS settings"}

# Route that skips global CORS
@api.get("/no-cors")
@skip_middleware("cors")
async def no_cors_endpoint():
    return {"message": "No CORS headers"}

# Protected route
@api.get("/protected")
@auth_required(mode="api_key", api_keys={"test-key-123"})
async def protected_endpoint():
    return {"message": "Protected data"}

# Route with multiple middleware
@api.post("/secure-upload")
@rate_limit(rps=5)
@cors(origins=["https://app.example.com"])
@auth_required(mode="jwt")
async def secure_upload(data: dict):
    return {"uploaded": True, "size": len(str(data))}

# Route that accesses middleware context
@api.get("/context-aware")
@auth_required(mode="api_key", api_keys={"key1", "key2"})
async def context_aware_endpoint(request: dict):
    context = request.get("context", {})
    return {
        "message": "Context aware endpoint",
        "has_context": context is not None,
        "context_keys": list(context.keys()) if context else []
    }

if __name__ == "__main__":
    # Print registered middleware info
    print("Registered routes with middleware:")
    for handler_id, meta in api._handler_middleware.items():
        handler = api._handlers.get(handler_id)
        if handler:
            print(f"  {handler.__name__}: {meta}")
    
    # Note: To actually run the server, use:
    # api.serve(host="127.0.0.1", port=8000)
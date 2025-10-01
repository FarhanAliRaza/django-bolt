#!/usr/bin/env python
"""
Test that middleware pipeline executes without errors
"""
import asyncio
from django_bolt import BoltAPI

# Create API with a simple test route
api = BoltAPI()

@api.get("/test")
async def test_endpoint():
    return {"status": "ok"}

@api.get("/test-context")
async def test_context(request: dict):
    """Test that context is accessible even without middleware"""
    context = request.get("context")
    return {
        "has_context": context is not None,
        "context_type": type(context).__name__ if context else "None"
    }

async def test_dispatch():
    """Test the dispatch without starting the server"""
    # Simulate a request
    test_request = {
        "method": "GET",
        "path": "/test",
        "body": b"",
        "params": {},
        "query": {},
        "headers": {},
        "cookies": {},
        "context": None
    }
    
    # Get the handler
    handler = None
    for method, path, handler_id, h in api._routes:
        if method == "GET" and path == "/test":
            handler = h
            break
    
    if handler:
        print("Testing dispatch...")
        try:
            result = await api._dispatch(handler, test_request)
            status, headers, body = result
            print(f"Status: {status}")
            print(f"Headers: {headers}")
            print(f"Body: {body.decode()}")
            print("✓ Dispatch successful")
        except Exception as e:
            print(f"✗ Dispatch failed: {e}")
    else:
        print("✗ Handler not found")

if __name__ == "__main__":
    print("Testing middleware pipeline...")
    asyncio.run(test_dispatch())
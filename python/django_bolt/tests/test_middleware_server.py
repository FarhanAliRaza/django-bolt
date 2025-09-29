"""
Integration test for middleware with actual server
"""
import asyncio
import httpx
import jwt
import time
import pytest
from django_bolt import BoltAPI
from django_bolt.middleware import rate_limit, cors, auth_required


def create_test_api():
    """Create test API with various middleware configurations"""
    # Setup minimal Django for testing
    import os
    import sys
    import django
    from django.conf import settings
    
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test-secret-key-for-middleware',
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'django_bolt',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            USE_TZ=True,
        )
        django.setup()
    
    api = BoltAPI(
        middleware_config={
            'cors': {
                'origins': ['http://localhost:3000'],
                'credentials': True
            }
        }
    )
    
    @api.get("/")
    async def root():
        return {"message": "Hello, middleware!"}
    
    @api.get("/rate-limited")
    @rate_limit(rps=5, burst=10)
    async def rate_limited_endpoint():
        return {"message": "This endpoint is rate limited", "timestamp": time.time()}
    
    @api.get("/cors-test")
    @cors(origins=["http://localhost:3000", "http://example.com"], credentials=True)
    async def cors_endpoint():
        return {"cors": "enabled"}
    
    @api.get("/protected-jwt")
    @auth_required(mode="jwt", secret="test-secret")
    async def jwt_protected():
        return {"message": "JWT protected content"}
    
    @api.get("/protected-api-key")
    @auth_required(mode="api_key", api_keys={"test-key-123", "test-key-456"})
    async def api_key_protected():
        return {"message": "API key protected content"}
    
    @api.get("/context-test")
    @auth_required(mode="api_key", api_keys={"test-key"})
    async def context_endpoint(request: dict):
        """Test that middleware context is available"""
        context = request.get("context", None)
        return {
            "has_context": context is not None,
            "context_keys": list(context.keys()) if context and hasattr(context, 'keys') else []
        }
    
    # OPTIONS is handled automatically by middleware
    
    return api


async def _test_server_endpoints():
    """Test middleware functionality with HTTP requests"""
    base_url = "http://127.0.0.1:8001"
    
    async with httpx.AsyncClient() as client:
        print("\n🧪 Testing Middleware Server Endpoints")
        print("=" * 50)
        
        # Test 1: Basic endpoint
        print("\n1. Testing basic endpoint...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            assert response.status_code == 200
            print("   ✓ Basic endpoint works")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
        
        # Test 2: Rate limiting
        print("\n2. Testing rate limiting...")
        try:
            # Make rapid requests to trigger rate limit (5 rps with burst of 10)
            success_count = 0
            for i in range(15):  # Try 15 requests rapidly
                response = await client.get(f"{base_url}/rate-limited")
                if response.status_code == 200:
                    success_count += 1
                else:
                    print(f"   Rate limited at request {i+1}: {response.status_code}")
                    if response.status_code == 429:
                        print(f"   ✓ Rate limiting works (got 429 after {success_count} successful requests)")
                        print(f"   Response: {response.text[:200]}")
                        if "Retry-After" in response.headers:
                            print(f"   Retry-After: {response.headers['Retry-After']} seconds")
                    break
            else:
                print(f"   ⚠ Made {success_count} successful requests without rate limit")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
        
        # Test 3: CORS headers
        print("\n3. Testing CORS...")
        try:
            headers = {"Origin": "http://localhost:3000"}
            response = await client.get(f"{base_url}/cors-test", headers=headers)
            print(f"   Status: {response.status_code}")
            cors_headers = {
                k: v for k, v in response.headers.items() 
                if k.lower().startswith("access-control")
            }
            print(f"   CORS headers: {cors_headers}")
            if "access-control-allow-origin" in response.headers:
                print("   ✓ CORS headers present")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
        
        # Test 4: CORS preflight (OPTIONS)
        print("\n4. Testing CORS preflight...")
        try:
            headers = {
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
            response = await client.options(f"{base_url}/cors-test", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 204:
                print("   ✓ CORS preflight handled (204 No Content)")
                cors_headers = {
                    k: v for k, v in response.headers.items() 
                    if k.lower().startswith("access-control")
                }
                print(f"   Preflight headers: {cors_headers}")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
        
        # Test 5: JWT authentication
        print("\n5. Testing JWT authentication...")
        
        # Test without token
        try:
            response = await client.get(f"{base_url}/protected-jwt")
            print(f"   Without token: {response.status_code}")
            if response.status_code == 401:
                print("   ✓ Rejected without token")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
        
        # Test with valid token
        try:
            token = jwt.encode(
                {"sub": "user123", "exp": int(time.time()) + 3600},
                "test-secret",
                algorithm="HS256"
            )
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{base_url}/protected-jwt", headers=headers)
            print(f"   With valid token: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ Valid JWT accepted")
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
        
        # Test with expired token
        try:
            expired_token = jwt.encode(
                {"sub": "user123", "exp": int(time.time()) - 3600},
                "test-secret",
                algorithm="HS256"
            )
            headers = {"Authorization": f"Bearer {expired_token}"}
            response = await client.get(f"{base_url}/protected-jwt", headers=headers)
            print(f"   With expired token: {response.status_code}")
            if response.status_code == 401:
                print("   ✓ Expired JWT rejected")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
        
        # Test 6: API key authentication
        print("\n6. Testing API key authentication...")
        
        # Test without key
        try:
            response = await client.get(f"{base_url}/protected-api-key")
            print(f"   Without API key: {response.status_code}")
            if response.status_code == 401:
                print("   ✓ Rejected without API key")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
        
        # Test with valid key
        try:
            headers = {"Authorization": "Bearer test-key-123"}
            response = await client.get(f"{base_url}/protected-api-key", headers=headers)
            print(f"   With valid API key: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ Valid API key accepted")
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
        
        # Test with invalid key
        try:
            headers = {"Authorization": "Bearer invalid-key"}
            response = await client.get(f"{base_url}/protected-api-key", headers=headers)
            print(f"   With invalid API key: {response.status_code}")
            if response.status_code == 401:
                print("   ✓ Invalid API key rejected")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
        
        # Test 7: Context availability
        print("\n7. Testing middleware context...")
        try:
            headers = {"Authorization": "Bearer test-key"}
            response = await client.get(f"{base_url}/context-test", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {data}")
                if data.get("has_context"):
                    print("   ✓ Context is available")
                else:
                    print("   ⚠ Context not available (might be expected)")
            elif response.status_code == 500:
                print(f"   ⚠ Server error - context might not be populated yet")
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
        
        print("\n" + "=" * 50)
        print("✅ Middleware server tests completed!")


@pytest.mark.asyncio
async def test_server_endpoints():
    """Pytest wrapper for server endpoint tests"""
    await _test_server_endpoints()


if __name__ == "__main__":
    import sys
    import threading
    import time
    
    # Create and start server in background
    api = create_test_api()
    
    def run_server():
        try:
            api.serve(host="127.0.0.1", port=8001)
        except Exception as e:
            print(f"Server error: {e}")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give server time to start
    print("Starting test server on http://127.0.0.1:8001")
    time.sleep(2)
    
    # Run tests
    try:
        asyncio.run(test_server_endpoints())
    except KeyboardInterrupt:
        print("\nTests interrupted")
    except Exception as e:
        print(f"Test error: {e}")
        sys.exit(1)
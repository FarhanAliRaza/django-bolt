"""
Test middleware functionality in Django-Bolt

Note: CORS and rate limiting are handled in Rust for performance.
The @cors() and @rate_limit() decorators attach metadata that Rust parses.
Python middleware classes (TimingMiddleware, etc.) run for custom logic only.
"""
import asyncio
import json
import time

import jwt
import msgspec
import pytest

from django_bolt import BoltAPI
from django_bolt.auth import APIKeyAuthentication, IsAuthenticated, JWTAuthentication
from django_bolt.middleware import Middleware, cors, rate_limit, skip_middleware


# Test models
class ItemModel(msgspec.Struct):
    id: int
    name: str


# Custom test middleware
class CustomTestMiddleware(Middleware):
    def __init__(self, name: str):
        self.name = name
        self.call_count = 0

    async def process_request(self, request, call_next):
        self.call_count += 1
        # Add marker to context
        if request.get("context"):
            request["context"][f"test_{self.name}"] = True
        response = await call_next(request)
        return response


class TestMiddlewareDecorators:
    """Test middleware decorator functionality"""

    def test_rate_limit_decorator(self):
        """Test rate limit decorator attaches metadata"""
        api = BoltAPI()

        @api.get("/limited")
        @rate_limit(rps=50, burst=100, key="ip")
        async def limited_endpoint():
            return {"status": "ok"}

        # Check that middleware metadata was attached
        handler = api._handlers[0]
        assert hasattr(handler, '__bolt_middleware__')
        middleware = handler.__bolt_middleware__
        assert len(middleware) > 0
        assert middleware[0]['type'] == 'rate_limit'
        assert middleware[0]['rps'] == 50
        assert middleware[0]['burst'] == 100
        assert middleware[0]['key'] == 'ip'

    def test_cors_decorator(self):
        """Test CORS decorator attaches metadata"""
        api = BoltAPI()

        @api.get("/cors-test")
        @cors(origins=["http://localhost:3000"], credentials=True, max_age=7200)
        async def cors_endpoint():
            return {"status": "ok"}

        handler = api._handlers[0]
        assert hasattr(handler, '__bolt_middleware__')
        middleware = handler.__bolt_middleware__
        assert len(middleware) > 0
        assert middleware[0]['type'] == 'cors'
        assert middleware[0]['origins'] == ["http://localhost:3000"]
        assert middleware[0]['credentials']
        assert middleware[0]['max_age'] == 7200

    def test_auth_via_guards(self):
        """Test authentication via guards parameter"""
        api = BoltAPI()

        @api.get(
            "/protected",
            auth=[JWTAuthentication(secret="test-secret", algorithms=["HS256", "HS384"])],
            guards=[IsAuthenticated()]
        )
        async def protected_endpoint():
            return {"status": "ok"}

        # Check that middleware metadata was compiled
        handler_id = 0
        assert handler_id in api._handler_middleware
        meta = api._handler_middleware[handler_id]
        assert 'auth_backends' in meta
        assert len(meta['auth_backends']) > 0
        assert meta['auth_backends'][0]['type'] == 'jwt'
        assert meta['auth_backends'][0]['secret'] == 'test-secret'
        assert meta['auth_backends'][0]['algorithms'] == ["HS256", "HS384"]

    def test_skip_middleware_decorator(self):
        """Test skip middleware decorator"""
        api = BoltAPI()

        @api.get("/no-middleware")
        @skip_middleware("cors", "rate_limit")
        async def no_middleware_endpoint():
            return {"status": "ok"}

        handler = api._handlers[0]
        assert hasattr(handler, '__bolt_skip_middleware__')
        skip = handler.__bolt_skip_middleware__
        assert "cors" in skip
        assert "rate_limit" in skip

    def test_multiple_middleware(self):
        """Test multiple middleware decorators on same route"""
        api = BoltAPI()

        @api.post(
            "/secure",
            auth=[APIKeyAuthentication(api_keys={"key1", "key2"})],
            guards=[IsAuthenticated()]
        )
        @rate_limit(rps=10)
        @cors(origins=["https://app.example.com"])
        async def secure_endpoint(data: dict):
            return {"received": data}

        handler = api._handlers[0]
        middleware = handler.__bolt_middleware__
        assert len(middleware) == 2  # rate_limit and cors

        # Check they're all there
        types = [m['type'] for m in middleware]
        assert 'rate_limit' in types
        assert 'cors' in types

        # Check auth is in metadata
        meta = api._handler_middleware[0]
        assert 'auth_backends' in meta
        assert len(meta['auth_backends']) > 0


class TestGlobalMiddleware:
    """Test global middleware configuration"""

    def test_global_middleware_config(self):
        """Test setting global middleware via BoltAPI constructor"""
        api = BoltAPI(
            middleware_config={
                'cors': {
                    'origins': ['*'],
                    'credentials': False
                },
                'rate_limit': {
                    'rps': 1000,
                    'burst': 2000,
                    'key': 'ip'
                }
            }
        )

        assert 'cors' in api.middleware_config
        assert 'rate_limit' in api.middleware_config
        assert api.middleware_config['cors']['origins'] == ['*']
        assert api.middleware_config['rate_limit']['rps'] == 1000

    def test_global_middleware_instances(self):
        """Test setting global middleware instances (Python middleware)"""
        # Create custom Python middleware instances
        custom_mw = CustomTestMiddleware("global1")

        api = BoltAPI(middleware=[custom_mw])

        assert len(api.middleware) == 1
        assert api.middleware[0] == custom_mw


class TestMiddlewareMetadata:
    """Test middleware metadata compilation"""

    def test_middleware_metadata_compilation(self):
        """Test that middleware metadata is compiled correctly"""
        api = BoltAPI(
            middleware_config={
                'cors': {'origins': ['*']}
            }
        )

        @api.get("/test")
        @rate_limit(rps=100)
        async def test_endpoint():
            return {"status": "ok"}

        # Check handler middleware metadata
        assert len(api._handler_middleware) > 0
        handler_id = 0
        meta = api._handler_middleware[handler_id]

        assert 'middleware' in meta
        assert len(meta['middleware']) == 2  # Global CORS + route rate_limit

        # Check types
        types = [m['type'] for m in meta['middleware']]
        assert 'cors' in types
        assert 'rate_limit' in types

    def test_skip_global_middleware(self):
        """Test skipping global middleware on specific routes"""
        api = BoltAPI(
            middleware_config={
                'cors': {'origins': ['*']},
                'rate_limit': {'rps': 100}
            }
        )

        @api.get("/no-cors")
        @skip_middleware("cors")
        async def no_cors_endpoint():
            return {"status": "ok"}

        handler_id = 0
        meta = api._handler_middleware[handler_id]

        # Should only have rate_limit, not cors
        assert len(meta['middleware']) == 1
        assert meta['middleware'][0]['type'] == 'rate_limit'
        assert 'cors' in meta['skip']


class TestMiddlewareExecution:
    """Test middleware execution in the pipeline"""

    @pytest.mark.asyncio
    async def test_request_dispatch_with_middleware(self):
        """Test that dispatch works with middleware metadata"""
        api = BoltAPI()

        @api.get("/test")
        @cors(origins=["*"])
        async def test_endpoint(request: dict):
            # Access context
            context = request.get("context")
            return {
                "has_context": context is not None,
                "context_type": type(context).__name__ if context else None
            }

        # Create test request
        test_request = {
            "method": "GET",
            "path": "/test",
            "body": b"",
            "params": {},
            "query": {},
            "headers": {},
            "cookies": {},
            "context": None  # Will be populated by middleware
        }

        # Get handler and handler_id
        handler_id = 0  # First registered handler
        handler = api._handlers[handler_id]

        # Dispatch with handler_id
        result = await api._dispatch(handler, test_request, handler_id)
        status, headers, body = result

        assert status == 200
        data = json.loads(body)
        assert "has_context" in data

    @pytest.mark.asyncio
    async def test_custom_middleware_execution(self):
        """Test custom middleware execution"""
        test_mw = CustomTestMiddleware("test1")
        api = BoltAPI(middleware=[test_mw])

        @api.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        # Note: This tests the Python side only
        # Rust middleware execution happens in the server
        assert test_mw.call_count == 0  # Not executed yet

    @pytest.mark.asyncio
    async def test_response_model_with_middleware(self):
        """Test response model validation with middleware"""
        api = BoltAPI()

        @api.post("/items", response_model=ItemModel)
        @cors(origins=["*"])
        async def create_item(item: ItemModel) -> ItemModel:
            return item

        test_request = {
            "method": "POST",
            "path": "/items",
            "body": msgspec.json.encode({"id": 1, "name": "Test"}),
            "params": {},
            "query": {},
            "headers": {"content-type": "application/json"},
            "cookies": {},
            "context": None
        }

        handler_id = 0  # First registered handler
        handler = api._handlers[handler_id]
        result = await api._dispatch(handler, test_request, handler_id)
        status, headers, body = result

        assert status == 200
        data = msgspec.json.decode(body)
        assert data["id"] == 1
        assert data["name"] == "Test"


class TestAuthTokenGeneration:
    """Test JWT token generation for auth testing"""

    def test_generate_valid_jwt(self):
        """Generate a valid JWT token for testing"""
        secret = "test-secret"
        payload = {
            "sub": "user123",
            "exp": int(time.time()) + 3600,  # 1 hour from now
            "iat": int(time.time()),
            "custom_claim": "test_value"
        }

        token = jwt.encode(payload, secret, algorithm="HS256")
        assert token is not None

        # Verify we can decode it
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        assert decoded["sub"] == "user123"
        assert decoded["custom_claim"] == "test_value"

    def test_generate_expired_jwt(self):
        """Generate an expired JWT token for testing"""
        secret = "test-secret"
        payload = {
            "sub": "user123",
            "exp": int(time.time()) - 3600,  # 1 hour ago
            "iat": int(time.time()) - 7200
        }

        token = jwt.encode(payload, secret, algorithm="HS256")

        # Should raise error when verifying
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, secret, algorithms=["HS256"])

    def test_generate_invalid_signature_jwt(self):
        """Generate a JWT with wrong signature"""
        secret = "test-secret"
        wrong_secret = "wrong-secret"
        payload = {
            "sub": "user123",
            "exp": int(time.time()) + 3600
        }

        token = jwt.encode(payload, wrong_secret, algorithm="HS256")

        # Should raise error when verifying with correct secret
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, secret, algorithms=["HS256"])


class TestMiddlewareIntegration:
    """Integration tests for middleware with actual server"""

    def test_middleware_registration(self):
        """Test that middleware gets registered with Rust"""
        api = BoltAPI()

        @api.get("/middleware-test")
        @rate_limit(rps=100)
        @cors(origins=["http://localhost:3000"])
        async def test_endpoint():
            return {"status": "ok"}

        # Check routes are registered
        assert len(api._routes) == 1
        method, path, handler_id, handler = api._routes[0]
        assert method == "GET"
        assert path == "/middleware-test"

        # Check middleware metadata
        assert handler_id in api._handler_middleware
        meta = api._handler_middleware[handler_id]
        assert len(meta['middleware']) == 2

        types = [m['type'] for m in meta['middleware']]
        assert 'rate_limit' in types
        assert 'cors' in types

    def test_preflight_route(self):
        """Test OPTIONS preflight handling"""
        api = BoltAPI()

        @api.get("/api/data")
        @cors(
            origins=["http://localhost:3000", "https://app.example.com"],
            methods=["GET", "POST", "PUT"],
            headers=["Content-Type", "Authorization", "X-Custom"],
            credentials=True,
            max_age=7200
        )
        async def get_data():
            return {"data": [1, 2, 3]}

        # The preflight will be handled by Rust middleware
        # Here we just verify the metadata is correct
        meta = api._handler_middleware[0]
        cors_config = next(m for m in meta['middleware'] if m['type'] == 'cors')

        assert cors_config['origins'] == ["http://localhost:3000", "https://app.example.com"]
        assert cors_config['methods'] == ["GET", "POST", "PUT"]
        assert cors_config['headers'] == ["Content-Type", "Authorization", "X-Custom"]
        assert cors_config['credentials']
        assert cors_config['max_age'] == 7200


if __name__ == "__main__":
    # Run basic tests
    print("Testing middleware decorators...")
    test_decorators = TestMiddlewareDecorators()
    test_decorators.test_rate_limit_decorator()
    test_decorators.test_cors_decorator()
    test_decorators.test_auth_via_guards()
    test_decorators.test_skip_middleware_decorator()
    test_decorators.test_multiple_middleware()
    print("✓ Decorator tests passed")

    print("\nTesting global middleware...")
    test_global = TestGlobalMiddleware()
    test_global.test_global_middleware_config()
    test_global.test_global_middleware_instances()
    print("✓ Global middleware tests passed")

    print("\nTesting middleware metadata...")
    test_meta = TestMiddlewareMetadata()
    test_meta.test_middleware_metadata_compilation()
    test_meta.test_skip_global_middleware()
    print("✓ Metadata tests passed")

    print("\nTesting JWT generation...")
    test_auth = TestAuthTokenGeneration()
    test_auth.test_generate_valid_jwt()
    test_auth.test_generate_expired_jwt()
    test_auth.test_generate_invalid_signature_jwt()
    print("✓ JWT tests passed")

    print("\nTesting middleware integration...")
    test_integration = TestMiddlewareIntegration()
    test_integration.test_middleware_registration()
    test_integration.test_preflight_route()
    print("✓ Integration tests passed")

    print("\nRunning async tests...")
    test_exec = TestMiddlewareExecution()
    asyncio.run(test_exec.test_request_dispatch_with_middleware())
    asyncio.run(test_exec.test_custom_middleware_execution())
    asyncio.run(test_exec.test_response_model_with_middleware())
    print("✓ Async execution tests passed")

    print("\n✅ All middleware tests passed!")

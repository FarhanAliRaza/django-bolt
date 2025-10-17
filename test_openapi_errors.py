#!/usr/bin/env python3
"""Test script to verify OpenAPI error responses are documented correctly."""

import sys
import msgspec
from typing import Optional

# Add django_bolt to path
sys.path.insert(0, "python")

# Configure Django settings before importing django_bolt
import django
from django.conf import settings

settings.configure(
    DEBUG=True,
    SECRET_KEY='test-secret-key-for-openapi-test',
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
    ],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
)
django.setup()

from django_bolt import BoltAPI
from django_bolt.openapi import OpenAPIConfig
from django_bolt.auth import JWTAuthentication, IsAuthenticated


# Create test structs
class UserCreate(msgspec.Struct):
    username: str
    email: str
    age: int


# Create API with OpenAPI enabled
api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="Test API",
        version="1.0.0",
        include_error_responses=True,
    )
)


@api.get("/simple")
async def simple_endpoint():
    """Simple GET endpoint without body."""
    return {"message": "ok"}


@api.post("/with-body")
async def endpoint_with_body(user: UserCreate):
    """POST endpoint with request body (should include 422)."""
    return {"username": user.username}


@api.get("/protected", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def protected_endpoint():
    """Protected endpoint (should include 401, 403)."""
    return {"message": "protected"}


@api.post("/protected-with-body", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def protected_with_body(user: UserCreate):
    """Protected endpoint with body (should include 401, 403, 422)."""
    return {"username": user.username}


def test_openapi_error_responses():
    """Test that error responses are properly documented in OpenAPI schema."""
    from django_bolt.openapi.schema_generator import SchemaGenerator

    # Generate schema
    config = api.openapi_config
    generator = SchemaGenerator(api, config)
    schema = generator.generate()

    print("=" * 80)
    print("OpenAPI Error Response Test")
    print("=" * 80)

    # Test 1: Simple GET endpoint (should only have 200, NOT 422)
    print("\n1. Testing /simple (GET without body):")
    simple_responses = schema.paths["/simple"].get.responses
    print(f"   Response codes: {list(simple_responses.keys())}")
    assert "200" in simple_responses, "Missing 200 response"
    assert "422" not in simple_responses, "Should NOT have 422 (no body)"
    print("   ✓ Correct - only successful response (no 422)")

    # Test 2: POST with body (should have 200 and 422)
    print("\n2. Testing /with-body (POST with body):")
    body_responses = schema.paths["/with-body"].post.responses
    print(f"   Response codes: {list(body_responses.keys())}")
    assert "200" in body_responses, "Missing 200 response"
    assert "422" in body_responses, "Missing 422 response (has body!)"
    print("   ✓ Correct - includes 422 for validation errors")

    # Test 3: Protected endpoint (should only have 200, NOT 422)
    print("\n3. Testing /protected (GET with auth/guards):")
    protected_responses = schema.paths["/protected"].get.responses
    print(f"   Response codes: {list(protected_responses.keys())}")
    assert "200" in protected_responses, "Missing 200 response"
    assert "422" not in protected_responses, "Should NOT have 422 (no body)"
    print("   ✓ Correct - only successful response (no 422)")

    # Test 4: Protected with body (should have 200 and 422)
    print("\n4. Testing /protected-with-body (POST with auth/guards/body):")
    full_responses = schema.paths["/protected-with-body"].post.responses
    print(f"   Response codes: {list(full_responses.keys())}")
    assert "200" in full_responses, "Missing 200 response"
    assert "422" in full_responses, "Missing 422 response (has body!)"
    print("   ✓ Correct - includes 422 for validation errors")

    # Test 5: Verify 422 validation error schema (FastAPI-compatible format)
    print("\n5. Testing 422 validation error schema structure:")
    validation_error_response = body_responses["422"]
    validation_schema = validation_error_response.content["application/json"].schema
    print(f"   Schema type: {validation_schema.type}")
    print(f"   Required fields: {validation_schema.required}")
    assert validation_schema.type == "object", "422 schema should be object"
    assert "detail" in validation_schema.required, "422 should require 'detail'"
    assert "detail" in validation_schema.properties, "422 should have 'detail' property"

    # In FastAPI format, "detail" is the array of errors (not a separate "errors" field)
    detail_schema = validation_schema.properties["detail"]
    assert detail_schema.type == "array", "detail should be array (FastAPI format)"

    # Verify the items in the array have the correct structure
    items_schema = detail_schema.items
    assert items_schema.type == "object", "detail items should be objects"
    assert "type" in items_schema.properties, "error items should have 'type'"
    assert "loc" in items_schema.properties, "error items should have 'loc'"
    assert "msg" in items_schema.properties, "error items should have 'msg'"
    print("   ✓ 422 validation error schema is correct (FastAPI-compatible)")

    print("\n" + "=" * 80)
    print("All tests passed! ✓")
    print("=" * 80)
    print("\nSummary:")
    print("  - Endpoints without body: Only 200 (successful response)")
    print("  - Endpoints with body: 200 + 422 (validation errors)")
    print("  - Standard errors (400, 401, 403, 500) are NOT documented")
    print("    (they are well-understood HTTP standards)")


def test_disable_error_responses():
    """Test that error responses can be disabled via config."""
    api_no_errors = BoltAPI(
        openapi_config=OpenAPIConfig(
            title="Test API",
            version="1.0.0",
            include_error_responses=False,  # Disable error responses
        )
    )

    @api_no_errors.post("/test")
    async def test_endpoint(user: UserCreate):
        return {"username": user.username}

    from django_bolt.openapi.schema_generator import SchemaGenerator

    config = api_no_errors.openapi_config
    generator = SchemaGenerator(api_no_errors, config)
    schema = generator.generate()

    print("\n" + "=" * 80)
    print("Testing include_error_responses=False")
    print("=" * 80)

    test_responses = schema.paths["/test"].post.responses
    print(f"\nResponse codes: {list(test_responses.keys())}")
    assert "200" in test_responses, "Should still have 200 response"
    assert "422" not in test_responses, "Should NOT have 422 (disabled)"
    assert "400" not in test_responses, "Should NOT have 400 (disabled)"
    assert "500" not in test_responses, "Should NOT have 500 (disabled)"
    print("✓ Error responses correctly disabled")


if __name__ == "__main__":
    try:
        test_openapi_error_responses()
        test_disable_error_responses()
        print("\n✓ All tests passed successfully!")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

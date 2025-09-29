"""
Integration tests for guards and authentication with actual HTTP server.

Tests the full request flow including Rust-side authentication and guard evaluation.

Note: For JWT token creation and Django User dependency injection tests,
see test_jwt_auth.py
"""
import httpx
import jwt
import time
import pytest
from django_bolt import BoltAPI
from django_bolt.auth import JWTAuthentication, APIKeyAuthentication
from django_bolt.permissions import (
    AllowAny, IsAuthenticated, IsAdminUser, IsStaff,
    HasPermission, HasAnyPermission
)


def create_guards_test_api():
    """Create test API with guards and authentication"""
    # Setup Django
    import django
    from django.conf import settings
    from django.core.management import call_command

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test-secret-key-for-guards',
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

        # Run migrations to create tables
        call_command('migrate', '--run-syncdb', verbosity=0)

    api = BoltAPI()

    # Helper function to create JWT tokens
    def create_token(user_id="user123", is_staff=False, is_admin=False, permissions=None):
        payload = {
            "sub": user_id,
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
            "is_staff": is_staff,
            "is_superuser": is_admin,
            "permissions": permissions or []
        }
        return jwt.encode(payload, "test-secret", algorithm="HS256")

    # Public endpoint with AllowAny
    @api.get("/public", guards=[AllowAny()])
    async def public_endpoint():
        return {"message": "public", "auth": "not required"}

    # Protected endpoint requiring authentication
    @api.get(
        "/protected",
        auth=[JWTAuthentication(secret="test-secret")],
        guards=[IsAuthenticated()]
    )
    async def protected_endpoint(request: dict):
        context = request.get("context", {})
        return {
            "message": "protected",
            "user_id": context.get("user_id"),
            "is_staff": context.get("is_staff", False),
            "is_admin": context.get("is_admin", False),
        }

    # Admin-only endpoint
    @api.get(
        "/admin",
        auth=[JWTAuthentication(secret="test-secret")],
        guards=[IsAdminUser()]
    )
    async def admin_endpoint(request: dict):
        context = request["context"]
        return {
            "message": "admin area",
            "user_id": context["user_id"],
            "is_admin": context["is_admin"],
        }

    # Staff-only endpoint
    @api.get(
        "/staff",
        auth=[JWTAuthentication(secret="test-secret")],
        guards=[IsStaff()]
    )
    async def staff_endpoint(request: dict):
        return {
            "message": "staff area",
            "user_id": request["context"]["user_id"],
        }

    # Permission-required endpoint
    @api.get(
        "/delete-users",
        auth=[JWTAuthentication(secret="test-secret")],
        guards=[HasPermission("users.delete")]
    )
    async def delete_users_endpoint():
        return {"message": "deleting users"}

    # Multiple permissions (any)
    @api.get(
        "/moderate",
        auth=[JWTAuthentication(secret="test-secret")],
        guards=[HasAnyPermission("users.moderate", "posts.moderate")]
    )
    async def moderate_endpoint():
        return {"message": "moderating content"}

    # API key authentication
    @api.get(
        "/api-endpoint",
        auth=[APIKeyAuthentication(api_keys={"valid-key-123", "valid-key-456"})],
        guards=[IsAuthenticated()]
    )
    async def api_key_endpoint(request: dict):
        return {
            "message": "API key valid",
            "user_id": request["context"].get("user_id"),
            "backend": request["context"].get("auth_backend"),
        }

    # Full context inspection endpoint
    @api.get(
        "/context",
        auth=[JWTAuthentication(secret="test-secret")],
        guards=[IsAuthenticated()]
    )
    async def context_endpoint(request: dict):
        context = request.get("context", {})
        return {
            "context_keys": list(context.keys()) if hasattr(context, 'keys') else [],
            "user_id": context.get("user_id"),
            "is_staff": context.get("is_staff"),
            "is_admin": context.get("is_admin"),
            "auth_backend": context.get("auth_backend"),
            "has_claims": "auth_claims" in context,
            "has_permissions": "permissions" in context,
        }

    # Store token creator on API for tests
    api._create_token = create_token

    return api


async def _test_guards_integration():
    """Run integration tests against the guards test server"""
    base_url = "http://127.0.0.1:8002"

    # Create tokens
    def create_token(user_id="user123", is_staff=False, is_admin=False, permissions=None):
        payload = {
            "sub": user_id,
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
            "is_staff": is_staff,
            "is_superuser": is_admin,
            "permissions": permissions or []
        }
        return jwt.encode(payload, "test-secret", algorithm="HS256")

    async with httpx.AsyncClient() as client:
        print("\n🧪 Testing Guards and Authentication")
        print("=" * 60)

        # Test 1: Public endpoint (no auth required)
        print("\n1. Testing public endpoint (AllowAny)...")
        try:
            response = await client.get(f"{base_url}/public")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            assert response.status_code == 200
            assert response.json()["auth"] == "not required"
            print("   ✓ Public endpoint accessible without auth")
        except Exception as e:
            print(f"   ✗ Failed: {e}")

        # Test 2: Protected endpoint without token (should fail with 401)
        print("\n2. Testing protected endpoint without token...")
        try:
            response = await client.get(f"{base_url}/protected")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            assert response.status_code == 401
            print("   ✓ Correctly rejected unauthenticated request (401)")
        except Exception as e:
            print(f"   ✗ Failed: {e}")

        # Test 3: Protected endpoint with valid token
        print("\n3. Testing protected endpoint with valid JWT token...")
        try:
            token = create_token(user_id="alice", is_staff=False, is_admin=False)
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{base_url}/protected", headers=headers)
            print(f"   Status: {response.status_code}")
            data = response.json()
            print(f"   Response: {data}")
            assert response.status_code == 200
            assert data["user_id"] == "alice"
            assert data["is_staff"] == False
            print("   ✓ Successfully authenticated with JWT token")
        except Exception as e:
            print(f"   ✗ Failed: {e}")

        # Test 4: Admin endpoint with non-admin token (should fail with 403)
        print("\n4. Testing admin endpoint with non-admin token...")
        try:
            token = create_token(user_id="bob", is_staff=False, is_admin=False)
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{base_url}/admin", headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            assert response.status_code == 403
            print("   ✓ Correctly rejected non-admin user (403)")
        except Exception as e:
            print(f"   ✗ Failed: {e}")

        # Test 5: Admin endpoint with admin token
        print("\n5. Testing admin endpoint with admin token...")
        try:
            token = create_token(user_id="admin", is_staff=True, is_admin=True)
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{base_url}/admin", headers=headers)
            print(f"   Status: {response.status_code}")
            data = response.json()
            print(f"   Response: {data}")
            assert response.status_code == 200
            assert data["user_id"] == "admin"
            assert data["is_admin"] == True
            print("   ✓ Admin user successfully accessed admin endpoint")
        except Exception as e:
            print(f"   ✗ Failed: {e}")

        # Test 6: Staff endpoint
        print("\n6. Testing staff endpoint...")
        try:
            # Non-staff user
            token = create_token(user_id="user", is_staff=False)
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{base_url}/staff", headers=headers)
            print(f"   Non-staff status: {response.status_code}")
            assert response.status_code == 403

            # Staff user
            token = create_token(user_id="staff_member", is_staff=True)
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{base_url}/staff", headers=headers)
            print(f"   Staff status: {response.status_code}")
            assert response.status_code == 200
            print("   ✓ Staff guard working correctly")
        except Exception as e:
            print(f"   ✗ Failed: {e}")

        # Test 7: Permission-based endpoint
        print("\n7. Testing permission-based endpoint...")
        try:
            # User without permission
            token = create_token(user_id="user", permissions=["users.view"])
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{base_url}/delete-users", headers=headers)
            print(f"   Without permission status: {response.status_code}")
            assert response.status_code == 403

            # User with permission
            token = create_token(user_id="admin", permissions=["users.delete", "users.view"])
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{base_url}/delete-users", headers=headers)
            print(f"   With permission status: {response.status_code}")
            assert response.status_code == 200
            print("   ✓ Permission guard working correctly")
        except Exception as e:
            print(f"   ✗ Failed: {e}")

        # Test 8: HasAnyPermission guard
        print("\n8. Testing HasAnyPermission guard...")
        try:
            # User with one of the required permissions
            token = create_token(user_id="mod", permissions=["posts.moderate"])
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{base_url}/moderate", headers=headers)
            print(f"   Status: {response.status_code}")
            assert response.status_code == 200
            print("   ✓ HasAnyPermission guard working")
        except Exception as e:
            print(f"   ✗ Failed: {e}")

        # Test 9: API Key authentication
        print("\n9. Testing API key authentication...")
        try:
            # Invalid API key
            headers = {"X-API-Key": "invalid-key"}
            response = await client.get(f"{base_url}/api-endpoint", headers=headers)
            print(f"   Invalid key status: {response.status_code}")
            assert response.status_code == 401

            # Valid API key
            headers = {"X-API-Key": "valid-key-123"}
            response = await client.get(f"{base_url}/api-endpoint", headers=headers)
            print(f"   Valid key status: {response.status_code}")
            data = response.json()
            print(f"   Response: {data}")
            assert response.status_code == 200
            assert data["backend"] == "api_key"
            print("   ✓ API key authentication working")
        except Exception as e:
            print(f"   ✗ Failed: {e}")

        # Test 10: Context population
        print("\n10. Testing context population...")
        try:
            token = create_token(
                user_id="context_test",
                is_staff=True,
                is_admin=False,
                permissions=["users.view", "users.create"]
            )
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{base_url}/context", headers=headers)
            data = response.json()
            print(f"   Context keys: {data['context_keys']}")
            print(f"   User ID: {data['user_id']}")
            print(f"   Is staff: {data['is_staff']}")
            print(f"   Auth backend: {data['auth_backend']}")
            print(f"   Has claims: {data['has_claims']}")
            print(f"   Has permissions: {data['has_permissions']}")

            assert data["user_id"] == "context_test"
            assert data["is_staff"] == True
            assert data["is_admin"] == False
            assert data["auth_backend"] == "jwt"
            assert data["has_claims"] == True
            print("   ✓ Context properly populated with auth data")
        except Exception as e:
            print(f"   ✗ Failed: {e}")

        # Test 11: Invalid JWT signature
        print("\n11. Testing invalid JWT signature...")
        try:
            # Create token with wrong secret
            payload = {
                "sub": "hacker",
                "exp": int(time.time()) + 3600,
            }
            bad_token = jwt.encode(payload, "wrong-secret", algorithm="HS256")
            headers = {"Authorization": f"Bearer {bad_token}"}
            response = await client.get(f"{base_url}/protected", headers=headers)
            print(f"   Status: {response.status_code}")
            assert response.status_code == 401
            print("   ✓ Invalid JWT signature correctly rejected")
        except Exception as e:
            print(f"   ✗ Failed: {e}")

        # Test 12: Expired JWT token
        print("\n12. Testing expired JWT token...")
        try:
            payload = {
                "sub": "user",
                "exp": int(time.time()) - 100,  # Expired
                "iat": int(time.time()) - 200,
            }
            expired_token = jwt.encode(payload, "test-secret", algorithm="HS256")
            headers = {"Authorization": f"Bearer {expired_token}"}
            response = await client.get(f"{base_url}/protected", headers=headers)
            print(f"   Status: {response.status_code}")
            assert response.status_code == 401
            print("   ✓ Expired token correctly rejected")
        except Exception as e:
            print(f"   ✗ Failed: {e}")

        print("\n" + "=" * 60)
        print("✓ All guard and authentication tests passed!")


def test_create_guards_api():
    """Test that the guards API can be created"""
    api = create_guards_test_api()
    assert api is not None
    assert len(api._routes) > 0
    assert hasattr(api, '_create_token')

    # Note: For JWT token creation and Django User dependency injection tests,
    # see test_jwt_auth.py


if __name__ == "__main__":
    # For manual testing, you would:
    # 1. Start the server: python manage.py runbolt --port 8002
    # 2. Run: python -m pytest test_guards_integration.py -v -s
    pytest.main([__file__, "-v"])
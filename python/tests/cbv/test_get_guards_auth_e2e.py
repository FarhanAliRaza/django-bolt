import time

import jwt

from django_bolt import BoltAPI
from django_bolt.auth.backends import APIKeyAuthentication, JWTAuthentication
from django_bolt.auth.guards import AllowAny, HasPermission, IsAuthenticated, IsStaff
from django_bolt.testing import TestClient
from django_bolt.views import APIView, ViewSet


def create_jwt_token(
    user_id: int = 1,
    is_staff: bool = False,
    is_superuser: bool = False,
    permissions: list[str] | None = None,
    secret: str = "test-secret",
) -> str:
    """Helper to create JWT tokens for testing."""
    payload = {
        "sub": str(user_id),
        "user_id": user_id,
        "exp": int(time.time()) + 3600,
        "iat": int(time.time()),
        "is_staff": is_staff,
        "is_superuser": is_superuser,
        "permissions": permissions or [],
    }
    return jwt.encode(payload, secret, algorithm="HS256")


# --- get_guards() E2E Tests ---


def test_get_guards_default_behavior_e2e():
    """Test that default guards work in real HTTP requests."""
    api = BoltAPI()

    @api.view("/protected")
    class ProtectedView(APIView):
        guards = [IsAuthenticated()]
        auth = [JWTAuthentication(secret="test-secret")]

        async def get(self, request) -> dict:
            return {"message": "protected", "user_id": request.get("auth", {}).get("user_id")}

    with TestClient(api) as client:
        # Without token - should be 401
        response = client.get("/protected")
        assert response.status_code == 401

        # With valid token - should be 200
        token = create_jwt_token(user_id=123, secret="test-secret")
        response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "protected"
        assert data["user_id"] == 123


def test_get_guards_override_behavior_e2e():
    """Test that overriding get_guards() works in real HTTP requests."""
    api = BoltAPI()

    @api.view("/dynamic-guards")
    class DynamicGuardsView(APIView):
        guards = [IsAuthenticated()]  # Default

        def get_guards(self):
            # Override to allow anonymous access
            return [AllowAny()]

        async def get(self, request) -> dict:
            return {"message": "public", "authenticated": "user_id" in request.get("auth", {})}

    with TestClient(api) as client:
        # Should work without token (AllowAny)
        response = client.get("/dynamic-guards")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "public"
        assert data["authenticated"] is False

        # Should also work with token
        token = create_jwt_token(user_id=123, secret="test-secret")
        response = client.get("/dynamic-guards", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True


def test_get_guards_action_based_e2e():
    """Test that get_guards() can use action to determine guards."""
    api = BoltAPI()

    @api.view("/articles")
    class ArticleView(APIView):
        guards = [IsAuthenticated()]  # Default

        def get_guards(self):
            # Allow anonymous for GET, require auth for POST
            action = getattr(self, "action", None)
            if action == "get":
                return [AllowAny()]
            return [IsAuthenticated()]

        auth = [JWTAuthentication(secret="test-secret")]

        async def get(self, request) -> dict:
            return {"message": "list articles", "public": True}

        async def post(self, request) -> dict:
            return {"message": "create article", "user_id": request.get("auth", {}).get("user_id")}

    with TestClient(api) as client:
        # GET should work without token (AllowAny)
        response = client.get("/articles")
        assert response.status_code == 200
        data = response.json()
        assert data["public"] is True

        # POST should require authentication
        response = client.post("/articles", json={"title": "Test"})
        assert response.status_code == 401

        # POST with token should work
        token = create_jwt_token(user_id=123, secret="test-secret")
        response = client.post("/articles", json={"title": "Test"}, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 123


def test_get_guards_in_viewset_e2e():
    """Test that ViewSet can override get_guards() for different actions."""
    api = BoltAPI()

    @api.viewset("/articles")
    class ArticleViewSet(ViewSet):
        guards = [IsAuthenticated()]  # Default
        auth = [JWTAuthentication(secret="test-secret")]

        def get_guards(self):
            # Allow anonymous for list/retrieve, require auth for create
            action = getattr(self, "action", None)
            if action in ("list", "retrieve"):
                return [AllowAny()]
            return [IsAuthenticated()]

        async def list(self, request) -> dict:
            return {"message": "list", "public": True}

        async def retrieve(self, request, pk: int) -> dict:
            return {"message": "retrieve", "pk": pk, "public": True}

        async def create(self, request, data: dict) -> dict:
            return {"message": "create", "user_id": request.get("auth", {}).get("user_id")}

    with TestClient(api) as client:
        # List should work without token
        response = client.get("/articles")
        assert response.status_code == 200
        data = response.json()
        assert data["public"] is True

        # Retrieve should work without token
        response = client.get("/articles/1")
        assert response.status_code == 200
        data = response.json()
        assert data["public"] is True

        # Create should require authentication
        response = client.post("/articles", json={"title": "Test"})
        assert response.status_code == 401

        # Create with token should work
        token = create_jwt_token(user_id=123, secret="test-secret")
        response = client.post("/articles", json={"title": "Test"}, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 123


def test_get_guards_returns_none_e2e():
    """Test that get_guards() returning None disables guards."""
    api = BoltAPI()

    @api.view("/no-guards")
    class NoGuardsView(APIView):
        guards = [IsAuthenticated()]  # Class-level default

        def get_guards(self):
            return None  # Explicitly disable guards

        async def get(self, request) -> dict:
            return {"message": "no guards", "public": True}

    with TestClient(api) as client:
        # Should work without any authentication
        response = client.get("/no-guards")
        assert response.status_code == 200
        data = response.json()
        assert data["public"] is True


def test_get_guards_multiple_guards_e2e():
    """Test that get_guards() can return multiple guards."""
    api = BoltAPI()

    @api.view("/staff-only")
    class StaffOnlyView(APIView):
        guards = [IsAuthenticated()]

        def get_guards(self):
            # Require both authentication and staff status
            return [IsAuthenticated(), IsStaff()]

        auth = [JWTAuthentication(secret="test-secret")]

        async def get(self, request) -> dict:
            return {"message": "staff only", "user_id": request.get("auth", {}).get("user_id")}

    with TestClient(api) as client:
        # Without token - 401
        response = client.get("/staff-only")
        assert response.status_code == 401

        # With token but not staff - 403
        token = create_jwt_token(user_id=123, is_staff=False, secret="test-secret")
        response = client.get("/staff-only", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

        # With token and staff - 200
        token = create_jwt_token(user_id=123, is_staff=True, secret="test-secret")
        response = client.get("/staff-only", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 123


# --- get_auth() E2E Tests ---


def test_get_auth_default_behavior_e2e():
    """Test that default auth works in real HTTP requests."""
    api = BoltAPI()

    @api.view("/auth-required")
    class AuthRequiredView(APIView):
        auth = [JWTAuthentication(secret="test-secret")]
        guards = [IsAuthenticated()]

        async def get(self, request) -> dict:
            return {"message": "authenticated", "user_id": request.get("auth", {}).get("user_id")}

    with TestClient(api) as client:
        # Without token - 401
        response = client.get("/auth-required")
        assert response.status_code == 401

        # With valid token - 200
        token = create_jwt_token(user_id=456, secret="test-secret")
        response = client.get("/auth-required", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 456


def test_get_auth_override_behavior_e2e():
    """Test that overriding get_auth() works in real HTTP requests."""
    api = BoltAPI()

    @api.view("/dynamic-auth")
    class DynamicAuthView(APIView):
        auth = [JWTAuthentication(secret="test-secret")]  # Default

        def get_auth(self):
            # Override to use API key instead
            return [APIKeyAuthentication(api_keys={"test-key": "test-user"})]

        guards = [IsAuthenticated()]

        async def get(self, request) -> dict:
            return {"message": "api key auth", "user_id": request.get("auth", {}).get("user_id")}

    with TestClient(api) as client:
        # Without API key - 401
        response = client.get("/dynamic-auth")
        assert response.status_code == 401

        # With API key - 200
        response = client.get("/dynamic-auth", headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "api key auth"


def test_get_auth_action_based_e2e():
    """Test that get_auth() can use action to determine auth backend."""
    api = BoltAPI()

    @api.view("/mixed-auth")
    class MixedAuthView(APIView):
        auth = [JWTAuthentication(secret="test-secret")]  # Default

        def get_auth(self):
            # Use API key for GET, JWT for POST
            action = getattr(self, "action", None)
            if action == "get":
                return [APIKeyAuthentication(api_keys={"read-key": "reader"})]
            return [JWTAuthentication(secret="test-secret")]

        guards = [IsAuthenticated()]

        async def get(self, request) -> dict:
            return {"message": "api key", "auth_type": "api_key"}

        async def post(self, request) -> dict:
            return {"message": "jwt", "user_id": request.get("auth", {}).get("user_id")}

    with TestClient(api) as client:
        # GET with API key should work
        response = client.get("/mixed-auth", headers={"X-API-Key": "read-key"})
        assert response.status_code == 200
        data = response.json()
        assert data["auth_type"] == "api_key"

        # POST with JWT should work
        token = create_jwt_token(user_id=789, secret="test-secret")
        response = client.post("/mixed-auth", json={}, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 789


def test_get_auth_returns_none_e2e():
    """Test that get_auth() returning None disables auth."""
    api = BoltAPI()

    @api.view("/no-auth")
    class NoAuthView(APIView):
        auth = [JWTAuthentication(secret="test-secret")]  # Class-level default

        def get_auth(self):
            return None  # Explicitly disable auth

        guards = [AllowAny()]  # No auth needed, so allow any

        async def get(self, request) -> dict:
            return {"message": "no auth required", "public": True}

    with TestClient(api) as client:
        # Should work without any authentication
        response = client.get("/no-auth")
        assert response.status_code == 200
        data = response.json()
        assert data["public"] is True


# --- Combined get_guards() and get_auth() E2E Tests ---


def test_get_guards_and_auth_together_e2e():
    """Test that both get_guards() and get_auth() work together."""
    api = BoltAPI()

    @api.view("/combined")
    class CombinedView(APIView):
        guards = [IsAuthenticated()]
        auth = [JWTAuthentication(secret="test-secret")]

        def get_guards(self):
            # Allow anonymous for GET
            action = getattr(self, "action", None)
            if action == "get":
                return [AllowAny()]
            return [IsAuthenticated()]

        def get_auth(self):
            # No auth for GET, JWT for POST
            action = getattr(self, "action", None)
            if action == "get":
                return None
            return [JWTAuthentication(secret="test-secret")]

        async def get(self, request) -> dict:
            return {"message": "public read", "public": True}

        async def post(self, request) -> dict:
            return {"message": "protected write", "user_id": request.get("auth", {}).get("user_id")}

    with TestClient(api) as client:
        # GET should work without auth (AllowAny + no auth)
        response = client.get("/combined")
        assert response.status_code == 200
        data = response.json()
        assert data["public"] is True

        # POST should require JWT auth
        response = client.post("/combined", json={})
        assert response.status_code == 401

        # POST with JWT should work
        token = create_jwt_token(user_id=999, secret="test-secret")
        response = client.post("/combined", json={}, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 999


def test_get_guards_and_auth_with_permissions_e2e():
    """Test get_guards() with permission-based guards."""
    api = BoltAPI()

    @api.view("/permission-based")
    class PermissionView(APIView):
        guards = [IsAuthenticated()]

        def get_guards(self):
            # Require specific permission
            return [IsAuthenticated(), HasPermission("articles.edit")]

        auth = [JWTAuthentication(secret="test-secret")]

        async def get(self, request) -> dict:
            return {"message": "permission required", "user_id": request.get("auth", {}).get("user_id")}

    with TestClient(api) as client:
        # Without token - 401
        response = client.get("/permission-based")
        assert response.status_code == 401

        # With token but no permission - 403
        token = create_jwt_token(user_id=111, permissions=[], secret="test-secret")
        response = client.get("/permission-based", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

        # With token and permission - 200
        token = create_jwt_token(user_id=111, permissions=["articles.edit"], secret="test-secret")
        response = client.get("/permission-based", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 111


def test_get_guards_inheritance_e2e():
    """Test that subclasses can override get_guards() and it works in requests."""
    api = BoltAPI()

    class BaseView(APIView):
        guards = [IsAuthenticated()]
        auth = [JWTAuthentication(secret="test-secret")]

    class DerivedView(BaseView):
        def get_guards(self):
            # Override to allow anonymous
            return [AllowAny()]

        async def get(self, request) -> dict:
            return {"message": "derived", "public": True}

    @api.view("/inherited")
    class TestView(DerivedView):
        pass

    with TestClient(api) as client:
        # Should work without token (AllowAny from get_guards())
        response = client.get("/inherited")
        assert response.status_code == 200
        data = response.json()
        assert data["public"] is True


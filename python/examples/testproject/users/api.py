from django_bolt import BoltAPI, JSON, action
from django_bolt.views import APIView, ViewSet, ModelViewSet
from django_bolt.exceptions import HTTPException, NotFound
from asgiref.sync import sync_to_async
import msgspec
from .models import User
from typing import List
api = BoltAPI(prefix="/users")


# ============================================================================
# Schemas
# ============================================================================

class UserFull(msgspec.Struct):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool


class UserMini(msgspec.Struct):
    id: int
    username: str


class UserCreate(msgspec.Struct):
    username: str
    email: str
    first_name: str = ""
    last_name: str = ""


class UserUpdate(msgspec.Struct):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None


# ============================================================================
# Function-Based Views (Original, for benchmarking)
# ============================================================================

@api.get("/")
async def users_root():
    return {"ok": True}


@api.get("/full10")
async def list_full_10() -> List[UserFull]:
    # Optimized: only fetch needed fields instead of all()
    return User.objects.only("id", "username", "email", "first_name", "last_name", "is_active")[:10]


@api.get("/mini10")
async def list_mini_10() -> List[UserMini]:
    # Already optimized: only() fetches just id and username
    return User.objects.only("id", "username")[:10]




# ============================================================================
# Unified ViewSet (DRF-style with api.viewset())
# ============================================================================
@api.viewset("/users")
class UnifiedUserViewSet(ModelViewSet):
    """
    Unified ViewSet demonstrating the new pattern inspired by Litestar/DRF.

    Single ViewSet handles both list and detail views with:
    - DRF-style action methods (list, retrieve, create, update, partial_update, destroy)
    - Automatic route generation with api.viewset()
    - Different serializers for list vs detail (list_serializer_class)
    - Type-driven serialization
    """

    queryset = User.objects.all()
    serializer_class = UserFull  # Used for detail views
    list_serializer_class = UserMini  # Used for list views
    lookup_field = 'id'

    # Custom actions using @action decorator
    @action(methods=["POST"], detail=True)
    async def activate(self, request, id: int):
        """Custom action: Activate a user. POST /users/unified-users/{id}/activate"""
        try:
            user = await User.objects.aget(id=id)
            user.is_active = True
            await user.asave()
            return {"user_id": id, "activated": True, "is_active": True}
        except User.DoesNotExist:
            raise NotFound(detail=f"User {id} not found")

    @action(methods=["GET"], detail=False)
    async def search(self, request, query: str):
        """Custom action: Search users by username. GET /users/unified-users/search"""
        users = []
        async for user in User.objects.filter(username__icontains=query)[:10]:
            users.append(UserMini(id=user.id, username=user.username))
        return {"query": query, "results": users}



@api.view("/cbv-mini10")
class UserBenchViewSet(APIView):
    """Benchmarking endpoints using class-based views."""

    async def get(self, request):
        """List first 10 users (CBV version for benchmarking)."""
        users = []
        async for user in User.objects.only("id", "username")[:10]:
            users.append(UserMini(id=user.id, username=user.username))
        return users



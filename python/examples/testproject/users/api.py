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


@api.view("/cbv-mini10")
class UserBenchViewSet(APIView):
    """Benchmarking endpoints using class-based views."""

    async def get(self, request):
        """List first 10 users (CBV version for benchmarking)."""
        users = []
        async for user in User.objects.only("id", "username")[:10]:
            users.append(UserMini(id=user.id, username=user.username))
        return users


@api.view("/cbv-full10")
class UserFull10ViewSet(APIView):
    """List first 10 users (CBV version for benchmarking)."""

    async def get(self, request):
        """List first 10 users (CBV version for benchmarking)."""
        users = []
        async for user in User.objects.only("id", "username", "email", "first_name", "last_name", "is_active")[:10]:
            users.append(UserFull(id=user.id, username=user.username, email=user.email, first_name=user.first_name, last_name=user.last_name, is_active=user.is_active))
        return users

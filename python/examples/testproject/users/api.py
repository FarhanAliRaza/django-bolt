from django_bolt import BoltAPI, JSON
from django_bolt.views import APIView, ViewSet, ModelViewSet
from django_bolt.exceptions import HTTPException, NotFound
from asgiref.sync import sync_to_async
import msgspec
from .models import User

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
async def list_full_10() -> list[UserFull]:
    # Optimized: only fetch needed fields instead of all()
    return User.objects.only("id", "username", "email", "first_name", "last_name", "is_active")[:10]


@api.get("/mini10")
async def list_mini_10() -> list[UserMini]:
    # Already optimized: only() fetches just id and username
    return User.objects.only("id", "username")[:10]


# ============================================================================
# Class-Based Views (APIView)
# ============================================================================

class UserStatsView(APIView):
    """Simple APIView for user statistics."""

    async def get(self, request):
        """Get user statistics."""
        total_users = await User.objects.acount()
        active_users = await User.objects.filter(is_active=True).acount()

        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users
        }


api.view("/stats", UserStatsView, methods=["GET"])


# ============================================================================
# Class-Based Views (ViewSet)
# ============================================================================

class UserViewSet(ViewSet):
    """ViewSet for complete CRUD operations on users."""

    queryset = User.objects.all()
    serializer_class = UserFull
    lookup_field = 'id'

    async def get(self, request, user_id: int):
        """Retrieve a single user by ID."""
        try:
            user = await User.objects.aget(id=user_id)
            return UserFull(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active
            )
        except User.DoesNotExist:
            raise NotFound(detail=f"User {user_id} not found")

    async def post(self, request, data: UserCreate):
        """Create a new user."""
        # Check if username exists
        exists = await User.objects.filter(username=data.username).aexists()
        if exists:
            raise HTTPException(
                status_code=400,
                detail=f"Username '{data.username}' already exists"
            )

        user = await User.objects.acreate(
            username=data.username,
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name
        )

        return UserFull(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )

    async def put(self, request, user_id: int, data: UserUpdate):
        """Update a user (full update)."""
        try:
            user = await User.objects.aget(id=user_id)
        except User.DoesNotExist:
            raise NotFound(detail=f"User {user_id} not found")

        # Update fields
        if data.email is not None:
            user.email = data.email
        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        if data.is_active is not None:
            user.is_active = data.is_active

        await user.asave()

        return UserFull(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )

    async def patch(self, request, user_id: int, data: UserUpdate):
        """Partially update a user."""
        try:
            user = await User.objects.aget(id=user_id)
        except User.DoesNotExist:
            raise NotFound(detail=f"User {user_id} not found")

        # Only update provided fields
        if data.email is not None:
            user.email = data.email
        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        if data.is_active is not None:
            user.is_active = data.is_active

        await user.asave()

        return UserFull(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )

    async def delete(self, request, user_id: int):
        """Delete a user."""
        try:
            user = await User.objects.aget(id=user_id)
            await user.adelete()
            return {"deleted": True, "user_id": user_id}
        except User.DoesNotExist:
            raise NotFound(detail=f"User {user_id} not found")

    # Custom actions
    @api.post("/cbv-users/{user_id}/activate")
    async def activate(self, request, user_id: int):
        """Custom action: Activate a user."""
        try:
            user = await User.objects.aget(id=user_id)
            user.is_active = True
            await user.asave()
            return {"user_id": user_id, "activated": True, "is_active": True}
        except User.DoesNotExist:
            raise NotFound(detail=f"User {user_id} not found")

    @api.post("/cbv-users/{user_id}/deactivate")
    async def deactivate(self, request, user_id: int):
        """Custom action: Deactivate a user."""
        try:
            user = await User.objects.aget(id=user_id)
            user.is_active = False
            await user.asave()
            return {"user_id": user_id, "deactivated": True, "is_active": False}
        except User.DoesNotExist:
            raise NotFound(detail=f"User {user_id} not found")

    @api.get("/cbv-users/search")
    async def search(self, request, query: str):
        """Custom action: Search users by username."""
        users = []
        async for user in User.objects.filter(username__icontains=query)[:10]:
            users.append(UserMini(id=user.id, username=user.username))
        return {"query": query, "results": users}


# Register the ViewSet
api.view("/cbv-users/{user_id}", UserViewSet, methods=["GET", "POST", "PUT", "PATCH", "DELETE"])


# ============================================================================
# Class-Based Views (List ViewSet)
# ============================================================================

class UserListViewSet(ViewSet):
    """ViewSet for listing users with filtering."""

    async def get(self, request, active: bool | None = None, limit: int = 100):
        """List users with optional filtering."""
        queryset = User.objects.all()

        if active is not None:
            queryset = queryset.filter(is_active=active)

        queryset = queryset[:limit]

        users = []
        async for user in queryset:
            users.append(UserMini(id=user.id, username=user.username))

        return {"count": len(users), "users": users}


api.view("/cbv-users", UserListViewSet, methods=["GET"])


# ============================================================================
# Unified ViewSet (DRF-style with api.viewset())
# ============================================================================

class UnifiedUserViewSet(ViewSet):
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

    async def list(self, request, active: bool | None = None, limit: int = 100) -> list[UserMini]:
        """List users with optional filtering."""
        qs = User.objects.all()

        if active is not None:
            qs = qs.filter(is_active=active)

        qs = qs[:limit]

        # Serialize using list_serializer_class (UserMini)
        users = []
        async for user in qs:
            users.append(UserMini(id=user.id, username=user.username))

        return users

    async def retrieve(self, request, id: int) -> UserFull:
        """Retrieve a single user by ID."""
        try:
            user = await User.objects.aget(id=id)
            return UserFull(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active
            )
        except User.DoesNotExist:
            raise NotFound(detail=f"User {id} not found")

    async def create(self, request, data: UserCreate) -> UserFull:
        """Create a new user."""
        # Check if username exists
        exists = await User.objects.filter(username=data.username).aexists()
        if exists:
            raise HTTPException(
                status_code=400,
                detail=f"Username '{data.username}' already exists"
            )

        user = await User.objects.acreate(
            username=data.username,
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name
        )

        return UserFull(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )

    async def update(self, request, id: int, data: UserUpdate) -> UserFull:
        """Update a user (full update)."""
        try:
            user = await User.objects.aget(id=id)
        except User.DoesNotExist:
            raise NotFound(detail=f"User {id} not found")

        # Update fields
        if data.email is not None:
            user.email = data.email
        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        if data.is_active is not None:
            user.is_active = data.is_active

        await user.asave()

        return UserFull(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )

    async def partial_update(self, request, id: int, data: UserUpdate) -> UserFull:
        """Partially update a user."""
        try:
            user = await User.objects.aget(id=id)
        except User.DoesNotExist:
            raise NotFound(detail=f"User {id} not found")

        # Only update provided fields
        if data.email is not None:
            user.email = data.email
        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        if data.is_active is not None:
            user.is_active = data.is_active

        await user.asave()

        return UserFull(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )

    async def destroy(self, request, id: int):
        """Delete a user."""
        try:
            user = await User.objects.aget(id=id)
            await user.adelete()
            return {"deleted": True, "user_id": id}
        except User.DoesNotExist:
            raise NotFound(detail=f"User {id} not found")

    # Custom actions still work!
    @api.post("/unified-users/{id}/activate")
    async def activate(self, request, id: int):
        """Custom action: Activate a user."""
        try:
            user = await User.objects.aget(id=id)
            user.is_active = True
            await user.asave()
            return {"user_id": id, "activated": True, "is_active": True}
        except User.DoesNotExist:
            raise NotFound(detail=f"User {id} not found")

    @api.get("/unified-users/search")
    async def search(self, request, query: str):
        """Custom action: Search users by username."""
        users = []
        async for user in User.objects.filter(username__icontains=query)[:10]:
            users.append(UserMini(id=user.id, username=user.username))
        return {"query": query, "results": users}


# Register the unified ViewSet - automatically generates all CRUD routes!
# This single line replaces the need for separate list and detail ViewSets
api.viewset("/unified-users", UnifiedUserViewSet)
# Auto-generates:
# GET    /users/unified-users          -> list()
# POST   /users/unified-users          -> create()
# GET    /users/unified-users/{id}     -> retrieve()
# PUT    /users/unified-users/{id}     -> update()
# PATCH  /users/unified-users/{id}     -> partial_update()
# DELETE /users/unified-users/{id}     -> destroy()
# Plus custom actions: activate, search


# ============================================================================
# Benchmark Endpoints (Class-Based Views)
# ============================================================================

class UserBenchViewSet(ViewSet):
    """Benchmarking endpoints using class-based views."""

    async def get(self, request):
        """List first 10 users (CBV version for benchmarking)."""
        users = []
        async for user in User.objects.only("id", "username")[:10]:
            users.append(UserMini(id=user.id, username=user.username))
        return users


api.view("/cbv-mini10", UserBenchViewSet, methods=["GET"])


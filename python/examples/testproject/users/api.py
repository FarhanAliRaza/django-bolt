from django_bolt import BoltAPI, JSON, action
from django_bolt.views import APIView, ViewSet, ModelViewSet
from django_bolt.exceptions import HTTPException, NotFound
from django_bolt.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    CursorPagination,
    paginate,
)
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
        print("get", dir(request), request)
        async for user in User.objects.only("id", "username", "email", "first_name", "last_name", "is_active")[:10]:
            users.append(UserFull(id=user.id, username=user.username, email=user.email, first_name=user.first_name, last_name=user.last_name, is_active=user.is_active))
        return users


# ============================================================================
# Pagination Examples
# ============================================================================

# 1. Functional View with PageNumberPagination
@api.get("/paginated")
@paginate(PageNumberPagination)
async def list_users_paginated() -> List[UserMini]:
    """
    List users with page number pagination.

    Query params:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 100, max: 1000)

    Example: GET /users/paginated?page=2&page_size=20
    """
    return User.objects.only("id", "username")


# 2. Functional View with LimitOffsetPagination
@api.get("/paginated-offset")
@paginate(LimitOffsetPagination)
async def list_users_offset(request) -> List[UserMini]:
    """
    List users with limit-offset pagination.

    Query params:
        - limit: Number of items (default: 100, max: 1000)
        - offset: Starting position (default: 0)

    Example: GET /users/paginated-offset?limit=20&offset=40
    """
    return User.objects.only("id", "username")


# 3. Functional View with CursorPagination
@api.get("/paginated-cursor")
@paginate(CursorPagination)
async def list_users_cursor(request) -> List[UserMini]:
    """
    List users with cursor-based pagination.

    Query params:
        - cursor: Opaque cursor string (optional)
        - page_size: Items per page (default: 100, max: 1000)

    Example: GET /users/paginated-cursor?page_size=20&cursor=eyJ2IjoxMDB9
    """
    return User.objects.only("id", "username")


# 4. Custom Pagination Class
class SmallPagePagination(PageNumberPagination):
    """Custom pagination with smaller page size"""
    page_size = 10
    max_page_size = 50


@api.get("/paginated-small")
@paginate(SmallPagePagination)
async def list_users_small_pages(request) -> List[UserMini]:
    """
    List users with custom small page size.

    Example: GET /users/paginated-small?page=2
    """
    return User.objects.only("id", "username")


# 5. Class-Based View (ViewSet) with Pagination
@api.viewset("/api-paginated")
class UserPaginatedViewSet(ViewSet):
    """
    ViewSet with automatic pagination on list action.

    Routes:
        - GET /users/api-paginated -> list (paginated)
        - GET /users/api-paginated/{id} -> retrieve (not paginated)

    Query params for list:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 20)
    """

    queryset = User.objects.only("id", "username", "email")
    pagination_class = PageNumberPagination

    async def list(self, request) -> List[UserMini]:
        """List all users with pagination."""
        qs = await self.get_queryset()

        # Apply pagination (returns PaginatedResponse if pagination_class is set)
        paginated = await self.paginate_queryset(qs)

        # If pagination is disabled, we'd need to manually convert queryset
        # But with pagination enabled, we get PaginatedResponse with items
        if hasattr(paginated, 'items'):
            # Convert items to UserMini schema
            paginated.items = [
                UserMini(id=user.id, username=user.username)
                async for user in paginated.items
            ]

        return paginated

    async def retrieve(self, request, id: int) -> UserFull:
        """Retrieve a single user by ID (not paginated)."""
        user = await self.get_object(id=id)
        return UserFull(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
        )


# 6. ModelViewSet with Pagination
@api.viewset("/model-paginated")
class UserModelPaginatedViewSet(ModelViewSet):
    """
    Full CRUD ModelViewSet with pagination on list action.

    Routes:
        - GET /users/model-paginated -> list (paginated)
        - POST /users/model-paginated -> create
        - GET /users/model-paginated/{id} -> retrieve
        - PUT /users/model-paginated/{id} -> update
        - PATCH /users/model-paginated/{id} -> partial_update
        - DELETE /users/model-paginated/{id} -> destroy

    Query params for list:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 25)
    """

    queryset = User.objects.all()
    serializer_class = UserFull
    list_serializer_class = UserMini
    pagination_class = SmallPagePagination

    # list(), retrieve(), create(), update(), partial_update(), destroy()
    # are all automatically implemented by ModelViewSet
    # Pagination is automatically applied to list() action

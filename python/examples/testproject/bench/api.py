from django_bolt import BoltAPI
from django_bolt.views import ViewSet
from django_bolt.exceptions import NotFound
import msgspec
from .models import BenchItem


api = BoltAPI(prefix="/bench")


# ============================================================================
# Schemas
# ============================================================================

class BenchItemSchema(msgspec.Struct):
    id: int
    name: str
    value: int
    description: str
    is_active: bool


class BenchItemCreate(msgspec.Struct):
    name: str
    value: int = 0
    description: str = ""
    is_active: bool = True


class BenchItemUpdate(msgspec.Struct):
    name: str | None = None
    value: int | None = None
    description: str | None = None
    is_active: bool | None = None


# ============================================================================
# Class-Based Views (ViewSet) for Full CRUD Benchmarking
# ============================================================================

class BenchItemViewSet(ViewSet):
    """ViewSet for CRUD operations on BenchItem (no unique constraints)."""

    queryset = BenchItem.objects.all()
    serializer_class = BenchItemSchema

    async def get(self, request, item_id: int):
        """Retrieve a single item by ID."""
        try:
            item = await BenchItem.objects.aget(id=item_id)
            return BenchItemSchema(
                id=item.id,
                name=item.name,
                value=item.value,
                description=item.description,
                is_active=item.is_active
            )
        except BenchItem.DoesNotExist:
            raise NotFound(detail=f"BenchItem {item_id} not found")

    async def post(self, request, data: BenchItemCreate):
        """Create a new item."""
        item = await BenchItem.objects.acreate(
            name=data.name,
            value=data.value,
            description=data.description,
            is_active=data.is_active
        )

        return BenchItemSchema(
            id=item.id,
            name=item.name,
            value=item.value,
            description=item.description,
            is_active=item.is_active
        )

    async def put(self, request, item_id: int, data: BenchItemUpdate):
        """Update an item (full update)."""
        try:
            item = await BenchItem.objects.aget(id=item_id)
        except BenchItem.DoesNotExist:
            raise NotFound(detail=f"BenchItem {item_id} not found")

        # Update all fields
        if data.name is not None:
            item.name = data.name
        if data.value is not None:
            item.value = data.value
        if data.description is not None:
            item.description = data.description
        if data.is_active is not None:
            item.is_active = data.is_active

        await item.asave()

        return BenchItemSchema(
            id=item.id,
            name=item.name,
            value=item.value,
            description=item.description,
            is_active=item.is_active
        )

    async def patch(self, request, item_id: int, data: BenchItemUpdate):
        """Partially update an item."""
        try:
            item = await BenchItem.objects.aget(id=item_id)
        except BenchItem.DoesNotExist:
            raise NotFound(detail=f"BenchItem {item_id} not found")

        # Only update provided fields
        if data.name is not None:
            item.name = data.name
        if data.value is not None:
            item.value = data.value
        if data.description is not None:
            item.description = data.description
        if data.is_active is not None:
            item.is_active = data.is_active

        await item.asave()

        return BenchItemSchema(
            id=item.id,
            name=item.name,
            value=item.value,
            description=item.description,
            is_active=item.is_active
        )

    async def delete(self, request, item_id: int):
        """Delete an item."""
        try:
            item = await BenchItem.objects.aget(id=item_id)
            await item.adelete()
            return {"deleted": True, "item_id": item_id}
        except BenchItem.DoesNotExist:
            raise NotFound(detail=f"BenchItem {item_id} not found")

    # Custom actions
    @api.post("/bench-items/{item_id}/increment")
    async def increment(self, request, item_id: int):
        """Custom action: Increment item value."""
        try:
            item = await BenchItem.objects.aget(id=item_id)
            item.value += 1
            await item.asave()
            return {"item_id": item_id, "value": item.value, "incremented": True}
        except BenchItem.DoesNotExist:
            raise NotFound(detail=f"BenchItem {item_id} not found")

    @api.post("/bench-items/{item_id}/toggle")
    async def toggle(self, request, item_id: int):
        """Custom action: Toggle is_active status."""
        try:
            item = await BenchItem.objects.aget(id=item_id)
            item.is_active = not item.is_active
            await item.asave()
            return {"item_id": item_id, "is_active": item.is_active, "toggled": True}
        except BenchItem.DoesNotExist:
            raise NotFound(detail=f"BenchItem {item_id} not found")

    @api.get("/bench-items/search")
    async def search(self, request, query: str):
        """Custom action: Search items by name."""
        items = []
        async for item in BenchItem.objects.filter(name__icontains=query)[:10]:
            items.append(BenchItemSchema(
                id=item.id,
                name=item.name,
                value=item.value,
                description=item.description,
                is_active=item.is_active
            ))
        return {"query": query, "count": len(items), "results": items}


# Register the ViewSet
api.view("/bench-items/{item_id}", BenchItemViewSet, methods=["GET", "POST", "PUT", "PATCH", "DELETE"])


# ============================================================================
# List ViewSet
# ============================================================================

class BenchItemListViewSet(ViewSet):
    """ViewSet for listing items with filtering."""

    async def get(self, request, active: bool | None = None, limit: int = 100):
        """List items with optional filtering."""
        queryset = BenchItem.objects.all()

        if active is not None:
            queryset = queryset.filter(is_active=active)

        queryset = queryset[:limit]

        items = []
        async for item in queryset:
            items.append(BenchItemSchema(
                id=item.id,
                name=item.name,
                value=item.value,
                description=item.description,
                is_active=item.is_active
            ))

        return {"count": len(items), "items": items}


api.view("/bench-items", BenchItemListViewSet, methods=["GET"])

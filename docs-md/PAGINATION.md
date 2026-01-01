# Pagination

Django-Bolt provides built-in pagination support that works seamlessly with both functional and class-based views. It leverages Django's Paginator under the hood while integrating with Bolt's parameter extraction and serialization systems.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Pagination Classes](#pagination-classes)
  - [PageNumberPagination](#pagenumberpagination)
  - [LimitOffsetPagination](#limitoffsetpagination)
  - [CursorPagination](#cursorpagination)
- [Using with Functional Views](#using-with-functional-views)
- [Using with Class-Based Views](#using-with-class-based-views)
- [Custom Pagination Classes](#custom-pagination-classes)
- [Response Format](#response-format)
- [Best Practices](#best-practices)

## Overview

Pagination divides large datasets into smaller, manageable pages, improving API performance and user experience. Django-Bolt provides three built-in pagination styles:

1. **PageNumberPagination** - Page number-based (`?page=2&page_size=20`)
2. **LimitOffsetPagination** - SQL-style limit/offset (`?limit=20&offset=40`)
3. **CursorPagination** - Cursor-based for large datasets (`?cursor=eyJ2IjoxMDB9`)

### Quick Comparison

| Feature           | PageNumber             | LimitOffset               | Cursor                          |
| ----------------- | ---------------------- | ------------------------- | ------------------------------- |
| **Use Case**      | General purpose        | Fine-grained control      | Large datasets, real-time feeds |
| **Performance**   | Good                   | Good                      | Excellent                       |
| **Jump to page**  | ✅ Yes                 | ✅ Yes                    | ❌ No (sequential only)         |
| **Total count**   | ✅ Yes                 | ✅ Yes                    | ❌ No (for performance)         |
| **User-friendly** | ✅✅✅ Very            | ✅✅ Moderate             | ✅ Less intuitive               |
| **Query params**  | `page`, `page_size`    | `limit`, `offset`         | `cursor`, `page_size`           |
| **Best for**      | Standard APIs, web UIs | SQL-like queries, exports | Infinite scroll, activity feeds |

## Quick Start

### Functional View

```python
from django_bolt import BoltAPI, paginate, PageNumberPagination
from myapp.models import Article

api = BoltAPI()

@api.get("/articles")
@paginate(PageNumberPagination)
async def list_articles(request):
    return Article.objects.all()
```

### Class-Based View (ViewSet)

```python
from django_bolt import BoltAPI, ViewSet, PageNumberPagination
from myapp.models import Article
import msgspec

class ArticleSchema(msgspec.Struct):
    id: int
    title: str

@api.viewset("/articles")
class ArticleViewSet(ViewSet):
    queryset = Article.objects.all()
    pagination_class = PageNumberPagination

    async def list(self, request):
        qs = await self.get_queryset()
        return await self.paginate_queryset(qs)
```

### Usage

```bash
# Default page (page 1, 100 items)
curl http://localhost:8000/articles

# Specific page
curl http://localhost:8000/articles?page=2

# Custom page size
curl http://localhost:8000/articles?page=2&page_size=20
```

## Pagination Classes

### PageNumberPagination

Standard page number-based pagination. Best for most use cases.

**Query Parameters:**

- `page` - Page number (default: 1)
- `page_size` - Items per page (optional, default: 100)

**Configuration:**

```python
from django_bolt.pagination import PageNumberPagination

class MyPagination(PageNumberPagination):
    page_size = 50                    # Default items per page
    max_page_size = 200               # Maximum allowed page size
    page_size_query_param = "page_size"  # Query param name for page size
```

**Response Format:**

```json
{
  "items": [...],
  "total": 500,
  "page": 2,
  "page_size": 50,
  "total_pages": 10,
  "has_next": true,
  "has_previous": true,
  "next_page": 3,
  "previous_page": 1
}
```

**Example:**

```python
@api.get("/users")
@paginate(PageNumberPagination)
async def list_users(request):
    return User.objects.all()

# GET /users?page=3&page_size=25
```

### LimitOffsetPagination

SQL-style limit/offset pagination. Useful for APIs that need fine-grained control over result sets.

**Query Parameters:**

- `limit` - Number of items to return (default: 100)
- `offset` - Starting position (default: 0)

**Configuration:**

```python
from django_bolt.pagination import LimitOffsetPagination

class MyPagination(LimitOffsetPagination):
    page_size = 50        # Default limit
    max_page_size = 200   # Maximum allowed limit
```

**Response Format:**

```json
{
  "items": [...],
  "total": 500,
  "limit": 25,
  "offset": 50,
  "has_next": true,
  "has_previous": true
}
```

**Example:**

```python
@api.get("/articles")
@paginate(LimitOffsetPagination)
async def list_articles(request):
    return Article.objects.all()

# GET /articles?limit=25&offset=50
```

### CursorPagination

Cursor-based pagination for large datasets. Most efficient for sequential traversal as it doesn't require counting all records.

**Query Parameters:**

- `cursor` - Opaque cursor string (optional, for next/previous page)
- `page_size` - Items per page (optional, default: 100)

**Configuration:**

```python
from django_bolt.pagination import CursorPagination

class MyPagination(CursorPagination):
    page_size = 50                    # Default items per page
    max_page_size = 200               # Maximum allowed page size
    page_size_query_param = "page_size"  # Query param name for page size
    ordering = "-created_at"          # Ordering field (required for cursor)
```

**Response Format:**

```json
{
  "items": [...],
  "page_size": 50,
  "has_next": true,
  "has_previous": true,
  "next_cursor": "eyJ2IjoxNTB9",
  "previous_cursor": null,
  "total": 0
}
```

**Note:** Cursor pagination doesn't provide `total` count for performance reasons.

**Example:**

```python
@api.get("/events")
@paginate(CursorPagination)
async def list_events(request):
    return Event.objects.all()

# First page: GET /events?page_size=25
# Next page: GET /events?page_size=25&cursor=eyJ2IjoxNTB9
```

## Using with Functional Views

Use the `@paginate` decorator on any async function that returns a Django QuerySet or iterable.

### Basic Usage

```python
from django_bolt import BoltAPI, paginate, PageNumberPagination
from myapp.models import Product

api = BoltAPI()

@api.get("/products")
@paginate(PageNumberPagination)
async def list_products(request):
    """Returns paginated list of products"""
    return Product.objects.all()
```

### With Filtering

```python
@api.get("/products")
@paginate(PageNumberPagination)
async def list_products(request, category: str = None):
    """Returns paginated list of products, optionally filtered by category"""
    qs = Product.objects.all()

    if category:
        qs = qs.filter(category=category)

    return qs

# GET /products?category=electronics&page=2&page_size=20
```

### With Type Annotations

```python
from typing import List

class ProductSchema(msgspec.Struct):
    id: int
    name: str
    price: float

@api.get("/products")
@paginate(PageNumberPagination)
async def list_products(request) -> List[ProductSchema]:
    """Returns paginated list of products"""
    return Product.objects.all()
```

### With QuerySet Methods

Pagination works seamlessly with Django QuerySet methods like `.values()`, `.values_list()`, `.only()`, etc.:

```python
@api.get("/products/ids")
@paginate(PageNumberPagination)
async def list_product_ids(request):
    """Returns paginated list of product IDs only"""
    return Product.objects.values_list('id', 'name')

@api.get("/products/summary")
@paginate(PageNumberPagination)
async def list_products_summary(request):
    """Returns paginated dict items instead of model instances"""
    return Product.objects.values('id', 'name', 'price')

@api.get("/products/optimized")
@paginate(PageNumberPagination)
async def list_products_optimized(request):
    """Returns paginated products with query optimization"""
    return Product.objects.select_related('category').only(
        'id', 'name', 'category__name'
    )
```

## Using with Class-Based Views

### ViewSet with Pagination

```python
from django_bolt import BoltAPI, ViewSet, PageNumberPagination
from myapp.models import Article
import msgspec

class ArticleSchema(msgspec.Struct):
    id: int
    title: str
    content: str
    published_at: str

api = BoltAPI()

@api.viewset("/articles")
class ArticleViewSet(ViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSchema
    pagination_class = PageNumberPagination  # Enable pagination

    async def list(self, request):
        """List articles with pagination"""
        qs = await self.get_queryset()

        # Apply filtering (optional)
        qs = await self.filter_queryset(qs)

        # Apply pagination
        paginated = await self.paginate_queryset(qs)

        # Convert items to schema
        if hasattr(paginated, 'items'):
            paginated.items = [
                ArticleSchema.from_model(article)
                async for article in paginated.items
            ]

        return paginated

    async def filter_queryset(self, queryset):
        """Optional: Add filtering logic"""
        # Get query params
        status = self.request.get('query', {}).get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Get ordering
        ordering = self.request.get('query', {}).get('ordering', '-published_at')
        queryset = queryset.order_by(ordering)

        return queryset
```

### ModelViewSet with Pagination

```python
from django_bolt import BoltAPI, ModelViewSet, PageNumberPagination
from myapp.models import Article
import msgspec

class ArticleFullSchema(msgspec.Struct):
    id: int
    title: str
    content: str
    published_at: str

class ArticleListSchema(msgspec.Struct):
    id: int
    title: str

@api.viewset("/articles")
class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleFullSchema
    list_serializer_class = ArticleListSchema  # Different schema for list
    pagination_class = PageNumberPagination

    # list(), retrieve(), create(), update(), partial_update(), destroy()
    # are all automatically implemented by ModelViewSet
    # Pagination is automatically applied to list() action
```

### Without Pagination

Set `pagination_class = None` to disable pagination:

```python
@api.viewset("/articles")
class ArticleViewSet(ViewSet):
    queryset = Article.objects.all()
    pagination_class = None  # Disable pagination

    async def list(self, request):
        qs = await self.get_queryset()
        return await self.paginate_queryset(qs)  # Returns queryset unchanged
```

### Using @paginate Decorator with ViewSets

You can also use the `@paginate` decorator directly on ViewSet methods:

```python
from django_bolt import BoltAPI, ViewSet, paginate, LimitOffsetPagination

@api.viewset("/articles")
class ArticleViewSet(ViewSet):
    queryset = Article.objects.all()

    @paginate(LimitOffsetPagination)
    async def list(self, request):
        """List method with pagination decorator"""
        return await self.get_queryset()

    @paginate(PageNumberPagination)
    async def search(self, request, query: str):
        """Custom search action with different pagination"""
        qs = await self.get_queryset()
        return qs.filter(title__icontains=query)

# GET /articles?limit=20&offset=0
# GET /articles/search?query=django&page=2
```

This approach allows you to use different pagination classes for different ViewSet methods.

## Custom Pagination Classes

Create custom pagination classes by subclassing `PaginationBase`:

### Example: Custom Page Size

```python
from django_bolt.pagination import PageNumberPagination

class SmallPagePagination(PageNumberPagination):
    """Pagination with smaller default page size"""
    page_size = 10
    max_page_size = 50
    page_size_query_param = "per_page"  # Custom query param name

@api.get("/items")
@paginate(SmallPagePagination)
async def list_items(request):
    return Item.objects.all()

# GET /items?page=2&per_page=20
```

### Example: Dynamic Pagination Class

```python
class DynamicViewSet(ViewSet):
    queryset = Item.objects.all()

    def get_pagination_class(self):
        """Dynamically select pagination class"""
        # Check user permissions, request params, etc.
        if self.action == "list":
            return PageNumberPagination
        return None  # No pagination for other actions

    @property
    def pagination_class(self):
        return self.get_pagination_class()
```

### Example: Custom Pagination Logic

```python
from django_bolt.pagination import PaginationBase, PaginatedResponse

class CustomPagination(PaginationBase):
    page_size = 20

    async def get_page_params(self, request):
        """Extract custom pagination params"""
        query = request.get('query', {})
        return {
            'custom_param': query.get('custom_param', 'default')
        }

    async def paginate_queryset(self, queryset, request, **params):
        """Custom pagination logic"""
        page_params = await self.get_page_params(request)

        # Your custom logic here
        items = await self._evaluate_queryset_slice(queryset[:self.page_size])
        total = await self._get_queryset_count(queryset)

        return PaginatedResponse(
            items=items,
            total=total,
            page_size=self.page_size,
            has_next=len(items) == self.page_size,
            has_previous=False,
        )
```

## Response Format

All pagination classes return a `PaginatedResponse` object with the following structure:

```python
class PaginatedResponse(msgspec.Struct):
    items: List[T]              # List of paginated items
    total: int                  # Total number of items across all pages

    # PageNumberPagination fields
    page: Optional[int]         # Current page number
    page_size: Optional[int]    # Items per page
    total_pages: Optional[int]  # Total number of pages
    has_next: bool              # Whether there is a next page
    has_previous: bool          # Whether there is a previous page
    next_page: Optional[int]    # Next page number
    previous_page: Optional[int] # Previous page number

    # LimitOffsetPagination fields
    limit: Optional[int]        # Number of items returned
    offset: Optional[int]       # Starting position

    # CursorPagination fields
    next_cursor: Optional[str]  # Cursor for next page
    previous_cursor: Optional[str] # Cursor for previous page
```

## Best Practices

### 1. Choose the Right Pagination Style

- **PageNumberPagination**: Default choice for most APIs. Easy to understand and use.
- **LimitOffsetPagination**: Use when clients need precise control over result sets.
- **CursorPagination**: Use for large datasets or real-time feeds where performance is critical.

### 2. Set Reasonable Limits

Always set `max_page_size` to prevent abuse:

```python
class MyPagination(PageNumberPagination):
    page_size = 50
    max_page_size = 200  # Prevent clients from requesting too many items
```

### 3. Optimize QuerySets

Use `.only()`, `.select_related()`, and `.prefetch_related()` to optimize database queries:

```python
@api.get("/articles")
@paginate(PageNumberPagination)
async def list_articles(request):
    return Article.objects.select_related('author').only(
        'id', 'title', 'author__name'
    )
```

### 4. Use Different Serializers for List vs Detail

```python
class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleFullSchema      # For retrieve, create, update
    list_serializer_class = ArticleListSchema # For list (lighter)
    pagination_class = PageNumberPagination
```

### 5. Add Filtering and Ordering

Combine pagination with filtering for powerful APIs:

```python
@api.viewset("/articles")
class ArticleViewSet(ViewSet):
    queryset = Article.objects.all()
    pagination_class = PageNumberPagination

    async def filter_queryset(self, queryset):
        query_params = self.request.get('query', {})

        # Filtering
        if status := query_params.get('status'):
            queryset = queryset.filter(status=status)

        # Searching
        if search := query_params.get('search'):
            queryset = queryset.filter(title__icontains=search)

        # Ordering
        if ordering := query_params.get('ordering'):
            queryset = queryset.order_by(ordering)

        return queryset

# GET /articles?status=published&search=django&ordering=-published_at&page=2
```

### 6. Document Your Pagination

Always document pagination parameters in your API docstrings:

```python
@api.get("/articles")
@paginate(PageNumberPagination)
async def list_articles(request, status: str = None):
    """
    List articles with pagination.

    Query Parameters:
        status: Filter by status (published, draft)
        page: Page number (default: 1)
        page_size: Items per page (default: 100, max: 1000)
        ordering: Order by field (e.g., -published_at)

    Returns:
        PaginatedResponse with list of articles
    """
    qs = Article.objects.all()
    if status:
        qs = qs.filter(status=status)
    return qs
```

### 7. Handle Empty Results Gracefully

All pagination classes handle empty results automatically:

```python
# Empty results return valid pagination response:
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 100,
  "total_pages": 0,
  "has_next": false,
  "has_previous": false
}
```

### 8. Use Cursor Pagination for Large Datasets

For very large datasets or real-time feeds, use cursor pagination:

```python
class EventPagination(CursorPagination):
    page_size = 100
    ordering = "-created_at"  # Must specify ordering field

@api.get("/events")
@paginate(EventPagination)
async def list_events(request):
    return Event.objects.all()
```

### 9. Test Your Pagination

Always test edge cases:

- Empty results
- Single page of results
- Last page
- Invalid page numbers
- Page size limits
- Offset beyond total results
- Invalid cursors

Django-Bolt includes comprehensive pagination tests in [test_pagination.py](../python/tests/test_pagination.py) with **46 test cases** covering:

- All three pagination classes with real Django ORM integration
- Edge cases (empty results, single result, invalid inputs)
- ViewSet integration
- Django QuerySet features (`.values()`, `.only()`, `.select_related()`, etc.)

```python
# Example tests
from django_bolt.testing import TestClient

async def test_pagination_empty_results():
    response = await client.get("/articles?page=1")
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0

async def test_pagination_invalid_page():
    response = await client.get("/articles?page=999")
    assert response.status_code == 200
    # Clamps to last valid page
    assert response.json()["page"] <= response.json()["total_pages"]

async def test_limit_offset_max_enforcement():
    response = await client.get("/articles?limit=10000")
    assert response.status_code == 200
    # Clamped to max_page_size
    assert response.json()["limit"] <= 1000
```

### 10. Consider Performance

- Use `.count()` judiciously (it's expensive on large tables)
- Consider caching total counts for very large datasets
- Use cursor pagination for sequential access patterns
- Add database indexes on fields used in `order_by()`

## Examples

See the [example/users/api.py](../python/example/users/api.py) file for complete working examples of all pagination styles.

## API Reference

For detailed API reference, see the [pagination.py](../python/django_bolt/pagination.py) source code.

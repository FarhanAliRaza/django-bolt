---
icon: lucide/list
---

# Pagination

Django-Bolt provides three pagination styles for handling large datasets efficiently.

## PageNumber Pagination

Classic page-based pagination:

```python
from django_bolt import BoltAPI
from django_bolt.pagination import PageNumberPagination, paginate

api = BoltAPI()

class ArticlePagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100

@api.get("/articles")
@paginate(ArticlePagination)
async def list_articles(request):
    return Article.objects.all()
```

Response:

```json
{
  "count": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8,
  "next": "/articles?page=2",
  "previous": null,
  "items": [...]
}
```

## LimitOffset Pagination

Flexible offset-based pagination:

```python
from django_bolt.pagination import LimitOffsetPagination, paginate

class ArticlePagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100

@api.get("/articles")
@paginate(ArticlePagination)
async def list_articles(request):
    return Article.objects.all()
```

Query: `/articles?limit=10&offset=20`

## Cursor Pagination

Efficient pagination for large datasets:

```python
from django_bolt.pagination import CursorPagination, paginate

class ArticlePagination(CursorPagination):
    page_size = 20
    ordering = "-created_at"

@api.get("/articles")
@paginate(ArticlePagination)
async def list_articles(request):
    return Article.objects.all()
```

## With Serializers

Pagination integrates with Bolt serializers for automatic field extraction:

```python
from django_bolt.serialization import Serializer

class ArticleSerializer(Serializer):
    id: int
    title: str
    author_name: str  # From related model

class ArticlePagination(PageNumberPagination):
    page_size = 20
    serializer_class = ArticleSerializer

@api.get("/articles")
@paginate(ArticlePagination)
async def list_articles(request):
    return Article.objects.select_related("author").all()
```

## Performance Considerations

### Avoiding N+1 Queries

Serialization happens after fetching items. If your serializer accesses related fields, use `select_related()` or `prefetch_related()` to avoid N+1 queries:

```python
# Bad - N+1 queries when serializer accesses article.author
@api.get("/articles")
@paginate(ArticlePagination)
async def list_articles(request):
    return Article.objects.all()

# Good - single query with JOIN
@api.get("/articles")
@paginate(ArticlePagination)
async def list_articles(request):
    return Article.objects.select_related("author").all()

# Good - prefetch for many-to-many
@api.get("/articles")
@paginate(ArticlePagination)
async def list_articles(request):
    return Article.objects.prefetch_related("tags").all()
```

### Cursor Pagination for Large Datasets

For tables with millions of rows, prefer `CursorPagination` over `PageNumberPagination`. Cursor pagination uses indexed columns for efficient seeking, while page number pagination requires counting total rows.

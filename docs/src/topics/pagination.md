---
icon: lucide/list
---

# Pagination

Django-Bolt provides three pagination styles for handling large datasets efficiently.

## PageNumber Pagination

Classic page-based pagination:

```python
from django_bolt import BoltAPI, PageNumberPagination, paginate

api = BoltAPI()

class ArticlePagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100
    page_size_query_param = "page_size"  # Allow client to customize

@api.get("/articles")
@paginate(ArticlePagination)
async def list_articles(request) -> list[ArticleSerializer]:
    return Article.objects.all()
```

Response:

```json
{
  "count": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8,
  "has_next": true,
  "has_previous": false,
  "next_page": 2,
  "previous_page": null,
  "items": [...]
}
```

Query: `/articles?page=2&page_size=10`

## LimitOffset Pagination

Flexible offset-based pagination:

```python
from django_bolt import LimitOffsetPagination, paginate

@api.get("/articles", response_model=list[ArticleSerializer])
@paginate(LimitOffsetPagination)
async def list_articles(request):
    return Article.objects.all()
```

Query: `/articles?limit=10&offset=20`

Response includes `limit`, `offset`, `total`, `has_next`, `has_previous`.

## Cursor Pagination

Efficient pagination for large datasets and real-time feeds:

```python
from django_bolt import CursorPagination, paginate

class ArticlePagination(CursorPagination):
    page_size = 20
    ordering = "-created_at"  # Required: field to paginate by

@api.get("/articles")
@paginate(ArticlePagination)
async def list_articles(request) -> list[ArticleSerializer]:
    return Article.objects.all()
```

Query: `/articles?cursor=eyJ2IjoxMDB9`

## Specifying the Serializer

Two equivalent ways to specify which serializer to use:

```python
# Option 1: Return type annotation (recommended)
@api.get("/articles")
@paginate(ArticlePagination)
async def list_articles(request) -> list[ArticleSerializer]:
    return Article.objects.all()

# Option 2: response_model parameter
@api.get("/articles", response_model=list[ArticleSerializer])
@paginate(ArticlePagination)
async def list_articles(request):
    return Article.objects.all()
```

Both approaches work identically. The serializer automatically filters fields - only declared fields are included in the response.

## ViewSet with Pagination

```python
from django_bolt.views import ViewSet

@api.viewset("/articles")
class ArticleViewSet(ViewSet):
    queryset = Article.objects.all()

    @paginate(ArticlePagination)
    async def list(self, request) -> list[ArticleSerializer]:
        return await self.get_queryset()
```

## ModelViewSet with Pagination

```python
from django_bolt.views import ModelViewSet

@api.viewset("/articles")
class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailSerializer  # For detail views
    list_serializer_class = ArticleListSerializer  # For list view
    pagination_class = ArticlePagination  # Automatically applied to list()
```

## Performance Considerations

### Avoiding N+1 Queries

Serialization happens after fetching items. If your serializer accesses related fields, use `select_related()` or `prefetch_related()` to avoid N+1 queries:

```python
# Bad - N+1 queries when serializer accesses article.author
@api.get("/articles")
@paginate(ArticlePagination)
async def list_articles(request) -> list[ArticleSerializer]:
    return Article.objects.all()

# Good - single query with JOIN
@api.get("/articles")
@paginate(ArticlePagination)
async def list_articles(request) -> list[ArticleSerializer]:
    return Article.objects.select_related("author").all()

# Good - prefetch for many-to-many
@api.get("/articles")
@paginate(ArticlePagination)
async def list_articles(request) -> list[ArticleSerializer]:
    return Article.objects.prefetch_related("tags").all()
```

### Cursor vs PageNumber for Large Datasets

For tables with millions of rows, prefer `CursorPagination` over `PageNumberPagination`. Cursor pagination uses indexed columns for efficient seeking, while page number pagination requires counting total rows.

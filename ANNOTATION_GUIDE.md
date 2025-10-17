# Django-Bolt Parameter Annotations Guide

## Type Annotations in Django-Bolt vs Django REST Framework

### The Key Difference

**Django REST Framework (DRF):**
- ❌ No type annotations required
- Uses explicit serializer calls: `serializer.is_valid()`
- Data extraction is manual: `request.data`

**Django-Bolt:**
- ✅ Type annotations required (but can be inferred!)
- Automatic validation based on types
- Data extraction is automatic based on annotations

---

## How Django-Bolt Parameter Binding Works

### 1. Automatic Inference (No Explicit Markers Needed!)

Django-Bolt is **smart** - it automatically infers parameter sources:

```python
from django_bolt import BoltAPI
import msgspec

api = BoltAPI()

class UserCreate(msgspec.Struct):
    name: str
    email: str

# ✅ AUTOMATIC INFERENCE - No explicit markers needed!

@api.get("/users/{user_id}")
async def get_user(
    user_id: int,              # ← Automatically inferred as PATH parameter
    include_posts: bool = False # ← Automatically inferred as QUERY parameter
):
    return {"user_id": user_id}

@api.post("/users")
async def create_user(
    user: UserCreate  # ← Automatically inferred as BODY parameter (msgspec.Struct)
):
    return {"id": 1, "name": user.name}
```

**Inference Rules:**
1. **Path parameters**: Detected from URL pattern (`{user_id}`)
2. **Query parameters**: Simple types (int, str, bool, float) with defaults
3. **Body parameters**: Complex types (msgspec.Struct, Pydantic models, dataclasses)

---

### 2. Explicit Markers (When You Need Control)

For ambiguous cases or when you want to be explicit, use parameter markers:

```python
from typing import Annotated
from django_bolt import BoltAPI
from django_bolt.params import Query, Path, Body, Header, Cookie, Form, File
import msgspec

api = BoltAPI()

class SearchFilters(msgspec.Struct):
    query: str
    tags: list[str]

@api.get("/search")
async def search(
    # Explicit markers for clarity
    q: Annotated[str, Query()],                    # Query parameter
    limit: Annotated[int, Query(ge=1, le=100)],    # Query with validation
    api_key: Annotated[str, Header("X-API-Key")],  # HTTP header
    session: Annotated[str, Cookie("session_id")], # Cookie
):
    return {"query": q, "limit": limit}

@api.post("/upload")
async def upload(
    title: Annotated[str, Form()],        # Form field
    file: Annotated[bytes, File()],       # File upload
    metadata: Annotated[dict, Body()],    # JSON body (rare with multipart)
):
    return {"uploaded": True}
```

---

## ViewSet Examples: Automatic vs Explicit

### Automatic Inference (Recommended)

```python
from django_bolt import BoltAPI, ModelViewSet
from myapp.models import Article
import msgspec

class ArticleSchema(msgspec.Struct):
    id: int
    title: str
    content: str

class ArticleCreateSchema(msgspec.Struct):
    title: str
    content: str

class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSchema

    # ✅ AUTOMATIC - Django-Bolt infers everything!
    async def get(self, request, pk: int):
        """pk automatically inferred as path parameter"""
        article = await self.get_object(pk)
        return ArticleSchema.from_model(article)

    async def post(self, request, data: ArticleCreateSchema):
        """data automatically inferred as body parameter (it's a Struct)"""
        article = await Article.objects.acreate(
            title=data.title,
            content=data.content
        )
        return ArticleSchema.from_model(article)

    async def patch(self, request, pk: int, data: ArticleCreateSchema):
        """Both pk (path) and data (body) automatically inferred!"""
        article = await self.get_object(pk)
        article.title = data.title
        await article.asave()
        return ArticleSchema.from_model(article)
```

### Explicit Markers (When Needed)

```python
from typing import Annotated
from django_bolt.params import Path, Body, Query

class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSchema

    # Explicit markers for clarity or special cases
    async def get(self,
                  request,
                  pk: Annotated[int, Path(ge=1)]):  # Validate pk >= 1
        article = await self.get_object(pk)
        return ArticleSchema.from_model(article)

    async def post(self,
                   request,
                   data: Annotated[ArticleCreateSchema, Body(embed=True)]):
        """Body(embed=True) wraps data in {"data": {...}}"""
        article = await Article.objects.acreate(
            title=data.title,
            content=data.content
        )
        return ArticleSchema.from_model(article)
```

---

## Complete Parameter Source Reference

### Available Parameter Markers

| Marker | Purpose | Example |
|--------|---------|---------|
| `Query()` | URL query parameters | `?page=1&limit=10` |
| `Path()` | URL path parameters | `/users/{user_id}` |
| `Body()` | Request body (JSON) | POST/PUT/PATCH body |
| `Header()` | HTTP headers | `X-API-Key`, `Authorization` |
| `Cookie()` | HTTP cookies | `session_id` |
| `Form()` | Form data | `application/x-www-form-urlencoded` |
| `File()` | File uploads | `multipart/form-data` |
| `Depends()` | Dependency injection | Computed values |

### Parameter Validation

All markers support validation constraints:

```python
from typing import Annotated
from django_bolt.params import Query, Path, Body

@api.get("/users")
async def list_users(
    # Numeric constraints
    page: Annotated[int, Query(ge=1)],              # >= 1
    limit: Annotated[int, Query(ge=1, le=100)],     # 1 <= x <= 100
    score: Annotated[float, Query(gt=0.0, lt=1.0)], # 0.0 < x < 1.0

    # String constraints
    username: Annotated[str, Query(min_length=3, max_length=20)],
    email: Annotated[str, Query(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")],

    # Metadata (for OpenAPI docs)
    search: Annotated[str, Query(
        description="Search query",
        example="django",
        deprecated=False
    )],
):
    return {"users": []}
```

---

## Common Patterns

### Pattern 1: List Endpoint (Query Parameters)

```python
@api.get("/articles")
async def list_articles(
    page: int = 1,           # Auto-inferred as query
    limit: int = 10,         # Auto-inferred as query
    search: str = "",        # Auto-inferred as query
    published: bool = True   # Auto-inferred as query
):
    articles = await Article.objects.filter(
        is_published=published
    )[:limit]
    return [ArticleSchema.from_model(a) for a in articles]
```

### Pattern 2: Detail Endpoint (Path Parameter)

```python
@api.get("/articles/{article_id}")
async def get_article(
    article_id: int  # Auto-inferred as path (matches URL pattern)
):
    article = await Article.objects.aget(id=article_id)
    return ArticleSchema.from_model(article)
```

### Pattern 3: Create Endpoint (Body Parameter)

```python
@api.post("/articles")
async def create_article(
    data: ArticleCreateSchema  # Auto-inferred as body (Struct type)
):
    article = await Article.objects.acreate(
        title=data.title,
        content=data.content
    )
    return ArticleSchema.from_model(article)
```

### Pattern 4: Update Endpoint (Path + Body)

```python
@api.put("/articles/{article_id}")
async def update_article(
    article_id: int,              # Auto-inferred as path
    data: ArticleCreateSchema     # Auto-inferred as body
):
    article = await Article.objects.aget(id=article_id)
    article.title = data.title
    article.content = data.content
    await article.asave()
    return ArticleSchema.from_model(article)
```

### Pattern 5: Mixed Parameters

```python
@api.get("/articles/{article_id}")
async def get_article(
    article_id: int,                               # Path
    include_comments: bool = False,                # Query
    api_key: Annotated[str, Header("X-API-Key")],  # Header
):
    article = await Article.objects.aget(id=article_id)
    result = ArticleSchema.from_model(article)

    if include_comments:
        result.comments = await get_comments(article_id)

    return result
```

---

## Why Type Annotations?

### 1. **Automatic Parameter Extraction**

```python
# DRF - Manual extraction
def create_user(self, request):
    name = request.data.get('name')      # Manual
    email = request.data.get('email')    # Manual
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

# Django-Bolt - Automatic extraction
async def post(self, request, data: UserCreateSchema):
    # 'data' is already extracted, validated, and typed!
    user = await User.objects.acreate(
        name=data.name,  # Type-safe access
        email=data.email
    )
```

### 2. **Type Safety & IDE Support**

```python
async def post(self, request, data: UserCreateSchema):
    # ✅ IDE autocomplete works!
    # ✅ Type checker catches errors!
    # ✅ Refactoring is safe!
    user = await User.objects.acreate(
        name=data.name,     # IDE knows this exists
        email=data.email,   # IDE knows the type
        # age=data.age      # ❌ IDE error if field doesn't exist!
    )
```

### 3. **Automatic Validation**

```python
class UserCreateSchema(msgspec.Struct):
    name: str
    email: str
    age: int

async def post(self, request, data: UserCreateSchema):
    # Django-Bolt already validated:
    # ✅ name is a string
    # ✅ email is a string
    # ✅ age is an integer
    # ❌ Returns 400 Bad Request if validation fails

    # You can use the data immediately - no need to call is_valid()!
    user = await User.objects.acreate(**data.__dict__)
```

### 4. **Performance**

```python
# msgspec deserialization is 5-10x faster than DRF's serializers
# Validation happens in Rust (via msgspec), not Python
# Zero-copy deserialization where possible
```

---

## Summary

### When to Use Automatic Inference (Recommended)

✅ **Use automatic inference when:**
- Parameters follow standard patterns
- Path params match URL pattern
- Body params are complex types (Struct, Pydantic models)
- Query params are simple types with defaults
- Code clarity is sufficient

```python
# Clean and simple!
async def get(self, request, pk: int):
    pass

async def post(self, request, data: ArticleCreateSchema):
    pass
```

### When to Use Explicit Markers

✅ **Use explicit markers when:**
- You need validation constraints (`ge=1`, `max_length=100`)
- Parameter source is ambiguous
- You want documentation metadata
- You're using advanced features (embed, alias)

```python
# More control and validation
async def get(self, request,
              pk: Annotated[int, Path(ge=1, description="Article ID")]):
    pass

async def post(self, request,
               data: Annotated[ArticleCreateSchema, Body(embed=True)]):
    pass
```

---

## Key Takeaways

1. **Type annotations are required** for Django-Bolt's parameter binding to work
2. **Most parameters are automatically inferred** - no explicit markers needed!
3. **Explicit markers give you control** when needed (validation, headers, cookies)
4. **It's type-safe** - IDE and type checkers help you write correct code
5. **It's fast** - msgspec validation is 5-10x faster than DRF
6. **It's just like DRF** - set `queryset` and `serializer_class`, then implement methods

The "annotation requirement" is actually Django-Bolt's **superpower** - it enables automatic parameter extraction, validation, type safety, and incredible performance!

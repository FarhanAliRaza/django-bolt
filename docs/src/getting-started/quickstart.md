---
icon: lucide/rocket
---

# Quick Start

This tutorial walks you through building a simple API with Django-Bolt. By the end, you'll understand the core concepts and be ready to build your own APIs.

## Your first endpoint

Open your `api.py` file and add:

```python
from django_bolt import BoltAPI

api = BoltAPI()

@api.get("/hello")
async def hello():
    return {"message": "Hello, World!"}
```

Start the server:

```bash
python manage.py runbolt --dev
```

Visit `http://localhost:8000/hello` in your browser. You'll see:

```json
{ "message": "Hello, World!" }
```

## Path parameters

Extract values from the URL path using curly braces:

```python
@api.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
```

The `user_id` parameter is automatically converted to an integer. Try:

- `http://localhost:8000/users/42` returns `{"user_id": 42}`
- `http://localhost:8000/users/abc` returns a 422 error (invalid integer)

## Query parameters

Function parameters without path placeholders become query parameters:

```python
@api.get("/search")
async def search(q: str, page: int = 1, limit: int = 10):
    return {"query": q, "page": page, "limit": limit}
```

Try: `http://localhost:8000/search?q=python&page=2`

Returns:

```json
{ "query": "python", "page": 2, "limit": 10 }
```

Optional parameters have default values. Required parameters (like `q`) return a 422 error if missing.

## Request body validation

Use `msgspec.Struct` to define and validate request bodies:

```python
import msgspec

class Item(msgspec.Struct):
    name: str
    price: float
    description: str | None = None

@api.post("/items")
async def create_item(item: Item):
    return {"name": item.name, "price": item.price}
```

Test with curl:

```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Widget", "price": 29.99}'
```

Returns:

```json
{ "name": "Widget", "price": 29.99 }
```

Invalid data returns a detailed validation error:

```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Widget"}'
```

Returns a [422 Unprocessable Entity](../topics/requests.md#validation-errors) because `price` is required:

```json
{
    "detail": [
        {
            "loc": ["body", "price"],
            "msg": "Object missing required field `price`",
            "type": "missing_field"
        }
    ]
}
```

## HTTP methods

Django-Bolt supports all common HTTP methods:

```python
@api.get("/resource")
async def get_resource():
    return {"method": "GET"}

@api.post("/resource")
async def create_resource():
    return {"method": "POST"}

@api.put("/resource/{id}")
async def update_resource(id: int):
    return {"method": "PUT", "id": id}

@api.patch("/resource/{id}")
async def partial_update(id: int):
    return {"method": "PATCH", "id": id}

@api.delete("/resource/{id}")
async def delete_resource(id: int):
    return {"method": "DELETE", "id": id}
```

## Response types

By default, returning a dict creates a JSON response. You can also return other types:

```python
from django_bolt.responses import PlainText, HTML, Redirect

@api.get("/text")
async def plain_text():
    return PlainText("Hello, plain text!")

@api.get("/html")
async def html_page():
    return HTML("<h1>Hello HTML</h1>")

@api.get("/redirect")
async def redirect():
    return Redirect("/hello")
```

## Working with Django models

Django-Bolt works seamlessly with Django's ORM. Use async methods for database queries:

```python
from myapp.models import Article

@api.get("/articles")
async def list_articles():
    # Use async ORM methods
    articles = []
    async for article in Article.objects.all()[:10]:
        articles.append({
            "id": article.id,
            "title": article.title
        })
    return {"articles": articles}

@api.get("/articles/{article_id}")
async def get_article(article_id: int):
    try:
        article = await Article.objects.aget(id=article_id)
        return {"id": article.id, "title": article.title}
    except Article.DoesNotExist:
        from django_bolt.exceptions import HTTPException
        raise HTTPException(status_code=404, detail="Article not found")
```

## Error handling

Raise `HTTPException` to return error responses:

```python
from django_bolt.exceptions import HTTPException

@api.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid item ID")

    # Simulate item not found
    if item_id > 1000:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"item_id": item_id}
```

Common HTTP exceptions are also available:

```python
from django_bolt.exceptions import NotFound, BadRequest, Unauthorized

@api.get("/resource/{id}")
async def get_resource(id: int):
    if id <= 0:
        raise BadRequest(detail="ID must be positive")

    # Check if exists...
    raise NotFound(detail=f"Resource {id} not found")
```

## API documentation

Django-Bolt automatically generates OpenAPI documentation. Visit:

- `http://localhost:8000/docs` - Interactive Swagger UI

Add descriptions to your endpoints for better documentation:

```python
@api.get(
    "/users/{user_id}",
    summary="Get a user",
    description="Retrieve a user by their unique ID",
    tags=["users"]
)
async def get_user(user_id: int):
    """
    This docstring also appears in the API documentation.
    """
    return {"user_id": user_id}
```

## Next steps

You now know the basics of Django-Bolt. Here's where to go next:

- **[Deployment](deployment.md)** - Deploy with multiple processes
- **[Routing](../topics/routing.md)** - Learn more about route patterns and path converters
- **[Responses](../topics/responses.md)** - Explore all response types including streaming
- **[Authentication](../topics/authentication.md)** - Add JWT or API key authentication
- **[Class-Based Views](../topics/class-based-views.md)** - Organize routes with ViewSets

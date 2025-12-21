---
icon: lucide/flask-conical
---

# Testing

Django-Bolt provides a `TestClient` for testing your API endpoints without starting a server.

## TestClient

The `TestClient` routes requests through the Rust layer, providing realistic testing:

```python
from django_bolt import BoltAPI
from django_bolt.testing import TestClient

api = BoltAPI()

@api.get("/hello")
async def hello():
    return {"message": "world"}

# Test the endpoint
with TestClient(api) as client:
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "world"}
```

## Making requests

### GET requests

```python
with TestClient(api) as client:
    # Simple GET
    response = client.get("/users")

    # GET with query parameters
    response = client.get("/search?q=test&limit=20")

    # GET with headers
    response = client.get("/secure", headers={"Authorization": "Bearer token"})
```

### POST requests

```python
with TestClient(api) as client:
    # POST with JSON body
    response = client.post(
        "/users",
        json={"name": "John", "email": "john@example.com"}
    )

    # POST with form data
    response = client.post(
        "/login",
        data={"username": "john", "password": "secret"}
    )
```

### PUT, PATCH, DELETE

```python
with TestClient(api) as client:
    # PUT (full update)
    response = client.put(
        "/users/1",
        json={"name": "Updated", "email": "updated@example.com"}
    )

    # PATCH (partial update)
    response = client.patch("/users/1", json={"name": "Patched"})

    # DELETE
    response = client.delete("/users/1")
```

## Response object

The response object provides access to status, headers, and body:

```python
response = client.get("/users/1")

# Status code
assert response.status_code == 200

# JSON body
data = response.json()
assert data["id"] == 1

# Raw content
raw = response.content  # bytes

# Headers
content_type = response.headers.get("content-type")
```

## Testing path parameters

```python
@api.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "name": f"User {user_id}"}

with TestClient(api) as client:
    response = client.get("/users/123")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 123
    assert data["name"] == "User 123"
```

## Testing query parameters

```python
@api.get("/search")
async def search(q: str, limit: int = 10):
    return {"query": q, "limit": limit}

with TestClient(api) as client:
    response = client.get("/search?q=test&limit=20")
    data = response.json()
    assert data["query"] == "test"
    assert data["limit"] == 20
```

## Testing headers

```python
from typing import Annotated
from django_bolt.param_functions import Header

@api.get("/with-header")
async def with_header(x_custom: Annotated[str, Header()]):
    return {"header_value": x_custom}

with TestClient(api) as client:
    response = client.get(
        "/with-header",
        headers={"X-Custom": "test-value"}
    )
    assert response.json() == {"header_value": "test-value"}
```

## Testing request body

```python
import msgspec

class UserCreate(msgspec.Struct):
    name: str
    email: str

@api.post("/users")
async def create_user(user: UserCreate):
    return {"id": 1, "name": user.name, "email": user.email}

with TestClient(api) as client:
    response = client.post(
        "/users",
        json={"name": "John", "email": "john@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "John"
```

## Testing error responses

```python
with TestClient(api) as client:
    # Test 404
    response = client.get("/nonexistent")
    assert response.status_code == 404

    # Test validation error (422)
    response = client.post("/users", json={})  # Missing required fields
    assert response.status_code == 422
```

## Testing custom status codes

```python
@api.post("/created", status_code=201)
async def create():
    return {"created": True}

with TestClient(api) as client:
    response = client.post("/created")
    assert response.status_code == 201
```

## Testing multiple HTTP methods

```python
@api.get("/resource")
async def get_resource():
    return {"method": "GET"}

@api.post("/resource")
async def create_resource():
    return {"method": "POST"}

@api.put("/resource")
async def update_resource():
    return {"method": "PUT"}

@api.delete("/resource")
async def delete_resource():
    return {"method": "DELETE"}

with TestClient(api) as client:
    assert client.get("/resource").json() == {"method": "GET"}
    assert client.post("/resource").json() == {"method": "POST"}
    assert client.put("/resource").json() == {"method": "PUT"}
    assert client.delete("/resource").json() == {"method": "DELETE"}
```

## Streaming responses

Test streaming with `stream=True`:

```python
@api.get("/stream")
async def stream():
    async def generate():
        for i in range(5):
            yield f"data: {i}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")

with TestClient(api) as client:
    response = client.get("/stream", stream=True)
    assert response.status_code == 200

    # Iterate over chunks
    chunks = list(response.iter_content(chunk_size=32, decode_unicode=True))
    assert len(chunks) > 0

    # Or iterate over lines
    lines = list(response.iter_lines())
    data_lines = [l for l in lines if l.startswith("data:")]
    assert len(data_lines) == 5
```

## Testing with pytest

### Basic test file

```python
# tests/test_api.py
import pytest
from django_bolt import BoltAPI
from django_bolt.testing import TestClient

@pytest.fixture
def api():
    """Create fresh API instance."""
    api = BoltAPI()

    @api.get("/hello")
    async def hello():
        return {"message": "world"}

    return api

@pytest.fixture
def client(api):
    """Create test client."""
    with TestClient(api) as client:
        yield client

def test_hello(client):
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "world"}
```

### Testing with Django database

```python
import pytest
from django_bolt import BoltAPI
from django_bolt.testing import TestClient
from myapp.models import User

@pytest.fixture
def api():
    api = BoltAPI()

    @api.get("/users/{user_id}")
    async def get_user(user_id: int):
        user = await User.objects.aget(id=user_id)
        return {"id": user.id, "username": user.username}

    return api

@pytest.mark.django_db(transaction=True)
def test_get_user(api):
    # Create test data
    user = User.objects.create(username="testuser", email="test@example.com")

    with TestClient(api) as client:
        response = client.get(f"/users/{user.id}")
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
```

### Testing ViewSets

```python
import pytest
from django_bolt import BoltAPI, ViewSet
from django_bolt.testing import TestClient
from myapp.models import Article

@pytest.fixture
def api():
    api = BoltAPI()

    @api.viewset("/articles")
    class ArticleViewSet(ViewSet):
        queryset = Article.objects.all()

        async def list(self, request):
            articles = []
            async for article in await self.get_queryset():
                articles.append({"id": article.id, "title": article.title})
            return articles

        async def retrieve(self, request, pk: int):
            article = await self.get_object(pk)
            return {"id": article.id, "title": article.title}

    return api

@pytest.mark.django_db(transaction=True)
def test_article_viewset(api):
    Article.objects.create(title="Test Article", content="Content")

    with TestClient(api) as client:
        # Test list
        response = client.get("/articles")
        assert response.status_code == 200
        assert len(response.json()) == 1

        # Test retrieve
        response = client.get("/articles/1")
        assert response.status_code == 200
        assert response.json()["title"] == "Test Article"
```

## AsyncTestClient

For async test functions, use `AsyncTestClient`:

```python
import pytest
from django_bolt import BoltAPI
from django_bolt.testing import AsyncTestClient

api = BoltAPI()

@api.get("/hello")
async def hello():
    return {"message": "world"}

@pytest.mark.asyncio
async def test_async():
    async with AsyncTestClient(api) as client:
        response = await client.get("/hello")
        assert response.status_code == 200
        assert response.json() == {"message": "world"}
```

The `AsyncTestClient` is useful when:

- Your test function is async
- You need to await other async operations in the same test
- You're using `pytest-asyncio`

## Test isolation

Each `TestClient` context creates isolated state:

```python
def test_isolated():
    api = BoltAPI()

    @api.get("/counter")
    async def counter():
        return {"count": 1}

    # Each with block is isolated
    with TestClient(api) as client:
        response = client.get("/counter")
        assert response.json()["count"] == 1

    with TestClient(api) as client:
        response = client.get("/counter")
        assert response.json()["count"] == 1  # Fresh state
```

## Best practices

1. **Use fixtures**: Create API and client fixtures for reuse.

2. **Test all status codes**: Verify success (2xx), client errors (4xx), and server errors (5xx).

3. **Test validation**: Ensure invalid input returns 422 with proper error messages.

4. **Test authentication**: Verify endpoints require proper auth when expected.

5. **Use `django_db` mark**: For tests that access the database.

6. **Clean up test data**: Use database transactions that roll back.

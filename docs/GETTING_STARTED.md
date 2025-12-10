# Getting Started with Django-Bolt

Welcome to Django-Bolt! This guide will walk you through everything you need to know to start building high-performance APIs with Django.

## Table of Contents

1. [What is Django-Bolt?](#what-is-django-bolt)
2. [Installation](#installation)
3. [Quick Start: Hello World](#quick-start-hello-world)
4. [Basic Concepts](#basic-concepts)
5. [Your First API Endpoint](#your-first-api-endpoint)
6. [Request Parameters](#request-parameters)
7. [Request Body & Validation](#request-body--validation)
8. [Response Types](#response-types)
9. [Running the Server](#running-the-server)
10. [Authentication](#authentication)
11. [Middleware](#middleware)
12. [Class-Based Views](#class-based-views)
13. [Testing Your API](#testing-your-api)
14. [Complete Example Application](#complete-example-application)
15. [Next Steps](#next-steps)

---

## What is Django-Bolt?

Django-Bolt is a high-performance API framework for Django that provides **Rust-powered API endpoints** capable of **60k+ RPS** performance. Think of it like Django REST Framework or Django Ninja, but with:

- **Blazing Fast Performance** - Actix Web + Rust handles HTTP, achieving 60k+ requests per second
- **Rust-Powered Auth** - JWT and API Key validation runs without Python GIL overhead
- **Fast Serialization** - msgspec provides 5-10x faster JSON encoding than standard library
- **Seamless Django Integration** - Use your existing Django models, ORM, and project structure
- **Full Async Support** - Built for modern async Python with coroutines
- **Type Safety** - Automatic request/response validation with Python type hints

Django-Bolt integrates seamlessly with your existing Django projects - no need to rewrite everything. You can use it alongside Django's standard views, admin panel, and all your favorite Django packages.

---

## Installation

> **Note:** Django-Bolt is currently in development and not yet published to PyPI. For now, you'll need to build it locally.

### Prerequisites

- Python 3.12+
- Rust (for building the extension)
- A Django project

### Building from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/django-bolt.git
cd django-bolt

# Install dependencies (using uv recommended)
pip install uv
uv sync

# Build the Rust extension
make build
# or: uv run maturin develop --release

# Run tests to verify installation
make test-py
```

Once Django-Bolt is published to PyPI, installation will be as simple as:

```bash
pip install django-bolt
```

---

## Quick Start: Hello World

Let's create your first Django-Bolt API in 60 seconds!

### 1. Create a Django Project (if you don't have one)

```bash
django-admin startproject myproject
cd myproject
```

### 2. Add Django-Bolt to INSTALLED_APPS

Edit `myproject/settings.py`:

```python
INSTALLED_APPS = [
    "django_bolt",  # Add this line
    'django.contrib.admin',
    'django.contrib.auth',
    # ... other apps
]
```

### 3. Create Your API File

Create `myproject/api.py` in the same directory as `settings.py`:

```python
from django_bolt import BoltAPI

api = BoltAPI()

@api.get("/hello")
async def hello_world():
    return {"message": "Hello, World!"}
```

### 4. Run the Server

```bash
python manage.py runbolt --host 0.0.0.0 --port 8000
```

### 5. Test Your API

```bash
curl http://localhost:8000/hello
# Output: {"message":"Hello, World!"}
```

Congratulations! You've just created your first high-performance API endpoint! 🎉

---

## Basic Concepts

### The BoltAPI Object

The `BoltAPI` class is the heart of Django-Bolt. It's similar to FastAPI's app or Django Ninja's API object:

```python
from django_bolt import BoltAPI

api = BoltAPI()  # Create an API instance
```

### Route Decorators

Django-Bolt uses decorators to define routes. Available HTTP methods:

- `@api.get()` - GET requests
- `@api.post()` - POST requests
- `@api.put()` - PUT requests
- `@api.patch()` - PATCH requests
- `@api.delete()` - DELETE requests
- `@api.head()` - HEAD requests
- `@api.options()` - OPTIONS requests

### Async Handlers

**All route handlers must be async functions:**

```python
# ✅ Correct
@api.get("/users")
async def get_users():
    return {"users": []}

# ❌ Wrong - will not work
@api.get("/users")
def get_users():  # Missing 'async'
    return {"users": []}
```

### Auto-Discovery

Django-Bolt automatically discovers `api.py` files in:

1. **Project root** - Same directory as `settings.py`
2. **All installed apps** - Each app can have its own `api.py`

Example project structure:

```
myproject/
├── manage.py
├── myproject/
│   ├── settings.py
│   └── api.py          # Project-level API routes
├── users/
│   ├── models.py
│   └── api.py          # Users app API routes
└── products/
    ├── models.py
    └── api.py          # Products app API routes
```

All routes are automatically merged when you run `python manage.py runbolt`.

---

## Your First API Endpoint

Let's build a simple user API step by step.

### Simple GET Endpoint

```python
from django_bolt import BoltAPI

api = BoltAPI()

@api.get("/users")
async def list_users():
    """List all users."""
    return {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    }
```

Test it:
```bash
curl http://localhost:8000/users
```

### Path Parameters

Capture dynamic values from the URL:

```python
@api.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get a specific user by ID."""
    return {"user_id": user_id, "name": "Alice"}
```

Test it:
```bash
curl http://localhost:8000/users/123
# Output: {"user_id":123,"name":"Alice"}
```

The type annotation `user_id: int` automatically converts and validates the path parameter.

### Multiple Path Parameters

```python
@api.get("/users/{user_id}/posts/{post_id}")
async def get_user_post(user_id: int, post_id: int):
    """Get a specific post from a specific user."""
    return {
        "user_id": user_id,
        "post_id": post_id,
        "title": "My Post"
    }
```

---

## Request Parameters

Django-Bolt supports multiple types of request parameters with automatic extraction and validation.

### Query Parameters

Extract values from the URL query string:

```python
from typing import Optional

@api.get("/search")
async def search_users(
    q: str,                    # Required query parameter
    limit: int = 10,           # Optional with default value
    offset: int = 0,
    active: Optional[bool] = None  # Optional, can be None
):
    return {
        "query": q,
        "limit": limit,
        "offset": offset,
        "active": active
    }
```

Test it:
```bash
curl "http://localhost:8000/search?q=alice&limit=20&active=true"
```

### Headers

Extract custom HTTP headers:

```python
from typing import Annotated
from django_bolt.param_functions import Header

@api.get("/protected")
async def protected_route(
    api_key: Annotated[str, Header(alias="x-api-key")]
):
    return {"api_key": api_key}
```

Test it:
```bash
curl -H "x-api-key: secret123" http://localhost:8000/protected
```

### Cookies

Extract cookie values:

```python
from django_bolt.param_functions import Cookie

@api.get("/session")
async def get_session(
    session_id: Annotated[str, Cookie(alias="sessionid")]
):
    return {"session_id": session_id}
```

Test it:
```bash
curl -b "sessionid=abc123" http://localhost:8000/session
```

### Form Data

Handle HTML form submissions:

```python
from django_bolt.param_functions import Form

@api.post("/login")
async def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    remember_me: Annotated[bool, Form()] = False
):
    return {"username": username, "remember_me": remember_me}
```

Test it:
```bash
curl -X POST \
  -F "username=alice" \
  -F "password=secret" \
  -F "remember_me=true" \
  http://localhost:8000/login
```

### File Uploads

Handle file uploads:

```python
from django_bolt.param_functions import File

@api.post("/upload")
async def upload_file(
    files: Annotated[list[dict], File(alias="file")]
):
    """Upload one or more files."""
    return {
        "uploaded": len(files),
        "files": [
            {"name": f.get("filename"), "size": f.get("size")}
            for f in files
        ]
    }
```

Test it:
```bash
curl -X POST \
  -F "file=@document.pdf" \
  -F "file=@image.png" \
  http://localhost:8000/upload
```

---

## Request Body & Validation

For JSON APIs, use `msgspec.Struct` for automatic validation and serialization.

### Basic Request Body

```python
import msgspec

class CreateUserRequest(msgspec.Struct):
    username: str
    email: str
    age: int

@api.post("/users")
async def create_user(user: CreateUserRequest):
    """Create a new user with automatic validation."""
    # user is already validated and typed
    return {
        "created": True,
        "username": user.username,
        "email": user.email,
        "age": user.age
    }
```

Test it:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","age":25}' \
  http://localhost:8000/users
```

If validation fails (e.g., age is a string instead of int), Django-Bolt automatically returns a 422 error with details.

### Optional Fields

```python
from typing import Optional

class UpdateUserRequest(msgspec.Struct):
    email: Optional[str] = None
    age: Optional[int] = None
    bio: str = ""  # Default value

@api.patch("/users/{user_id}")
async def update_user(user_id: int, data: UpdateUserRequest):
    """Partially update a user."""
    updates = {}
    if data.email is not None:
        updates["email"] = data.email
    if data.age is not None:
        updates["age"] = data.age

    return {"user_id": user_id, "updates": updates}
```

### Nested Structures

```python
class Address(msgspec.Struct):
    street: str
    city: str
    country: str

class CreateUserWithAddress(msgspec.Struct):
    username: str
    email: str
    address: Address  # Nested structure

@api.post("/users-with-address")
async def create_user_with_address(user: CreateUserWithAddress):
    return {
        "username": user.username,
        "city": user.address.city,
        "country": user.address.country
    }
```

Test it:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "username":"alice",
    "email":"alice@example.com",
    "address":{"street":"123 Main St","city":"New York","country":"USA"}
  }' \
  http://localhost:8000/users-with-address
```

### Response Models

Validate response data as well:

```python
class UserResponse(msgspec.Struct):
    id: int
    username: str
    email: str

@api.post("/users", response_model=UserResponse)
async def create_user(user: CreateUserRequest) -> UserResponse:
    """Create user with validated response."""
    # Your response will be validated against UserResponse
    return UserResponse(
        id=1,
        username=user.username,
        email=user.email
    )
```

---

## Response Types

Django-Bolt supports multiple response types beyond JSON.

### JSON Response (Default)

Return a dict or list, and it's automatically serialized to JSON:

```python
@api.get("/users")
async def list_users():
    return {"users": [{"id": 1, "name": "Alice"}]}
```

### Plain Text

```python
from django_bolt.responses import PlainText

@api.get("/health")
async def health_check():
    return PlainText("OK")
```

### HTML

```python
from django_bolt.responses import HTML

@api.get("/welcome")
async def welcome():
    return HTML("<h1>Welcome to Django-Bolt!</h1>")
```

### Redirect

```python
from django_bolt.responses import Redirect

@api.get("/old-path")
async def old_endpoint():
    return Redirect("/new-path", status_code=301)
```

### File Download (In-Memory)

```python
from django_bolt.responses import File

@api.get("/download")
async def download_file():
    content = b"Hello, World!"
    return File(content, filename="hello.txt", media_type="text/plain")
```

### File Download (Streaming)

For large files, use `FileResponse` which streams from disk in Rust (zero-copy):

```python
from django_bolt.responses import FileResponse

@api.get("/download-large")
async def download_large_file():
    return FileResponse(
        path="/path/to/large-file.pdf",
        filename="document.pdf",
        media_type="application/pdf"
    )
```

### Streaming Response

For long-running responses or Server-Sent Events (SSE):

```python
from django_bolt.responses import StreamingResponse
import asyncio

@api.get("/stream")
async def stream_data():
    async def generate():
        for i in range(10):
            yield f"data: {i}\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

---

## Running the Server

### Basic Command

```bash
python manage.py runbolt --host 0.0.0.0 --port 8000
```

### Multi-Process for Production

Scale horizontally with multiple processes (SO_REUSEPORT provides kernel-level load balancing):

```bash
python manage.py runbolt --host 0.0.0.0 --port 8000 --processes 4 --workers 1
```

- `--processes`: Number of Python processes (recommended: CPU cores)
- `--workers`: Actix workers per process (usually keep at 1)

### Development Mode

For development with auto-reload:

```bash
python manage.py runbolt --dev
```

This runs in single-process mode and watches for file changes.

### All Available Options

```bash
python manage.py runbolt --help
```

Options:
- `--host`: Bind address (default: 127.0.0.1)
- `--port`: Port number (default: 8000)
- `--processes` / `-p`: Number of processes (default: 1)
- `--workers` / `-w`: Actix workers per process (default: 1)
- `--dev`: Development mode with auto-reload

---

## Authentication

Django-Bolt includes high-performance authentication that runs in Rust without Python GIL overhead.

### JWT Authentication

#### Setup

```python
from django_bolt import BoltAPI
from django_bolt.auth import JWTAuthentication, IsAuthenticated

api = BoltAPI()
```

#### Creating JWT Tokens

Use Django's built-in User model to generate tokens:

```python
from django.contrib.auth.models import User
from django_bolt.auth import create_jwt_for_user

@api.post("/login")
async def login(username: str, password: str):
    """Login endpoint that returns JWT token."""
    # Get user from database
    try:
        user = await User.objects.aget(username=username)
    except User.DoesNotExist:
        from django_bolt.exceptions import Unauthorized
        raise Unauthorized(detail="Invalid credentials")

    # Verify password (in production, use proper password hashing)
    if not user.check_password(password):
        from django_bolt.exceptions import Unauthorized
        raise Unauthorized(detail="Invalid credentials")

    # Create JWT token
    token = create_jwt_for_user(user, exp_hours=24)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 86400  # 24 hours in seconds
    }
```

#### Protected Routes

Require authentication for specific routes:

```python
@api.get(
    "/protected",
    auth=[JWTAuthentication()],
    guards=[IsAuthenticated()]
)
async def protected_route(request):
    """Route that requires valid JWT token."""
    # Access authentication context
    auth = request.get("auth", {})
    user_id = auth.get("user_id")
    username = auth.get("username")

    return {
        "message": f"Hello, {username}!",
        "user_id": user_id
    }
```

Test it:
```bash
# Get token
TOKEN=$(curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret"}' \
  http://localhost:8000/login | jq -r .access_token)

# Use token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/protected
```

### Permission Guards

Django-Bolt includes several built-in guards:

```python
from django_bolt.auth import (
    IsAuthenticated,    # Requires valid auth
    IsAdminUser,        # Requires admin/superuser
    IsStaff,            # Requires staff status
    HasPermission,      # Single permission
    HasAnyPermission,   # Any of the permissions (OR)
    HasAllPermissions,  # All permissions (AND)
)

# Require admin access
@api.get(
    "/admin/stats",
    auth=[JWTAuthentication()],
    guards=[IsAdminUser()]
)
async def admin_stats(request):
    return {"total_users": 100}

# Require specific permission
@api.post(
    "/articles",
    auth=[JWTAuthentication()],
    guards=[HasPermission("articles.create")]
)
async def create_article(request):
    return {"created": True}

# Require any of multiple permissions
@api.get(
    "/content",
    auth=[JWTAuthentication()],
    guards=[HasAnyPermission("content.view", "content.edit")]
)
async def view_content(request):
    return {"content": "..."}
```

### API Key Authentication

For service-to-service authentication:

```python
from django_bolt.auth import APIKeyAuthentication

@api.get(
    "/api/data",
    auth=[APIKeyAuthentication()],
    guards=[IsAuthenticated()]
)
async def api_data(request):
    return {"data": [...]}
```

Test it:
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/api/data
```

---

## Middleware

Django-Bolt includes a powerful middleware system that runs in Rust for maximum performance.

### CORS (Cross-Origin Resource Sharing)

#### Global CORS

Apply CORS to all routes:

```python
from django_bolt import BoltAPI

api = BoltAPI(
    middleware_config={
        "cors": {
            "origins": ["http://localhost:3000", "https://myapp.com"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "headers": ["Content-Type", "Authorization"],
            "credentials": True,
            "max_age": 3600,
        }
    }
)
```

#### Per-Route CORS

Override CORS settings for specific routes:

```python
from django_bolt.auth import cors

@api.get("/public")
@cors(origins=["*"])  # Allow all origins
async def public_endpoint():
    return {"public": True}
```

### Rate Limiting

Protect your API from abuse with token bucket rate limiting:

```python
from django_bolt.auth import rate_limit

# Limit to 10 requests per second, with burst of 20
@api.get("/limited")
@rate_limit(rps=10, burst=20)
async def limited_endpoint():
    return {"message": "Rate limited endpoint"}
```

### Compression

Django-Bolt automatically compresses responses (gzip, brotli, zstd) based on the client's `Accept-Encoding` header. To disable compression for specific routes:

```python
from django_bolt.middleware import no_compress

@api.get("/stream")
@no_compress
async def streaming_endpoint():
    # Compression disabled for streaming
    return StreamingResponse(...)
```

### Skip Middleware

Selectively disable middleware for specific routes:

```python
from django_bolt.auth import skip_middleware

@api.get("/no-cors")
@skip_middleware("cors", "rate_limit")
async def no_middleware():
    return {"message": "No CORS or rate limiting"}
```

---

## Class-Based Views

For better code organization, use class-based views (similar to Django REST Framework's ViewSets).

### APIView (Simple Class-Based View)

Group related handlers in a class:

```python
from django_bolt import BoltAPI
from django_bolt.views import APIView
import msgspec

api = BoltAPI()

class Item(msgspec.Struct):
    name: str
    price: float

@api.view("/items/{item_id}")
class ItemAPIView(APIView):
    """Handle CRUD operations for items."""

    async def get(self, request, item_id: int):
        """Get an item by ID."""
        return {"item_id": item_id, "name": "Widget"}

    async def put(self, request, item_id: int, item: Item):
        """Update an item."""
        return {"item_id": item_id, "name": item.name, "price": item.price}

    async def delete(self, request, item_id: int):
        """Delete an item."""
        return {"deleted": True, "item_id": item_id}
```

This creates three routes:
- `GET /items/{item_id}`
- `PUT /items/{item_id}`
- `DELETE /items/{item_id}`

### ViewSet (DRF-Style)

For full CRUD operations with custom actions:

```python
from django_bolt import BoltAPI, action
from django_bolt.views import ViewSet

api = BoltAPI()

@api.viewset("/products")
class ProductViewSet(ViewSet):
    """Full CRUD ViewSet for products."""

    async def list(self, request):
        """GET /products - List all products."""
        return {"products": [...]}

    async def create(self, request, product: ProductCreate):
        """POST /products - Create a product."""
        return {"created": True, "product": product}

    async def retrieve(self, request, id: int):
        """GET /products/{id} - Get a specific product."""
        return {"id": id, "name": "Product"}

    async def update(self, request, id: int, product: ProductUpdate):
        """PUT /products/{id} - Update a product."""
        return {"id": id, "updated": True}

    async def partial_update(self, request, id: int, product: ProductUpdate):
        """PATCH /products/{id} - Partially update a product."""
        return {"id": id, "updated": True}

    async def destroy(self, request, id: int):
        """DELETE /products/{id} - Delete a product."""
        return {"deleted": True, "id": id}

    # Custom action
    @action(methods=["POST"], detail=True)
    async def publish(self, request, id: int):
        """POST /products/{id}/publish - Publish a product."""
        return {"id": id, "published": True}
```

This automatically creates routes:
- `GET /products` → `list()`
- `POST /products` → `create()`
- `GET /products/{id}` → `retrieve()`
- `PUT /products/{id}` → `update()`
- `PATCH /products/{id}` → `partial_update()`
- `DELETE /products/{id}` → `destroy()`
- `POST /products/{id}/publish` → `publish()` (custom action)

---

## Testing Your API

### Manual Testing with curl

```bash
# GET request
curl http://localhost:8000/users

# POST with JSON
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"alice"}' \
  http://localhost:8000/users

# With authentication
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/protected
```

### Using Python Requests

```python
import requests

# Simple GET
response = requests.get("http://localhost:8000/users")
print(response.json())

# POST with data
response = requests.post(
    "http://localhost:8000/users",
    json={"username": "alice", "email": "alice@example.com"}
)
print(response.json())

# With authentication
headers = {"Authorization": "Bearer YOUR_TOKEN"}
response = requests.get("http://localhost:8000/protected", headers=headers)
print(response.json())
```

### Testing with httpx (Async)

```python
import asyncio
import httpx

async def test_api():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/users")
        print(response.json())

asyncio.run(test_api())
```

### Unit Testing

Django-Bolt works with Django's test framework:

```python
from django.test import TestCase
import requests

class APITestCase(TestCase):
    def setUp(self):
        self.base_url = "http://localhost:8000"

    def test_list_users(self):
        response = requests.get(f"{self.base_url}/users")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("users", data)
```

---

## Complete Example Application

Let's build a complete blog API with articles, authentication, and pagination.

### Project Structure

```
myblog/
├── manage.py
├── myblog/
│   ├── settings.py
│   └── api.py          # Authentication routes
└── articles/
    ├── models.py       # Article model
    └── api.py          # Article CRUD routes
```

### Step 1: Create the Model

`articles/models.py`:
```python
from django.db import models
from django.contrib.auth.models import User

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
```

### Step 2: Create Authentication API

`myblog/api.py`:
```python
from django_bolt import BoltAPI
from django_bolt.auth import create_jwt_for_user
from django_bolt.exceptions import Unauthorized
from django.contrib.auth.models import User
import msgspec

api = BoltAPI()

class LoginRequest(msgspec.Struct):
    username: str
    password: str

class RegisterRequest(msgspec.Struct):
    username: str
    email: str
    password: str

@api.post("/auth/login")
async def login(credentials: LoginRequest):
    """Login and get JWT token."""
    try:
        user = await User.objects.aget(username=credentials.username)
    except User.DoesNotExist:
        raise Unauthorized(detail="Invalid credentials")

    if not user.check_password(credentials.password):
        raise Unauthorized(detail="Invalid credentials")

    token = create_jwt_for_user(user, exp_hours=24)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }

@api.post("/auth/register")
async def register(data: RegisterRequest):
    """Register a new user."""
    # Check if user exists
    if await User.objects.filter(username=data.username).aexists():
        from django_bolt.exceptions import BadRequest
        raise BadRequest(detail="Username already exists")

    # Create user
    user = await User.objects.acreate_user(
        username=data.username,
        email=data.email,
        password=data.password
    )

    # Generate token
    token = create_jwt_for_user(user, exp_hours=24)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }
```

### Step 3: Create Articles API

`articles/api.py`:
```python
from django_bolt import BoltAPI, action
from django_bolt.views import ViewSet
from django_bolt.auth import JWTAuthentication, IsAuthenticated
from django_bolt.exceptions import NotFound, Forbidden
import msgspec
from typing import Optional
from .models import Article
from django.contrib.auth.models import User

api = BoltAPI(prefix="/articles")

# Schemas
class ArticleResponse(msgspec.Struct):
    id: int
    title: str
    content: str
    author: str
    created_at: str
    updated_at: str
    published: bool

class ArticleCreate(msgspec.Struct):
    title: str
    content: str
    published: bool = False

class ArticleUpdate(msgspec.Struct):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None

# ViewSet
@api.viewset("")
class ArticleViewSet(ViewSet):
    """CRUD operations for articles."""

    async def list(self, request, published: Optional[bool] = None, limit: int = 20):
        """GET /articles - List articles (optionally filter by published status)."""
        queryset = Article.objects.select_related('author')

        if published is not None:
            queryset = queryset.filter(published=published)

        queryset = queryset[:limit]

        articles = []
        async for article in queryset:
            articles.append(ArticleResponse(
                id=article.id,
                title=article.title,
                content=article.content,
                author=article.author.username,
                created_at=article.created_at.isoformat(),
                updated_at=article.updated_at.isoformat(),
                published=article.published
            ))

        return {"count": len(articles), "articles": articles}

    async def retrieve(self, request, id: int):
        """GET /articles/{id} - Get a specific article."""
        try:
            article = await Article.objects.select_related('author').aget(id=id)
            return ArticleResponse(
                id=article.id,
                title=article.title,
                content=article.content,
                author=article.author.username,
                created_at=article.created_at.isoformat(),
                updated_at=article.updated_at.isoformat(),
                published=article.published
            )
        except Article.DoesNotExist:
            raise NotFound(detail=f"Article {id} not found")

    @api.post(
        "",
        auth=[JWTAuthentication()],
        guards=[IsAuthenticated()]
    )
    async def create(self, request, data: ArticleCreate):
        """POST /articles - Create a new article (requires authentication)."""
        auth = request.get("auth", {})
        user_id = auth.get("user_id")

        # Get user
        user = await User.objects.aget(id=user_id)

        # Create article
        article = await Article.objects.acreate(
            title=data.title,
            content=data.content,
            author=user,
            published=data.published
        )

        return ArticleResponse(
            id=article.id,
            title=article.title,
            content=article.content,
            author=user.username,
            created_at=article.created_at.isoformat(),
            updated_at=article.updated_at.isoformat(),
            published=article.published
        )

    @api.patch(
        "/{id}",
        auth=[JWTAuthentication()],
        guards=[IsAuthenticated()]
    )
    async def partial_update(self, request, id: int, data: ArticleUpdate):
        """PATCH /articles/{id} - Update an article (requires authentication and ownership)."""
        auth = request.get("auth", {})
        user_id = auth.get("user_id")

        try:
            article = await Article.objects.select_related('author').aget(id=id)
        except Article.DoesNotExist:
            raise NotFound(detail=f"Article {id} not found")

        # Check ownership
        if article.author_id != user_id:
            raise Forbidden(detail="You can only edit your own articles")

        # Update fields
        if data.title is not None:
            article.title = data.title
        if data.content is not None:
            article.content = data.content
        if data.published is not None:
            article.published = data.published

        await article.asave()

        return ArticleResponse(
            id=article.id,
            title=article.title,
            content=article.content,
            author=article.author.username,
            created_at=article.created_at.isoformat(),
            updated_at=article.updated_at.isoformat(),
            published=article.published
        )

    @api.delete(
        "/{id}",
        auth=[JWTAuthentication()],
        guards=[IsAuthenticated()]
    )
    async def destroy(self, request, id: int):
        """DELETE /articles/{id} - Delete an article (requires authentication and ownership)."""
        auth = request.get("auth", {})
        user_id = auth.get("user_id")

        try:
            article = await Article.objects.aget(id=id)
        except Article.DoesNotExist:
            raise NotFound(detail=f"Article {id} not found")

        # Check ownership
        if article.author_id != user_id:
            raise Forbidden(detail="You can only delete your own articles")

        await article.adelete()
        return {"deleted": True, "article_id": id}

    @action(methods=["POST"], detail=True)
    @api.post(
        "/{id}/publish",
        auth=[JWTAuthentication()],
        guards=[IsAuthenticated()]
    )
    async def publish(self, request, id: int):
        """POST /articles/{id}/publish - Publish an article."""
        auth = request.get("auth", {})
        user_id = auth.get("user_id")

        try:
            article = await Article.objects.aget(id=id)
        except Article.DoesNotExist:
            raise NotFound(detail=f"Article {id} not found")

        # Check ownership
        if article.author_id != user_id:
            raise Forbidden(detail="You can only publish your own articles")

        article.published = True
        await article.asave()

        return {"published": True, "article_id": id}
```

### Step 4: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Start the Server

```bash
python manage.py runbolt --host 0.0.0.0 --port 8000
```

### Step 6: Test the Complete API

```bash
# Register a user
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"secret123"}' \
  http://localhost:8000/auth/register

# Login and get token
TOKEN=$(curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret123"}' \
  http://localhost:8000/auth/login | jq -r .access_token)

# Create an article
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title":"My First Article",
    "content":"This is the content of my first article.",
    "published":false
  }' \
  http://localhost:8000/articles

# List articles
curl http://localhost:8000/articles

# Get specific article
curl http://localhost:8000/articles/1

# Publish article
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/articles/1/publish

# Update article
curl -X PATCH \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"My Updated Article"}' \
  http://localhost:8000/articles/1

# Delete article
curl -X DELETE \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/articles/1
```

---

## Next Steps

Congratulations! You now have a solid foundation in Django-Bolt. Here's what to explore next:

### Documentation

- **[Class-Based Views Guide](CLASS_BASED_VIEWS.md)** - Deep dive into APIView, ViewSet, and ModelViewSet
- **[Pagination Guide](PAGINATION.md)** - Learn about PageNumber, LimitOffset, and Cursor pagination
- **[Authentication & Security](SECURITY.md)** - Advanced JWT configuration, token revocation, and API keys
- **[Middleware Guide](MIDDLEWARE.md)** - Custom middleware, CORS, rate limiting, and compression
- **[Exception Handling](EXCEPTIONS.md)** - Custom exceptions and error responses
- **[OpenAPI/Swagger](OPENAPI_ERROR_RESPONSES.md)** - Auto-generated API documentation
- **[Django Admin Integration](DJANGO_ADMIN.md)** - Use Django-Bolt with Django's admin panel
- **[Testing Utilities](TESTING_UTILITIES.md)** - Testing tools and patterns

### Advanced Topics

- **Dependency Injection** - Use `Depends()` for reusable logic
- **Background Tasks** - Offload work to background tasks
- **WebSockets** - Real-time communication (coming soon)
- **GraphQL** - GraphQL support (coming soon)

### Community & Support

- **GitHub Issues** - Report bugs or request features
- **GitHub Discussions** - Ask questions and share your projects
- **Contributing** - Check out the contributing guide to help improve Django-Bolt

### Performance Tips

1. **Use async Django ORM methods**: `aget()`, `acreate()`, `afilter()`, etc.
2. **Optimize queries**: Use `select_related()` and `prefetch_related()`
3. **Run multi-process**: Use `--processes` flag for production
4. **Enable compression**: Automatic for responses >1KB
5. **Cache aggressively**: Use Django's cache framework
6. **Monitor performance**: Use Django-Bolt's built-in logging

---

**Happy Building with Django-Bolt!** 🚀

Built with ⚡ by developers who need speed without sacrificing Python's elegance.

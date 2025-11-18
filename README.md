<div align="center">
  <img src="docs/logo.png" alt="Django-Bolt Logo" width="400"/>
</div>

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/django-bolt?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/django-bolt)

# High-Performance Fully Typed API Framework for Django

Your first question might be: why? Well, consider this: **Faster than _FastAPI_, but with Django ORM, Django Admin, and Django packages**. That’s exactly what this project achieves. Django-Bolt is a high-performance API framework for Django, providing Rust-powered API endpoints capable of 60k+ RPS. Similar to Django REST Framework or Django Ninja, it integrates seamlessly with existing Django projects while leveraging Actix Web for HTTP handling, PyO3 to bridge Python async handlers with Rust's async runtime, and msgspec for fast serialization. You can deploy it directly—no gunicorn or uvicorn needed.

## 🚀 Quick Start

### Installation 🎉

```bash
pip install django-bolt
```

**📖 Full Documentation:** (Coming Soon).

### Run Your First API

```python
# myproject/api.py
from django_bolt import BoltAPI
from django.contrib.auth import get_user_model
import msgspec

User = get_user_model()

api = BoltAPI()

class UserSchema(msgspec.Struct):
    id: int
    username: str


@api.get("/users/{user_id}")
async def get_user(user_id: int) -> UserSchema: # 🎉 Reponse is type validated
    user = await User.objects.aget(id=user_id) # 🤯 Yes and Django orm works without any setup
    return {"id": user.id, "username": user.username} # or you could just return the queryset

```

```python
# myproject/settings.py
INSTALLED_APPS = [
    ...
    "django_bolt"
    ...
]
```

```bash
# Start the server
python manage.py runbolt --dev  # for development with reload enabled
[django-bolt] OpenAPI docs enabled at /docs
[django-bolt] Django admin enabled at http://0.0.0.0:8000/admin/ #django admin
[django-bolt] Static files serving enabled
[django-bolt] Found 94 routes
[django-bolt] Registered middleware for 83 handlers
[django-bolt] Starting server on http://0.0.0.0:8000
[django-bolt] Workers: 1, Processes: 1
[django-bolt] OpenAPI docs enabled at http://0.0.0.0:8000/docs/ #swagger docs builtin

python manage.py runbolt --processes 8 #for deployment (depends on your cpu cores)
# processes are separate processes that handle request 1 actix worker and 1 python eventloop.
```

---

**Key Features:**

- 🚀 **High Performance** - Rust-powered HTTP server (Actix Web + Tokio + PyO3)
- 🔐 **Authentication in Rust** - JWT/API Key/Session validation without Python GIL
- 📦 **msgspec Serialization** - 5-10x faster than standard JSON
- 🎯 **Django Integration** - Use your existing Django models and other django features you love (django admin, django packages)
- 🔄 **Async/Await** - Full async support with Python coroutines
- 🎛️ **Middleware System** - CORS, rate limiting, compression (gzip/brotli/zstd)
- 🔒 **Guards & Permissions** - DRF and Litestar inspired route protection
- 📚 **OpenAPI Support** - 7 render plugins (Swagger, ReDoc, Scalar, RapidDoc, Stoplight, JSON, YAML)
- 📡 **Streaming Responses** - SSE, long-polling, async generators
- 🎨 **Class-Based Views** - ViewSet and ModelViewSet with DRF-style conventions

## 📊 Performance Benchmarks

> **⚠️ Disclaimer:** Django-Bolt is a **feature-incomplete framework** currently in development. Benchmarks were run on a Ryzen 5600G with 16GB RAM (8 processes × 1 worker, C=100 N=10,000) on localhost. Performance will vary significantly based on hardware, OS, configuration, and workload.
>
> **📁 Resources:** Example project available at [python/example/](python/example/). Run benchmarks with `make save-bench` or see [scripts/benchmark.sh](scripts/benchmark.sh).

### Standard Endpoints

| Endpoint Type                  | Requests/sec     |
| ------------------------------ | ---------------- |
| Root endpoint                  | **~100,000 RPS** |
| JSON parsing/validation (10kb) | **~83,700 RPS**  |
| Path + Query parameters        | **~85,300 RPS**  |
| HTML response                  | **~100,600 RPS** |
| Redirect response              | **~96,300 RPS**  |
| Form data handling             | **~76,800 RPS**  |
| ORM reads (SQLite, 10 records) | **~13,000 RPS**  |

### Streaming Performance (Async)

**Server-Sent Events (SSE) with 10,000 concurrent clients (60 Second load time):**

- **Total Throughput:** 9,489 messages/sec
- **Successful Connections:** 10,000 (100%)
- **Avg Messages per Client:** 57.3 messages
- **Data Transfer:** 14.06 MB across test
- **CPU Usage:** 11.9% average during test (peak: 101.9%)
- **Memory Usage:** 236.1 MB

> **Note:** Async streaming is recommended for high-concurrency scenarios (10k+ concurrent connections). It has no thread limits and can handle sustained load efficiently. For sync streaming details and thread limit configuration, see [docs/RESPONSES.md](docs/RESPONSES.md).

**Why so fast?**

- HTTP Parsing and Response is handled by Actix-rs framework (one of the fastest in the world)
- Request routing uses matchit (zero-copy path matching)
- JSON serialization with msgspec (5-10x faster than stdlib)

---

## ✅ What's Complete

### Core Framework ✅

- ✅ **Rust HTTP Server** - Actix Web with tokio async runtime
- ✅ **Fast Routing** - matchit-based routing with path parameters (`/items/{id}`)
- ✅ **Async Handlers** - Full async/await support (enforced async handlers)
- ✅ **Request/Response** - msgspec-based validation and serialization
- ✅ **Multiple Response Types**:
  - `JSON` - msgspec-serialized JSON responses
  - `PlainText` - Plain text responses
  - `HTML` - HTML responses
  - `Redirect` - HTTP redirects
  - `File` - File downloads (in-memory)
  - `FileResponse` - Streaming file responses (handled in Rust)
  - `StreamingResponse` - Async streaming for large payloads
- ✅ **Parameter Injection**:
  - Path parameters (`/items/{id}`)
  - Query parameters (`?page=1&limit=10`)
  - Headers (`Annotated[str, Header("x-api-key")]`)
  - Cookies (`Annotated[str, Cookie("session")]`)
  - Form data (`Annotated[str, Form("username")]`)
  - File uploads (`Annotated[bytes, File("upload")]`)
  - Request body (msgspec.Struct)
- ✅ **Dependency Injection** - `Depends()` system for reusable dependencies
- ✅ **Django ORM Integration** - Full access to Django models (async methods)
- ✅ **Multi-Process Scaling** - SO_REUSEPORT for horizontal scaling
- ✅ **Auto-Discovery** - Finds `api.py` in project root and all installed apps

### Middleware System ✅

- ✅ **Global Middleware** - Apply to all routes via `BoltAPI(middleware=[...])`
- ✅ **Per-Route Middleware** - `@middleware`, `@rate_limit`, `@cors` decorators
- ✅ **CORS Middleware** - Full CORS support with preflight handling
  - Django settings integration (`CORS_ALLOWED_ORIGINS`, `CORS_ALLOW_ALL_ORIGINS`)
  - Route-level overrides with `@cors()` decorator
  - Origin validation, credentials support, preflight caching
  - Runs entirely in Rust (zero GIL overhead)
- ✅ **Rate Limiting** - Token bucket algorithm (in Rust, no GIL)
- ✅ **Compression** - Automatic gzip/brotli/zstd compression (client-negotiated)
- ✅ **Skip Middleware** - `@skip_middleware("cors", "rate_limit", "compression")`
- ✅ **Middleware Config** - Dictionary-based configuration

### Authentication & Authorization ✅

- ✅ **JWT Authentication** - **Complete** (runs in Rust without GIL)

  - Algorithms: HS256, HS384, HS512, RS256, RS384, RS512, ES256, ES384, ES512
  - Token validation in Rust (zero Python overhead)
  - Expiration validation (`exp`) and not-before (`nbf`) checks
  - Custom claims support with audience/issuer validation
  - Django User integration helpers
  - Token revocation support (optional: `InMemoryRevocation`, `DjangoCacheRevocation`, `DjangoORMRevocation`)

- ✅ **API Key Authentication** - **Complete** (runs in Rust without GIL)

  - Header-based API keys (Bearer or ApiKey prefix)
  - Per-key permissions
  - Constant-time comparison (timing attack prevention)
  - Fast validation in Rust

- ✅ **Permission Guards** (all run in Rust):

  - `AllowAny()` - Public access
  - `IsAuthenticated()` - Requires valid auth
  - `IsAdminUser()` - Requires admin/superuser
  - `IsStaff()` - Requires staff status
  - `HasPermission("perm")` - Single permission check
  - `HasAnyPermission("p1", "p2")` - OR logic
  - `HasAllPermissions("p1", "p2")` - AND logic

- ✅ **Auth Context** - Request-level auth context with user info, permissions, and backend details
- ✅ **Token Utilities**:

  - `create_jwt_for_user(user, exp_hours=24)` - Generate JWT for Django User
  - Custom claims and permissions support

**📖 See [docs/SECURITY.md](docs/SECURITY.md) for complete authentication documentation.**

### Developer Tools ✅

- ✅ **CLI** - `python -m django_bolt init` for project setup
- ✅ **Management Command** - `python manage.py runbolt` with auto-discovery
- ✅ **Auto-Discovery** - Finds `api.py` in project root and all Django apps
- ✅ **OpenAPI/Swagger** - 7 render plugins: Swagger UI, ReDoc, Scalar, RapidDoc, Stoplight Elements, JSON, YAML
- ✅ **Error Messages** - Clear, structured error messages with Django DEBUG integration
- ✅ **Type Hints** - Full type hint support with msgspec
- ✅ **Dependency Injection** - `Depends()` marker with per-request caching

**📖 See [docs/README.md](docs/README.md) for complete documentation index.**

---

### Request Flow

```
HTTP Request → Actix Web (Rust)
           ↓
    Route Matching (matchit)
           ↓
    Middleware Pipeline (Rust - no GIL)
      - CORS
      - Rate Limiting
           ↓
    Authentication (Rust - no GIL)
      - JWT validation (HS256/384/512, RS256/384/512, ES256/384)
      - API Key validation (constant-time comparison)
      - Session validation (Django session integration)
           ↓
    Guards/Permissions (Rust - no GIL)
      - IsAuthenticated
      - IsAdminUser
      - HasPermission
           ↓
    Python Handler (PyO3 bridge)
           ↓
    Parameter Extraction & Validation (msgspec)
           ↓
    Handler Execution (async Python)
      - Django ORM access
      - Business logic
           ↓
    Response Serialization (msgspec)
           ↓
    HTTP Response
```

---

## 📖 Documentation (Coming Soon)

- **[Getting Started Guide](docs/GETTING_STARTED.md)** - Complete tutorial from installation to first API
- **[Security Guide](docs/SECURITY.md)** - Authentication, authorization, CORS, rate limiting
- **[Serializers Guide](docs/SERIALIZERS.md)** - Type-safe validation, nested serializers, Django model integration
- **[Middleware Guide](docs/MIDDLEWARE.md)** - CORS, rate limiting, custom middleware
- **[Responses Guide](docs/RESPONSES.md)** - All response types and streaming
- **[Class-Based Views](docs/CLASS_BASED_VIEWS.md)** - ViewSet and ModelViewSet patterns
- **[OpenAPI Guide](docs/OPENAPI.md)** - Auto-generated API documentation
- **[Pagination Guide](docs/PAGINATION.md)** - PageNumber, LimitOffset, Cursor pagination
- **[Logging Guide](docs/LOGGING.md)** - Request/response logging and metrics
- **[Full Documentation Index](docs/README.md)** - Complete list of all documentation

---

## 📖 Usage Examples

### Basic Routes

```python
from django_bolt import BoltAPI
import msgspec
from typing import Optional

api = BoltAPI()

# Simple GET
@api.get("/hello")
async def hello():
    return {"message": "Hello, World!"}

# Path parameters
@api.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

# Query parameters
@api.get("/search")
async def search(q: str, limit: int = 10):
    return {"query": q, "limit": limit}

# Request body with validation
class CreateUserRequest(msgspec.Struct):
    username: str
    email: str
    age: int

@api.post("/users", response_model=CreateUserRequest)
async def create_user(user: CreateUserRequest):
    # Validated automatically
    return user
```

### Authentication & Guards

```python
from django_bolt import BoltAPI
from django_bolt.auth import (
    JWTAuthentication,
    APIKeyAuthentication,
    IsAuthenticated,
    IsAdminUser,
    HasPermission,
)

api = BoltAPI()

# JWT Authentication
@api.get(
    "/protected",
    auth=[JWTAuthentication()],
    guards=[IsAuthenticated()]
)
async def protected_route(request):
    auth = request.get("auth", {})
    user_id = auth.get("user_id")
    return {"message": f"Hello, user {user_id}"}

# API Key Authentication
@api.get(
    "/api-data",
    auth=[APIKeyAuthentication(api_keys={"key1", "key2"})],
    guards=[IsAuthenticated()]
)
async def api_data(request):
    return {"message": "API key authenticated"}

# Permission-based access
@api.post(
    "/articles",
    auth=[JWTAuthentication()],
    guards=[HasPermission("articles.create")]
)
async def create_article(request):
    return {"message": "Article created"}

# Create JWT token for Django user
from django_bolt.auth import create_jwt_for_user
from django.contrib.auth.models import User

@api.post("/login")
async def login(username: str, password: str):
    user = await User.objects.aget(username=username)
    # Verify password...
    token = create_jwt_for_user(user, exp_hours=24)
    return {"access_token": token, "token_type": "bearer"}
```

**📖 See [docs/SECURITY.md](docs/SECURITY.md) for complete authentication documentation.**

### Middleware & CORS

```python
from django_bolt import BoltAPI
from django_bolt.middleware import cors, rate_limit, skip_middleware

# Option 1: Use Django settings (recommended for production)
# In settings.py:
# CORS_ALLOWED_ORIGINS = ["https://example.com", "https://app.example.com"]
# CORS_ALLOW_CREDENTIALS = True
# CORS_MAX_AGE = 3600

api = BoltAPI()  # Automatically reads Django CORS settings

# Option 2: Global middleware config
api = BoltAPI(
    middleware_config={
        "cors": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "credentials": True,
            "max_age": 3600,
        }
    }
)

# Option 3: Per-route CORS override (overrides global/Django settings)
@api.get("/public-api")
@cors(origins=["*"], credentials=False)  # Allow all origins
async def public_endpoint():
    return {"message": "Public endpoint with custom CORS"}

# CORS with credentials and specific origins
@api.post("/auth-endpoint")
@cors(origins=["https://app.example.com"], credentials=True, max_age=3600)
async def auth_endpoint():
    return {"message": "Authenticated endpoint with CORS"}

# Rate limiting (runs in Rust, no GIL)
@api.get("/limited")
@rate_limit(rps=100, burst=200, key="ip")  # 100 req/s with burst of 200
async def limited_endpoint():
    return {"message": "Rate limited"}

# Rate limiting by user ID
@api.get("/user-limited", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
@rate_limit(rps=50, burst=100, key="user")
async def user_limited():
    return {"message": "Per-user rate limiting"}

# Skip global middleware
@api.get("/no-cors")
@skip_middleware("cors", "rate_limit")
async def no_cors():
    return {"message": "Middleware skipped"}
```

**📖 See [docs/MIDDLEWARE.md](docs/MIDDLEWARE.md) for complete middleware documentation.**

### Django ORM Integration

```python
from django_bolt import BoltAPI
from django.contrib.auth.models import User
from myapp.models import Article

api = BoltAPI()

@api.get("/users/{user_id}")
async def get_user(user_id: int):
    # Use Django's async ORM methods
    user = await User.objects.aget(id=user_id)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }

@api.get("/articles")
async def list_articles(limit: int = 10):
    # Async query with select_related
    articles = await Article.objects.select_related("author").all()[:limit]
    return [
        {
            "id": a.id,
            "title": a.title,
            "author": a.author.username,
        }
        async for a in articles
    ]
```

### Response Types

```python
from django_bolt import BoltAPI
from django_bolt.responses import (
    PlainText, HTML, Redirect, File, FileResponse, StreamingResponse
)
import asyncio

api = BoltAPI()

@api.get("/text")
async def text_response():
    return PlainText("Hello, World!")

@api.get("/html")
async def html_response():
    return HTML("<h1>Hello</h1>")

@api.get("/redirect")
async def redirect_response():
    return Redirect("/new-location", status_code=302)

@api.get("/download-memory")
async def download_memory():
    # In-memory file download
    content = b"File contents here"
    return File(content, filename="document.txt", media_type="text/plain")

@api.get("/download-disk")
async def download_disk():
    # Streams file from disk (zero-copy in Rust)
    return FileResponse("/path/to/file.pdf", filename="document.pdf")

@api.get("/stream-sse")
async def stream_sse():
    # Server-Sent Events
    async def generate():
        for i in range(100):
            yield f"data: {i}\n\n"
            await asyncio.sleep(0.1)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

@api.get("/stream-json")
async def stream_json():
    # Streaming JSON (sync generator)
    def generate():
        yield '{"items": ['
        for i in range(1000):
            yield f'{{"id": {i}}}'
            if i < 999:
                yield ','
        yield ']}'

    return StreamingResponse(generate(), media_type="application/json")
```

**📖 See [docs/RESPONSES.md](docs/RESPONSES.md) for complete response documentation.**

### Serializers - Type-Safe Validation

Django-Bolt includes an enhanced serialization system built on `msgspec.Struct` that provides Pydantic-like functionality with 5-10x better performance:

```python
from django_bolt.serializers import Serializer, field_validator, model_validator, Nested
from typing import Annotated
from msgspec import Meta

# Simple serializer with validation
class UserCreate(Serializer):
    username: Annotated[str, Meta(min_length=3, max_length=150)]
    email: str
    password: Annotated[str, Meta(min_length=8)]

    @field_validator('email')
    def validate_email(cls, value):
        if '@' not in value:
            raise ValueError('Invalid email address')
        return value.lower()

# Using in API routes
@api.post("/users", response_model=UserPublic)
async def create_user(data: UserCreate):
    # Validation happens automatically
    user = await User.objects.acreate(**data.to_dict())
    return UserPublic.from_model(user)

# Nested serializers for relationships
class AuthorSerializer(Serializer):
    id: int
    name: str
    email: str

class BlogPostSerializer(Serializer):
    id: int
    title: str
    content: str
    # Nested author - single object
    author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]
    # Nested tags - list of objects
    tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)]

@api.get("/posts/{post_id}")
async def get_post(post_id: int):
    # Efficient query with relationships loaded
    post = await (
        BlogPost.objects
        .select_related("author")
        .prefetch_related("tags")
        .aget(id=post_id)
    )
    return BlogPostSerializer.from_model(post)

# Model validators for cross-field validation
class PasswordChangeSerializer(Serializer):
    old_password: str
    new_password: str
    new_password_confirm: str

    @model_validator
    def validate_passwords(self):
        if self.new_password != self.new_password_confirm:
            raise ValueError("New passwords don't match")
        if self.old_password == self.new_password:
            raise ValueError("New password must be different")

# Auto-generate serializers from Django models
from django_bolt.serializers import create_serializer_set

UserCreate, UserUpdate, UserPublic = create_serializer_set(
    User,
    create_fields=['username', 'email', 'password'],
    update_fields=['username', 'email'],
    public_fields=['id', 'username', 'email', 'date_joined'],
)
```

**Key Features:**

- ✅ **Field-level validation** with `@field_validator` decorator
- ✅ **Model-level validation** with `@model_validator` decorator
- ✅ **Nested serializers** for relationships (ForeignKey, ManyToMany)
- ✅ **Django model integration** - `.from_model()`, `.to_dict()`, `.to_model()`
- ✅ **Auto-generation** - Create serializers from models with `create_serializer()`
- ✅ **Type constraints** - `Meta(min_length=3, max_length=150, pattern=r"...")`
- ✅ **100% type safety** - Full IDE autocomplete and type checking
- ✅ **Performant** Thanks to msgspec.

**📖 See [docs/SERIALIZERS.md](docs/SERIALIZERS.md) for complete serializer documentation.**

---

## 🔧 Development

### Setup

```bash
# Clone repository
git clone https://github.com/FarhanAliRaza/django-bolt.git
cd django-bolt

# Install dependencies
uv sync

# Build Rust extension
make build  # or: maturin develop --release

# Run tests
make test-py
```

### Commands

```bash
# Build
make build          # Build Rust extension
make rebuild        # Clean and rebuild

# Testing
make test-py        # Run Python tests

# Benchmarking
make save-bench     # Run and save results

# Server
```

---

## 🤝 Contributing

Contributions welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test-py`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Areas That Need Help

- Testing and fixing bugs
- Serlialization layer
- Add extension support (adding lifecycle events, making di comprehensive)
- WebSocket support
- Cleaning up code.
- Adding django compatibility layer for views and middlewares
- More examples, tutorials, and docs.

---

## 🙏 Acknowledgments & Inspiration

Django-Bolt stands on the shoulders of giants. We're grateful to the following projects and communities that inspired our design and implementation:

### Core Inspirations

- **[Django REST Framework](https://github.com/encode/django-rest-framework)** - Our syntax, ViewSet patterns, and permission system are heavily inspired by DRF's elegant API design. The class-based views and guard system follow DRF's philosophy of making common patterns simple.

- **[FastAPI](https://github.com/tivy520/fastapi)** - We drew extensive inspiration from FastAPI's dependency injection system, parameter extraction patterns, and modern Python type hints usage. The codebase structure and async patterns heavily influenced our implementation.

- **[Litestar](https://github.com/litestar-org/litestar)** - Our OpenAPI plugin system is adapted from Litestar's excellent architecture. Many architectural decisions around middleware, guards, and route handling were inspired by Litestar's design philosophy.

- **[Robyn](https://github.com/sparckles/Robyn)** - Robyn's Rust-Python integration patterns and performance-first approach influenced our decision to use PyO3 and showed us the potential of Rust-powered Python web frameworks.

### Additional Credits

- **[Actix Web](https://github.com/actix/actix-web)** - The Rust HTTP framework that powers our performance
- **[PyO3](https://github.com/PyO3/pyo3)** - For making Rust-Python interop seamless
- **[msgspec](https://github.com/jcrist/msgspec)** - For blazing-fast serialization
- **[matchit](https://github.com/ibraheemdev/matchit)** - For zero-copy routing

Thank you to all the maintainers, contributors, and communities behind these projects. Django-Bolt wouldn't exist without your incredible work.

---

## 📄 License

Django-Bolt is open source and available under the MIT License.

---

For questions, issues, or feature requests, please visit our [GitHub repository](https://github.com/FarhanAliRaza/django-bolt).

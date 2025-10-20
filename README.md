<div align="center">
  <img src="docs/logo.png" alt="Django-Bolt Logo" width="400"/>

[![Seeking Remote Work](https://img.shields.io/badge/🌍-Actively%20Seeking%20Remote%20Work-success?style=for-the-badge)](mailto:farhanalirazaazeemi@gmail.com)

</div>

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
from django.contrib.auth.models import User
import msgspec

api = BoltAPI()

class UserSchema(msgspec.Struct):
    id: str
    username: str


@api.get("/users/{user_id}")
async def get_user(user_id: int) -> UserSchema: # 🎉 Reponse is type validated
    user = await User.objects.aget(id=user_id) # 🤯 Yes and Django orm works without any setup
    return {"id": user.id, "username": user.username} # or you could just return the queryset

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

# processes are python processes that handle request 1 actix worker
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

> **⚠️ Disclaimer:** Django-Bolt is a **feature-incomplete framework** currently in development. Benchmarks were run on a Ryzen 5600G with 16GB RAM (8 processes × 1 worker, C=100 N=10000) on localhost. Performance will vary significantly based on hardware, OS, configuration, and workload.
>
> **📁 Resources:** Example project available at [python/example/](python/example/). Run benchmarks with `make save-bench` or see [scripts/benchmark.sh](scripts/benchmark.sh).

| Endpoint Type              | Requests/sec    |
| -------------------------- | --------------- |
| Root endpoint              | **~85,000 RPS** |
| JSON parsing/validation    | **~80,000 RPS** |
| Path + Query params        | **~83,500 RPS** |
| HTML/Redirect responses    | **~86,000 RPS** |
| Form data handling         | **~68,000 RPS** |
| ORM reads (SQLite, 10 rec) | **~15,000 RPS** |

**Why so fast?**

- HTTP Parsing and Reponse is handled Actix-rs framework(One of the fastest in the world)
- Request routing uses matchit (zero-copy path matching)
- JSON serialization with msgspec

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
- ✅ **CORS Middleware** - Full CORS support with preflight
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

- ✅ **Session Authentication** - **Complete** (Django session integration)

  - Django session backend integration
  - Automatic user lookup from session
  - Compatible with Django's session middleware
  - Supports both cookie-based and custom session stores

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

---

## 📋 TODO / Roadmap

### Must Have (Blockers) 🚨

- ✅ **Core API functionality** - DONE
- ✅ **Authentication** - DONE (JWT complete)
- ✅ **Tests passing** - DONE (142 passed)
- ✅ **Better error messages** - DONE (Enhanced exception system with structured errors)
- ✅ **Health check endpoints** - DONE (`/health`, `/ready` with custom checks)
- ✅ **Request/Response logging** - DONE (Integrates with Django's logging)
- ❌ **PyPI package** - Missing (currently manual install)

### Should Have (Important) 🎯

- ✅ **Error handling with Django DEBUG integration** - DONE
- ✅ **Structured error responses** (FastAPI-compatible) - DONE
- ✅ **Response compression** - DONE (gzip/brotli/zstd)
- ✅ **OpenAPI/Swagger docs** - DONE (full support for tags, summary, description)
- ✅ **Django admin integration** - DONE
- ⚠️ **API Key auth** - Partial (only in-memory)
- ⚠️ **Testing utilities** - Partial

### Nice to Have (Can defer) 📝

- [ ] **Static file serving** - Efficient static file serving from Rust
- [ ] **Pagination helpers** - Built-in pagination utilities
- [ ] **OAuth2/OpenID** - OAuth2 and OpenID Connect support
- [ ] **API Versioning** - URL/header-based versioning
- [ ] **Content Negotiation** - Accept header-based content negotiation
- [ ] **ETags & Conditional Requests** - Caching optimization
- [ ] **Filtering & Sorting** - Query parameter-based filtering

---

## 🏗️ Architecture

### Core Components

1. **[src/lib.rs](src/lib.rs)** - Main Rust entry point, exposes PyO3 module
2. **[src/server.rs](src/server.rs)** - Actix Web server with multi-worker tokio runtime
3. **[src/router.rs](src/router.rs)** - matchit-based routing
4. **[src/middleware/](src/middleware/)** - Middleware pipeline
   - `auth.rs` - JWT/API Key authentication (zero GIL overhead)
   - `cors.rs` - CORS handling
   - `rate_limit.rs` - Token bucket rate limiting
5. **[src/permissions.rs](src/permissions.rs)** - Guard evaluation
6. **[python/django_bolt/api.py](python/django_bolt/api.py)** - Python decorator-based API
7. **[python/django_bolt/auth/](python/django_bolt/auth/)** - Authentication system
   - `backends.py` - Auth backend classes (compile to Rust metadata)
   - `guards.py` - Permission guard classes
   - `jwt_utils.py` - JWT utilities for Django User integration
   - `middleware.py` - Middleware decorators
   - `token.py` - Token handling
   - `revocation.py` - Token revocation stores

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

### Middleware

```python
from django_bolt import BoltAPI
from django_bolt.middleware import cors, rate_limit, skip_middleware

# Global middleware
api = BoltAPI(
    middleware_config={
        "cors": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "credentials": True,
        }
    }
)

# Per-route rate limiting (runs in Rust, no GIL)
@api.get("/limited")
@rate_limit(rps=100, burst=200, key="ip")  # 100 req/s with burst of 200
async def limited_endpoint():
    return {"message": "Rate limited"}

# Rate limiting by user ID
@api.get("/user-limited", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
@rate_limit(rps=50, burst=100, key="user")
async def user_limited():
    return {"message": "Per-user rate limiting"}

# Custom CORS for specific route
@api.get("/public")
@cors(origins=["https://example.com"], credentials=True, max_age=3600)
async def public_endpoint():
    return {"message": "Public endpoint with CORS"}

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

---

## 🔧 Development

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/django-bolt.git
cd django-bolt

# Install dependencies
pip install -r requirements-dev.txt

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

- Testing utilities and test client
- WebSocket support
- OAuth2/OpenID Connect
- API versioning
- More examples and tutorials

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

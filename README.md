# Django-Bolt ⚡

**High-Performance Python Web Framework with Rust-Powered HTTP Server**

Django-Bolt is an experimental web framework that integrates with existing Django projects to provide a Rust-powered HTTP server (Actix Web) capable of **60k+ RPS** performance. It uses PyO3 to bridge Python async handlers with Rust's async runtime, msgspec for fast serialization, and supports multi-process scaling with SO_REUSEPORT.

**Key Features:**

- 🚀 **60k+ RPS** - Rust-powered HTTP server (Actix Web + Tokio)
- ⚡ **Zero-Copy Request Handling** - PyO3 integration without GIL overhead
- 🔐 **Authentication in Rust** - JWT/API Key validation without Python GIL
- 📦 **msgspec Serialization** - 5-10x faster than standard JSON
- 🎯 **Django ORM Integration** - Use your existing Django models
- 🔄 **Async/Await** - Full async support with Python coroutines
- 🎛️ **Middleware System** - CORS, rate limiting, custom middleware
- 🔒 **Guards & Permissions** - DRF-style route protection

---

## 🚀 Quick Start

### Installation

COMING VERY SOON NEAR YOUR DJANGO PROJECTS

For now you can build and use it locally if you want.

````

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



````

```bash
# Start the server
python manage.py runbolt --host 0.0.0.0 --port 8000 --processes 4 --workers 1
# processes are python processes that handle request 1 actix worker
```

---

## 📊 Performance Benchmarks

Current benchmarks (4 processes × 1 workers on consumer hardware):

| Endpoint Type      | Requests/sec     | Latency (avg) |
| ------------------ | ---------------- | ------------- |
| Root endpoint      | **~64,000 RPS**  | <1ms          |
| JSON parsing       | **~37,000 RPS**  | ~1ms          |
| ORM reads (SQLite) | **~7-9,000 RPS** | ~5ms          |

**Why so fast?**

- Authentication and guards run in Rust without the Python GIL
- Request routing uses matchit (zero-copy path matching)
- No middlwares if dont require any.
- JSON serialization with msgspec
- Multi-process with SO_REUSEPORT (kernel-level load balancing)

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
- ✅ **Skip Middleware** - `@skip_middleware("cors", "rate_limit")`
- ✅ **Middleware Config** - Dictionary-based configuration

### Authentication & Authorization ✅

- ✅ **JWT Authentication** - **Complete** (runs in Rust without GIL)

  - Algorithms: HS256, HS384, HS512, RS256, RS384, RS512, ES256, ES384, ES512
  - Token validation in Rust (zero Python overhead)
  - Expiration validation
  - Custom claims support
  - Django User integration helpers
  - Token revocation support (optional)

- ✅ **API Key Authentication** - **Partial** (runs in Rust without GIL)

  - Header-based API keys
  - Per-key permissions
  - Fast validation in Rust

- ✅ **Permission Guards** (all run in Rust):

  - `AllowAny()` - Public access
  - `IsAuthenticated()` - Requires valid auth
  - `IsAdminUser()` - Requires admin/superuser
  - `IsStaff()` - Requires staff status
  - `HasPermission("perm")` - Single permission check
  - `HasAnyPermission("p1", "p2")` - OR logic
  - `HasAllPermissions("p1", "p2")` - AND logic

- ✅ **Auth Context** - Request-level auth context with user info
- ✅ **Token Utilities**:

  - `create_jwt_for_user(user)` - Generate JWT for Django User
  - `get_current_user(request)` - Get User from auth context
  - `extract_user_id_from_context(request)` - Get user ID

- ✅ **Token Revocation** (optional):
  - `InMemoryRevocation` - In-memory token blacklist
  - `DjangoCacheRevocation` - Cache-based revocation
  - `DjangoORMRevocation` - Database-backed revocation

### Developer Tools ✅

- ✅ **CLI** - `python -m django_bolt init` for project setup
- ✅ **Management Command** - `python manage.py runbolt`
- ✅ **Auto-Discovery** - Finds APIs in all Django apps
- ✅ **Error Messages** - Clear error messages
- ✅ **Type Hints** - Full type hint support with msgspec
- ✅ **Test Suite** - Comprehensive tests covering auth, guards, middleware

---

## ⚠️ Partially Complete / In Progress

### Session Authentication ⚠️

**Status:** Basic implementation exists, needs optimization and testing

**What Works:**

- Django session cookie validation
- Basic user authentication via sessions

**What's Missing:**

- [ ] Optimize session lookups (currently hits Python for every request)
- [ ] Comprehensive test coverage
- [ ] Documentation and examples
- [ ] Session middleware integration

**Why It's Slower:** Session auth requires Python execution (Django session lookup) for each request, unlike JWT/API Key which run entirely in Rust.

---

## 📋 TODO / Roadmap

### High Priority 🔥

- [ ] **OpenAPI/Swagger** - Auto-generated API documentation from route definitions
- [ ] **Request Validation** - More advanced validation (custom validators, nested models)
- [ ] **Response Compression** - gzip/brotli compression in Rust
- [ ] **Request Logging** - Structured logging (configurable)
- [ ] **Pagination** - Built-in pagination helpers
- [ ] **Static File Serving** - Efficient static file serving from Rust

### Medium Priority 🎯

- [ ] **Testing Utilities** - Test client and fixtures
- [ ] **Admin Interface** - Django admin integration
- [ ] **Health Checks** - `/health` and `/ready` endpoints

### Low Priority 📝

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
    Route Matching (matchit - zero copy)
           ↓
    Middleware Pipeline (Rust - no GIL)
      - CORS
      - Rate Limiting
           ↓
    Authentication (Rust - no GIL)
      - JWT validation
      - API Key validation
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

**Key Performance Points:**

- **No GIL** until Python handler execution
- Authentication, guards, and middleware run in Rust
- Multi-process with SO_REUSEPORT (kernel load balancing)
- msgspec serialization (5-10x faster than standard JSON)

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
    IsAuthenticated,
    IsAdminUser,
    HasPermission,
)

api = BoltAPI()

# Require JWT authentication
@api.get(
    "/protected",
    auth=[JWTAuthentication()],
    guards=[IsAuthenticated()]
)
async def protected_route(request):
    auth_context = request.get("auth", {})
    user_id = auth_context.get("user_id")
    return {"message": f"Hello, user {user_id}"}

# Require admin access
@api.get(
    "/admin",
    auth=[JWTAuthentication()],
    guards=[IsAdminUser()]
)
async def admin_only(request):
    return {"message": "Admin access"}

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

### Middleware

```python
from django_bolt import BoltAPI
from django_bolt.auth import cors, rate_limit, skip_middleware

# Global middleware
api = BoltAPI(
    middleware_config={
        "cors": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
        }
    }
)

# Per-route rate limiting
@api.get("/limited")
@rate_limit(rps=10, burst=20)
async def limited_endpoint():
    return {"message": "Rate limited to 10 req/s"}

# Custom CORS for specific route
@api.get("/public")
@cors(origins=["*"])
async def public_endpoint():
    return {"message": "Public endpoint with CORS"}

# Skip global middleware
@api.get("/no-cors")
@skip_middleware("cors")
async def no_cors():
    return {"message": "CORS disabled for this route"}
```

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
from django_bolt.responses import PlainText, HTML, Redirect, FileResponse

api = BoltAPI()

@api.get("/text")
async def text_response():
    return PlainText("Hello, World!")

@api.get("/html")
async def html_response():
    return HTML("<h1>Hello</h1>")

@api.get("/redirect")
async def redirect_response():
    return Redirect("/new-location")

@api.get("/download")
async def download_file():
    # Streams file from Rust (zero-copy)
    return FileResponse("/path/to/file.pdf", filename="document.pdf")
```

### Streaming Responses

```python
from django_bolt import BoltAPI
from django_bolt.responses import StreamingResponse
import asyncio

api = BoltAPI()

@api.get("/stream")
async def stream_data():
    async def generate():
        for i in range(100):
            yield f"data: {i}\n\n"
            await asyncio.sleep(0.1)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

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
make smoke          # Quick smoke tests
make orm-smoke      # ORM-specific tests

# Benchmarking
make bench          # Run benchmarks
make save-bench     # Run and save results
make bench C=100 N=50000  # Custom benchmark

# Server
make run-bg HOST=127.0.0.1 PORT=8000 P=2 WORKERS=2
```

---

## 📁 Project Structure

```
django-bolt/
├── src/                              # Rust server code
│   ├── lib.rs                        # PyO3 module entry point
│   ├── server.rs                     # Actix Web server
│   ├── router.rs                     # matchit routing
│   ├── middleware/
│   │   ├── mod.rs
│   │   ├── auth.rs                   # JWT/API Key auth (no GIL)
│   │   ├── cors.rs                   # CORS handling
│   │   └── rate_limit.rs             # Token bucket rate limiting
│   ├── permissions.rs                # Guard evaluation
│   └── streaming.rs                  # Streaming response handling
├── python/django_bolt/               # Python framework
│   ├── api.py                        # BoltAPI class, decorators
│   ├── responses.py                  # Response types
│   ├── exceptions.py                 # HTTP exceptions
│   ├── params.py                     # Parameter markers
│   ├── auth/                         # Authentication system
│   │   ├── __init__.py
│   │   ├── backends.py               # Auth backends
│   │   ├── guards.py                 # Permission guards
│   │   ├── middleware.py             # Middleware decorators
│   │   ├── jwt_utils.py              # JWT utilities
│   │   ├── token.py                  # Token handling
│   │   └── revocation.py             # Token revocation
│   ├── management/commands/
│   │   └── runbolt.py                # Django management command
│   ├── cli.py                        # django-bolt CLI
│   ├── tests/                        # Test suite
│   │   ├── test_auth_secret_key.py
│   │   ├── test_guards_auth.py
│   │   ├── test_guards_integration.py
│   │   ├── test_jwt_auth.py
│   │   ├── test_jwt_token.py
│   │   ├── test_middleware.py
│   │   └── test_syntax.py
│   └── bootstrap.py                  # Django setup helper
└── python/examples/testproject/      # Example Django project
    ├── manage.py
    ├── testproject/
    │   ├── settings.py
    │   └── api.py                    # Example routes
    └── users/                        # Example app
        ├── models.py
        └── api.py
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

- Authentication
- OpenAPI/Swagger generation
- More comprehensive tests
- Documentation improvements

---

**Built with ⚡ by developers who need speed without sacrificing Python's elegance**

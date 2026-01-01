<div align="center">
  <img src="docs/logo.png" alt="Django-Bolt Logo" width="400"/>
</div>

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/django-bolt?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/django-bolt)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/FarhanAliRaza/django-bolt)

# High-Performance Fully Typed API Framework for Django

Your first question might be: why? Well, consider this: **Faster than _FastAPI_, but with Django ORM, Django Admin, and Django packages**. That’s exactly what this project achieves. Django-Bolt is a high-performance API framework for Django, providing Rust-powered API endpoints capable of 60k+ RPS. Similar to Django REST Framework or Django Ninja, it integrates seamlessly with existing Django projects while leveraging Actix Web for HTTP handling, PyO3 to bridge Python async handlers with Rust's async runtime, and msgspec for fast serialization. You can deploy it directly—no gunicorn or uvicorn needed.

## 🚀 Quick Start

### Installation 🎉

```bash
pip install django-bolt
```

**📖 Full Documentation:** [bolt.farhana.li](https://bolt.farhana.li/)

> ⚠️ **Note:** Django-Bolt is under active development. Some features are not yet finalized.

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
async def get_user(user_id: int) -> UserSchema: # 🎉 Response is type validated
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
# Start the server in dev mode
python manage.py runbolt --dev
```

---

**Key Features:**

- 🚀 **High Performance** - Rust-powered HTTP server (Actix Web + Tokio + PyO3)
- 🔐 **[Authentication](https://bolt.farhana.li/topics/authentication/)** - JWT/API Key validation in Rust without Python GIL
- 🔒 **[Permissions & Guards](https://bolt.farhana.li/topics/permissions/)** - Route protection with IsAuthenticated, HasPermission, etc.
- 🎛️ **[Middleware](https://bolt.farhana.li/topics/middleware/)** - CORS, rate limiting, compression, Django middleware integration
- 📦 **[Serializers](https://bolt.farhana.li/topics/serializers/)** - msgspec-based validation (5-10x faster than stdlib)
- 🎯 **[Django ORM](https://bolt.farhana.li/topics/async-orm/)** - Full async ORM support with your existing models
- 📡 **[Responses](https://bolt.farhana.li/topics/responses/)** - JSON, HTML, streaming, SSE, file downloads
- 📚 **[OpenAPI](https://bolt.farhana.li/topics/openapi/)** - Auto-generated docs (Swagger, ReDoc, Scalar, RapidDoc)
- 🎨 **[Class-Based Views](https://bolt.farhana.li/topics/class-based-views/)** - ViewSet and ModelViewSet patterns
- 🧪 **[Testing](https://bolt.farhana.li/topics/testing/)** - Built-in test client for API testing

## 📊 Performance Benchmarks

> **⚠️ Disclaimer:** Django-Bolt is a **feature-incomplete framework** currently in development. Benchmarks were run on a Ryzen 5600G with 16GB RAM (8 processes × 1 worker, C=100 N=10,000) on localhost. Performance will vary significantly based on hardware, OS, configuration, and workload.
>
> **📁 Resources:** Example project available at [python/example/](python/example/). Run benchmarks with `just save-bench` or see [scripts/benchmark.sh](scripts/benchmark.sh).

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

> **Note:** Async streaming is recommended for high-concurrency scenarios (10k+ concurrent connections). It has no thread limits and can handle sustained load efficiently.

**Why so fast?**

- HTTP Parsing and Response is handled by Actix-rs framework (one of the fastest in the world)
- Request routing uses matchit (zero-copy path matching)
- JSON serialization with msgspec (5-10x faster than stdlib)

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
just build  # or: maturin develop --release
# Run tests
just test-py
# for linting
just lint-lib
```

### Commands

```bash
# Build
just build          # Build Rust extension
just rebuild        # Clean and rebuild

# Testing
just test-py        # Run Python tests

# Benchmarking
just save-bench     # Run and save results

```

---

## 🤝 Contributing

Contributions welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`just test-py`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Areas That Need Help

- Testing and fixing bugs
- Serlialization layer
- Add extension support (adding lifecycle events, making di comprehensive)
- Cleaning up code.
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

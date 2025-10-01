# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django-Bolt is a high-performance API framework for Django (similar to Django REST Framework) that provides Rust-powered API endpoints with 60k+ RPS performance. It integrates with existing Django projects, using Actix Web for HTTP handling, PyO3 to bridge Python handlers with Rust's async runtime, msgspec for fast serialization, and supports multi-process scaling with SO_REUSEPORT.

## Installation & Setup

```bash
# 1. Create a standard Django project
django-admin startproject myproject
cd myproject
# 3. Initialize Django-Bolt in your project
uv run django-bolt init  # Adds django_bolt to INSTALLED_APPS and creates api.py template
```

## Key Commands

### Development

```bash
# Build Rust extension (required after Rust changes)
make build  # or: uv run maturin develop --release

# Run server (from Django project directory)
python manage.py runbolt --host 0.0.0.0 --port 8000 --processes 2 --workers 2
# Or for background multi-process:
make run-bg HOST=127.0.0.1 PORT=8000 P=2 WORKERS=2

# Quick tests (from testproject example)
make smoke  # Test basic endpoints
make orm-smoke  # Test ORM endpoints

# Benchmarks
make save-bench  # Run full benchmark suite and save results
make bench C=100 N=50000  # Custom benchmark (100 concurrent, 50k requests)

# Database (standard Django commands)
python manage.py migrate
python manage.py makemigrations [app_name]

# Clean/rebuild
make clean  # Remove build artifacts
make rebuild  # Full clean and rebuild
```

## Architecture

### Core Components

1. **Rust Server (`src/lib.rs`)**: Actix Web server handling HTTP, routing via matchit, multi-worker tokio runtime. Dispatches to Python via PyO3.

2. **Python API (`python/django_bolt/api.py`)**: Decorator-based routing (`@api.get/post/put/patch/delete`) with:

   - Async-only handlers (enforced)
   - msgspec for request/response validation
   - Path/query parameter extraction via type hints
   - Response models with automatic serialization
   - Support for PlainText, HTML, Redirect, File responses

3. **Django Integration (`python/django_bolt/bootstrap.py`)**: Ensures Django is properly configured using the project's `DJANGO_SETTINGS_MODULE`. Falls back to minimal config if settings module is not found.

4. **Management Command (`runbolt`)**: Auto-discovers APIs from installed apps, merges routes, supports multi-process scaling with SO_REUSEPORT. Looks for `api.py` files in the project root and installed apps.

### Request Flow

1. HTTP request → Actix Web (Rust)
2. Route matching → Python callback via PyO3
3. Parameter extraction from path/query/body
4. Handler execution (async) → msgspec validation
5. Response serialization → HTTP response

## API Development

### Defining Routes

Create an `api.py` file in your Django project root (e.g., `myproject/api.py`):

```python
from django_bolt import BoltAPI
import msgspec
from typing import Optional

api = BoltAPI()

class Item(msgspec.Struct):
    name: str
    price: float

@api.get("/items/{item_id}")
async def get_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@api.post("/items", response_model=Item)
async def create_item(item: Item) -> Item:
    return item
```

The `runbolt` management command will automatically discover this file.

### Parameter Types

- **Path params**: Function arguments matching `{param}` in path
- **Query params**: Optional function arguments with defaults
- **Request body**: msgspec.Struct type hint
- **Headers/Cookies**: Use `Annotated[str, Header()]` or `Cookie()`
- **Forms/Files**: Use `Annotated[str, Form()]` or `File()`

### Response Types

- Return dict/list for JSON (auto-serialized)
- Use `response_model=` for validation
- Return `PlainText()`, `HTML()`, `Redirect()`, `File()` for other types
- Raise `HTTPException(status_code=, detail=)` for errors

## Performance Targets

Current benchmarks (2 processes × 2 workers):

- Root endpoint: ~64k RPS
- JSON parsing: ~37k RPS
- ORM reads: ~7-9k RPS (SQLite)

Optimization areas:

- Rust-side JSON serialization for large payloads
- Connection pooling for PostgreSQL
- Better async handler integration with pyo3-asyncio

## Testing

```bash
# Python tests
make test-py  # or: uv run pytest python/django_bolt/tests -vv

# Performance tests
make perf-test  # High-concurrency benchmark
make orm-test   # ORM-specific benchmark
```

## Project Structure

- `src/`: Rust server code
- `python/django_bolt/`: Python framework code
  - `api.py`: Route decorators and request handling
  - `bootstrap.py`: Django configuration helper
  - `management/commands/runbolt.py`: Server management command
  - `cli.py`: Django-Bolt CLI for project initialization
- `python/examples/testproject/`: Example Django project (standard Django structure)
  - `manage.py`: Django management script
  - `testproject/settings.py`: Django settings
  - `testproject/api.py`: Main API routes
  - `users/`: Django app with models and API routes

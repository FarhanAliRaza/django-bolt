# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django-Bolt is a high-performance Python web framework that combines Django's ORM and ecosystem compatibility with a Rust-powered HTTP server (Actix Web). The architecture uses PyO3 to bridge Python handlers with Rust's async runtime, targeting 100k+ RPS for simple endpoints while maintaining Django compatibility.

## Key Commands

### Development

```bash
# Build the Rust extension and develop locally
make develop

# Run the example server
make run  # Foreground (default port 8000)
make run-bg  # Background with PID tracking

# Test endpoints
make smoke  # Quick test of /hello endpoint
make bench  # Run Apache Bench performance test (50k requests, 100 concurrent)

# Database operations
make migrate  # Run Django migrations
make makemigrations  # Create new migrations
make orm-smoke  # Test ORM connectivity
make create-user  # Create demo user (username: demo, password: demo)

# Clean and rebuild
make clean  # Clean Rust build artifacts
make reinstall  # Full clean + rebuild
```

### Django-Bolt CLI

```bash
# Run server via CLI
uv run django-bolt run --host 0.0.0.0 --port 8000

# Database management
uv run django-bolt migrate
uv run django-bolt makemigrations [app_name]
uv run django-bolt migrations  # Show migration status
```

## Architecture

### Core Components

1. **Rust Server (`src/lib.rs`)**: Actix Web server that receives HTTP requests and dispatches to Python handlers via PyO3. Handles the event loop, HTTP parsing, and response building.

2. **Python API (`python/django_bolt/api.py`)**: Simple routing decorator system (`@api.get`, `@api.post`) that maps HTTP methods/paths to Python handlers. Handlers receive request dicts and return JSON-serializable data.

3. **Bootstrap System (`python/django_bolt/bootstrap.py`)**: Two-mode Django configuration:

   - **Attached Mode**: Uses existing Django project via `DJANGO_SETTINGS_MODULE`
   - **Embedded Mode**: Auto-configures minimal Django with SQLite for standalone development

4. **Bridge Layer**: PyO3-based FFI that passes requests from Rust to Python and handles response serialization. The `_core` module (built from Rust) provides the `start_server` function.

### Request Flow

1. HTTP request → Actix Web server (Rust)
2. Parse headers/body → Call Python dispatch callback via PyO3
3. Python router finds handler → Execute handler with request dict
4. Handler returns Python data → Serialize and return via Rust
5. Actix sends HTTP response

### Performance Optimizations (Planned)

- Async-only handlers with pyo3-asyncio integration
- Rust-side JSON serialization for large payloads
- Path routing and middleware in Rust
- Multi-process workers with SO_REUSEPORT
- Connection pooling for PostgreSQL

## Development Workflow

### Adding New Endpoints

```python
# In python/examples/embedded_app.py or your app file
from django_bolt import BoltAPI, JSON

api = BoltAPI()

@api.get("/endpoint")
def handler(req):
    # req contains: method, path, headers, body
    return {"data": "value"}  # Auto-serialized to JSON
```

### Testing Changes

1. Run `make develop` after Rust changes
2. Use `make run` to start the server
3. Test with `curl http://localhost:8000/endpoint`
4. Benchmark with `make bench` (requires Apache Bench)

## Database Configuration

### Embedded Mode (Default)

- SQLite with WAL mode enabled
- Database file: `./db.sqlite3`
- Auto-creates tables on first run

### Attached Mode

- Set `DJANGO_SETTINGS_MODULE` to use existing Django project
- Inherits all Django database settings
- Full ORM compatibility maintained

## Dependencies

### Build Requirements

- Python 3.8+ with `uv` package manager
- Rust toolchain (for Maturin builds)
- Maturin for Python/Rust integration

### Runtime Dependencies

- Django 4.2+
- PyO3 (Rust-Python bridge)
- Actix Web (Rust HTTP server)
- msgspec/pydantic (planned for fast serialization)

## Performance Targets

Current baseline (MVP):

- Hello JSON: ~19.5k RPS (target: 60k+)
- ORM read: ~1.96k RPS on SQLite (target: 10-20k with PostgreSQL)

Optimization roadmap in `plan.md` includes async handlers, Rust routing, and multi-process scaling.

!important we do no do legacy or derecation here we are building from scratch. Just remove code.

# Installation

This guide covers how to install Django-Bolt and set it up in your Django project.

## Requirements

Django-Bolt requires:

- Python 3.12 or later
- Django 4.2, 5.0, or 5.1

## Install Django-Bolt

Install using pip:

```bash
pip install django-bolt
```

Or with uv:

```bash
uv add django-bolt
```

## Add to your Django project

### Using the init command

The easiest way to set up Django-Bolt is using the `init` command. Navigate to your Django project directory (where `manage.py` is located) and run:

```bash
django-bolt init
```

This command:

1. Adds `django_bolt` to your `INSTALLED_APPS`
2. Creates an `api.py` file with example routes

### Manual setup

If you prefer to set up manually:

1. Add `django_bolt` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    "django_bolt",  # Add this at the top
    "django.contrib.admin",
    "django.contrib.auth",
    # ... other apps
]
```

2. Create an `api.py` file in your project directory (same folder as `settings.py`):

```python
from django_bolt import BoltAPI

api = BoltAPI()

@api.get("/")
async def root():
    return {"message": "Hello, World!"}
```

## Verify the installation

Start the development server:

```bash
python manage.py runbolt
```

You should see output like:

```
Starting Django-Bolt server on http://0.0.0.0:8000
```

Open your browser to `http://localhost:8000/` and you should see:

```json
{"message": "Hello, World!"}
```

## API documentation

Django-Bolt automatically generates API documentation. After starting the server, visit:

- `http://localhost:8000/docs` - Interactive Swagger UI

## Development mode

For development with auto-reload (restarts when you change Python files):

```bash
python manage.py runbolt --dev
```

## Server options

The `runbolt` command accepts several options:

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `0.0.0.0` | Host to bind to |
| `--port` | `8000` | Port to bind to |
| `--workers` | `1` | Workers per process |
| `--processes` | `1` | Number of processes |
| `--dev` | off | Enable auto-reload |
| `--no-admin` | off | Disable Django admin integration |

Examples:

```bash
# Development with auto-reload
python manage.py runbolt --dev

# Production with multiple workers
python manage.py runbolt --processes 4 --workers 2

# Custom host and port
python manage.py runbolt --host 127.0.0.1 --port 3000
```

## Auto-discovery

Django-Bolt automatically discovers `api.py` files in:

1. Your project directory (where `settings.py` is)
2. Any installed Django app directories

This means you can organize your routes per app:

```
myproject/
    manage.py
    myproject/
        settings.py
        api.py          # Project-level routes
    users/
        models.py
        api.py          # User-related routes
    products/
        models.py
        api.py          # Product-related routes
```

All routes from these files are automatically combined.

## Next steps

Now that you have Django-Bolt installed, continue to the [Quick Start](quickstart.md) tutorial to build your first API.

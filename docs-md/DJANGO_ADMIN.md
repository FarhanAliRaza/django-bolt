# Django Admin Integration

Django-Bolt provides seamless integration with Django's admin interface, allowing you to use the standard Django admin alongside your high-performance API routes.

## Overview

The admin integration uses an ASGI bridge to connect Django-Bolt's routing system with Django's ASGI application. This allows Django admin to work with all its features (sessions, CSRF, middleware) while maintaining django-bolt's high performance for API routes.

## Quick Start

### Create Your API

```python
from django_bolt import BoltAPI

# Admin is auto-enabled by default when django.contrib.admin is installed
api = BoltAPI()

@api.get("/")
async def hello():
    return {"message": "Hello World"}
```

### Run the Server

```bash
# Admin is enabled by default
python manage.py runbolt --host 0.0.0.0 --port 8000
```

The admin interface will be available at `http://localhost:8000/admin/`

### Disable Admin (Optional)

```bash
# Disable admin if you don't need it
python manage.py runbolt --no-admin
```

## Configuration

### Required Settings

Your Django settings must include these apps:

```python
INSTALLED_APPS = [
    'django.contrib.admin',       # Required for admin
    'django.contrib.auth',        # Required for authentication
    'django.contrib.contenttypes',# Required for admin
    'django.contrib.sessions',    # Required for admin
    'django.contrib.messages',    # Optional but recommended
    'django.contrib.staticfiles', # Required for admin CSS/JS
    'django_bolt',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'yourproject.urls'  # Must include admin URLs
```

### URL Configuration

In your `urls.py`:

```python
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
```

## How It Works

### Auto-Detection

Django-Bolt automatically detects and enables admin if:

1. `django.contrib.admin` is in `INSTALLED_APPS`
2. Your `ROOT_URLCONF` contains admin URL patterns
3. The `--no-admin` flag is NOT used

The detection happens at server startup via `should_enable_admin()` in `admin_detection.py`.

### ASGI Bridge Architecture

Django-Bolt uses an ASGI bridge to handle admin requests:

```
HTTP Request → django-bolt Router
              ↓
         /admin/* route?
              ↓ YES
         ASGI Bridge
              ↓
    Django ASGI Application
    (with full middleware stack)
              ↓
         Admin Interface
```

### Route Registration

When you enable admin, django-bolt automatically registers these routes:

- `/admin/` - Admin root (redirects to login)
- `/admin/{path:path}` - Catch-all for all admin URLs
- `/static/{path:path}` - Static files for admin CSS/JS

The catch-all pattern ensures all Django admin URLs work correctly.

## Performance Considerations

### Admin vs API Performance

- **API Routes**: 60,000+ RPS (full Rust performance)
- **Admin Routes**: ~10,000 RPS (Django ASGI performance)

Admin routes run through Django's ASGI handler, so they have Django's performance characteristics, not django-bolt's. This is by design - admin is for management, not high-throughput operations.

### Static Files

Static files for admin are served by django-bolt's static file handler, which provides good performance for CSS/JS assets.

## Advanced Usage

### Custom Admin URL Prefix

Django-bolt auto-detects your admin URL prefix from `ROOT_URLCONF`. If you use a custom prefix:

```python
# urls.py
urlpatterns = [
    path('dashboard/', admin.site.urls),  # Custom prefix
]
```

Django-bolt will automatically detect and use `dashboard/` instead of `admin/`.

### Disable Admin

Admin is enabled by default when `django.contrib.admin` is in your `INSTALLED_APPS`. To disable it:

```bash
# Disable admin via command line flag
python manage.py runbolt --no-admin
```

Note: There is no `enable_admin` parameter in `BoltAPI()`. Admin enablement is controlled solely by the `--no-admin` command-line flag.

### Multiple Processes

Admin works with multiple processes using shared sessions:

```bash
python manage.py runbolt --processes 4 --workers 2
```

Make sure your session backend supports multi-process (e.g., database or cache sessions, not file sessions).

## Troubleshooting

### Admin Returns 404

**Problem**: `/admin/` or `/admin/login/` returns "Not Found"

**Solutions**:
1. Check that `django.contrib.admin` is in `INSTALLED_APPS`
2. Verify `ROOT_URLCONF` is set and includes admin URLs
3. Ensure you're not using the `--no-admin` flag
4. Check server logs for admin registration confirmation
5. Verify admin URL patterns are defined in your `urls.py`

### Empty Response Body

**Problem**: Admin pages return empty body or status 500

**Solutions**:
1. Update to latest django-bolt version (fixed in recent releases)
2. Ensure all required Django apps are in `INSTALLED_APPS`
3. Check that middleware stack includes required middleware
4. Run `python manage.py migrate` to create admin tables

### Static Files Not Loading

**Problem**: Admin CSS/JS not loading

**Solutions**:
1. Ensure `django.contrib.staticfiles` is in `INSTALLED_APPS`
2. Set `STATIC_URL = '/static/'` in settings
3. Run `python manage.py collectstatic` for production
4. Check that static routes are registered (logs show "Static files serving enabled")

### CSRF Token Errors

**Problem**: Admin login fails with CSRF errors

**Solutions**:
1. Ensure `CsrfViewMiddleware` is in `MIDDLEWARE`
2. Check that `SESSION_COOKIE_HTTPONLY = True` is set
3. Clear browser cookies and try again
4. Ensure `SECRET_KEY` is set in settings

## API Reference

### Command Line Options

```bash
python manage.py runbolt [OPTIONS]

Options:
  --no-admin          Disable Django admin integration (admin enabled by default)
  --host HOST         Bind address (default: 127.0.0.1)
  --port PORT         Bind port (default: 8000)
  --processes N       Number of processes (default: 1)
  --workers N         Workers per process (default: 2)
  --dev               Development mode with auto-reload
```

Note: `BoltAPI()` does not have an `enable_admin` parameter. Admin is controlled via the `--no-admin` flag.

### Admin Detection Functions

```python
from django_bolt.admin import (
    is_admin_installed,        # Check if admin is installed
    should_enable_admin,       # Check if admin can be enabled
    detect_admin_url_prefix,   # Get admin URL prefix
    get_admin_route_patterns,  # Get route patterns for admin
    get_admin_info,           # Get admin configuration info
)
```

### ASGI Bridge

```python
from django_bolt.admin import ASGIFallbackHandler

# Create ASGI bridge handler
handler = ASGIFallbackHandler(
    server_host="127.0.0.1",
    server_port=8000
)

# Handle a request
status, headers, body = await handler.handle_request(request)
```

## Examples

### Basic Admin Setup

```python
# api.py
from django_bolt import BoltAPI

# Admin is auto-enabled by default
api = BoltAPI()

@api.get("/api/users")
async def get_users():
    return {"users": []}
```

Run with:
```bash
python manage.py runbolt  # Admin enabled by default
```

### Admin with Custom Models

```python
# models.py
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

# admin.py
from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
```

### Mixing API and Admin

```python
from django_bolt import BoltAPI
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

# Admin auto-enabled when django.contrib.admin is installed
api = BoltAPI()

@api.get("/api/admin/users")
async def list_users():
    """API endpoint to list users (for admin dashboard)"""
    users = await sync_to_async(list)(
        User.objects.all().values('id', 'username', 'email')
    )
    return {"users": users}
```

The admin interface and API endpoints work side-by-side:
- Admin UI: `http://localhost:8000/admin/`
- API endpoint: `http://localhost:8000/api/admin/users`

## Best Practices

1. **Use Admin for Management Only**: Admin is for CRUD operations and management, not high-throughput APIs
2. **Secure Admin Access**: Use strong authentication and limit admin access in production
3. **Separate API and Admin**: Keep API routes under `/api/` and admin under `/admin/`
4. **Monitor Performance**: Admin routes have different performance than API routes
5. **Use Database Sessions**: File-based sessions don't work well with multiple processes

## Limitations

1. **No Hot Reload**: Admin route registration happens at startup; requires restart to pick up changes
2. **ASGI Only**: Admin uses Django's ASGI handler, not WSGI
3. **Session Backend**: File-based sessions may not work correctly with multi-process deployment
4. **Static Files**: In production, consider serving static files via nginx/CDN for better performance

## Related Documentation

- [Testing Utilities](TESTING_UTILITIES.md) - Testing admin integration
- [Async Django](ASYNC_DJANGO.md) - Using Django ORM with django-bolt
- [Exceptions](EXCEPTIONS.md) - Error handling in admin and API routes

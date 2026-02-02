---
icon: lucide/file-image
---

# Static Files

Django-Bolt serves static files directly from Rust using Actix-files, providing high-performance static file delivery without Python overhead.

## Overview

Static files are served with:

- **Streaming responses** - Memory efficient for large files
- **ETag and Last-Modified headers** - Automatic caching support
- **Conditional requests** - 304 Not Modified responses
- **Range requests** - Resumable downloads
- **Content-Type detection** - Automatic MIME type handling
- **Content Security Policy** - Configurable CSP headers

## Configuration

Django-Bolt reads your existing Django static files settings:

```python
# settings.py

# URL prefix for static files
STATIC_URL = "/static/"

# Directory where collectstatic gathers files (primary lookup)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Additional directories to search (optional)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
```

## File lookup order

When a static file is requested, Django-Bolt searches in this order:

1. **STATIC_ROOT** - Collected static files (fastest)
2. **STATICFILES_DIRS** - Additional configured directories
3. **Django staticfiles finders** - App-level static files (e.g., admin)

The first match is returned. Files in `STATIC_ROOT` take priority.

## Django admin integration

Django admin static files are automatically served. No additional configuration is needed - Django-Bolt uses Django's staticfiles finders as a fallback to locate admin CSS, JavaScript, and images.

```python
# Admin works out of the box
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.staticfiles",
    # ...
]
```

## Security

### Directory traversal protection

Django-Bolt blocks directory traversal attacks:

- Paths containing `..` are rejected
- Symlink targets are verified to stay within allowed directories
- Only files (not directories) are served

### Content Security Policy (CSP)

Django-Bolt applies CSP headers to all static file responses. This protects against XSS attacks in HTML files and ensures scripts/styles are loaded only from trusted sources.

Configure CSP using Django 6.0+'s native [`SECURE_CSP`](https://docs.djangoproject.com/en/6.0/ref/csp/) setting:

```python
# settings.py
from django.utils.csp import CSP

SECURE_CSP = {
    "default-src": [CSP.SELF],
    "script-src": [CSP.SELF],
    "style-src": [CSP.SELF, CSP.UNSAFE_INLINE],
    "img-src": [CSP.SELF, "data:"],
}
```

You can also use raw strings:

```python
SECURE_CSP = {
    "default-src": ["'self'"],
    "script-src": ["'self'"],
    "style-src": ["'self'", "'unsafe-inline'"],
    "img-src": ["'self'", "data:"],
}
```

#### CSP constants

Django provides constants via `django.utils.csp.CSP`:

| Constant | Value | Purpose |
|----------|-------|---------|
| `CSP.SELF` | `'self'` | Same origin only |
| `CSP.NONE` | `'none'` | Block all resources |
| `CSP.UNSAFE_INLINE` | `'unsafe-inline'` | Allow inline scripts/styles |
| `CSP.UNSAFE_EVAL` | `'unsafe-eval'` | Allow `eval()` |
| `CSP.STRICT_DYNAMIC` | `'strict-dynamic'` | Trust scripts loaded by trusted scripts |

#### How CSP works

- CSP configuration is read once at server startup
- The header is pre-built for performance (no per-request overhead)
- `CSP.NONCE` values are automatically filtered out (static files cannot inject nonces)

!!! note "Nonces not supported"
    `CSP.NONCE` requires per-request nonce injection which isn't possible for static files. Use `CSP.NONCE` only for dynamic responses served by your Django views.

#### Common CSP directives

| Directive | Purpose | Example |
|-----------|---------|---------|
| `default-src` | Default policy for all content | `[CSP.SELF]` |
| `script-src` | JavaScript sources | `[CSP.SELF, "https://cdn.example.com"]` |
| `style-src` | CSS sources | `[CSP.SELF, CSP.UNSAFE_INLINE]` |
| `img-src` | Image sources | `[CSP.SELF, "data:", "https:"]` |
| `font-src` | Font sources | `[CSP.SELF, "https://fonts.gstatic.com"]` |
| `connect-src` | XHR/WebSocket destinations | `[CSP.SELF, "https://api.example.com"]` |
| `frame-ancestors` | Who can embed this page | `[CSP.NONE]` |
| `upgrade-insecure-requests` | Upgrade HTTP to HTTPS | `[]` (boolean directive) |
| `block-all-mixed-content` | Block mixed HTTP/HTTPS | `[]` (boolean directive) |

## Using with templates

The Django `{% static %}` template tag works as expected:

```html
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <img src="{% static 'img/logo.png' %}" alt="Logo">
    <script src="{% static 'js/app.js' %}"></script>
</body>
</html>
```

## Performance

Static file serving runs primarily in Rust:

- **No Python GIL for configured directories** - Files in `STATIC_ROOT` and `STATICFILES_DIRS` are served without touching Python
- **Django finders fallback** - Only app-level static files (like admin) require a Python call
- **Async I/O** - Non-blocking file reads via Actix
- **Smart read modes** - Sync reads for small files (<256KB), async for large files
- **Efficient caching** - Proper HTTP caching headers reduce server load

### Comparison with alternatives

| Method | RPS (approx) | Notes |
|--------|--------------|-------|
| Django-Bolt (Rust) | 50,000+ | Direct Actix serving |
| WhiteNoise | 10,000 | Python middleware |
| Django dev server | 500 | Not for production |
| Nginx (separate) | 100,000+ | Additional infrastructure |

Django-Bolt provides near-Nginx performance without requiring a separate web server.

## Production deployment

For production, collect static files as usual:

```bash
python manage.py collectstatic
```

Then run Django-Bolt:

```bash
python manage.py runbolt --host 0.0.0.0 --port 8000 --processes 4
```

Static files are served from `STATIC_ROOT` at high performance. No additional web server (Nginx, Apache) is required for static files.

## Troubleshooting

### Static files not found

1. Verify `STATIC_ROOT` is set and contains files:
   ```bash
   python manage.py collectstatic
   ls -la $(python -c "from django.conf import settings; print(settings.STATIC_ROOT)")
   ```

2. Check `STATIC_URL` matches your requests:
   ```python
   # settings.py
   STATIC_URL = "/static/"  # Requests should be /static/css/style.css
   ```

3. For development without collectstatic, ensure `STATICFILES_DIRS` is configured.

### Admin styles missing

Ensure `django.contrib.staticfiles` is in `INSTALLED_APPS` and run `collectstatic`:

```bash
python manage.py collectstatic --noinput
```

### CSP blocking resources

Check browser console for CSP violations. Adjust your CSP directives to allow required sources:

```python
from django.utils.csp import CSP

SECURE_CSP = {
    "script-src": [CSP.SELF, "https://trusted-cdn.com"],
    "style-src": [CSP.SELF, CSP.UNSAFE_INLINE],  # Allow inline styles
}
```

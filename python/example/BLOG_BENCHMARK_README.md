# Blog Homepage Performance Benchmark

## Overview

This benchmark compares the performance of serving an HTML blog homepage with database queries using:
- **Django-Bolt** (ASGI + Rust acceleration)
- **Gunicorn** (Traditional WSGI + Python threads)

### What's Being Tested

Both servers serve an identical blog homepage that:
- Queries **50 blog posts** from SQLite database
- Renders an HTML template with **Tailwind CSS** styling
- Includes performance metrics on the page
- Uses realistic database access patterns

### Performance Characteristics Expected

Based on our earlier research and the 49x URL resolution optimization:

- **Django-Bolt**: Faster async handling, Rust-powered HTTP layer, optimized serialization
- **Gunicorn**: Traditional WSGI, Python-based threading, GIL overhead on multi-threading

## Setup & Running the Benchmark

### Prerequisites

```bash
cd /home/farhan/code/django-bolt/python/example

# Database should already have 50 blog posts
# If not, seed them:
uv run python manage.py shell << 'EOF'
from core.models import Blog
blogs_to_create = []
for i in range(50):
    blogs_to_create.append(
        Blog(
            name=f'Blog Post {i+1}: Understanding Django Performance',
            description=f'In this article, we explore advanced techniques...',
            status='published'
        )
    )
Blog.objects.bulk_create(blogs_to_create)
EOF
```

### Option 1: Django-Bolt Only Benchmark

```bash
# Terminal 1: Start Django-Bolt server
cd /home/farhan/code/django-bolt/python/example
uv run python manage.py runbolt --host 127.0.0.1 --port 8000 --workers 2

# Terminal 2: Run benchmark against Django-Bolt
cd /home/farhan/code/django-bolt/python/example
uv run python bench_blog_performance.py 100
```

### Option 2: Full Comparison (Django-Bolt + Gunicorn)

```bash
# Terminal 1: Start Django-Bolt server
cd /home/farhan/code/django-bolt/python/example
uv run python manage.py runbolt --host 127.0.0.1 --port 8000 --workers 2

# Terminal 2: Start Gunicorn server
cd /home/farhan/code/django-bolt/python/example
uv run gunicorn testproject.wsgi:application \
    --bind 127.0.0.1:8001 \
    --workers 2 \
    --threads 4 \
    --worker-class gthread \
    --access-logfile -

# Terminal 3: Run benchmark
cd /home/farhan/code/django-bolt/python/example
uv run python bench_blog_performance.py 100
```

### Option 3: Quick Visual Test

View the blog homepage in your browser:

```bash
# Start server
uv run python manage.py runbolt --host 127.0.0.1 --port 8000 --dev

# Open browser
# Django-Bolt: http://127.0.0.1:8000/blog
# Django WSGI: http://127.0.0.1:8000/blog/ (requires separate server)
```

## Endpoints

### Django-Bolt (BoltAPI)
- **URL**: `http://127.0.0.1:8000/blog`
- **View**: `testproject/api.py::blog_home_bolt()`
- **Features**: Async database queries, Rust HTTP layer, optimized serialization

### Traditional Django (WSGI)
- **URL**: `http://127.0.0.1:8000/blog/` (with trailing slash)
- **View**: `testproject/views.py::blog_home()`
- **Features**: Sync database queries, Python threads, standard Django rendering

## Benchmark Parameters

The `bench_blog_performance.py` script accepts:

```bash
# Run 100 requests (default)
uv run python bench_blog_performance.py

# Run 500 requests
uv run python bench_blog_performance.py 500

# Run 1000 requests for more stable statistics
uv run python bench_blog_performance.py 1000
```

## Expected Results

Based on the 49x URL resolution optimization and async advantages:

```
Blog Homepage Performance Comparison
=======================================================
Metric              Django-Bolt    Gunicorn      Improvement
---------------------------------------------------------
Min (ms)            8.5            25.2          66.3%
Median (ms)         12.3           35.7          65.5%
Max (ms)            45.2           120.5         62.5%
Speedup             1.0x           2.9x          ✓
```

**Expected Speedup**: Django-Bolt should be **2-3x faster** than Gunicorn for this workload.

### Why Django-Bolt is Faster

1. **Async/Await**: Non-blocking database queries and I/O
2. **Rust HTTP Layer**: Zero-copy routing and request handling
3. **No GIL**: Async Python code doesn't compete for GIL like threaded code
4. **Optimized Serialization**: msgspec for JSON (when used in APIs)
5. **Connection Pooling**: Actix Web manages connections efficiently

### Why Gunicorn is Slower

1. **GIL Contention**: Multiple threads compete for Python's Global Lock
2. **Thread Overhead**: Context switching between worker threads
3. **Blocking I/O**: Database queries block the entire thread
4. **Traditional WSGI**: Synchronous request/response handling

## Files

- **testproject/templates/blog_home.html** - Tailwind CSS styled blog homepage template
- **testproject/views.py::blog_home()** - Traditional Django WSGI view
- **testproject/api.py::blog_home_bolt()** - Django-Bolt async view
- **testproject/urls.py** - URL patterns for both views
- **bench_blog_performance.py** - Benchmark script with HTTP load testing
- **testproject/settings.py** - Django configuration with template directories

## Understanding the Results

### Response Time Components

**Django-Bolt** (`/blog`):
```
Total Time = Database Query (3-5ms) + Template Rendering (2-3ms) + HTTP Overhead (1-2ms)
           ≈ 8-12 ms
```

**Gunicorn** (`/blog/`):
```
Total Time = Database Query (3-5ms) + Template Rendering (2-3ms) + Thread Overhead (15-25ms) + HTTP Overhead (5-10ms)
           ≈ 30-45 ms
```

The extra overhead in Gunicorn comes from:
- Thread scheduling and context switching
- GIL contention with other worker threads
- Synchronous blocking on database queries
- Traditional WSGI protocol overhead

### Metrics Explained

- **Min**: Fastest single request (best case)
- **Median**: 50th percentile (typical case) - **Use this for comparison**
- **Max**: Slowest single request (worst case, includes outliers)
- **Std Dev**: Variability in response times

## Advanced Tuning

### Django-Bolt Tuning

```bash
# Increase workers for multi-core scaling
uv run python manage.py runbolt \
    --host 0.0.0.0 \
    --port 8000 \
    --processes 4 \
    --workers 2 \
    --no-reload

# This starts 4 processes × 2 workers = 8 concurrent handlers
```

### Gunicorn Tuning

```bash
# Match Django-Bolt concurrency (8 concurrent)
uv run gunicorn testproject.wsgi:application \
    --bind 127.0.0.1:8001 \
    --workers 4 \          # 4 worker processes
    --threads 2 \          # 2 threads per worker
    --worker-class gthread \  # Use threaded worker
    --access-logfile -
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000
# Kill it
kill -9 <PID>

# Or use different port
uv run python manage.py runbolt --port 8001
```

### Template Not Found

Make sure `DEBUG = True` in settings.py and templates directory is configured:

```python
# testproject/settings.py
DEBUG = True
TEMPLATES = [{
    'DIRS': [BASE_DIR / 'testproject' / 'templates'],
    ...
}]
```

### No Results from Gunicorn

- Make sure Gunicorn is installed: `uv run pip install gunicorn`
- Check that it's running on port 8001
- Verify URL in benchmark script points to correct port

## Next Steps

1. **Run the benchmark** with default settings (100 requests)
2. **Record the median response times**
3. **Run again** with 500+ requests for more stable results
4. **Compare** Django-Bolt median vs Gunicorn median
5. **Calculate speedup** = Gunicorn median / Django-Bolt median

Expected: Django-Bolt should be 2-3x faster for this I/O-bound HTML rendering workload.

## References

- Performance Analysis: See `PERFORMANCE_ANALYSIS.md` for URL resolution optimization details
- Django-Bolt Docs: Documentation on async views and performance features
- Gunicorn Docs: Configuration and tuning for synchronous WSGI applications

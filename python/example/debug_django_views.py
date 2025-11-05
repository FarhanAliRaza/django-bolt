#!/usr/bin/env python
"""Debug script to trace Django views registration."""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testproject.settings')
django.setup()

from django.urls import get_resolver
from django_bolt.admin.django_view_detection import extract_views_from_patterns, get_django_views
from django_bolt.admin.django_view_routes import DjangoViewRegistrar

print("=" * 80)
print("DEBUGGING DJANGO VIEWS REGISTRATION")
print("=" * 80)

# Step 1: Get all urlpatterns
print("\n[Step 1] Getting Django URL patterns...")
resolver = get_resolver()
all_patterns = resolver.url_patterns
print(f"Found {len(all_patterns)} url patterns")

# Step 2: Extract views from patterns
print("\n[Step 2] Extracting views from patterns...")
extracted = extract_views_from_patterns(all_patterns)
print(f"Extracted {len(extracted)} views:")
for route, view, methods in extracted[:5]:
    print(f"  - {route}: {view.__name__ if hasattr(view, '__name__') else view}")

# Look specifically for /blog
blog_views = [v for v in extracted if 'blog' in v[0].lower()]
print(f"\nBlog-related views: {len(blog_views)}")
for route, view, methods in blog_views:
    print(f"  - Route: {route}")
    print(f"  - View: {view}")
    print(f"  - Methods: {methods}")

# Step 3: Get Django views with filtering
print("\n[Step 3] Getting Django views (with filtering)...")
django_views = get_django_views()
print(f"Returned {len(django_views)} views after filtering")

blog_views_filtered = [v for v in django_views if 'blog' in v[0].lower()]
print(f"\nBlog-related views after filtering: {len(blog_views_filtered)}")
for route, view, methods in blog_views_filtered:
    print(f"  - Route: {route}")
    print(f"  - View: {view}")
    print(f"  - Methods: {methods}")

# Step 4: Test pattern validation
print("\n[Step 4] Testing pattern validation...")

if blog_views_filtered:
    from django_bolt import BoltAPI
    api = BoltAPI()
    registrar = DjangoViewRegistrar(api)

    route, view, methods = blog_views_filtered[0]
    print(f"\nValidating route: {route}")
    is_valid = registrar._is_valid_pattern(route)
    print(f"  Pattern valid: {is_valid}")

    if not is_valid:
        print(f"  Reason: Pattern validation failed")
        # Test individual checks
        print(f"    - Open count: {route.count('{')}")
        print(f"    - Close count: {route.count('}')}")
        print(f"    - Has invalid chars: {any(c in route for c in ['\\\\', '^', '$', '+', '*', '?', '|', '(', ')'])}")

# Step 5: Try to register and check routes
print("\n[Step 5] Testing route registration...")
if blog_views_filtered:
    from django_bolt import BoltAPI
    api = BoltAPI()
    registrar = DjangoViewRegistrar(api)

    route, view, methods = blog_views_filtered[0]
    print(f"\nRegistering route: {route}")
    print(f"  View: {view}")
    print(f"  Methods: {methods}")

    try:
        registrar.register_views([(route, view, methods)], host='127.0.0.1', port=8000)
        print(f"  ✓ Successfully registered")
        print(f"  Total routes in API: {len(api._routes)}")
        for method, path, handler_id, handler in api._routes:
            print(f"    - {method} {path}")
    except Exception as e:
        print(f"  ✗ Registration failed: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)

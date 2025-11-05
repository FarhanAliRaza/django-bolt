"""
Utilities for detecting and extracting Django views from URL patterns.

Converts Django path() patterns to django-bolt matchit syntax and
extracts view callables for ASGI bridge registration.
"""

from __future__ import annotations

import re
from typing import Any, List, Optional, Tuple, Callable


# Mapping of Django path converters to matchit pattern syntax
DJANGO_CONVERTERS = {
    'int': r'\d+',
    'str': r'[^/]+',
    'slug': r'[-a-zA-Z0-9_]+',
    'uuid': r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
    'path': r'.+',
}


def _clean_pattern(pattern_str: str) -> str:
    """
    Clean up Django path pattern string by removing regex markers.

    Examples:
        '^admin$' -> 'admin'
        'articles/' -> 'articles'
        '^$' -> ''
        'users' -> 'users'

    Args:
        pattern_str: Raw pattern string from Django

    Returns:
        Cleaned pattern string
    """
    # Remove leading ^ and trailing $ and /
    if pattern_str.startswith('^'):
        pattern_str = pattern_str[1:]
    if pattern_str.endswith('$'):
        pattern_str = pattern_str[:-1]
    if pattern_str.endswith('/'):
        pattern_str = pattern_str[:-1]

    return pattern_str


def django_path_to_matchit(django_path: str) -> str:
    """
    Convert Django path pattern to matchit syntax.

    Examples:
        'users/<int:user_id>' -> 'users/{user_id}'
        'articles/<slug:slug>' -> 'articles/{slug}'
        'files/<path:path>' -> 'files/{path:path}'
        'posts/<int:pk>/comments/' -> 'posts/{pk}/comments/'

    Args:
        django_path: Django path pattern (without leading slash)

    Returns:
        Matchit-compatible path pattern
    """
    # Pattern to match Django path converters: <converter:name>
    pattern = r'<(\w+):(\w+)>'

    def replace_converter(match):
        converter = match.group(1)
        param_name = match.group(2)

        # For 'path' converter, use special matchit syntax {name:path}
        if converter == 'path':
            return f'{{{param_name}:path}}'
        else:
            # For other converters, just use {name}
            # Validation will be handled by Django middleware
            return f'{{{param_name}}}'

    return re.sub(pattern, replace_converter, django_path)


def extract_views_from_patterns(
    urlpatterns: List[Any],
    prefix: str = '',
) -> List[Tuple[str, Callable, List[str]]]:
    """
    Extract views from Django URLconf patterns.

    Recursively processes url() and path() patterns, handling include().
    Returns list of (route_pattern, view_callable, methods) tuples.

    Args:
        urlpatterns: Django URLconf urlpatterns list
        prefix: Current URL prefix (for include())

    Returns:
        List of (matchit_pattern, view, methods) tuples
    """
    views = []

    for url_pattern in urlpatterns:
        # Handle include()
        if hasattr(url_pattern, 'url_patterns'):
            # This is an include()
            pattern_str = str(url_pattern.pattern)
            # Clean up pattern string properly
            pattern_str = _clean_pattern(pattern_str)
            if not pattern_str:
                # Empty pattern, use existing prefix
                new_prefix = prefix
            else:
                new_prefix = prefix + '/' + pattern_str if prefix else '/' + pattern_str

            # Recursively extract from included patterns
            included = extract_views_from_patterns(url_pattern.url_patterns, prefix=new_prefix)
            views.extend(included)
            continue

        # Extract route pattern
        pattern_str = str(url_pattern.pattern)

        # Skip regex patterns (old-style re_path) - only support path() style
        if pattern_str.startswith('^'):
            continue

        # Clean up pattern string
        pattern_str = _clean_pattern(pattern_str)
        if not pattern_str:
            # Empty pattern, skip
            continue

        # Convert Django path syntax to matchit
        matchit_pattern = django_path_to_matchit(pattern_str)

        # Build full path with prefix
        if prefix:
            full_path = prefix + '/' + matchit_pattern
        else:
            full_path = '/' + matchit_pattern

        # Clean up path (remove duplicate slashes)
        while '//' in full_path:
            full_path = full_path.replace('//', '/')

        # Extract view callable
        if hasattr(url_pattern, 'callback'):
            view = url_pattern.callback

            # Determine supported HTTP methods
            # For CBVs, check allowed_methods
            # For FBVs, support all methods by default
            methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']

            if hasattr(view, 'cls'):
                # This is a CBV wrapped by as_view()
                view_cls = view.cls
                if hasattr(view_cls, 'http_method_names'):
                    methods = [m.upper() for m in view_cls.http_method_names if m != 'options']
                    methods.append('OPTIONS')

            views.append((full_path, view, methods))

    return views


def _is_matchit_compatible(pattern: str) -> bool:
    """
    Check if a matchit pattern is compatible with the router.

    The pattern will be converted by convert_path in router.rs:
    - {path:path} → {*path} (catch-all, must be at end)
    - {int:id} → {id} (parameter)

    So we validate the post-conversion patterns.

    Args:
        pattern: The pattern to check (FastAPI-style before conversion)

    Returns:
        True if compatible, False otherwise
    """
    # Simulate the conversion that happens in router.rs
    converted = pattern
    converted = converted.replace('{path:', '{*')

    # After conversion, catch-all must be at the end
    if '{*' in converted:
        # Find the catch-all position
        catch_all_pos = converted.rfind('{*')
        # Find the closing brace
        close_pos = converted.find('}', catch_all_pos)
        if close_pos != len(converted) - 1:
            # Catch-all is not at the end
            return False

    # No regex characters allowed
    if any(c in pattern for c in ['^', '$', '+', '?', '|', '(', ')', '\\']):
        return False

    # Braces must be balanced
    if pattern.count('{') != pattern.count('}'):
        return False

    return True


def get_django_views(
    urlpatterns: Optional[List[Any]] = None,
    exclude_patterns: Optional[List[str]] = None,
) -> List[Tuple[str, Callable, List[str]]]:
    """
    Get all registered Django views from URLconf.

    Args:
        urlpatterns: Django urlpatterns (if None, loads from ROOT_URLCONF)
        exclude_patterns: List of patterns to exclude (e.g., ['^admin/', '^static/'])

    Returns:
        List of (route_pattern, view, methods) tuples
    """
    if urlpatterns is None:
        try:
            from django.conf import settings
            from django.urls import get_resolver

            resolver = get_resolver(getattr(settings, 'ROOT_URLCONF', None))
            urlpatterns = resolver.url_patterns
        except Exception as e:
            import sys
            print(f"[django-bolt] Warning: Could not load urlpatterns: {e}", file=sys.stderr)
            return []

    # Extract all views
    all_views = extract_views_from_patterns(urlpatterns)

    # Filter using provided exclusion patterns only
    exclude_patterns = exclude_patterns or []
    filtered_views = []
    problematic_views = []

    for route, view, methods in all_views:
        # Only check explicit exclude patterns (not default exclusions)
        excluded = False
        for pattern in exclude_patterns:
            clean_pattern = pattern.lstrip('^').lstrip('/')
            clean_route = route.lstrip('/')
            if clean_route.startswith(clean_pattern):
                excluded = True
                break

        if excluded:
            continue

        # Check for issues but DON'T filter - just log them
        issues = []

        # Check for multiple catch-all parameters
        if route.count('{') > 1 and ':path}' in route:
            if route.count(':path}') > 1:
                issues.append("Multiple catch-all parameters ({path:...})")
            elif not route.endswith(':path}'):
                issues.append("Catch-all parameter not at end of route")

        # Check for old Django syntax that won't convert properly
        if '<' in route or '>' in route:
            issues.append("Old Django path syntax (<id>) - won't convert to matchit {id}")

        # Check for duplicate slashes
        if '//' in route:
            issues.append("Duplicate slashes in path")

        if issues:
            # Skip routes with issues - don't register them
            problematic_views.append((route, view, methods, issues))
        else:
            # Only add compatible views
            filtered_views.append((route, view, methods))

    # Log skipped views if any
    if problematic_views:
        import sys
        print(f"[django-bolt] SKIPPED: {len(problematic_views)} Django view(s) with incompatible routing patterns:", file=sys.stderr)
        for route, view, methods, issues in problematic_views:
            print(f"[django-bolt]   ✗ {route}", file=sys.stderr)
            for issue in issues:
                print(f"[django-bolt]       {issue}", file=sys.stderr)
        print(f"[django-bolt]", file=sys.stderr)
        print(f"[django-bolt] Note: These views are incompatible with matchit router constraints:", file=sys.stderr)
        print(f"[django-bolt]   • Multiple catch-all parameters not supported", file=sys.stderr)
        print(f"[django-bolt]   • Catch-all parameters must be at end of route", file=sys.stderr)
        print(f"[django-bolt]   • Regex patterns (re_path) not supported", file=sys.stderr)
        print(f"[django-bolt]   • Old Django syntax <id> must be <type:name>", file=sys.stderr)

    if filtered_views:
        print(f"[django-bolt] Registered {len(filtered_views)} compatible Django view(s)", file=sys.stderr)

    return filtered_views


def get_django_view_info() -> dict:
    """
    Get information about registered Django views.

    Returns:
        Dict with view registration details
    """
    try:
        from django.conf import settings

        views = get_django_views(
            exclude_patterns=['^/admin/', '^/static/', '^/media/']
        )

        return {
            'installed': True,
            'view_count': len(views),
            'views': views,
        }
    except Exception as e:
        import sys
        print(f"[django-bolt] Warning: Could not get Django view info: {e}", file=sys.stderr)
        return {
            'installed': False,
            'view_count': 0,
            'views': [],
        }

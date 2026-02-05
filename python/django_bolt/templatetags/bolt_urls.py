from django import template
from django.urls.exceptions import NoReverseMatch
from django_bolt.api import _BOLT_API_REGISTRY

register = template.Library()

@register.simple_tag
def bolt_url(name, **kwargs):
    """
    Reverse a BoltAPI named route.
    
    Usage:
        {% bolt_url 'my-route' id=1 %}
    """
    for api in _BOLT_API_REGISTRY:
        if name in api._named_routes:
            path_pattern = api._named_routes[name]
            try:
                # Replace {param} with values from kwargs
                # We need to handle potentially missing params by raising NoReverseMatch
                # Bolt paths use {param} syntax which is compatible with python format()
                return path_pattern.format(**kwargs)
            except KeyError as e:
                # If a key is missing in kwargs that is required by the pattern
                raise NoReverseMatch(f"Missing argument for bolt_url '{name}': {e}")
            except ValueError as e:
                # If format string is invalid
                raise NoReverseMatch(f"Invalid format for bolt_url '{name}': {e}")
                
    # If we fall through, the named route was not found in any registered API
    raise NoReverseMatch(f"Bolt URL '{name}' not found")

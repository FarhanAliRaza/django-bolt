"""
Minimal Django views for performance testing.
These bypass most Django features for maximum speed.
"""

from django.http import HttpResponse, JsonResponse
import json

# Pre-create response objects to avoid allocation overhead
HELLO_WORLD_RESPONSE = JsonResponse({"Hello": "World"})
HELLO_WORLD_RESPONSE['Content-Length'] = '18'

# Even faster: raw HttpResponse with pre-serialized JSON
HELLO_WORLD_RAW = HttpResponse(
    b'{"Hello":"World"}',
    content_type='application/json'
)
HELLO_WORLD_RAW['Content-Length'] = '17'

def fast_root(request):
    """Ultra-fast root endpoint - returns pre-created response"""
    return HELLO_WORLD_RAW

def fast_json(request):
    """Fast JSON endpoint with minimal overhead"""
    # Skip all Django serialization, use raw bytes
    return HttpResponse(
        b'{"status":"ok","fast":true}',
        content_type='application/json'
    )
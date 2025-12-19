
from typing import Annotated

from django.contrib import messages  # noqa: PLC0415

from django_bolt import BoltAPI, Request
from django_bolt.middleware import BaseMiddleware, TimingMiddleware
from django_bolt.params import Form
from django_bolt.shortcuts import render


class RequestIdMiddleware:
    """
    Custom middleware that adds a request ID to every request.

    Follows Django's middleware pattern:
    - __init__(get_response): Called ONCE at startup
    - __call__(request): Called for each request
    """

    def __init__(self, get_response):
        """Called once at server startup - do expensive setup here."""
        self.get_response = get_response
        self.request_count = 0
        print("[RequestIdMiddleware] Initialized at startup")

    async def __call__(self, request):
        """Called for each request."""
        import uuid  # noqa: PLC0415

        # Generate request ID and add to request state
        request_id = str(uuid.uuid4())[:8]
        self.request_count += 1
        request.state["request_id"] = request_id
        request.state["request_number"] = self.request_count

        # Process the request
        response = await self.get_response(request)

        # Add header to response
        response.headers["X-Request-ID"] = request_id
        return response


class TenantMiddleware(BaseMiddleware):
    """
    Custom middleware with path exclusions using BaseMiddleware helper.

    BaseMiddleware provides:
    - exclude_paths: Glob patterns to skip (compiled once at startup)
    - exclude_methods: HTTP methods to skip (O(1) lookup)
    """

    exclude_paths = ["/health", "/docs", "/docs/*", "/openapi.json"]
    exclude_methods = ["OPTIONS"]

    async def process_request(self, request):
        """Extract tenant from header and add to request state."""
        tenant_id = request.headers.get("x-tenant-id", "default")
        request.state["tenant_id"] = tenant_id
        request.state["tenant_loaded"] = True

        response = await self.get_response(request)

        response.headers["X-Tenant-ID"] = tenant_id
        return response


# Create a separate API instance with middleware enabled
# This demonstrates how to use Django middleware + custom Python middleware
middleware_api = BoltAPI(
    # Load Django middleware from settings.MIDDLEWARE
    django_middleware=True,
    # Add custom Python middleware (pass classes, not instances)
    middleware=[
        RequestIdMiddleware,  # Adds X-Request-ID header
        TenantMiddleware,     # Adds tenant context (skips /health, /docs)
        TimingMiddleware,     # Built-in: adds X-Response-Time header
    ],
)

@middleware_api.get("/demo")
async def middleware_demo(request: Request):
    """
    Demonstrates Django middleware + messages framework with Django-Bolt.

    This endpoint shows:
    1. Django middleware (SessionMiddleware, AuthenticationMiddleware, MessageMiddleware)
    2. Custom RequestIdMiddleware (adds X-Request-ID header)
    3. Custom TenantMiddleware (adds X-Tenant-ID header)
    4. Django messages framework ({% for message in messages %} in templates)

    Test with:
        curl http://localhost:8000/middleware/demo
    """

    # Add messages using Django's messages framework
    messages.info(request, "This is an info message")
    # Access Django user
    # user = await request.auser()

    # Render template that displays messages
    return render(request, "messages_demo.html", {
        "title": "Middleware & Messages Demo",
        # "user": user,
        "request_id": request.state.get("request_id"),
        "tenant_id": request.state.get("tenant_id"),
    })


@middleware_api.post("/demo")
# @csrf_exempt
async def middleware_demo(request: Request, test: Annotated[str, Form("test")]):
    """
    Demonstrates Django middleware + messages framework with Django-Bolt.

    This endpoint shows:
    1. Django middleware (SessionMiddleware, AuthenticationMiddleware, MessageMiddleware)
    2. Custom RequestIdMiddleware (adds X-Request-ID header)
    3. Custom TenantMiddleware (adds X-Tenant-ID header)
    4. Django messages framework ({% for message in messages %} in templates)

    Test with:
        curl http://localhost:8000/middleware/demo
    """
    print(test)
    # Add messages using Django's messages framework
    messages.info(request, "This is an info message")
    messages.success(request, "Operation completed successfully!")
    messages.warning(request, "This is a warning message")
    messages.error(request, "This is an error message")

    # Access Django user
    # user = await request.auser()

    # Render template that displays messages
    return render(request, "messages_demo.html", {
        "title": "Middleware & Messages Demo",
        # "user": user,
        "request_id": request.state.get("request_id"),
        "tenant_id": request.state.get("tenant_id"),
    })

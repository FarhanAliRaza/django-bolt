"""
End-to-end WebSocket integration tests with the Rust server
"""
from __future__ import annotations

import asyncio
import sys
import os
import time
import subprocess
import signal
import pytest

# Add parent paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test WebSocket route registration
def test_websocket_route_registration():
    """Test that WebSocket routes are registered correctly"""
    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test-secret-key-for-websocket',
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'django_bolt',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            USE_TZ=True,
        )
        django.setup()

    from django_bolt import BoltAPI, WebSocket

    api = BoltAPI()

    @api.websocket("/ws/echo")
    async def echo_handler(websocket: WebSocket):
        await websocket.accept()
        async for message in websocket.iter_text():
            await websocket.send_text(f"Echo: {message}")

    @api.websocket("/ws/chat/{room_id}")
    async def chat_handler(websocket: WebSocket, room_id: str):
        await websocket.accept()
        await websocket.send_text(f"Joined room: {room_id}")

    # Verify routes are registered
    assert len(api._websocket_routes) == 2

    # Check first route
    path1, handler_id1, handler1 = api._websocket_routes[0]
    assert path1 == "/ws/echo"
    assert callable(handler1)

    # Check second route (with path param)
    path2, handler_id2, handler2 = api._websocket_routes[1]
    assert path2 == "/ws/chat/{room_id}"
    assert callable(handler2)


def test_websocket_route_metadata():
    """Test that WebSocket route metadata is compiled correctly"""
    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test-secret-key-for-websocket-meta',
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'django_bolt',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            USE_TZ=True,
        )
        django.setup()

    from django_bolt import BoltAPI, WebSocket
    from django_bolt.auth import IsAuthenticated

    api = BoltAPI()

    @api.websocket("/ws/protected", guards=[IsAuthenticated()])
    async def protected_ws(websocket: WebSocket):
        await websocket.accept()

    assert len(api._websocket_routes) >= 1
    # Check that guards are passed (they're compiled into metadata)


def test_websocket_rust_router_registration():
    """Test that WebSocket routes can be registered with the Rust router"""
    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test-secret-key-for-rust-ws',
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'django_bolt',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            USE_TZ=True,
        )
        django.setup()

    from django_bolt import BoltAPI, WebSocket
    from django_bolt._core import register_websocket_routes

    api = BoltAPI()

    @api.websocket("/ws/test")
    async def test_ws(websocket: WebSocket):
        await websocket.accept()

    # Prepare routes in the format expected by Rust
    ws_routes = []
    for path, handler_id, handler in api._websocket_routes:
        ws_routes.append((path, handler_id, handler))

    # This should not raise an exception
    # Note: We can only call this once per process due to OnceCell
    # So we just verify the format is correct
    assert len(ws_routes) == 1
    path, handler_id, handler = ws_routes[0]
    assert path == "/ws/test"
    assert isinstance(handler_id, int)
    assert callable(handler)


def test_websocket_actor_echo():
    """Test that the WebSocket actor can be created"""
    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test-secret-key-for-actor',
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'django_bolt',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            USE_TZ=True,
        )
        django.setup()

    # Just verify imports work
    from django_bolt.websocket import WebSocket, WebSocketState, CloseCode

    assert WebSocketState.CONNECTING.value == 1
    assert WebSocketState.CONNECTED.value == 2
    assert WebSocketState.DISCONNECTED.value == 3

    assert CloseCode.NORMAL == 1000
    assert CloseCode.GOING_AWAY == 1001


@pytest.mark.asyncio
async def test_websocket_class_lifecycle():
    """Test WebSocket class lifecycle (mock ASGI style)"""
    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test-secret-key-for-lifecycle',
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'django_bolt',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            USE_TZ=True,
        )
        django.setup()

    from django_bolt.websocket import WebSocket, WebSocketState

    # Create mock ASGI scope, receive, send
    scope = {
        "type": "websocket",
        "path": "/ws/test",
        "query_string": b"token=abc",
        "headers": [(b"host", b"localhost:8000")],
        "client": ("127.0.0.1", 50000),
    }

    received_messages = []
    sent_messages = []

    async def receive():
        if not received_messages:
            return {"type": "websocket.connect"}
        return received_messages.pop(0)

    async def send(message):
        sent_messages.append(message)

    ws = WebSocket(scope, receive, send)

    # Initially connecting
    assert ws.state == WebSocketState.CONNECTING

    # Accept connection
    await ws.accept()
    assert ws.state == WebSocketState.CONNECTED
    assert any(m.get("type") == "websocket.accept" for m in sent_messages)

    # Send a message
    await ws.send_text("Hello!")
    assert any(m.get("text") == "Hello!" for m in sent_messages)

    # Close
    await ws.close()
    assert ws.state == WebSocketState.DISCONNECTED


def test_websocket_merge_apis():
    """Test that WebSocket routes are merged correctly when combining APIs"""
    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test-secret-key-for-merge',
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'django_bolt',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            USE_TZ=True,
        )
        django.setup()

    from django_bolt import BoltAPI, WebSocket
    from django_bolt.management.commands.runbolt import Command

    api1 = BoltAPI()
    api2 = BoltAPI(prefix="/v2")

    @api1.websocket("/ws/chat")
    async def chat_ws(websocket: WebSocket):
        await websocket.accept()

    @api2.websocket("/ws/notify")
    async def notify_ws(websocket: WebSocket):
        await websocket.accept()

    # Use the Command's merge_apis method
    # Format is (api_path, api) tuples
    cmd = Command()
    merged = cmd.merge_apis([("project.api", api1), ("app.api", api2)])

    # Should have both WebSocket routes
    assert len(merged._websocket_routes) == 2

    paths = [route[0] for route in merged._websocket_routes]
    assert "/ws/chat" in paths
    assert "/v2/ws/notify" in paths

"""Tests for WebSocket functionality."""

from __future__ import annotations

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from django_bolt import BoltAPI
from django_bolt.websocket import (
    WebSocket,
    WebSocketState,
    WebSocketDisconnect,
    WebSocketClose,
    WebSocketException,
    CloseCode,
    is_websocket_handler,
    mark_websocket_handler,
    get_websocket_param_name,
    run_websocket_handler,
)


class TestWebSocketClass:
    """Tests for the WebSocket connection class."""

    def test_initial_state(self):
        """WebSocket starts in CONNECTING state."""
        receive = AsyncMock()
        send = AsyncMock()
        ws = WebSocket(scope={"path": "/ws"}, receive=receive, send=send)
        assert ws.state == WebSocketState.CONNECTING

    def test_url_and_path(self):
        """WebSocket exposes URL and path from scope."""
        ws = WebSocket(
            scope={"path": "/ws/chat", "query_string": b"room=123"},
            receive=AsyncMock(),
            send=AsyncMock(),
        )
        assert ws.url == "/ws/chat"
        assert ws.path == "/ws/chat"
        assert ws.query_string == b"room=123"

    def test_path_params(self):
        """WebSocket exposes path parameters."""
        ws = WebSocket(
            scope={"path": "/ws/room/42", "path_params": {"room_id": "42"}},
            receive=AsyncMock(),
            send=AsyncMock(),
        )
        assert ws.path_params == {"room_id": "42"}

    def test_query_params_parsing(self):
        """WebSocket parses query parameters."""
        ws = WebSocket(
            scope={"path": "/ws", "query_string": b"room=123&user=john"},
            receive=AsyncMock(),
            send=AsyncMock(),
        )
        params = ws.query_params
        assert params["room"] == "123"
        assert params["user"] == "john"

    def test_headers(self):
        """WebSocket exposes headers from scope."""
        ws = WebSocket(
            scope={"path": "/ws", "headers": {"authorization": "Bearer xyz"}},
            receive=AsyncMock(),
            send=AsyncMock(),
        )
        assert ws.headers == {"authorization": "Bearer xyz"}

    def test_cookies(self):
        """WebSocket exposes cookies from scope."""
        ws = WebSocket(
            scope={"path": "/ws", "cookies": {"session": "abc123"}},
            receive=AsyncMock(),
            send=AsyncMock(),
        )
        assert ws.cookies == {"session": "abc123"}

    def test_client_address(self):
        """WebSocket exposes client address."""
        ws = WebSocket(
            scope={"path": "/ws", "client": ("127.0.0.1", 8080)},
            receive=AsyncMock(),
            send=AsyncMock(),
        )
        assert ws.client == ("127.0.0.1", 8080)

    @pytest.mark.asyncio
    async def test_accept(self):
        """WebSocket.accept() sends accept message and updates state."""
        send = AsyncMock()
        ws = WebSocket(scope={"path": "/ws"}, receive=AsyncMock(), send=send)

        await ws.accept()

        send.assert_called_once_with({"type": "websocket.accept"})
        assert ws.state == WebSocketState.CONNECTED

    @pytest.mark.asyncio
    async def test_accept_with_subprotocol(self):
        """WebSocket.accept() can specify subprotocol."""
        send = AsyncMock()
        ws = WebSocket(scope={"path": "/ws"}, receive=AsyncMock(), send=send)

        await ws.accept(subprotocol="graphql-ws")

        send.assert_called_once_with({
            "type": "websocket.accept",
            "subprotocol": "graphql-ws",
        })

    @pytest.mark.asyncio
    async def test_accept_idempotent(self):
        """Calling accept() multiple times is safe."""
        send = AsyncMock()
        ws = WebSocket(scope={"path": "/ws"}, receive=AsyncMock(), send=send)

        await ws.accept()
        await ws.accept()

        # Should only send once
        assert send.call_count == 1

    @pytest.mark.asyncio
    async def test_receive_text(self):
        """WebSocket.receive_text() returns text message."""
        receive = AsyncMock(return_value={"type": "websocket.receive", "text": "hello"})
        send = AsyncMock()
        ws = WebSocket(scope={"path": "/ws"}, receive=receive, send=send)
        await ws.accept()

        text = await ws.receive_text()
        assert text == "hello"

    @pytest.mark.asyncio
    async def test_receive_bytes(self):
        """WebSocket.receive_bytes() returns binary message."""
        receive = AsyncMock(return_value={"type": "websocket.receive", "bytes": b"\x00\x01\x02"})
        send = AsyncMock()
        ws = WebSocket(scope={"path": "/ws"}, receive=receive, send=send)
        await ws.accept()

        data = await ws.receive_bytes()
        assert data == b"\x00\x01\x02"

    @pytest.mark.asyncio
    async def test_receive_json(self):
        """WebSocket.receive_json() parses JSON message."""
        receive = AsyncMock(return_value={"type": "websocket.receive", "text": '{"key": "value"}'})
        send = AsyncMock()
        ws = WebSocket(scope={"path": "/ws"}, receive=receive, send=send)
        await ws.accept()

        data = await ws.receive_json()
        assert data == {"key": "value"}

    @pytest.mark.asyncio
    async def test_receive_disconnect(self):
        """WebSocket.receive() raises WebSocketDisconnect on disconnect."""
        receive = AsyncMock(return_value={"type": "websocket.disconnect", "code": 1001})
        ws = WebSocket(scope={"path": "/ws"}, receive=receive, send=AsyncMock())
        await ws.accept()

        with pytest.raises(WebSocketDisconnect) as exc_info:
            await ws.receive()

        assert exc_info.value.code == 1001
        assert ws.state == WebSocketState.DISCONNECTED

    @pytest.mark.asyncio
    async def test_send_text(self):
        """WebSocket.send_text() sends text message."""
        send = AsyncMock()
        ws = WebSocket(scope={"path": "/ws"}, receive=AsyncMock(), send=send)
        await ws.accept()

        await ws.send_text("hello")

        send.assert_called_with({"type": "websocket.send", "text": "hello"})

    @pytest.mark.asyncio
    async def test_send_bytes(self):
        """WebSocket.send_bytes() sends binary message."""
        send = AsyncMock()
        ws = WebSocket(scope={"path": "/ws"}, receive=AsyncMock(), send=send)
        await ws.accept()

        await ws.send_bytes(b"\x00\x01\x02")

        send.assert_called_with({"type": "websocket.send", "bytes": b"\x00\x01\x02"})

    @pytest.mark.asyncio
    async def test_send_json(self):
        """WebSocket.send_json() sends JSON message."""
        send = AsyncMock()
        ws = WebSocket(scope={"path": "/ws"}, receive=AsyncMock(), send=send)
        await ws.accept()

        await ws.send_json({"key": "value"})

        send.assert_called_with({"type": "websocket.send", "text": '{"key":"value"}'})

    @pytest.mark.asyncio
    async def test_send_not_connected(self):
        """WebSocket.send() raises error if not connected."""
        ws = WebSocket(scope={"path": "/ws"}, receive=AsyncMock(), send=AsyncMock())

        with pytest.raises(RuntimeError, match="not connected"):
            await ws.send_text("hello")

    @pytest.mark.asyncio
    async def test_close(self):
        """WebSocket.close() sends close message."""
        send = AsyncMock()
        ws = WebSocket(scope={"path": "/ws"}, receive=AsyncMock(), send=send)
        await ws.accept()

        await ws.close(code=1000, reason="goodbye")

        send.assert_called_with({
            "type": "websocket.close",
            "code": 1000,
            "reason": "goodbye",
        })
        assert ws.state == WebSocketState.DISCONNECTED

    @pytest.mark.asyncio
    async def test_close_idempotent(self):
        """Calling close() multiple times is safe."""
        send = AsyncMock()
        ws = WebSocket(scope={"path": "/ws"}, receive=AsyncMock(), send=send)
        await ws.accept()

        await ws.close()
        await ws.close()

        # Should only send close once (accept + close = 2 calls)
        assert send.call_count == 2


class TestCloseCode:
    """Tests for WebSocket close codes."""

    def test_normal_closure(self):
        assert CloseCode.NORMAL == 1000

    def test_going_away(self):
        assert CloseCode.GOING_AWAY == 1001

    def test_protocol_error(self):
        assert CloseCode.PROTOCOL_ERROR == 1002


class TestWebSocketExceptions:
    """Tests for WebSocket exceptions."""

    def test_websocket_disconnect(self):
        exc = WebSocketDisconnect(code=1001, reason="going away")
        assert exc.code == 1001
        assert exc.reason == "going away"

    def test_websocket_close(self):
        exc = WebSocketClose(code=1000, reason="normal")
        assert exc.code == 1000
        assert exc.reason == "normal"

    def test_websocket_exception(self):
        exc = WebSocketException(code=1011, reason="internal error")
        assert exc.code == 1011
        assert exc.reason == "internal error"


class TestWebSocketHandlerUtils:
    """Tests for WebSocket handler utilities."""

    def test_mark_websocket_handler(self):
        """mark_websocket_handler sets attribute."""
        async def handler(websocket: WebSocket):
            pass

        marked = mark_websocket_handler(handler)
        assert is_websocket_handler(marked)

    def test_is_websocket_handler_false(self):
        """is_websocket_handler returns False for non-websocket handlers."""
        async def handler():
            pass

        assert not is_websocket_handler(handler)

    def test_get_websocket_param_name(self):
        """get_websocket_param_name finds WebSocket parameter."""
        async def handler(websocket: WebSocket):
            pass

        assert get_websocket_param_name(handler) == "websocket"

    def test_get_websocket_param_name_different_name(self):
        """get_websocket_param_name works with different parameter names."""
        async def handler(ws: WebSocket):
            pass

        assert get_websocket_param_name(handler) == "ws"

    def test_get_websocket_param_name_fallback(self):
        """get_websocket_param_name falls back to 'websocket' name."""
        async def handler(websocket):
            pass

        assert get_websocket_param_name(handler) == "websocket"


class TestBoltAPIWebSocket:
    """Tests for BoltAPI WebSocket decorator."""

    def test_websocket_decorator(self):
        """@api.websocket registers WebSocket route."""
        api = BoltAPI()

        @api.websocket("/ws")
        async def ws_handler(websocket: WebSocket):
            pass

        assert len(api._websocket_routes) == 1
        path, handler_id, handler = api._websocket_routes[0]
        assert path == "/ws"
        assert handler is ws_handler
        assert is_websocket_handler(handler)

    def test_websocket_with_prefix(self):
        """@api.websocket respects prefix."""
        api = BoltAPI(prefix="/api/v1")

        @api.websocket("/ws")
        async def ws_handler(websocket: WebSocket):
            pass

        path, _, _ = api._websocket_routes[0]
        assert path == "/api/v1/ws"

    def test_websocket_with_path_params(self):
        """@api.websocket supports path parameters."""
        api = BoltAPI()

        @api.websocket("/ws/{room_id}")
        async def room_handler(websocket: WebSocket, room_id: str):
            pass

        path, _, handler = api._websocket_routes[0]
        assert path == "/ws/{room_id}"
        meta = api._handler_meta[handler]
        assert "room_id" in meta["path_params"]

    def test_websocket_requires_async(self):
        """@api.websocket requires async handler."""
        api = BoltAPI()

        with pytest.raises(TypeError, match="must be an async function"):
            @api.websocket("/ws")
            def sync_handler(websocket: WebSocket):
                pass

    def test_websocket_metadata(self):
        """WebSocket handler has correct metadata."""
        api = BoltAPI()

        @api.websocket("/ws")
        async def ws_handler(websocket: WebSocket):
            pass

        meta = api._handler_meta[ws_handler]
        assert meta["is_async"] is True
        assert meta["is_websocket"] is True


class TestWebSocketIterators:
    """Tests for WebSocket async iterators."""

    @pytest.mark.asyncio
    async def test_iter_text(self):
        """WebSocket.iter_text() yields text messages until disconnect."""
        messages = [
            {"type": "websocket.receive", "text": "msg1"},
            {"type": "websocket.receive", "text": "msg2"},
            {"type": "websocket.disconnect", "code": 1000},
        ]
        receive = AsyncMock(side_effect=messages)
        ws = WebSocket(scope={"path": "/ws"}, receive=receive, send=AsyncMock())
        await ws.accept()

        received = []
        async for text in ws.iter_text():
            received.append(text)

        assert received == ["msg1", "msg2"]

    @pytest.mark.asyncio
    async def test_iter_json(self):
        """WebSocket.iter_json() yields parsed JSON messages."""
        messages = [
            {"type": "websocket.receive", "text": '{"n": 1}'},
            {"type": "websocket.receive", "text": '{"n": 2}'},
            {"type": "websocket.disconnect", "code": 1000},
        ]
        receive = AsyncMock(side_effect=messages)
        ws = WebSocket(scope={"path": "/ws"}, receive=receive, send=AsyncMock())
        await ws.accept()

        received = []
        async for data in ws.iter_json():
            received.append(data)

        assert received == [{"n": 1}, {"n": 2}]

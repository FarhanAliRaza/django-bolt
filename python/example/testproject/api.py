from typing import Optional, List, Annotated
import msgspec
import asyncio
import time
import json
from django_bolt import BoltAPI, JSON, OpenAPIConfig, SwaggerRenderPlugin, RedocRenderPlugin
from django_bolt.views import APIView, ViewSet
from django_bolt.param_functions import Header, Cookie, Form, File
from django_bolt.responses import PlainText, HTML, Redirect, FileResponse, StreamingResponse
from django_bolt.exceptions import (
    HTTPException,
    NotFound,
    BadRequest,
    Unauthorized,
    UnprocessableEntity,
    RequestValidationError,
)
from django_bolt.health import register_health_checks, add_health_check
from django_bolt.middleware import no_compress, cors


# OpenAPI is enabled by default at /docs with Swagger UI
# You can customize it by passing openapi_config:
api = BoltAPI()


register_health_checks(api)


class Item(msgspec.Struct):
    name: str
    price: float
    is_offer: Optional[bool] = None


import test_data

@api.get("/", tags=["root"], summary="summary", description="description")
@cors()  # Uses global CORS_ALLOWED_ORIGINS from Django settings
async def read_root():
    """
    Endpoint that returns a simple "Hello World" dictionary.
    """
    return {"message": "Hello World"}


@api.get("/10k-json")
async def read_10k():
    """
    Endpoint that returns 10k JSON objects.
    
    """
    return test_data.JSON_10K

@api.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@api.put("/items/{item_id}", response_model=dict)
async def update_item(item_id: int, item: Item) -> dict:
    return {"item_name": item.name, "item_id": item_id}


@api.get("/items100", response_model=list[Item])
async def items100() -> list[Item]:
    return [
        Item(name=f"item{i}", price=float(i), is_offer=(i % 2 == 0))
        for i in range(100)
    ]


# ==== Benchmarks: JSON parsing/validation & slow async op ====
class BenchPayload(msgspec.Struct):
    title: str
    count: int
    items: List[Item]


@api.post("/bench/parse")
async def bench_parse(payload: BenchPayload):
    # msgspec validates and decodes in one pass; just return minimal data
    return {"ok": True, "n": len(payload.items), "count": payload.count}


@api.get("/bench/slow")
async def bench_slow(ms: Optional[int] = 100):
    # Simulate slow I/O (network) with asyncio.sleep
    delay = max(0, (ms or 0)) / 1000.0
    await asyncio.sleep(delay)
    return {"ok": True, "ms": ms}


# ==== Benchmark endpoints for Header/Cookie/Exception/HTML/Redirect ====
@api.get("/header")
async def get_header(x: Annotated[str, Header(alias="x-test")]):
    return PlainText(x)


@api.get("/cookie")
async def get_cookie(val: Annotated[str, Cookie(alias="session")]):
    return PlainText(val)


@api.get("/exc")
async def raise_exc():
    raise HTTPException(status_code=404, detail="Not found")


@api.get("/html")
async def get_html():
    return HTML("<h1>Hello</h1>")


@api.get("/redirect")
async def get_redirect():
    return Redirect("/", status_code=302)


# ==== Form and File upload endpoints ====
@api.post("/form")
async def handle_form(
    name: Annotated[str, Form()],
    age: Annotated[int, Form()],
    email: Annotated[str, Form()] = "default@example.com"
):
    return {"name": name, "age": age, "email": email}


@api.post("/upload")
async def handle_upload(
    files: Annotated[list[dict], File(alias="file")]
):
    # Return file metadata
    return {
        "uploaded": len(files),
        "files": [{"name": f.get("filename"), "size": f.get("size")} for f in files]
    }


@api.post("/mixed-form")
async def handle_mixed(
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    attachments: Annotated[list[dict], File(alias="file")] = None
):
    result = {
        "title": title,
        "description": description,
        "has_attachments": bool(attachments)
    }
    if attachments:
        result["attachment_count"] = len(attachments)
    return result


# ==== File serving endpoint for benchmarks ====
import os
THIS_FILE = os.path.abspath(__file__)


@api.get("/file-static")
async def file_static():
    return FileResponse(THIS_FILE, filename="api.py")

@api.get("/file-static-nonexistent")
async def file_static():
    return FileResponse("/path/to/nonexistent/file.txt", filename="asdfasd.py")

# ==== Streaming endpoints for benchmarks ====
@api.get("/stream")
@no_compress
async def stream_plain():
    def gen():
        for i in range(100):
            yield "x"
    return StreamingResponse(gen, media_type="text/plain")


@api.get("/collected")
async def collected_plain():
    # Same data but collected into a single response
    return PlainText("x" * 100)

@api.get("/sse")
@no_compress
async def sse():
    def gen():
        for i in range(3):
            yield f"data: {i}\n\n"
    return StreamingResponse(gen, media_type="text/event-stream")


# ==== OpenAI-style Chat Completions (streaming/non-streaming) ====
class ChatMessage(msgspec.Struct):
    role: str
    content: str


class ChatCompletionRequest(msgspec.Struct):
    model: str = "gpt-4o-mini"
    messages: List[ChatMessage] = []
    stream: bool = True
    n_chunks: int = 50
    token: str = " hello"
    delay_ms: int = 0


# Optimized msgspec structs for streaming responses (zero-allocation serialization)
class ChatCompletionChunkDelta(msgspec.Struct):
    content: Optional[str] = None

class ChatCompletionChunkChoice(msgspec.Struct):
    index: int
    delta: ChatCompletionChunkDelta
    finish_reason: Optional[str] = None

class ChatCompletionChunk(msgspec.Struct):
    id: str
    created: int
    model: str
    choices: List[ChatCompletionChunkChoice]
    object: str = "chat.completion.chunk"


@api.post("/v1/chat/completions")
@no_compress
async def openai_chat_completions(payload: ChatCompletionRequest):
    created = int(time.time())
    model = payload.model or "gpt-4o-mini"
    chat_id = "chatcmpl-bolt-bench"

    if payload.stream:
        def gen():
            delay = max(0, payload.delay_ms or 0) / 1000.0
            for i in range(max(1, payload.n_chunks)):
                data = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [
                        {"index": 0, "delta": {"content": payload.token}, "finish_reason": None}
                    ],
                }
                yield f"data: {json.dumps(data, separators=(',', ':'))}\n\n"
                if delay > 0:
                    time.sleep(delay)
            final = {
                "id": chat_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [
                    {"index": 0, "delta": {}, "finish_reason": "stop"}
                ],
            }
            yield f"data: {json.dumps(final, separators=(',', ':'))}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(gen, media_type="text/event-stream")

    text = (payload.token * max(1, payload.n_chunks)).strip()
    response = {
        "id": chat_id,
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [
            {"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}
        ],
    }
    return response


@api.get("/sse-async")
@no_compress
async def sse_async():
    async def agen():
        for i in range(3):
            yield f"data: {i}\n\n"
    return StreamingResponse(agen(), media_type="text/event-stream")

@api.get("/sse-async-sleep")
async def sse_async_sleep():
    async def agen():
        for i in range(3):
            yield f"data: {i}\n\n"
            await asyncio.sleep(0)
    return StreamingResponse(agen(), media_type="text/event-stream")

@api.get("/sse-async-batch")
@no_compress
async def sse_async_batch():
    """Optimized async endpoint that yields all data at once to reduce overhead"""
    async def agen():
        # Batch all data into single yield to minimize GIL crossings
        all_data = "".join(f"data: {i}\n\n" for i in range(3))
        yield all_data
    return StreamingResponse(agen(), media_type="text/event-stream")


@api.post("/v1/chat/completions-async")
@no_compress
async def openai_chat_completions_async(payload: ChatCompletionRequest):
    created = int(time.time())
    model = payload.model or "gpt-4o-mini"
    chat_id = "chatcmpl-bolt-bench-async"

    if payload.stream:
        async def agen():
            import os
            debug_timing = os.environ.get("DJANGO_BOLT_DEBUG_TIMING")
            if debug_timing:
                gen_start = time.time()
                chunk_times = []
            
            delay = max(0, payload.delay_ms or 0) / 1000.0
            for i in range(max(1, payload.n_chunks)):
                if debug_timing:
                    chunk_start = time.time()
                
                # ULTRA-OPTIMIZATION: Use msgspec structs for 5-10x faster JSON serialization
                chunk = ChatCompletionChunk(
                    id=chat_id,
                    created=created,
                    model=model,
                    choices=[ChatCompletionChunkChoice(
                        index=0,
                        delta=ChatCompletionChunkDelta(content=payload.token),
                        finish_reason=None
                    )]
                )
                # msgspec.json.encode is 5-10x faster than json.dumps + much faster than dict creation
                chunk_json = msgspec.json.encode(chunk)
                
                if debug_timing:
                    serialize_time = time.time() - chunk_start
                    yield_start = time.time()
                
                yield b"data: " + chunk_json + b"\n\n"
                
                if debug_timing:
                    total_chunk_time = time.time() - chunk_start
                    chunk_times.append((serialize_time * 1000, total_chunk_time * 1000))
                    if i == 0:  # Log first chunk timing
                        print(f"[PY-TIMING] First chunk: serialize={serialize_time*1000:.3f}ms, total={total_chunk_time*1000:.3f}ms")
                
                if delay > 0:
                    await asyncio.sleep(delay)
                    
            # Final chunk with msgspec optimization
            final_chunk = ChatCompletionChunk(
                id=chat_id,
                created=created,
                model=model,
                choices=[ChatCompletionChunkChoice(
                    index=0,
                    delta=ChatCompletionChunkDelta(),
                    finish_reason="stop"
                )]
            )
            final_json = msgspec.json.encode(final_chunk)
            yield b"data: " + final_json + b"\n\n"
            yield b"data: [DONE]\n\n"
            
            if debug_timing:
                total_gen_time = (time.time() - gen_start) * 1000
                avg_serialize = sum(t[0] for t in chunk_times) / len(chunk_times) if chunk_times else 0
                avg_total = sum(t[1] for t in chunk_times) / len(chunk_times) if chunk_times else 0
                print(f"[PY-TIMING] Generator complete: total={total_gen_time:.3f}ms, avg_serialize={avg_serialize:.3f}ms, avg_chunk={avg_total:.3f}ms")
                
        return StreamingResponse(agen(), media_type="text/event-stream")

    # Non-streaming identical to sync path
    text = (payload.token * max(1, payload.n_chunks)).strip()
    response = {
        "id": chat_id,
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [
            {"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}
        ],
    }
    return response


@api.post("/v1/chat/completions-ultra")
@no_compress
async def openai_chat_completions_ultra_optimized(payload: ChatCompletionRequest):
    """Ultra-optimized version with msgspec structs and minimal allocations."""
    created = int(time.time())
    model = payload.model or "gpt-4o-mini"
    chat_id = "chatcmpl-bolt-ultra"

    if payload.stream:
        # Pre-create reusable msgspec structs (minimal object creation)
        token_delta = ChatCompletionChunkDelta(content=payload.token)
        stop_delta = ChatCompletionChunkDelta()
        
        async def ultra_agen():
            delay = max(0, payload.delay_ms or 0) / 1000.0
            
            # Ultra-optimized: reuse structs and minimize allocations
            for _ in range(max(1, payload.n_chunks)):
                # Reuse pre-created delta struct
                choice = ChatCompletionChunkChoice(
                    index=0,
                    delta=token_delta,
                    finish_reason=None
                )
                chunk = ChatCompletionChunk(
                    id=chat_id,
                    created=created,
                    model=model,
                    choices=[choice]
                )
                
                # msgspec.json.encode directly to bytes - fastest possible path
                chunk_bytes = msgspec.json.encode(chunk)
                yield b"data: " + chunk_bytes + b"\n\n"
                
                if delay > 0:
                    await asyncio.sleep(delay)
            
            # Final chunk with stop reason
            final_choice = ChatCompletionChunkChoice(
                index=0,
                delta=stop_delta,
                finish_reason="stop"
            )
            final_chunk = ChatCompletionChunk(
                id=chat_id,
                created=created,
                model=model,
                choices=[final_choice]
            )
            final_bytes = msgspec.json.encode(final_chunk)
            yield b"data: " + final_bytes + b"\n\n"
            yield b"data: [DONE]\n\n"
            
        return StreamingResponse(ultra_agen(), media_type="text/event-stream")

    # Non-streaming path unchanged
    text = (payload.token * max(1, payload.n_chunks)).strip()
    response = {
        "id": chat_id,
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [
            {"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}
        ],
    }
    return response

# ==== Error Handling & Logging Examples ====

# Example 1: Using specialized HTTP exceptions
@api.get("/errors/not-found/{resource_id}")
async def error_not_found(resource_id: int):
    """Example of NotFound exception with custom message."""
    if resource_id == 0:
        raise NotFound(detail=f"Resource {resource_id} not found")
    return {"resource_id": resource_id, "status": "found"}


@api.get("/errors/bad-request")
async def error_bad_request(value: Optional[int] = None):
    """Example of BadRequest exception."""
    if value is None or value < 0:
        raise BadRequest(detail="Value must be a positive integer")
    return {"value": value, "doubled": value * 2}


@api.get("/errors/unauthorized")
async def error_unauthorized():
    """Example of Unauthorized exception with headers."""
    raise Unauthorized(
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer realm=\"API\""}
    )


# Example 2: Validation errors with field-level details
class UserCreate(msgspec.Struct):
    username: str
    email: str
    age: int


@api.post("/errors/validation")
async def error_validation(user: UserCreate):
    """Example of manual validation with RequestValidationError."""
    errors = []

    if len(user.username) < 3:
        errors.append({
            "loc": ["body", "username"],
            "msg": "Username must be at least 3 characters",
            "type": "value_error.min_length",
        })

    if "@" not in user.email:
        errors.append({
            "loc": ["body", "email"],
            "msg": "Invalid email format",
            "type": "value_error.email",
        })

    if user.age < 0 or user.age > 150:
        errors.append({
            "loc": ["body", "age"],
            "msg": "Age must be between 0 and 150",
            "type": "value_error.range",
        })

    if errors:
        raise RequestValidationError(errors, body=user)

    return {"status": "created", "user": user}


# Example 3: Generic exception (will show traceback in DEBUG mode)
@api.get("/errors/internal")
async def error_internal():
    """Example of generic exception that triggers debug mode behavior.
    
    In DEBUG=True: Returns 500 with full traceback
    In DEBUG=False: Returns 500 with generic message
    """
    # This simulates an unexpected error
    result = 1 / 0  # ZeroDivisionError
    return {"result": result}


# Example 4: Custom error with extra data
@api.get("/errors/complex")
async def error_complex():
    """Example of HTTPException with extra structured data."""
    raise UnprocessableEntity(
        detail="Multiple validation errors occurred",
        extra={
            "errors": [
                {"field": "email", "reason": "Email already exists"},
                {"field": "username", "reason": "Username contains invalid characters"},
            ],
            "suggestion": "Please correct the highlighted fields",
            "documentation": "https://api.example.com/docs/validation"
        }
    )


# Example 5: Custom health check
async def check_external_api():
    """Custom health check for external API."""
    try:
        # Simulate checking external service
        # In real app: await httpx.get("https://api.example.com/health")
        await asyncio.sleep(0.001)
        return True, "External API OK"
    except Exception as e:
        return False, f"External API error: {str(e)}"


# Add custom health check to /ready endpoint
add_health_check(check_external_api)


# ==== Compression Test Endpoint ====
@api.get("/compression-test")
# @no_compress
async def compression_test():
    """
    Endpoint to test compression.

    Returns a large JSON response (>1KB) that should be compressed
    when client sends Accept-Encoding: gzip, br, deflate headers.

    Test with:
        curl -H "Accept-Encoding: gzip, br" http://localhost:8000/compression-test -v

    Check for "Content-Encoding" header in response.
    """
    # Generate large data (>1KB to trigger compression)
    large_data = {
        "message": "This is a compression test endpoint",
        "compression_info": {
            "enabled": "Compression is enabled by default in Django-Bolt",
            "algorithms": ["brotli", "gzip", "zstd"],
            "automatic": "Actix Web automatically compresses based on Accept-Encoding header",
            "threshold": "Responses larger than ~1KB are compressed",
        },
        "sample_data": [
            {
                "id": i,
                "name": f"Item {i}",
                "description": "This is a sample description that adds to the response size. " * 5,
                "metadata": {
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-02T00:00:00Z",
                    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
                    "properties": {
                        "key1": "value1",
                        "key2": "value2",
                        "key3": "value3",
                    }
                }
            }
            for i in range(50)  # 50 items to ensure >1KB
        ],
        "instructions": {
            "step1": "Send a request with 'Accept-Encoding: gzip, br' header",
            "step2": "Check response headers for 'Content-Encoding'",
            "step3": "Compare response size with/without compression",
            "note": "Small responses (<1KB) won't be compressed even with Accept-Encoding",
        }
    }

    return large_data


# ============================================================================
# Class-Based Views (APIView) - Using Decorator Syntax
# ============================================================================

@api.view("/cbv-simple")
class SimpleAPIView(APIView):
    """Simple APIView for benchmarking."""

    async def get(self, request):
        """GET /cbv-simple - Simple GET endpoint."""
        return {"message": "Hello from APIView"}

    async def post(self, request, data: Item):
        """POST /cbv-simple - POST with validation."""
        return {"name": data.name, "price": data.price, "cbv": True}


@api.view("/cbv-items/{item_id}")
class ItemAPIView(APIView):
    """APIView for item operations."""

    async def get(self, request, item_id: int, q: Optional[str] = None):
        """GET /cbv-items/{item_id} - Get item with optional query param."""
        return {"item_id": item_id, "q": q, "cbv": True}

    async def put(self, request, item_id: int, item: Item):
        """PUT /cbv-items/{item_id} - Update item."""
        return {"item_name": item.name, "item_id": item_id, "cbv": True}


# ============================================================================
# Class-Based Views (ViewSet) - Using Unified ViewSet Pattern with @action
# ============================================================================

from django_bolt import action



# ============================================================================
# Benchmark ViewSets - Using Decorator Syntax
# ============================================================================

@api.view("/cbv-items100")
class Items100ViewSet(ViewSet):
    """ViewSet that returns 100 items (for benchmarking)."""

    async def get(self, request):
        """GET /cbv-items100 - Return 100 items."""
        return [
            {"name": f"item{i}", "price": float(i), "is_offer": (i % 2 == 0)}
            for i in range(100)
        ]


@api.view("/cbv-bench-parse")
class BenchParseViewSet(ViewSet):
    """ViewSet for JSON parsing benchmark."""

    async def post(self, request, payload: BenchPayload):
        """POST /cbv-bench-parse - Parse and validate JSON payload."""
        return {"ok": True, "n": len(payload.items), "count": payload.count, "cbv": True}




# ============================================================================
# Response Type ViewSets - Using Decorator Syntax
# ============================================================================

@api.view("/cbv-response")
class ResponseTypeViewSet(ViewSet):
    """ViewSet demonstrating different response types."""

    async def get(self, request, response_type: str = "json"):
        """GET /cbv-response - Return different response types based on parameter."""
        if response_type == "plain":
            return PlainText("Hello from ViewSet")
        elif response_type == "html":
            return HTML("<h1>Hello from ViewSet</h1>")
        elif response_type == "redirect":
            return Redirect("/", status_code=302)
        else:
            return {"type": "json", "message": "Hello from ViewSet"}


@api.view("/cbv-header")
class HeaderViewSet(ViewSet):
    """ViewSet for header extraction."""

    async def get(self, request, x: Annotated[str, Header(alias="x-test")]):
        """GET /cbv-header - Extract custom header."""
        return PlainText(f"Header: {x}")


@api.view("/cbv-cookie")
class CookieViewSet(ViewSet):
    """ViewSet for cookie extraction."""

    async def post(self, request, val: Annotated[str, Cookie(alias="session")]):
        """POST /cbv-cookie - Extract cookie."""
        return PlainText(f"Cookie: {val}")


# ============================================================================
# Streaming ViewSets - Using Decorator Syntax
# ============================================================================

@api.view("/cbv-stream")
class StreamViewSet(ViewSet):
    """ViewSet for streaming responses."""

    @no_compress
    async def get(self, request):
        """GET /cbv-stream - Stream plain text."""
        def gen():
            for i in range(100):
                yield "x"
        return StreamingResponse(gen, media_type="text/plain")


@api.view("/cbv-sse")
class SSEViewSet(ViewSet):
    """ViewSet for Server-Sent Events."""

    @no_compress
    async def get(self, request):
        """GET /cbv-sse - Stream SSE events."""
        def gen():
            for i in range(3):
                yield f"data: {i}\n\n"
        return StreamingResponse(gen, media_type="text/event-stream")


@api.view("/cbv-chat-completions")
class ChatCompletionsViewSet(ViewSet):
    """ViewSet for OpenAI-style chat completions."""

    @no_compress
    async def post(self, request, payload: ChatCompletionRequest):
        """POST /cbv-chat-completions - Handle chat completions with streaming support."""
        created = int(time.time())
        model = payload.model or "gpt-4o-mini"
        chat_id = "chatcmpl-bolt-cbv"

        if payload.stream:
            async def agen():
                delay = max(0, payload.delay_ms or 0) / 1000.0
                for i in range(max(1, payload.n_chunks)):
                    chunk = ChatCompletionChunk(
                        id=chat_id,
                        created=created,
                        model=model,
                        choices=[ChatCompletionChunkChoice(
                            index=0,
                            delta=ChatCompletionChunkDelta(content=payload.token),
                            finish_reason=None
                        )]
                    )
                    chunk_json = msgspec.json.encode(chunk)
                    yield b"data: " + chunk_json + b"\n\n"

                    if delay > 0:
                        await asyncio.sleep(delay)

                # Final chunk
                final_chunk = ChatCompletionChunk(
                    id=chat_id,
                    created=created,
                    model=model,
                    choices=[ChatCompletionChunkChoice(
                        index=0,
                        delta=ChatCompletionChunkDelta(),
                        finish_reason="stop"
                    )]
                )
                final_json = msgspec.json.encode(final_chunk)
                yield b"data: " + final_json + b"\n\n"
                yield b"data: [DONE]\n\n"

            return StreamingResponse(agen(), media_type="text/event-stream")

        # Non-streaming
        text = (payload.token * max(1, payload.n_chunks)).strip()
        response = {
            "id": chat_id,
            "object": "chat.completion",
            "created": created,
            "model": model,
            "choices": [
                {"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}
            ],
        }
        return response




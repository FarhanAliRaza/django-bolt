from typing import Optional, List, Annotated
import msgspec
import asyncio
import time
import json
from django_bolt import BoltAPI, JSON
from django_bolt.param_functions import Header, Cookie, Form, File
from django_bolt.responses import PlainText, HTML, Redirect, FileResponse, StreamingResponse
from django_bolt.exceptions import HTTPException

api = BoltAPI()


class Item(msgspec.Struct):
    name: str
    price: float
    is_offer: Optional[bool] = None


@api.get("/")
async def read_root():
    return {"Hello": "World"}


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


# ==== Streaming endpoints for benchmarks ====
@api.get("/stream")
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
async def sse_async_batch():
    """Optimized async endpoint that yields all data at once to reduce overhead"""
    async def agen():
        # Batch all data into single yield to minimize GIL crossings
        all_data = "".join(f"data: {i}\n\n" for i in range(3))
        yield all_data
    return StreamingResponse(agen(), media_type="text/event-stream")


@api.post("/v1/chat/completions-async")
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

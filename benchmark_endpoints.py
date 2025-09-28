# Additional benchmark endpoints for comparing optimization approaches
# Add this to the main api.py or import these endpoints

import time
import json
import msgspec
from typing import Optional, List

from django_bolt import BoltAPI
from django_bolt.responses import StreamingResponse

# These would be imported from the main api.py
from testproject.api import ChatCompletionRequest, ChatCompletionChunk, ChatCompletionChunkChoice, ChatCompletionChunkDelta

api = BoltAPI()

@api.post("/v1/chat/completions-baseline")
async def openai_chat_completions_baseline(payload: ChatCompletionRequest):
    """Baseline: original dict + json.dumps approach for comparison."""
    created = int(time.time())
    model = payload.model or "gpt-4o-mini"
    chat_id = "chatcmpl-baseline"

    if payload.stream:
        async def baseline_agen():
            delay = max(0, payload.delay_ms or 0) / 1000.0
            for _ in range(max(1, payload.n_chunks)):
                # Original slow approach: dict + json.dumps + string
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
                    await asyncio.sleep(delay)
            final = {
                "id": chat_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            yield f"data: {json.dumps(final, separators=(',', ':'))}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(baseline_agen(), media_type="text/event-stream")

    # Non-streaming path
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


@api.post("/v1/chat/completions-msgspec-dict")
async def openai_chat_completions_msgspec_dict(payload: ChatCompletionRequest):
    """Middle ground: dict + msgspec.json.encode for comparison."""
    created = int(time.time())
    model = payload.model or "gpt-4o-mini"
    chat_id = "chatcmpl-msgspec-dict"

    if payload.stream:
        async def msgspec_dict_agen():
            delay = max(0, payload.delay_ms or 0) / 1000.0
            for _ in range(max(1, payload.n_chunks)):
                # msgspec.json.encode with dict (faster than json.dumps)
                data = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [
                        {"index": 0, "delta": {"content": payload.token}, "finish_reason": None}
                    ],
                }
                chunk_json = msgspec.json.encode(data)
                yield b"data: " + chunk_json + b"\n\n"
                if delay > 0:
                    await asyncio.sleep(delay)
            final = {
                "id": chat_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            final_json = msgspec.json.encode(final)
            yield b"data: " + final_json + b"\n\n"
            yield b"data: [DONE]\n\n"
        return StreamingResponse(msgspec_dict_agen(), media_type="text/event-stream")

    # Non-streaming path
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
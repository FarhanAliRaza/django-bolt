import json
import time
import asyncio
from typing import Optional
from django.http import JsonResponse, HttpResponse, FileResponse, StreamingHttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.views import View
from asgiref.sync import sync_to_async
from users.models import User
import os

# ========== Main API endpoints ==========

async def read_root(request):
    """GET /plain/"""
    return HttpResponse("Hello, World!")
    # return JsonResponse({"Hello": "World"})


async def read_item(request, item_id):
    """GET /plain/items/<item_id>"""
    q = request.GET.get('q')
    return JsonResponse({"item_id": item_id, "q": q})


@csrf_exempt
async def update_item(request, item_id):
    """PUT /plain/items/<item_id>"""
    if request.method != 'PUT':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        return JsonResponse({
            "item_name": data.get('name'),
            "item_id": item_id
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


async def items100(request):
    """GET /plain/items100"""
    items = [
        {
            "name": f"item{i}",
            "price": float(i),
            "is_offer": (i % 2 == 0)
        }
        for i in range(100)
    ]
    return JsonResponse(items, safe=False)


# ========== Benchmark endpoints ==========

@csrf_exempt
async def bench_parse(request):
    """POST /plain/bench/parse"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        payload = json.loads(request.body)
        return JsonResponse({
            "ok": True,
            "n": len(payload.get('items', [])),
            "count": payload.get('count', 0)
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


async def bench_slow(request):
    """GET /plain/bench/slow - Async view for slow operation"""
    ms = request.GET.get('ms', '100')
    try:
        ms = int(ms)
    except ValueError:
        ms = 100
    
    delay = max(0, ms) / 1000.0
    await asyncio.sleep(delay)
    return JsonResponse({"ok": True, "ms": ms})


# ========== Header/Cookie/Exception/HTML/Redirect endpoints ==========

async def get_header(request):
    """GET /plain/header"""
    x_test = request.headers.get('x-test', '')
    return HttpResponse(x_test, content_type='text/plain')


async def get_cookie(request):
    """GET /plain/cookie"""
    session_val = request.COOKIES.get('session', '')
    return HttpResponse(session_val, content_type='text/plain')


async def raise_exc(request):
    """GET /plain/exc"""
    raise Http404("Not found")


async def get_html(request):
    """GET /plain/html"""
    return HttpResponse("<h1>Hello</h1>", content_type='text/html')


async def get_redirect(request):
    """GET /plain/redirect"""
    return redirect('/', permanent=False)


# ========== Form and File upload endpoints ==========

@csrf_exempt
async def handle_form(request):
    """POST /plain/form"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    name = request.POST.get('name', '')
    try:
        age = int(request.POST.get('age', '0'))
    except ValueError:
        age = 0
    email = request.POST.get('email', 'default@example.com')
    
    return JsonResponse({
        "name": name,
        "age": age,
        "email": email
    })


@csrf_exempt
async def handle_upload(request):
    """POST /plain/upload"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    files = request.FILES.getlist('file')
    file_info = [
        {"name": f.name, "size": f.size}
        for f in files
    ]
    
    return JsonResponse({
        "uploaded": len(files),
        "files": file_info
    })


@csrf_exempt
async def handle_mixed(request):
    """POST /plain/mixed-form"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    title = request.POST.get('title', '')
    description = request.POST.get('description', '')
    attachments = request.FILES.getlist('file')
    
    result = {
        "title": title,
        "description": description,
        "has_attachments": bool(attachments)
    }
    if attachments:
        result["attachment_count"] = len(attachments)
    
    return JsonResponse(result)


# ========== File serving endpoint ==========

async def file_static(request):
    """GET /plain/file-static"""
    THIS_FILE = os.path.abspath(__file__)
    return FileResponse(
        open(THIS_FILE, 'rb'),
        as_attachment=True,
        filename='views.py'
    )


# ========== Streaming endpoints ==========

async def stream_plain(request):
    """GET /plain/stream"""
    async def generate():
        for i in range(100):
            yield b"x"
    return StreamingHttpResponse(generate(), content_type='text/plain')


async def collected_plain(request):
    """GET /plain/collected"""
    return HttpResponse("x" * 100, content_type='text/plain')


async def sse(request):
    """GET /plain/sse"""
    async def generate():
        for i in range(3):
            yield f"data: {i}\n\n".encode()
    return StreamingHttpResponse(generate(), content_type='text/event-stream')


async def sse_async(request):
    """GET /plain/sse-async"""
    async def generate():
        for i in range(3):
            yield f"data: {i}\n\n".encode()
            await asyncio.sleep(0)
    return StreamingHttpResponse(generate(), content_type='text/event-stream')


# ========== OpenAI-style Chat Completions ==========

@csrf_exempt
async def openai_chat_completions(request):
    """POST /plain/v1/chat/completions"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    created = int(time.time())
    model = payload.get('model', 'gpt-4o-mini')
    chat_id = "chatcmpl-django-bench"
    stream = payload.get('stream', True)
    n_chunks = max(1, payload.get('n_chunks', 50))
    token = payload.get('token', ' hello')
    delay_ms = max(0, payload.get('delay_ms', 0))
    
    if stream:
        def generate():
            delay = delay_ms / 1000.0
            for i in range(n_chunks):
                data = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [
                        {"index": 0, "delta": {"content": token}, "finish_reason": None}
                    ],
                }
                yield f"data: {json.dumps(data, separators=(',', ':'))}\n\n".encode()
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
            yield f"data: {json.dumps(final, separators=(',', ':'))}\n\n".encode()
            yield b"data: [DONE]\n\n"
        
        return StreamingHttpResponse(generate(), content_type='text/event-stream')
    
    # Non-streaming response
    text = (token * n_chunks).strip()
    response = {
        "id": chat_id,
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [
            {"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}
        ],
    }
    return JsonResponse(response)


@csrf_exempt
async def openai_chat_completions_async(request):
    """POST /plain/v1/chat/completions-async"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        body = await sync_to_async(lambda: request.body)()
        payload = json.loads(body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    created = int(time.time())
    model = payload.get('model', 'gpt-4o-mini')
    chat_id = "chatcmpl-django-bench-async"
    stream = payload.get('stream', True)
    n_chunks = max(1, payload.get('n_chunks', 50))
    token = payload.get('token', ' hello')
    delay_ms = max(0, payload.get('delay_ms', 0))
    
    if stream:
        async def generate():
            delay = delay_ms / 1000.0
            for _ in range(n_chunks):
                data = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [
                        {"index": 0, "delta": {"content": token}, "finish_reason": None}
                    ],
                }
                yield f"data: {json.dumps(data, separators=(',', ':'))}\n\n".encode()
                if delay > 0:
                    await asyncio.sleep(delay)
            
            final = {
                "id": chat_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            yield f"data: {json.dumps(final, separators=(',', ':'))}\n\n".encode()
            yield b"data: [DONE]\n\n"
        
        return StreamingHttpResponse(generate(), content_type='text/event-stream')
    
    # Non-streaming response
    text = (token * n_chunks).strip()
    response = {
        "id": chat_id,
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [
            {"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}
        ],
    }
    return JsonResponse(response)


# ========== User API endpoints ==========

async def users_root(request):
    """GET /plain/users/"""
    return JsonResponse({"ok": True})


async def list_full_10(request):
    """GET /plain/users/full10"""
    @sync_to_async
    def fetch():
        users = User.objects.all()[:10]
        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active
            }
            for user in users
        ]
    
    users = await fetch()
    return JsonResponse(users, safe=False)


async def list_mini_10(request):
    """GET /plain/users/mini10"""
    @sync_to_async
    def fetch():
        users = User.objects.only("id", "username")[:10]
        return [
            {
                "id": user.id,
                "username": user.username
            }
            for user in users
        ]
    
    users = await fetch()
    return JsonResponse(users, safe=False)

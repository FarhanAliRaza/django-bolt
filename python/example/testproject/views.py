from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from core.models import Blog
from test_data import JSON_10K, JSON_1K
import time

def index(request):
    return JsonResponse(JSON_1K, safe=False)


@require_http_methods(["GET"])
def blog_home(request):
    """Traditional Django view serving blog homepage with database query."""
    start_time = time.time()

    # Database query for published blogs
    blogs = Blog.objects.filter(status="published").values('id', 'name', 'description', 'status')
    blogs_list = list(blogs)

    render_time = round((time.time() - start_time) * 1000, 2)

    context = {
        'blogs': blogs_list,
        'blogs_count': len(blogs_list),
        'server_type': 'Gunicorn + Django (WSGI)',
        'render_time': render_time,
    }

    return render(request, 'blog_home.html', context)

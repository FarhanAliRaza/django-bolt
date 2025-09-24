from django.urls import path
from . import views

app_name = 'plain'

urlpatterns = [
    # Main API endpoints
    path('', views.read_root, name='root'),
    path('items/<int:item_id>', views.read_item, name='read_item'),
    path('items/<int:item_id>/update', views.update_item, name='update_item'),
    path('items100', views.items100, name='items100'),
    
    # Benchmark endpoints
    path('bench/parse', views.bench_parse, name='bench_parse'),
    path('bench/slow', views.bench_slow, name='bench_slow'),
    
    # Header/Cookie/Exception/HTML/Redirect endpoints
    path('header', views.get_header, name='get_header'),
    path('cookie', views.get_cookie, name='get_cookie'),
    path('exc', views.raise_exc, name='raise_exc'),
    path('html', views.get_html, name='get_html'),
    path('redirect', views.get_redirect, name='get_redirect'),
    
    # Form and File upload endpoints
    path('form', views.handle_form, name='handle_form'),
    path('upload', views.handle_upload, name='handle_upload'),
    path('mixed-form', views.handle_mixed, name='handle_mixed'),
    
    # File serving endpoint
    path('file-static', views.file_static, name='file_static'),
    
    # Streaming endpoints
    path('stream', views.stream_plain, name='stream_plain'),
    path('collected', views.collected_plain, name='collected_plain'),
    path('sse', views.sse, name='sse'),
    path('sse-async', views.sse_async, name='sse_async'),
    
    # OpenAI-style Chat Completions
    path('v1/chat/completions', views.openai_chat_completions, name='openai_chat_completions'),
    path('v1/chat/completions-async', views.openai_chat_completions_async, name='openai_chat_completions_async'),
    
    # User API endpoints
    path('users/', views.users_root, name='users_root'),
    path('users/full10', views.list_full_10, name='list_full_10'),
    path('users/mini10', views.list_mini_10, name='list_mini_10'),
]
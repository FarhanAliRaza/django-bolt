from django.http import JsonResponse
from test_data import JSON_10K, JSON_1K

def index(request):
    return JsonResponse(JSON_1K, safe=False)

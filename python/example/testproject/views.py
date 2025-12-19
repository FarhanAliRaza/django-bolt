import time

from django.http import JsonResponse, StreamingHttpResponse


def index(request):
    return JsonResponse({}, safe=False)

def sse(request):
    """Server-Sent Events endpoint that sends timestamp data every second"""
    def gen():
        while True:
            time.sleep(1)
            yield f"data: {time.time()}\n\n"

    return StreamingHttpResponse(gen(), content_type="text/event-stream")

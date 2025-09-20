from django_bolt import BoltAPI, JSON

api = BoltAPI()


@api.get("/hello")
async def hello(req):
    """Sample API endpoint"""
    return JSON({"message": "Hello from Django-Bolt!"})


@api.get("/health")
async def health(req):
    """Health check endpoint"""
    return JSON({"status": "ok"})


@api.get("/status")
async def status(req):
    """Project status endpoint"""
    return JSON({"project": "testproject", "apis": 2})

# Django-Bolt Test Project

This is a working example of Django-Bolt integration with a Django project.

## What's been tested ✅

### 1. `django-bolt init` command

- Automatically finds Django project root
- Adds `'django_bolt'` to `INSTALLED_APPS`
- Creates project-level `api.py` with sample routes
- Provides clear next steps

### 2. `python manage.py runbolt` command

- **Zero-config autodiscovery** of BoltAPI instances
- Discovers project-level APIs: `testproject/api.py`
- Discovers app-level APIs: `users/api.py`
- **Route conflict detection** with clear error messages
- **Prefix support** for app-level APIs (`/users/...`)

### 3. API Structure

#### Project-level API (`testproject/api.py`)

```python
from django_bolt import BoltAPI, JSON

api = BoltAPI()  # No prefix - routes at root level

@api.get("/hello")
async def hello(req):
    return JSON({"message": "Hello from Django-Bolt!"})

@api.get("/health")
async def health(req):
    return JSON({"status": "ok"})

@api.get("/status")
async def status(req):
    return JSON({"project": "testproject", "apis": 2})
```

#### App-level API (`users/api.py`)

```python
from django_bolt import BoltAPI, JSON

api = BoltAPI(prefix="/users")  # All routes prefixed with /users

@api.get("/")  # → /users/
async def list_users(req):
    return JSON({"users": ["alice", "bob", "charlie"]})

@api.get("/{user_id}")  # → /users/{user_id}
async def get_user(req):
    user_id = req.get("params", {}).get("user_id")
    return JSON({"user_id": user_id, "name": f"User {user_id}"})

@api.post("/")  # → /users/
async def create_user(req):
    return JSON({"message": "User created", "id": 123})

@api.get("/test")  # → /users/test
async def test_users(req):
    return JSON({"from_users_app": True})
```

## Available Routes

When you run `python manage.py runbolt`, these routes are available:

- `GET /hello` - Hello message
- `GET /health` - Health check
- `GET /status` - Project status
- `GET /users/` - List users
- `GET /users/{user_id}` - Get specific user
- `POST /users/` - Create user
- `GET /users/test` - Test endpoint

## Running the server

```bash
# Standard Django setup
python manage.py migrate
python manage.py createsuperuser  # optional

# Start Django-Bolt server
python manage.py runbolt

# With custom options
python manage.py runbolt --host 0.0.0.0 --port 8000 --workers 4
```

## Key Features Demonstrated

1. **Zero configuration** - Just run `python manage.py runbolt`
2. **Multi-app support** - APIs from multiple apps are merged automatically
3. **Prefix support** - Apps can namespace their routes
4. **Conflict detection** - Clear errors when routes conflict
5. **Single-arg handlers** - Fast `handler(req)` pattern for performance
6. **Standard Django integration** - Works with existing Django projects

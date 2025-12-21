---
icon: lucide/zap
---

# Django-Bolt

Django-Bolt is a high-performance API framework for Django. It lets you build APIs using familiar Django patterns while leveraging Rust for speed.

## Installation

Install using pip:

```bash
pip install django-bolt
```

Or with uv:

```bash
uv add django-bolt
```

Then initialize in your Django project:

```bash
django-bolt init
```

This adds `django_bolt` to your `INSTALLED_APPS` and creates an `api.py` file.

## At a glance

Here's a simple API endpoint:

```python
from django_bolt import BoltAPI

api = BoltAPI()

@api.get("/hello")
async def hello():
    return {"message": "Hello, World!"}
```

Run it with:

```bash
python manage.py runbolt
```

That's it. You now have an API endpoint at `http://localhost:8000/hello`.

## Why Django-Bolt?

Django-Bolt is designed for developers who:

- Already know Django and want to build APIs quickly
- Need high performance without leaving Python
- Want type-safe request handling with automatic validation
- Prefer async/await for I/O-bound operations

## Key features

**Simple routing** - Decorator-based routing similar to FastAPI and Flask:

```python
@api.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
```

**Automatic validation** - Request data is validated using Python type hints:

```python
import msgspec

class CreateUser(msgspec.Struct):
    username: str
    email: str

@api.post("/users")
async def create_user(user: CreateUser):
    return {"username": user.username}
```

**Django integration** - Works with your existing Django models and ORM:

```python
from myapp.models import User

@api.get("/users")
async def list_users():
    users = await User.objects.all().acount()
    return {"count": users}
```

**Built-in authentication** - JWT and API key authentication out of the box:

```python
from django_bolt.auth import JWTAuthentication, IsAuthenticated

@api.get("/profile", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def profile(request):
    return {"user_id": request.context.get("user_id")}
```

## Next steps

- **[Installation](getting-started/installation.md)** - Full installation guide with all options
- **[Quick Start](getting-started/quickstart.md)** - Build your first API
- **[Deployment](getting-started/deployment.md)** - Deploy with multiple processes

## Getting help

- Check the [topic guides](topics/routing.md) for in-depth explanations
- Look at the [API reference](ref/api.md) for detailed information
- Report issues on [GitHub](https://github.com/FarhanAliRaza/django-bolt/issues)

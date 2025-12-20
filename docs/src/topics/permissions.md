# Permissions

Django-Bolt uses "guards" to control access to endpoints. Guards are permission checks that run in Rust after authentication but before your handler is called.

## Built-in guards

### IsAuthenticated

Requires a valid authentication token:

```python
from django_bolt.auth import JWTAuthentication, IsAuthenticated

@api.get("/profile", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def profile(request):
    return {"user_id": request.context.get("user_id")}
```

Returns 401 Unauthorized if authentication fails.

### IsAdminUser

Requires the user to be a superuser:

```python
from django_bolt.auth import IsAdminUser

@api.delete("/admin/users/{user_id}", auth=[JWTAuthentication()], guards=[IsAdminUser()])
async def delete_user(user_id: int):
    # Only superusers can access this
    return {"deleted": user_id}
```

Returns 403 Forbidden if the user is not a superuser.

### IsStaff

Requires the user to have staff status:

```python
from django_bolt.auth import IsStaff

@api.get("/admin/dashboard", auth=[JWTAuthentication()], guards=[IsStaff()])
async def admin_dashboard():
    return {"dashboard": "staff only"}
```

### HasPermission

Requires a specific Django permission:

```python
from django_bolt.auth import HasPermission

@api.post("/articles", auth=[JWTAuthentication()], guards=[HasPermission("blog.add_article")])
async def create_article():
    return {"created": True}
```

Permission strings follow Django's format: `app_label.permission_codename`.

### HasAnyPermission

Requires at least one of the specified permissions (OR logic):

```python
from django_bolt.auth import HasAnyPermission

@api.get(
    "/content",
    auth=[JWTAuthentication()],
    guards=[HasAnyPermission(["blog.view_article", "blog.add_article"])]
)
async def view_content():
    return {"content": "visible"}
```

### HasAllPermissions

Requires all specified permissions (AND logic):

```python
from django_bolt.auth import HasAllPermissions

@api.delete(
    "/articles/{id}",
    auth=[JWTAuthentication()],
    guards=[HasAllPermissions(["blog.delete_article", "blog.change_article"])]
)
async def delete_article(id: int):
    return {"deleted": id}
```

### AllowAny

Explicitly allows any request, bypassing authentication:

```python
from django_bolt.auth import AllowAny

@api.get("/public", guards=[AllowAny()])
async def public():
    return {"message": "Anyone can see this"}
```

## Combining guards

Use multiple guards for layered security:

```python
@api.post(
    "/admin/settings",
    auth=[JWTAuthentication()],
    guards=[IsAuthenticated(), IsStaff(), HasPermission("core.change_settings")]
)
async def update_settings():
    return {"updated": True}
```

Guards are checked in order. The request is rejected as soon as any guard fails.

## Error responses

Guards return appropriate HTTP status codes:

| Guard | Failure Status |
|-------|----------------|
| `IsAuthenticated` | 401 Unauthorized |
| `IsAdminUser` | 403 Forbidden |
| `IsStaff` | 403 Forbidden |
| `HasPermission` | 403 Forbidden |
| `HasAnyPermission` | 403 Forbidden |
| `HasAllPermissions` | 403 Forbidden |

## Permissions in JWT tokens

For guards to work, your JWT tokens must include the relevant claims:

```python
from django_bolt.auth import create_jwt_for_user

# This function automatically includes permissions from the user
token = create_jwt_for_user(user, expires_in=3600)
```

The token includes:

- `is_staff` - For `IsStaff` guard
- `is_superuser` - For `IsAdminUser` guard
- `permissions` - List of permission strings for `HasPermission` guards

## Default guards

Set default guards for all endpoints:

```python
api = BoltAPI(
    default_auth=[JWTAuthentication()],
    default_guards=[IsAuthenticated()]
)

# All endpoints require authentication by default

@api.get("/data")
async def get_data():
    return {"protected": True}

# Override for public endpoints
@api.get("/health", guards=[AllowAny()])
async def health():
    return {"status": "ok"}
```

## Runtime permission checks

For complex permission logic, perform checks in your handler:

```python
from django_bolt.exceptions import Forbidden

@api.delete(
    "/articles/{article_id}",
    auth=[JWTAuthentication()],
    guards=[IsAuthenticated()]
)
async def delete_article(request, article_id: int):
    article = await Article.objects.aget(id=article_id)

    # Check if user owns the article or is admin
    user_id = request.context.get("user_id")
    is_superuser = request.context.get("is_superuser")

    if str(article.author_id) != user_id and not is_superuser:
        raise Forbidden(detail="You can only delete your own articles")

    await article.adelete()
    return {"deleted": article_id}
```

## Performance

Guards run in Rust before your Python handler is called. This means:

- Invalid requests are rejected without Python GIL overhead
- Authentication and authorization happen in a single pass
- Your handler only runs for authorized requests

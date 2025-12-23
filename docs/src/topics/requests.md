---
icon: lucide/arrow-down-to-line
---

# Request Handling

This guide covers how Django-Bolt processes requests and how to access request data in your handlers.

## The request object

Access the full request using a `request` parameter:

```python
@api.get("/info")
async def request_info(request):
    return {
        "method": request.get("method"),
        "path": request.get("path"),
    }
```

## Request properties

The request dict contains:

| Property | Type | Description |
|----------|------|-------------|
| `method` | `str` | HTTP method (GET, POST, etc.) |
| `path` | `str` | Request path |
| `query` | `dict` | Query parameters |
| `params` | `dict` | Path parameters |
| `headers` | `dict` | Request headers |
| `body` | `bytes` | Raw request body |
| `context` | `dict` | Authentication context |

## Type-safe request

For better IDE support, use the `Request` type:

```python
from django_bolt import Request

@api.get("/profile", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def profile(request: Request):
    # IDE knows about .user, .context, .get(), etc.
    return {"user_id": request.user.id}
```

The `Request` type provides:

- `request.user` - Authenticated user (lazy loaded)
- `request.context` - Authentication context dict
- `request.get(key, default)` - Get request property
- `request[key]` - Access request property

## Path parameters

Extract path parameters using curly braces in the route and matching function arguments:

```python
@api.get("/users/{user_id}/posts/{post_id}")
async def get_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}
```

Type conversion happens automatically:

- `int` - Converts to integer
- `float` - Converts to float
- `str` - Keeps as string (default)

Invalid conversions return a 422 Unprocessable Entity.

## Query parameters

Parameters without path placeholders become query parameters:

```python
@api.get("/search")
async def search(
    q: str,              # Required
    page: int = 1,       # Optional with default
    limit: int = 20,     # Optional with default
    sort: str | None = None  # Optional, None if not provided
):
    return {"q": q, "page": page, "limit": limit, "sort": sort}
```

## Request body

### JSON body

Use `msgspec.Struct` for validated JSON bodies:

```python
import msgspec

class CreateUser(msgspec.Struct):
    username: str
    email: str
    age: int | None = None

@api.post("/users")
async def create_user(user: CreateUser):
    return {"username": user.username}
```

### Raw body access

Access the raw body bytes:

```python
@api.post("/raw")
async def raw_body(request):
    body = request.get("body", b"")
    return {"size": len(body)}
```

## Headers

### Using Annotated

Extract specific headers:

```python
from typing import Annotated
from django_bolt.param_functions import Header

@api.get("/auth")
async def check_auth(
    authorization: Annotated[str, Header(alias="Authorization")]
):
    return {"auth": authorization}
```

### Optional headers

```python
@api.get("/optional-header")
async def optional_header(
    custom: Annotated[str | None, Header(alias="X-Custom")] = None
):
    return {"custom": custom}
```

### All headers

Access all headers from the request:

```python
@api.get("/headers")
async def all_headers(request):
    headers = request.get("headers", {})
    return {"headers": dict(headers)}
```

## Cookies

Extract cookie values:

```python
from typing import Annotated
from django_bolt.param_functions import Cookie

@api.get("/session")
async def get_session(
    session_id: Annotated[str, Cookie(alias="sessionid")]
):
    return {"session_id": session_id}
```

## Form data

### URL-encoded forms

```python
from typing import Annotated
from django_bolt.param_functions import Form

@api.post("/login")
async def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()]
):
    return {"username": username}
```

### Multipart forms

```python
@api.post("/profile")
async def update_profile(
    name: Annotated[str, Form()],
    bio: Annotated[str, Form()] = ""
):
    return {"name": name, "bio": bio}
```

## Parameter models

You can use `msgspec.Struct` or `Serializer` to group related parameters into a single validated object. This works with `Form()`, `Query()`, `Header()`, and `Cookie()`.

### Form models

Group form fields into a struct:

```python
import msgspec
from typing import Annotated
from django_bolt.param_functions import Form

class LoginForm(msgspec.Struct):
    username: str
    password: str
    remember_me: bool = False

@api.post("/login")
async def login(form: Annotated[LoginForm, Form()]):
    return {"username": form.username, "remember": form.remember_me}
```

With `Serializer` for custom validation:

```python
from django_bolt.serializers import Serializer, field_validator

class RegisterForm(Serializer):
    username: str
    email: str
    password: str

    @field_validator("username")
    def validate_username(cls, value):
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters")
        return value

@api.post("/register")
async def register(form: Annotated[RegisterForm, Form()]):
    return {"username": form.username}
```

### Query models

Group query parameters:

```python
class FilterParams(msgspec.Struct):
    limit: int = 10
    offset: int = 0
    search: str | None = None
    sort_by: str = "created_at"

@api.get("/items")
async def list_items(params: Annotated[FilterParams, Query()]):
    return {
        "limit": params.limit,
        "offset": params.offset,
        "search": params.search
    }
```

Request: `GET /items?limit=20&search=test`

### Header models

Group headers into a struct. Field names are converted from `snake_case` to `kebab-case` for HTTP header lookup:

```python
class AuthHeaders(msgspec.Struct):
    x_api_key: str           # maps to X-Api-Key header
    x_request_id: str | None = None  # maps to X-Request-Id header

@api.get("/secure")
async def secure_endpoint(headers: Annotated[AuthHeaders, Header()]):
    return {"api_key": headers.x_api_key}
```

Request: `GET /secure` with headers `X-Api-Key: secret123`

### Cookie models

Group cookies:

```python
class SessionCookies(msgspec.Struct):
    session_id: str
    theme: str = "light"
    language: str = "en"

@api.get("/preferences")
async def get_preferences(cookies: Annotated[SessionCookies, Cookie()]):
    return {"theme": cookies.theme, "language": cookies.language}
```

### Benefits of parameter models

| Feature | Individual params | Parameter models |
|---------|-------------------|------------------|
| Reusability | Copy-paste params | Define once, use everywhere |
| Validation | Per-field only | Custom `@field_validator` |
| Defaults | Per-field | Centralized in struct |
| IDE support | Basic | Full autocomplete |
| Documentation | Manual | Auto-generated from struct |

## File uploads

```python
from typing import Annotated
from django_bolt.param_functions import File

@api.post("/upload")
async def upload(
    files: Annotated[list[dict], File(alias="file")]
):
    for f in files:
        print(f"Received: {f.get('filename')} ({f.get('size')} bytes)")

    return {"uploaded": len(files)}
```

Each file dict contains:

- `filename` - Original filename
- `content_type` - MIME type
- `size` - Size in bytes
- `content` - File bytes

### Mixed form and files

```python
@api.post("/submit")
async def submit(
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    attachments: Annotated[list[dict], File(alias="file")] = []
):
    return {
        "title": title,
        "attachments": len(attachments)
    }
```

## Dependency injection

Use `Depends` for reusable parameter extractors:

```python
from django_bolt import Depends

async def get_pagination(page: int = 1, limit: int = 20):
    return {"page": page, "limit": limit, "offset": (page - 1) * limit}

@api.get("/items")
async def list_items(pagination=Depends(get_pagination)):
    return {"pagination": pagination}
```

Dependencies can be chained and cached. See [Dependency Injection](../ref/api.md#dependency-injection) for more details.

## Validation errors

When request validation fails, Django-Bolt returns a 422 Unprocessable Entity with details:

```json
{
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "Expected `str` - at `$.email`",
            "type": "validation_error"
        }
    ]
}
```

Common validation scenarios that return 422:

| Scenario | Example Message |
|----------|-----------------|
| Missing required query param | `Missing required query parameter: page` |
| Missing required header | `Missing required header: x-api-key` |
| Missing required cookie | `Missing required cookie: session` |
| Missing required form field | `Missing required form field: username` |
| Missing required file | `Missing required file: document` |
| Type conversion failure | `Invalid integer value: 'abc'` |
| Struct field validation | `name: Name must be at least 3 characters` |

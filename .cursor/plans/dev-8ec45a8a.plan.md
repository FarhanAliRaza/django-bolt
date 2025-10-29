<!-- 8ec45a8a-1707-4e72-8607-65e81372a309 4f63531b-122b-4532-aaba-90bb9ad526a0 -->
# Dev-time Type Safety for Django‑Bolt

### Goals

- Generate editor-only types (Pyright/Pylance) for models, QuerySets, and request params.
- Zero runtime impact; opt-in via a dev CLI.
- Simple defaults; extensible when needed.

### High-level design

- Dev CLI scans Django apps and emits .pyi stubs for models/QuerySets under `stubs/`.
- Handlers need no decorator. Parameters are typed with generic wrappers: `Body[T]`, `Query[T]`, `Headers[T]`, `Path[T]`, `Cookies[T]`.
- Provide runtime wrappers + `.pyi` that alias wrappers to `T` so editors see plain `T`.
- Pyright reads `stubs/` via `pyrightconfig.json` → rich IntelliSense and errors.
- Real runtime remains Django; wrappers are thin metadata/injection helpers.

### File layout

- Generator: `python/django_bolt/_devtypes/` (inspector + emitters)
- Public types: `python/django_bolt/typing/` (`TypedRequest`, `TypedQuerySet`, managers, lookups)
- Output: `stubs/<package path>/... .pyi`
- Config: `pyrightconfig.json` with `stubPath: ["stubs"]`

### What it looks like (user experience)

- Models and queries
```python
from myapp.models import User

users = User.objects.filter(username="a").all()
# pyright: users -> list[User]
User.objects.filter(unknown="x")  # pyright error: unexpected kwarg "unknown"
User.objects.get(id="str")        # pyright error: id expects int
```

- Requests (body/query/headers/path) with msgspec
```python
import msgspec
from django_bolt import bolt, Request

class CreateBody(msgspec.Struct):
    username: str
    active: bool = True

class ListQuery(msgspec.Struct):
    active: bool | None = None

class AuthHeaders(msgspec.Struct):
    authorization: str

@bolt.validate(body=CreateBody, query=ListQuery, headers=AuthHeaders)
def create_user(request: Request):
    request.body.username     # typed: str
    request.query.active      # typed: bool | None
    request.headers.authorization
```

- The generator emits a stub like:
```python
# stubs/myapp/views.pyi
from django_bolt.typing import TypedRequest
from .models import User
from myapp.views import create_user as _create_user

def create_user(request: TypedRequest[CreateBody, ListQuery, AuthHeaders, None]) -> object: ...
```


…and model/QuerySet stubs like:

```python
# stubs/myapp/models.pyi
from django_bolt.typing import TypedQuerySet
from django.db.models import Model

class User(Model):
    id: int
    username: str
    active: bool
    objects: UserManager

class UserQuerySet(TypedQuerySet[User]):
    def filter(self, *, username: str | None = None, active: bool | None = None, id: int | None = None) -> UserQuerySet: ...
    def get(self, *, id: int | None = None, username: str | None = None) -> User: ...
    def all(self) -> list[User]: ...

class UserManager:
    def get_queryset(self) -> UserQuerySet: ...
    def create(self, *, username: str, active: bool = ...) -> User: ...
```

### Scope v1 (pragmatic)

- Fields: eq lookups only; infer Optional by `null=True`.
- Common relations: `FK → RelatedModel`, `M2M → TypedQuerySet[Related]`.
- QuerySet ops: `filter/get/all/first/create/update/delete` with precise returns.
- Request params: `msgspec.Struct` only; path params inferred from route pattern.

### Stretch v1.1

- Extra lookups by field kind: `__in`, `__lt/__gt`, `__icontains`.
- JSONField: configurable typed payload via annotation comment.
- `values`/`values_list` typed overloads.

### Pyright integration

- Add `pyrightconfig.json`:
```json
{
  "venvPath": ".",
  "stubPath": ["stubs"],
  "reportUnknownMemberType": true,
  "reportUnknownArgumentType": true
}
```

- Dev-only: run `uv run django-bolt types sync` (or `watch`) during development.

### Implementation details

- Django inspector loads project (DJANGO_SETTINGS_MODULE), walks `apps.get_models()`; maps fields → Python types; relations handled.
- Emitters write `.pyi` mirroring module paths (`<app>/models.pyi`, `<app>/views.pyi` where decorated views live).
- Typed core in `django_bolt/typing/` provides `TypedRequest[Body, Query, Headers, Path]`, `TypedQuerySet[T]`, and manager Protocols.
- Route decorator records param types for the inspector (via module-level registry), no runtime behavior change.
- Watch mode uses `watchfiles` to re-emit on model or view changes.

### Opt-in/escape hatches

- Per-app include/exclude via `pyproject.toml` under `tool.django-bolt.types`.
- Fallback to `Any` for unsupported custom fields.
- Users can import `from typing import TYPE_CHECKING` and refer to generated types without hard runtime deps.

### Validation/testing

- Add example app under `python/example/` showcasing completions and Pyright errors.
- CI job: `uvx pyright` against example to guard regressions.

### To-dos

- [ ] Create dev types CLI: sync and watch commands
- [ ] Add pyrightconfig.json and document VS Code setup
- [ ] Implement django_bolt.typing core (TypedRequest, TypedQuerySet, managers)
- [ ] Implement Django model inspector to extract fields/relations
- [ ] Emit .pyi for models/managers/querysets into stubs/
- [ ] Support equality lookups and Optional/null mapping
- [ ] Add @bolt.validate registry for body/query/headers/path types
- [ ] Emit .pyi for view functions with TypedRequest generics
- [ ] Implement watch mode with watchfiles to re-generate
- [ ] Write docs and example app demonstrating errors/completions
- [ ] Add typed lookups (__in, lt/gt, icontains) by field type
- [ ] Optional Astral ty integration command and docs
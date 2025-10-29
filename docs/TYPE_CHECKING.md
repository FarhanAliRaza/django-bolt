### Dev-time type safety for Django‑Bolt (editor-only stubs)

This adds opt‑in, development‑only type safety for Django models/queries and request params, designed to work great in VS Code with Pyright/Pylance and in CI.

It is non-invasive: nothing changes at runtime, and you don’t have to change how you write views. The system generates `.pyi` stubs and minimal typing shims that your editor/CI consumes for type checking.

---

### What’s included

- Generator: `django-bolt types` to emit `.pyi` stubs from your Django models
- Typed shims: `django_bolt.typecheck.TypedQuerySet[T]` and `TypedManager[T]`
  - Equality lookup kwargs on `filter/get/exclude` are typed per model
  - Primary key aliases: `id`, `pk`, and the actual pk field name are accepted
  - Common APIs with simple typing: `only`, `values`, `values_list`
  - Slicing support: `qs[:N] -> list[T]`
- Pyright config for local development

This brings immediate editor-time errors like:

```python
from users.models import User

User.objects.filter(unknown="x")   # error: unexpected kwarg "unknown"
User.objects.get(id="str")         # error: id expects int
User.objects.only("id")[:10]        # ok; slice returns list[User]
```

---

### Usage

1. Generate stubs (dev only)

Run from your Django project (where `manage.py` lives) and set your settings module:

```bash
export DJANGO_SETTINGS_MODULE=yourproject.settings
uv run django-bolt types sync            # writes to stubs/ (respects pyrightconfig.json)
uv run django-bolt types sync --overlay  # writes models.pyi next to each models.py (recommended for Pyright)
```

Watch mode (optional):

```bash
uv add watchfiles
uv run django-bolt types watch --overlay
```

2. VS Code / Pyright

- Pyright is already configured at repo root (`pyrightconfig.json`).
- Overlay mode is the most reliable for Pyright because it prefers a sibling `.pyi` over `.py` for your code.
- If you don’t want overlay files in the tree, use stubs mode and keep `stubPath: "stubs"` in `pyrightconfig.json`.

3. CI

Run the generator before checks so the type checker sees the stubs:

```yaml
name: Types
on: [push, pull_request]
jobs:
  types:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - name: Install deps
        run: uv sync --frozen
      - name: Generate stubs
        env:
          DJANGO_SETTINGS_MODULE: yourproject.settings
        run: uv run django-bolt types sync --overlay
      - name: Pyright
        run: uvx pyright
      # Optional: ty (Astral)
      - name: ty
        run: uvx ty check
```

---

### Hiding generated files in the editor

If overlay is distracting, hide the files from your workspace while still letting Pyright use them:

```gitignore
**/models.pyi
**/_types.pyi
stubs/**
```

```json
// .vscode/settings.json
{
  "files.exclude": {
    "**/models.pyi": true,
    "**/_types.pyi": true,
    "stubs/**": true
  },
  "files.watcherExclude": {
    "**/models.pyi": true,
    "**/_types.pyi": true,
    "stubs/**": true
  }
}
```

---

### Request param typing (Body / Query / Header / Path / Cookie)

You can keep using your current style with `typing.Annotated` and our markers from `django_bolt.param_functions`:

```python
from typing import Annotated
from django_bolt.param_functions import Body, Query, Header
import msgspec

class CreateUser(msgspec.Struct):
    username: str
    is_active: bool = True

class ListQuery(msgspec.Struct):
    page: int | None = None

@api.post("/users")
async def create_user(user: Annotated[CreateUser, Body()]):
    return user

@api.get("/users")
async def list_users(q: Annotated[ListQuery, Query()], x: Annotated[str, Header(alias="x-test")]):
    return []
```

The binding/validation rules you already use continue to work; the added value here is editor-time type checking for these inputs and your ORM calls.

---

### How it works (high level)

- Inspector walks `apps.get_models()` and extracts fields and relations
  - Infers Optional from `null=True`
  - Adds `id`/`pk` aliases for the primary key
  - Adds `<fk>_id` alias for ForeignKey filters
- Emitter writes per-app `.pyi` files:
  - `models.pyi` declares the model attributes and `UserQuerySet`/`UserManager` with typed kwargs
  - `_types.pyi` provides convenience types used under `TYPE_CHECKING` if needed
- Typed shims live in `django_bolt/typecheck` and are importable by the stubs
- Overlay mode writes stubs next to your `models.py` so Pyright takes them over the `.py` source automatically; otherwise they go into `stubs/` and Pyright reads them via `stubPath`.

---

### Limitations (v1)

- Equality lookups only (`field=value`). Planned: `__in`, `__lt/__gt`, `__icontains`.
- `values`/`values_list` have coarse return typing; field-precise overloads are planned.
- `annotate`, `aggregate` typing is not yet modeled.
- Custom field types fall back to `Any`.

---

### Relationship to django‑stubs

- [`django-stubs`](https://github.com/typeddjango/django-stubs) ships framework stubs and a mypy plugin. It does not generate per‑project model stubs, and the plugin is mypy‑only.
- This feature complements it by generating project‑specific `.pyi` so Pyright/Pylance in VS Code can flag unknown kwargs and type mismatches inside your app code.
- You can use both: django‑stubs + mypy for CI; overlay stubs for Pyright editor‑time checks.

---

### Developer notes (what changed in the codebase)

- New: `python/django_bolt/typecheck/__init__.py` — defines `TypedQuerySet[T]` and `TypedManager[T]` with indexing/slicing, common APIs.
- New: Dev generator under `python/django_bolt/_devtypes/`:
  - `inspector.py` (model metadata), `emit.py` (write `.pyi`), `cli.py` (sync/watch, `--overlay`).
- CLI: `django_bolt/cli.py` adds `types` command group.
- Config: `pyrightconfig.json` updated to discover `stubs/` and the workspace.

This is dev‑only; no runtime behavior changed.

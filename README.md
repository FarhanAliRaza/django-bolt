## Django‑Bolt (experimental)

Fast, typed HTTP APIs for Django using a Rust engine and msgspec serialization. This project is a prototype exploring how far we can push performance while keeping a simple, familiar developer experience.

### What this is

- **Rust server core**: Actix + Tokio behind the scenes, driven from Python via pyo3-asyncio.
- **Simple API syntax**: Define routes with `BoltAPI` decorators (`get/post/put/patch/delete`).
- **Typed params + body**: Function parameters are bound from path/query; request bodies decode into `msgspec.Struct`.
- **Typed responses**: Validate/serialize responses using either the function return type annotation or a `response_model=` on the decorator. Django ORM objects are automatically coerced into your `msgspec.Struct` models.
- **Batteries included**: Example project, benchmarks, and tests.

### Status

This is an experimental project. The API is unstable and may change without notice. Do not use in production yet.

### Quick start

1. Build the native module (uses uv + maturin):

```bash
make build
```

2. Run the example server (multi‑process background):

```bash
make run-bg HOST=127.0.0.1 PORT=8000 WORKERS=2 P=2
# then
make smoke
```

3. Run tests:

```bash
make test-py
```

4. Run benchmarks (root, items, ORM, and Ninja‑style tests):

```bash
make save-bench
# knobs: C, N, P, WORKERS, SLOW_MS, SLOW_CONC, SLOW_DURATION, WORKER_SET
```

### Minimal usage

```python
import msgspec
from typing import Optional
from django_bolt import BoltAPI

api = BoltAPI()

class Item(msgspec.Struct):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    tags: list[str] = []

@api.post("/items/")
async def create_item(item: Item) -> Item:
    return item

@api.get("/items/", response_model=list[Item]) # return type and response_model both are supprted like FastAPI
async def read_items():
    return [Item(name="Portal Gun", price=42.0), Item(name="Plumbus", price=32.0)]
```

Notes:

- If both a return annotation and `response_model` are present, `response_model` wins.
- If neither is provided, responses are returned as‑is for maximal performance.

### Why msgspec?

`msgspec` provides extremely fast type validation and JSON encoding/decoding. We lean on it for both request body parsing and response serialization.

### Caveats

- Experimental: APIs and internals will change.
- Limited error handling: response validation errors currently return 500; this may change to 422 in the future.
- Benchmarks are local and environment‑dependent; treat numbers as indicative, not absolute.

### Contributing

Feedback, issues, and PRs are welcome. Please keep in mind the project is evolving quickly and performance is the primary goal.

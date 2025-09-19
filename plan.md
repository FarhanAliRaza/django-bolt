## Django-Bolt Performance Optimization Plan

This plan drives Django-Bolt to Actix-class throughput and better-than–FastAPI performance while remaining fully compatible with the Django ecosystem. The guiding constraints are:

- Only async Python views are exposed in the public API.
- Django remains the source of truth for models, migrations, admin, settings.
- Benchmarks are realistic and reproducible.

### High-level Goals (Community-aligned)

- Native REST API ergonomics people expect (decorators, Pydantic option, OpenAPI) with Django fidelity.
- Async-by-default view layer to unlock concurrency and streaming (SSE/WebSockets).
- Outperform FastAPI for common API shapes; be 5–10x faster than DRF.

Target single-host numbers (amd64, release, no TLS):

- Hello JSON: ≥ 100k RPS (single process), ≥ 200k RPS aggregate with N workers
- Simple ORM read: ≥ 10–20k RPS (Postgres), p95 ≤ 10–15 ms
- SSE tick: ≤ 1 ms tick overhead @ 10k concurrent
- WebSockets chat echo: ≥ 50k concurrent connections (memory bound)

---

## Current Baseline (as of MVP)

- Hello JSON via Python handler: ~19.5k RPS, p50 ≈ 5 ms (ab -k -c100)
- ORM `/users` on embedded SQLite: ~1.96k RPS, p50 ≈ 42 ms (ab -k -c100)

Notes: Embedded SQLite is not representative. Expect order-of-magnitude gains with Postgres + pooling and query shaping.

---

## Roadmap Overview

1. Async-only handler path and tight PyO3 integration
2. Rust-side request/response fast path and serialization
3. Router and middleware in Rust (path params, query decode, CORS, gzip)
4. Django async ORM happy path; DB tuning and pooling
5. Streaming (SSE), WebSockets, backpressure, and memory discipline
6. Multi-process worker model (1 Python interpreter per core)
7. Observability, benchmarking, and CI perf gates

Each step yields measurable speedups; we’ll capture metrics at every milestone.

---

## Default Behavior & DX (fast by default)

- Zero-config: choose the fastest pipeline automatically; users can override, but don’t need to.
- Handlers: async-only by default; sync raises a clear error (legacy adapter optional).
- Router & HTTP: Rust router and header/query parsing on by default; Django middlewares are bypassed for API routes. Full Django stack remains available for admin or compatibility mounts.
- Serialization: Pydantic v2 for request validation; msgspec for response JSON serialization by default. Optional Rust-side JSON for pure-Rust paths.
- Workers: default `workers = cpu_count` via SO_REUSEPORT; override with `--workers` or `DJANGO_BOLT_WORKERS`.
- Event loop: prefer uvloop automatically if present.
- Database: if `DATABASE_URL` is set, auto-configure Postgres (psycopg 3) with pooling; otherwise use embedded SQLite (WAL) for dev with a prod warning.
- Compression & CORS: enabled with safe defaults; can be disabled.
- Observability: JSON logs and `/metrics` enabled by default.
- Docs: OpenAPI served at `/docs` and `/openapi.json` by default; can be disabled.

Override model:

- Minimal settings surface (env or `DJANGO_BOLT` dict) to override defaults without changing code. DX stays the same either way.

## 1) Async-only Handler Path

Goal: Python APIs must be async; the bridge awaits coroutines directly without threadpools.

- Integrate `pyo3-asyncio` to bind Python event loop to Tokio.
- Dispatch contract: `dispatch(method, path, headers, body) -> await (status, headers, body)`.
- Hold the GIL only to schedule/resolve the awaitable; release during await.
- Detect accidental sync functions and fail fast with clear error.
- Provide `@api.get`/`@api.post` that wrap sync functions via `anyio.to_thread.run_sync` only for legacy migration, but default to async.

Why: eliminates unnecessary threadpool hops and reduces GIL contention for IO-bound work.

---

## 2) Rust Fast Path & Serialization

Goal: Minimize Python <-> Rust conversion overhead.

- Zero-copy request body into Python (pass PyBytes view) and avoid header churn.
- Add Rust-native JSON response helper:
  - If handler returns Python builtins (dict/list/str/bytes), keep current path.
  - If handler opts-in (`return RustJSON(data)` or decorator), serialize with `serde_json` in Rust via `pyo3-serde` for 2–4x faster dumps on large payloads.
- Pre-allocate response buffers; reuse small buffer pools.
- Optional `simd-json` feature flag for AVX2/NEON builds.

---

## 2.1) Typed Response Models & Schema Generation

Goal: FastAPI-like DX where return annotations drive response serialization and OpenAPI, with fastest default encoders.

- Introspect handler return type at route registration (e.g., `UserSchema`, `list[UserSchema]`).
- If the annotation is a Pydantic v2 model (or list thereof):
  - Use Pydantic for input validation.
  - For output, prefer `msgspec.json.encode(model.model_dump())` for maximum speed, or `model.model_dump_json()` when configured for pydantic-core JSON.
- If the annotation is a Django model (or list):
  - Auto-generate a Pydantic schema with `from_attributes=True` (fields from `_meta`).
  - Prefer queryset `.values(*fields)`/`.values_list()` to avoid per-instance attribute access; encode dicts via msgspec.
- Dev-only strict output validation (assert shape matches schema) with a toggle; disabled by default in production for zero overhead.
- Cache compiled encoders/field lists per route to avoid repeated work.
- Generate OpenAPI schemas from the discovered/auto-generated models.

## 3) Router & Middleware in Rust

Goal: O(1) route lookup with compiled patterns and minimal Python work per request.

- Implement a Rust router (method trie + path param extractor) and store Python handler objects by route ID.
- Extract path params, query params in Rust; pass a small dict (or tuple) to Python.
- CORS, gzip/deflate/br, request size limits, and basic auth/JWT verification implemented as Rust middlewares.
- Access log and per-endpoint latency histograms at the Rust layer.

---

## 4) Django ORM & DB Tuning

Goal: Make async ORM the happy-path; keep sync fallback efficient.

- Require Django ≥ 5.x for best async coverage; where ORM is sync, use `asgiref.sync.sync_to_async` with threadpool sized to DB cores.
- Encourage Postgres (psycopg 3) with:
  - `CONN_MAX_AGE` > 0 (keep-alive)
  - Prepared statements/cache
  - Proper pool sizing (via database server or external pooler like pgbouncer)
- Query shaping patterns in examples: `.values()`/`.only()`, pagination, avoiding N+1.
- Dev SQLite profile:
  - WAL mode, `PRAGMA synchronous=NORMAL`, batch writes; clearly mark as dev-only numbers.

---

## 5) Streaming & WebSockets

Goal: First-class async streaming with tight backpressure.

- SSE: Rust chunked encoder with heartbeat; Python generator/coroutine for payloads.
- WebSockets: actix-web-actors with Python callback hooks, or pure Rust actor with JSON hooks into Python.
- Backpressure: pause reading from socket when Python is busy; bounded channel between Rust and Python.

---

## 6) Multi-process Workers

Goal: Scale linearly across cores by running multiple Python interpreters.

- CLI/management: `--workers N` spawns N OS processes; SO_REUSEPORT for socket sharding.
- Use `actix_web::HttpServer::workers` inside each process for IO concurrency.
- Pin workers to cores (optional) and expose graceful shutdown.

---

## 7) Observability & CI Perf Gates

Goal: Track performance regressions and validate claims.

- Built-in structured logs (JSON), request IDs, timings, errors.
- `/metrics` (Prometheus) with QPS, latency, in-flight, memory.
- `scripts/bench.sh` or Make targets for: hello, users (ORM), SSE tick.
- CI job to run micro-bench (limited iterations) and post trends; nightly full bench.

---

## Bench Methodology (Reproducible)

- Tools: `oha` preferred, fallback to `ab`; same machine, no TLS.
- Matrix:
  - hello: c=[50,100,200], n large; record p50/p95/p99
  - users (Postgres): values-only response; same matrix
  - SSE tick: 1k–10k concurrent, tick latency and memory
- Compare against:
  - FastAPI (uvicorn, uvloop, httptools)
  - DRF (gunicorn+uvicorn workers)
- Publish scripts and configs.

---

## Implementation Milestones

1. Async dispatch via `pyo3-asyncio` and awaitable handlers
2. Rust router with path params + query decode; header map cleanup
3. Rust JSON serialization opt-in; buffer pool
4. Middleware: CORS, gzip, request limits, auth hook
5. ORM examples with Postgres + pooling; guidance docs; benchmarks
6. SSE and WebSockets minimal viable
7. Multi-process workers; CLI `--workers`; graceful shutdown
8. Metrics endpoint, structured logs; CI perf gate

Each milestone includes a benchmark to validate target deltas (documented in README/bench report).

---

## Community Alignment

- Async-first APIs, Pydantic option, class/function styles, and DRF migration story are all on the path.
- Our differentiator: Rust network stack and serialization fast path to push beyond FastAPI.
- Outcome: “Django-native API framework with modern performance and deployment.”

---

## Risks & Mitigations

- GIL contention: keep critical sections short; prefer Rust work; multi-process scaling.
- Async ORM gaps: ship sync bridge where needed; document coverage and caveats.
- Compatibility: maintain pure-Django escape hatches; avoid monkey-patching core internals.

---

## Done Definition (Phase: Performance Beta)

- Async handlers supported and required by default.
- Hello ≥ 60k RPS single process; users (Postgres) ≥ 10k RPS.
- Router + CORS + gzip in Rust; JSON fast path available.
- SSE + WebSockets examples stable; backpressure validated.
- Bench scripts and CI gates in place with published results.

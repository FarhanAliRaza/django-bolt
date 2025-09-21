## GIL optimization and scalability playbook

This document outlines concrete, high‑impact strategies to minimize Python GIL overhead in our framework without compromising features we plan to add (FastAPI‑style params, DI, and model serialization). This is a plan, not an implementation.

### Principles

- Keep Python time short and predictable: enter GIL briefly to create the coroutine and to extract results only.
- Prefer processes over threads for CPU parallelism; use threads for I/O parallelism.
- Move per‑request work to registration time (precompile adapters, encoders).
- Keep the hot path single‑arg and kwargs‑free to unlock CPython’s fast call path.

## Production‑ready optimizations (apply first)

### Multi‑process scaling (default)

- Start 1 OS process per core (or per NUMA node) with SO_REUSEPORT.
- Keep per‑process Actix workers small (1–2) to avoid GIL contention in a single interpreter.
- Keep a simple launcher (Makefile/CLI) to spawn N processes and manage PIDs/logs.

### Single‑arg fast call path

- Call Python handlers as `handler(req)` (no kwargs), reading path/query params from `req`.
- Benefits: enables CPython’s vectorcall, fewer allocations, smaller GIL sections.

### PyRequest pyclass with lazy fields

- Represent the request as a Rust `pyclass` (`req`), exposed as a single object.
- Lazily materialize `req.params`/`req.query`/`req.form` dicts only when accessed.
- Body accessible as bytes (later: memoryview when safe) to cut copies.

### msgspec‑first I/O path

- Request decode: use `msgspec` for JSON (and optionally CBOR/MessagePack).
- Response encode: use `msgspec` by default; allow custom content types.
- Precompile encoders for response models at startup.

### Scope‑local event loop context

- Cache `TaskLocals` per worker and use `pyo3_async_runtimes::tokio::scope_local` around the handler.
- Avoid per‑request loop setup or cross‑thread context passing.

### Actix runtime tuning

- KeepAlive=OS, client_request_timeout=0, small worker count per process.
- Bind pre‑created listener when SO_REUSEPORT is enabled.

## Advanced options (feature‑flagged / later)

### Subinterpreter pool (PEP 684)

- One Python subinterpreter per worker thread; no object sharing between interpreters.
- Pros: minimizes shared‑GIL contention within a process.
- Cons: more complex lifecycle; each interpreter maintains its own imports/state.

### Zero‑copy buffers (when safe)

- Request body as `memoryview` backed by reference‑counted bytes (or pinned buffers) to avoid copies.
- Streaming responses via iterables/async generators backed by Rust buffers.

### Precompiled route adapters (FastAPI semantics, no reflection at runtime)

- At route registration, inspect handler signature once and emit a tiny adapter to:
  - Extract typed path/query/header/body params from `req`.
  - Execute DI dependencies in precomputed order.
  - Validate/coerce using `msgspec.Struct` (fast path) or optional Pydantic v2.
- Store and call the adapter directly from Rust.

### No‑GIL readiness (PEP 703/CPython 3.13+)

- Treat GIL as an optimization barrier, not a correctness guarantee.
- Ensure all Rust shared state is thread‑safe (no reliance on GIL for safety).
- Avoid `static mut`; prefer `OnceCell/OnceLock` + `RwLock/Mutex`.
- Keep FFI boundaries “plain data” (bytes/str/ints/memoryview) so the same code path works under no‑GIL builds.

### HPy / C‑ABI future proofing

- Track HPy maturity for no‑GIL compatible extensions; consider an HPy shim for hot paths.

## Benchmarks and guardrails

- Track: RPS, p50/p99 latency, CPU%, context switches, GIL hold time (via sampling), allocations per request.
- Define budgets for added features (DI/validation/serialization) and test with adapters enabled.

## Suggested rollout order

1. Multi‑process launcher with SO_REUSEPORT (default production mode).
2. Single‑arg fast path + PyRequest (lazy fields) on hot path.
3. msgspec‑first request/response; precompiled encoders at startup.
4. Precompiled route adapters for params/DI/validation.
5. Subinterpreter pool (feature flag); keep multi‑process as default.
6. Zero‑copy buffers and streaming responses where safe.
7. Validate on no‑GIL Python builds as PyO3 support matures.

## Risks / notes

- Subinterpreters: per‑interpreter state can diverge; avoid sharing Python objects across interpreters.
- Zero‑copy: ensure Rust buffer lifetimes outlive Python views to avoid UAF.
- DI/validation ergonomics: keep Pydantic v2 optional to protect hot‑path RPS; use `msgspec.Struct` by default.

## After these optimizations

Once the production‑ready set (multi‑process launcher, single‑arg fast path, lazy `PyRequest`, msgspec I/O, scope‑local loop, tuned Actix) is in place, here’s how we proceed and what to expect:

- Expected impact (directional)

  - JSON echo/validate endpoints: substantial gains vs. pure‑Python stacks due to Rust networking + msgspec. Further wins taper off after the single‑arg/`PyRequest` path is in.
  - ORM endpoints: dominated by DB I/O; multi‑process and connection pooling matter more than micro‑optimizations in Python.
  - Latency improvements will mostly come from reducing per‑request allocations and avoiding extra JSON parses/serializations.

- Verification checklist (each change)

  - Measure RPS, p50/p99, CPU%, RSS, context switches with the included benchmarks.
  - Sample GIL hold time (e.g., py‑spy) during load; confirm short GIL regions around coroutine create/extract only.
  - Validate no functional regressions with our pytest suite (binding/body/response‑model/coercion tests).

- Guardrails / budgets

  - Feature budgets: new features must stay within a small RPS regression budget on JSON echo (e.g., ≤3–5%).
  - Keep the hot path: one Python call with one argument; avoid kwargs/varargs.
  - Prefer precomputed adapters at registration time rather than reflection per request.

- Next experiments (behind flags)

  - Streaming responses from Rust (chunked JSON/NDJSON) for large lists to lower memory and GIL contention.
  - Selective Rust‑side decode/validation for specific hot endpoints using reflected msgspec schemas, returning lightweight Python proxies.
  - Subinterpreter pool (PEP 684) per worker thread; validate startup cost and memory vs. gains.
  - Zero‑copy body buffers and memoryview exposure when safe.

- Ops tuning

  - Default to SO_REUSEPORT multi‑process; set workers low (1–2) per process; scale with `P` primarily.
  - Confirm keep‑alive settings and kernel backlog; pin CPU where helpful.

- When to stop optimizing
  - Once p50/p99 and throughput meet the SLA with headroom, prefer shipping features. Use flags to re‑enable deeper paths only if needed.

This playbook keeps Python time small and predictable, uses Rust for the event loop and networking, and applies heavier Rust‑side work only where it clearly beats msgspec + simple FFI.

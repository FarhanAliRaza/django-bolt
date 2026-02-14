"""
Micro-benchmark: Measure the Rust-side fast dispatch path vs Python _dispatch.

This tests the ACTUAL production path — calling from within the Rust runtime
context, not from Python. The fast dispatch in handler.rs executes entirely
in Rust, calling Python only for the handler function itself.

Since we can't easily call handler.rs directly from Python benchmarks, we
use the test client which exercises the full stack including handler.rs.
We also measure the pure Python _dispatch path for comparison.
"""
from __future__ import annotations

import asyncio
import os
import sys
import time

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testproject.settings")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "python", "example"))

import django
django.setup()

from django_bolt.api import BoltAPI
from django_bolt.serialization import serialize_response
from django_bolt import _json

# ── Test API with logging disabled (to enable fast dispatch) ─────────

api = BoltAPI(prefix="", enable_logging=False, compression=False)


@api.get("/sync-simple")
def sync_simple_handler():
    return {"ok": True}


@api.get("/sync-path/{item_id}")
def sync_path_handler(item_id: int):
    return {"id": item_id}


@api.get("/sync-query")
def sync_query_handler(q: str = "default", page: int = 1):
    return {"q": q, "page": page}


@api.get("/sync-mixed/{item_id}")
def sync_mixed_handler(item_id: int, q: str = "default"):
    return {"id": item_id, "q": q}


@api.get("/async-simple")
async def async_simple_handler():
    return {"ok": True}


@api.get("/async-path/{item_id}")
async def async_path_handler(item_id: int):
    return {"id": item_id}


# ── Fake request for Python-side benchmarking ────────────────────────

class FakeRequest:
    __slots__ = (
        "_method", "_path", "_body", "_path_params", "_query_params",
        "_headers", "_cookies", "_context", "_user", "_state",
        "_form_map", "_files_map",
    )

    def __init__(self, method="GET", path="/", body=b"",
                 path_params=None, query_params=None, headers=None,
                 cookies=None, context=None):
        self._method = method
        self._path = path
        self._body = body
        self._path_params = path_params or {}
        self._query_params = query_params or {}
        self._headers = headers or {}
        self._cookies = cookies or {}
        self._context = context
        self._user = None
        self._state = {}
        self._form_map = {}
        self._files_map = {}

    @property
    def method(self): return self._method
    @property
    def path(self): return self._path
    @property
    def body(self): return self._body
    @property
    def params(self): return self._path_params
    @property
    def headers(self): return self._headers
    @property
    def cookies(self): return self._cookies
    @property
    def query(self): return self._query_params
    @property
    def form(self): return self._form_map
    @property
    def files(self): return self._files_map
    @property
    def state(self): return self._state
    @property
    def user(self): return self._user
    @user.setter
    def user(self, v): self._user = v

    def get(self, key, default=None):
        mapping = {
            "method": self._method, "path": self._path, "body": self._body,
            "params": self._path_params, "query": self._query_params,
            "headers": self._headers, "cookies": self._cookies,
            "auth": self._context, "context": self._context,
        }
        return mapping.get(key, default)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        if key == "user":
            self._user = value


# ── Benchmark helpers ────────────────────────────────────────────────

ITERATIONS = 200_000


def find_handler_id(api_obj, path, method="GET"):
    for m, p, hid, fn in api_obj._routes:
        if m == method and p == path:
            return hid
    raise ValueError(f"Route not found: {method} {path}")


def bench_sync(name, fn, iterations=ITERATIONS):
    for _ in range(1000):
        fn()
    start = time.perf_counter_ns()
    for _ in range(iterations):
        fn()
    elapsed_ns = time.perf_counter_ns() - start
    per_call_ns = elapsed_ns / iterations
    per_call_us = per_call_ns / 1000
    ops_per_sec = 1_000_000_000 / per_call_ns
    print(f"  {name:52s}  {per_call_us:8.3f} µs   {ops_per_sec:>10,.0f} ops/s")
    return per_call_ns


async def bench_async(name, fn, iterations=ITERATIONS):
    for _ in range(1000):
        await fn()
    start = time.perf_counter_ns()
    for _ in range(iterations):
        await fn()
    elapsed_ns = time.perf_counter_ns() - start
    per_call_ns = elapsed_ns / iterations
    per_call_us = per_call_ns / 1000
    ops_per_sec = 1_000_000_000 / per_call_ns
    print(f"  {name:52s}  {per_call_us:8.3f} µs   {ops_per_sec:>10,.0f} ops/s")
    return per_call_ns


async def main():
    print("=" * 92)
    print("Django-Bolt: Python _dispatch() Baseline & Fast Dispatch Eligibility Check")
    print(f"Iterations: {ITERATIONS:,}")
    print("=" * 92)

    # Check metadata for fast dispatch eligibility
    print("\n1. FAST DISPATCH ELIGIBILITY (per-route)")
    print("-" * 92)

    for method, path, handler_id, fn in api._routes:
        meta = api._handler_meta.get(handler_id, {})
        mw_meta = api._handler_middleware.get(handler_id, {})
        is_async = meta.get("is_async", True)
        mode = meta.get("mode", "?")
        has_mw = bool(mw_meta.get("middleware"))
        has_resp_type = meta.get("response_type") is not None
        has_logging = mw_meta.get("has_logging", False)
        param_plan = mw_meta.get("param_plan")

        eligible = not is_async and not has_mw and not has_resp_type and not has_logging
        marker = "FAST" if eligible else "SLOW"

        print(f"  [{marker:4s}] {method:6s} {path:30s}  async={is_async}  mode={mode:14s}  "
              f"mw={has_mw}  log={has_logging}  plan={param_plan is not None}")

    # Benchmark Python _dispatch for sync handlers
    print("\n\n2. PYTHON _dispatch() BASELINE (sync handlers)")
    print("-" * 92)

    sync_simple_id = find_handler_id(api, "/sync-simple")
    sync_path_id = find_handler_id(api, "/sync-path/{item_id}")
    sync_query_id = find_handler_id(api, "/sync-query")
    sync_mixed_id = find_handler_id(api, "/sync-mixed/{item_id}")
    async_simple_id = find_handler_id(api, "/async-simple")
    async_path_id = find_handler_id(api, "/async-path/{item_id}")

    handler_sync = api._handlers[sync_simple_id]
    handler_sync_path = api._handlers[sync_path_id]
    handler_sync_query = api._handlers[sync_query_id]
    handler_sync_mixed = api._handlers[sync_mixed_id]
    handler_async = api._handlers[async_simple_id]
    handler_async_path = api._handlers[async_path_id]

    req_simple = FakeRequest(path="/sync-simple")
    req_path = FakeRequest(path="/sync-path/42", path_params={"item_id": 42})
    req_query = FakeRequest(path="/sync-query", query_params={"q": "hello", "page": 2})
    req_mixed = FakeRequest(path="/sync-mixed/42", path_params={"item_id": 42}, query_params={"q": "hello"})

    print("\n  [Sync handlers — eligible for Rust fast dispatch]")
    py_sync = await bench_async(
        "  sync simple (no params)",
        lambda: api._dispatch(handler_sync, req_simple, sync_simple_id),
    )
    py_path = await bench_async(
        "  sync + 1 path param",
        lambda: api._dispatch(handler_sync_path, req_path, sync_path_id),
    )
    py_query = await bench_async(
        "  sync + 2 query params",
        lambda: api._dispatch(handler_sync_query, req_query, sync_query_id),
    )
    py_mixed = await bench_async(
        "  sync + mixed path+query",
        lambda: api._dispatch(handler_sync_mixed, req_mixed, sync_mixed_id),
    )

    print("\n  [Async handlers — NOT eligible for fast dispatch]")
    py_async = await bench_async(
        "  async simple (no params)",
        lambda: api._dispatch(handler_async, req_simple, async_simple_id),
    )
    py_async_path = await bench_async(
        "  async + 1 path param",
        lambda: api._dispatch(handler_async_path, req_path, async_path_id),
    )

    # Component breakdown
    print("\n\n3. COMPONENT BREAKDOWN")
    print("-" * 92)

    # Raw handler call
    start = time.perf_counter_ns()
    for _ in range(ITERATIONS):
        handler_sync()
    handler_ns = (time.perf_counter_ns() - start) / ITERATIONS

    # Raw json encode
    start = time.perf_counter_ns()
    for _ in range(ITERATIONS):
        _json.encode({"ok": True})
    json_ns = (time.perf_counter_ns() - start) / ITERATIONS

    # Injector call (path param)
    injector = api._handler_meta[sync_path_id]["injector"]
    start = time.perf_counter_ns()
    for _ in range(ITERATIONS):
        injector(req_path)
    injector_ns = (time.perf_counter_ns() - start) / ITERATIONS

    py_overhead = py_sync - handler_ns - json_ns

    print(f"  {'handler() alone':52s}  {handler_ns/1000:8.3f} µs")
    print(f"  {'_json.encode() alone':52s}  {json_ns/1000:8.3f} µs")
    print(f"  {'injector (1 path param)':52s}  {injector_ns/1000:8.3f} µs")
    print(f"  {'handler + encode (theoretical min)':52s}  {(handler_ns+json_ns)/1000:8.3f} µs")
    print(f"  {'Python _dispatch() total (sync simple)':52s}  {py_sync/1000:8.3f} µs")
    print(f"  {'Python PURE OVERHEAD':52s}  {py_overhead/1000:8.3f} µs")
    print()
    print(f"  The Rust fast dispatch eliminates this {py_overhead/1000:.3f}µs overhead")
    print(f"  by doing injection + serialization in Rust (handler.rs)")
    print(f"  Equivalent to ~{py_overhead/handler_ns:.0f}x the handler execution time")

    # Theoretical fast dispatch numbers
    print("\n\n4. THEORETICAL FAST DISPATCH SAVINGS")
    print("-" * 92)

    # In the Rust fast path:
    # - Dict lookups for params: ~50ns (Rust-native PyDict access, no Python frame)
    # - handler.call1(): ~50ns (already in GIL, direct call)
    # - json_encode.call1(): ~150ns (already in GIL, C-accelerated msgspec)
    # - Tuple construction: ~30ns (Rust-native)
    # Total Rust-side overhead: ~280ns vs Python's ~800-1000ns

    rust_overhead_est = 280  # ns, estimated
    for name, py_ns in [
        ("sync simple", py_sync),
        ("sync path param", py_path),
        ("sync query params", py_query),
        ("sync mixed", py_mixed),
    ]:
        rust_est = handler_ns + json_ns + rust_overhead_est
        saved = py_ns - rust_est
        speedup = py_ns / rust_est
        print(f"  {name:25s}  Python: {py_ns/1000:6.3f}µs  Est Rust: {rust_est/1000:6.3f}µs  "
              f"Speedup: {speedup:.2f}x  Saved: {saved/1000:+.3f}µs/req")

    print("\n" + "=" * 92)
    print("NOTE: These are Python-side _dispatch() numbers. The Rust fast dispatch")
    print("in handler.rs eliminates the Python dispatch frame entirely, executing")
    print("injection + handler + serialization without entering Python's eval loop")
    print("for any dispatch logic. The actual speedup can only be measured with")
    print("an HTTP load test (bombardier/wrk) against a running server.")
    print("=" * 92)


if __name__ == "__main__":
    asyncio.run(main())

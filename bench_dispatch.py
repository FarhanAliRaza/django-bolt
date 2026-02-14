"""
Micro-benchmark: Python dispatch overhead vs Rust single-call fast path.

KEY INSIGHT: Each Python→Rust FFI crossing costs ~0.5-1µs. Calling separate
Rust functions from Python is SLOWER. The win comes from doing the ENTIRE
dispatch (inject + call handler + serialize) in ONE Rust function call.

This benchmark tests:
1. Python serialize_response() vs Rust fast_serialize_json() (standalone)
2. Full Python _dispatch() vs Rust fast_dispatch_full() (single FFI crossing)
3. Overhead breakdown
"""
from __future__ import annotations

import asyncio
import os
import sys
import time

# Setup Django before any imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testproject.settings")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "python", "example"))

import django
django.setup()

from django_bolt.api import BoltAPI
from django_bolt.serialization import serialize_response
from django_bolt import _json

# Import Rust fast dispatch functions
from django_bolt._core import (
    DispatchInfo,
    fast_serialize_json,
    fast_dispatch_full,
)

# ── Create a test API with various handler patterns ──────────────────────

api = BoltAPI(prefix="", enable_logging=False, compression=False)


@api.get("/simple")
async def simple_handler():
    return {"ok": True}


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


# Async versions
@api.get("/path/{item_id}")
async def path_handler(item_id: int):
    return {"id": item_id}


@api.get("/query")
async def query_handler(q: str = "default", page: int = 1):
    return {"q": q, "page": page}


@api.get("/mixed/{item_id}")
async def mixed_handler(item_id: int, q: str = "default"):
    return {"id": item_id, "q": q}


# ── Build fake PyRequest-like objects ────────────────────────────────────

class FakeRequest:
    __slots__ = (
        "_method", "_path", "_body", "_path_params", "_query_params",
        "_headers", "_cookies", "_context", "_user", "_state",
        "_form_map", "_files_map",
    )

    def __init__(self, method="GET", path="/simple", body=b"",
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


# ── Benchmark helpers ────────────────────────────────────────────────────

ITERATIONS = 200_000


def find_handler_id(api_obj, path, method="GET"):
    for m, p, hid, fn in api_obj._routes:
        if m == method and p == path:
            return hid
    raise ValueError(f"Route not found: {method} {path}")


def bench_sync(name, fn, iterations=ITERATIONS):
    # Warmup
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


def build_dispatch_info(api_obj, handler_id, param_plan=None):
    """Build a DispatchInfo from existing handler metadata."""
    meta = api_obj._handler_meta[handler_id]
    mode = 0 if meta["mode"] == "request_only" else 1
    return DispatchInfo(
        handler_id=handler_id,
        mode=mode,
        is_async=meta["is_async"],
        is_blocking=meta.get("is_blocking", False),
        default_status_code=meta["default_status_code"],
        has_middleware=False,
        has_response_type=meta["response_type"] is not None,
        has_file_uploads=meta.get("has_file_uploads", False),
        injector=meta.get("injector"),
        injector_is_async=meta.get("injector_is_async", False),
        param_plan=param_plan,
    )


async def main():
    print("=" * 92)
    print("Django-Bolt: Python _dispatch() vs Rust fast_dispatch_full() (single FFI crossing)")
    print(f"Iterations: {ITERATIONS:,}")
    print("=" * 92)

    # Setup — async handlers (for Python _dispatch baseline)
    simple_id = find_handler_id(api, "/simple")
    path_id = find_handler_id(api, "/path/{item_id}")
    query_id = find_handler_id(api, "/query")
    mixed_id = find_handler_id(api, "/mixed/{item_id}")

    # Sync handlers (for Rust fast_dispatch)
    sync_simple_id = find_handler_id(api, "/sync-simple")
    sync_path_id = find_handler_id(api, "/sync-path/{item_id}")
    sync_query_id = find_handler_id(api, "/sync-query")
    sync_mixed_id = find_handler_id(api, "/sync-mixed/{item_id}")

    req_simple = FakeRequest(path="/simple")
    req_path = FakeRequest(path="/path/42", path_params={"item_id": 42})
    req_query = FakeRequest(path="/query", query_params={"q": "hello", "page": 2})
    req_mixed = FakeRequest(path="/mixed/42", path_params={"item_id": 42}, query_params={"q": "hello"})

    handler_simple = api._handlers[simple_id]
    handler_sync = api._handlers[sync_simple_id]
    handler_path = api._handlers[path_id]
    handler_query = api._handlers[query_id]
    handler_mixed = api._handlers[mixed_id]
    handler_sync_path = api._handlers[sync_path_id]
    handler_sync_query = api._handlers[sync_query_id]
    handler_sync_mixed = api._handlers[sync_mixed_id]

    meta_simple = api._handler_meta[simple_id]

    # DispatchInfo objects with param_plan for inline Rust injection
    di_sync = build_dispatch_info(api, sync_simple_id)
    di_sync_path = build_dispatch_info(api, sync_path_id, param_plan=[("item_id", 0, None)])
    di_sync_query = build_dispatch_info(api, sync_query_id, param_plan=[("q", 1, "default"), ("page", 1, 1)])
    di_sync_mixed = build_dispatch_info(api, sync_mixed_id, param_plan=[("item_id", 0, None), ("q", 1, "default")])

    # ═══════════════════════════════════════════════════════════════════════
    # 1. SERIALIZE RESPONSE: standalone comparison
    # ═══════════════════════════════════════════════════════════════════════
    print("\n1. SERIALIZE RESPONSE: Python vs Rust (standalone, for reference)")
    print("-" * 92)

    test_dict = {"ok": True}

    py_ser = await bench_async(
        "[Python] serialize_response({'ok': True})",
        lambda: serialize_response(test_dict, meta_simple),
    )
    rust_ser = bench_sync(
        "[Rust]   fast_serialize_json({'ok': True})",
        lambda: fast_serialize_json(test_dict, 200),
    )
    print(f"\n  Note: Rust standalone is SLOWER ({py_ser/rust_ser:.2f}x) due to FFI crossing")
    print(f"  But when combined with handler call, the crossing is amortized\n")

    # ═══════════════════════════════════════════════════════════════════════
    # 2. FULL DISPATCH: Python _dispatch() vs Rust fast_dispatch_full()
    # ═══════════════════════════════════════════════════════════════════════
    print("2. FULL DISPATCH: Python _dispatch() vs Rust fast_dispatch_full()")
    print("   (single FFI crossing: inject + call handler + serialize)")
    print("-" * 92)

    # -- Python full dispatch (sync handlers via async _dispatch) --
    print("\n  [Python _dispatch — sync handlers through async dispatch]")
    py_sync = await bench_async(
        "  sync simple (no params, dict return)",
        lambda: api._dispatch(handler_sync, req_simple, sync_simple_id),
    )
    py_sync_path = await bench_async(
        "  sync + 1 path param (int)",
        lambda: api._dispatch(handler_sync_path, req_path, sync_path_id),
    )
    py_sync_query = await bench_async(
        "  sync + 2 query params (str + int)",
        lambda: api._dispatch(handler_sync_query, req_query, sync_query_id),
    )
    py_sync_mixed = await bench_async(
        "  sync + mixed path + query",
        lambda: api._dispatch(handler_sync_mixed, req_mixed, sync_mixed_id),
    )

    # For reference: async dispatch overhead
    print("\n  [Python _dispatch — async handlers]")
    py_simple = await bench_async(
        "  async simple (no params, dict return)",
        lambda: api._dispatch(handler_simple, req_simple, simple_id),
    )
    py_path = await bench_async(
        "  async + 1 path param (int)",
        lambda: api._dispatch(handler_path, req_path, path_id),
    )

    # -- Rust fast_dispatch_full (one FFI call, sync only) --
    print("\n  [Rust fast_dispatch_full — one FFI call, sync handlers]")
    rust_sync = bench_sync(
        "  sync simple (no params, dict return)",
        lambda: fast_dispatch_full(handler_sync, req_simple, di_sync),
    )
    rust_path = bench_sync(
        "  sync + 1 path param (inline inject in Rust)",
        lambda: fast_dispatch_full(handler_sync_path, req_path, di_sync_path),
    )
    rust_query = bench_sync(
        "  sync + 2 query params (inline inject in Rust)",
        lambda: fast_dispatch_full(handler_sync_query, req_query, di_sync_query),
    )
    rust_mixed = bench_sync(
        "  sync + mixed path+query (inline inject in Rust)",
        lambda: fast_dispatch_full(handler_sync_mixed, req_mixed, di_sync_mixed),
    )

    # ═══════════════════════════════════════════════════════════════════════
    # 3. COMPARISON TABLE
    # ═══════════════════════════════════════════════════════════════════════
    print("\n\n3. SPEEDUP COMPARISON")
    print("-" * 92)

    comparisons = [
        ("sync simple", py_sync, rust_sync),
        ("sync path param", py_sync_path, rust_path),
        ("sync query params", py_sync_query, rust_query),
        ("sync mixed", py_sync_mixed, rust_mixed),
    ]

    print(f"  {'Handler':25s}  {'Python':>10s}  {'Rust':>10s}  {'Speedup':>10s}  {'Saved':>10s}")
    print(f"  {'-'*25}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*10}")
    for name, py_ns, rust_ns in comparisons:
        py_us = py_ns / 1000
        rust_us = rust_ns / 1000
        speedup = py_ns / rust_ns
        saved = (py_ns - rust_ns) / 1000
        marker = " ***" if speedup > 1.0 else ""
        print(f"  {name:25s}  {py_us:8.3f}µs  {rust_us:8.3f}µs  {speedup:8.2f}x  {saved:+8.3f}µs{marker}")

    # ═══════════════════════════════════════════════════════════════════════
    # 4. OVERHEAD BREAKDOWN
    # ═══════════════════════════════════════════════════════════════════════
    print("\n\n4. OVERHEAD BREAKDOWN (simple handler)")
    print("-" * 92)

    # Handler alone (no framework)
    start = time.perf_counter_ns()
    for _ in range(ITERATIONS):
        handler_sync()
    handler_ns = (time.perf_counter_ns() - start) / ITERATIONS

    # Raw json encode (minimum possible)
    start = time.perf_counter_ns()
    for _ in range(ITERATIONS):
        _json.encode({"ok": True})
    json_ns = (time.perf_counter_ns() - start) / ITERATIONS

    py_overhead = py_sync - handler_ns - json_ns
    rust_overhead = rust_sync - handler_ns - json_ns

    print(f"  {'handler() alone':50s}  {handler_ns/1000:8.3f} µs")
    print(f"  {'_json.encode() alone':50s}  {json_ns/1000:8.3f} µs")
    print(f"  {'handler + encode (theoretical minimum)':50s}  {(handler_ns+json_ns)/1000:8.3f} µs")
    print()
    print(f"  {'Python _dispatch() total':50s}  {py_sync/1000:8.3f} µs")
    print(f"  {'Rust fast_dispatch_full() total':50s}  {rust_sync/1000:8.3f} µs")
    print()
    print(f"  {'Python PURE OVERHEAD (dispatch - handler - encode)':50s}  {py_overhead/1000:8.3f} µs")
    print(f"  {'Rust PURE OVERHEAD':50s}  {rust_overhead/1000:8.3f} µs")
    if rust_overhead > 0:
        print(f"  {'Overhead reduction':50s}  {py_overhead/rust_overhead:.2f}x less")
        savings_pct = (py_overhead - rust_overhead) / py_overhead * 100
        print(f"  {'% overhead eliminated':50s}  {savings_pct:.1f}%")

    print("\n" + "=" * 92)


if __name__ == "__main__":
    asyncio.run(main())

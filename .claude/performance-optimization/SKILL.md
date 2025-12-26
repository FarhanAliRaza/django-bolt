---
name: performance-optimization
description: "Apply systematic performance optimization techniques for Python and Rust code: estimation + profiling, API/bulk design, algorithmic wins, cache-friendly memory layout, fewer allocations, fast paths, caching, and compiler-friendly hot loops. Use for performance code reviews, refactors, and profiling-driven optimizations. Keywords: performance, latency, throughput, cache, allocation, memory layout, PyO3, msgspec, tokio, async, pprof, py-spy, perf."
license: Apache-2.0
compatibility: Skills-compatible coding agents working on Python and Rust codebases.
metadata:
  upstream_url: "https://abseil.io/fast/hints"
  upstream_authors: "Jeff Dean; Sanjay Ghemawat"
  upstream_original_version: "2023-07-27"
  upstream_last_updated: "2025-12-25"
---

# Python & Rust Performance Hints (Jeff Dean & Sanjay Ghemawat style)

This skill packages key ideas from Abseil's **Performance Hints** document, adapted for Python and Rust development.

Use it to:

- review Python/Rust code for performance risks
- propose high-impact optimizations with **explicit tradeoffs**
- design APIs/data structures that keep future optimizations possible
- write an experiment plan (profile + microbenchmark) to validate changes

## Scope and guardrails

- **Scope:** single-process / single-binary performance (CPU, memory, allocations, cache behavior).
- **Do not:** change externally observable behavior unless the user explicitly agrees.
- **Do not:** introduce undefined behavior, data races, or brittle "clever" micro-opts without evidence.
- **Default philosophy:** choose the faster alternative **when it doesn't materially harm readability or complexity**; otherwise, measure first.

## When to apply

Use this skill when the task involves any of:

- reducing **latency** or improving **throughput**
- cutting **memory footprint** or **allocation rate**
- improving **cache locality** / reducing cache misses
- designing performant **APIs** (bulk ops, view types, threading model)
- reviewing performance-sensitive Python or Rust changes
- interpreting a **flat profile** and finding next steps

## What to ask for (minimum inputs)

If you don't have enough information, ask for the smallest set that changes your recommendation quality:

1. **Goal:** latency vs throughput vs memory (and the SLO if any)
2. **Where:** hot path vs init vs test-only (and typical input sizes)
3. **Evidence:** profile / flame graph / perf counters / allocation profile (if available)
4. **Constraints:** correctness constraints, API constraints, thread-safety requirements

If none exists yet, proceed with _static analysis + "what to measure first"_.

---

# Workflow: how an agent should use these hints

## Step 1 — classify the code

- **Test code:** mostly care about asymptotic complexity and test runtime.
- **Application code:** separate **init/cold** vs **hot path**.
- **Library code:** prefer "safe, low-complexity" performance techniques because you can't predict callers.

## Step 2 — do a back-of-the-envelope estimate

Before implementing changes, estimate what might dominate:

1. Count expensive operations (seeks, round-trips, allocations, bytes touched, comparisons, etc.)
2. Multiply by rough cost.
3. If latency matters and there is concurrency, consider overlap.

### Reference latency table (rough order-of-magnitude)

| Operation                         |             Approx time |
| --------------------------------- | ----------------------: |
| L1 cache reference                |                  0.5 ns |
| L2 cache reference                |                    3 ns |
| Branch mispredict                 |                    5 ns |
| Mutex lock/unlock (uncontended)   |                   15 ns |
| Main memory reference             |                   50 ns |
| Python function call overhead     |               50-100 ns |
| Rust function call (non-inlined)  |                 1-10 ns |
| PyO3 GIL acquire/release          |              100-500 ns |
| Compress 1K bytes with Snappy     |                1,000 ns |
| Read 4KB from SSD                 |               20,000 ns |
| Round trip within same datacenter |               50,000 ns |
| Read 1MB sequentially from memory |               64,000 ns |
| Read 1MB over 100 Gbps network    |              100,000 ns |
| Read 1MB from SSD                 |     1,000,000 ns (1 ms) |
| Disk seek                         |     5,000,000 ns (5 ms) |
| Read 1MB sequentially from disk   |   10,000,000 ns (10 ms) |
| Send packet CA→Netherlands→CA     | 150,000,000 ns (150 ms) |

### Python-specific costs

| Operation                      |       Approx time |
| ------------------------------ | ----------------: |
| dict lookup                    |           20-50 ns |
| list.append                    |           20-40 ns |
| getattr on object              |           50-100 ns |
| isinstance check               |           30-60 ns |
| JSON parse (stdlib) 1KB        |           50-100 us |
| msgspec parse 1KB              |             5-15 us |
| Django ORM query (simple)      |           1-10 ms |
| Django ORM async query         |         0.5-5 ms |

### Rust-specific costs

| Operation                      |       Approx time |
| ------------------------------ | ----------------: |
| HashMap lookup                 |           10-30 ns |
| Vec push (no realloc)          |            2-10 ns |
| String allocation (small)      |           20-50 ns |
| Arc clone                      |           10-20 ns |
| tokio task spawn               |          200-500 ns |
| async channel send             |           50-200 ns |

### Estimation examples (templates)

**Web request through PyO3 bridge:**

- Rust HTTP parsing: ~1us
- GIL acquisition: ~200ns
- Python handler execution: ~50us (simple) to ~5ms (with ORM)
- Response serialization (msgspec): ~10us
- GIL release + Rust response: ~200ns
- Total: **~50us to ~5ms** depending on handler complexity

**Batch processing 10K items:**

- Per-item Python function call: 10K × 100ns = **1ms** (overhead alone)
- With msgspec struct validation: 10K × 500ns = **5ms**
- With dict allocation per item: 10K × 50ns = **0.5ms** (plus GC pressure)

## Step 3 — measure before paying complexity

When you can, measure to validate impact:

- **Python profiling:**
  - `py-spy` for sampling profiler (low overhead, production-safe)
  - `cProfile` for deterministic profiling (high overhead)
  - `memray` or `memory_profiler` for allocation profiling
  - `scalene` for CPU + memory + GPU profiling

- **Rust profiling:**
  - `perf` for Linux sampling profiler
  - `flamegraph` crate for generating flame graphs
  - `criterion` for microbenchmarks
  - `dhat` for allocation profiling

- Watch for **GIL contention** in Python: contention can lower CPU usage and hide the "real" bottleneck.
- Watch for **async runtime overhead** in Rust: too many small tasks can hurt more than help.

## Step 4 — pick the biggest lever first

Prioritize in this order unless evidence suggests otherwise:

1. **Algorithmic complexity** wins (O(N²) → O(N log N) or O(N))
2. **Data structure choice / memory layout** (cache locality; fewer cache lines)
3. **Allocation reduction** (fewer allocs, better reuse)
4. **Avoid unnecessary work** (fast paths, precompute, defer)
5. **Language boundary optimization** (minimize Python↔Rust crossings)
6. **Compiler/interpreter friendliness** (simplify hot loops, reduce abstraction overhead)

## Step 5 — produce an LLM-friendly output

When you respond to the user, use this structure:

1. **Hot path hypothesis** (what you think dominates, and why)
2. **Top issues** (ranked): _issue → evidence/estimate → proposed fix → expected impact_
3. **Patch sketch** (minimal code changes or pseudocode)
4. **Tradeoffs & risks** (correctness, memory, API, complexity)
5. **Measurement plan** (what to profile/benchmark and success criteria)

---

# Techniques and patterns

## 1) API design for performance

### Use bulk APIs to amortize overhead

**When:** callers do N similar operations (lookups, deletes, updates, decoding, locking).

**Why:** reduce boundary crossings and repeated fixed costs (locks, dispatch, decoding, syscalls).

**Python patterns:**

```python
# BAD: N database round trips
for user_id in user_ids:
    user = await User.objects.aget(id=user_id)

# GOOD: 1 database round trip
users = await sync_to_async(list)(User.objects.filter(id__in=user_ids))
users_by_id = {u.id: u for u in users}
```

**Rust patterns:**

```rust
// BAD: N individual operations
for id in ids {
    let result = cache.get(&id)?;
    // ...
}

// GOOD: Batch lookup
let results = cache.get_many(&ids)?;
```

### Prefer view types for function arguments

**Python:**
- Use `Sequence[T]` or `Iterable[T]` instead of `list[T]` when you don't mutate
- Accept `bytes` or `memoryview` instead of copying to `bytearray`
- Use `msgspec.Struct` for zero-copy deserialization

**Rust:**
- Use `&[T]` or `impl AsRef<[T]>` instead of `Vec<T>` when you don't need ownership
- Use `&str` instead of `String` for read-only string access
- Use `Cow<'_, T>` when you might need to own or borrow

### Thread-compatible vs thread-safe types

**Python:**
- Default to thread-compatible (external GIL or explicit locks)
- Use `threading.local()` for per-thread state
- Prefer `asyncio` over threads for I/O-bound work

**Rust:**
- Default to `Send + Sync` for shared state
- Use `Arc<RwLock<T>>` only when needed; prefer message passing
- Consider `dashmap` or sharded maps for high-contention scenarios

---

## 2) Algorithmic improvements

The rare-but-massive wins.

### Reduce complexity class

Common transformations:

- O(N²) → O(N log N) or O(N)
- O(N log N) sorted-list intersection → O(N) using a hash set
- O(log N) tree lookup → O(1) using hash lookup

### Python-specific patterns

```python
# BAD: O(N²) - checking membership in list
for item in items:
    if item in seen_list:  # O(N) lookup
        continue
    seen_list.append(item)

# GOOD: O(N) - using set
seen = set()
for item in items:
    if item in seen:  # O(1) lookup
        continue
    seen.add(item)

# BETTER: O(N) - using dict.fromkeys for deduplication
unique_items = list(dict.fromkeys(items))
```

### Rust-specific patterns

```rust
// BAD: O(N²) - nested iteration
for a in &items_a {
    for b in &items_b {
        if a.key == b.key {
            // ...
        }
    }
}

// GOOD: O(N) - hash lookup
let b_map: HashMap<_, _> = items_b.iter().map(|b| (&b.key, b)).collect();
for a in &items_a {
    if let Some(b) = b_map.get(&a.key) {
        // ...
    }
}
```

---

## 3) Better memory representation and cache locality

### Python: Prefer slots and dataclasses

```python
# BAD: Regular class with __dict__
class Item:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

# GOOD: Slots-based class (smaller memory, faster attribute access)
class Item:
    __slots__ = ('x', 'y', 'z')
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

# BETTER: msgspec.Struct (even more compact, fast serialization)
class Item(msgspec.Struct):
    x: int
    y: int
    z: int
```

### Python: Prefer numpy/array for numeric data

```python
# BAD: List of floats (each is a Python object)
values = [1.0, 2.0, 3.0, ...]  # ~28 bytes per float

# GOOD: numpy array (contiguous, cache-friendly)
values = np.array([1.0, 2.0, 3.0, ...])  # 8 bytes per float

# GOOD: array module for simpler cases
from array import array
values = array('d', [1.0, 2.0, 3.0, ...])
```

### Rust: Memory layout and padding

```rust
// BAD: 24 bytes due to padding
struct Item {
    flag: bool,      // 1 byte + 7 padding
    value: i64,      // 8 bytes
    count: i32,      // 4 bytes + 4 padding
}

// GOOD: 16 bytes with reordering
struct Item {
    value: i64,      // 8 bytes
    count: i32,      // 4 bytes
    flag: bool,      // 1 byte + 3 padding
}

// Use #[repr(C)] or #[repr(packed)] when ABI matters
```

### Rust: Indices instead of pointers

```rust
// Pointer-heavy: 8 bytes per reference, poor cache locality
struct Node {
    data: i32,
    left: Option<Box<Node>>,
    right: Option<Box<Node>>,
}

// Index-based: 4 bytes per reference, better cache locality
struct Tree {
    nodes: Vec<NodeData>,
}
struct NodeData {
    data: i32,
    left: Option<u32>,  // index into nodes
    right: Option<u32>,
}
```

### Rust: SmallVec and tinyvec for small collections

```rust
use smallvec::SmallVec;

// Stack allocation for up to 8 elements, heap only if larger
let mut items: SmallVec<[Item; 8]> = SmallVec::new();
```

---

## 4) Reduce allocations

### Python: Avoid unnecessary allocations

```python
# BAD: Creates new list on every call
def process(items):
    return [transform(item) for item in items]

# GOOD: Generator for streaming (no intermediate list)
def process(items):
    for item in items:
        yield transform(item)

# GOOD: Pre-allocate when size is known
def process(items):
    result = [None] * len(items)
    for i, item in enumerate(items):
        result[i] = transform(item)
    return result
```

### Python: Reuse objects

```python
# BAD: New dict on every iteration
for data in stream:
    result = {}  # allocation
    result['key'] = process(data)
    yield result

# GOOD: Reuse dict (if consumers don't hold reference)
result = {}
for data in stream:
    result.clear()
    result['key'] = process(data)
    yield result  # Caveat: only if consumer processes immediately
```

### Python: Use __slots__ to reduce memory

```python
# Without __slots__: ~152 bytes per instance
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# With __slots__: ~56 bytes per instance
class Point:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

### Rust: Pre-allocate with capacity

```rust
// BAD: Multiple reallocations
let mut results = Vec::new();
for item in items {
    results.push(transform(item));
}

// GOOD: Single allocation
let mut results = Vec::with_capacity(items.len());
for item in items {
    results.push(transform(item));
}

// BETTER: Use collect with size hint
let results: Vec<_> = items.iter().map(transform).collect();
```

### Rust: Avoid cloning when borrowing suffices

```rust
// BAD: Unnecessary clone
fn process(data: &Data) -> String {
    let s = data.name.clone();  // allocation
    format!("Hello, {}", s)
}

// GOOD: Borrow
fn process(data: &Data) -> String {
    format!("Hello, {}", &data.name)
}
```

---

## 5) Avoid unnecessary work

### Fast paths for common cases

**Python:**

```python
# BAD: Always takes slow path
def parse_int(s: str) -> int:
    return int(s)  # Handles all edge cases

# GOOD: Fast path for common ASCII digits
def parse_int(s: str) -> int:
    if len(s) <= 10 and s.isdigit():  # Fast check
        result = 0
        for c in s:
            result = result * 10 + (ord(c) - 48)
        return result
    return int(s)  # Fallback for edge cases
```

**Rust:**

```rust
// Fast path for single-byte varint (common case)
fn parse_varint(data: &[u8]) -> (u64, usize) {
    if data[0] < 128 {
        return (data[0] as u64, 1);  // 90% of cases
    }
    parse_varint_slow(data)  // Rare multi-byte
}
```

### Defer expensive computations

**Python:**

```python
# BAD: Always computes expensive value
def process(data, config):
    expensive = compute_expensive(data)  # Always runs
    if config.needs_expensive:
        use(expensive)

# GOOD: Defer until needed
def process(data, config):
    if config.needs_expensive:
        expensive = compute_expensive(data)  # Only when needed
        use(expensive)
```

### Move loop-invariant code outside loops

```python
# BAD: Repeated attribute lookup
for item in items:
    result = self.config.transform_fn(item)  # 2 lookups per iteration

# GOOD: Hoist invariant lookups
transform = self.config.transform_fn
for item in items:
    result = transform(item)
```

### Cache computed results

```python
from functools import lru_cache

# Cache expensive computations
@lru_cache(maxsize=1024)
def expensive_computation(key: str) -> Result:
    # ...
```

---

## 6) Python↔Rust boundary optimization (PyO3)

### Minimize GIL crossings

```rust
// BAD: Acquire/release GIL for each item
fn process_items(py: Python, items: Vec<PyObject>) -> PyResult<Vec<PyObject>> {
    items.iter().map(|item| {
        // Each call acquires GIL internally
        process_one(py, item)
    }).collect()
}

// GOOD: Hold GIL for batch, release for Rust-only work
fn process_items(py: Python, items: Vec<PyObject>) -> PyResult<Vec<PyObject>> {
    // Extract data while holding GIL
    let data: Vec<_> = items.iter().map(|i| extract_data(py, i)).collect::<PyResult<_>>()?;

    // Release GIL for CPU-intensive work
    let results = py.allow_threads(|| {
        data.par_iter().map(|d| rust_process(d)).collect()
    });

    // Re-acquire GIL to build Python objects
    results.iter().map(|r| to_python(py, r)).collect()
}
```

### Batch data across the boundary

```python
# BAD: N PyO3 calls
for item in items:
    rust_process(item)

# GOOD: Single PyO3 call with batch
rust_process_batch(items)
```

### Use zero-copy types

```rust
// Accept bytes without copying
#[pyfunction]
fn process_bytes(data: &[u8]) -> PyResult<Vec<u8>> {
    // data is a view into Python bytes, no copy
    Ok(transform(data))
}

// Use Py<PyBytes> for owned bytes without copying
#[pyfunction]
fn process_bytes_owned(py: Python, data: Py<PyBytes>) -> PyResult<Py<PyBytes>> {
    let bytes = data.as_bytes(py);
    // ...
}
```

---

## 7) Async optimization

### Python async patterns

```python
# BAD: Sequential await
async def fetch_all(urls):
    results = []
    for url in urls:
        results.append(await fetch(url))  # Sequential
    return results

# GOOD: Concurrent await
async def fetch_all(urls):
    return await asyncio.gather(*[fetch(url) for url in urls])

# BETTER: Bounded concurrency
async def fetch_all(urls, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)
    async def fetch_with_limit(url):
        async with semaphore:
            return await fetch(url)
    return await asyncio.gather(*[fetch_with_limit(url) for url in urls])
```

### Rust async patterns

```rust
// BAD: Sequential await
async fn fetch_all(urls: Vec<Url>) -> Vec<Response> {
    let mut results = Vec::new();
    for url in urls {
        results.push(fetch(&url).await);  // Sequential
    }
    results
}

// GOOD: Concurrent with join_all
async fn fetch_all(urls: Vec<Url>) -> Vec<Response> {
    futures::future::join_all(urls.iter().map(fetch)).await
}

// BETTER: Bounded concurrency with buffer_unordered
use futures::stream::{self, StreamExt};

async fn fetch_all(urls: Vec<Url>) -> Vec<Response> {
    stream::iter(urls)
        .map(|url| fetch(url))
        .buffer_unordered(10)  // Max 10 concurrent
        .collect()
        .await
}
```

---

## 8) Reduce logging and stats costs

### Python logging in hot paths

```python
# BAD: Logging overhead even when disabled
for item in items:
    logger.debug(f"Processing {item}")  # String formatting always happens

# GOOD: Check level first
if logger.isEnabledFor(logging.DEBUG):
    for item in items:
        logger.debug(f"Processing {item}")

# BETTER: Remove logging from innermost loops entirely
```

### Rust logging in hot paths

```rust
// BAD: log! macro overhead in hot loop
for item in items {
    log::debug!("Processing {:?}", item);  // Format even if disabled
}

// GOOD: Check level outside loop
if log::log_enabled!(log::Level::Debug) {
    for item in items {
        log::debug!("Processing {:?}", item);
    }
}

// BETTER: Use tracing with static filtering
#[tracing::instrument(skip_all)]
fn process_batch(items: &[Item]) {
    // Span created once, not per item
    for item in items {
        // Hot loop without logging
    }
}
```

---

# Flat-profile playbook

If no single hotspot dominates:

1. Don't discount many small wins (twenty 1% improvements can matter).
2. Look for loops closer to the top of call stacks (flame graphs help).
3. Consider structural refactors (one-shot construction instead of incremental mutation).
4. Replace overly general abstractions with specialized code.
5. Reduce allocations (allocation profiles help).
6. Use hardware counters (cache misses, branch misses) to find invisible costs.
7. **Python-specific:** Look for GIL contention, excessive object creation, slow imports.
8. **Rust-specific:** Look for excessive async overhead, unnecessary clones, poor cache locality.

---

# Quick review checklist

When reviewing a performance-sensitive change, scan for:

## Python

- [ ] Any O(N²) behavior on realistic N?
- [ ] List comprehension where generator would suffice?
- [ ] Missing `__slots__` on frequently instantiated classes?
- [ ] dict/list allocation inside hot loops?
- [ ] Sequential awaits where concurrent would work?
- [ ] Repeated attribute lookups in loops?
- [ ] Logging/debug in innermost loops?
- [ ] Using stdlib json instead of msgspec/orjson?
- [ ] Synchronous I/O in async context?
- [ ] Missing @lru_cache for repeated expensive computations?

## Rust

- [ ] Any O(N²) behavior on realistic N?
- [ ] Missing `with_capacity()` for known-size collections?
- [ ] Unnecessary `.clone()` where borrow would work?
- [ ] String allocation in hot loops (use `&str` or `Cow`)?
- [ ] Box/Arc where stack allocation would work?
- [ ] Excessive async task spawning for small operations?
- [ ] Poor struct field ordering (padding waste)?
- [ ] Missing `#[inline]` on critical small functions?
- [ ] Lock contention in concurrent code?
- [ ] Logging format overhead in hot paths?

## PyO3 boundary

- [ ] Multiple GIL acquisitions where one would suffice?
- [ ] Python object creation in hot Rust loops?
- [ ] Missing `allow_threads()` for CPU-bound Rust work?
- [ ] Copying data across boundary when view would work?
- [ ] Single-item APIs where batch API would reduce crossings?

---

# Examples (inputs → outputs)

## Example A — Python list vs generator

**Input:**

```python
def process_large_file(path):
    lines = open(path).readlines()  # Load entire file
    return [transform(line) for line in lines]  # Another full copy
```

**Agent output:**

- Issue: Two full copies of file contents; O(N) memory for O(N) items.
- Fix: Use generator for streaming:

```python
def process_large_file(path):
    with open(path) as f:
        for line in f:
            yield transform(line)
```

- Expected impact: O(1) memory instead of O(N).
- Tradeoff: Can only iterate once; caller must handle streaming.

## Example B — Rust unnecessary clones

**Input:**

```rust
fn build_response(data: &ResponseData) -> String {
    let name = data.name.clone();
    let id = data.id.clone();
    format!("User {} ({})", name, id)
}
```

**Agent output:**

- Issue: Unnecessary clones; format! can borrow directly.
- Fix:

```rust
fn build_response(data: &ResponseData) -> String {
    format!("User {} ({})", &data.name, &data.id)
}
```

- Expected impact: 2 fewer allocations per call.

## Example C — PyO3 batch optimization

**Input:**

```python
# Python side
for item in items:
    result = rust_validate(item)  # 10K calls
```

**Agent output:**

- Issue: 10K GIL acquisitions/releases (~2-5ms overhead alone).
- Fix: Add batch API:

```rust
#[pyfunction]
fn rust_validate_batch(items: Vec<Item>) -> Vec<bool> {
    items.iter().map(|i| validate(i)).collect()
}
```

```python
results = rust_validate_batch(items)  # 1 call
```

- Expected impact: ~10-50x faster for large batches.
- Tradeoff: Must collect all items first; can't stream results.

---
name: perf-hints
description: "Improve C++ (C++11+) performance using Abseil “Performance Hints” (Jeff Dean & Sanjay Ghemawat): estimation + profiling, API/bulk design, algorithmic wins, cache-friendly memory layout, fewer allocations, fast paths, caching, and compiler-friendly hot loops. Use for performance code reviews, refactors, and profiling-driven optimizations. Keywords: performance, latency, throughput, cache, allocation, memory layout, InlinedVector, string_view, Span, flat_hash_map, pprof, perf."
license: Apache-2.0
compatibility: Skills-compatible coding agents working on modern C++ codebases; Abseil optional.
metadata:
  upstream_url: "https://abseil.io/fast/hints"
  upstream_authors: "Jeff Dean; Sanjay Ghemawat"
  upstream_original_version: "2023-07-27"
  upstream_last_updated: "2025-12-16"
---

# C++ Performance Hints (Jeff Dean & Sanjay Ghemawat style)

This skill packages key ideas from Abseil’s **Performance Hints** document.

Use it to:

- review C++ code for performance risks
- propose high-impact optimizations with **explicit tradeoffs**
- design APIs/data structures that keep future optimizations possible
- write an experiment plan (profile + microbenchmark) to validate changes

## Scope and guardrails

- **Scope:** single-process / single-binary performance (CPU, memory, allocations, cache behavior).
- **Do not:** change externally observable behavior unless the user explicitly agrees.
- **Do not:** introduce undefined behavior, data races, or brittle “clever” micro-opts without evidence.
- **Default philosophy:** choose the faster alternative **when it doesn’t materially harm readability or complexity**; otherwise, measure first.

## When to apply

Use this skill when the task involves any of:

- reducing **latency** or improving **throughput**
- cutting **memory footprint** or **allocation rate**
- improving **cache locality** / reducing cache misses
- designing performant **APIs** (bulk ops, view types, threading model)
- reviewing performance-sensitive C++ changes
- interpreting a **flat profile** and finding next steps

## What to ask for (minimum inputs)

If you don’t have enough information, ask for the smallest set that changes your recommendation quality:

1. **Goal:** latency vs throughput vs memory (and the SLO if any)
2. **Where:** hot path vs init vs test-only (and typical input sizes)
3. **Evidence:** profile / flame graph / perf counters / allocation profile (if available)
4. **Constraints:** correctness constraints, ABI/API constraints, thread-safety requirements

If none exists yet, proceed with _static analysis + “what to measure first”_.

---

# Workflow: how an agent should use these hints

## Step 1 — classify the code

- **Test code:** mostly care about asymptotic complexity and test runtime.
- **Application code:** separate **init/cold** vs **hot path**.
- **Library code:** prefer “safe, low-complexity” performance techniques because you can’t predict callers.

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
| Compress 1K bytes with Snappy     |                1,000 ns |
| Read 4KB from SSD                 |               20,000 ns |
| Round trip within same datacenter |               50,000 ns |
| Read 1MB sequentially from memory |               64,000 ns |
| Read 1MB over 100 Gbps network    |              100,000 ns |
| Read 1MB from SSD                 |     1,000,000 ns (1 ms) |
| Disk seek                         |     5,000,000 ns (5 ms) |
| Read 1MB sequentially from disk   |   10,000,000 ns (10 ms) |
| Send packet CA→Netherlands→CA     | 150,000,000 ns (150 ms) |

### Estimation examples (templates)

**Quicksort a billion 4-byte integers** (very rough):

- Memory transfer: ~30 passes × 4GB ÷ 16GB/s ≈ **7.5s**
- Branch mispredicts: ~15B misses × 5ns ≈ **75s**
- Total: ≈ **82.5s** (dominant cost is mispredicts; cache refinements reduce memory-transfer term)

**Web page with 30 thumbnails from 1MB images:**

- On disk serial: 30 × (5ms seek + 10ms transfer) ≈ **450ms**
- Spread across K disks in parallel: ≈ **450ms / K** → if K≈100 ⇒ ~**15ms** (ignoring variance)
- Single SSD: 30 × (20µs + 1ms) ≈ **30ms**

## Step 3 — measure before paying complexity

When you can, measure to validate impact:

- Start with high-level CPU profiling (**pprof**) and consider **perf** for deeper counter-based analysis.
- Build optimized binaries with useful debug info.
- Prefer a **microbenchmark** when iterating on a specific routine, but treat microbenchmarks carefully (they can mislead).
- Watch for **lock contention**: contention can lower CPU usage and hide the “real” bottleneck.

## Step 4 — pick the biggest lever first

Prioritize in this order unless evidence suggests otherwise:

1. **Algorithmic complexity** wins (O(N²) → O(N log N) or O(N))
2. **Data structure choice / memory layout** (cache locality; fewer cache lines)
3. **Allocation reduction** (fewer allocs, better reuse)
4. **Avoid unnecessary work** (fast paths, precompute, defer)
5. **Compiler friendliness** (simplify hot loops, reduce abstraction overhead)

## Step 5 — produce an LLM-friendly output

When you respond to the user, use this structure:

1. **Hot path hypothesis** (what you think dominates, and why)
2. **Top issues** (ranked): _issue → evidence/estimate → proposed fix → expected impact_
3. **Patch sketch** (minimal code changes or pseudocode)
4. **Tradeoffs & risks** (correctness, memory, ABI, complexity)
5. **Measurement plan** (what to profile/benchmark and success criteria)

---

# Techniques and patterns

## 1) API design for performance

### Use bulk APIs to amortize overhead

**When:** callers do N similar operations (lookups, deletes, updates, decoding, locking).

**Why:** reduce boundary crossings and repeated fixed costs (locks, dispatch, decoding, syscalls).

**Patterns:**

- Prefer `DeleteRefs(Span<const Ref> refs)` over `DeleteRef(Ref)` in a loop if it lets you lock once.
- Provide bulk “build” APIs (e.g., Floyd heap construction is **O(N)** vs inserting N items one-at-a-time **O(N log N)**).

**Pragmatic migration:** if you can’t change callers quickly, use the bulk API internally and **cache** results for future non-bulk calls.

### Prefer view types for function arguments

**When:** you don’t need ownership transfer.

**Use:**

- `std::string_view` / `absl::string_view` instead of `const std::string&` when you can accept any string-backed buffer.
- `absl::Span<T>` or `std::span<T>` for contiguous sequences.
- `absl::FunctionRef<R(Args...)>` for callbacks when you don’t need ownership.

**Why:** reduces copies and lets callers use efficient containers (including inlined/chunked types).

### Accept pre-allocated / pre-computed arguments

**When:** a low-level routine is called frequently and it would otherwise allocate temporaries or recompute something the caller already has.

**Pattern:** add overloads that accept caller-owned scratch buffers or already-known timestamps/values.

### Thread-compatible vs thread-safe types

- Default many generally-used types to **thread-compatible** (externally synchronized) so single-threaded or already-synchronized callers don’t pay for internal locking.
- If typical usage _requires_ synchronization, internalize it so you can later optimize the mechanism (e.g., sharding to reduce contention) without changing callers.

---

## 2) Algorithmic improvements

The rare-but-massive wins.

### Reduce complexity class

Common transformations:

- O(N²) → O(N log N) or O(N)
- O(N log N) sorted-list intersection → O(N) using a hash set
- O(log N) interval-map lookup → O(1) using hash lookup (if adjacency/coalescing can still be supported)

### Patterns to look for (code review heuristics)

- nested loops over large N (especially over “all pairs”)
- repeated sorting/intersection where hashing would do
- maps/trees used for “lookup by key” when ordering is unused
- hash tables with poor hash functions (accidental O(N))

### Concrete examples from the source document

- **Graph initialization / cycle detection:** instead of adding nodes/edges one-by-one to a cycle detector (expensive per edge), add the entire graph in **reverse post-order** so cycle detection becomes trivial.
- **Deadlock detection:** replacing a deadlock detection algorithm with a dynamic topological sort approach yields ~**50×** speedup and scales to very large graphs. In a DEBUG benchmark at the old 2K-node limit, the new algorithm is about **0.5µs per InsertEdge** vs **22µs** previously.
- **IntervalMap → hash table:** if coalescing adjacent blocks can be done via hash lookups, replace O(log N) lookup structures with O(1) hash lookups; the example mentions an allocator improving by ~**4×** (along with other changes).
- **Sorted intersection → hash lookups:** build a hash set for one list and probe with the other; an example compilation benchmark improved from ~**28.5s** to ~**22.4s**.
- **Good hashing matters:** invest in a hash function that avoids collisions and keeps expected operations O(1).

---

## 3) Better memory representation and cache locality

Memory layout often dominates when working sets are large.

### Compact data structures

- Prefer compact representations for frequently accessed data or data comprising a large fraction of memory.
- Watch for **cache-line contention** when multiple threads write to nearby memory.

### Memory layout checklist

For a frequently used struct/class:

1. Reorder fields to reduce padding.
2. Use smaller numeric types when safe.
3. Use sized enums when appropriate: `enum class OpType : uint8_t { ... }`.
4. Group fields commonly accessed together.
5. Separate **hot mutable** fields from **hot read-only** fields to avoid eviction.
6. Move cold data to the end or behind indirection.
7. Consider bit/byte packing only inside well-tested modules and validate with benchmarks.

### Indices instead of pointers

If you have pointer-heavy structures:

- consider using 32-bit indices into a contiguous `T[]` storage
- benefits: smaller references + better locality + fewer cache lines

### Batched / flat storage

Avoid “one allocation per element” structures:

- prefer `std::vector` and flat/chunked hash sets/maps over `std::map` / `std::unordered_map` when possible
- chunking can preserve asymptotics while improving cache footprint

### Inlined storage

When containers are _usually small_ and frequently constructed:

- use `absl::InlinedVector<T, N>` (or similar small-buffer-optimized containers)
- caveat: avoid if `sizeof(T)` is large (inlined backing store becomes too big)

### Maps: when to flatten vs when to nest

There are two opposite-but-related patterns:

1. **Avoid unnecessarily nested maps** by using a compound key (fewer allocations, better cache footprint):

- `btree_map<A, btree_map<B, C>>` → `btree_map<pair<A,B>, C>`

2. **Introduce hierarchy / nesting** when a large first-level key is repeated across many entries:

- if a string “path” appears in ~1000 keys on average, a two-level map can reduce repeated string storage by ~1000× and improve locality
- an example reports a **76%** microbenchmark improvement from splitting a single-level map into a two-level structure

### Arenas

Arenas reduce allocation overhead and can pack related objects together:

- fewer cache lines touched
- less destruction overhead
- often a big win for complex object graphs

Caveat: don’t put many short-lived objects into long-lived arenas (memory bloat).

### Arrays instead of maps

If the key domain is a small integer range or enum (or the map is tiny):

- replace maps with arrays/vectors
- e.g., payload type → clock rate as `int map[128]`

### Bit vectors / bit matrices instead of sets

If the key domain is representable as small integers:

- replace sets with a bit vector (e.g., `InlinedBitVector<256>`)
- use bitwise ops for union/intersection
- for reachability/transitive relationships, consider a bit matrix after assigning dense IDs

One example replacing a set with a bit-vector reports ~**26–32%** improvement across various benchmark sizes.

---

## 4) Reduce allocations (and allocator overhead)

Allocations cost time in the allocator, touch new cache lines, and incur init/destruction overhead.

### Avoid unnecessary allocations

Common patterns:

- use statically allocated buffers when size is usually bounded (e.g., static “zero buffers” up to a typical max)
- prefer stack allocation when lifetime is bounded by scope (watch stack size)
- avoid `shared_ptr` when ownership is clear
- for “empty” shared objects, consider reusing a static empty instance

### Resize or reserve containers

When you know the expected max size:

- use `reserve()` before repeated `push_back()` / `emplace_back()`
- or `resize()` and fill via pointer/index if that avoids repeated growth checks

Caveats:

- don’t grow one element at a time via repeated `reserve/resize` (can go quadratic)
- if construction is expensive, prefer `reserve` + `push_back` over `resize` (avoids double construction)

### Avoid copying when possible

- prefer move (`std::move`) for large structures
- store pointers/indices in transient structures instead of copying large objects
- sort indices instead of sorting large objects when movement/copies are expensive
- prefer `std::sort` over `std::stable_sort` unless stability is required

Example: avoiding an extra copy when receiving ~400KB tensors via gRPC improved a benchmark by ~**10–15%**.

### Reuse temporary objects

Hoist loop-local allocations outside the loop:

- reuse `std::string` via `clear()`
- reuse protobuf objects via `Clear()`
- reuse serialization buffers by passing a caller-owned scratch string

Caveat: many containers grow to their max-ever size; periodically reconstruct after N uses if peak sizes are rare.

---

## 5) Avoid unnecessary work

Often the biggest category of wins after “big-O”.

### Fast paths for common cases

Structure code so the common case stays in the I-cache and does minimal branching:

- extend fast ASCII scanning in UTF-8 parsing to handle trailing bytes
- fast path 1-byte varints; tail-call slow path for multi-byte
- skip error tracking loops when no errors occurred
- simplify InlinedVector resize paths (separate destroy vs in-place grow vs overflow)
- specialize common tensor initialization shapes (1D–4D)

### Precompute expensive information

Patterns:

- precompute boolean flags or bitfields instead of recomputing predicates
- build small lookup tables (e.g., 256-entry byte tables)
- compute stats on demand instead of updating eagerly on hot operations

A simple example: reducing a preallocated pool size from **200** nodes to **10** cut a web server’s CPU usage by **7.5%**.

### Move expensive computations outside loops

- hoist bounds checks, shape/dimension lookups, invariant pointer fetches

### Defer expensive computations until needed

- check cheap conditions first
- avoid computing expensive values for branches/operands that are rarely taken

Example: deferring an expensive `GetSubSharding` call until needed reduced CPU time from **43s** to **2s** in a workload.

### Search order matters

If searching two tiers and the second is a subset of the first:

- it can be cheaper to search the _larger_ tier first if success allows skipping the smaller tier

An example reports **19%** throughput improvement from changing the search order.

### Specialize hot code paths

- custom formatting/logging instead of general formatting
- prefix matching instead of regex
- `StrCat`-style composition for known formats (e.g., IP addresses)
- specialize logging levels (e.g., VLOG constants) to enable constant propagation

### Cache to avoid repeated work

- cache results keyed by a precomputed fingerprint
- decode blocks once and cache decoded entries

---

## 6) Make the compiler’s job easier (hot loops)

Only do this in truly hot code.

Techniques:

1. Avoid function calls in the hottest loops when they force frame setup.
2. Move slow paths into separate tail-called functions.
3. Copy small data into locals to improve alias analysis and auto-vectorization.
4. Hand-unroll very hot loops (e.g., CRC processing 16 bytes at a time).
5. Replace span/view abstractions with raw pointers _inside the innermost loop_ when needed.
6. In rare hot paths, replace `ABSL_LOG(FATAL)` with `ABSL_DCHECK(false)` to avoid frame setup costs.

---

## 7) Reduce stats and logging costs

Stats and logging can be surprisingly expensive in hot paths — even when "disabled."

### Stats collection

- drop stats that aren't used
- prefer sampling over per-event accounting
- use power-of-two sampling with bitwise AND (`x & 31`) rather than modulus

One example reduces alarm-setting time from **771 ns** to **271 ns** as part of a broader stats-related cleanup.

### Logging in hot paths

Even disabled logging has cost:

- `VLOG(n)` requires at least a **load + compare** on every call, even when the level is not enabled
- the presence of logging code can inhibit compiler optimizations (larger stack frames, blocked inlining)
- formatting arguments may be evaluated even if the log is ultimately suppressed

**Mitigations:**

- **Remove logging entirely** from innermost hot loops when possible
- **Precompute** `VLOG_IS_ON(n)` **outside** the loop and pass as a parameter to helper functions
- Avoid building log message strings in hot paths; if you must log, gate the entire block:
  ```cpp
  if (VLOG_IS_ON(2)) {
    VLOG(2) << ExpensiveDebugString();
  }
  ```

---

## 8) Code size considerations

Large generated code increases compile/link time, icache pressure, and memory footprint.

### Why it matters

- more icache misses in hot paths
- slower builds and larger binaries
- can push hot code out of L1 instruction cache

### Techniques

- **Small inline fast path + `NOINLINE` slow path:** keep the common case tiny; move complex/rare handling to a separate function marked `ABSL_ATTRIBUTE_NOINLINE` or `[[gnu::noinline]]`.
- **Specialize for compile-time constants:** e.g., VLOG levels 0–5 can have dedicated `SlowIsEnabled0()` … `SlowIsEnabled5()` functions, avoiding an extra integer parameter at each call site.
- **Avoid heavy template instantiation** in headers included by many translation units.
- **Watch macro expansion:** logging and assertion macros can silently bloat code.

---

# Flat-profile playbook

If no single hotspot dominates:

1. Don’t discount many small wins (twenty 1% improvements can matter).
2. Look for loops closer to the top of call stacks (flame graphs help).
3. Consider structural refactors (one-shot construction instead of incremental mutation).
4. Replace overly general abstractions with specialized code.
5. Reduce allocations (allocation profiles help).
6. Use hardware counters (cache misses, branch misses) to find invisible costs.

---

# Examples (inputs → outputs)

These are intentionally small; in real work, pair them with a profile or a microbenchmark.

## Example A — avoid repeated vector growth

**Input (common anti-pattern):**

```cpp
std::vector<Widget> out;
for (const auto& x : xs) {
  out.push_back(MakeWidget(x));
}
```

**Agent output (sketch):**

- Issue: repeated growth checks and reallocations possible.
- Fix: `out.reserve(xs.size())` if `xs.size()` is known/cheap; or `out.resize(n)` + fill by index/pointer if it simplifies hot code.
- Expected impact: fewer reallocations, fewer copies/moves, better cache behavior.
- Measurement: microbench the loop for realistic `xs` sizes; also check allocation profile.

## Example B — “nested map” choice depends on key duplication

**Input:** a single-level hash map keyed by `(path_string, subkey_int)` where each `path_string` repeats many times.

**Agent output (sketch):**

- Hypothesis: the repeated `path_string` dominates memory and cache footprint.
- Fix: split into `map<path_string, map<subkey_int, Value>>` so the path is stored once per path.
- Why: reduces repeated storage and can improve locality when accessing many subkeys for the same path.
- Caveat: if the first-level key is huge and rarely repeats, the added indirection may not help.

## Example C — defer expensive computation

**Input:** compute an expensive value for every loop iteration, but only a small subset uses it.

**Agent output (sketch):**

- Fix: restructure to check the cheap condition first, then compute the expensive value only on the matching path.
- Expected impact: proportional to the fraction of iterations that skip the expensive work.
- Measurement: add a microbenchmark or count how often the condition is true in production.

---

# Quick review checklist

When reviewing a performance-sensitive change, scan for:

- [ ] Any O(N²) behavior on realistic N?
- [ ] Repeated sorting/intersection where hashing would do?
- [ ] Hash tables with weak hash functions or pathological keys?
- [ ] Per-element allocations (`new` inside loops, per-node maps/sets)?
- [ ] Missing `reserve()` / avoidable `resize()` patterns?
- [ ] Unnecessary copying of large objects (missing `std::move`, passing by value)?
- [ ] “Cold” data living next to “hot” data in structs?
- [ ] Pointer-heavy graphs that could be index-based arrays?
- [ ] Unnecessary locking or lock contention (thread-safe when thread-compatible would do)?
- [ ] Logging/stats in the hottest loops? (even disabled `VLOG` has load+compare cost)
- [ ] Missing fast paths for common cases?
- [ ] Repeated expensive computation that could be cached, hoisted, or deferred?

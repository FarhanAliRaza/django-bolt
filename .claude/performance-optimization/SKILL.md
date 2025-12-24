---
name: performance-optimization
description: Apply systematic performance optimization techniques when writing or reviewing code. Use when optimizing hot paths, reducing latency, improving throughput, fixing performance regressions, or when the user mentions performance, optimization, speed, latency, throughput, profiling, or benchmarking.
---

# Performance Optimization Skill

Apply these principles when optimizing code for performance. Focus on the critical 3% where performance truly matters - a 12% improvement is never marginal in engineering.

## Core Philosophy

1. **Measure First**: Never optimize without profiling data
2. **Estimate Costs**: Back-of-envelope calculations before implementation
3. **Avoid Work**: The fastest code is code that doesn't run
4. **Reduce Allocations**: Memory allocation is often the hidden bottleneck
5. **Cache Locality**: Memory access patterns dominate modern performance

## Reference Latency Numbers

Use these for back-of-envelope calculations:

| Operation | Latency |
|-----------|---------|
| L1 cache reference | 0.5 ns |
| Branch mispredict | 5 ns |
| L2 cache reference | 7 ns |
| Mutex lock/unlock | 25 ns |
| Main memory reference | 100 ns |
| Compress 1KB (Snappy) | 3 us |
| SSD random read (4KB) | 20 us |
| Round trip in datacenter | 50 us |
| Disk seek | 5 ms |

## Optimization Techniques (Priority Order)

### 1. Algorithmic Improvements (Highest Impact)

**Always check algorithm complexity first:**

```
O(N^2) → O(N log N)  = 1000x faster for N=1M
O(N)   → O(1)        = unbounded improvement
```

**Common patterns:**
- Replace nested loops with hash lookups
- Use sorted-list intersection → hash table lookups
- Process in reverse post-order to eliminate per-element checks
- Replace interval trees (O(log N)) with hash maps (O(1)) when ranges aren't needed

### 2. Reduce Memory Allocations

**Allocation is expensive (~25-100ns + GC pressure)**

```python
# BAD: Allocates on every call
def process(items):
    result = []  # New allocation
    for item in items:
        result.append(transform(item))
    return result

# GOOD: Pre-allocate or reuse
def process(items, out=None):
    if out is None:
        out = [None] * len(items)
    for i, item in enumerate(items):
        out[i] = transform(item)
    return out
```

**Techniques:**
- Pre-size containers with `reserve()` or known capacity
- Hoist temporary containers outside loops
- Reuse buffers across iterations (clear instead of recreate)
- Move instead of copy large structures
- Use stack allocation for bounded-lifetime objects

### 3. Compact Data Structures

**Minimize memory footprint and cache lines touched:**

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
```

**Techniques:**
- Reorder struct fields by size (largest first)
- Use smaller numeric types when range permits (u8 vs i32)
- Replace 64-bit pointers with 32-bit indices
- Keep hot fields together, move cold fields to separate struct
- Use bit vectors for small-domain sets
- Flatten nested maps: `Map<A, Map<B, C>>` → `Map<(A,B), C>`

### 4. Fast Paths for Common Cases

**Optimize the common case without hurting rare cases:**

```python
# BAD: Always takes slow path
def parse_varint(data):
    return generic_varint_parser(data)

# GOOD: Fast path for common 1-byte case
def parse_varint(data):
    if data[0] < 128:  # Single byte - 90% of cases
        return data[0], 1
    return generic_varint_parser(data)  # Rare multi-byte
```

**Techniques:**
- Handle common dimensions inline (1-D, 2-D tensors)
- Check for empty/trivial inputs early
- Specialize for common sizes (small strings, few elements)
- Process trailing elements separately to avoid slow generic code

### 5. Precompute Expensive Information

**Trade memory for compute when beneficial:**

```python
# BAD: Recomputes on every access
def is_vowel(char):
    return char.lower() in 'aeiou'

# GOOD: Lookup table
VOWEL_TABLE = [c.lower() in 'aeiou' for c in (chr(i) for i in range(256))]
def is_vowel(char):
    return VOWEL_TABLE[ord(char)]
```

**Techniques:**
- Precompute flags/properties at construction time
- Build lookup tables for character classification
- Cache expensive computed properties
- Validate at boundaries once, not repeatedly inside

### 6. Bulk/Batch APIs

**Amortize fixed costs across multiple operations:**

```python
# BAD: N round trips
for item in items:
    result = db.lookup(item)

# GOOD: 1 round trip
results = db.lookup_many(items)
```

**Design APIs that support:**
- Batch lookups instead of individual fetches
- Vectorized operations over loops
- Streaming interfaces for large datasets

### 7. Avoid Unnecessary Work

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

**Techniques:**
- Lazy evaluation for expensive operations
- Short-circuit evaluation in conditions
- Move loop-invariant code outside loops
- Specialize instead of using general-purpose libraries in hot paths

### 8. Help the Compiler/Runtime

**Lower-level optimizations when profiling shows need:**

```rust
// Avoid function call overhead in hot loops
#[inline(always)]
fn hot_function(x: i32) -> i32 { x * 2 }

// Copy to local variable for better alias analysis
fn process(data: &mut [i32], factor: &i32) {
    let f = *factor;  // Compiler knows this won't change
    for x in data {
        *x *= f;
    }
}
```

**Techniques:**
- Use raw pointers/indices instead of iterators in critical loops
- Hand-unroll very hot loops (4+ iterations)
- Move slow-path code to separate non-inlined functions
- Avoid abstractions that hide costs in hot paths

### 9. Reduce Synchronization

**Minimize lock contention and atomic operations:**

- Default to thread-compatible (external sync) not thread-safe
- Sample statistics (1-in-32) instead of tracking everything
- Batch updates to shared state
- Use thread-local storage for per-thread data

## Profiling Workflow

1. **Identify hotspots**: Use profiler (pprof, perf, py-spy)
2. **Measure baseline**: Write benchmark before optimizing
3. **Estimate improvement**: Calculate expected gain
4. **Implement change**: Focus on one optimization at a time
5. **Verify improvement**: Run benchmark, confirm gain
6. **Check for regressions**: Ensure no other code paths slowed down

## When Profile is Flat (No Clear Hotspots)

- Pursue multiple small 1-2% improvements collectively
- Look for restructuring opportunities higher in call stack
- Profile allocations specifically (often hidden cost)
- Gather hardware performance counters (cache misses, branch mispredicts)
- Consider if the code is already well-optimized

## Anti-Patterns to Avoid

1. **Premature optimization** in non-critical code
2. **Optimizing without measurement** - changes based on intuition
3. **Micro-optimizing** while ignoring algorithmic complexity
4. **Copying** when moving would suffice
5. **Growing containers** one element at a time (quadratic)
6. **Allocating in loops** when reuse is possible
7. **String formatting** in hot paths (use pre-built templates)
8. **Regex** when simple string matching suffices

## Estimation Template

Before optimizing, estimate:

```
Operation cost: ___ ns/us/ms
Frequency: ___ times per second/request
Total time: cost × frequency = ___
Improvement target: ___% reduction
Expected new time: ___
Is this worth it? [ ] Yes [ ] No
```

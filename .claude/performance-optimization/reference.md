# Performance Optimization Reference

Detailed examples and patterns for each optimization technique.

## Memory Allocation Patterns

### Python: Avoid Repeated Allocations

```python
# BAD: Creates new list every iteration
def process_batches(batches):
    for batch in batches:
        results = []  # Allocated every iteration
        for item in batch:
            results.append(transform(item))
        yield results

# GOOD: Reuse list
def process_batches(batches):
    results = []  # Allocated once
    for batch in batches:
        results.clear()  # Reuse existing allocation
        for item in batch:
            results.append(transform(item))
        yield results.copy()  # Copy only when needed
```

### Rust: Pre-allocate Vectors

```rust
// BAD: Grows vector repeatedly
fn collect_items(source: &[Data]) -> Vec<Output> {
    let mut result = Vec::new();  // Starts empty
    for item in source {
        result.push(process(item));  // May reallocate
    }
    result
}

// GOOD: Pre-allocate
fn collect_items(source: &[Data]) -> Vec<Output> {
    let mut result = Vec::with_capacity(source.len());
    for item in source {
        result.push(process(item));  // No reallocation
    }
    result
}
```

### JavaScript/TypeScript: Object Pooling

```typescript
// BAD: Creates new objects in hot path
function processEvents(events: Event[]) {
    return events.map(e => ({
        id: e.id,
        timestamp: new Date(),
        data: transform(e.data)
    }));
}

// GOOD: Reuse object pool
const resultPool: Result[] = [];
function processEvents(events: Event[]) {
    // Ensure pool has enough objects
    while (resultPool.length < events.length) {
        resultPool.push({ id: 0, timestamp: null, data: null });
    }

    for (let i = 0; i < events.length; i++) {
        const r = resultPool[i];
        r.id = events[i].id;
        r.timestamp = Date.now();
        r.data = transform(events[i].data);
    }
    return resultPool.slice(0, events.length);
}
```

## Data Structure Optimization

### Struct Field Reordering

```rust
// Calculate struct size with padding
// Rule: Fields are aligned to their size

// BAD: 32 bytes (with padding)
struct BadLayout {
    a: bool,      // 1 byte
    // 7 bytes padding (b needs 8-byte alignment)
    b: u64,       // 8 bytes
    c: u32,       // 4 bytes
    // 4 bytes padding (struct aligns to largest member)
    d: bool,      // 1 byte
    // 7 bytes padding
    e: u64,       // 8 bytes
}

// GOOD: 24 bytes (minimal padding)
struct GoodLayout {
    b: u64,       // 8 bytes
    e: u64,       // 8 bytes
    c: u32,       // 4 bytes
    a: bool,      // 1 byte
    d: bool,      // 1 byte
    // 2 bytes padding
}
```

### Index vs Pointer

```rust
// BAD: 64-bit pointers everywhere
struct Node {
    value: i32,
    left: Option<Box<Node>>,   // 8 bytes
    right: Option<Box<Node>>,  // 8 bytes
}

// GOOD: 32-bit indices into arena
struct NodeArena {
    nodes: Vec<NodeData>,
}

struct NodeData {
    value: i32,
    left: u32,   // Index, u32::MAX = none
    right: u32,  // 4 bytes instead of 8
}
```

### Flatten Nested Maps

```python
# BAD: Nested dict (2 hash lookups, 2 allocations per entry)
user_permissions = {
    user_id: {
        resource_id: permission_level
    }
}
perm = user_permissions.get(uid, {}).get(rid)

# GOOD: Flat dict with tuple key (1 lookup, 1 allocation per entry)
user_permissions = {
    (user_id, resource_id): permission_level
}
perm = user_permissions.get((uid, rid))
```

## Fast Path Patterns

### Early Exit for Common Cases

```python
# BAD: Always executes full logic
def validate_email(email: str) -> bool:
    # Complex regex validation
    return bool(EMAIL_REGEX.match(email))

# GOOD: Fast reject common invalid cases
def validate_email(email: str) -> bool:
    # Quick checks first (no regex)
    if not email or len(email) > 254:
        return False
    if '@' not in email:
        return False
    if email.count('@') != 1:
        return False

    # Only run expensive regex if basic checks pass
    return bool(EMAIL_REGEX.match(email))
```

### Specialized Small Cases

```rust
// BAD: Always use generic implementation
fn sum(values: &[i32]) -> i32 {
    values.iter().sum()
}

// GOOD: Specialize common small sizes
fn sum(values: &[i32]) -> i32 {
    match values.len() {
        0 => 0,
        1 => values[0],
        2 => values[0] + values[1],
        3 => values[0] + values[1] + values[2],
        _ => values.iter().sum(),
    }
}
```

## Avoiding Unnecessary Work

### Lazy Evaluation

```python
# BAD: Always computes all fields
class Report:
    def __init__(self, data):
        self.data = data
        self.summary = self._compute_summary()      # Expensive
        self.statistics = self._compute_stats()     # Expensive
        self.charts = self._render_charts()         # Very expensive

# GOOD: Compute on demand
class Report:
    def __init__(self, data):
        self.data = data
        self._summary = None
        self._statistics = None
        self._charts = None

    @property
    def summary(self):
        if self._summary is None:
            self._summary = self._compute_summary()
        return self._summary
```

### Loop-Invariant Code Motion

```python
# BAD: Recomputes inside loop
def process_items(items, config):
    for item in items:
        threshold = compute_threshold(config)  # Same every iteration!
        if item.value > threshold:
            handle(item)

# GOOD: Hoist outside loop
def process_items(items, config):
    threshold = compute_threshold(config)  # Computed once
    for item in items:
        if item.value > threshold:
            handle(item)
```

## Batch Operations

### Database Queries

```python
# BAD: N+1 query pattern
def get_order_details(order_ids):
    results = []
    for oid in order_ids:
        order = db.query(Order).get(oid)        # 1 query
        items = db.query(OrderItem).filter(order_id=oid).all()  # N queries
        results.append((order, items))
    return results

# GOOD: Batch fetch
def get_order_details(order_ids):
    orders = db.query(Order).filter(Order.id.in_(order_ids)).all()
    items = db.query(OrderItem).filter(OrderItem.order_id.in_(order_ids)).all()

    items_by_order = defaultdict(list)
    for item in items:
        items_by_order[item.order_id].append(item)

    return [(order, items_by_order[order.id]) for order in orders]
```

### API Bulk Endpoints

```python
# BAD: Individual operations
class ItemAPI:
    def get(self, id: int) -> Item: ...
    def update(self, id: int, data: dict) -> Item: ...

# GOOD: Bulk operations
class ItemAPI:
    def get(self, id: int) -> Item: ...
    def get_many(self, ids: list[int]) -> list[Item]: ...  # Batch fetch
    def update(self, id: int, data: dict) -> Item: ...
    def update_many(self, updates: list[tuple[int, dict]]) -> list[Item]: ...
```

## String Optimization

### Avoid String Formatting in Hot Paths

```python
# BAD: String formatting every call
def log_request(method, path, status):
    logger.info(f"Request: {method} {path} -> {status}")

# GOOD: Pre-build format, check log level
def log_request(method, path, status):
    if logger.isEnabledFor(logging.INFO):
        logger.info("Request: %s %s -> %s", method, path, status)
```

### StringBuilder Pattern

```python
# BAD: String concatenation in loop (O(n^2))
def build_html(items):
    html = ""
    for item in items:
        html += f"<li>{item}</li>"
    return f"<ul>{html}</ul>"

# GOOD: List join (O(n))
def build_html(items):
    parts = [f"<li>{item}</li>" for item in items]
    return f"<ul>{''.join(parts)}</ul>"
```

## Cache Patterns

### LRU Cache for Expensive Computations

```python
from functools import lru_cache

# Automatic caching with LRU eviction
@lru_cache(maxsize=1024)
def expensive_computation(key: str) -> Result:
    return compute(key)
```

### Manual Cache with TTL

```python
import time

class TTLCache:
    def __init__(self, ttl_seconds: float):
        self.ttl = ttl_seconds
        self.cache = {}
        self.timestamps = {}

    def get(self, key):
        if key in self.cache:
            if time.time() - self.timestamps[key] < self.ttl:
                return self.cache[key]
            del self.cache[key]
            del self.timestamps[key]
        return None

    def set(self, key, value):
        self.cache[key] = value
        self.timestamps[key] = time.time()
```

## Profiling Commands

### Python

```bash
# CPU profiling
python -m cProfile -o output.prof script.py
python -m pstats output.prof

# Line profiling
pip install line_profiler
kernprof -l -v script.py

# Memory profiling
pip install memory_profiler
python -m memory_profiler script.py

# Live profiling
pip install py-spy
py-spy top --pid <PID>
py-spy record -o profile.svg --pid <PID>
```

### Rust

```bash
# CPU profiling with perf
perf record --call-graph dwarf ./target/release/binary
perf report

# Flamegraph
cargo install flamegraph
cargo flamegraph --release

# Memory profiling
cargo install heaptrack
heaptrack ./target/release/binary
```

### General

```bash
# Linux perf counters
perf stat -e cache-misses,cache-references,instructions,cycles ./binary

# Valgrind cachegrind
valgrind --tool=cachegrind ./binary
```

## Benchmarking Best Practices

1. **Warm up**: Run several iterations before measuring
2. **Multiple runs**: Report median, not mean (avoid outliers)
3. **Isolate**: Minimize system interference (disable turbo, pin CPU)
4. **Realistic data**: Use production-like data sizes
5. **Compare fairly**: Same hardware, same conditions
6. **Track over time**: Prevent regressions with CI benchmarks

```python
# Python benchmark template
import time
import statistics

def benchmark(func, args, iterations=100, warmup=10):
    # Warmup
    for _ in range(warmup):
        func(*args)

    # Measure
    times = []
    for _ in range(iterations):
        start = time.perf_counter_ns()
        func(*args)
        elapsed = time.perf_counter_ns() - start
        times.append(elapsed)

    return {
        'median_ns': statistics.median(times),
        'mean_ns': statistics.mean(times),
        'stdev_ns': statistics.stdev(times),
        'min_ns': min(times),
        'max_ns': max(times),
    }
```

# Serializer Benchmark Results - AFTER OPTIMIZATION

## django-bolt (msgspec) vs Pydantic v2

**Test Date:** 2025-11-16
**Iterations:** 100,000 per test (10,000 for error detection)
**Status:** ✅ **OPTIMIZED** - Caching type metadata at class definition time

---

## 🎉 Performance Breakthrough: 89-100x Speedup

### Before Optimization
- Dict → Object: **10,937 ops/sec** (118x slower than Pydantic)
- JSON → Object: **10,836 ops/sec** (97x slower than Pydantic)

### After Optimization
- Dict → Object: **973,131 ops/sec** (only 1.28x slower than Pydantic)
- JSON → Object: **1,085,577 ops/sec** (1.03x FASTER than Pydantic) ⚡

**Result:** We are now **competitive with Pydantic** at deserialization while maintaining our 3-6x serialization advantage!

---

## Results Summary

### 🏆 django-bolt Wins

| Operation | Performance | Winner |
|-----------|-------------|--------|
| **JSON Deserialization** | **1.03x faster** | django-bolt: 1.09M ops/sec vs Pydantic: 1.05M ops/sec ✅ |
| **Dict Serialization** | **3.28x faster** | django-bolt: 4.3M ops/sec vs Pydantic: 1.3M ops/sec |
| **JSON Serialization** | **6.02x faster** | django-bolt: 6.9M ops/sec vs Pydantic: 1.1M ops/sec |
| **Error Detection** | **1.64x faster** | django-bolt: 1.6M ops/sec vs Pydantic: 959K ops/sec |

### 🏆 Pydantic v2 Wins (Minor Edge)

| Operation | Performance | Winner |
|-----------|-------------|--------|
| **Dict Deserialization** | **1.28x faster** | Pydantic: 1.25M ops/sec vs django-bolt: 973K ops/sec |
| **Dict Deserialization (with validators)** | **1.42x faster** | Pydantic: 1.08M ops/sec vs django-bolt: 761K ops/sec |
| **JSON Deserialization (with validators)** | **1.21x faster** | Pydantic: 928K ops/sec vs django-bolt: 766K ops/sec |

---

## Detailed Results

### Scenario 1: Basic Meta Validation (No Custom Validators)

```
Dict → Object Deserialization
  django-bolt: 0.1028s  (973,131 ops/sec)
  Pydantic v2: 0.0800s  (1,250,342 ops/sec)
  Winner: Pydantic v2 (1.28x faster)

JSON → Object Deserialization
  django-bolt: 0.0921s  (1,085,577 ops/sec)
  Pydantic v2: 0.0948s  (1,054,640 ops/sec)
  Winner: django-bolt (1.03x faster) ✅

Object → Dict Serialization
  django-bolt: 0.0233s  (4,293,887 ops/sec)
  Pydantic v2: 0.0765s  (1,307,373 ops/sec)
  Winner: django-bolt (3.28x faster) ✅

Object → JSON Serialization
  django-bolt: 0.0146s  (6,872,159 ops/sec)
  Pydantic v2: 0.0875s  (1,142,420 ops/sec)
  Winner: django-bolt (6.02x faster) ✅
```

### Scenario 2: With Custom Field Validators

```
Dict → Object Deserialization (with validators)
  django-bolt: 0.1314s  (761,056 ops/sec)
  Pydantic v2: 0.0928s  (1,077,046 ops/sec)
  Winner: Pydantic v2 (1.42x faster)

JSON → Object Deserialization (with validators)
  django-bolt: 0.1305s  (766,140 ops/sec)
  Pydantic v2: 0.1078s  (927,984 ops/sec)
  Winner: Pydantic v2 (1.21x faster)
```

### Scenario 3: Validation Error Detection

```
Iterations: 10,000
  django-bolt: 0.0063s  (1,576,647 ops/sec)
  Pydantic v2: 0.0104s  (958,923 ops/sec)
  Winner: django-bolt (1.64x faster) ✅
```

---

## What Changed?

### The Problem
The django-bolt `Serializer` wrapper was running **expensive type introspection** on every instance creation:
- Walking up 10 stack frames with `inspect.currentframe()`
- Calling `get_type_hints()` repeatedly
- Processing all fields for nested/Literal checks

This happened in `__post_init__()`, which runs **on every instance**, not just at class definition time.

### The Solution
Moved all expensive introspection to `__init_subclass__()` which runs **once per class**:

```python
@classmethod
def _cache_type_metadata(cls) -> None:
    """Called ONCE at class definition time"""
    hints = get_type_hints(cls, ...)
    cls.__cached_type_hints__ = hints
    cls.__nested_fields__ = {...}
    cls.__literal_fields__ = {...}

def __post_init__(self):
    # Use pre-computed cached data ✅
    for field_name, nested_config in self.__nested_fields__.items():
        # Fast lookup, no introspection!
```

This follows the same pattern as Pydantic v2's metaclass approach.

---

## Analysis

### Why django-bolt is Now Fast

**Before:** Every instance creation walked the stack and resolved type hints
**After:** Type metadata cached once at class definition time
**Result:** 89-100x speedup in deserialization

### Why Pydantic Still Has a Slight Edge (1.28x)

Pydantic v2 uses **pydantic-core** written entirely in Rust:
- JSON parsing in Rust
- Validation logic in Rust
- Field validators compiled to Rust
- Type coercion in Rust

**Zero Python overhead** during instance creation.

### Why django-bolt Beats Pydantic at JSON Deserialization

For JSON → Object without custom validators, django-bolt leverages **msgspec's** ultra-fast JSON decoder:
- Optimized Rust-based JSON parsing
- Direct struct construction
- Minimal allocations

**Result:** 1.03x faster than Pydantic v2

### Why django-bolt Dominates at Serialization

msgspec is specifically optimized for serialization:
- **3.28x faster** at dict serialization
- **6.02x faster** at JSON serialization
- Direct memory access patterns
- Optimized for common data types

---

## Use Case Recommendations

### Choose django-bolt When:

✅ **High-throughput API responses** - You're returning lots of data to clients
✅ **Serialization-heavy workloads** - Most operations are converting objects → JSON
✅ **Performance-critical endpoints** - Every microsecond matters
✅ **Balanced performance** - Need both fast deserialization AND fast serialization

**Best for:** REST APIs, microservices, real-time data APIs, GraphQL servers

### Choose Pydantic v2 When:

✅ **Complex input validation with many custom validators** - Heavy Python validator logic
✅ **Data transformation pipelines** - Converting external data formats
✅ **Deserialization-only workloads** - No need to serialize back to JSON

**Best for:** Data processing, ETL pipelines, webhook handlers (input-only)

---

## Hybrid Approach (Optional)

For maximum performance in specific scenarios:

- **Pydantic v2** for complex input validation with many custom validators (1.42x faster)
- **django-bolt** for everything else (balanced performance + 3-6x faster serialization)

However, **django-bolt is now competitive enough** that this hybrid approach is usually unnecessary.

---

## Benchmark Code

The benchmark code is available in:
- `benchmark_serializer_updated.py` - Full comparison with/without validators
- `benchmark_raw.py` - Raw msgspec vs Pydantic (no wrappers)

Run with:
```bash
uv run python benchmark_serializer_updated.py
```

---

## Conclusion

### The Optimization Achievement

**89-100x speedup** in deserialization performance by moving type introspection from instance-time to class-time.

### Current Status

**django-bolt (msgspec) is now the best choice for most Django REST APIs:**

✅ **Competitive deserialization** (within 1.28x of Pydantic, beats it for JSON)
✅ **Dominant serialization** (3-6x faster than Pydantic)
✅ **Faster error detection** (1.64x faster)
✅ **Lower latency** for API responses
✅ **Better balanced** performance across all operations

**Pydantic v2 retains a slight edge only when:**
- Using many custom field validators (1.21-1.42x faster)
- Validation-only workloads (no serialization needed)

For a typical Django REST API that both receives AND returns data, **django-bolt is the clear winner** with its balanced high performance across all operations.

---

## Technical Details

See [SERIALIZER_PERFORMANCE_FIX.md](SERIALIZER_PERFORMANCE_FIX.md) for implementation details of the optimization.

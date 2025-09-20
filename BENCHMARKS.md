# Django-Bolt Benchmark Results

Generated: September 20, 2025

## Performance Comparison Summary

### Test Configuration

- **Concurrency**: 50 concurrent connections
- **Requests**: 10,000 total requests
- **Machine**: Linux 6.15.9-arch1-1
- **Test**: Simple JSON hello world endpoint

## Framework Results

| Framework       | RPS        | Latency (mean) | Relative Performance          |
| --------------- | ---------- | -------------- | ----------------------------- |
| **Django-Bolt** | **43,240** | **1.2ms**      | **11.3x faster than FastAPI** |
| Robyn           | 11,246     | 4.4ms          | 2.9x faster than FastAPI      |
| FastAPI         | 3,813      | 13.1ms         | Baseline                      |

## Django-Bolt Scaling Analysis

| Configuration           | RPS     | Scaling Factor | Notes                      |
| ----------------------- | ------- | -------------- | -------------------------- |
| 1 process × 1 worker    | ~19,000 | 1x             | Single GIL baseline        |
| 2 processes × 2 workers | ~43,000 | 2.3x           | Multi-process advantage    |
| 4 processes × 1 worker  | ~72,000 | 3.8x           | Maximum tested performance |

## ORM Performance (with Django models)

| Test Type     | RPS    | Latency | Notes                |
| ------------- | ------ | ------- | -------------------- |
| Hello (no DB) | 43,240 | 1.2ms   | Pure API performance |
| ORM queries   | 2,836  | 17.6ms  | Django ORM + SQLite  |

## Key Insights

### Why Django-Bolt is fastest:

1. **Multi-process architecture**: Each process has isolated Python GIL
2. **Actix-Web core**: Rust HTTP server vs Python async event loops
3. **SO_REUSEPORT**: OS kernel load balancing across processes
4. **Minimal Python overhead**: Single-arg handlers, lazy field access

### Architecture advantage:

- **Processes > Workers**: For Python frameworks, separate processes avoid GIL contention
- **1-2 workers per process**: Optimal for I/O concurrency without GIL thrashing
- **Linear scaling**: Each additional process adds ~19-25k RPS capacity

### Production recommendations:

- **Development**: 2 processes × 2 workers (good balance)
- **Production**: 1 process per CPU core × 1-2 workers
- **High load**: Scale horizontally with more instances

## Historical Performance

### Before optimizations:

- Single process, multiple workers: ~22k RPS (GIL limited)
- Embedded mode: ~26k RPS (minimal Django overhead)

### After optimizations:

- Multi-process: ~43-75k RPS (GIL isolation)
- Django integration: ~43k RPS (full compatibility)

## Conclusion

Django-Bolt achieves **11x better performance than FastAPI** while providing:

- Full Django compatibility (models, admin, migrations)
- Zero-config autodiscovery
- Multi-app support with route prefixes
- Production-ready multi-process scaling

The multi-process + SO_REUSEPORT architecture gives Django-Bolt a massive performance advantage over single-process Python frameworks.

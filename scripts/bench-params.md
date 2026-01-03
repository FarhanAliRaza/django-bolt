just bench-params
P=8 WORKERS=1 C=100 N=10000 HOST=127.0.0.1 PORT=8001 ./scripts/benchmark_params.sh

# Django-Bolt Parameter & Form Benchmark

Generated: Sat Jan 3 06:52:30 PM PKT 2026
Config: 8 processes x 1 workers | C=100 N=10000

## Parameter Extraction Performance

### Baseline - No Parameters (/)

Reqs/sec 102367.37 21346.63 120322.02
Latency 0.97ms 757.36us 9.73ms
Latency Distribution
50% 840.00us
75% 1.14ms
90% 1.46ms
99% 4.67ms

### Path Parameter - int (/items/12345)

Reqs/sec 105508.05 9368.20 114162.92
Latency 0.93ms 307.67us 4.17ms
Latency Distribution
50% 0.86ms
75% 1.16ms
90% 1.48ms
99% 2.19ms

### Path + Query Parameters (/items/12345?q=hello)

Reqs/sec 104176.39 9239.32 110254.43
Latency 0.94ms 295.52us 4.04ms
Latency Distribution
50% 0.87ms
75% 1.15ms
90% 1.46ms
99% 2.29ms

### Typed Params - int/float/bool (/bench/params/typed/1?count=10&price=19.99&active=true)

Reqs/sec 104376.06 10054.48 111572.03
Latency 0.95ms 355.49us 6.11ms
Latency Distribution
50% 0.88ms
75% 1.14ms
90% 1.46ms
99% 2.26ms

### Multi Query - 7 params (/bench/params/multi-query?page=1&limit=20&sort=name&order=desc&filter_active=true&min_price=10.0&max_price=500.0)

Reqs/sec 100101.48 11848.78 109790.08
Latency 0.97ms 354.70us 5.81ms
Latency Distribution
50% 0.89ms
75% 1.16ms
90% 1.46ms
99% 2.52ms

### Header Extraction (/header)

Reqs/sec 110807.05 11476.29 118230.29
Latency 0.89ms 384.15us 5.87ms
Latency Distribution
50% 812.00us
75% 1.07ms
90% 1.38ms
99% 2.30ms

### Cookie Extraction (/cookie)

Reqs/sec 103191.80 7887.88 108495.19
Latency 0.95ms 416.10us 5.89ms
Latency Distribution
50% 0.85ms
75% 1.15ms
90% 1.47ms
99% 3.13ms

## Form Parsing Performance

### URL-Encoded Form - 3 fields (/form)

Reqs/sec 89014.76 7683.88 93723.90
Latency 1.11ms 391.32us 5.89ms
Latency Distribution
50% 1.00ms
75% 1.32ms
90% 1.71ms
99% 2.85ms

### URL-Encoded Form - Typed int/float/bool (/bench/form/typed)

Reqs/sec 93323.99 7824.24 98367.40
Latency 1.05ms 291.10us 4.63ms
Latency Distribution
50% 0.98ms
75% 1.27ms
90% 1.58ms
99% 2.36ms

### URL-Encoded Form - 10 fields (/bench/form/large)

Reqs/sec 79664.30 7447.54 88145.17
Latency 1.25ms 423.21us 4.96ms
Latency Distribution
50% 1.16ms
75% 1.49ms
90% 1.91ms
99% 3.26ms

## Multipart Form Parsing Performance

### Multipart - Single File Upload (/upload)

Reqs/sec 75150.91 6129.60 78954.95
Latency 1.32ms 421.77us 4.39ms
Latency Distribution
50% 1.21ms
75% 1.58ms
90% 2.04ms
99% 3.24ms

### Multipart - Mixed Form + File (/mixed-form)

Reqs/sec 62159.44 5561.69 66884.85
Latency 1.59ms 461.13us 7.30ms
Latency Distribution
50% 1.54ms
75% 1.94ms
90% 2.42ms
99% 3.50ms

### Multipart - Multiple Files (/upload)

Reqs/sec 65691.68 5192.71 69119.79
Latency 1.51ms 494.98us 5.66ms
Latency Distribution
50% 1.41ms
75% 1.84ms
90% 2.33ms
99% 3.74ms

## Summary

Use this benchmark before and after moving form parsing/coercion to Rust.
Key metrics: Reqs/sec (higher=better), p50/p90/p99 latency (lower=better)

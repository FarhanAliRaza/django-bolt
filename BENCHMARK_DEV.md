# Django-Bolt Benchmark
Generated: Fri Nov  7 11:22:58 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    98955.03 [#/sec] (mean)
Time per request:       1.011 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    83702.32 [#/sec] (mean)
Time per request:       1.195 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    83450.16 [#/sec] (mean)
Time per request:       1.198 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    99725.75 [#/sec] (mean)
Time per request:       1.003 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    100876.62 [#/sec] (mean)
Time per request:       0.991 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    99840.26 [#/sec] (mean)
Time per request:       1.002 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    99644.27 [#/sec] (mean)
Time per request:       1.004 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    96303.86 [#/sec] (mean)
Time per request:       1.038 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    23718.72 [#/sec] (mean)
Time per request:       4.216 [ms] (mean)
Time per request:       0.042 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    85316.22 [#/sec] (mean)
Time per request:       1.172 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    81945.05 [#/sec] (mean)
Time per request:       1.220 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    13077.67 [#/sec] (mean)
Time per request:       7.647 [ms] (mean)
Time per request:       0.076 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    12932.73 [#/sec] (mean)
Time per request:       7.732 [ms] (mean)
Time per request:       0.077 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    17690.44 [#/sec] (mean)
Time per request:       5.653 [ms] (mean)
Time per request:       0.057 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    17752.84 [#/sec] (mean)
Time per request:       5.633 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    95330.70 [#/sec] (mean)
Time per request:       1.049 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    84207.69 [#/sec] (mean)
Time per request:       1.188 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    38253.64 [#/sec] (mean)
Time per request:       2.614 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    84354.02 [#/sec] (mean)
Time per request:       1.185 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    71251.46 [#/sec] (mean)
Time per request:       1.403 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    57352.93 [#/sec] (mean)
Time per request:       1.744 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    52415.30 [#/sec] (mean)
Time per request:       1.908 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    17792.33 [#/sec] (mean)
Time per request:       5.620 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    76848.00 [#/sec] (mean)
Time per request:       1.301 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    59557.13 [#/sec] (mean)
Time per request:       1.679 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    41765.69 [#/sec] (mean)
Time per request:       2.394 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    91742.28 [#/sec] (mean)
Time per request:       1.090 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

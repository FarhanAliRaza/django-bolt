# Django-Bolt Benchmark
Generated: Fri Nov  7 09:28:07 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    102442.22 [#/sec] (mean)
Time per request:       0.976 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    85943.88 [#/sec] (mean)
Time per request:       1.164 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    85451.10 [#/sec] (mean)
Time per request:       1.170 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    103166.17 [#/sec] (mean)
Time per request:       0.969 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    103383.75 [#/sec] (mean)
Time per request:       0.967 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    100461.12 [#/sec] (mean)
Time per request:       0.995 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    103619.43 [#/sec] (mean)
Time per request:       0.965 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    104285.07 [#/sec] (mean)
Time per request:       0.959 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    35057.09 [#/sec] (mean)
Time per request:       2.852 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    91116.17 [#/sec] (mean)
Time per request:       1.097 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    89901.38 [#/sec] (mean)
Time per request:       1.112 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15942.71 [#/sec] (mean)
Time per request:       6.272 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    15404.85 [#/sec] (mean)
Time per request:       6.491 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    17902.19 [#/sec] (mean)
Time per request:       5.586 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    19380.52 [#/sec] (mean)
Time per request:       5.160 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    101794.64 [#/sec] (mean)
Time per request:       0.982 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    98436.82 [#/sec] (mean)
Time per request:       1.016 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    71580.42 [#/sec] (mean)
Time per request:       1.397 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    97737.38 [#/sec] (mean)
Time per request:       1.023 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    95966.53 [#/sec] (mean)
Time per request:       1.042 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    92187.14 [#/sec] (mean)
Time per request:       1.085 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    103595.81 [#/sec] (mean)
Time per request:       0.965 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    18378.70 [#/sec] (mean)
Time per request:       5.441 [ms] (mean)
Time per request:       0.054 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    79584.89 [#/sec] (mean)
Time per request:       1.257 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    63632.66 [#/sec] (mean)
Time per request:       1.572 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    60323.09 [#/sec] (mean)
Time per request:       1.658 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    98439.73 [#/sec] (mean)
Time per request:       1.016 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

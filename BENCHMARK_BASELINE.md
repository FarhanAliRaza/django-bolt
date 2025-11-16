# Django-Bolt Benchmark
Generated: Sat Nov 15 09:17:41 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    97354.87 [#/sec] (mean)
Time per request:       1.027 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    79659.06 [#/sec] (mean)
Time per request:       1.255 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    40493.54 [#/sec] (mean)
Time per request:       2.470 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    94057.45 [#/sec] (mean)
Time per request:       1.063 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    93939.93 [#/sec] (mean)
Time per request:       1.065 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    94899.17 [#/sec] (mean)
Time per request:       1.054 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    98375.82 [#/sec] (mean)
Time per request:       1.017 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    91189.29 [#/sec] (mean)
Time per request:       1.097 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    30087.13 [#/sec] (mean)
Time per request:       3.324 [ms] (mean)
Time per request:       0.033 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Get Authenticated User (/auth/me)
Failed requests:        0
Requests per second:    13366.96 [#/sec] (mean)
Time per request:       7.481 [ms] (mean)
Time per request:       0.075 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    7635.14 [#/sec] (mean)
Time per request:       13.097 [ms] (mean)
Time per request:       0.131 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    52394.15 [#/sec] (mean)
Time per request:       1.909 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    64951.94 [#/sec] (mean)
Time per request:       1.540 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    87144.45 [#/sec] (mean)
Time per request:       1.148 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15490.38 [#/sec] (mean)
Time per request:       6.456 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    13180.72 [#/sec] (mean)
Time per request:       7.587 [ms] (mean)
Time per request:       0.076 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    18799.85 [#/sec] (mean)
Time per request:       5.319 [ms] (mean)
Time per request:       0.053 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    16788.52 [#/sec] (mean)
Time per request:       5.956 [ms] (mean)
Time per request:       0.060 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    92882.42 [#/sec] (mean)
Time per request:       1.077 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    84833.47 [#/sec] (mean)
Time per request:       1.179 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    62476.57 [#/sec] (mean)
Time per request:       1.601 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    86753.59 [#/sec] (mean)
Time per request:       1.153 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    86676.14 [#/sec] (mean)
Time per request:       1.154 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    88153.10 [#/sec] (mean)
Time per request:       1.134 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    58319.92 [#/sec] (mean)
Time per request:       1.715 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    16431.94 [#/sec] (mean)
Time per request:       6.086 [ms] (mean)
Time per request:       0.061 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    76216.61 [#/sec] (mean)
Time per request:       1.312 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    59630.29 [#/sec] (mean)
Time per request:       1.677 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    54809.24 [#/sec] (mean)
Time per request:       1.825 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    91323.37 [#/sec] (mean)
Time per request:       1.095 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

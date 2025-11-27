# Django-Bolt Benchmark
Generated: Thu Nov 27 05:22:11 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    64858.41 [#/sec] (mean)
Time per request:       1.542 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    55073.05 [#/sec] (mean)
Time per request:       1.816 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    40506.99 [#/sec] (mean)
Time per request:       2.469 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    61311.33 [#/sec] (mean)
Time per request:       1.631 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    60679.61 [#/sec] (mean)
Time per request:       1.648 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    60723.83 [#/sec] (mean)
Time per request:       1.647 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    62871.33 [#/sec] (mean)
Time per request:       1.591 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    53526.31 [#/sec] (mean)
Time per request:       1.868 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    26524.78 [#/sec] (mean)
Time per request:       3.770 [ms] (mean)
Time per request:       0.038 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Get Authenticated User (/auth/me)
Failed requests:        0
Requests per second:    10841.05 [#/sec] (mean)
Time per request:       9.224 [ms] (mean)
Time per request:       0.092 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    57472.92 [#/sec] (mean)
Time per request:       1.740 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    57008.64 [#/sec] (mean)
Time per request:       1.754 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

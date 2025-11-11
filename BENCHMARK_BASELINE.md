# Django-Bolt Benchmark
Generated: Wed Nov 12 01:12:49 AM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    74773.62 [#/sec] (mean)
Time per request:       1.337 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    62173.98 [#/sec] (mean)
Time per request:       1.608 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    62767.15 [#/sec] (mean)
Time per request:       1.593 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    72524.20 [#/sec] (mean)
Time per request:       1.379 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    73028.95 [#/sec] (mean)
Time per request:       1.369 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    72522.10 [#/sec] (mean)
Time per request:       1.379 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    74181.78 [#/sec] (mean)
Time per request:       1.348 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    74665.31 [#/sec] (mean)
Time per request:       1.339 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    29149.93 [#/sec] (mean)
Time per request:       3.431 [ms] (mean)
Time per request:       0.034 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Get Authenticated User (/auth/me)
Failed requests:        0
Requests per second:    12044.94 [#/sec] (mean)
Time per request:       8.302 [ms] (mean)
Time per request:       0.083 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    6865.69 [#/sec] (mean)
Time per request:       14.565 [ms] (mean)
Time per request:       0.146 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    55519.47 [#/sec] (mean)
Time per request:       1.801 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    59140.10 [#/sec] (mean)
Time per request:       1.691 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    60367.15 [#/sec] (mean)
Time per request:       1.657 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    14153.10 [#/sec] (mean)
Time per request:       7.066 [ms] (mean)
Time per request:       0.071 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    11916.17 [#/sec] (mean)
Time per request:       8.392 [ms] (mean)
Time per request:       0.084 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    16580.83 [#/sec] (mean)
Time per request:       6.031 [ms] (mean)
Time per request:       0.060 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    17087.33 [#/sec] (mean)
Time per request:       5.852 [ms] (mean)
Time per request:       0.059 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    73927.86 [#/sec] (mean)
Time per request:       1.353 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    70359.11 [#/sec] (mean)
Time per request:       1.421 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    52107.49 [#/sec] (mean)
Time per request:       1.919 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    69138.60 [#/sec] (mean)
Time per request:       1.446 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    67458.18 [#/sec] (mean)
Time per request:       1.482 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    69004.06 [#/sec] (mean)
Time per request:       1.449 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    69818.75 [#/sec] (mean)
Time per request:       1.432 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    16062.66 [#/sec] (mean)
Time per request:       6.226 [ms] (mean)
Time per request:       0.062 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    56607.83 [#/sec] (mean)
Time per request:       1.767 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    45118.41 [#/sec] (mean)
Time per request:       2.216 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    41206.36 [#/sec] (mean)
Time per request:       2.427 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    68107.36 [#/sec] (mean)
Time per request:       1.468 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

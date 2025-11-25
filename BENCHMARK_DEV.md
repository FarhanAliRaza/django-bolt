# Django-Bolt Benchmark
Generated: Tue Nov 25 11:20:51 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    102008.55 [#/sec] (mean)
Time per request:       0.980 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    82906.37 [#/sec] (mean)
Time per request:       1.206 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    59132.76 [#/sec] (mean)
Time per request:       1.691 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    103230.07 [#/sec] (mean)
Time per request:       0.969 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    100639.06 [#/sec] (mean)
Time per request:       0.994 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    99294.02 [#/sec] (mean)
Time per request:       1.007 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    99096.24 [#/sec] (mean)
Time per request:       1.009 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    103676.36 [#/sec] (mean)
Time per request:       0.965 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    34608.78 [#/sec] (mean)
Time per request:       2.889 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Get Authenticated User (/auth/me)
Failed requests:        0
Requests per second:    12013.47 [#/sec] (mean)
Time per request:       8.324 [ms] (mean)
Time per request:       0.083 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    7699.84 [#/sec] (mean)
Time per request:       12.987 [ms] (mean)
Time per request:       0.130 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    87681.61 [#/sec] (mean)
Time per request:       1.140 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    91573.41 [#/sec] (mean)
Time per request:       1.092 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    87984.80 [#/sec] (mean)
Time per request:       1.137 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    14610.51 [#/sec] (mean)
Time per request:       6.844 [ms] (mean)
Time per request:       0.068 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    12780.65 [#/sec] (mean)
Time per request:       7.824 [ms] (mean)
Time per request:       0.078 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    19595.66 [#/sec] (mean)
Time per request:       5.103 [ms] (mean)
Time per request:       0.051 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    17106.30 [#/sec] (mean)
Time per request:       5.846 [ms] (mean)
Time per request:       0.058 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    100691.75 [#/sec] (mean)
Time per request:       0.993 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    95014.58 [#/sec] (mean)
Time per request:       1.052 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    67321.93 [#/sec] (mean)
Time per request:       1.485 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    93909.06 [#/sec] (mean)
Time per request:       1.065 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    92779.87 [#/sec] (mean)
Time per request:       1.078 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    93754.98 [#/sec] (mean)
Time per request:       1.067 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    97999.82 [#/sec] (mean)
Time per request:       1.020 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    17556.98 [#/sec] (mean)
Time per request:       5.696 [ms] (mean)
Time per request:       0.057 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    80667.93 [#/sec] (mean)
Time per request:       1.240 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    59684.75 [#/sec] (mean)
Time per request:       1.675 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    56670.39 [#/sec] (mean)
Time per request:       1.765 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    88814.68 [#/sec] (mean)
Time per request:       1.126 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    87511.27 [#/sec] (mean)
Time per request:       1.143 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    83120.68 [#/sec] (mean)
Time per request:       1.203 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    92402.65 [#/sec] (mean)
Time per request:       1.082 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

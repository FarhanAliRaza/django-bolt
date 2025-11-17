# Django-Bolt Benchmark
Generated: Mon Nov 17 07:30:38 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    101898.37 [#/sec] (mean)
Time per request:       0.981 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    83837.05 [#/sec] (mean)
Time per request:       1.193 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    47992.94 [#/sec] (mean)
Time per request:       2.084 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    101284.28 [#/sec] (mean)
Time per request:       0.987 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    99403.58 [#/sec] (mean)
Time per request:       1.006 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    97954.71 [#/sec] (mean)
Time per request:       1.021 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    98103.66 [#/sec] (mean)
Time per request:       1.019 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    94879.36 [#/sec] (mean)
Time per request:       1.054 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    18880.54 [#/sec] (mean)
Time per request:       5.296 [ms] (mean)
Time per request:       0.053 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Get Authenticated User (/auth/me)
Failed requests:        0
Requests per second:    14351.05 [#/sec] (mean)
Time per request:       6.968 [ms] (mean)
Time per request:       0.070 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    7899.17 [#/sec] (mean)
Time per request:       12.660 [ms] (mean)
Time per request:       0.127 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    92858.27 [#/sec] (mean)
Time per request:       1.077 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    90670.05 [#/sec] (mean)
Time per request:       1.103 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    92014.10 [#/sec] (mean)
Time per request:       1.087 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    17828.14 [#/sec] (mean)
Time per request:       5.609 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    14766.82 [#/sec] (mean)
Time per request:       6.772 [ms] (mean)
Time per request:       0.068 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    20737.85 [#/sec] (mean)
Time per request:       4.822 [ms] (mean)
Time per request:       0.048 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    17907.03 [#/sec] (mean)
Time per request:       5.584 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    101411.65 [#/sec] (mean)
Time per request:       0.986 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    95365.25 [#/sec] (mean)
Time per request:       1.049 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    70678.37 [#/sec] (mean)
Time per request:       1.415 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    95152.91 [#/sec] (mean)
Time per request:       1.051 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    89575.23 [#/sec] (mean)
Time per request:       1.116 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    97281.94 [#/sec] (mean)
Time per request:       1.028 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    101280.18 [#/sec] (mean)
Time per request:       0.987 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    21391.47 [#/sec] (mean)
Time per request:       4.675 [ms] (mean)
Time per request:       0.047 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    79711.13 [#/sec] (mean)
Time per request:       1.255 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    62419.25 [#/sec] (mean)
Time per request:       1.602 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    57126.21 [#/sec] (mean)
Time per request:       1.751 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    97546.70 [#/sec] (mean)
Time per request:       1.025 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    93053.55 [#/sec] (mean)
Time per request:       1.075 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    89653.13 [#/sec] (mean)
Time per request:       1.115 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    93999.98 [#/sec] (mean)
Time per request:       1.064 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

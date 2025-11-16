# Django-Bolt Benchmark
Generated: Mon Nov 17 12:38:21 AM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    99433.23 [#/sec] (mean)
Time per request:       1.006 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    77867.67 [#/sec] (mean)
Time per request:       1.284 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    45941.10 [#/sec] (mean)
Time per request:       2.177 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    100835.93 [#/sec] (mean)
Time per request:       0.992 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    87364.48 [#/sec] (mean)
Time per request:       1.145 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    93141.09 [#/sec] (mean)
Time per request:       1.074 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    69562.31 [#/sec] (mean)
Time per request:       1.438 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    99504.47 [#/sec] (mean)
Time per request:       1.005 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    30467.65 [#/sec] (mean)
Time per request:       3.282 [ms] (mean)
Time per request:       0.033 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Get Authenticated User (/auth/me)
Failed requests:        0
Requests per second:    14102.88 [#/sec] (mean)
Time per request:       7.091 [ms] (mean)
Time per request:       0.071 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    7952.08 [#/sec] (mean)
Time per request:       12.575 [ms] (mean)
Time per request:       0.126 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    88645.41 [#/sec] (mean)
Time per request:       1.128 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    88610.06 [#/sec] (mean)
Time per request:       1.129 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    87109.53 [#/sec] (mean)
Time per request:       1.148 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15089.60 [#/sec] (mean)
Time per request:       6.627 [ms] (mean)
Time per request:       0.066 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    13219.14 [#/sec] (mean)
Time per request:       7.565 [ms] (mean)
Time per request:       0.076 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    17800.12 [#/sec] (mean)
Time per request:       5.618 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    16716.96 [#/sec] (mean)
Time per request:       5.982 [ms] (mean)
Time per request:       0.060 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    99745.65 [#/sec] (mean)
Time per request:       1.003 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    88085.55 [#/sec] (mean)
Time per request:       1.135 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    63768.19 [#/sec] (mean)
Time per request:       1.568 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    94030.92 [#/sec] (mean)
Time per request:       1.063 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    87810.96 [#/sec] (mean)
Time per request:       1.139 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    85920.25 [#/sec] (mean)
Time per request:       1.164 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    99510.41 [#/sec] (mean)
Time per request:       1.005 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    21272.66 [#/sec] (mean)
Time per request:       4.701 [ms] (mean)
Time per request:       0.047 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    73043.35 [#/sec] (mean)
Time per request:       1.369 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    57766.74 [#/sec] (mean)
Time per request:       1.731 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    50376.31 [#/sec] (mean)
Time per request:       1.985 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    97690.59 [#/sec] (mean)
Time per request:       1.024 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    90714.47 [#/sec] (mean)
Time per request:       1.102 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    88151.55 [#/sec] (mean)
Time per request:       1.134 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    91519.78 [#/sec] (mean)
Time per request:       1.093 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

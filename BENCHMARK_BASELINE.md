# Django-Bolt Benchmark
Generated: Tue Nov 25 11:17:26 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    99861.19 [#/sec] (mean)
Time per request:       1.001 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    77802.85 [#/sec] (mean)
Time per request:       1.285 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    58383.93 [#/sec] (mean)
Time per request:       1.713 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    97454.49 [#/sec] (mean)
Time per request:       1.026 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    93917.88 [#/sec] (mean)
Time per request:       1.065 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    94194.78 [#/sec] (mean)
Time per request:       1.062 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    98607.66 [#/sec] (mean)
Time per request:       1.014 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    98493.06 [#/sec] (mean)
Time per request:       1.015 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    34549.00 [#/sec] (mean)
Time per request:       2.894 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Get Authenticated User (/auth/me)
Failed requests:        0
Requests per second:    13549.11 [#/sec] (mean)
Time per request:       7.381 [ms] (mean)
Time per request:       0.074 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    7778.83 [#/sec] (mean)
Time per request:       12.855 [ms] (mean)
Time per request:       0.129 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    90105.51 [#/sec] (mean)
Time per request:       1.110 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    93633.84 [#/sec] (mean)
Time per request:       1.068 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    92141.27 [#/sec] (mean)
Time per request:       1.085 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15155.88 [#/sec] (mean)
Time per request:       6.598 [ms] (mean)
Time per request:       0.066 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    11226.15 [#/sec] (mean)
Time per request:       8.908 [ms] (mean)
Time per request:       0.089 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    13472.40 [#/sec] (mean)
Time per request:       7.423 [ms] (mean)
Time per request:       0.074 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    15281.43 [#/sec] (mean)
Time per request:       6.544 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    95648.02 [#/sec] (mean)
Time per request:       1.046 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    93254.87 [#/sec] (mean)
Time per request:       1.072 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    69116.62 [#/sec] (mean)
Time per request:       1.447 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    92381.31 [#/sec] (mean)
Time per request:       1.082 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    88967.97 [#/sec] (mean)
Time per request:       1.124 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    87903.59 [#/sec] (mean)
Time per request:       1.138 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    98340.02 [#/sec] (mean)
Time per request:       1.017 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    20727.79 [#/sec] (mean)
Time per request:       4.824 [ms] (mean)
Time per request:       0.048 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    78753.80 [#/sec] (mean)
Time per request:       1.270 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    61479.44 [#/sec] (mean)
Time per request:       1.627 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    56940.80 [#/sec] (mean)
Time per request:       1.756 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    93903.77 [#/sec] (mean)
Time per request:       1.065 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    94784.93 [#/sec] (mean)
Time per request:       1.055 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    81038.59 [#/sec] (mean)
Time per request:       1.234 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    92632.05 [#/sec] (mean)
Time per request:       1.080 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

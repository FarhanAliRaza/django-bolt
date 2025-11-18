# Django-Bolt Benchmark
Generated: Tue Nov 18 09:26:27 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    101258.64 [#/sec] (mean)
Time per request:       0.988 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    83184.99 [#/sec] (mean)
Time per request:       1.202 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    58362.47 [#/sec] (mean)
Time per request:       1.713 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    98208.67 [#/sec] (mean)
Time per request:       1.018 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    100014.00 [#/sec] (mean)
Time per request:       1.000 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    98935.45 [#/sec] (mean)
Time per request:       1.011 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    105487.46 [#/sec] (mean)
Time per request:       0.948 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    102840.45 [#/sec] (mean)
Time per request:       0.972 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    28408.36 [#/sec] (mean)
Time per request:       3.520 [ms] (mean)
Time per request:       0.035 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Get Authenticated User (/auth/me)
Failed requests:        0
Requests per second:    13965.39 [#/sec] (mean)
Time per request:       7.161 [ms] (mean)
Time per request:       0.072 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    8047.55 [#/sec] (mean)
Time per request:       12.426 [ms] (mean)
Time per request:       0.124 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    90511.66 [#/sec] (mean)
Time per request:       1.105 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    93471.92 [#/sec] (mean)
Time per request:       1.070 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    92126.84 [#/sec] (mean)
Time per request:       1.085 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15898.76 [#/sec] (mean)
Time per request:       6.290 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    13257.76 [#/sec] (mean)
Time per request:       7.543 [ms] (mean)
Time per request:       0.075 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    19430.19 [#/sec] (mean)
Time per request:       5.147 [ms] (mean)
Time per request:       0.051 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    16981.10 [#/sec] (mean)
Time per request:       5.889 [ms] (mean)
Time per request:       0.059 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    102445.37 [#/sec] (mean)
Time per request:       0.976 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    99204.38 [#/sec] (mean)
Time per request:       1.008 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    65890.48 [#/sec] (mean)
Time per request:       1.518 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    98020.00 [#/sec] (mean)
Time per request:       1.020 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    96241.76 [#/sec] (mean)
Time per request:       1.039 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    97296.14 [#/sec] (mean)
Time per request:       1.028 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    101398.28 [#/sec] (mean)
Time per request:       0.986 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    21740.83 [#/sec] (mean)
Time per request:       4.600 [ms] (mean)
Time per request:       0.046 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    84485.86 [#/sec] (mean)
Time per request:       1.184 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    58426.91 [#/sec] (mean)
Time per request:       1.712 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    56956.04 [#/sec] (mean)
Time per request:       1.756 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    90557.56 [#/sec] (mean)
Time per request:       1.104 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    93402.08 [#/sec] (mean)
Time per request:       1.071 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    79611.50 [#/sec] (mean)
Time per request:       1.256 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    97033.68 [#/sec] (mean)
Time per request:       1.031 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

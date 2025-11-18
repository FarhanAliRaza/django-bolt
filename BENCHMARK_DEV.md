# Django-Bolt Benchmark
Generated: Tue Nov 18 09:35:50 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    103029.05 [#/sec] (mean)
Time per request:       0.971 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    85282.03 [#/sec] (mean)
Time per request:       1.173 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    60708.34 [#/sec] (mean)
Time per request:       1.647 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    103104.48 [#/sec] (mean)
Time per request:       0.970 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    100783.08 [#/sec] (mean)
Time per request:       0.992 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    100290.84 [#/sec] (mean)
Time per request:       0.997 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    103450.06 [#/sec] (mean)
Time per request:       0.967 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    105591.05 [#/sec] (mean)
Time per request:       0.947 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    35986.37 [#/sec] (mean)
Time per request:       2.779 [ms] (mean)
Time per request:       0.028 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Get Authenticated User (/auth/me)
Failed requests:        0
Requests per second:    14587.98 [#/sec] (mean)
Time per request:       6.855 [ms] (mean)
Time per request:       0.069 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    8115.45 [#/sec] (mean)
Time per request:       12.322 [ms] (mean)
Time per request:       0.123 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    83694.62 [#/sec] (mean)
Time per request:       1.195 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    78608.32 [#/sec] (mean)
Time per request:       1.272 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    88488.53 [#/sec] (mean)
Time per request:       1.130 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15919.43 [#/sec] (mean)
Time per request:       6.282 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    13469.81 [#/sec] (mean)
Time per request:       7.424 [ms] (mean)
Time per request:       0.074 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    19416.68 [#/sec] (mean)
Time per request:       5.150 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    16789.31 [#/sec] (mean)
Time per request:       5.956 [ms] (mean)
Time per request:       0.060 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    104948.31 [#/sec] (mean)
Time per request:       0.953 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    98720.58 [#/sec] (mean)
Time per request:       1.013 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    68590.40 [#/sec] (mean)
Time per request:       1.458 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    97747.89 [#/sec] (mean)
Time per request:       1.023 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    72581.05 [#/sec] (mean)
Time per request:       1.378 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    97780.39 [#/sec] (mean)
Time per request:       1.023 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    101572.34 [#/sec] (mean)
Time per request:       0.985 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    21720.95 [#/sec] (mean)
Time per request:       4.604 [ms] (mean)
Time per request:       0.046 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    82756.11 [#/sec] (mean)
Time per request:       1.208 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    60885.77 [#/sec] (mean)
Time per request:       1.642 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    58824.91 [#/sec] (mean)
Time per request:       1.700 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    100496.45 [#/sec] (mean)
Time per request:       0.995 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    94998.34 [#/sec] (mean)
Time per request:       1.053 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    92371.93 [#/sec] (mean)
Time per request:       1.083 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    91255.86 [#/sec] (mean)
Time per request:       1.096 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

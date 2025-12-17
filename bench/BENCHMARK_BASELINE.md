# Django-Bolt Benchmark
Generated: Wed Dec 17 12:50:03 AM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    100392.53 [#/sec] (mean)
Time per request:       0.996 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    84235.35 [#/sec] (mean)
Time per request:       1.187 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    85334.43 [#/sec] (mean)
Time per request:       1.172 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    102061.65 [#/sec] (mean)
Time per request:       0.980 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    102777.04 [#/sec] (mean)
Time per request:       0.973 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    101855.81 [#/sec] (mean)
Time per request:       0.982 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    104297.04 [#/sec] (mean)
Time per request:       0.959 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    105584.36 [#/sec] (mean)
Time per request:       0.947 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    34098.74 [#/sec] (mean)
Time per request:       2.933 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
Failed requests:        0
Requests per second:    83422.32 [#/sec] (mean)
Time per request:       1.199 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
Failed requests:        0
Requests per second:    18049.76 [#/sec] (mean)
Time per request:       5.540 [ms] (mean)
Time per request:       0.055 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    16580.01 [#/sec] (mean)
Time per request:       6.031 [ms] (mean)
Time per request:       0.060 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    89841.61 [#/sec] (mean)
Time per request:       1.113 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    96291.80 [#/sec] (mean)
Time per request:       1.039 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    96804.48 [#/sec] (mean)
Time per request:       1.033 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15131.87 [#/sec] (mean)
Time per request:       6.609 [ms] (mean)
Time per request:       0.066 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    13409.16 [#/sec] (mean)
Time per request:       7.458 [ms] (mean)
Time per request:       0.075 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    17346.29 [#/sec] (mean)
Time per request:       5.765 [ms] (mean)
Time per request:       0.058 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    15275.15 [#/sec] (mean)
Time per request:       6.547 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    103171.49 [#/sec] (mean)
Time per request:       0.969 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    101506.35 [#/sec] (mean)
Time per request:       0.985 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    69238.65 [#/sec] (mean)
Time per request:       1.444 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    93501.64 [#/sec] (mean)
Time per request:       1.069 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    96864.50 [#/sec] (mean)
Time per request:       1.032 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    99937.04 [#/sec] (mean)
Time per request:       1.001 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    100854.24 [#/sec] (mean)
Time per request:       0.992 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    17955.71 [#/sec] (mean)
Time per request:       5.569 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    81564.74 [#/sec] (mean)
Time per request:       1.226 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    60810.98 [#/sec] (mean)
Time per request:       1.644 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    57830.21 [#/sec] (mean)
Time per request:       1.729 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
Failed requests:        0
Requests per second:    14892.59 [#/sec] (mean)
Time per request:       6.715 [ms] (mean)
Time per request:       0.067 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    100697.84 [#/sec] (mean)
Time per request:       0.993 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    100089.08 [#/sec] (mean)
Time per request:       0.999 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    90203.05 [#/sec] (mean)
Time per request:       1.109 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    97977.74 [#/sec] (mean)
Time per request:       1.021 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

# Django-Bolt Benchmark
Generated: Tue Dec  9 10:04:09 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    105131.47 [#/sec] (mean)
Time per request:       0.951 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    86123.74 [#/sec] (mean)
Time per request:       1.161 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    85705.23 [#/sec] (mean)
Time per request:       1.167 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    101892.14 [#/sec] (mean)
Time per request:       0.981 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    106018.68 [#/sec] (mean)
Time per request:       0.943 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    102671.51 [#/sec] (mean)
Time per request:       0.974 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    106333.21 [#/sec] (mean)
Time per request:       0.940 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    106748.65 [#/sec] (mean)
Time per request:       0.937 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    29921.75 [#/sec] (mean)
Time per request:       3.342 [ms] (mean)
Time per request:       0.033 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
Failed requests:        0
Requests per second:    83281.98 [#/sec] (mean)
Time per request:       1.201 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
Failed requests:        0
Requests per second:    17929.24 [#/sec] (mean)
Time per request:       5.577 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    16510.61 [#/sec] (mean)
Time per request:       6.057 [ms] (mean)
Time per request:       0.061 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    89392.67 [#/sec] (mean)
Time per request:       1.119 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    94877.56 [#/sec] (mean)
Time per request:       1.054 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    95242.63 [#/sec] (mean)
Time per request:       1.050 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15156.29 [#/sec] (mean)
Time per request:       6.598 [ms] (mean)
Time per request:       0.066 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    12978.30 [#/sec] (mean)
Time per request:       7.705 [ms] (mean)
Time per request:       0.077 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    18835.62 [#/sec] (mean)
Time per request:       5.309 [ms] (mean)
Time per request:       0.053 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    15705.74 [#/sec] (mean)
Time per request:       6.367 [ms] (mean)
Time per request:       0.064 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    102368.81 [#/sec] (mean)
Time per request:       0.977 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    103549.68 [#/sec] (mean)
Time per request:       0.966 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    70477.63 [#/sec] (mean)
Time per request:       1.419 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    95371.62 [#/sec] (mean)
Time per request:       1.049 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    97422.21 [#/sec] (mean)
Time per request:       1.026 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    99936.04 [#/sec] (mean)
Time per request:       1.001 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    101870.34 [#/sec] (mean)
Time per request:       0.982 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    17406.20 [#/sec] (mean)
Time per request:       5.745 [ms] (mean)
Time per request:       0.057 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    82782.14 [#/sec] (mean)
Time per request:       1.208 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    63975.43 [#/sec] (mean)
Time per request:       1.563 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    59587.65 [#/sec] (mean)
Time per request:       1.678 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
Failed requests:        0
Requests per second:    11061.79 [#/sec] (mean)
Time per request:       9.040 [ms] (mean)
Time per request:       0.090 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    101934.72 [#/sec] (mean)
Time per request:       0.981 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    100321.03 [#/sec] (mean)
Time per request:       0.997 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    89592.09 [#/sec] (mean)
Time per request:       1.116 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    100632.98 [#/sec] (mean)
Time per request:       0.994 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

# Django-Bolt Benchmark
Generated: Wed Dec 24 04:25:02 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    105138.10 [#/sec] (mean)
Time per request:       0.951 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    86825.15 [#/sec] (mean)
Time per request:       1.152 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    87434.75 [#/sec] (mean)
Time per request:       1.144 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    105599.97 [#/sec] (mean)
Time per request:       0.947 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    107938.91 [#/sec] (mean)
Time per request:       0.926 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    103813.05 [#/sec] (mean)
Time per request:       0.963 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    106213.49 [#/sec] (mean)
Time per request:       0.942 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    103018.44 [#/sec] (mean)
Time per request:       0.971 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    28531.24 [#/sec] (mean)
Time per request:       3.505 [ms] (mean)
Time per request:       0.035 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
Failed requests:        0
Requests per second:    88975.89 [#/sec] (mean)
Time per request:       1.124 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
Failed requests:        0
Requests per second:    17614.91 [#/sec] (mean)
Time per request:       5.677 [ms] (mean)
Time per request:       0.057 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    16657.45 [#/sec] (mean)
Time per request:       6.003 [ms] (mean)
Time per request:       0.060 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    73416.05 [#/sec] (mean)
Time per request:       1.362 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    81453.12 [#/sec] (mean)
Time per request:       1.228 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    77690.42 [#/sec] (mean)
Time per request:       1.287 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15029.68 [#/sec] (mean)
Time per request:       6.654 [ms] (mean)
Time per request:       0.067 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    12910.69 [#/sec] (mean)
Time per request:       7.746 [ms] (mean)
Time per request:       0.077 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    17027.54 [#/sec] (mean)
Time per request:       5.873 [ms] (mean)
Time per request:       0.059 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    15299.20 [#/sec] (mean)
Time per request:       6.536 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    103136.38 [#/sec] (mean)
Time per request:       0.970 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    104539.09 [#/sec] (mean)
Time per request:       0.957 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    67955.56 [#/sec] (mean)
Time per request:       1.472 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    97618.12 [#/sec] (mean)
Time per request:       1.024 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    99141.44 [#/sec] (mean)
Time per request:       1.009 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    101635.31 [#/sec] (mean)
Time per request:       0.984 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    103871.28 [#/sec] (mean)
Time per request:       0.963 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    17850.03 [#/sec] (mean)
Time per request:       5.602 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    84463.03 [#/sec] (mean)
Time per request:       1.184 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    63341.25 [#/sec] (mean)
Time per request:       1.579 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    59097.81 [#/sec] (mean)
Time per request:       1.692 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
Failed requests:        0
Requests per second:    15337.31 [#/sec] (mean)
Time per request:       6.520 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    102597.78 [#/sec] (mean)
Time per request:       0.975 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    94421.57 [#/sec] (mean)
Time per request:       1.059 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    87942.24 [#/sec] (mean)
Time per request:       1.137 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    102429.63 [#/sec] (mean)
Time per request:       0.976 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

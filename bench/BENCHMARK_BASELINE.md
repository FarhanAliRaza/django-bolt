# Django-Bolt Benchmark
Generated: Wed Dec 24 01:17:49 AM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    106482.66 [#/sec] (mean)
Time per request:       0.939 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    84727.81 [#/sec] (mean)
Time per request:       1.180 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    85181.78 [#/sec] (mean)
Time per request:       1.174 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    101638.41 [#/sec] (mean)
Time per request:       0.984 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    103087.47 [#/sec] (mean)
Time per request:       0.970 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    101330.47 [#/sec] (mean)
Time per request:       0.987 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    104213.35 [#/sec] (mean)
Time per request:       0.960 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    105843.63 [#/sec] (mean)
Time per request:       0.945 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    33429.83 [#/sec] (mean)
Time per request:       2.991 [ms] (mean)
Time per request:       0.030 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
Failed requests:        0
Requests per second:    83175.30 [#/sec] (mean)
Time per request:       1.202 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
Failed requests:        0
Requests per second:    17838.25 [#/sec] (mean)
Time per request:       5.606 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    16460.66 [#/sec] (mean)
Time per request:       6.075 [ms] (mean)
Time per request:       0.061 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    87681.61 [#/sec] (mean)
Time per request:       1.140 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    93240.96 [#/sec] (mean)
Time per request:       1.072 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    94004.40 [#/sec] (mean)
Time per request:       1.064 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    14774.19 [#/sec] (mean)
Time per request:       6.769 [ms] (mean)
Time per request:       0.068 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    13196.69 [#/sec] (mean)
Time per request:       7.578 [ms] (mean)
Time per request:       0.076 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    17101.27 [#/sec] (mean)
Time per request:       5.848 [ms] (mean)
Time per request:       0.058 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    15312.36 [#/sec] (mean)
Time per request:       6.531 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    103271.65 [#/sec] (mean)
Time per request:       0.968 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    99208.32 [#/sec] (mean)
Time per request:       1.008 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    69536.68 [#/sec] (mean)
Time per request:       1.438 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    94504.56 [#/sec] (mean)
Time per request:       1.058 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    96194.54 [#/sec] (mean)
Time per request:       1.040 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    101418.85 [#/sec] (mean)
Time per request:       0.986 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    99911.08 [#/sec] (mean)
Time per request:       1.001 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    17669.56 [#/sec] (mean)
Time per request:       5.659 [ms] (mean)
Time per request:       0.057 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    80422.70 [#/sec] (mean)
Time per request:       1.243 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    62296.76 [#/sec] (mean)
Time per request:       1.605 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    58259.78 [#/sec] (mean)
Time per request:       1.716 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
Failed requests:        0
Requests per second:    15122.46 [#/sec] (mean)
Time per request:       6.613 [ms] (mean)
Time per request:       0.066 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    102564.10 [#/sec] (mean)
Time per request:       0.975 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    97966.22 [#/sec] (mean)
Time per request:       1.021 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    92743.73 [#/sec] (mean)
Time per request:       1.078 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    100984.60 [#/sec] (mean)
Time per request:       0.990 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

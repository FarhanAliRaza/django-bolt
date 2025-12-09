# Django-Bolt Benchmark
Generated: Tue Dec  9 11:31:53 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    100092.08 [#/sec] (mean)
Time per request:       0.999 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    81322.63 [#/sec] (mean)
Time per request:       1.230 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    80857.74 [#/sec] (mean)
Time per request:       1.237 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    95616.92 [#/sec] (mean)
Time per request:       1.046 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    103700.02 [#/sec] (mean)
Time per request:       0.964 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    99389.75 [#/sec] (mean)
Time per request:       1.006 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    106089.54 [#/sec] (mean)
Time per request:       0.943 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    105817.87 [#/sec] (mean)
Time per request:       0.945 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    22480.65 [#/sec] (mean)
Time per request:       4.448 [ms] (mean)
Time per request:       0.044 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
Failed requests:        0
Requests per second:    78445.52 [#/sec] (mean)
Time per request:       1.275 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
Failed requests:        0
Requests per second:    17052.92 [#/sec] (mean)
Time per request:       5.864 [ms] (mean)
Time per request:       0.059 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    15965.79 [#/sec] (mean)
Time per request:       6.263 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    88747.68 [#/sec] (mean)
Time per request:       1.127 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    95083.25 [#/sec] (mean)
Time per request:       1.052 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    95616.92 [#/sec] (mean)
Time per request:       1.046 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15944.92 [#/sec] (mean)
Time per request:       6.272 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    13689.78 [#/sec] (mean)
Time per request:       7.305 [ms] (mean)
Time per request:       0.073 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    19208.79 [#/sec] (mean)
Time per request:       5.206 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    16008.02 [#/sec] (mean)
Time per request:       6.247 [ms] (mean)
Time per request:       0.062 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    105539.78 [#/sec] (mean)
Time per request:       0.948 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    99946.03 [#/sec] (mean)
Time per request:       1.001 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    68705.86 [#/sec] (mean)
Time per request:       1.455 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    96247.32 [#/sec] (mean)
Time per request:       1.039 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    97520.06 [#/sec] (mean)
Time per request:       1.025 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    101192.04 [#/sec] (mean)
Time per request:       0.988 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    104681.35 [#/sec] (mean)
Time per request:       0.955 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    18036.48 [#/sec] (mean)
Time per request:       5.544 [ms] (mean)
Time per request:       0.055 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    80656.22 [#/sec] (mean)
Time per request:       1.240 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    61424.68 [#/sec] (mean)
Time per request:       1.628 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    59122.97 [#/sec] (mean)
Time per request:       1.691 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
Failed requests:        0
Requests per second:    10701.87 [#/sec] (mean)
Time per request:       9.344 [ms] (mean)
Time per request:       0.093 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    103603.32 [#/sec] (mean)
Time per request:       0.965 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    100258.67 [#/sec] (mean)
Time per request:       0.997 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    87753.94 [#/sec] (mean)
Time per request:       1.140 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    96321.48 [#/sec] (mean)
Time per request:       1.038 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

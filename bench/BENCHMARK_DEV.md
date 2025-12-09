# Django-Bolt Benchmark
Generated: Tue Dec  9 10:24:53 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    102905.01 [#/sec] (mean)
Time per request:       0.972 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    77955.08 [#/sec] (mean)
Time per request:       1.283 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    81143.14 [#/sec] (mean)
Time per request:       1.232 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    102130.44 [#/sec] (mean)
Time per request:       0.979 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    101017.24 [#/sec] (mean)
Time per request:       0.990 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    101383.89 [#/sec] (mean)
Time per request:       0.986 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    100401.61 [#/sec] (mean)
Time per request:       0.996 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    98161.44 [#/sec] (mean)
Time per request:       1.019 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    28132.48 [#/sec] (mean)
Time per request:       3.555 [ms] (mean)
Time per request:       0.036 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
Failed requests:        0
Requests per second:    81926.25 [#/sec] (mean)
Time per request:       1.221 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
Failed requests:        0
Requests per second:    17220.51 [#/sec] (mean)
Time per request:       5.807 [ms] (mean)
Time per request:       0.058 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    16291.90 [#/sec] (mean)
Time per request:       6.138 [ms] (mean)
Time per request:       0.061 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    85842.07 [#/sec] (mean)
Time per request:       1.165 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    92918.67 [#/sec] (mean)
Time per request:       1.076 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    89528.72 [#/sec] (mean)
Time per request:       1.117 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15699.97 [#/sec] (mean)
Time per request:       6.369 [ms] (mean)
Time per request:       0.064 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    13206.72 [#/sec] (mean)
Time per request:       7.572 [ms] (mean)
Time per request:       0.076 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    19328.34 [#/sec] (mean)
Time per request:       5.174 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    15474.80 [#/sec] (mean)
Time per request:       6.462 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    101664.24 [#/sec] (mean)
Time per request:       0.984 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    99155.20 [#/sec] (mean)
Time per request:       1.009 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    69370.26 [#/sec] (mean)
Time per request:       1.442 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    93012.87 [#/sec] (mean)
Time per request:       1.075 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    98117.13 [#/sec] (mean)
Time per request:       1.019 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    97090.21 [#/sec] (mean)
Time per request:       1.030 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    99899.10 [#/sec] (mean)
Time per request:       1.001 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    17928.92 [#/sec] (mean)
Time per request:       5.578 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    71480.14 [#/sec] (mean)
Time per request:       1.399 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    60222.10 [#/sec] (mean)
Time per request:       1.661 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    56731.79 [#/sec] (mean)
Time per request:       1.763 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
Failed requests:        0
Requests per second:    10538.71 [#/sec] (mean)
Time per request:       9.489 [ms] (mean)
Time per request:       0.095 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    94695.18 [#/sec] (mean)
Time per request:       1.056 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    93183.62 [#/sec] (mean)
Time per request:       1.073 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    90848.80 [#/sec] (mean)
Time per request:       1.101 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    99701.89 [#/sec] (mean)
Time per request:       1.003 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

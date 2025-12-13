# Django-Bolt Benchmark
Generated: Thu Dec 11 10:54:07 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    103110.85 [#/sec] (mean)
Time per request:       0.970 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    84893.97 [#/sec] (mean)
Time per request:       1.178 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    85537.35 [#/sec] (mean)
Time per request:       1.169 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    102987.67 [#/sec] (mean)
Time per request:       0.971 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    99144.38 [#/sec] (mean)
Time per request:       1.009 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    103211.96 [#/sec] (mean)
Time per request:       0.969 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    105542.01 [#/sec] (mean)
Time per request:       0.947 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    103741.97 [#/sec] (mean)
Time per request:       0.964 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    34483.12 [#/sec] (mean)
Time per request:       2.900 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
Failed requests:        0
Requests per second:    83055.79 [#/sec] (mean)
Time per request:       1.204 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
Failed requests:        0
Requests per second:    17508.66 [#/sec] (mean)
Time per request:       5.711 [ms] (mean)
Time per request:       0.057 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    16279.88 [#/sec] (mean)
Time per request:       6.143 [ms] (mean)
Time per request:       0.061 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    86805.56 [#/sec] (mean)
Time per request:       1.152 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    93852.65 [#/sec] (mean)
Time per request:       1.066 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    95211.80 [#/sec] (mean)
Time per request:       1.050 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    14919.54 [#/sec] (mean)
Time per request:       6.703 [ms] (mean)
Time per request:       0.067 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    12799.98 [#/sec] (mean)
Time per request:       7.813 [ms] (mean)
Time per request:       0.078 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    17029.10 [#/sec] (mean)
Time per request:       5.872 [ms] (mean)
Time per request:       0.059 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    15694.03 [#/sec] (mean)
Time per request:       6.372 [ms] (mean)
Time per request:       0.064 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    103903.66 [#/sec] (mean)
Time per request:       0.962 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    100648.17 [#/sec] (mean)
Time per request:       0.994 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    71130.33 [#/sec] (mean)
Time per request:       1.406 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    95664.49 [#/sec] (mean)
Time per request:       1.045 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    96095.63 [#/sec] (mean)
Time per request:       1.041 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    99928.05 [#/sec] (mean)
Time per request:       1.001 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    103632.31 [#/sec] (mean)
Time per request:       0.965 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    17753.10 [#/sec] (mean)
Time per request:       5.633 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    79793.81 [#/sec] (mean)
Time per request:       1.253 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    61143.38 [#/sec] (mean)
Time per request:       1.635 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    56347.23 [#/sec] (mean)
Time per request:       1.775 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
Failed requests:        0
Requests per second:    12682.82 [#/sec] (mean)
Time per request:       7.885 [ms] (mean)
Time per request:       0.079 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    99599.61 [#/sec] (mean)
Time per request:       1.004 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    92631.19 [#/sec] (mean)
Time per request:       1.080 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    91646.43 [#/sec] (mean)
Time per request:       1.091 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    98267.54 [#/sec] (mean)
Time per request:       1.018 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

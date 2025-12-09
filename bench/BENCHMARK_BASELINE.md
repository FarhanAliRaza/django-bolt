# Django-Bolt Benchmark
Generated: Tue Dec  9 10:09:55 AM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    102571.47 [#/sec] (mean)
Time per request:       0.975 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    72506.85 [#/sec] (mean)
Time per request:       1.379 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    85712.57 [#/sec] (mean)
Time per request:       1.167 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    102524.14 [#/sec] (mean)
Time per request:       0.975 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    103265.25 [#/sec] (mean)
Time per request:       0.968 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    103757.04 [#/sec] (mean)
Time per request:       0.964 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    105688.14 [#/sec] (mean)
Time per request:       0.946 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    104506.31 [#/sec] (mean)
Time per request:       0.957 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    31981.37 [#/sec] (mean)
Time per request:       3.127 [ms] (mean)
Time per request:       0.031 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
Failed requests:        0
Requests per second:    77134.90 [#/sec] (mean)
Time per request:       1.296 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
Failed requests:        0
Requests per second:    17947.49 [#/sec] (mean)
Time per request:       5.572 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    16135.72 [#/sec] (mean)
Time per request:       6.197 [ms] (mean)
Time per request:       0.062 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    89145.63 [#/sec] (mean)
Time per request:       1.122 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    98712.79 [#/sec] (mean)
Time per request:       1.013 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    90902.48 [#/sec] (mean)
Time per request:       1.100 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    14761.67 [#/sec] (mean)
Time per request:       6.774 [ms] (mean)
Time per request:       0.068 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    13879.44 [#/sec] (mean)
Time per request:       7.205 [ms] (mean)
Time per request:       0.072 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    19308.08 [#/sec] (mean)
Time per request:       5.179 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    15986.19 [#/sec] (mean)
Time per request:       6.255 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    103381.61 [#/sec] (mean)
Time per request:       0.967 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    102246.35 [#/sec] (mean)
Time per request:       0.978 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    68204.45 [#/sec] (mean)
Time per request:       1.466 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    94731.06 [#/sec] (mean)
Time per request:       1.056 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    100081.07 [#/sec] (mean)
Time per request:       0.999 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    100815.60 [#/sec] (mean)
Time per request:       0.992 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    97032.74 [#/sec] (mean)
Time per request:       1.031 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    17821.98 [#/sec] (mean)
Time per request:       5.611 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    80817.88 [#/sec] (mean)
Time per request:       1.237 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    58155.43 [#/sec] (mean)
Time per request:       1.720 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    57632.57 [#/sec] (mean)
Time per request:       1.735 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    102100.20 [#/sec] (mean)
Time per request:       0.979 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    97573.35 [#/sec] (mean)
Time per request:       1.025 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    90439.63 [#/sec] (mean)
Time per request:       1.106 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    99454.00 [#/sec] (mean)
Time per request:       1.005 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

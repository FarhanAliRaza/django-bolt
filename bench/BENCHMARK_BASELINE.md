# Django-Bolt Benchmark
Generated: Fri Jan  2 10:45:10 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    105523.08 [#/sec] (mean)
Time per request:       0.948 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    86823.64 [#/sec] (mean)
Time per request:       1.152 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    87643.96 [#/sec] (mean)
Time per request:       1.141 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    105040.91 [#/sec] (mean)
Time per request:       0.952 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    104637.54 [#/sec] (mean)
Time per request:       0.956 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    103883.15 [#/sec] (mean)
Time per request:       0.963 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    104323.15 [#/sec] (mean)
Time per request:       0.959 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    106006.32 [#/sec] (mean)
Time per request:       0.943 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    33918.43 [#/sec] (mean)
Time per request:       2.948 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
Failed requests:        0
Requests per second:    87304.22 [#/sec] (mean)
Time per request:       1.145 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
Failed requests:        0
Requests per second:    17965.74 [#/sec] (mean)
Time per request:       5.566 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    16837.31 [#/sec] (mean)
Time per request:       5.939 [ms] (mean)
Time per request:       0.059 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    92482.13 [#/sec] (mean)
Time per request:       1.081 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    99049.13 [#/sec] (mean)
Time per request:       1.010 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    101363.34 [#/sec] (mean)
Time per request:       0.987 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15291.06 [#/sec] (mean)
Time per request:       6.540 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    13421.50 [#/sec] (mean)
Time per request:       7.451 [ms] (mean)
Time per request:       0.075 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    17838.67 [#/sec] (mean)
Time per request:       5.606 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    15348.84 [#/sec] (mean)
Time per request:       6.515 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    104242.68 [#/sec] (mean)
Time per request:       0.959 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    104794.34 [#/sec] (mean)
Time per request:       0.954 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    69837.77 [#/sec] (mean)
Time per request:       1.432 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    100303.92 [#/sec] (mean)
Time per request:       0.997 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    102171.14 [#/sec] (mean)
Time per request:       0.979 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    104763.60 [#/sec] (mean)
Time per request:       0.955 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    105310.82 [#/sec] (mean)
Time per request:       0.950 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    18013.67 [#/sec] (mean)
Time per request:       5.551 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    83047.51 [#/sec] (mean)
Time per request:       1.204 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    61959.40 [#/sec] (mean)
Time per request:       1.614 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    59887.05 [#/sec] (mean)
Time per request:       1.670 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
Failed requests:        0
Requests per second:    15587.13 [#/sec] (mean)
Time per request:       6.416 [ms] (mean)
Time per request:       0.064 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    104030.13 [#/sec] (mean)
Time per request:       0.961 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    100811.53 [#/sec] (mean)
Time per request:       0.992 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    88311.92 [#/sec] (mean)
Time per request:       1.132 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    102303.88 [#/sec] (mean)
Time per request:       0.977 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Latency Percentile Benchmarks (bombardier)
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    114762.19   10163.32  123326.30
  Latency      840.88us   380.83us     6.42ms
  Latency Distribution
     50%   755.00us
     75%     1.01ms
     90%     1.32ms
     99%     2.25ms

### Path Parameter - int (/items/12345)
  Reqs/sec    105545.98    7101.40  112716.86
  Latency        0.92ms   306.09us     4.20ms
  Latency Distribution
     50%   846.00us
     75%     1.13ms
     90%     1.42ms
     99%     2.40ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    101798.16    7774.93  109064.91
  Latency        0.96ms   276.70us     4.30ms
  Latency Distribution
     50%     0.89ms
     75%     1.17ms
     90%     1.45ms
     99%     2.11ms

### Header Parameter (/header)
  Reqs/sec    106333.85    9939.15  116254.83
  Latency        0.92ms   287.88us     4.54ms
  Latency Distribution
     50%   837.00us
     75%     1.14ms
     90%     1.44ms
     99%     2.15ms

### Cookie Parameter (/cookie)
  Reqs/sec    107695.55   10336.80  116269.75
  Latency        0.92ms   263.46us     3.65ms
  Latency Distribution
     50%     0.85ms
     75%     1.10ms
     90%     1.35ms
     99%     2.21ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     90434.11    4932.62   95644.06
  Latency        1.09ms   328.59us     5.70ms
  Latency Distribution
     50%     1.01ms
     75%     1.35ms
     90%     1.69ms
     99%     2.52ms

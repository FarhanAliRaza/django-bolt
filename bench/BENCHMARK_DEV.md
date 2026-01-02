# Django-Bolt Benchmark
Generated: Fri Jan  2 11:22:04 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    106385.24 [#/sec] (mean)
Time per request:       0.940 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    87129.26 [#/sec] (mean)
Time per request:       1.148 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    87971.64 [#/sec] (mean)
Time per request:       1.137 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    106491.74 [#/sec] (mean)
Time per request:       0.939 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    105082.86 [#/sec] (mean)
Time per request:       0.952 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    105351.88 [#/sec] (mean)
Time per request:       0.949 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    106602.99 [#/sec] (mean)
Time per request:       0.938 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    105728.36 [#/sec] (mean)
Time per request:       0.946 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    25280.17 [#/sec] (mean)
Time per request:       3.956 [ms] (mean)
Time per request:       0.040 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
Failed requests:        0
Requests per second:    96309.42 [#/sec] (mean)
Time per request:       1.038 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
Failed requests:        0
Requests per second:    18574.14 [#/sec] (mean)
Time per request:       5.384 [ms] (mean)
Time per request:       0.054 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    16914.15 [#/sec] (mean)
Time per request:       5.912 [ms] (mean)
Time per request:       0.059 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    98217.36 [#/sec] (mean)
Time per request:       1.018 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    104648.49 [#/sec] (mean)
Time per request:       0.956 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    105528.65 [#/sec] (mean)
Time per request:       0.948 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15603.01 [#/sec] (mean)
Time per request:       6.409 [ms] (mean)
Time per request:       0.064 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    13368.32 [#/sec] (mean)
Time per request:       7.480 [ms] (mean)
Time per request:       0.075 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    17788.31 [#/sec] (mean)
Time per request:       5.622 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    15345.17 [#/sec] (mean)
Time per request:       6.517 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    107282.32 [#/sec] (mean)
Time per request:       0.932 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    105661.33 [#/sec] (mean)
Time per request:       0.946 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    71850.95 [#/sec] (mean)
Time per request:       1.392 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    104310.09 [#/sec] (mean)
Time per request:       0.959 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    104371.06 [#/sec] (mean)
Time per request:       0.958 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    105736.19 [#/sec] (mean)
Time per request:       0.946 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    105756.32 [#/sec] (mean)
Time per request:       0.946 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    18392.90 [#/sec] (mean)
Time per request:       5.437 [ms] (mean)
Time per request:       0.054 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    88073.14 [#/sec] (mean)
Time per request:       1.135 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    66333.23 [#/sec] (mean)
Time per request:       1.508 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    63708.88 [#/sec] (mean)
Time per request:       1.570 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
Failed requests:        0
Requests per second:    15794.32 [#/sec] (mean)
Time per request:       6.331 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    104709.85 [#/sec] (mean)
Time per request:       0.955 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    104305.74 [#/sec] (mean)
Time per request:       0.959 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    100450.02 [#/sec] (mean)
Time per request:       0.996 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    105408.51 [#/sec] (mean)
Time per request:       0.949 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)

## Latency Percentile Benchmarks (bombardier)
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    124127.91   12421.15  132650.34
  Latency      788.09us   308.67us     4.92ms
  Latency Distribution
     50%   708.00us
     75%     0.95ms
     90%     1.23ms
     99%     2.12ms

### Path Parameter - int (/items/12345)
  Reqs/sec    112974.45    8563.75  120479.29
  Latency        0.85ms   286.56us     4.80ms
  Latency Distribution
     50%   789.00us
     75%     1.03ms
     90%     1.29ms
     99%     2.25ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    111110.28    9125.65  117687.09
  Latency        0.86ms   234.77us     3.79ms
  Latency Distribution
     50%   819.00us
     75%     1.06ms
     90%     1.33ms
     99%     1.93ms

### Header Parameter (/header)
  Reqs/sec    116262.78    9209.08  126112.87
  Latency        0.85ms   261.76us     4.69ms
  Latency Distribution
     50%   799.00us
     75%     1.05ms
     90%     1.31ms
     99%     2.00ms

### Cookie Parameter (/cookie)
  Reqs/sec    112051.30    8670.96  121531.45
  Latency        0.86ms   289.41us     4.16ms
  Latency Distribution
     50%   780.00us
     75%     1.04ms
     90%     1.36ms
     99%     2.33ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     98452.03    6221.05  105361.21
  Latency        1.01ms   300.94us     3.65ms
  Latency Distribution
     50%     0.95ms
     75%     1.26ms
     90%     1.60ms
     99%     2.42ms

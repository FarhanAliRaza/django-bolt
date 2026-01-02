# Django-Bolt Benchmark
Generated: Fri Jan  2 10:46:52 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    103716.15 [#/sec] (mean)
Time per request:       0.964 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    86469.29 [#/sec] (mean)
Time per request:       1.156 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    81574.72 [#/sec] (mean)
Time per request:       1.226 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    105445.19 [#/sec] (mean)
Time per request:       0.948 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    103505.74 [#/sec] (mean)
Time per request:       0.966 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    101633.25 [#/sec] (mean)
Time per request:       0.984 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    105330.79 [#/sec] (mean)
Time per request:       0.949 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    105440.74 [#/sec] (mean)
Time per request:       0.948 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    33976.39 [#/sec] (mean)
Time per request:       2.943 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
Failed requests:        0
Requests per second:    90608.44 [#/sec] (mean)
Time per request:       1.104 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
Failed requests:        0
Requests per second:    18450.90 [#/sec] (mean)
Time per request:       5.420 [ms] (mean)
Time per request:       0.054 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    16684.80 [#/sec] (mean)
Time per request:       5.993 [ms] (mean)
Time per request:       0.060 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    93378.53 [#/sec] (mean)
Time per request:       1.071 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    99478.73 [#/sec] (mean)
Time per request:       1.005 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    101021.33 [#/sec] (mean)
Time per request:       0.990 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15470.30 [#/sec] (mean)
Time per request:       6.464 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    13939.92 [#/sec] (mean)
Time per request:       7.174 [ms] (mean)
Time per request:       0.072 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    16811.22 [#/sec] (mean)
Time per request:       5.948 [ms] (mean)
Time per request:       0.059 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    15365.11 [#/sec] (mean)
Time per request:       6.508 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    103540.03 [#/sec] (mean)
Time per request:       0.966 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    100815.60 [#/sec] (mean)
Time per request:       0.992 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    69894.88 [#/sec] (mean)
Time per request:       1.431 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    100867.46 [#/sec] (mean)
Time per request:       0.991 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    101070.33 [#/sec] (mean)
Time per request:       0.989 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    104904.27 [#/sec] (mean)
Time per request:       0.953 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    102971.77 [#/sec] (mean)
Time per request:       0.971 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    18322.07 [#/sec] (mean)
Time per request:       5.458 [ms] (mean)
Time per request:       0.055 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    82134.85 [#/sec] (mean)
Time per request:       1.218 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    63062.84 [#/sec] (mean)
Time per request:       1.586 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    60343.48 [#/sec] (mean)
Time per request:       1.657 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
Failed requests:        0
Requests per second:    15468.48 [#/sec] (mean)
Time per request:       6.465 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    104095.10 [#/sec] (mean)
Time per request:       0.961 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    103333.54 [#/sec] (mean)
Time per request:       0.968 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    95047.10 [#/sec] (mean)
Time per request:       1.052 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    101555.84 [#/sec] (mean)
Time per request:       0.985 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Latency Percentile Benchmarks (bombardier)
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    117948.92   12126.52  132346.37
  Latency        0.85ms   331.14us     4.93ms
  Latency Distribution
     50%   774.00us
     75%     1.03ms
     90%     1.30ms
     99%     2.33ms

### Path Parameter - int (/items/12345)
  Reqs/sec    107291.89    8612.20  113436.79
  Latency        0.91ms   294.60us     5.74ms
  Latency Distribution
     50%   832.00us
     75%     1.12ms
     90%     1.42ms
     99%     2.21ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    104319.70    9424.19  109091.55
  Latency        0.94ms   280.58us     4.55ms
  Latency Distribution
     50%     0.88ms
     75%     1.16ms
     90%     1.45ms
     99%     2.17ms

### Header Parameter (/header)
  Reqs/sec     97657.91    8170.06  104375.83
  Latency        1.01ms   302.23us     5.07ms
  Latency Distribution
     50%     0.93ms
     75%     1.23ms
     90%     1.57ms
     99%     2.29ms

### Cookie Parameter (/cookie)
  Reqs/sec    105708.72    8209.87  111555.69
  Latency        0.93ms   329.02us     3.71ms
  Latency Distribution
     50%   839.00us
     75%     1.19ms
     90%     1.56ms
     99%     2.50ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     88845.84    3812.94   92824.86
  Latency        1.10ms   345.68us     4.69ms
  Latency Distribution
     50%     1.02ms
     75%     1.33ms
     90%     1.69ms
     99%     2.60ms

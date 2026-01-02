# Django-Bolt Benchmark
Generated: Sat Jan  3 12:45:03 AM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    102464.27 [#/sec] (mean)
Time per request:       0.976 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    86935.35 [#/sec] (mean)
Time per request:       1.150 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    86566.60 [#/sec] (mean)
Time per request:       1.155 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    106484.93 [#/sec] (mean)
Time per request:       0.939 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    106240.57 [#/sec] (mean)
Time per request:       0.941 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    105131.47 [#/sec] (mean)
Time per request:       0.951 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    105085.07 [#/sec] (mean)
Time per request:       0.952 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    107136.35 [#/sec] (mean)
Time per request:       0.933 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    32413.76 [#/sec] (mean)
Time per request:       3.085 [ms] (mean)
Time per request:       0.031 [ms] (mean, across all concurrent requests)

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
Failed requests:        0
Requests per second:    95521.93 [#/sec] (mean)
Time per request:       1.047 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
Failed requests:        0
Requests per second:    18727.50 [#/sec] (mean)
Time per request:       5.340 [ms] (mean)
Time per request:       0.053 [ms] (mean, across all concurrent requests)
### Get User via Dependency (/auth/me-dependency)
Failed requests:        0
Requests per second:    16003.35 [#/sec] (mean)
Time per request:       6.249 [ms] (mean)
Time per request:       0.062 [ms] (mean, across all concurrent requests)
### Get Auth Context (/auth/context) validated jwt no db
Failed requests:        0
Requests per second:    86811.58 [#/sec] (mean)
Time per request:       1.152 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
SEE STREAMING_BENCHMARK_DEV.md

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    104473.56 [#/sec] (mean)
Time per request:       0.957 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    101041.74 [#/sec] (mean)
Time per request:       0.990 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15482.08 [#/sec] (mean)
Time per request:       6.459 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    13411.62 [#/sec] (mean)
Time per request:       7.456 [ms] (mean)
Time per request:       0.075 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    18265.27 [#/sec] (mean)
Time per request:       5.475 [ms] (mean)
Time per request:       0.055 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    15342.53 [#/sec] (mean)
Time per request:       6.518 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    104174.26 [#/sec] (mean)
Time per request:       0.960 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    103628.02 [#/sec] (mean)
Time per request:       0.965 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    73940.43 [#/sec] (mean)
Time per request:       1.352 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    83531.72 [#/sec] (mean)
Time per request:       1.197 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    94496.52 [#/sec] (mean)
Time per request:       1.058 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    96439.46 [#/sec] (mean)
Time per request:       1.037 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    103110.85 [#/sec] (mean)
Time per request:       0.970 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    18337.92 [#/sec] (mean)
Time per request:       5.453 [ms] (mean)
Time per request:       0.055 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    89874.71 [#/sec] (mean)
Time per request:       1.113 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    67135.72 [#/sec] (mean)
Time per request:       1.490 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    62967.93 [#/sec] (mean)
Time per request:       1.588 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
Failed requests:        0
Requests per second:    15711.73 [#/sec] (mean)
Time per request:       6.365 [ms] (mean)
Time per request:       0.064 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    103629.09 [#/sec] (mean)
Time per request:       0.965 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
Failed requests:        0
Requests per second:    104473.56 [#/sec] (mean)
Time per request:       0.957 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
Failed requests:        0
Requests per second:    99284.16 [#/sec] (mean)
Time per request:       1.007 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Users msgspec Serializer (POST /users/bench/msgspec)
Failed requests:        0
Requests per second:    105186.76 [#/sec] (mean)
Time per request:       0.951 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Latency Percentile Benchmarks (bombardier)
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    114993.48    9279.67  123988.04
  Latency      849.15us   422.20us    10.67ms
  Latency Distribution
     50%   736.00us
     75%     1.05ms
     90%     1.43ms
     99%     2.71ms

### Path Parameter - int (/items/12345)
  Reqs/sec    114606.71   11389.13  126070.35
  Latency      844.22us   228.60us     3.37ms
  Latency Distribution
     50%   796.00us
     75%     1.05ms
     90%     1.34ms
     99%     1.89ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    108074.07    8981.53  116073.04
  Latency        0.91ms   352.31us     5.28ms
  Latency Distribution
     50%   812.00us
     75%     1.11ms
     90%     1.48ms
     99%     2.39ms

### Header Parameter (/header)
  Reqs/sec    113784.30   10950.95  119910.36
  Latency      846.83us   221.11us     4.02ms
  Latency Distribution
     50%   790.00us
     75%     1.05ms
     90%     1.29ms
     99%     1.83ms

### Cookie Parameter (/cookie)
  Reqs/sec    113815.63   10164.53  122071.17
  Latency        0.86ms   302.00us     5.29ms
  Latency Distribution
     50%   803.00us
     75%     1.05ms
     90%     1.32ms
     99%     2.09ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     94767.94    5949.11   99103.98
  Latency        1.03ms   354.74us     4.15ms
  Latency Distribution
     50%     0.94ms
     75%     1.28ms
     90%     1.71ms
     99%     2.70ms

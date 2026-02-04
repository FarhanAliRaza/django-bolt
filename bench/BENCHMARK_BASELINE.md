# Django-Bolt Benchmark
Generated: Wed 04 Feb 2026 08:00:32 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec     28234.79    2030.29   31675.86
  Latency        3.51ms     1.05ms    10.53ms
  Latency Distribution
     50%     3.38ms
     75%     4.23ms
     90%     5.18ms
     99%     7.13ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     20860.55    4605.01   27125.70
  Latency        4.76ms     2.23ms    20.71ms
  Latency Distribution
     50%     4.30ms
     75%     5.74ms
     90%     7.59ms
     99%    13.72ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     25444.75    1450.41   28498.63
  Latency        3.90ms     1.35ms    12.61ms
  Latency Distribution
     50%     3.69ms
     75%     4.78ms
     90%     6.00ms
     99%     8.85ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     27079.15    1938.40   30106.35
  Latency        3.67ms     1.11ms     9.77ms
  Latency Distribution
     50%     3.60ms
     75%     4.46ms
     90%     5.45ms
     99%     7.25ms
### Cookie Endpoint (/cookie)
  Reqs/sec     27943.84    1628.13   30474.27
  Latency        3.54ms     1.20ms    10.78ms
  Latency Distribution
     50%     3.35ms
     75%     4.35ms
     90%     5.51ms
     99%     7.87ms
### Exception Endpoint (/exc)
  Reqs/sec     25447.24    1817.97   28271.63
  Latency        3.89ms     1.41ms    13.63ms
  Latency Distribution
     50%     3.73ms
     75%     4.76ms
     90%     6.05ms
     99%     8.97ms
### HTML Response (/html)
  Reqs/sec     28326.94    2658.26   34672.11
  Latency        3.53ms     1.10ms    11.22ms
  Latency Distribution
     50%     3.42ms
     75%     4.30ms
     90%     5.28ms
     99%     7.26ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     14419.55    2651.17   16731.42
  Latency        6.92ms     2.63ms    33.46ms
  Latency Distribution
     50%     6.41ms
     75%     8.14ms
     90%    10.22ms
     99%    16.32ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     21026.66    1903.87   27547.58
  Latency        4.79ms     1.55ms    15.71ms
  Latency Distribution
     50%     4.50ms
     75%     5.88ms
     90%     7.00ms
     99%    10.49ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     11182.56    1246.73   17105.20
  Latency        8.99ms     2.45ms    20.98ms
  Latency Distribution
     50%     8.79ms
     75%    10.86ms
     90%    12.65ms
     99%    16.39ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     10374.22     819.01   12186.12
  Latency        9.61ms     2.61ms    22.52ms
  Latency Distribution
     50%     9.27ms
     75%    11.37ms
     90%    13.53ms
     99%    17.79ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     20959.90    1549.01   23973.51
  Latency        4.75ms     1.48ms    13.58ms
  Latency Distribution
     50%     4.41ms
     75%     5.72ms
     90%     7.14ms
     99%    10.22ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     28181.09    1426.14   30415.44
  Latency        3.50ms     1.06ms    10.50ms
  Latency Distribution
     50%     3.35ms
     75%     4.22ms
     90%     5.22ms
     99%     7.30ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     26589.40    1328.42   29606.19
  Latency        3.72ms     1.15ms    14.04ms
  Latency Distribution
     50%     3.46ms
     75%     4.41ms
     90%     5.44ms
     99%     8.01ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     10769.58    1132.51   13247.84
  Latency        9.26ms     3.66ms    28.77ms
  Latency Distribution
     50%     8.55ms
     75%    11.35ms
     90%    14.70ms
     99%    21.41ms
### Users Full10 (Sync) (/users/sync-full10)
 0 / 10000 [-------------------------------------------------------]   0.00% 1995 / 10000 [========>------------------------------------]  19.95% 9948/s 4050 / 10000 [=================>--------------------------]  40.50% 10107/s 6047 / 10000 [==========================>-----------------]  60.47% 10059/s 7975 / 10000 [===================================>---------]  79.75% 9952/s 9725 / 10000 [===========================================>-]  97.25% 9710/s 10000 / 10000 [============================================] 100.00% 8316/s 10000 / 10000 [=========================================] 100.00% 8315/s 1s
  Reqs/sec      9682.45     988.08   11761.66
  Latency       10.27ms     3.19ms    29.45ms
  Latency Distribution
     50%     9.93ms
     75%    12.33ms
     90%    14.84ms
     99%    19.93ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     11589.14    1227.44   16227.05
  Latency        8.64ms     2.98ms    21.97ms
  Latency Distribution
     50%     8.12ms
     75%    10.51ms
     90%    13.12ms
     99%    18.11ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     10551.98    1116.81   12814.27
  Latency        9.44ms     4.82ms    35.10ms
  Latency Distribution
     50%     8.35ms
     75%    12.51ms
     90%    16.60ms
     99%    24.89ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec     30618.78    2481.78   34282.40
  Latency        3.24ms     0.97ms    10.12ms
  Latency Distribution
     50%     2.97ms
     75%     3.91ms
     90%     4.77ms
     99%     6.95ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     28555.46    1754.58   31280.81
  Latency        3.48ms     1.31ms    11.13ms
  Latency Distribution
     50%     3.18ms
     75%     4.50ms
     90%     5.56ms
     99%     8.07ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     25396.28    2840.73   35915.86
  Latency        4.00ms     1.34ms    11.32ms
  Latency Distribution
     50%     3.88ms
     75%     4.94ms
     90%     6.16ms
     99%     8.57ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     27763.91    1858.46   30677.97
  Latency        3.57ms     1.13ms    10.49ms
  Latency Distribution
     50%     3.35ms
     75%     4.42ms
     90%     5.44ms
     99%     7.53ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     25799.36    1373.27   28197.13
  Latency        3.85ms     1.13ms    11.06ms
  Latency Distribution
     50%     3.69ms
     75%     4.57ms
     90%     5.60ms
     99%     7.74ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     27887.75    1455.16   30196.55
  Latency        3.56ms     1.12ms    12.11ms
  Latency Distribution
     50%     3.36ms
     75%     4.32ms
     90%     5.28ms
     99%     7.75ms
### CBV Response Types (/cbv-response)
  Reqs/sec     29289.05    3150.86   39737.25
  Latency        3.43ms     1.28ms    11.21ms
  Latency Distribution
     50%     3.17ms
     75%     4.21ms
     90%     5.43ms
     99%     8.30ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     12071.90    1312.54   14350.32
  Latency        8.27ms     2.35ms    22.35ms
  Latency Distribution
     50%     7.86ms
     75%     9.74ms
     90%    11.83ms
     99%    15.95ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     25580.11    1721.84   28478.54
  Latency        3.86ms     1.18ms    11.93ms
  Latency Distribution
     50%     3.70ms
     75%     4.64ms
     90%     5.72ms
     99%     7.75ms
### File Upload (POST /upload)
  Reqs/sec     20561.20    1548.19   22792.62
  Latency        4.77ms     1.45ms    13.93ms
  Latency Distribution
     50%     4.59ms
     75%     5.67ms
     90%     7.06ms
     99%     9.67ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     19719.72    1244.01   21662.96
  Latency        5.01ms     1.41ms    15.07ms
  Latency Distribution
     50%     4.73ms
     75%     5.82ms
     90%     7.16ms
     99%    10.01ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      7050.47     816.28    9932.70
  Latency       14.19ms     4.02ms    33.43ms
  Latency Distribution
     50%    13.58ms
     75%    17.07ms
     90%    20.22ms
     99%    26.03ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     28040.09    1988.85   31036.68
  Latency        3.54ms     1.25ms    11.95ms
  Latency Distribution
     50%     3.37ms
     75%     4.44ms
     90%     5.61ms
     99%     7.72ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     28939.58    6455.35   54430.12
  Latency        3.60ms     1.04ms     9.45ms
  Latency Distribution
     50%     3.43ms
     75%     4.35ms
     90%     5.32ms
     99%     7.24ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     26628.87    1728.56   29113.12
  Latency        3.71ms     1.43ms    13.69ms
  Latency Distribution
     50%     3.36ms
     75%     4.58ms
     90%     5.95ms
     99%     9.17ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     27788.39    1681.84   30055.11
  Latency        3.57ms     1.17ms    14.08ms
  Latency Distribution
     50%     3.44ms
     75%     4.36ms
     90%     5.46ms
     99%     7.65ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec     32243.99    1767.79   34275.96
  Latency        3.08ms     0.90ms     9.45ms
  Latency Distribution
     50%     2.95ms
     75%     3.74ms
     90%     4.54ms
     99%     6.27ms

### Path Parameter - int (/items/12345)
  Reqs/sec     28342.35    1964.69   30480.94
  Latency        3.51ms     1.09ms    10.30ms
  Latency Distribution
     50%     3.29ms
     75%     4.28ms
     90%     5.27ms
     99%     7.40ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec     27085.84    2414.39   29291.14
  Latency        3.61ms     1.24ms    10.89ms
  Latency Distribution
     50%     3.52ms
     75%     4.54ms
     90%     5.59ms
     99%     7.76ms

### Header Parameter (/header)
  Reqs/sec     29884.85    4621.91   47652.91
  Latency        3.42ms     1.09ms     9.72ms
  Latency Distribution
     50%     3.29ms
     75%     4.22ms
     90%     5.24ms
     99%     7.21ms

### Cookie Parameter (/cookie)
  Reqs/sec     29326.74    1434.69   31629.68
  Latency        3.38ms     0.88ms     8.71ms
  Latency Distribution
     50%     3.30ms
     75%     3.99ms
     90%     4.80ms
     99%     6.39ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     19689.65    1799.94   22160.64
  Latency        5.05ms     2.06ms    17.32ms
  Latency Distribution
     50%     4.56ms
     75%     6.17ms
     90%     7.99ms
     99%    12.80ms

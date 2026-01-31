# Django-Bolt Benchmark
Generated: Sat 31 Jan 2026 11:03:58 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    109635.39   10759.89  120050.70
  Latency        0.91ms   322.84us     4.89ms
  Latency Distribution
     50%   836.00us
     75%     1.11ms
     90%     1.38ms
     99%     2.24ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     86781.76    6099.23   92752.58
  Latency        1.13ms   380.37us     5.81ms
  Latency Distribution
     50%     1.06ms
     75%     1.35ms
     90%     1.69ms
     99%     2.84ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     83994.45    5206.01   89065.03
  Latency        1.17ms   404.15us     5.79ms
  Latency Distribution
     50%     1.08ms
     75%     1.41ms
     90%     1.79ms
     99%     2.71ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    103148.02    8327.60  109933.99
  Latency        0.95ms   299.86us     4.23ms
  Latency Distribution
     50%     0.88ms
     75%     1.16ms
     90%     1.44ms
     99%     2.23ms
### Cookie Endpoint (/cookie)
  Reqs/sec    100256.42    6530.32  108335.99
  Latency        0.98ms   333.85us     4.66ms
  Latency Distribution
     50%     0.91ms
     75%     1.19ms
     90%     1.49ms
     99%     2.51ms
### Exception Endpoint (/exc)
  Reqs/sec    100768.05    9054.76  106062.00
  Latency        0.97ms   320.72us     6.62ms
  Latency Distribution
     50%     0.91ms
     75%     1.22ms
     90%     1.52ms
     99%     2.30ms
### HTML Response (/html)
  Reqs/sec    107354.14    8652.08  113949.29
  Latency        0.92ms   315.15us     5.34ms
  Latency Distribution
     50%     0.85ms
     75%     1.11ms
     90%     1.41ms
     99%     2.20ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
 0 / 10000 [--------------------------------------------------------------]   0.00% 6075 / 10000 [==============================>--------------------]  60.75% 30302/s 10000 / 10000 [==================================================] 100.00% 24914/s 10000 / 10000 [===============================================] 100.00% 24909/s 0s
  Reqs/sec     32893.98    7752.23   40988.41
  Latency        3.07ms     1.77ms    23.05ms
  Latency Distribution
     50%     2.63ms
     75%     3.66ms
     90%     5.03ms
     99%    10.22ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     75851.83    5035.65   80888.43
  Latency        1.30ms   418.05us     5.26ms
  Latency Distribution
     50%     1.20ms
     75%     1.59ms
     90%     2.00ms
     99%     3.02ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     16803.34    2005.34   19646.51
  Latency        5.93ms     1.32ms    16.71ms
  Latency Distribution
     50%     5.81ms
     75%     6.67ms
     90%     7.63ms
     99%    11.04ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15695.12     978.84   16841.21
  Latency        6.33ms     1.82ms    15.34ms
  Latency Distribution
     50%     6.09ms
     75%     7.76ms
     90%     9.22ms
     99%    12.03ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     83363.98    7409.40   93059.57
  Latency        1.17ms   367.52us     5.26ms
  Latency Distribution
     50%     1.09ms
     75%     1.45ms
     90%     1.85ms
     99%     2.64ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    100786.50   10861.69  116713.12
  Latency        1.00ms   362.56us     4.80ms
  Latency Distribution
     50%     0.92ms
     75%     1.24ms
     90%     1.55ms
     99%     2.60ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     99303.65    9751.52  106497.86
  Latency        0.99ms   297.91us     4.76ms
  Latency Distribution
     50%     0.91ms
     75%     1.22ms
     90%     1.56ms
     99%     2.31ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     14661.63    1214.79   16401.42
  Latency        6.80ms     2.08ms    20.70ms
  Latency Distribution
     50%     6.72ms
     75%     8.37ms
     90%     9.85ms
     99%    13.06ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     13147.15    1168.50   15081.05
  Latency        7.58ms     2.15ms    20.48ms
  Latency Distribution
     50%     7.39ms
     75%     9.19ms
     90%    10.80ms
     99%    13.87ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     16748.45     941.19   18671.04
  Latency        5.91ms     1.91ms    17.73ms
  Latency Distribution
     50%     5.58ms
     75%     7.22ms
     90%     8.91ms
     99%    12.28ms
### Users Mini10 (Sync) (/users/sync-mini10)
 0 / 10000 [--------------------------------------------------------------]   0.00% 2782 / 10000 [==============>------------------------------------]  27.82% 13833/s 5765 / 10000 [=============================>---------------------]  57.65% 14365/s 8790 / 10000 [============================================>------]  87.90% 14614/s 10000 / 10000 [==================================================] 100.00% 12463/s 10000 / 10000 [===============================================] 100.00% 12462/s 0s
  Reqs/sec     14591.20    1687.65   18210.94
  Latency        6.82ms     3.13ms    24.14ms
  Latency Distribution
     50%     6.05ms
     75%     8.60ms
     90%    11.71ms
     99%    17.79ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    105489.28    7126.74  111562.14
  Latency        0.93ms   334.58us     4.51ms
  Latency Distribution
     50%   839.00us
     75%     1.18ms
     90%     1.57ms
     99%     2.47ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     99468.86    7243.41  107334.41
  Latency        0.98ms   362.98us     5.20ms
  Latency Distribution
     50%     0.91ms
     75%     1.19ms
     90%     1.52ms
     99%     2.37ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     67141.58    4371.97   72025.47
  Latency        1.47ms   425.00us     5.71ms
  Latency Distribution
     50%     1.37ms
     75%     1.71ms
     90%     2.12ms
     99%     3.38ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     95892.13    8071.97  110475.79
  Latency        1.05ms   368.21us     4.72ms
  Latency Distribution
     50%     0.96ms
     75%     1.30ms
     90%     1.71ms
     99%     2.73ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     90710.70    6038.03  101442.62
  Latency        1.08ms   365.16us     5.75ms
  Latency Distribution
     50%     1.00ms
     75%     1.34ms
     90%     1.70ms
     99%     2.57ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     95265.75    8262.41  106605.23
  Latency        1.02ms   331.92us     5.38ms
  Latency Distribution
     50%     0.96ms
     75%     1.25ms
     90%     1.59ms
     99%     2.32ms
### CBV Response Types (/cbv-response)
  Reqs/sec     98174.77    7868.74  106726.15
  Latency        1.00ms   385.89us     6.64ms
  Latency Distribution
     50%     0.90ms
     75%     1.25ms
     90%     1.65ms
     99%     2.72ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16951.02    1388.64   18983.22
  Latency        5.87ms     2.10ms    17.40ms
  Latency Distribution
     50%     5.48ms
     75%     7.48ms
     90%     9.20ms
     99%    12.82ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     90163.96    8736.41   98529.21
  Latency        1.09ms   445.79us     6.12ms
  Latency Distribution
     50%     1.00ms
     75%     1.31ms
     90%     1.66ms
     99%     2.82ms
### File Upload (POST /upload)
  Reqs/sec     80537.70    7104.00   88703.59
  Latency        1.23ms   436.75us     6.07ms
  Latency Distribution
     50%     1.13ms
     75%     1.52ms
     90%     1.95ms
     99%     3.15ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     74274.76    5062.19   77786.16
  Latency        1.32ms   577.00us     7.12ms
  Latency Distribution
     50%     1.20ms
     75%     1.66ms
     90%     2.20ms
     99%     3.68ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9073.77    1267.49   14204.56
  Latency       11.06ms     3.27ms    25.64ms
  Latency Distribution
     50%    10.45ms
     75%    12.77ms
     90%    16.35ms
     99%    21.07ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     91066.82    4928.93   96151.76
  Latency        1.07ms   360.81us     4.61ms
  Latency Distribution
     50%     0.99ms
     75%     1.33ms
     90%     1.67ms
     99%     2.69ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     89615.53    4387.89   95191.67
  Latency        1.10ms   449.75us     6.38ms
  Latency Distribution
     50%     1.00ms
     75%     1.30ms
     90%     1.74ms
     99%     3.16ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     83083.81    6292.78   90482.91
  Latency        1.19ms   400.41us     5.56ms
  Latency Distribution
     50%     1.09ms
     75%     1.44ms
     90%     1.79ms
     99%     3.07ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     93937.56    5860.27  100957.81
  Latency        1.05ms   342.25us     6.71ms
  Latency Distribution
     50%     0.97ms
     75%     1.30ms
     90%     1.65ms
     99%     2.54ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    101778.62    8293.91  110456.86
  Latency        0.96ms   308.83us     4.18ms
  Latency Distribution
     50%     0.89ms
     75%     1.17ms
     90%     1.48ms
     99%     2.48ms

### Path Parameter - int (/items/12345)
  Reqs/sec     90423.64   12157.91  106220.29
  Latency        1.06ms   442.80us     6.45ms
  Latency Distribution
     50%     0.96ms
     75%     1.29ms
     90%     1.69ms
     99%     3.06ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec     94428.37    6235.82  103319.50
  Latency        1.04ms   405.80us     4.74ms
  Latency Distribution
     50%     0.93ms
     75%     1.27ms
     90%     1.71ms
     99%     2.99ms

### Header Parameter (/header)
  Reqs/sec     91100.90   13889.07  102673.81
  Latency        1.03ms   349.65us     7.53ms
  Latency Distribution
     50%     0.95ms
     75%     1.27ms
     90%     1.59ms
     99%     2.31ms

### Cookie Parameter (/cookie)
  Reqs/sec     94115.28    8613.41  107198.26
  Latency        1.06ms   369.14us     4.85ms
  Latency Distribution
     50%     0.98ms
     75%     1.30ms
     90%     1.67ms
     99%     2.76ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     75639.82    6579.29   82624.95
  Latency        1.28ms   494.71us     6.55ms
  Latency Distribution
     50%     1.16ms
     75%     1.58ms
     90%     2.06ms
     99%     3.37ms

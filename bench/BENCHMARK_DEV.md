# Django-Bolt Benchmark
Generated: Tue 03 Feb 2026 10:27:23 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    105015.79    6122.30  111119.94
  Latency        0.93ms   270.76us     4.21ms
  Latency Distribution
     50%     0.87ms
     75%     1.17ms
     90%     1.50ms
     99%     2.15ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     78694.85    3669.26   83182.22
  Latency        1.25ms   436.38us     5.02ms
  Latency Distribution
     50%     1.16ms
     75%     1.51ms
     90%     1.93ms
     99%     3.40ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     84228.99    9164.42   99033.23
  Latency        1.20ms   409.66us     5.22ms
  Latency Distribution
     50%     1.12ms
     75%     1.50ms
     90%     1.88ms
     99%     2.84ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     99492.21    6470.85  104412.86
  Latency        0.99ms   316.17us     4.28ms
  Latency Distribution
     50%     0.92ms
     75%     1.20ms
     90%     1.56ms
     99%     2.35ms
### Cookie Endpoint (/cookie)
  Reqs/sec     98603.80    7302.40  109057.25
  Latency        1.02ms   368.74us     5.34ms
  Latency Distribution
     50%     0.93ms
     75%     1.25ms
     90%     1.60ms
     99%     2.56ms
### Exception Endpoint (/exc)
  Reqs/sec     90912.37    4482.05   96716.48
  Latency        1.08ms   437.17us     5.30ms
  Latency Distribution
     50%     0.99ms
     75%     1.32ms
     90%     1.70ms
     99%     3.32ms
### HTML Response (/html)
  Reqs/sec    106475.19    9008.55  114861.18
  Latency        0.92ms   322.32us     5.77ms
  Latency Distribution
     50%     0.86ms
     75%     1.12ms
     90%     1.40ms
     99%     2.15ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     31501.68    6542.40   36917.14
  Latency        3.17ms     1.62ms    22.42ms
  Latency Distribution
     50%     2.82ms
     75%     3.82ms
     90%     4.80ms
     99%     8.89ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     79937.00    4512.68   83015.32
  Latency        1.23ms   356.94us     4.62ms
  Latency Distribution
     50%     1.15ms
     75%     1.49ms
     90%     1.89ms
     99%     2.88ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     19567.94   13210.98   89181.21
  Latency        5.79ms     1.24ms    14.17ms
  Latency Distribution
     50%     5.65ms
     75%     6.73ms
     90%     7.73ms
     99%     9.57ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15147.51     888.53   16838.80
  Latency        6.57ms     1.05ms    13.47ms
  Latency Distribution
     50%     6.56ms
     75%     7.39ms
     90%     8.19ms
     99%     9.83ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     85174.44    7029.40   91380.17
  Latency        1.16ms   394.75us     5.95ms
  Latency Distribution
     50%     1.06ms
     75%     1.45ms
     90%     1.84ms
     99%     2.74ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    100995.31    6971.89  106616.30
  Latency        0.97ms   323.93us     5.57ms
  Latency Distribution
     50%     0.91ms
     75%     1.17ms
     90%     1.46ms
     99%     2.15ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     90288.30    5933.82   95519.84
  Latency        1.09ms   347.93us     5.45ms
  Latency Distribution
     50%     1.01ms
     75%     1.34ms
     90%     1.71ms
     99%     2.62ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13733.13    1050.47   15029.20
  Latency        7.19ms     1.86ms    18.64ms
  Latency Distribution
     50%     7.14ms
     75%     8.44ms
     90%    10.45ms
     99%    12.23ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     11998.29    1033.12   13470.20
  Latency        8.20ms     2.22ms    18.23ms
  Latency Distribution
     50%     7.81ms
     75%     9.70ms
     90%    12.48ms
     99%    14.40ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     15990.90     807.59   17657.60
  Latency        6.23ms     1.73ms    13.55ms
  Latency Distribution
     50%     6.08ms
     75%     7.55ms
     90%     9.40ms
     99%    11.22ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13193.79    1157.01   15641.60
  Latency        7.54ms     3.36ms    26.48ms
  Latency Distribution
     50%     6.73ms
     75%     9.53ms
     90%    12.91ms
     99%    18.42ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    108671.32   10763.54  116516.83
  Latency        0.91ms   313.13us     4.49ms
  Latency Distribution
     50%     0.85ms
     75%     1.11ms
     90%     1.39ms
     99%     2.23ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    101834.61    7478.79  106119.23
  Latency        0.97ms   319.21us     4.91ms
  Latency Distribution
     50%     0.89ms
     75%     1.20ms
     90%     1.51ms
     99%     2.26ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     66560.18    5106.44   69765.22
  Latency        1.48ms   398.68us     6.00ms
  Latency Distribution
     50%     1.42ms
     75%     1.76ms
     90%     2.17ms
     99%     3.07ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     90233.93   18287.88  102797.01
  Latency        1.01ms   316.70us     5.64ms
  Latency Distribution
     50%     0.94ms
     75%     1.26ms
     90%     1.57ms
     99%     2.32ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     93839.10    6259.93   99266.91
  Latency        1.03ms   326.17us     5.11ms
  Latency Distribution
     50%     0.95ms
     75%     1.27ms
     90%     1.62ms
     99%     2.46ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     98618.71    8696.76  104149.72
  Latency        0.99ms   291.72us     5.44ms
  Latency Distribution
     50%     0.93ms
     75%     1.22ms
     90%     1.50ms
     99%     2.18ms
### CBV Response Types (/cbv-response)
  Reqs/sec    101120.63   10219.27  108014.82
  Latency        0.95ms   265.80us     4.18ms
  Latency Distribution
     50%     0.90ms
     75%     1.18ms
     90%     1.49ms
     99%     2.15ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16220.04    1152.19   16868.21
  Latency        6.12ms     2.06ms    17.16ms
  Latency Distribution
     50%     5.87ms
     75%     7.94ms
     90%     9.96ms
     99%    11.46ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     97551.95    8484.92  107804.86
  Latency        1.03ms   320.22us     4.46ms
  Latency Distribution
     50%     0.96ms
     75%     1.25ms
     90%     1.57ms
     99%     2.42ms
### File Upload (POST /upload)
  Reqs/sec     84420.11    5619.21   89273.59
  Latency        1.16ms   373.39us     5.68ms
  Latency Distribution
     50%     1.10ms
     75%     1.46ms
     90%     1.84ms
     99%     2.68ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     84375.17    4356.90   87809.33
  Latency        1.16ms   338.79us     5.85ms
  Latency Distribution
     50%     1.09ms
     75%     1.41ms
     90%     1.77ms
     99%     2.62ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9323.01     856.76   11568.28
  Latency       10.70ms     2.62ms    23.18ms
  Latency Distribution
     50%     9.80ms
     75%    12.26ms
     90%    15.24ms
     99%    19.28ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     99131.06    7298.34  102908.28
  Latency        0.99ms   318.99us     5.00ms
  Latency Distribution
     50%     0.92ms
     75%     1.24ms
     90%     1.58ms
     99%     2.28ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     95155.31    8001.62  102953.00
  Latency        1.01ms   313.76us     4.89ms
  Latency Distribution
     50%     0.94ms
     75%     1.26ms
     90%     1.59ms
     99%     2.32ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     85837.37    4880.95   89348.02
  Latency        1.15ms   379.11us     4.72ms
  Latency Distribution
     50%     1.05ms
     75%     1.43ms
     90%     1.87ms
     99%     2.81ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    170686.73  181436.25  540979.17
  Latency        1.02ms   278.52us     4.26ms
  Latency Distribution
     50%     0.96ms
     75%     1.25ms
     90%     1.54ms
     99%     2.24ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    110207.62    9101.52  116779.55
  Latency        0.90ms   321.46us     4.32ms
  Latency Distribution
     50%   815.00us
     75%     1.11ms
     90%     1.45ms
     99%     2.34ms

### Path Parameter - int (/items/12345)
  Reqs/sec    103796.24    6209.90  108173.94
  Latency        0.95ms   288.67us     4.54ms
  Latency Distribution
     50%     0.89ms
     75%     1.15ms
     90%     1.46ms
     99%     2.20ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    100839.01    8271.08  107627.58
  Latency        0.97ms   330.52us     4.25ms
  Latency Distribution
     50%     0.89ms
     75%     1.21ms
     90%     1.53ms
     99%     2.46ms

### Header Parameter (/header)
  Reqs/sec     99136.75    6672.20  107634.89
  Latency        0.99ms   293.94us     5.53ms
  Latency Distribution
     50%     0.94ms
     75%     1.21ms
     90%     1.51ms
     99%     2.21ms

### Cookie Parameter (/cookie)
  Reqs/sec    101702.53    6553.88  105293.94
  Latency        0.97ms   345.74us     5.39ms
  Latency Distribution
     50%     0.88ms
     75%     1.18ms
     90%     1.54ms
     99%     2.35ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     85366.83    5035.26   89275.29
  Latency        1.15ms   332.71us     6.03ms
  Latency Distribution
     50%     1.09ms
     75%     1.43ms
     90%     1.77ms
     99%     2.49ms

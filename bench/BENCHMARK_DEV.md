# Django-Bolt Benchmark
Generated: Wed 04 Feb 2026 08:47:25 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    111908.02    7614.01  119279.72
  Latency        0.89ms   290.37us     4.11ms
  Latency Distribution
     50%   819.00us
     75%     1.07ms
     90%     1.36ms
     99%     2.35ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     87445.34    5999.10   90609.09
  Latency        1.13ms   338.12us     4.73ms
  Latency Distribution
     50%     1.06ms
     75%     1.37ms
     90%     1.73ms
     99%     2.56ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     89565.25    6333.09   96644.15
  Latency        1.10ms   366.94us     4.63ms
  Latency Distribution
     50%     1.00ms
     75%     1.34ms
     90%     1.71ms
     99%     2.83ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    102382.36    6738.06  107253.29
  Latency        0.96ms   304.00us     3.92ms
  Latency Distribution
     50%     0.88ms
     75%     1.20ms
     90%     1.55ms
     99%     2.27ms
### Cookie Endpoint (/cookie)
  Reqs/sec    103651.87    8429.06  111418.33
  Latency        0.95ms   307.14us     4.60ms
  Latency Distribution
     50%     0.89ms
     75%     1.14ms
     90%     1.47ms
     99%     2.28ms
### Exception Endpoint (/exc)
  Reqs/sec     98023.16    9365.55  113085.16
  Latency        1.03ms   395.48us     6.58ms
  Latency Distribution
     50%     0.95ms
     75%     1.25ms
     90%     1.61ms
     99%     2.59ms
### HTML Response (/html)
  Reqs/sec    101324.05    6518.78  111709.37
  Latency        0.97ms   342.61us     4.82ms
  Latency Distribution
     50%     0.89ms
     75%     1.18ms
     90%     1.53ms
     99%     2.50ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     31529.96    6289.61   36793.72
  Latency        3.18ms     1.75ms    24.95ms
  Latency Distribution
     50%     2.73ms
     75%     3.90ms
     90%     5.38ms
     99%     8.88ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     77752.90    4606.73   82402.53
  Latency        1.26ms   425.71us     4.87ms
  Latency Distribution
     50%     1.17ms
     75%     1.54ms
     90%     2.03ms
     99%     3.20ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17615.71    1414.66   19075.74
  Latency        5.64ms     1.10ms    13.33ms
  Latency Distribution
     50%     5.45ms
     75%     6.44ms
     90%     7.48ms
     99%     9.01ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15734.86     891.28   16946.94
  Latency        6.31ms     2.25ms    15.22ms
  Latency Distribution
     50%     6.38ms
     75%     8.08ms
     90%     9.75ms
     99%    12.60ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     82172.38    4665.46   86961.72
  Latency        1.20ms   438.89us     4.67ms
  Latency Distribution
     50%     1.10ms
     75%     1.50ms
     90%     1.94ms
     99%     3.09ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     93506.89    6621.29   98707.38
  Latency        1.06ms   371.91us     5.81ms
  Latency Distribution
     50%     0.99ms
     75%     1.32ms
     90%     1.66ms
     99%     2.62ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     93829.44    5416.64   99184.42
  Latency        1.05ms   370.21us     4.56ms
  Latency Distribution
     50%     0.95ms
     75%     1.32ms
     90%     1.67ms
     99%     2.82ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     14689.69    1134.77   15502.75
  Latency        6.76ms     2.34ms    19.29ms
  Latency Distribution
     50%     6.49ms
     75%     8.68ms
     90%    10.46ms
     99%    13.48ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     13208.13     737.22   14632.45
  Latency        7.53ms     2.42ms    20.30ms
  Latency Distribution
     50%     7.15ms
     75%     8.92ms
     90%    11.25ms
     99%    15.39ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     16992.32     950.92   18630.25
  Latency        5.86ms     1.88ms    14.43ms
  Latency Distribution
     50%     5.89ms
     75%     7.38ms
     90%     8.68ms
     99%    11.48ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13767.28    1322.77   16187.74
  Latency        7.21ms     3.41ms    27.83ms
  Latency Distribution
     50%     6.45ms
     75%     9.08ms
     90%    12.28ms
     99%    18.93ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    108307.26    8990.98  114838.64
  Latency        0.91ms   327.45us     6.46ms
  Latency Distribution
     50%   840.00us
     75%     1.12ms
     90%     1.43ms
     99%     2.22ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     92538.13   14268.55  102928.59
  Latency        1.00ms   372.27us     4.97ms
  Latency Distribution
     50%     0.92ms
     75%     1.26ms
     90%     1.65ms
     99%     2.62ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     68823.11    5145.34   74057.94
  Latency        1.44ms   415.09us     5.24ms
  Latency Distribution
     50%     1.38ms
     75%     1.72ms
     90%     2.13ms
     99%     3.18ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    100264.00   10000.32  118115.87
  Latency        1.02ms   325.92us     4.53ms
  Latency Distribution
     50%     0.96ms
     75%     1.29ms
     90%     1.60ms
     99%     2.36ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     93602.92    9340.30  104172.00
  Latency        1.07ms   334.83us     4.58ms
  Latency Distribution
     50%     1.00ms
     75%     1.33ms
     90%     1.66ms
     99%     2.51ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     93898.23    7624.49  105267.25
  Latency        1.05ms   379.49us     5.62ms
  Latency Distribution
     50%     0.97ms
     75%     1.31ms
     90%     1.70ms
     99%     2.71ms
### CBV Response Types (/cbv-response)
  Reqs/sec    103936.12    8125.86  113459.84
  Latency        0.94ms   322.99us     4.61ms
  Latency Distribution
     50%     0.87ms
     75%     1.15ms
     90%     1.48ms
     99%     2.34ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     17251.98    1272.04   18617.36
  Latency        5.77ms     1.76ms    15.21ms
  Latency Distribution
     50%     5.56ms
     75%     6.96ms
     90%     8.45ms
     99%    11.52ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     91378.65    7278.36  100627.28
  Latency        1.07ms   408.31us     4.93ms
  Latency Distribution
     50%     0.97ms
     75%     1.32ms
     90%     1.72ms
     99%     2.95ms
### File Upload (POST /upload)
  Reqs/sec     79496.45    5533.40   84560.18
  Latency        1.25ms   441.48us     5.49ms
  Latency Distribution
     50%     1.17ms
     75%     1.55ms
     90%     1.92ms
     99%     3.24ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     75621.42    6125.97   81482.30
  Latency        1.31ms   462.64us     5.58ms
  Latency Distribution
     50%     1.21ms
     75%     1.63ms
     90%     2.09ms
     99%     3.30ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9754.40    1130.31   11184.47
  Latency       10.18ms     3.09ms    22.82ms
  Latency Distribution
     50%    10.73ms
     75%    12.51ms
     90%    14.04ms
     99%    17.93ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     91876.65    7838.83  100854.62
  Latency        1.07ms   402.43us     4.98ms
  Latency Distribution
     50%     0.99ms
     75%     1.31ms
     90%     1.70ms
     99%     2.94ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     94350.00    9761.76  105779.66
  Latency        1.06ms   345.87us     4.15ms
  Latency Distribution
     50%     0.98ms
     75%     1.29ms
     90%     1.64ms
     99%     2.67ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     83865.89    8268.19   92829.75
  Latency        1.17ms   436.41us     6.90ms
  Latency Distribution
     50%     1.08ms
     75%     1.41ms
     90%     1.80ms
     99%     3.13ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     98100.85    8356.28  106094.31
  Latency        1.01ms   335.54us     4.96ms
  Latency Distribution
     50%     0.95ms
     75%     1.24ms
     90%     1.59ms
     99%     2.53ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    113541.94    9428.32  120114.94
  Latency        0.87ms   312.36us     4.92ms
  Latency Distribution
     50%   819.00us
     75%     1.05ms
     90%     1.29ms
     99%     2.10ms

### Path Parameter - int (/items/12345)
  Reqs/sec    104808.34    7489.29  110756.11
  Latency        0.93ms   342.88us     5.49ms
  Latency Distribution
     50%     0.87ms
     75%     1.15ms
     90%     1.47ms
     99%     2.31ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    103933.94    7075.36  109715.18
  Latency        0.94ms   259.56us     3.88ms
  Latency Distribution
     50%     0.88ms
     75%     1.17ms
     90%     1.47ms
     99%     2.08ms

### Header Parameter (/header)
  Reqs/sec    101854.05    8129.61  107807.94
  Latency        0.97ms   333.17us     5.71ms
  Latency Distribution
     50%     0.90ms
     75%     1.18ms
     90%     1.51ms
     99%     2.18ms

### Cookie Parameter (/cookie)
  Reqs/sec    104448.47    6594.86  108962.45
  Latency        0.94ms   270.87us     4.84ms
  Latency Distribution
     50%     0.88ms
     75%     1.14ms
     90%     1.41ms
     99%     2.15ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     87295.80    5271.28   90752.84
  Latency        1.13ms   358.97us     4.37ms
  Latency Distribution
     50%     1.05ms
     75%     1.40ms
     90%     1.74ms
     99%     2.75ms

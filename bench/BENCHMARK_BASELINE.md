# Django-Bolt Benchmark
Generated: Wed 04 Feb 2026 10:23:41 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    107015.51    8967.76  114400.64
  Latency        0.92ms   356.29us     5.16ms
  Latency Distribution
     50%   843.00us
     75%     1.11ms
     90%     1.39ms
     99%     2.46ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     79947.95   18804.53   92172.14
  Latency        1.19ms     0.88ms    13.63ms
  Latency Distribution
     50%     1.06ms
     75%     1.36ms
     90%     1.70ms
     99%     3.53ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     86420.91    8672.56   92414.18
  Latency        1.14ms   361.10us     4.75ms
  Latency Distribution
     50%     1.04ms
     75%     1.39ms
     90%     1.81ms
     99%     2.67ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    102701.46    7350.20  108016.70
  Latency        0.96ms   320.56us     5.47ms
  Latency Distribution
     50%     0.89ms
     75%     1.17ms
     90%     1.49ms
     99%     2.36ms
### Cookie Endpoint (/cookie)
  Reqs/sec    105568.72    7983.09  111925.76
  Latency        0.93ms   290.57us     4.13ms
  Latency Distribution
     50%     0.87ms
     75%     1.12ms
     90%     1.41ms
     99%     2.13ms
### Exception Endpoint (/exc)
  Reqs/sec     98736.05    7328.00  105126.31
  Latency        1.00ms   299.43us     4.86ms
  Latency Distribution
     50%     0.94ms
     75%     1.23ms
     90%     1.52ms
     99%     2.29ms
### HTML Response (/html)
  Reqs/sec    105485.41    6396.79  110707.25
  Latency        0.93ms   308.35us     4.19ms
  Latency Distribution
     50%     0.85ms
     75%     1.16ms
     90%     1.50ms
     99%     2.33ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     30791.42    6799.77   36292.42
  Latency        3.27ms     1.79ms    26.00ms
  Latency Distribution
     50%     2.91ms
     75%     3.88ms
     90%     5.16ms
     99%    11.38ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     78201.57    6210.63   82363.75
  Latency        1.26ms   425.47us     6.20ms
  Latency Distribution
     50%     1.17ms
     75%     1.52ms
     90%     1.91ms
     99%     3.05ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17045.16    1332.41   18880.40
  Latency        5.85ms     1.69ms    14.15ms
  Latency Distribution
     50%     6.22ms
     75%     7.19ms
     90%     8.11ms
     99%    10.99ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15879.83    1194.43   18519.48
  Latency        6.27ms     2.42ms    18.69ms
  Latency Distribution
     50%     5.72ms
     75%     7.64ms
     90%    10.16ms
     99%    14.48ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     83536.23    6756.60   90357.67
  Latency        1.17ms   369.10us     5.80ms
  Latency Distribution
     50%     1.12ms
     75%     1.43ms
     90%     1.79ms
     99%     2.70ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     86106.34    7380.91   98336.58
  Latency        1.13ms   471.28us     6.42ms
  Latency Distribution
     50%     1.01ms
     75%     1.41ms
     90%     1.87ms
     99%     3.40ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     69841.99   11276.88   79404.48
  Latency        1.43ms   659.85us    10.14ms
  Latency Distribution
     50%     1.29ms
     75%     1.77ms
     90%     2.40ms
     99%     4.34ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     14825.88    1839.18   23418.22
  Latency        6.82ms     1.68ms    15.94ms
  Latency Distribution
     50%     6.69ms
     75%     7.97ms
     90%     9.24ms
     99%    12.19ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     13099.88    1268.18   16481.89
  Latency        7.63ms     2.61ms    22.78ms
  Latency Distribution
     50%     7.09ms
     75%     9.11ms
     90%    11.70ms
     99%    16.17ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     17161.40    1319.74   22063.13
  Latency        5.84ms     1.63ms    14.72ms
  Latency Distribution
     50%     5.61ms
     75%     7.01ms
     90%     8.42ms
     99%    11.10ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     14539.94    2075.75   19082.49
  Latency        6.77ms     3.21ms    26.10ms
  Latency Distribution
     50%     6.47ms
     75%     8.99ms
     90%    11.60ms
     99%    16.89ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec     81756.60    8299.02   93915.56
  Latency        1.21ms   527.69us     6.08ms
  Latency Distribution
     50%     1.09ms
     75%     1.51ms
     90%     1.98ms
     99%     3.80ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     86437.88    8966.20   94494.62
  Latency        1.14ms   439.94us     6.45ms
  Latency Distribution
     50%     1.05ms
     75%     1.44ms
     90%     1.85ms
     99%     3.04ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     62501.33    5281.47   66625.70
  Latency        1.58ms   550.29us     7.30ms
  Latency Distribution
     50%     1.48ms
     75%     1.89ms
     90%     2.40ms
     99%     3.88ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     88420.00    5079.45   93094.85
  Latency        1.11ms   375.38us     4.64ms
  Latency Distribution
     50%     1.03ms
     75%     1.39ms
     90%     1.78ms
     99%     2.81ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     73577.78   12774.30   89784.76
  Latency        1.35ms   749.45us     6.39ms
  Latency Distribution
     50%     1.09ms
     75%     1.67ms
     90%     2.48ms
     99%     4.84ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    104114.47   19058.27  139926.08
  Latency        1.01ms   392.89us     4.89ms
  Latency Distribution
     50%     0.91ms
     75%     1.26ms
     90%     1.71ms
     99%     2.77ms
### CBV Response Types (/cbv-response)
  Reqs/sec     98354.04    7418.56  107090.18
  Latency        0.99ms   336.88us     5.06ms
  Latency Distribution
     50%     0.92ms
     75%     1.25ms
     90%     1.60ms
     99%     2.48ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     17245.80    1286.43   18544.26
  Latency        5.77ms     2.27ms    17.93ms
  Latency Distribution
     50%     5.46ms
     75%     7.46ms
     90%     9.47ms
     99%    12.70ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     94748.71    7681.23  102462.62
  Latency        1.04ms   373.68us     4.77ms
  Latency Distribution
     50%     0.95ms
     75%     1.29ms
     90%     1.61ms
     99%     2.65ms
### File Upload (POST /upload)
  Reqs/sec     90875.78    5318.73   94753.73
  Latency        1.08ms   347.47us     4.59ms
  Latency Distribution
     50%     1.02ms
     75%     1.32ms
     90%     1.69ms
     99%     2.73ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     85660.91    6068.12   93061.33
  Latency        1.14ms   409.81us     3.99ms
  Latency Distribution
     50%     1.03ms
     75%     1.45ms
     90%     1.94ms
     99%     2.94ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9924.34     911.77   11034.62
  Latency       10.03ms     3.65ms    34.80ms
  Latency Distribution
     50%     9.41ms
     75%    12.18ms
     90%    15.78ms
     99%    21.42ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     97155.22   10033.79  106633.69
  Latency        1.03ms   447.62us     6.40ms
  Latency Distribution
     50%     0.93ms
     75%     1.24ms
     90%     1.60ms
     99%     3.12ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     93631.89    7087.32   97927.27
  Latency        1.05ms   397.98us     5.17ms
  Latency Distribution
     50%     0.96ms
     75%     1.26ms
     90%     1.63ms
     99%     2.83ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     84662.56    9211.01   90486.42
  Latency        1.14ms   395.31us     7.44ms
  Latency Distribution
     50%     1.06ms
     75%     1.41ms
     90%     1.80ms
     99%     2.68ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     94127.23   10879.30  103193.37
  Latency        1.01ms   311.15us     5.17ms
  Latency Distribution
     50%     0.95ms
     75%     1.22ms
     90%     1.55ms
     99%     2.30ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    113877.13    9245.99  119673.62
  Latency        0.87ms   326.50us     4.75ms
  Latency Distribution
     50%   802.00us
     75%     1.09ms
     90%     1.38ms
     99%     2.27ms

### Path Parameter - int (/items/12345)
  Reqs/sec    104760.86    8265.33  109826.53
  Latency        0.93ms   288.24us     4.17ms
  Latency Distribution
     50%     0.88ms
     75%     1.14ms
     90%     1.43ms
     99%     2.11ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    102284.93    8277.54  109700.91
  Latency        0.95ms   296.27us     5.37ms
  Latency Distribution
     50%     0.89ms
     75%     1.15ms
     90%     1.42ms
     99%     2.11ms

### Header Parameter (/header)
  Reqs/sec    104187.12    7012.38  111115.54
  Latency        0.94ms   298.76us     5.36ms
  Latency Distribution
     50%     0.88ms
     75%     1.15ms
     90%     1.43ms
     99%     2.27ms

### Cookie Parameter (/cookie)
  Reqs/sec    102757.41    8539.60  110254.35
  Latency        0.95ms   349.49us     5.12ms
  Latency Distribution
     50%     0.90ms
     75%     1.14ms
     90%     1.44ms
     99%     2.34ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     83209.90    4096.70   87900.15
  Latency        1.18ms   412.12us     4.96ms
  Latency Distribution
     50%     1.07ms
     75%     1.47ms
     90%     1.90ms
     99%     3.06ms

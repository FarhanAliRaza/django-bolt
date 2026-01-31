# Django-Bolt Benchmark
Generated: Sun 01 Feb 2026 12:59:30 AM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    115772.65    9901.40  123056.54
  Latency        0.86ms   305.99us     4.68ms
  Latency Distribution
     50%   799.00us
     75%     1.02ms
     90%     1.27ms
     99%     2.21ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     85977.14    5930.21   91707.79
  Latency        1.15ms   364.39us     4.27ms
  Latency Distribution
     50%     1.07ms
     75%     1.43ms
     90%     1.81ms
     99%     2.75ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     86242.26    5910.92   93305.09
  Latency        1.14ms   372.75us     5.12ms
  Latency Distribution
     50%     1.06ms
     75%     1.38ms
     90%     1.77ms
     99%     2.62ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     99968.05    7679.31  106544.47
  Latency        0.98ms   309.79us     5.14ms
  Latency Distribution
     50%     0.92ms
     75%     1.22ms
     90%     1.50ms
     99%     2.16ms
### Cookie Endpoint (/cookie)
  Reqs/sec    106274.05    7699.91  111063.00
  Latency        0.93ms   253.11us     4.81ms
  Latency Distribution
     50%     0.88ms
     75%     1.13ms
     90%     1.40ms
     99%     1.92ms
### Exception Endpoint (/exc)
  Reqs/sec    102514.29    6372.35  107544.58
  Latency        0.96ms   308.41us     5.12ms
  Latency Distribution
     50%     0.87ms
     75%     1.17ms
     90%     1.48ms
     99%     2.21ms
### HTML Response (/html)
  Reqs/sec    108780.80    9024.01  115192.75
  Latency        0.90ms   319.00us     4.89ms
  Latency Distribution
     50%   833.00us
     75%     1.12ms
     90%     1.41ms
     99%     2.29ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     33964.52    7382.16   39411.22
  Latency        2.96ms     1.43ms    22.39ms
  Latency Distribution
     50%     2.71ms
     75%     3.35ms
     90%     4.17ms
     99%     9.28ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     76107.85    4708.66   82170.83
  Latency        1.28ms   366.14us     4.75ms
  Latency Distribution
     50%     1.22ms
     75%     1.55ms
     90%     1.92ms
     99%     2.90ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17606.99    3106.38   32320.36
  Latency        5.81ms     1.29ms    13.62ms
  Latency Distribution
     50%     6.03ms
     75%     6.79ms
     90%     7.49ms
     99%     9.32ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15217.30     838.08   17034.63
  Latency        6.54ms     1.37ms    15.32ms
  Latency Distribution
     50%     6.37ms
     75%     7.53ms
     90%     8.77ms
     99%    10.75ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     82911.41    5488.18   87320.91
  Latency        1.18ms   370.49us     5.16ms
  Latency Distribution
     50%     1.11ms
     75%     1.49ms
     90%     1.82ms
     99%     2.76ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     98864.69    7919.85  106525.95
  Latency        0.99ms   362.79us     5.34ms
  Latency Distribution
     50%     0.91ms
     75%     1.21ms
     90%     1.58ms
     99%     2.65ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     98328.35    8085.95  109504.14
  Latency        1.02ms   337.34us     4.98ms
  Latency Distribution
     50%     0.94ms
     75%     1.26ms
     90%     1.60ms
     99%     2.39ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13811.39    1126.00   17383.39
  Latency        7.24ms     1.56ms    17.43ms
  Latency Distribution
     50%     7.27ms
     75%     8.46ms
     90%     9.55ms
     99%    11.80ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     11933.89     657.54   13307.91
  Latency        8.35ms     2.45ms    21.05ms
  Latency Distribution
     50%     8.69ms
     75%    10.17ms
     90%    11.47ms
     99%    14.18ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     15924.80     872.25   18000.59
  Latency        6.26ms     1.89ms    17.23ms
  Latency Distribution
     50%     5.83ms
     75%     7.60ms
     90%     9.61ms
     99%    12.16ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13453.09    1699.99   18522.05
  Latency        7.45ms     2.94ms    23.50ms
  Latency Distribution
     50%     7.13ms
     75%     9.47ms
     90%    11.88ms
     99%    16.46ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    105957.73    8876.96  113968.24
  Latency        0.93ms   271.70us     4.53ms
  Latency Distribution
     50%     0.87ms
     75%     1.14ms
     90%     1.42ms
     99%     2.06ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     90336.32    6551.60   98611.72
  Latency        1.09ms   372.42us     5.80ms
  Latency Distribution
     50%     1.01ms
     75%     1.33ms
     90%     1.68ms
     99%     2.70ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     63550.24    5554.05   69906.99
  Latency        1.55ms   464.87us     8.07ms
  Latency Distribution
     50%     1.46ms
     75%     1.90ms
     90%     2.39ms
     99%     3.40ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     89923.42    4873.80   94476.65
  Latency        1.09ms   374.15us     5.61ms
  Latency Distribution
     50%     1.02ms
     75%     1.36ms
     90%     1.74ms
     99%     2.54ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     96921.26    8221.09  106018.81
  Latency        1.03ms   306.66us     4.75ms
  Latency Distribution
     50%     0.97ms
     75%     1.26ms
     90%     1.57ms
     99%     2.27ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     96320.06    7746.91  101032.74
  Latency        1.03ms   282.30us     3.94ms
  Latency Distribution
     50%     0.98ms
     75%     1.25ms
     90%     1.54ms
     99%     2.24ms
### CBV Response Types (/cbv-response)
  Reqs/sec    101878.47    8953.04  108062.38
  Latency        0.96ms   350.20us     4.84ms
  Latency Distribution
     50%     0.88ms
     75%     1.17ms
     90%     1.53ms
     99%     2.49ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16538.61    1186.46   19710.80
  Latency        6.04ms     1.69ms    15.98ms
  Latency Distribution
     50%     5.92ms
     75%     7.44ms
     90%     8.59ms
     99%    11.31ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     96234.58    9933.31  111383.35
  Latency        1.05ms   343.76us     5.28ms
  Latency Distribution
     50%     0.98ms
     75%     1.27ms
     90%     1.58ms
     99%     2.47ms
### File Upload (POST /upload)
  Reqs/sec     82452.61    5769.92   89676.43
  Latency        1.19ms   396.84us     5.21ms
  Latency Distribution
     50%     1.11ms
     75%     1.46ms
     90%     1.86ms
     99%     2.91ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     83937.22    5630.61   87811.92
  Latency        1.18ms   340.93us     4.62ms
  Latency Distribution
     50%     1.12ms
     75%     1.46ms
     90%     1.81ms
     99%     2.65ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
 0 / 10000 [---------------------------------]   0.00% 1763 / 10000 [====>------------------]  17.63% 8784/s 3599 / 10000 [========>--------------]  35.99% 8974/s 5499 / 10000 [============>----------]  54.99% 9147/s 7395 / 10000 [=================>-----]  73.95% 9228/s 9255 / 10000 [=====================>-]  92.55% 9241/s 10000 / 10000 [======================] 100.00% 8318/s 10000 / 10000 [===================] 100.00% 8315/s 1s
  Reqs/sec      9283.23     859.79   10419.89
  Latency       10.73ms     2.39ms    25.54ms
  Latency Distribution
     50%    10.43ms
     75%    11.94ms
     90%    14.27ms
     99%    18.50ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     99529.04    5564.45  104289.47
  Latency        0.98ms   319.22us     6.05ms
  Latency Distribution
     50%     0.91ms
     75%     1.22ms
     90%     1.56ms
     99%     2.35ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     97997.50    7651.48  109086.77
  Latency        1.02ms   301.47us     4.14ms
  Latency Distribution
     50%     0.96ms
     75%     1.27ms
     90%     1.58ms
     99%     2.31ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     85598.16    6661.75   92580.75
  Latency        1.14ms   402.68us     5.39ms
  Latency Distribution
     50%     1.05ms
     75%     1.40ms
     90%     1.80ms
     99%     2.77ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     82801.27    3815.42   86717.21
  Latency        1.19ms   361.91us     5.00ms
  Latency Distribution
     50%     1.12ms
     75%     1.47ms
     90%     1.83ms
     99%     2.72ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    105856.07    8744.67  113663.76
  Latency        0.93ms   346.43us     4.63ms
  Latency Distribution
     50%   839.00us
     75%     1.15ms
     90%     1.44ms
     99%     2.50ms

### Path Parameter - int (/items/12345)
  Reqs/sec    100059.46    7760.58  108339.31
  Latency        0.98ms   311.21us     4.46ms
  Latency Distribution
     50%     0.92ms
     75%     1.20ms
     90%     1.47ms
     99%     2.30ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    100085.77    8751.79  106650.15
  Latency        0.98ms   305.91us     4.70ms
  Latency Distribution
     50%     0.92ms
     75%     1.20ms
     90%     1.48ms
     99%     2.31ms

### Header Parameter (/header)
  Reqs/sec    100886.80    9338.67  107790.91
  Latency        0.97ms   325.88us     5.13ms
  Latency Distribution
     50%     0.90ms
     75%     1.19ms
     90%     1.53ms
     99%     2.29ms

### Cookie Parameter (/cookie)
  Reqs/sec    104034.26    7578.66  110571.12
  Latency        0.94ms   320.95us     5.82ms
  Latency Distribution
     50%     0.87ms
     75%     1.14ms
     90%     1.43ms
     99%     2.10ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     85386.79    5608.31   88820.79
  Latency        1.15ms   328.22us     5.69ms
  Latency Distribution
     50%     1.09ms
     75%     1.39ms
     90%     1.72ms
     99%     2.59ms

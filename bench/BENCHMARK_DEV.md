# Django-Bolt Benchmark
Generated: Fri Jan  9 10:39:28 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    120377.14   14217.01  132497.18
  Latency      808.13us   264.90us     4.31ms
  Latency Distribution
     50%   741.00us
     75%     1.00ms
     90%     1.30ms
     99%     1.95ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec    103269.81   14822.37  130401.45
  Latency        1.01ms   299.41us     3.81ms
  Latency Distribution
     50%     0.92ms
     75%     1.21ms
     90%     1.54ms
     99%     2.34ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     97925.16    6845.00  105203.33
  Latency        1.01ms   343.73us     6.17ms
  Latency Distribution
     50%     0.92ms
     75%     1.25ms
     90%     1.57ms
     99%     2.38ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    114101.00    7272.09  120168.36
  Latency        0.86ms   295.67us     4.33ms
  Latency Distribution
     50%   801.00us
     75%     1.06ms
     90%     1.33ms
     99%     2.06ms
### Cookie Endpoint (/cookie)
  Reqs/sec    112493.16   11837.57  124983.21
  Latency      843.25us   291.08us     4.36ms
  Latency Distribution
     50%   794.00us
     75%     1.04ms
     90%     1.32ms
     99%     2.19ms
### Exception Endpoint (/exc)
  Reqs/sec    112503.27    7947.16  117845.84
  Latency        0.88ms   305.05us     3.54ms
  Latency Distribution
     50%   805.00us
     75%     1.09ms
     90%     1.42ms
     99%     2.29ms
### HTML Response (/html)
  Reqs/sec    123154.91   11260.00  129216.49
  Latency      797.26us   298.91us     4.53ms
  Latency Distribution
     50%   726.00us
     75%     0.99ms
     90%     1.27ms
     99%     2.00ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     32401.23    9878.04   40349.99
  Latency        3.09ms     2.42ms    27.27ms
  Latency Distribution
     50%     2.59ms
     75%     3.39ms
     90%     4.47ms
     99%    18.02ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     75667.35    5909.79   81894.45
  Latency        1.30ms   583.32us    10.45ms
  Latency Distribution
     50%     1.17ms
     75%     1.56ms
     90%     2.05ms
     99%     4.41ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17586.98    1523.22   18952.48
  Latency        5.66ms     1.71ms    14.31ms
  Latency Distribution
     50%     5.05ms
     75%     7.33ms
     90%     8.37ms
     99%    11.64ms
### Get User via Dependency (/auth/me-dependency)
 0 / 10000 [---------------------------------------------------------------]   0.00% 3275 / 10000 [=================>----------------------------------]  32.75% 16292/s 6655 / 10000 [==================================>-----------------]  66.55% 16586/s 10000 / 10000 [===================================================] 100.00% 16625/s 10000 / 10000 [================================================] 100.00% 16623/s 0s
  Reqs/sec     16850.51    1389.61   19311.32
  Latency        5.92ms     1.62ms    13.94ms
  Latency Distribution
     50%     5.83ms
     75%     7.14ms
     90%     8.39ms
     99%    10.95ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     73637.30   17848.45   95956.72
  Latency        1.32ms   775.24us    10.10ms
  Latency Distribution
     50%     1.10ms
     75%     1.59ms
     90%     2.25ms
     99%     4.43ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    104442.07    8315.07  117049.25
  Latency        0.93ms   348.62us     4.61ms
  Latency Distribution
     50%   842.00us
     75%     1.12ms
     90%     1.43ms
     99%     2.59ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec    101687.00    5256.83  107802.68
  Latency        0.96ms   343.63us     4.79ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.47ms
     99%     2.72ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     15343.65    1268.73   17363.91
  Latency        6.50ms     2.74ms    71.62ms
  Latency Distribution
     50%     6.41ms
     75%     7.62ms
     90%     8.94ms
     99%    11.99ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12838.84    3111.65   15814.73
  Latency        7.40ms     5.50ms    70.44ms
  Latency Distribution
     50%     6.65ms
     75%     9.01ms
     90%    11.12ms
     99%    15.90ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     17918.61    1297.75   20152.59
  Latency        5.55ms     2.72ms    62.41ms
  Latency Distribution
     50%     5.22ms
     75%     6.81ms
     90%     8.13ms
     99%    11.14ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     15912.49    2158.25   19037.52
  Latency        6.20ms     2.61ms    27.68ms
  Latency Distribution
     50%     5.76ms
     75%     7.97ms
     90%    10.05ms
     99%    14.74ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    120656.35   12300.28  128807.83
  Latency      820.38us   333.01us     4.72ms
  Latency Distribution
     50%   749.00us
     75%     0.98ms
     90%     1.26ms
     99%     2.34ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    113011.94    8735.28  119431.69
  Latency        0.87ms   261.30us     4.21ms
  Latency Distribution
     50%   805.00us
     75%     1.04ms
     90%     1.35ms
     99%     2.06ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     70865.42    6479.50   77923.03
  Latency        1.39ms   405.27us     5.26ms
  Latency Distribution
     50%     1.31ms
     75%     1.63ms
     90%     2.10ms
     99%     3.18ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    106966.17    9897.41  114840.16
  Latency        0.91ms   310.32us     4.68ms
  Latency Distribution
     50%   846.00us
     75%     1.11ms
     90%     1.41ms
     99%     2.25ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    104734.61    6094.70  111348.43
  Latency        0.94ms   369.83us     5.31ms
  Latency Distribution
     50%     0.86ms
     75%     1.14ms
     90%     1.46ms
     99%     2.62ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    108679.82    8814.95  117393.01
  Latency        0.90ms   286.36us     3.88ms
  Latency Distribution
     50%   845.00us
     75%     1.10ms
     90%     1.38ms
     99%     2.32ms
### CBV Response Types (/cbv-response)
  Reqs/sec    117021.18    9827.08  130014.37
  Latency        0.85ms   272.66us     4.09ms
  Latency Distribution
     50%   791.00us
     75%     1.05ms
     90%     1.31ms
     99%     2.06ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     17135.51    2338.36   19542.35
  Latency        5.81ms     3.51ms   101.61ms
  Latency Distribution
     50%     5.50ms
     75%     7.00ms
     90%     8.45ms
     99%    12.51ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    101019.64    5598.49  106510.59
  Latency        0.97ms   350.93us     4.97ms
  Latency Distribution
     50%     0.89ms
     75%     1.17ms
     90%     1.50ms
     99%     2.57ms
### File Upload (POST /upload)
  Reqs/sec    100365.51    6459.79  105394.13
  Latency        0.97ms   319.81us     4.70ms
  Latency Distribution
     50%     0.91ms
     75%     1.18ms
     90%     1.50ms
     99%     2.26ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     92231.95    9146.26  103368.40
  Latency        1.04ms   368.31us     4.83ms
  Latency Distribution
     50%     0.95ms
     75%     1.28ms
     90%     1.70ms
     99%     2.69ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec     12871.20    4243.53   16908.30
  Latency        7.59ms     8.89ms   105.25ms
  Latency Distribution
     50%     6.81ms
     75%     8.35ms
     90%     9.72ms
     99%    28.36ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    111099.02   12413.50  121209.34
  Latency        0.89ms   376.01us     5.23ms
  Latency Distribution
     50%   807.00us
     75%     1.08ms
     90%     1.38ms
     99%     2.44ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec    109582.71   13588.12  119748.24
  Latency        0.88ms   298.30us     5.34ms
  Latency Distribution
     50%   823.00us
     75%     1.06ms
     90%     1.35ms
     99%     2.18ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec    100579.78    7760.76  104924.03
  Latency        0.97ms   328.85us     4.98ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.49ms
     99%     2.46ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    111896.15   11146.80  120635.94
  Latency        0.89ms   296.86us     4.45ms
  Latency Distribution
     50%   816.00us
     75%     1.06ms
     90%     1.36ms
     99%     2.51ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    119960.47    9887.97  128803.99
  Latency      815.25us   279.76us     3.71ms
  Latency Distribution
     50%   737.00us
     75%     1.00ms
     90%     1.31ms
     99%     2.07ms

### Path Parameter - int (/items/12345)
  Reqs/sec    116495.22    9997.22  127266.99
  Latency      849.25us   292.06us     5.56ms
  Latency Distribution
     50%   787.00us
     75%     1.05ms
     90%     1.34ms
     99%     2.04ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    115290.57   10450.03  121523.15
  Latency      846.89us   294.47us     6.21ms
  Latency Distribution
     50%   785.00us
     75%     1.04ms
     90%     1.29ms
     99%     2.07ms

### Header Parameter (/header)
  Reqs/sec    118414.25   11346.52  132304.95
  Latency      842.25us   293.97us     3.94ms
  Latency Distribution
     50%   775.00us
     75%     1.02ms
     90%     1.27ms
     99%     2.15ms

### Cookie Parameter (/cookie)
  Reqs/sec    114232.57   11798.09  121424.87
  Latency        0.86ms   289.48us     5.04ms
  Latency Distribution
     50%   793.00us
     75%     1.05ms
     90%     1.33ms
     99%     2.04ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     87071.13    7797.24   94820.21
  Latency        1.11ms   359.49us     4.72ms
  Latency Distribution
     50%     1.04ms
     75%     1.39ms
     90%     1.70ms
     99%     2.65ms

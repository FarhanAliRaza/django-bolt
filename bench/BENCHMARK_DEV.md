# Django-Bolt Benchmark
Generated: Wed 04 Feb 2026 08:02:57 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    106534.67    6670.85  111784.05
  Latency        0.92ms   292.26us     3.93ms
  Latency Distribution
     50%   844.00us
     75%     1.14ms
     90%     1.47ms
     99%     2.24ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     88919.94    8198.04   94858.79
  Latency        1.11ms   341.19us     4.83ms
  Latency Distribution
     50%     1.04ms
     75%     1.36ms
     90%     1.71ms
     99%     2.49ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     86860.77    5943.19   90712.00
  Latency        1.13ms   375.65us     5.82ms
  Latency Distribution
     50%     1.06ms
     75%     1.39ms
     90%     1.72ms
     99%     2.67ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     94578.93    8061.78  105589.19
  Latency        1.05ms   362.39us     4.45ms
  Latency Distribution
     50%     0.98ms
     75%     1.30ms
     90%     1.65ms
     99%     2.61ms
### Cookie Endpoint (/cookie)
  Reqs/sec     96339.49    7268.93  106365.25
  Latency        1.03ms   348.18us     5.14ms
  Latency Distribution
     50%     0.95ms
     75%     1.26ms
     90%     1.64ms
     99%     2.50ms
### Exception Endpoint (/exc)
  Reqs/sec     98153.43    7786.55  103815.21
  Latency        1.00ms   303.30us     4.70ms
  Latency Distribution
     50%     0.94ms
     75%     1.22ms
     90%     1.53ms
     99%     2.37ms
### HTML Response (/html)
  Reqs/sec    108831.35    8117.65  113177.49
  Latency        0.91ms   292.23us     5.34ms
  Latency Distribution
     50%   847.00us
     75%     1.10ms
     90%     1.38ms
     99%     2.21ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     31701.60    6650.76   36758.33
  Latency        3.15ms     1.53ms    23.01ms
  Latency Distribution
     50%     2.86ms
     75%     3.59ms
     90%     4.54ms
     99%     9.09ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     74940.24    5229.97   81090.59
  Latency        1.30ms   390.03us     5.62ms
  Latency Distribution
     50%     1.20ms
     75%     1.60ms
     90%     2.02ms
     99%     2.90ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     16867.29    1499.29   18089.54
  Latency        5.90ms     1.23ms    14.48ms
  Latency Distribution
     50%     5.86ms
     75%     6.91ms
     90%     7.73ms
     99%     9.92ms
### Get User via Dependency (/auth/me-dependency)
 0 / 10000 [-------------------------------------------------------]   0.00% 2955 / 10000 [=============>------------------------------]  29.55% 14731/s 6025 / 10000 [==========================>-----------------]  60.25% 15027/s 9075 / 10000 [=======================================>----]  90.75% 15097/s 10000 / 10000 [===========================================] 100.00% 12474/s 10000 / 10000 [========================================] 100.00% 12473/s 0s
  Reqs/sec     15171.51     789.17   16023.24
  Latency        6.55ms     1.72ms    15.50ms
  Latency Distribution
     50%     6.26ms
     75%     7.91ms
     90%     9.33ms
     99%    11.64ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     86386.04    5566.87   89717.95
  Latency        1.13ms   312.67us     5.31ms
  Latency Distribution
     50%     1.08ms
     75%     1.39ms
     90%     1.70ms
     99%     2.35ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     85765.77    3967.39   90443.24
  Latency        1.14ms   380.12us     5.10ms
  Latency Distribution
     50%     1.06ms
     75%     1.41ms
     90%     1.78ms
     99%     2.81ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     77651.18   12544.40   89087.51
  Latency        1.21ms   499.96us     6.13ms
  Latency Distribution
     50%     1.09ms
     75%     1.45ms
     90%     1.94ms
     99%     3.56ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13656.16     975.65   15198.73
  Latency        7.29ms     1.79ms    19.05ms
  Latency Distribution
     50%     7.01ms
     75%     8.80ms
     90%    10.46ms
     99%    12.26ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12099.54     817.97   15682.67
  Latency        8.26ms     1.68ms    17.90ms
  Latency Distribution
     50%     8.36ms
     75%     9.46ms
     90%    10.88ms
     99%    12.84ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     15804.42     694.49   17120.71
  Latency        6.30ms     1.80ms    15.61ms
  Latency Distribution
     50%     6.05ms
     75%     8.17ms
     90%     9.18ms
     99%    10.55ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13235.37    1185.62   14723.43
  Latency        7.52ms     2.66ms    24.09ms
  Latency Distribution
     50%     7.13ms
     75%     9.38ms
     90%    11.64ms
     99%    15.56ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    106431.78    9267.20  113842.83
  Latency        0.93ms   309.19us     4.62ms
  Latency Distribution
     50%     0.86ms
     75%     1.13ms
     90%     1.41ms
     99%     2.25ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    100991.92    7507.20  106151.87
  Latency        0.97ms   287.69us     4.73ms
  Latency Distribution
     50%     0.92ms
     75%     1.19ms
     90%     1.49ms
     99%     2.16ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     64339.30    4916.10   67866.04
  Latency        1.53ms   515.12us     6.14ms
  Latency Distribution
     50%     1.43ms
     75%     1.92ms
     90%     2.41ms
     99%     3.66ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     98395.43    6674.56  104413.13
  Latency        1.00ms   320.91us     4.43ms
  Latency Distribution
     50%     0.92ms
     75%     1.22ms
     90%     1.58ms
     99%     2.41ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     94758.98    7504.67  100431.63
  Latency        1.04ms   312.36us     4.84ms
  Latency Distribution
     50%     0.98ms
     75%     1.28ms
     90%     1.60ms
     99%     2.30ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     89877.79   20113.89  102038.11
  Latency        1.00ms   335.02us     5.31ms
  Latency Distribution
     50%     0.91ms
     75%     1.24ms
     90%     1.64ms
     99%     2.56ms
### CBV Response Types (/cbv-response)
  Reqs/sec    104962.18    6861.90  109110.95
  Latency        0.94ms   259.07us     3.53ms
  Latency Distribution
     50%     0.88ms
     75%     1.14ms
     90%     1.43ms
     99%     2.10ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16221.88    1035.38   17025.24
  Latency        6.13ms     1.81ms    17.36ms
  Latency Distribution
     50%     5.78ms
     75%     7.88ms
     90%     9.35ms
     99%    10.89ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     92957.77    7700.26   98074.29
  Latency        1.07ms   412.42us     5.11ms
  Latency Distribution
     50%     0.96ms
     75%     1.31ms
     90%     1.69ms
     99%     2.87ms
### File Upload (POST /upload)
  Reqs/sec     84192.41    4581.43   88065.29
  Latency        1.17ms   415.89us     5.19ms
  Latency Distribution
     50%     1.05ms
     75%     1.48ms
     90%     1.94ms
     99%     2.99ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     83860.74    5682.96   89415.39
  Latency        1.18ms   334.41us     5.08ms
  Latency Distribution
     50%     1.11ms
     75%     1.42ms
     90%     1.77ms
     99%     2.49ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9142.08     969.48   10554.54
  Latency       10.91ms     3.10ms    24.50ms
  Latency Distribution
     50%    10.96ms
     75%    13.51ms
     90%    15.42ms
     99%    19.20ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     99129.83    9083.32  104407.95
  Latency        0.99ms   339.64us     5.64ms
  Latency Distribution
     50%     0.92ms
     75%     1.22ms
     90%     1.53ms
     99%     2.33ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     96841.73    8232.49  103385.07
  Latency        1.03ms   329.72us     5.82ms
  Latency Distribution
     50%     0.94ms
     75%     1.26ms
     90%     1.62ms
     99%     2.40ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     87517.20    5786.14   91174.60
  Latency        1.13ms   400.29us     6.57ms
  Latency Distribution
     50%     1.04ms
     75%     1.38ms
     90%     1.76ms
     99%     2.70ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    103168.25   14784.30  131034.16
  Latency        1.01ms   265.17us     3.19ms
  Latency Distribution
     50%     0.95ms
     75%     1.25ms
     90%     1.55ms
     99%     2.19ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    113070.15    8845.95  117676.06
  Latency        0.87ms   285.84us     4.83ms
  Latency Distribution
     50%   812.00us
     75%     1.08ms
     90%     1.35ms
     99%     2.16ms

### Path Parameter - int (/items/12345)
  Reqs/sec    104222.30    7815.38  110450.23
  Latency        0.95ms   310.92us     5.01ms
  Latency Distribution
     50%     0.87ms
     75%     1.16ms
     90%     1.47ms
     99%     2.23ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec     99904.54    8960.04  104966.71
  Latency        0.98ms   323.89us     5.45ms
  Latency Distribution
     50%     0.91ms
     75%     1.20ms
     90%     1.54ms
     99%     2.24ms

### Header Parameter (/header)
  Reqs/sec    103205.43    8142.44  109751.29
  Latency        0.96ms   290.92us     4.74ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.43ms
     99%     2.10ms

### Cookie Parameter (/cookie)
  Reqs/sec    103932.54    8191.15  109864.14
  Latency        0.95ms   278.29us     4.49ms
  Latency Distribution
     50%     0.88ms
     75%     1.18ms
     90%     1.47ms
     99%     2.09ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     84314.99    5239.33   89416.45
  Latency        1.16ms   362.79us     5.67ms
  Latency Distribution
     50%     1.07ms
     75%     1.41ms
     90%     1.82ms
     99%     2.73ms

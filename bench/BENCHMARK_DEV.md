# Django-Bolt Benchmark
Generated: Mon Jan  5 07:50:24 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    117496.38    8311.12  125755.37
  Latency      820.53us   340.58us     4.69ms
  Latency Distribution
     50%   744.00us
     75%     0.98ms
     90%     1.25ms
     99%     2.55ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec    103870.63   22841.07  146412.10
  Latency        1.03ms   376.24us     5.88ms
  Latency Distribution
     50%     0.95ms
     75%     1.23ms
     90%     1.52ms
     99%     2.67ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     95808.38    7479.16  105554.03
  Latency        1.05ms   318.27us     4.46ms
  Latency Distribution
     50%     0.97ms
     75%     1.28ms
     90%     1.61ms
     99%     2.42ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    112206.92   11673.74  123378.37
  Latency        0.85ms   325.82us     5.81ms
  Latency Distribution
     50%   780.00us
     75%     1.04ms
     90%     1.32ms
     99%     2.08ms
### Cookie Endpoint (/cookie)
  Reqs/sec    108519.96    9084.02  116384.57
  Latency        0.89ms   304.76us     5.88ms
  Latency Distribution
     50%   838.00us
     75%     1.09ms
     90%     1.35ms
     99%     2.07ms
### Exception Endpoint (/exc)
  Reqs/sec    111470.26    6872.35  116914.71
  Latency        0.88ms   305.37us     4.54ms
  Latency Distribution
     50%   811.00us
     75%     1.07ms
     90%     1.37ms
     99%     2.18ms
### HTML Response (/html)
  Reqs/sec    117545.50    7146.52  122190.76
  Latency      837.74us   252.96us     4.55ms
  Latency Distribution
     50%   782.00us
     75%     1.02ms
     90%     1.31ms
     99%     1.93ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     32969.24    7899.89   39609.66
  Latency        3.04ms     1.68ms    24.75ms
  Latency Distribution
     50%     2.70ms
     75%     3.52ms
     90%     4.59ms
     99%     9.21ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     84261.04    5885.93   90420.77
  Latency        1.16ms   336.35us     4.70ms
  Latency Distribution
     50%     1.09ms
     75%     1.45ms
     90%     1.80ms
     99%     2.68ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17983.98    1694.44   21185.76
  Latency        5.54ms     1.61ms    13.23ms
  Latency Distribution
     50%     5.64ms
     75%     6.70ms
     90%     7.72ms
     99%    10.58ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     16697.44    1281.16   18713.22
  Latency        5.96ms     2.00ms    15.89ms
  Latency Distribution
     50%     5.86ms
     75%     7.47ms
     90%     8.96ms
     99%    11.82ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     84922.10    7067.70   92266.53
  Latency        1.15ms   446.44us     6.80ms
  Latency Distribution
     50%     1.08ms
     75%     1.40ms
     90%     1.76ms
     99%     2.85ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    107126.30    6971.86  113906.29
  Latency        0.91ms   266.39us     3.75ms
  Latency Distribution
     50%     0.86ms
     75%     1.13ms
     90%     1.41ms
     99%     2.14ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec    105256.41   10026.16  115495.87
  Latency        0.94ms   284.42us     4.12ms
  Latency Distribution
     50%     0.87ms
     75%     1.14ms
     90%     1.42ms
     99%     2.27ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     14665.35    2548.98   18723.24
  Latency        6.81ms     2.88ms    56.95ms
  Latency Distribution
     50%     6.45ms
     75%     8.09ms
     90%     9.95ms
     99%    16.76ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12872.26    3051.86   17353.74
  Latency        7.44ms     6.02ms    78.38ms
  Latency Distribution
     50%     6.33ms
     75%     9.23ms
     90%    11.37ms
     99%    17.52ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     17800.16    1406.95   20549.60
  Latency        5.58ms     2.35ms    58.02ms
  Latency Distribution
     50%     5.15ms
     75%     6.89ms
     90%     8.63ms
     99%    11.56ms
### Users Mini10 (Sync) (/users/sync-mini10)
 0 / 10000 [---------------------------------------------------------------]   0.00% 2990 / 10000 [===============>------------------------------------]  29.90% 14881/s 6229 / 10000 [================================>-------------------]  62.29% 15530/s 9404 / 10000 [================================================>---]  94.04% 15634/s 10000 / 10000 [===================================================] 100.00% 12469/s 10000 / 10000 [================================================] 100.00% 12467/s 0s
  Reqs/sec     15668.10    1871.91   17984.39
  Latency        6.34ms     3.52ms    31.18ms
  Latency Distribution
     50%     5.18ms
     75%     7.89ms
     90%    12.17ms
     99%    19.11ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    122569.06    9213.58  130461.72
  Latency      798.53us   279.36us     4.22ms
  Latency Distribution
     50%   717.00us
     75%     0.97ms
     90%     1.23ms
     99%     2.04ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    114262.39    8223.17  121909.74
  Latency        0.86ms   278.71us     4.42ms
  Latency Distribution
     50%   796.00us
     75%     1.04ms
     90%     1.32ms
     99%     2.19ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     72112.63    6612.59   77169.59
  Latency        1.36ms   416.02us     4.90ms
  Latency Distribution
     50%     1.25ms
     75%     1.64ms
     90%     2.11ms
     99%     3.12ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    104366.28   10027.54  110071.84
  Latency        0.94ms   293.85us     4.33ms
  Latency Distribution
     50%     0.88ms
     75%     1.17ms
     90%     1.48ms
     99%     2.31ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    108073.97    8999.82  114066.51
  Latency        0.91ms   265.81us     3.47ms
  Latency Distribution
     50%   832.00us
     75%     1.12ms
     90%     1.45ms
     99%     2.14ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    111008.84   10321.92  118097.01
  Latency        0.89ms   323.41us     5.44ms
  Latency Distribution
     50%   816.00us
     75%     1.06ms
     90%     1.34ms
     99%     2.45ms
### CBV Response Types (/cbv-response)
  Reqs/sec    110374.18    5348.36  115151.96
  Latency        0.89ms   341.37us     4.91ms
  Latency Distribution
     50%   791.00us
     75%     1.09ms
     90%     1.44ms
     99%     2.35ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     17484.51    2222.22   19618.13
  Latency        5.61ms     2.42ms    67.00ms
  Latency Distribution
     50%     5.40ms
     75%     6.52ms
     90%     7.86ms
     99%    11.16ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    103206.37   10215.40  113354.43
  Latency        0.95ms   344.53us     6.33ms
  Latency Distribution
     50%     0.86ms
     75%     1.18ms
     90%     1.51ms
     99%     2.66ms
### File Upload (POST /upload)
  Reqs/sec     93517.09    8091.76  104435.49
  Latency        1.05ms   348.05us     3.75ms
  Latency Distribution
     50%     0.96ms
     75%     1.29ms
     90%     1.68ms
     99%     2.55ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     91605.74   13577.01  103269.13
  Latency        1.03ms   344.61us     4.70ms
  Latency Distribution
     50%     0.94ms
     75%     1.25ms
     90%     1.59ms
     99%     2.79ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec     13637.37    3948.01   16910.77
  Latency        6.95ms     4.70ms    80.03ms
  Latency Distribution
     50%     6.20ms
     75%     8.06ms
     90%     9.60ms
     99%    18.09ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    116401.29    9706.15  123523.04
  Latency      841.63us   320.67us     4.76ms
  Latency Distribution
     50%   770.00us
     75%     1.02ms
     90%     1.29ms
     99%     2.04ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec    110380.72    7313.27  116956.45
  Latency        0.89ms   293.48us     4.82ms
  Latency Distribution
     50%   824.00us
     75%     1.06ms
     90%     1.33ms
     99%     2.15ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     98623.57    6761.68  106021.25
  Latency        0.98ms   294.88us     5.21ms
  Latency Distribution
     50%     0.92ms
     75%     1.20ms
     90%     1.51ms
     99%     2.33ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    111015.53    9349.23  118028.50
  Latency        0.89ms   308.27us     4.75ms
  Latency Distribution
     50%   822.00us
     75%     1.07ms
     90%     1.35ms
     99%     2.29ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    124984.18   15341.50  138151.17
  Latency      780.83us   316.56us     4.28ms
  Latency Distribution
     50%   699.00us
     75%     0.92ms
     90%     1.19ms
     99%     2.42ms

### Path Parameter - int (/items/12345)
  Reqs/sec    111026.69    6005.21  117288.66
  Latency        0.88ms   291.36us     4.38ms
  Latency Distribution
     50%   810.00us
     75%     1.09ms
     90%     1.38ms
     99%     2.10ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    110680.88   11227.80  117382.05
  Latency        0.89ms   286.85us     4.29ms
  Latency Distribution
     50%   817.00us
     75%     1.07ms
     90%     1.40ms
     99%     2.08ms

### Header Parameter (/header)
  Reqs/sec    117178.25   10466.31  127586.42
  Latency      849.03us   267.46us     3.19ms
  Latency Distribution
     50%   776.00us
     75%     1.04ms
     90%     1.36ms
     99%     2.16ms

### Cookie Parameter (/cookie)
  Reqs/sec    116166.20    9338.82  125569.94
  Latency        0.85ms   247.48us     3.05ms
  Latency Distribution
     50%   793.00us
     75%     1.03ms
     90%     1.29ms
     99%     2.07ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     96646.29    7526.03  101749.02
  Latency        1.01ms   316.23us     4.32ms
  Latency Distribution
     50%     0.96ms
     75%     1.25ms
     90%     1.56ms
     99%     2.51ms

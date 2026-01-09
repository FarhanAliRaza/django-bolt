# Django-Bolt Benchmark
Generated: Fri Jan  9 08:30:06 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    125780.41    8268.96  131016.21
  Latency      780.89us   244.11us     3.14ms
  Latency Distribution
     50%   731.00us
     75%     0.96ms
     90%     1.20ms
     99%     1.95ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec    100609.37    8869.42  107459.51
  Latency        0.98ms   326.33us     5.20ms
  Latency Distribution
     50%     0.92ms
     75%     1.17ms
     90%     1.48ms
     99%     2.33ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     96770.57    8700.04  109178.15
  Latency        1.04ms   333.44us     4.44ms
  Latency Distribution
     50%     0.96ms
     75%     1.22ms
     90%     1.52ms
     99%     2.59ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    120463.89   13258.58  135630.77
  Latency      829.07us   269.40us     4.37ms
  Latency Distribution
     50%   762.00us
     75%     1.00ms
     90%     1.29ms
     99%     2.04ms
### Cookie Endpoint (/cookie)
  Reqs/sec    112106.87    7518.29  118985.07
  Latency        0.86ms   318.01us     4.55ms
  Latency Distribution
     50%   788.00us
     75%     1.04ms
     90%     1.32ms
     99%     2.42ms
### Exception Endpoint (/exc)
  Reqs/sec    121448.01   15476.14  139590.72
  Latency      831.84us   278.68us     4.67ms
  Latency Distribution
     50%   763.00us
     75%     1.02ms
     90%     1.30ms
     99%     2.09ms
### HTML Response (/html)
  Reqs/sec    125848.88   11366.22  132035.61
  Latency      769.12us   253.02us     5.48ms
  Latency Distribution
     50%   711.00us
     75%     0.93ms
     90%     1.19ms
     99%     1.87ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
 0 / 10000 [-------------------------------------------------------------------------------------------------------------------------------------------------------------]   0.00% 7150 / 10000 [========================================================================================================>-----------------------------------------]  71.50% 35467/s 10000 / 10000 [=================================================================================================================================================] 100.00% 24855/s 10000 / 10000 [==============================================================================================================================================] 100.00% 24848/s 0s
  Reqs/sec     36346.11    9136.20   43506.02
  Latency        2.73ms     1.59ms    21.94ms
  Latency Distribution
     50%     2.33ms
     75%     3.10ms
     90%     4.23ms
     99%     8.87ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     85725.27    5399.09   89325.86
  Latency        1.14ms   313.91us     4.24ms
  Latency Distribution
     50%     1.09ms
     75%     1.41ms
     90%     1.75ms
     99%     2.45ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     18211.81    1408.25   19192.46
  Latency        5.44ms     1.40ms    17.68ms
  Latency Distribution
     50%     5.12ms
     75%     6.38ms
     90%     7.85ms
     99%     9.91ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     16789.64    1264.73   19142.24
  Latency        5.92ms     1.51ms    13.71ms
  Latency Distribution
     50%     5.79ms
     75%     7.06ms
     90%     8.22ms
     99%    10.73ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     72088.57   27391.57   87647.23
  Latency        1.18ms   420.23us     7.96ms
  Latency Distribution
     50%     1.09ms
     75%     1.53ms
     90%     1.91ms
     99%     2.88ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     98127.59    7758.54  108425.99
  Latency        0.99ms   353.50us     5.09ms
  Latency Distribution
     50%     0.92ms
     75%     1.23ms
     90%     1.62ms
     99%     2.55ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     88622.59   25745.39  108848.14
  Latency        1.00ms   383.83us     4.53ms
  Latency Distribution
     50%     0.90ms
     75%     1.22ms
     90%     1.62ms
     99%     2.78ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     15464.50    1298.27   17779.34
  Latency        6.44ms     3.08ms    64.21ms
  Latency Distribution
     50%     6.05ms
     75%     8.12ms
     90%     9.70ms
     99%    12.47ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     13649.11    1682.46   16267.93
  Latency        7.30ms     5.27ms    68.03ms
  Latency Distribution
     50%     6.59ms
     75%     8.40ms
     90%    10.05ms
     99%    13.91ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     18186.90    1308.09   19658.85
  Latency        5.47ms     2.23ms    56.22ms
  Latency Distribution
     50%     5.13ms
     75%     6.74ms
     90%     8.14ms
     99%    10.83ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     19907.44   21613.24  137665.20
  Latency        6.17ms     3.04ms    24.72ms
  Latency Distribution
     50%     5.47ms
     75%     7.80ms
     90%    10.53ms
     99%    17.56ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    124036.70   12746.90  131926.59
  Latency      792.44us   260.46us     3.86ms
  Latency Distribution
     50%   733.00us
     75%     0.96ms
     90%     1.21ms
     99%     1.97ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    118385.03   12384.55  128485.58
  Latency      833.93us   264.97us     5.52ms
  Latency Distribution
     50%   775.00us
     75%     1.01ms
     90%     1.29ms
     99%     1.91ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     76735.89    5893.55   82443.27
  Latency        1.28ms   329.49us     4.22ms
  Latency Distribution
     50%     1.20ms
     75%     1.50ms
     90%     1.89ms
     99%     2.84ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    110504.22   10216.01  123367.74
  Latency        0.87ms   251.89us     4.00ms
  Latency Distribution
     50%   803.00us
     75%     1.07ms
     90%     1.38ms
     99%     2.00ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    108091.41    7791.91  116620.74
  Latency        0.90ms   278.91us     4.61ms
  Latency Distribution
     50%   847.00us
     75%     1.12ms
     90%     1.40ms
     99%     2.12ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    113390.03    9787.78  122332.89
  Latency      844.73us   246.97us     3.86ms
  Latency Distribution
     50%   789.00us
     75%     1.04ms
     90%     1.34ms
     99%     1.98ms
### CBV Response Types (/cbv-response)
  Reqs/sec    123194.54   12260.91  129543.99
  Latency      790.74us   233.29us     5.19ms
  Latency Distribution
     50%   736.00us
     75%     0.95ms
     90%     1.19ms
     99%     1.73ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16694.07    4762.50   19561.52
  Latency        5.53ms     3.04ms    58.46ms
  Latency Distribution
     50%     5.10ms
     75%     6.42ms
     90%     8.13ms
     99%    11.63ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    108519.26    7800.50  113758.58
  Latency        0.90ms   308.05us     4.33ms
  Latency Distribution
     50%   825.00us
     75%     1.12ms
     90%     1.45ms
     99%     2.35ms
### File Upload (POST /upload)
  Reqs/sec    108157.82   27772.33  159758.42
  Latency        1.00ms   349.61us     6.81ms
  Latency Distribution
     50%     0.93ms
     75%     1.20ms
     90%     1.52ms
     99%     2.50ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     98860.66    9153.31  113488.56
  Latency        1.02ms   303.07us     4.04ms
  Latency Distribution
     50%     0.96ms
     75%     1.22ms
     90%     1.57ms
     99%     2.43ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec     14261.61    4358.63   16968.95
  Latency        6.60ms     3.92ms    70.57ms
  Latency Distribution
     50%     6.23ms
     75%     7.52ms
     90%     8.71ms
     99%    12.58ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    117715.50   12018.48  128407.38
  Latency      849.51us   340.37us     5.08ms
  Latency Distribution
     50%   782.00us
     75%     1.01ms
     90%     1.27ms
     99%     2.46ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec    110024.94   11292.07  117489.44
  Latency        0.89ms   281.34us     4.58ms
  Latency Distribution
     50%   817.00us
     75%     1.09ms
     90%     1.38ms
     99%     2.06ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec    103683.55    8368.93  109469.48
  Latency        0.95ms   332.75us     4.70ms
  Latency Distribution
     50%     0.88ms
     75%     1.12ms
     90%     1.43ms
     99%     2.67ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    106573.14    9998.04  116984.16
  Latency        0.91ms   296.31us     4.28ms
  Latency Distribution
     50%   840.00us
     75%     1.11ms
     90%     1.42ms
     99%     2.15ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    127981.96   14163.94  135939.18
  Latency      768.24us   302.63us     5.02ms
  Latency Distribution
     50%   713.00us
     75%     0.93ms
     90%     1.17ms
     99%     1.94ms

### Path Parameter - int (/items/12345)
  Reqs/sec    116335.80    8066.72  123323.12
  Latency      841.50us   277.25us     5.33ms
  Latency Distribution
     50%   782.00us
     75%     1.03ms
     90%     1.31ms
     99%     2.14ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    118416.74    9503.94  127696.98
  Latency      831.07us   294.68us     5.68ms
  Latency Distribution
     50%   780.00us
     75%     1.03ms
     90%     1.31ms
     99%     1.90ms

### Header Parameter (/header)
  Reqs/sec    133410.39   29342.14  183522.26
  Latency      807.33us   267.91us     4.19ms
  Latency Distribution
     50%   735.00us
     75%     0.98ms
     90%     1.24ms
     99%     1.99ms

### Cookie Parameter (/cookie)
  Reqs/sec    118889.37    9499.88  124555.37
  Latency      822.36us   289.06us     5.50ms
  Latency Distribution
     50%   755.00us
     75%     0.98ms
     90%     1.25ms
     99%     1.96ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec    100076.73    8107.75  106718.44
  Latency        0.97ms   303.88us     5.34ms
  Latency Distribution
     50%     0.92ms
     75%     1.23ms
     90%     1.57ms
     99%     2.32ms

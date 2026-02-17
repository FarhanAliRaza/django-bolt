# Django-Bolt Benchmark
Generated: Tue Feb 17 11:32:04 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    111044.70    7893.83  116143.69
  Latency        0.88ms   314.32us     5.34ms
  Latency Distribution
     50%   799.00us
     75%     1.12ms
     90%     1.48ms
     99%     2.22ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     76154.42   18180.63   91892.10
  Latency        1.20ms   399.45us     4.80ms
  Latency Distribution
     50%     1.11ms
     75%     1.47ms
     90%     1.84ms
     99%     3.08ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     71886.52    7316.74   77626.14
  Latency        1.37ms   446.72us     5.46ms
  Latency Distribution
     50%     1.28ms
     75%     1.69ms
     90%     2.12ms
     99%     3.28ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     95084.45   13316.55  111050.46
  Latency        1.06ms   343.56us     5.88ms
  Latency Distribution
     50%     0.98ms
     75%     1.30ms
     90%     1.67ms
     99%     2.44ms
### Cookie Endpoint (/cookie)
  Reqs/sec    102479.92    6697.42  107589.42
  Latency        0.96ms   319.66us     4.40ms
  Latency Distribution
     50%     0.89ms
     75%     1.17ms
     90%     1.50ms
     99%     2.39ms
### Exception Endpoint (/exc)
  Reqs/sec    100797.72    7574.48  105552.49
  Latency        0.98ms   301.14us     4.50ms
  Latency Distribution
     50%     0.92ms
     75%     1.20ms
     90%     1.51ms
     99%     2.21ms
### HTML Response (/html)
  Reqs/sec    110094.66    7530.25  117304.57
  Latency        0.90ms   312.44us     4.89ms
  Latency Distribution
     50%   827.00us
     75%     1.14ms
     90%     1.47ms
     99%     2.32ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
 0 / 10000 [-----------------------------------------------------------]   0.00% 7050 / 10000 [=================================>--------------]  70.50% 35144/s 10000 / 10000 [===============================================] 100.00% 24868/s 10000 / 10000 [============================================] 100.00% 24862/s 0s
  Reqs/sec     36353.56    8005.80   40876.61
  Latency        2.75ms     1.43ms    19.12ms
  Latency Distribution
     50%     2.50ms
     75%     3.13ms
     90%     3.92ms
     99%     7.97ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     82976.71   10112.49  102341.11
  Latency        1.22ms   308.38us     4.72ms
  Latency Distribution
     50%     1.16ms
     75%     1.48ms
     90%     1.78ms
     99%     2.50ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17289.73    1393.50   19333.27
  Latency        5.76ms     1.64ms    15.83ms
  Latency Distribution
     50%     5.32ms
     75%     7.05ms
     90%     8.49ms
     99%    11.05ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15021.23     908.71   16124.71
  Latency        6.59ms     2.19ms    15.94ms
  Latency Distribution
     50%     6.58ms
     75%     8.29ms
     90%     9.87ms
     99%    12.84ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     86429.10    6172.98   90219.80
  Latency        1.13ms   348.81us     4.75ms
  Latency Distribution
     50%     1.07ms
     75%     1.38ms
     90%     1.76ms
     99%     2.57ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    106515.60    7768.92  113718.72
  Latency        0.93ms   257.16us     4.13ms
  Latency Distribution
     50%     0.87ms
     75%     1.15ms
     90%     1.47ms
     99%     2.07ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec    100334.01    7137.54  105182.64
  Latency        0.98ms   354.09us     4.79ms
  Latency Distribution
     50%     0.89ms
     75%     1.21ms
     90%     1.56ms
     99%     2.46ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13801.44    1086.46   17918.50
  Latency        7.25ms     1.01ms    15.26ms
  Latency Distribution
     50%     7.34ms
     75%     8.07ms
     90%     8.71ms
     99%     9.85ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec      4611.54     372.95    5304.04
  Latency       21.60ms     6.01ms    48.85ms
  Latency Distribution
     50%    21.55ms
     75%    25.38ms
     90%    29.81ms
     99%    37.43ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     15999.59     910.75   18313.87
  Latency        6.23ms     1.10ms    11.55ms
  Latency Distribution
     50%     6.12ms
     75%     7.03ms
     90%     8.11ms
     99%     9.66ms
### Users Mini10 (Sync) (/users/sync-mini10)
 0 / 10000 [-----------------------------------------------------------]   0.00% 2638 / 10000 [============>-----------------------------------]  26.38% 13146/s 5339 / 10000 [=========================>----------------------]  53.39% 13316/s 8075 / 10000 [======================================>---------]  80.75% 13428/s 10000 / 10000 [===============================================] 100.00% 12462/s 10000 / 10000 [============================================] 100.00% 12461/s 0s
  Reqs/sec     13530.98    1163.14   14931.67
  Latency        7.36ms     2.80ms    23.31ms
  Latency Distribution
     50%     6.87ms
     75%     9.20ms
     90%    11.72ms
     99%    16.47ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    109555.81    7641.10  114367.79
  Latency        0.89ms   309.52us     4.23ms
  Latency Distribution
     50%   821.00us
     75%     1.10ms
     90%     1.41ms
     99%     2.32ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    103486.62    8565.57  110830.92
  Latency        0.95ms   338.04us     4.82ms
  Latency Distribution
     50%     0.86ms
     75%     1.17ms
     90%     1.53ms
     99%     2.38ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     67057.25    3695.95   73124.48
  Latency        1.48ms   395.70us     4.66ms
  Latency Distribution
     50%     1.38ms
     75%     1.76ms
     90%     2.17ms
     99%     3.25ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    101134.20    5281.83  105892.02
  Latency        0.97ms   332.68us     4.31ms
  Latency Distribution
     50%     0.89ms
     75%     1.18ms
     90%     1.53ms
     99%     2.49ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     99072.46    5375.90  102799.84
  Latency        0.99ms   271.90us     4.03ms
  Latency Distribution
     50%     0.94ms
     75%     1.22ms
     90%     1.52ms
     99%     2.16ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     99088.45    6995.89  105400.33
  Latency        0.99ms   325.87us     5.87ms
  Latency Distribution
     50%     0.93ms
     75%     1.24ms
     90%     1.56ms
     99%     2.38ms
### CBV Response Types (/cbv-response)
  Reqs/sec    105986.25    6513.56  110841.91
  Latency        0.92ms   260.86us     4.05ms
  Latency Distribution
     50%     0.87ms
     75%     1.13ms
     90%     1.40ms
     99%     2.09ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
 0 / 10000 [-----------------------------------------------------------]   0.00% 3190 / 10000 [===============>--------------------------------]  31.90% 15905/s 6480 / 10000 [===============================>----------------]  64.80% 16167/s 9771 / 10000 [==============================================>-]  97.71% 16256/s 10000 / 10000 [===============================================] 100.00% 12479/s 10000 / 10000 [============================================] 100.00% 12477/s 0s
  Reqs/sec     16330.32    1024.05   18110.00
  Latency        6.10ms     1.25ms    12.61ms
  Latency Distribution
     50%     6.03ms
     75%     7.06ms
     90%     8.11ms
     99%     9.70ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    100140.40    8873.32  107059.78
  Latency        0.98ms   317.71us     5.47ms
  Latency Distribution
     50%     0.91ms
     75%     1.19ms
     90%     1.51ms
     99%     2.21ms
### File Upload (POST /upload)
  Reqs/sec     86540.81    4124.37   91112.21
  Latency        1.13ms   359.74us     4.55ms
  Latency Distribution
     50%     1.06ms
     75%     1.46ms
     90%     1.87ms
     99%     2.61ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     85057.62    5190.75   88468.13
  Latency        1.15ms   404.48us     6.86ms
  Latency Distribution
     50%     1.03ms
     75%     1.45ms
     90%     1.97ms
     99%     2.84ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
 0 / 10000 [-----------------------------------------------------------]   0.00% 1838 / 10000 [=========>---------------------------------------]  18.38% 9149/s 3787 / 10000 [==================>------------------------------]  37.87% 9442/s 5739 / 10000 [============================>--------------------]  57.39% 9545/s 7702 / 10000 [=====================================>-----------]  77.02% 9607/s 9575 / 10000 [==============================================>--]  95.75% 9554/s 10000 / 10000 [================================================] 100.00% 8311/s 10000 / 10000 [=============================================] 100.00% 8311/s 1s
  Reqs/sec     10131.90    4067.41   38434.04
  Latency       10.38ms     2.04ms    21.49ms
  Latency Distribution
     50%    10.50ms
     75%    11.80ms
     90%    12.95ms
     99%    16.42ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    105827.48    9382.69  113044.33
  Latency        0.92ms   290.36us     5.96ms
  Latency Distribution
     50%     0.86ms
     75%     1.12ms
     90%     1.41ms
     99%     2.09ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     99686.15    7353.39  105216.57
  Latency        0.98ms   246.62us     4.14ms
  Latency Distribution
     50%     0.93ms
     75%     1.19ms
     90%     1.46ms
     99%     2.00ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     90274.41    7462.27   95237.62
  Latency        1.09ms   372.99us     5.16ms
  Latency Distribution
     50%     1.01ms
     75%     1.34ms
     90%     1.70ms
     99%     2.68ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     93517.95    9491.28  101532.89
  Latency        1.01ms   345.97us     4.60ms
  Latency Distribution
     50%     0.93ms
     75%     1.29ms
     90%     1.70ms
     99%     2.50ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    114283.24    8925.73  120904.82
  Latency        0.86ms   337.11us     5.16ms
  Latency Distribution
     50%   784.00us
     75%     1.09ms
     90%     1.39ms
     99%     2.15ms

### Path Parameter - int (/items/12345)
  Reqs/sec    108966.03    9009.49  115748.60
  Latency        0.91ms   253.50us     4.84ms
  Latency Distribution
     50%   847.00us
     75%     1.13ms
     90%     1.42ms
     99%     2.01ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    106508.06    6737.36  110837.73
  Latency        0.92ms   269.60us     3.74ms
  Latency Distribution
     50%     0.87ms
     75%     1.13ms
     90%     1.43ms
     99%     2.08ms

### Header Parameter (/header)
  Reqs/sec    107753.42    6200.44  113493.26
  Latency        0.91ms   268.41us     4.97ms
  Latency Distribution
     50%     0.86ms
     75%     1.10ms
     90%     1.35ms
     99%     1.97ms

### Cookie Parameter (/cookie)
  Reqs/sec    104804.04    7446.96  109382.11
  Latency        0.93ms   330.39us     4.62ms
  Latency Distribution
     50%     0.86ms
     75%     1.14ms
     90%     1.47ms
     99%     2.33ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     87372.12    4260.25   90228.97
  Latency        1.12ms   344.94us     5.54ms
  Latency Distribution
     50%     1.05ms
     75%     1.36ms
     90%     1.74ms
     99%     2.60ms

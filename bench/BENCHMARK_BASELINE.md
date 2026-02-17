# Django-Bolt Benchmark
Generated: Tue 17 Feb 2026 11:22:01 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    108306.25    9817.79  116429.34
  Latency        0.91ms   311.39us     4.74ms
  Latency Distribution
     50%     0.85ms
     75%     1.17ms
     90%     1.47ms
     99%     2.11ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     86811.22    5301.19   90936.76
  Latency        1.13ms   372.77us     4.51ms
  Latency Distribution
     50%     1.03ms
     75%     1.38ms
     90%     1.80ms
     99%     2.88ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     87485.78    4343.26   90714.42
  Latency        1.12ms   324.21us     4.43ms
  Latency Distribution
     50%     1.05ms
     75%     1.35ms
     90%     1.73ms
     99%     2.54ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    101928.74    6329.62  106779.58
  Latency        0.96ms   282.75us     4.83ms
  Latency Distribution
     50%     0.90ms
     75%     1.18ms
     90%     1.47ms
     99%     2.11ms
### Cookie Endpoint (/cookie)
  Reqs/sec    101542.63    5975.71  106220.63
  Latency        0.96ms   302.51us     5.09ms
  Latency Distribution
     50%     0.89ms
     75%     1.19ms
     90%     1.52ms
     99%     2.29ms
### Exception Endpoint (/exc)
  Reqs/sec     97086.77    6395.10  102554.60
  Latency        1.00ms   291.58us     5.49ms
  Latency Distribution
     50%     0.95ms
     75%     1.22ms
     90%     1.53ms
     99%     2.15ms
### HTML Response (/html)
  Reqs/sec    108626.68    7831.79  113400.36
  Latency        0.90ms   264.78us     4.62ms
  Latency Distribution
     50%     0.85ms
     75%     1.11ms
     90%     1.38ms
     99%     1.96ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     29317.73    7546.79   39536.94
  Latency        3.44ms     2.55ms    47.12ms
  Latency Distribution
     50%     2.87ms
     75%     3.85ms
     90%     5.21ms
     99%    15.32ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     78024.86    5623.04   82542.65
  Latency        1.27ms   411.13us     4.85ms
  Latency Distribution
     50%     1.18ms
     75%     1.61ms
     90%     2.04ms
     99%     2.99ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     16985.59    1375.69   18104.34
  Latency        5.81ms     1.77ms    15.17ms
  Latency Distribution
     50%     5.33ms
     75%     7.08ms
     90%     8.98ms
     99%    11.38ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     14342.32     970.83   16058.23
  Latency        6.93ms     2.28ms    17.84ms
  Latency Distribution
     50%     6.73ms
     75%     8.56ms
     90%    10.41ms
     99%    13.72ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     83013.94    6050.72   89453.96
  Latency        1.18ms   374.77us     5.01ms
  Latency Distribution
     50%     1.11ms
     75%     1.47ms
     90%     1.84ms
     99%     2.88ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    104326.50    6364.26  110265.98
  Latency        0.94ms   299.79us     4.48ms
  Latency Distribution
     50%     0.88ms
     75%     1.16ms
     90%     1.45ms
     99%     2.17ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     97590.66    7515.85  103393.76
  Latency        1.00ms   306.98us     5.12ms
  Latency Distribution
     50%     0.95ms
     75%     1.22ms
     90%     1.51ms
     99%     2.15ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13664.92     791.53   14752.06
  Latency        7.28ms     1.77ms    16.91ms
  Latency Distribution
     50%     7.12ms
     75%     8.59ms
     90%    10.35ms
     99%    11.84ms
### Users Full10 (Sync) (/users/sync-full10)
 0 / 10000 [-------------------------------------------------------------]   0.00% 845 / 10000 [===>-----------------------------------------]   8.45% 4204/s 00m02s 1775 / 10000 [=======>------------------------------------]  17.75% 4421/s 00m01s 2688 / 10000 [===========>--------------------------------]  26.88% 4467/s 00m01s 3617 / 10000 [===============>----------------------------]  36.17% 4508/s 00m01s 4541 / 10000 [===================>------------------------]  45.41% 4529/s 00m01s 5454 / 10000 [=======================>--------------------]  54.54% 4533/s 00m01s 6388 / 10000 [================================>------------------]  63.88% 4552/s 7322 / 10000 [=====================================>-------------]  73.22% 4566/s 8236 / 10000 [==========================================>--------]  82.36% 4565/s 9171 / 10000 [==============================================>----]  91.71% 4576/s 10000 / 10000 [==================================================] 100.00% 4535/s 10000 / 10000 [===============================================] 100.00% 4535/s 2s
  Reqs/sec      4564.80     519.04    5688.26
  Latency       21.75ms     7.91ms    65.34ms
  Latency Distribution
     50%    20.23ms
     75%    25.20ms
     90%    34.57ms
     99%    45.73ms
### Users Mini10 (Async) (/users/mini10)
 0 / 10000 [-------------------------------------------------------------]   0.00% 3114 / 10000 [===============>----------------------------------]  31.14% 15531/s 6323 / 10000 [===============================>------------------]  63.23% 15776/s 9599 / 10000 [===============================================>--]  95.99% 15969/s 10000 / 10000 [=================================================] 100.00% 12465/s 10000 / 10000 [==============================================] 100.00% 12464/s 0s
  Reqs/sec     15785.03    1863.42   18109.65
  Latency        6.19ms     1.60ms    15.15ms
  Latency Distribution
     50%     5.86ms
     75%     7.29ms
     90%     8.88ms
     99%    11.32ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13309.43    1720.78   14996.77
  Latency        7.38ms     3.71ms    31.54ms
  Latency Distribution
     50%     6.40ms
     75%     8.98ms
     90%    12.50ms
     99%    21.50ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    107308.87   10315.45  113361.83
  Latency        0.92ms   330.32us     5.37ms
  Latency Distribution
     50%     0.86ms
     75%     1.11ms
     90%     1.39ms
     99%     2.11ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     99498.22    6887.87  104702.99
  Latency        0.98ms   335.46us     5.39ms
  Latency Distribution
     50%     0.89ms
     75%     1.20ms
     90%     1.57ms
     99%     2.47ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     67367.74    4231.18   72215.27
  Latency        1.46ms   355.16us     4.51ms
  Latency Distribution
     50%     1.38ms
     75%     1.71ms
     90%     2.09ms
     99%     2.86ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     98540.71    6896.66  103213.09
  Latency        0.99ms   311.22us     5.11ms
  Latency Distribution
     50%     0.93ms
     75%     1.22ms
     90%     1.55ms
     99%     2.19ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     92988.52    5585.84   99494.80
  Latency        1.05ms   377.83us     5.23ms
  Latency Distribution
     50%     0.96ms
     75%     1.30ms
     90%     1.70ms
     99%     2.61ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     88915.19   22765.65  101384.09
  Latency        1.12ms     0.95ms    13.28ms
  Latency Distribution
     50%     0.96ms
     75%     1.27ms
     90%     1.66ms
     99%     3.35ms
### CBV Response Types (/cbv-response)
  Reqs/sec     99990.70    7363.38  107380.69
  Latency        0.98ms   329.94us     5.35ms
  Latency Distribution
     50%     0.92ms
     75%     1.19ms
     90%     1.51ms
     99%     2.41ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16340.46    1099.19   18349.66
  Latency        6.10ms     1.42ms    18.33ms
  Latency Distribution
     50%     5.86ms
     75%     7.29ms
     90%     8.43ms
     99%    10.54ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     99654.73    8919.15  113210.99
  Latency        1.01ms   309.76us     4.05ms
  Latency Distribution
     50%     0.94ms
     75%     1.24ms
     90%     1.53ms
     99%     2.44ms
### File Upload (POST /upload)
  Reqs/sec     86298.80    6052.99   92639.52
  Latency        1.13ms   338.93us     4.79ms
  Latency Distribution
     50%     1.08ms
     75%     1.39ms
     90%     1.73ms
     99%     2.54ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     83722.59    6008.54   88150.02
  Latency        1.17ms   327.85us     5.59ms
  Latency Distribution
     50%     1.11ms
     75%     1.44ms
     90%     1.76ms
     99%     2.45ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9722.42    1330.52   17273.03
  Latency       10.39ms     2.75ms    22.01ms
  Latency Distribution
     50%    10.83ms
     75%    12.32ms
     90%    14.02ms
     99%    17.96ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     95156.23    6810.14   99188.77
  Latency        1.03ms   359.69us     5.56ms
  Latency Distribution
     50%     0.98ms
     75%     1.27ms
     90%     1.60ms
     99%     2.37ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     91347.44   14333.02   99182.09
  Latency        1.09ms   442.31us     7.62ms
  Latency Distribution
     50%     1.00ms
     75%     1.32ms
     90%     1.69ms
     99%     3.06ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     86209.40    6607.81   90989.33
  Latency        1.15ms   419.90us     4.81ms
  Latency Distribution
     50%     1.04ms
     75%     1.44ms
     90%     1.89ms
     99%     3.01ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     95861.71    7556.72  104976.16
  Latency        1.04ms   347.93us     5.87ms
  Latency Distribution
     50%     0.98ms
     75%     1.28ms
     90%     1.57ms
     99%     2.25ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    111038.57   10498.50  119064.23
  Latency        0.89ms   332.39us     5.13ms
  Latency Distribution
     50%   826.00us
     75%     1.08ms
     90%     1.35ms
     99%     2.17ms

### Path Parameter - int (/items/12345)
  Reqs/sec    101159.72    7198.76  106655.07
  Latency        0.97ms   325.48us     4.21ms
  Latency Distribution
     50%     0.89ms
     75%     1.22ms
     90%     1.59ms
     99%     2.37ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    101923.57    7387.71  107755.49
  Latency        0.96ms   297.74us     4.40ms
  Latency Distribution
     50%     0.92ms
     75%     1.20ms
     90%     1.48ms
     99%     2.23ms

### Header Parameter (/header)
  Reqs/sec    101884.25    8108.67  107541.44
  Latency        0.96ms   314.57us     5.20ms
  Latency Distribution
     50%     0.89ms
     75%     1.19ms
     90%     1.50ms
     99%     2.23ms

### Cookie Parameter (/cookie)
  Reqs/sec    102534.17    7382.55  106882.06
  Latency        0.96ms   292.44us     5.18ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.43ms
     99%     2.07ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     84228.37    5120.54   89138.15
  Latency        1.17ms   339.26us     4.91ms
  Latency Distribution
     50%     1.12ms
     75%     1.44ms
     90%     1.76ms
     99%     2.59ms

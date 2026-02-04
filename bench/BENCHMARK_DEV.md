# Django-Bolt Benchmark
Generated: Wed 04 Feb 2026 06:09:27 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    106795.47    9061.59  115818.97
  Latency        0.92ms   349.71us     5.35ms
  Latency Distribution
     50%   844.00us
     75%     1.13ms
     90%     1.45ms
     99%     2.23ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     87790.47    7248.88   91771.39
  Latency        1.13ms   374.93us     5.62ms
  Latency Distribution
     50%     1.04ms
     75%     1.34ms
     90%     1.68ms
     99%     2.55ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     87775.44    6868.16   93725.59
  Latency        1.12ms   342.77us     5.95ms
  Latency Distribution
     50%     1.04ms
     75%     1.37ms
     90%     1.73ms
     99%     2.51ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     99814.20    5563.46  104839.23
  Latency        0.98ms   353.75us     5.33ms
  Latency Distribution
     50%     0.91ms
     75%     1.21ms
     90%     1.59ms
     99%     2.47ms
### Cookie Endpoint (/cookie)
  Reqs/sec    104159.57    9867.66  112591.34
  Latency        0.95ms   306.51us     4.42ms
  Latency Distribution
     50%     0.89ms
     75%     1.16ms
     90%     1.46ms
     99%     2.30ms
### Exception Endpoint (/exc)
  Reqs/sec    100978.48    7238.55  106765.50
  Latency        0.97ms   312.89us     4.64ms
  Latency Distribution
     50%     0.90ms
     75%     1.18ms
     90%     1.45ms
     99%     2.29ms
### HTML Response (/html)
  Reqs/sec    111082.44    8034.18  119036.12
  Latency        0.89ms   300.33us     4.34ms
  Latency Distribution
     50%   828.00us
     75%     1.09ms
     90%     1.38ms
     99%     2.12ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     34570.41    7977.42   38747.31
  Latency        2.89ms     1.63ms    21.93ms
  Latency Distribution
     50%     2.58ms
     75%     3.35ms
     90%     4.25ms
     99%     9.01ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     79624.45    5571.40   82852.66
  Latency        1.24ms   333.06us     6.00ms
  Latency Distribution
     50%     1.18ms
     75%     1.52ms
     90%     1.84ms
     99%     2.58ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
 0 / 10000 [-------------------------------------------------------]   0.00% 3375 / 10000 [==============>-----------------------------]  33.75% 16835/s 6963 / 10000 [==============================>-------------]  69.63% 17380/s 10000 / 10000 [===========================================] 100.00% 16619/s 10000 / 10000 [========================================] 100.00% 16616/s 0s
  Reqs/sec     17660.64    1655.01   20989.55
  Latency        5.65ms     1.24ms    14.10ms
  Latency Distribution
     50%     5.62ms
     75%     6.40ms
     90%     7.40ms
     99%     9.76ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15858.55    1014.34   18145.14
  Latency        6.28ms     1.75ms    14.37ms
  Latency Distribution
     50%     6.42ms
     75%     7.58ms
     90%     8.67ms
     99%    10.90ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     84200.36    6101.22   89490.79
  Latency        1.17ms   387.85us     5.88ms
  Latency Distribution
     50%     1.10ms
     75%     1.45ms
     90%     1.86ms
     99%     2.85ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    101835.26    5907.10  106097.50
  Latency        0.96ms   286.09us     4.25ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.49ms
     99%     2.25ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     98582.76    8030.61  110154.57
  Latency        1.02ms   329.07us     4.79ms
  Latency Distribution
     50%     0.94ms
     75%     1.24ms
     90%     1.62ms
     99%     2.45ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     14302.97    1003.30   15394.53
  Latency        6.95ms     1.96ms    16.07ms
  Latency Distribution
     50%     7.09ms
     75%     8.73ms
     90%     9.80ms
     99%    12.41ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12968.50     989.50   15301.35
  Latency        7.65ms     2.65ms    21.73ms
  Latency Distribution
     50%     7.32ms
     75%     9.24ms
     90%    11.72ms
     99%    16.15ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     16761.36     996.44   18994.46
  Latency        5.93ms     1.80ms    14.81ms
  Latency Distribution
     50%     5.56ms
     75%     7.15ms
     90%     8.95ms
     99%    11.54ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13781.10    1453.28   17148.22
  Latency        7.24ms     2.87ms    23.95ms
  Latency Distribution
     50%     6.57ms
     75%     8.86ms
     90%    11.81ms
     99%    16.71ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    104100.37    9145.69  111609.41
  Latency        0.94ms   318.88us     6.20ms
  Latency Distribution
     50%     0.89ms
     75%     1.19ms
     90%     1.50ms
     99%     2.29ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    101778.93    7060.75  107190.77
  Latency        0.96ms   296.52us     5.17ms
  Latency Distribution
     50%     0.90ms
     75%     1.18ms
     90%     1.43ms
     99%     2.07ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     68153.86    4632.96   71860.09
  Latency        1.45ms   376.09us     5.87ms
  Latency Distribution
     50%     1.38ms
     75%     1.70ms
     90%     2.09ms
     99%     3.00ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     94050.65   10067.40  101271.37
  Latency        1.01ms   313.99us     5.45ms
  Latency Distribution
     50%     0.94ms
     75%     1.24ms
     90%     1.58ms
     99%     2.31ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     96558.08    5712.08  101809.78
  Latency        1.03ms   343.75us     7.03ms
  Latency Distribution
     50%     0.96ms
     75%     1.29ms
     90%     1.66ms
     99%     2.54ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     96080.99    2906.15   98445.24
  Latency        1.02ms   306.68us     5.06ms
  Latency Distribution
     50%     0.95ms
     75%     1.26ms
     90%     1.60ms
     99%     2.33ms
### CBV Response Types (/cbv-response)
  Reqs/sec    103832.21    5263.87  108718.27
  Latency        0.95ms   323.72us     4.50ms
  Latency Distribution
     50%     0.86ms
     75%     1.16ms
     90%     1.51ms
     99%     2.42ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     17230.74    1145.72   18240.76
  Latency        5.77ms     1.36ms    15.57ms
  Latency Distribution
     50%     5.74ms
     75%     6.77ms
     90%     7.78ms
     99%     9.96ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     96322.34    7175.03  101596.40
  Latency        1.03ms   388.27us     5.95ms
  Latency Distribution
     50%     0.94ms
     75%     1.28ms
     90%     1.71ms
     99%     2.73ms
### File Upload (POST /upload)
  Reqs/sec     89785.11    6534.87   94802.88
  Latency        1.10ms   388.13us     5.27ms
  Latency Distribution
     50%     1.03ms
     75%     1.38ms
     90%     1.72ms
     99%     2.89ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     85682.13    6428.22   92171.90
  Latency        1.14ms   364.82us     5.09ms
  Latency Distribution
     50%     1.06ms
     75%     1.42ms
     90%     1.78ms
     99%     2.68ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9508.39     911.08   11963.16
  Latency       10.52ms     2.58ms    23.26ms
  Latency Distribution
     50%     9.84ms
     75%    12.23ms
     90%    14.94ms
     99%    18.48ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    101065.04    7465.81  104756.03
  Latency        0.97ms   321.00us     4.62ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.47ms
     99%     2.35ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     95528.23    7454.15  102304.08
  Latency        1.01ms   337.29us     4.62ms
  Latency Distribution
     50%     0.94ms
     75%     1.25ms
     90%     1.58ms
     99%     2.45ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     89739.24    7262.87   94135.00
  Latency        1.10ms   381.40us     5.20ms
  Latency Distribution
     50%     1.00ms
     75%     1.33ms
     90%     1.70ms
     99%     2.77ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     95706.27    6620.36  101575.09
  Latency        1.00ms   314.99us     4.52ms
  Latency Distribution
     50%     0.94ms
     75%     1.25ms
     90%     1.54ms
     99%     2.42ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    113067.98    9658.00  120720.69
  Latency        0.87ms   341.60us     5.20ms
  Latency Distribution
     50%   789.00us
     75%     1.04ms
     90%     1.31ms
     99%     2.19ms

### Path Parameter - int (/items/12345)
  Reqs/sec    105394.48    6061.38  109014.10
  Latency        0.94ms   277.93us     4.04ms
  Latency Distribution
     50%     0.88ms
     75%     1.15ms
     90%     1.41ms
     99%     2.19ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    104093.76    6996.13  108787.12
  Latency        0.95ms   304.54us     4.42ms
  Latency Distribution
     50%     0.88ms
     75%     1.17ms
     90%     1.49ms
     99%     2.25ms

### Header Parameter (/header)
  Reqs/sec    102085.46    6049.00  105857.35
  Latency        0.96ms   304.44us     3.87ms
  Latency Distribution
     50%     0.90ms
     75%     1.20ms
     90%     1.53ms
     99%     2.40ms

### Cookie Parameter (/cookie)
  Reqs/sec     98641.54    4952.37  103054.40
  Latency        0.99ms   344.03us     4.36ms
  Latency Distribution
     50%     0.92ms
     75%     1.24ms
     90%     1.58ms
     99%     2.57ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     86557.03    6026.21   91850.36
  Latency        1.13ms   339.36us     5.04ms
  Latency Distribution
     50%     1.07ms
     75%     1.38ms
     90%     1.73ms
     99%     2.47ms

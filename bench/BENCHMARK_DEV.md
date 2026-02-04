# Django-Bolt Benchmark
Generated: Wed 04 Feb 2026 10:39:06 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    106545.78    8775.89  113666.21
  Latency        0.93ms   383.86us     5.07ms
  Latency Distribution
     50%   849.00us
     75%     1.15ms
     90%     1.46ms
     99%     2.47ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     86544.40    6122.30   91184.68
  Latency        1.14ms   343.76us     5.29ms
  Latency Distribution
     50%     1.08ms
     75%     1.39ms
     90%     1.77ms
     99%     2.63ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     84713.88    7003.38   89342.79
  Latency        1.16ms   377.33us     5.01ms
  Latency Distribution
     50%     1.08ms
     75%     1.39ms
     90%     1.76ms
     99%     2.78ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     98898.94    7626.97  105727.39
  Latency        0.99ms   327.41us     5.29ms
  Latency Distribution
     50%     0.92ms
     75%     1.21ms
     90%     1.54ms
     99%     2.39ms
### Cookie Endpoint (/cookie)
  Reqs/sec    299341.07  493129.49 1305832.72
  Latency        1.00ms   386.73us     6.54ms
  Latency Distribution
     50%     0.93ms
     75%     1.21ms
     90%     1.53ms
     99%     2.31ms
### Exception Endpoint (/exc)
  Reqs/sec     98916.87    9217.82  111862.96
  Latency        1.02ms   358.13us     5.54ms
  Latency Distribution
     50%     0.95ms
     75%     1.23ms
     90%     1.57ms
     99%     2.52ms
### HTML Response (/html)
  Reqs/sec    103643.09    8419.83  109143.39
  Latency        0.95ms   356.91us     5.73ms
  Latency Distribution
     50%     0.89ms
     75%     1.15ms
     90%     1.44ms
     99%     2.47ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     29857.36    6332.07   35162.72
  Latency        3.35ms     1.68ms    22.70ms
  Latency Distribution
     50%     2.96ms
     75%     3.98ms
     90%     5.22ms
     99%    10.48ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     77548.90    5186.83   80901.02
  Latency        1.28ms   370.20us     5.54ms
  Latency Distribution
     50%     1.19ms
     75%     1.54ms
     90%     1.90ms
     99%     2.91ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     16374.12    1425.12   18125.50
  Latency        6.07ms     1.87ms    14.74ms
  Latency Distribution
     50%     6.04ms
     75%     7.29ms
     90%     8.98ms
     99%    11.88ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15571.45    1010.57   17343.06
  Latency        6.39ms     1.78ms    14.90ms
  Latency Distribution
     50%     6.21ms
     75%     7.65ms
     90%     9.15ms
     99%    12.00ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     83459.43    5985.05   88995.48
  Latency        1.18ms   434.36us     5.89ms
  Latency Distribution
     50%     1.09ms
     75%     1.43ms
     90%     1.82ms
     99%     3.06ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     99171.84    5705.19  103769.86
  Latency        0.99ms   320.90us     3.63ms
  Latency Distribution
     50%     0.91ms
     75%     1.23ms
     90%     1.61ms
     99%     2.42ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     92925.78    7092.46   97662.36
  Latency        1.06ms   361.27us     5.46ms
  Latency Distribution
     50%     0.97ms
     75%     1.33ms
     90%     1.68ms
     99%     2.55ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     14069.54    1418.61   14877.26
  Latency        6.97ms     1.94ms    16.83ms
  Latency Distribution
     50%     6.67ms
     75%     8.91ms
     90%    10.24ms
     99%    12.23ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12682.71     733.72   13929.71
  Latency        7.84ms     2.35ms    18.13ms
  Latency Distribution
     50%     7.75ms
     75%     9.65ms
     90%    11.61ms
     99%    14.37ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     16667.95    1099.59   21170.24
  Latency        6.01ms     1.29ms    11.72ms
  Latency Distribution
     50%     5.93ms
     75%     7.01ms
     90%     8.07ms
     99%     9.93ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13437.18    1160.00   15592.70
  Latency        7.43ms     2.80ms    23.09ms
  Latency Distribution
     50%     6.95ms
     75%     9.20ms
     90%    11.74ms
     99%    16.46ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    107488.44    8239.29  113121.94
  Latency        0.92ms   333.78us     5.24ms
  Latency Distribution
     50%   834.00us
     75%     1.14ms
     90%     1.45ms
     99%     2.41ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    100300.38    8880.33  112213.55
  Latency        1.00ms   329.00us     6.07ms
  Latency Distribution
     50%     0.92ms
     75%     1.22ms
     90%     1.53ms
     99%     2.33ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     67246.43    6220.40   72352.85
  Latency        1.48ms   436.64us     5.95ms
  Latency Distribution
     50%     1.38ms
     75%     1.73ms
     90%     2.17ms
     99%     3.28ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     93675.72   11064.12  103461.93
  Latency        1.01ms   306.85us     4.88ms
  Latency Distribution
     50%     0.95ms
     75%     1.23ms
     90%     1.53ms
     99%     2.32ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     90529.67    3729.45   94352.85
  Latency        1.08ms   382.29us     5.37ms
  Latency Distribution
     50%     0.98ms
     75%     1.33ms
     90%     1.73ms
     99%     2.73ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    103105.06   13173.21  126714.61
  Latency        1.00ms   292.48us     5.13ms
  Latency Distribution
     50%     0.94ms
     75%     1.22ms
     90%     1.52ms
     99%     2.15ms
### CBV Response Types (/cbv-response)
  Reqs/sec    101752.93    6652.65  108769.88
  Latency        0.96ms   318.08us     4.57ms
  Latency Distribution
     50%     0.90ms
     75%     1.16ms
     90%     1.46ms
     99%     2.36ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16795.79    1173.30   18119.15
  Latency        5.92ms     1.73ms    13.68ms
  Latency Distribution
     50%     5.90ms
     75%     7.37ms
     90%     8.67ms
     99%    10.94ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     87254.25    6162.04   93272.38
  Latency        1.13ms   420.08us     5.29ms
  Latency Distribution
     50%     1.02ms
     75%     1.38ms
     90%     1.79ms
     99%     3.11ms
### File Upload (POST /upload)
  Reqs/sec     81175.33    6241.91   89163.75
  Latency        1.23ms   398.56us     5.57ms
  Latency Distribution
     50%     1.17ms
     75%     1.53ms
     90%     1.90ms
     99%     2.73ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     83280.13    7903.27   89359.20
  Latency        1.19ms   384.52us     5.43ms
  Latency Distribution
     50%     1.09ms
     75%     1.47ms
     90%     1.89ms
     99%     2.83ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9665.94    1038.56   11377.05
  Latency       10.33ms     2.83ms    25.33ms
  Latency Distribution
     50%     9.64ms
     75%    12.62ms
     90%    14.74ms
     99%    19.40ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    100354.90    8572.20  105797.43
  Latency        0.98ms   328.50us     5.83ms
  Latency Distribution
     50%     0.91ms
     75%     1.21ms
     90%     1.49ms
     99%     2.40ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     95597.75    8526.32  102351.31
  Latency        1.01ms   313.04us     5.30ms
  Latency Distribution
     50%     0.95ms
     75%     1.23ms
     90%     1.54ms
     99%     2.34ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     87415.27    6845.61   92775.81
  Latency        1.13ms   388.15us     5.48ms
  Latency Distribution
     50%     1.03ms
     75%     1.37ms
     90%     1.75ms
     99%     2.78ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     95994.38    6572.56  102621.41
  Latency        1.03ms   368.07us     5.47ms
  Latency Distribution
     50%     0.95ms
     75%     1.25ms
     90%     1.62ms
     99%     2.72ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    106881.40   10550.51  114508.43
  Latency        0.92ms   357.28us     5.02ms
  Latency Distribution
     50%   844.00us
     75%     1.15ms
     90%     1.49ms
     99%     2.54ms

### Path Parameter - int (/items/12345)
  Reqs/sec    103152.91    9698.57  109156.59
  Latency        0.95ms   318.22us     5.01ms
  Latency Distribution
     50%     0.88ms
     75%     1.16ms
     90%     1.50ms
     99%     2.27ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    101374.49    6731.95  106439.90
  Latency        0.97ms   348.63us     5.37ms
  Latency Distribution
     50%     0.89ms
     75%     1.17ms
     90%     1.52ms
     99%     2.58ms

### Header Parameter (/header)
  Reqs/sec     97880.82   11098.50  103781.76
  Latency        1.01ms   311.11us     6.00ms
  Latency Distribution
     50%     0.94ms
     75%     1.24ms
     90%     1.59ms
     99%     2.33ms

### Cookie Parameter (/cookie)
  Reqs/sec     99588.44    4723.85  103706.66
  Latency        0.99ms   320.39us     4.36ms
  Latency Distribution
     50%     0.92ms
     75%     1.20ms
     90%     1.53ms
     99%     2.40ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     85702.99    5895.63   89030.87
  Latency        1.14ms   376.41us     4.91ms
  Latency Distribution
     50%     1.07ms
     75%     1.39ms
     90%     1.73ms
     99%     2.68ms

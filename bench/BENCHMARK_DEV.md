# Django-Bolt Benchmark
Generated: Wed 04 Feb 2026 09:26:20 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    108198.62   11507.76  119773.31
  Latency        0.92ms   366.61us     5.45ms
  Latency Distribution
     50%   844.00us
     75%     1.11ms
     90%     1.41ms
     99%     2.31ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     84012.54   11585.67  107688.61
  Latency        1.22ms   376.21us     5.46ms
  Latency Distribution
     50%     1.15ms
     75%     1.49ms
     90%     1.88ms
     99%     2.72ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     85520.94    9665.46   93945.27
  Latency        1.16ms   387.24us     5.40ms
  Latency Distribution
     50%     1.07ms
     75%     1.39ms
     90%     1.73ms
     99%     2.64ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     89995.04    5759.06   94582.06
  Latency        1.09ms   419.64us     5.68ms
  Latency Distribution
     50%     0.98ms
     75%     1.39ms
     90%     1.83ms
     99%     2.82ms
### Cookie Endpoint (/cookie)
  Reqs/sec     95640.86    7304.80  103742.11
  Latency        1.03ms   311.19us     5.21ms
  Latency Distribution
     50%     0.97ms
     75%     1.25ms
     90%     1.55ms
     99%     2.39ms
### Exception Endpoint (/exc)
  Reqs/sec     92586.09    6640.29  100807.78
  Latency        1.04ms   333.21us     5.03ms
  Latency Distribution
     50%     0.96ms
     75%     1.27ms
     90%     1.61ms
     99%     2.35ms
### HTML Response (/html)
  Reqs/sec     96953.66    5200.26  100334.32
  Latency        1.01ms   340.21us     6.21ms
  Latency Distribution
     50%     0.95ms
     75%     1.26ms
     90%     1.58ms
     99%     2.38ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     27015.39    7722.56   36362.06
  Latency        3.72ms     2.16ms    23.80ms
  Latency Distribution
     50%     3.22ms
     75%     4.60ms
     90%     6.25ms
     99%    11.76ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     77100.50    5835.35   83081.73
  Latency        1.28ms   377.41us     5.11ms
  Latency Distribution
     50%     1.20ms
     75%     1.55ms
     90%     1.97ms
     99%     2.96ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17041.51    1371.74   20408.50
  Latency        5.86ms     1.73ms    14.33ms
  Latency Distribution
     50%     5.44ms
     75%     7.75ms
     90%     8.78ms
     99%    10.70ms
### Get User via Dependency (/auth/me-dependency)
 0 / 10000 [-------------------------------------------------------]   0.00% 2952 / 10000 [============>-------------------------------]  29.52% 14723/s 6026 / 10000 [==========================>-----------------]  60.26% 15021/s 9090 / 10000 [=======================================>----]  90.90% 15111/s 10000 / 10000 [===========================================] 100.00% 12460/s 10000 / 10000 [========================================] 100.00% 12459/s 0s
  Reqs/sec     15186.08     755.50   16338.50
  Latency        6.55ms     1.56ms    14.43ms
  Latency Distribution
     50%     6.31ms
     75%     8.10ms
     90%     9.16ms
     99%    10.95ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     84097.43    5527.14   90583.09
  Latency        1.16ms   367.91us     5.38ms
  Latency Distribution
     50%     1.09ms
     75%     1.44ms
     90%     1.81ms
     99%     2.69ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     99677.34    7418.26  105379.54
  Latency        0.98ms   316.62us     4.44ms
  Latency Distribution
     50%     0.91ms
     75%     1.20ms
     90%     1.53ms
     99%     2.40ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     91869.59    6253.10  100001.20
  Latency        1.08ms   370.99us     3.93ms
  Latency Distribution
     50%     0.98ms
     75%     1.38ms
     90%     1.83ms
     99%     2.73ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13949.06    1937.70   22069.12
  Latency        7.24ms     1.89ms    21.17ms
  Latency Distribution
     50%     7.13ms
     75%     8.55ms
     90%     9.97ms
     99%    13.11ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12020.28     589.45   13412.51
  Latency        8.28ms     3.15ms    22.28ms
  Latency Distribution
     50%     8.64ms
     75%    11.04ms
     90%    13.53ms
     99%    15.48ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     15897.56     787.16   17374.39
  Latency        6.26ms     1.71ms    14.08ms
  Latency Distribution
     50%     6.18ms
     75%     7.21ms
     90%     9.40ms
     99%    11.31ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13463.03    1358.62   18516.30
  Latency        7.45ms     2.60ms    21.46ms
  Latency Distribution
     50%     7.02ms
     75%     9.25ms
     90%    11.48ms
     99%    15.76ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    107484.16    7281.41  112537.04
  Latency        0.92ms   363.85us     5.54ms
  Latency Distribution
     50%   839.00us
     75%     1.11ms
     90%     1.42ms
     99%     2.32ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     75411.30   15098.76   93581.91
  Latency        1.27ms   624.80us     6.23ms
  Latency Distribution
     50%     1.09ms
     75%     1.53ms
     90%     2.09ms
     99%     4.58ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     65166.11    5680.40   69653.92
  Latency        1.52ms   560.93us     7.76ms
  Latency Distribution
     50%     1.42ms
     75%     1.84ms
     90%     2.32ms
     99%     3.70ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     96363.35    8492.85  106727.74
  Latency        1.04ms   305.58us     4.65ms
  Latency Distribution
     50%     0.97ms
     75%     1.27ms
     90%     1.60ms
     99%     2.35ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     87962.16    5565.24   95548.66
  Latency        1.13ms   408.78us     5.30ms
  Latency Distribution
     50%     1.03ms
     75%     1.39ms
     90%     1.79ms
     99%     2.97ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     98103.58    7866.29  107708.96
  Latency        1.02ms   324.03us     4.80ms
  Latency Distribution
     50%     0.95ms
     75%     1.25ms
     90%     1.58ms
     99%     2.39ms
### CBV Response Types (/cbv-response)
  Reqs/sec     99889.42    6023.63  107072.70
  Latency        0.98ms   338.52us     5.02ms
  Latency Distribution
     50%     0.91ms
     75%     1.19ms
     90%     1.51ms
     99%     2.39ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16486.47    1096.14   18747.70
  Latency        6.05ms     1.38ms    15.08ms
  Latency Distribution
     50%     5.80ms
     75%     7.04ms
     90%     8.34ms
     99%    10.55ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     95179.76    8502.89  103973.92
  Latency        1.05ms   357.01us     5.03ms
  Latency Distribution
     50%     0.97ms
     75%     1.28ms
     90%     1.65ms
     99%     2.54ms
### File Upload (POST /upload)
  Reqs/sec     87742.53    5348.78   91723.34
  Latency        1.12ms   383.49us     6.58ms
  Latency Distribution
     50%     1.04ms
     75%     1.38ms
     90%     1.78ms
     99%     2.69ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     83840.15    4198.74   88464.62
  Latency        1.18ms   403.71us     5.18ms
  Latency Distribution
     50%     1.08ms
     75%     1.45ms
     90%     1.92ms
     99%     2.98ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec     10592.22    7296.61   62386.40
  Latency       10.38ms     2.22ms    24.36ms
  Latency Distribution
     50%    10.64ms
     75%    11.95ms
     90%    13.11ms
     99%    16.73ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    100572.85    8076.02  105886.80
  Latency        0.97ms   329.30us     5.12ms
  Latency Distribution
     50%     0.90ms
     75%     1.19ms
     90%     1.47ms
     99%     2.19ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     95894.38    8521.44  104097.76
  Latency        1.01ms   284.76us     5.43ms
  Latency Distribution
     50%     0.97ms
     75%     1.24ms
     90%     1.54ms
     99%     2.19ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     88308.55    7040.47   94641.12
  Latency        1.12ms   369.90us     5.13ms
  Latency Distribution
     50%     1.04ms
     75%     1.34ms
     90%     1.69ms
     99%     2.55ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     96252.99    5835.12  100709.79
  Latency        1.02ms   310.80us     4.31ms
  Latency Distribution
     50%     0.96ms
     75%     1.27ms
     90%     1.62ms
     99%     2.39ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    111137.52   12198.00  120794.37
  Latency        0.89ms   358.66us     5.47ms
  Latency Distribution
     50%   815.00us
     75%     1.08ms
     90%     1.35ms
     99%     2.38ms

### Path Parameter - int (/items/12345)
  Reqs/sec    103467.46    7031.69  107911.20
  Latency        0.95ms   291.38us     4.41ms
  Latency Distribution
     50%     0.89ms
     75%     1.17ms
     90%     1.47ms
     99%     2.21ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    101580.58    8218.63  108152.94
  Latency        0.97ms   305.21us     4.60ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.49ms
     99%     2.32ms

### Header Parameter (/header)
  Reqs/sec    101531.34    7555.37  107142.47
  Latency        0.97ms   322.05us     4.89ms
  Latency Distribution
     50%     0.90ms
     75%     1.20ms
     90%     1.52ms
     99%     2.21ms

### Cookie Parameter (/cookie)
  Reqs/sec     98646.05    4296.27  101530.63
  Latency        0.99ms   298.15us     4.61ms
  Latency Distribution
     50%     0.94ms
     75%     1.23ms
     90%     1.54ms
     99%     2.25ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     85877.31    5467.73   89941.00
  Latency        1.14ms   304.40us     6.08ms
  Latency Distribution
     50%     1.09ms
     75%     1.40ms
     90%     1.71ms
     99%     2.29ms

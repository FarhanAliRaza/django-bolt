# Django-Bolt Benchmark
Generated: Mon Feb 23 01:40:45 AM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    110116.59    8304.53  116759.81
  Latency        0.90ms   313.65us     4.26ms
  Latency Distribution
     50%   817.00us
     75%     1.11ms
     90%     1.41ms
     99%     2.33ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     86769.23    6048.65   90197.64
  Latency        1.14ms   338.10us     4.32ms
  Latency Distribution
     50%     1.06ms
     75%     1.37ms
     90%     1.74ms
     99%     2.60ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     87270.29    6511.60   93355.05
  Latency        1.13ms   319.83us     5.13ms
  Latency Distribution
     50%     1.06ms
     75%     1.36ms
     90%     1.74ms
     99%     2.53ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    100741.90    6241.39  104903.22
  Latency        0.97ms   323.19us     4.19ms
  Latency Distribution
     50%     0.91ms
     75%     1.25ms
     90%     1.59ms
     99%     2.40ms
### Cookie Endpoint (/cookie)
  Reqs/sec    104578.18    8038.06  109293.10
  Latency        0.94ms   293.38us     6.85ms
  Latency Distribution
     50%     0.89ms
     75%     1.14ms
     90%     1.41ms
     99%     2.02ms
### Exception Endpoint (/exc)
  Reqs/sec     98406.88    6408.28  101999.48
  Latency        0.99ms   298.41us     6.09ms
  Latency Distribution
     50%     0.93ms
     75%     1.22ms
     90%     1.54ms
     99%     2.29ms
### HTML Response (/html)
  Reqs/sec    107299.67    7004.31  113350.27
  Latency        0.91ms   295.14us     5.03ms
  Latency Distribution
     50%     0.85ms
     75%     1.10ms
     90%     1.40ms
     99%     2.11ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     35803.04    8599.13   42090.26
  Latency        2.79ms     1.45ms    19.85ms
  Latency Distribution
     50%     2.52ms
     75%     3.15ms
     90%     3.85ms
     99%     9.02ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     76777.88    4633.08   80070.41
  Latency        1.28ms   329.02us     4.31ms
  Latency Distribution
     50%     1.22ms
     75%     1.53ms
     90%     1.84ms
     99%     2.72ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17279.16    1389.51   18467.73
  Latency        5.76ms     1.53ms    13.88ms
  Latency Distribution
     50%     5.57ms
     75%     7.03ms
     90%     8.20ms
     99%    10.71ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     14934.07    1209.66   15984.46
  Latency        6.58ms     2.57ms    16.95ms
  Latency Distribution
     50%     6.34ms
     75%     8.23ms
     90%    10.49ms
     99%    14.10ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     85814.16    5927.68   92026.41
  Latency        1.14ms   332.33us     4.94ms
  Latency Distribution
     50%     1.07ms
     75%     1.40ms
     90%     1.74ms
     99%     2.50ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    103820.70    6020.22  109860.57
  Latency        0.95ms   277.10us     4.88ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.44ms
     99%     2.06ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     96123.89    6718.77  102176.61
  Latency        1.01ms   320.23us     4.94ms
  Latency Distribution
     50%     0.93ms
     75%     1.26ms
     90%     1.57ms
     99%     2.39ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13696.94     841.99   15838.49
  Latency        7.28ms     1.47ms    18.30ms
  Latency Distribution
     50%     7.52ms
     75%     8.70ms
     90%     9.36ms
     99%    10.51ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec      9735.29     965.28   11947.85
  Latency       10.26ms     4.51ms    36.39ms
  Latency Distribution
     50%     9.18ms
     75%    13.14ms
     90%    17.01ms
     99%    25.25ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     15825.13     725.31   18045.51
  Latency        6.30ms     1.31ms    11.78ms
  Latency Distribution
     50%     6.50ms
     75%     7.49ms
     90%     8.25ms
     99%     9.50ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     11978.84     748.43   14751.21
  Latency        8.33ms     3.42ms    30.74ms
  Latency Distribution
     50%     7.50ms
     75%     9.81ms
     90%    13.38ms
     99%    20.67ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    107932.75    7841.30  112087.29
  Latency        0.92ms   282.33us     4.25ms
  Latency Distribution
     50%     0.87ms
     75%     1.13ms
     90%     1.43ms
     99%     2.12ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    102900.53    7582.50  107330.44
  Latency        0.96ms   282.25us     3.88ms
  Latency Distribution
     50%     0.89ms
     75%     1.16ms
     90%     1.47ms
     99%     2.26ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     64737.64    3129.69   67929.28
  Latency        1.52ms   460.36us     5.46ms
  Latency Distribution
     50%     1.50ms
     75%     1.90ms
     90%     2.38ms
     99%     3.30ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     99889.09    7552.17  112386.85
  Latency        1.01ms   333.82us     4.02ms
  Latency Distribution
     50%     0.93ms
     75%     1.31ms
     90%     1.70ms
     99%     2.48ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    100512.27    9496.58  117180.61
  Latency        1.01ms   295.90us     3.97ms
  Latency Distribution
     50%     0.94ms
     75%     1.26ms
     90%     1.58ms
     99%     2.34ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    110943.24   30812.11  172747.37
  Latency        0.99ms   318.04us     4.74ms
  Latency Distribution
     50%     0.91ms
     75%     1.22ms
     90%     1.59ms
     99%     2.37ms
### CBV Response Types (/cbv-response)
  Reqs/sec    102551.66    7925.86  107267.95
  Latency        0.96ms   304.74us     6.11ms
  Latency Distribution
     50%     0.89ms
     75%     1.16ms
     90%     1.47ms
     99%     2.11ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16292.09    1106.34   18275.92
  Latency        6.11ms     1.15ms    16.35ms
  Latency Distribution
     50%     5.89ms
     75%     7.05ms
     90%     8.11ms
     99%     9.69ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    100525.36   10379.03  115439.08
  Latency        1.00ms   288.45us     4.91ms
  Latency Distribution
     50%     0.94ms
     75%     1.22ms
     90%     1.54ms
     99%     2.21ms
### File Upload (POST /upload)
  Reqs/sec     86146.06    5247.91   92232.73
  Latency        1.14ms   372.46us     4.87ms
  Latency Distribution
     50%     1.05ms
     75%     1.43ms
     90%     1.84ms
     99%     2.75ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     85607.69    4921.89   89481.57
  Latency        1.15ms   353.87us     4.01ms
  Latency Distribution
     50%     1.08ms
     75%     1.41ms
     90%     1.74ms
     99%     2.76ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9700.28     869.48   11145.83
  Latency       10.29ms     2.49ms    22.87ms
  Latency Distribution
     50%    10.16ms
     75%    12.52ms
     90%    13.91ms
     99%    17.13ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    100606.80    7630.70  106060.37
  Latency        0.98ms   341.22us     5.35ms
  Latency Distribution
     50%     0.90ms
     75%     1.18ms
     90%     1.49ms
     99%     2.55ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     98513.77    7046.26  103754.69
  Latency        1.00ms   277.51us     5.97ms
  Latency Distribution
     50%     0.94ms
     75%     1.23ms
     90%     1.50ms
     99%     2.14ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     86842.98    6264.29   91637.11
  Latency        1.14ms   330.28us     4.59ms
  Latency Distribution
     50%     1.08ms
     75%     1.41ms
     90%     1.74ms
     99%     2.44ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     95249.07    6138.39   99879.80
  Latency        1.03ms   308.86us     4.66ms
  Latency Distribution
     50%     0.96ms
     75%     1.25ms
     90%     1.58ms
     99%     2.30ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    112764.41    7946.91  117946.09
  Latency        0.87ms   308.91us     5.03ms
  Latency Distribution
     50%   805.00us
     75%     1.05ms
     90%     1.36ms
     99%     2.10ms

### Path Parameter - int (/items/12345)
  Reqs/sec    105230.96    6654.38  109346.00
  Latency        0.93ms   293.99us     4.89ms
  Latency Distribution
     50%     0.88ms
     75%     1.13ms
     90%     1.39ms
     99%     2.13ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    104083.26    8294.19  109679.80
  Latency        0.94ms   287.00us     4.50ms
  Latency Distribution
     50%     0.88ms
     75%     1.14ms
     90%     1.45ms
     99%     2.12ms

### Header Parameter (/header)
  Reqs/sec    104843.64    8026.13  109392.29
  Latency        0.94ms   316.16us     4.88ms
  Latency Distribution
     50%   845.00us
     75%     1.17ms
     90%     1.56ms
     99%     2.29ms

### Cookie Parameter (/cookie)
  Reqs/sec    106025.54    6564.33  111943.64
  Latency        0.93ms   265.10us     3.47ms
  Latency Distribution
     50%     0.87ms
     75%     1.14ms
     90%     1.43ms
     99%     2.07ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     86248.33    5370.52   90203.53
  Latency        1.14ms   357.05us     5.86ms
  Latency Distribution
     50%     1.09ms
     75%     1.41ms
     90%     1.75ms
     99%     2.65ms

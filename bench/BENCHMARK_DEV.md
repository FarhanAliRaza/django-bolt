# Django-Bolt Benchmark
Generated: Sun Feb 22 09:48:38 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    112400.72    7910.95  117578.90
  Latency        0.88ms   286.09us     5.12ms
  Latency Distribution
     50%   815.00us
     75%     1.07ms
     90%     1.34ms
     99%     2.02ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     87449.03    6534.42   91642.53
  Latency        1.13ms   307.97us     4.81ms
  Latency Distribution
     50%     1.06ms
     75%     1.35ms
     90%     1.66ms
     99%     2.52ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     85601.10    5063.94   88654.14
  Latency        1.15ms   319.74us     4.44ms
  Latency Distribution
     50%     1.10ms
     75%     1.42ms
     90%     1.74ms
     99%     2.44ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    102700.03    7416.20  108134.94
  Latency        0.96ms   277.60us     5.40ms
  Latency Distribution
     50%     0.90ms
     75%     1.16ms
     90%     1.46ms
     99%     2.13ms
### Cookie Endpoint (/cookie)
  Reqs/sec    103430.64    5633.80  108013.28
  Latency        0.95ms   274.01us     4.83ms
  Latency Distribution
     50%     0.89ms
     75%     1.16ms
     90%     1.42ms
     99%     2.13ms
### Exception Endpoint (/exc)
  Reqs/sec     96856.17    5833.02  102517.23
  Latency        1.01ms   277.35us     4.25ms
  Latency Distribution
     50%     0.96ms
     75%     1.22ms
     90%     1.49ms
     99%     2.18ms
### HTML Response (/html)
  Reqs/sec    109540.52    6684.87  114804.64
  Latency        0.90ms   222.70us     4.82ms
  Latency Distribution
     50%   844.00us
     75%     1.09ms
     90%     1.36ms
     99%     1.86ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     35397.88    8330.51   41425.39
  Latency        2.84ms     1.63ms    21.49ms
  Latency Distribution
     50%     2.52ms
     75%     3.49ms
     90%     4.45ms
     99%     9.32ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     77521.21    5674.09   81845.46
  Latency        1.27ms   311.41us     6.54ms
  Latency Distribution
     50%     1.21ms
     75%     1.52ms
     90%     1.86ms
     99%     2.58ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17522.30    1347.22   19956.90
  Latency        5.69ms     1.36ms    13.20ms
  Latency Distribution
     50%     5.55ms
     75%     6.88ms
     90%     7.75ms
     99%     9.76ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15323.20     743.45   16059.20
  Latency        6.49ms     2.16ms    14.35ms
  Latency Distribution
     50%     6.50ms
     75%     8.28ms
     90%     9.67ms
     99%    12.37ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     84667.56    5205.81   89098.66
  Latency        1.16ms   363.54us     5.21ms
  Latency Distribution
     50%     1.07ms
     75%     1.42ms
     90%     1.81ms
     99%     2.73ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    103793.05    6120.14  107209.59
  Latency        0.95ms   263.44us     4.21ms
  Latency Distribution
     50%     0.90ms
     75%     1.16ms
     90%     1.45ms
     99%     2.04ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     95347.96    4909.64   99022.06
  Latency        1.03ms   337.46us     4.18ms
  Latency Distribution
     50%     0.96ms
     75%     1.28ms
     90%     1.65ms
     99%     2.50ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13609.70    1642.93   15112.57
  Latency        7.19ms     1.40ms    20.40ms
  Latency Distribution
     50%     7.43ms
     75%     8.31ms
     90%     8.97ms
     99%    10.41ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec      4567.10     428.55    5683.23
  Latency       21.82ms     6.11ms    50.03ms
  Latency Distribution
     50%    20.90ms
     75%    25.90ms
     90%    30.72ms
     99%    39.15ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     16041.64     803.36   17160.05
  Latency        6.20ms     1.47ms    13.28ms
  Latency Distribution
     50%     6.27ms
     75%     7.53ms
     90%     8.49ms
     99%     9.98ms
### Users Mini10 (Sync) (/users/sync-mini10)
 0 / 10000 [-----------------------------------------------------------]   0.00% 2630 / 10000 [============>-----------------------------------]  26.30% 13115/s 5390 / 10000 [=========================>----------------------]  53.90% 13448/s 8142 / 10000 [=======================================>--------]  81.42% 13540/s 10000 / 10000 [===============================================] 100.00% 12462/s 10000 / 10000 [============================================] 100.00% 12460/s 0s
  Reqs/sec     13560.89    1137.55   15521.16
  Latency        7.32ms     3.73ms    30.31ms
  Latency Distribution
     50%     6.08ms
     75%     9.38ms
     90%    13.39ms
     99%    20.03ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    109820.51    7029.73  115118.15
  Latency        0.90ms   287.36us     4.31ms
  Latency Distribution
     50%   834.00us
     75%     1.09ms
     90%     1.37ms
     99%     2.14ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    102247.89    7042.85  108388.17
  Latency        0.96ms   268.19us     5.07ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.47ms
     99%     2.07ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     68106.55    5728.33   78468.82
  Latency        1.47ms   356.08us     4.24ms
  Latency Distribution
     50%     1.39ms
     75%     1.75ms
     90%     2.11ms
     99%     2.99ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    101036.18    6474.37  104757.36
  Latency        0.97ms   290.32us     4.60ms
  Latency Distribution
     50%     0.91ms
     75%     1.20ms
     90%     1.47ms
     99%     2.12ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    102656.73   13976.31  127128.44
  Latency        1.00ms   305.98us     6.24ms
  Latency Distribution
     50%     0.92ms
     75%     1.21ms
     90%     1.54ms
     99%     2.22ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     97727.19    7688.17  106123.04
  Latency        1.00ms   326.38us     5.84ms
  Latency Distribution
     50%     0.94ms
     75%     1.22ms
     90%     1.52ms
     99%     2.29ms
### CBV Response Types (/cbv-response)
  Reqs/sec    105064.56    8726.43  110332.56
  Latency        0.94ms   293.29us     5.00ms
  Latency Distribution
     50%     0.88ms
     75%     1.15ms
     90%     1.44ms
     99%     2.15ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16404.68    1084.96   18328.75
  Latency        6.06ms     1.45ms    17.37ms
  Latency Distribution
     50%     6.14ms
     75%     7.41ms
     90%     8.29ms
     99%     9.81ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    101948.79   12776.26  124406.19
  Latency        1.01ms   349.54us     4.72ms
  Latency Distribution
     50%     0.93ms
     75%     1.20ms
     90%     1.54ms
     99%     2.56ms
### File Upload (POST /upload)
  Reqs/sec     86638.04    5392.13   90041.88
  Latency        1.13ms   401.38us     6.41ms
  Latency Distribution
     50%     1.04ms
     75%     1.41ms
     90%     1.79ms
     99%     2.90ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     84377.55    6200.43   88184.64
  Latency        1.17ms   417.93us     5.53ms
  Latency Distribution
     50%     1.06ms
     75%     1.48ms
     90%     1.94ms
     99%     2.92ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
 0 / 10000 [-----------------------------------------------------------]   0.00% 1853 / 10000 [=========>---------------------------------------]  18.53% 9238/s 3816 / 10000 [==================>------------------------------]  38.16% 9522/s 5775 / 10000 [============================>--------------------]  57.75% 9607/s 7756 / 10000 [======================================>----------]  77.56% 9676/s 9739 / 10000 [===============================================>-]  97.39% 9719/s 10000 / 10000 [================================================] 100.00% 8312/s 10000 / 10000 [=============================================] 100.00% 8311/s 1s
  Reqs/sec      9699.41     994.99   11147.96
  Latency       10.20ms     2.69ms    24.13ms
  Latency Distribution
     50%     9.57ms
     75%    11.82ms
     90%    14.46ms
     99%    19.31ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    102594.72    9280.10  107554.88
  Latency        0.95ms   297.21us     4.76ms
  Latency Distribution
     50%     0.90ms
     75%     1.15ms
     90%     1.43ms
     99%     2.18ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     94501.57    8558.30  101310.54
  Latency        1.01ms   339.21us     4.97ms
  Latency Distribution
     50%     0.93ms
     75%     1.26ms
     90%     1.61ms
     99%     2.38ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     89077.21    6902.51   94365.67
  Latency        1.10ms   353.65us     5.03ms
  Latency Distribution
     50%     1.02ms
     75%     1.33ms
     90%     1.67ms
     99%     2.63ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     96758.59    8575.58  104037.20
  Latency        1.03ms   320.80us     4.97ms
  Latency Distribution
     50%     0.95ms
     75%     1.26ms
     90%     1.58ms
     99%     2.39ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    111315.20    9569.24  118695.68
  Latency        0.88ms   321.37us     5.84ms
  Latency Distribution
     50%   815.00us
     75%     1.08ms
     90%     1.35ms
     99%     2.13ms

### Path Parameter - int (/items/12345)
  Reqs/sec    104554.08    8023.42  113450.08
  Latency        0.95ms   271.62us     3.73ms
  Latency Distribution
     50%     0.89ms
     75%     1.16ms
     90%     1.47ms
     99%     2.15ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    102300.83    8050.47  107916.96
  Latency        0.96ms   273.40us     3.75ms
  Latency Distribution
     50%     0.92ms
     75%     1.18ms
     90%     1.43ms
     99%     2.11ms

### Header Parameter (/header)
  Reqs/sec    103149.82    7636.81  107655.48
  Latency        0.95ms   292.86us     5.38ms
  Latency Distribution
     50%     0.89ms
     75%     1.18ms
     90%     1.51ms
     99%     2.26ms

### Cookie Parameter (/cookie)
  Reqs/sec    102282.19    7587.33  109357.57
  Latency        0.96ms   296.75us     4.54ms
  Latency Distribution
     50%     0.91ms
     75%     1.20ms
     90%     1.51ms
     99%     2.24ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     83588.21    4932.77   87480.52
  Latency        1.17ms   325.47us     5.54ms
  Latency Distribution
     50%     1.11ms
     75%     1.43ms
     90%     1.76ms
     99%     2.50ms

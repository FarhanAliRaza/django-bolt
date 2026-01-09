# Django-Bolt Benchmark
Generated: Fri Jan  9 09:00:30 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    124109.97   11801.15  132835.85
  Latency      790.98us   269.56us     4.55ms
  Latency Distribution
     50%   732.00us
     75%     0.98ms
     90%     1.24ms
     99%     2.00ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec    100363.20   10067.35  105503.73
  Latency        0.97ms   304.70us     6.25ms
  Latency Distribution
     50%     0.92ms
     75%     1.16ms
     90%     1.44ms
     99%     2.18ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec    100371.93    9545.84  108317.01
  Latency        0.97ms   282.86us     4.43ms
  Latency Distribution
     50%     0.91ms
     75%     1.18ms
     90%     1.47ms
     99%     2.19ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    129070.43   24688.83  169415.22
  Latency      817.45us   263.78us     5.17ms
  Latency Distribution
     50%   763.00us
     75%     0.99ms
     90%     1.23ms
     99%     1.88ms
### Cookie Endpoint (/cookie)
  Reqs/sec    124541.62   14220.34  143591.51
  Latency      812.66us   245.38us     3.95ms
  Latency Distribution
     50%   759.00us
     75%     0.99ms
     90%     1.25ms
     99%     1.94ms
### Exception Endpoint (/exc)
  Reqs/sec    122362.98   10409.53  133668.25
  Latency      813.97us   244.76us     4.79ms
  Latency Distribution
     50%   764.00us
     75%     0.98ms
     90%     1.23ms
     99%     1.87ms
### HTML Response (/html)
  Reqs/sec    125359.04   11661.08  134417.51
  Latency      771.26us   265.82us     4.27ms
  Latency Distribution
     50%   712.00us
     75%     0.94ms
     90%     1.20ms
     99%     1.92ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     36780.09    9026.31   43972.57
  Latency        2.71ms     1.52ms    19.32ms
  Latency Distribution
     50%     2.43ms
     75%     3.13ms
     90%     3.98ms
     99%     8.97ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     86951.37    8255.12   91089.03
  Latency        1.11ms   311.43us     4.82ms
  Latency Distribution
     50%     1.03ms
     75%     1.34ms
     90%     1.70ms
     99%     2.46ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     18665.64    1618.90   20457.01
  Latency        5.33ms     1.28ms    15.16ms
  Latency Distribution
     50%     5.32ms
     75%     6.08ms
     90%     7.34ms
     99%     9.39ms
### Get User via Dependency (/auth/me-dependency)
 0 / 10000 [---------------------------------------------------------------]   0.00% 3289 / 10000 [=================>----------------------------------]  32.89% 16414/s 6699 / 10000 [==================================>-----------------]  66.99% 16726/s 10000 / 10000 [===================================================] 100.00% 16635/s 10000 / 10000 [================================================] 100.00% 16633/s 0s
  Reqs/sec     16989.25    1106.68   20371.94
  Latency        5.87ms     1.64ms    14.60ms
  Latency Distribution
     50%     5.70ms
     75%     7.13ms
     90%     8.54ms
     99%    10.93ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     90121.48    8935.39  101351.09
  Latency        1.07ms   321.81us     6.24ms
  Latency Distribution
     50%     1.01ms
     75%     1.32ms
     90%     1.66ms
     99%     2.38ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    108236.40    9528.36  117379.11
  Latency        0.91ms   306.70us     4.41ms
  Latency Distribution
     50%   828.00us
     75%     1.15ms
     90%     1.49ms
     99%     2.37ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec    110181.93    8505.72  115381.47
  Latency        0.89ms   301.47us     3.80ms
  Latency Distribution
     50%   826.00us
     75%     1.07ms
     90%     1.38ms
     99%     2.16ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     15301.57    1792.19   16794.36
  Latency        6.40ms     2.08ms    15.19ms
  Latency Distribution
     50%     6.22ms
     75%     7.91ms
     90%     9.84ms
     99%    12.74ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     13276.65    1886.52   16341.46
  Latency        7.48ms     5.82ms    70.39ms
  Latency Distribution
     50%     6.69ms
     75%     8.10ms
     90%    10.16ms
     99%    18.21ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     18136.90     757.68   19179.26
  Latency        5.48ms     1.46ms    12.59ms
  Latency Distribution
     50%     5.37ms
     75%     6.64ms
     90%     7.72ms
     99%    10.01ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     17336.07    2649.44   22081.74
  Latency        5.74ms     2.32ms    20.78ms
  Latency Distribution
     50%     5.21ms
     75%     7.07ms
     90%     9.24ms
     99%    13.99ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    111684.39    8299.49  119999.81
  Latency        0.88ms   303.97us     4.29ms
  Latency Distribution
     50%   797.00us
     75%     1.08ms
     90%     1.40ms
     99%     2.25ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    108579.34    7837.22  113942.04
  Latency        0.91ms   306.28us     4.93ms
  Latency Distribution
     50%   845.00us
     75%     1.11ms
     90%     1.41ms
     99%     2.13ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     71013.32    5229.30   78268.71
  Latency        1.39ms   451.13us     5.77ms
  Latency Distribution
     50%     1.26ms
     75%     1.69ms
     90%     2.18ms
     99%     3.46ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     56703.07    7421.57   69196.07
  Latency        1.73ms     0.92ms     9.78ms
  Latency Distribution
     50%     1.47ms
     75%     2.21ms
     90%     3.06ms
     99%     5.45ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     84406.28   19805.90  106547.53
  Latency        1.17ms   580.91us     8.07ms
  Latency Distribution
     50%     1.02ms
     75%     1.41ms
     90%     1.85ms
     99%     4.19ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     90193.63   12506.01  106146.89
  Latency        1.08ms   404.12us     4.54ms
  Latency Distribution
     50%     1.00ms
     75%     1.34ms
     90%     1.69ms
     99%     3.09ms
### CBV Response Types (/cbv-response)
  Reqs/sec    112868.79   10449.21  122183.68
  Latency        0.85ms   309.31us     4.32ms
  Latency Distribution
     50%   784.00us
     75%     1.03ms
     90%     1.35ms
     99%     2.25ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     17188.62    3498.98   20022.18
  Latency        5.60ms     4.37ms    73.68ms
  Latency Distribution
     50%     4.92ms
     75%     6.56ms
     90%     8.66ms
     99%    12.75ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    110490.37    7772.31  117268.58
  Latency        0.88ms   256.75us     3.84ms
  Latency Distribution
     50%   826.00us
     75%     1.07ms
     90%     1.36ms
     99%     2.00ms
### File Upload (POST /upload)
  Reqs/sec     99355.41    6584.52  106295.73
  Latency        0.98ms   335.12us     4.81ms
  Latency Distribution
     50%     0.90ms
     75%     1.22ms
     90%     1.60ms
     99%     2.59ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     95626.69   10617.95  106318.31
  Latency        0.97ms   297.77us     3.42ms
  Latency Distribution
     50%     0.90ms
     75%     1.19ms
     90%     1.52ms
     99%     2.33ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec     14318.71    4034.76   17465.27
  Latency        6.72ms     6.04ms    81.25ms
  Latency Distribution
     50%     6.44ms
     75%     7.56ms
     90%     8.32ms
     99%    15.37ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    118977.16    9705.77  127220.47
  Latency      837.08us   273.29us     3.88ms
  Latency Distribution
     50%   770.00us
     75%     1.01ms
     90%     1.27ms
     99%     1.98ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec    115331.88   11547.51  125201.93
  Latency        0.86ms   283.18us     5.07ms
  Latency Distribution
     50%   783.00us
     75%     1.04ms
     90%     1.30ms
     99%     2.16ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec    103289.98    8930.33  109704.17
  Latency        0.95ms   270.06us     4.36ms
  Latency Distribution
     50%     0.87ms
     75%     1.20ms
     90%     1.52ms
     99%     2.18ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    112886.47    8490.33  118134.32
  Latency        0.87ms   300.49us     5.34ms
  Latency Distribution
     50%   796.00us
     75%     1.04ms
     90%     1.35ms
     99%     2.23ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    129848.94   11391.02  139100.48
  Latency      758.58us   264.26us     4.12ms
  Latency Distribution
     50%   692.00us
     75%     0.93ms
     90%     1.18ms
     99%     2.03ms

### Path Parameter - int (/items/12345)
  Reqs/sec    119775.86    9802.14  127586.33
  Latency      810.63us   276.57us     5.28ms
  Latency Distribution
     50%   745.00us
     75%     0.99ms
     90%     1.23ms
     99%     1.85ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    117747.22   11540.74  126858.26
  Latency      808.30us   316.62us     7.99ms
  Latency Distribution
     50%   748.00us
     75%     1.01ms
     90%     1.28ms
     99%     1.98ms

### Header Parameter (/header)
  Reqs/sec    120123.12    8996.95  124445.04
  Latency      815.30us   263.93us     5.31ms
  Latency Distribution
     50%   759.00us
     75%     1.00ms
     90%     1.29ms
     99%     1.98ms

### Cookie Parameter (/cookie)
  Reqs/sec    115852.32   12737.41  126707.35
  Latency      807.89us   218.73us     5.34ms
  Latency Distribution
     50%   759.00us
     75%     0.97ms
     90%     1.22ms
     99%     1.74ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     99615.41    7362.10  105019.12
  Latency        0.98ms   303.95us     4.13ms
  Latency Distribution
     50%     0.91ms
     75%     1.22ms
     90%     1.55ms
     99%     2.29ms

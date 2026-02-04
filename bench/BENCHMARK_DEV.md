# Django-Bolt Benchmark
Generated: Wed 04 Feb 2026 08:19:38 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    112788.51    8644.31  120980.03
  Latency        0.88ms   253.54us     4.00ms
  Latency Distribution
     50%   830.00us
     75%     1.06ms
     90%     1.34ms
     99%     2.03ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     89086.28    6698.70   93815.05
  Latency        1.11ms   303.29us     4.21ms
  Latency Distribution
     50%     1.04ms
     75%     1.33ms
     90%     1.63ms
     99%     2.46ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     89088.15    6429.87   95685.37
  Latency        1.11ms   363.18us     6.57ms
  Latency Distribution
     50%     1.02ms
     75%     1.32ms
     90%     1.71ms
     99%     2.62ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    101722.79    9092.65  109868.56
  Latency        0.97ms   363.78us     5.38ms
  Latency Distribution
     50%     0.88ms
     75%     1.18ms
     90%     1.53ms
     99%     2.43ms
### Cookie Endpoint (/cookie)
  Reqs/sec    104399.59    6578.20  108877.54
  Latency        0.94ms   327.94us     5.50ms
  Latency Distribution
     50%     0.87ms
     75%     1.13ms
     90%     1.41ms
     99%     2.23ms
### Exception Endpoint (/exc)
  Reqs/sec    101547.82    6904.05  105610.41
  Latency        0.97ms   291.69us     4.25ms
  Latency Distribution
     50%     0.90ms
     75%     1.16ms
     90%     1.48ms
     99%     2.18ms
### HTML Response (/html)
  Reqs/sec    110881.76    6203.17  115438.51
  Latency        0.89ms   284.43us     5.11ms
  Latency Distribution
     50%   825.00us
     75%     1.09ms
     90%     1.39ms
     99%     2.03ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     32192.92    7325.18   39284.41
  Latency        3.11ms     1.44ms    17.31ms
  Latency Distribution
     50%     2.84ms
     75%     3.69ms
     90%     4.66ms
     99%     8.73ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     80510.80    6871.65   87482.07
  Latency        1.23ms   410.89us     5.91ms
  Latency Distribution
     50%     1.11ms
     75%     1.53ms
     90%     2.01ms
     99%     3.03ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17527.10    1363.36   18536.20
  Latency        5.67ms     1.40ms    14.01ms
  Latency Distribution
     50%     5.19ms
     75%     6.84ms
     90%     8.26ms
     99%    10.23ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15580.66     727.91   16292.42
  Latency        6.37ms     2.13ms    15.15ms
  Latency Distribution
     50%     6.40ms
     75%     8.16ms
     90%     9.75ms
     99%    11.98ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     86534.38    6918.30   93020.47
  Latency        1.13ms   335.75us     4.86ms
  Latency Distribution
     50%     1.08ms
     75%     1.39ms
     90%     1.72ms
     99%     2.50ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    101499.32    8379.60  109184.49
  Latency        0.97ms   340.15us     4.61ms
  Latency Distribution
     50%     0.88ms
     75%     1.20ms
     90%     1.51ms
     99%     2.45ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     98313.58    7258.05  104475.53
  Latency        1.01ms   296.16us     4.12ms
  Latency Distribution
     50%     0.95ms
     75%     1.24ms
     90%     1.57ms
     99%     2.29ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     14175.62    1074.35   17948.90
  Latency        7.05ms     1.75ms    16.80ms
  Latency Distribution
     50%     7.12ms
     75%     8.14ms
     90%     9.76ms
     99%    11.53ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12539.38     643.66   14225.60
  Latency        7.94ms     2.69ms    19.26ms
  Latency Distribution
     50%     7.59ms
     75%    10.61ms
     90%    12.06ms
     99%    14.71ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     16315.87     740.06   18610.23
  Latency        6.11ms     2.01ms    13.91ms
  Latency Distribution
     50%     5.76ms
     75%     7.90ms
     90%     9.58ms
     99%    11.26ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13489.97    1153.32   16207.26
  Latency        7.41ms     2.68ms    26.50ms
  Latency Distribution
     50%     6.95ms
     75%     9.05ms
     90%    11.30ms
     99%    16.36ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    108978.80    9559.33  118862.05
  Latency        0.90ms   315.59us     4.37ms
  Latency Distribution
     50%   846.00us
     75%     1.07ms
     90%     1.35ms
     99%     2.37ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    102459.84    9798.23  108680.25
  Latency        0.96ms   295.27us     4.10ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.47ms
     99%     2.27ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     67390.93    3991.67   70137.64
  Latency        1.47ms   487.25us     5.04ms
  Latency Distribution
     50%     1.35ms
     75%     1.82ms
     90%     2.31ms
     99%     3.66ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     86326.05   27981.40  103566.25
  Latency        1.00ms   280.92us     4.42ms
  Latency Distribution
     50%     0.95ms
     75%     1.23ms
     90%     1.52ms
     99%     2.17ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     97663.28    9179.63  111633.66
  Latency        1.03ms   342.36us     4.36ms
  Latency Distribution
     50%     0.95ms
     75%     1.27ms
     90%     1.62ms
     99%     2.64ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     98502.64    7279.52  103197.51
  Latency        0.99ms   301.00us     4.93ms
  Latency Distribution
     50%     0.93ms
     75%     1.20ms
     90%     1.50ms
     99%     2.20ms
### CBV Response Types (/cbv-response)
  Reqs/sec    102691.89    7454.42  108256.46
  Latency        0.95ms   336.22us     5.01ms
  Latency Distribution
     50%     0.86ms
     75%     1.18ms
     90%     1.55ms
     99%     2.30ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16865.63    1139.85   19116.79
  Latency        5.91ms     1.27ms    13.95ms
  Latency Distribution
     50%     5.86ms
     75%     6.88ms
     90%     7.91ms
     99%     9.76ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     96945.82    7144.31  103876.19
  Latency        1.03ms   358.53us     4.49ms
  Latency Distribution
     50%     0.94ms
     75%     1.27ms
     90%     1.60ms
     99%     2.80ms
### File Upload (POST /upload)
  Reqs/sec     84466.56    4185.79   89623.74
  Latency        1.16ms   344.25us     4.71ms
  Latency Distribution
     50%     1.10ms
     75%     1.41ms
     90%     1.80ms
     99%     2.64ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     79904.13    5236.29   88452.43
  Latency        1.25ms   404.22us     4.91ms
  Latency Distribution
     50%     1.16ms
     75%     1.51ms
     90%     1.98ms
     99%     3.00ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
 0 / 10000 [-------------------------------------------------------]   0.00% 1792 / 10000 [========>------------------------------------]  17.92% 8934/s 3662 / 10000 [================>----------------------------]  36.62% 9138/s 5581 / 10000 [=========================>-------------------]  55.81% 9287/s 7450 / 10000 [=================================>-----------]  74.50% 9296/s 9368 / 10000 [==========================================>--]  93.68% 9353/s 10000 / 10000 [============================================] 100.00% 8315/s 10000 / 10000 [=========================================] 100.00% 8314/s 1s
  Reqs/sec      9392.06     865.18   10396.81
  Latency       10.62ms     2.72ms    28.15ms
  Latency Distribution
     50%    10.18ms
     75%    11.66ms
     90%    15.56ms
     99%    19.22ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    101059.07    9584.48  108278.37
  Latency        0.97ms   355.27us     6.51ms
  Latency Distribution
     50%     0.91ms
     75%     1.17ms
     90%     1.46ms
     99%     2.33ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     97837.85    7566.39  104520.57
  Latency        1.00ms   306.78us     6.16ms
  Latency Distribution
     50%     0.95ms
     75%     1.20ms
     90%     1.50ms
     99%     2.19ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     88906.45    7415.97   93986.73
  Latency        1.11ms   360.00us     4.91ms
  Latency Distribution
     50%     1.04ms
     75%     1.33ms
     90%     1.65ms
     99%     2.51ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     97451.29    5217.65  100737.95
  Latency        1.01ms   288.16us     5.01ms
  Latency Distribution
     50%     0.95ms
     75%     1.26ms
     90%     1.57ms
     99%     2.25ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    111734.09   11457.26  120261.78
  Latency        0.89ms   339.74us     6.51ms
  Latency Distribution
     50%   822.00us
     75%     1.07ms
     90%     1.32ms
     99%     2.44ms

### Path Parameter - int (/items/12345)
  Reqs/sec    105746.90    7297.75  112323.59
  Latency        0.93ms   306.61us     4.52ms
  Latency Distribution
     50%     0.87ms
     75%     1.12ms
     90%     1.41ms
     99%     2.16ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    101421.52    7632.47  108668.24
  Latency        0.97ms   289.46us     4.35ms
  Latency Distribution
     50%     0.91ms
     75%     1.19ms
     90%     1.49ms
     99%     2.19ms

### Header Parameter (/header)
  Reqs/sec    101479.27    8658.53  108450.86
  Latency        0.97ms   345.91us     5.39ms
  Latency Distribution
     50%     0.91ms
     75%     1.16ms
     90%     1.49ms
     99%     2.37ms

### Cookie Parameter (/cookie)
  Reqs/sec    102009.24    8021.43  108576.01
  Latency        0.96ms   320.60us     4.83ms
  Latency Distribution
     50%     0.90ms
     75%     1.18ms
     90%     1.51ms
     99%     2.23ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     85985.80    4955.65   89964.09
  Latency        1.13ms   377.35us     4.26ms
  Latency Distribution
     50%     1.04ms
     75%     1.39ms
     90%     1.79ms
     99%     2.79ms

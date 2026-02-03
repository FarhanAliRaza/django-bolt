# Django-Bolt Benchmark
Generated: Tue 03 Feb 2026 10:38:08 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    110089.64    8608.02  117685.64
  Latency        0.90ms   337.51us     5.38ms
  Latency Distribution
     50%   828.00us
     75%     1.11ms
     90%     1.40ms
     99%     2.20ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     89825.69    6071.40   94703.17
  Latency        1.10ms   323.34us     5.08ms
  Latency Distribution
     50%     1.03ms
     75%     1.31ms
     90%     1.60ms
     99%     2.38ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     87255.04    6067.12   91033.47
  Latency        1.13ms   350.89us     5.77ms
  Latency Distribution
     50%     1.05ms
     75%     1.38ms
     90%     1.71ms
     99%     2.52ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    100456.14    7207.37  107751.14
  Latency        0.98ms   281.31us     5.00ms
  Latency Distribution
     50%     0.93ms
     75%     1.20ms
     90%     1.49ms
     99%     2.13ms
### Cookie Endpoint (/cookie)
  Reqs/sec    104390.78    6078.66  107948.18
  Latency        0.94ms   297.32us     3.89ms
  Latency Distribution
     50%     0.88ms
     75%     1.14ms
     90%     1.45ms
     99%     2.27ms
### Exception Endpoint (/exc)
  Reqs/sec    101018.93    7251.42  106340.28
  Latency        0.97ms   311.20us     4.88ms
  Latency Distribution
     50%     0.91ms
     75%     1.20ms
     90%     1.51ms
     99%     2.33ms
### HTML Response (/html)
  Reqs/sec    107739.65    7657.98  113332.02
  Latency        0.91ms   320.68us     5.82ms
  Latency Distribution
     50%   830.00us
     75%     1.14ms
     90%     1.47ms
     99%     2.20ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     20332.27   10558.33   40313.94
  Latency        5.05ms    22.40ms   284.98ms
  Latency Distribution
     50%     2.39ms
     75%     3.63ms
     90%     5.13ms
     99%    44.85ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     85397.38    7564.74   90312.65
  Latency        1.16ms   377.87us     5.46ms
  Latency Distribution
     50%     1.07ms
     75%     1.41ms
     90%     1.79ms
     99%     2.84ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17219.42    1190.54   18731.39
  Latency        5.78ms     1.24ms    13.54ms
  Latency Distribution
     50%     5.63ms
     75%     6.80ms
     90%     7.86ms
     99%     9.57ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     14923.69    1250.58   15824.45
  Latency        6.58ms     1.96ms    16.21ms
  Latency Distribution
     50%     6.43ms
     75%     8.24ms
     90%     9.74ms
     99%    11.77ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     82989.08    5254.96   89895.44
  Latency        1.18ms   416.04us     5.18ms
  Latency Distribution
     50%     1.09ms
     75%     1.47ms
     90%     1.90ms
     99%     2.90ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    100531.74    5845.95  105341.54
  Latency        0.98ms   327.70us     4.79ms
  Latency Distribution
     50%     0.91ms
     75%     1.23ms
     90%     1.58ms
     99%     2.32ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     96811.74    7166.77  104040.34
  Latency        1.03ms   359.16us     3.59ms
  Latency Distribution
     50%     0.93ms
     75%     1.27ms
     90%     1.69ms
     99%     2.75ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13879.65     952.65   14784.29
  Latency        7.16ms     2.55ms    19.13ms
  Latency Distribution
     50%     6.69ms
     75%     8.54ms
     90%    12.48ms
     99%    14.74ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12255.80     653.11   14349.52
  Latency        8.13ms     2.02ms    16.14ms
  Latency Distribution
     50%     8.40ms
     75%    10.14ms
     90%    10.99ms
     99%    12.51ms
### Users Mini10 (Async) (/users/mini10)
 0 / 10000 [-------------------------------------------------------]   0.00% 3182 / 10000 [==============>-----------------------------]  31.82% 15868/s 6450 / 10000 [============================>---------------]  64.50% 16085/s 9688 / 10000 [==========================================>-]  96.88% 16116/s 10000 / 10000 [===========================================] 100.00% 12480/s 10000 / 10000 [========================================] 100.00% 12479/s 0s
  Reqs/sec     16141.02     751.83   17141.27
  Latency        6.15ms     1.65ms    13.56ms
  Latency Distribution
     50%     5.35ms
     75%     7.94ms
     90%     9.34ms
     99%    10.90ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13636.21    1767.47   22523.44
  Latency        7.41ms     2.36ms    20.09ms
  Latency Distribution
     50%     7.13ms
     75%     9.11ms
     90%    11.03ms
     99%    14.69ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec     98303.60    8058.10  106749.69
  Latency        1.01ms   327.49us     4.80ms
  Latency Distribution
     50%     0.95ms
     75%     1.25ms
     90%     1.55ms
     99%     2.51ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     92413.92    5887.39   96853.78
  Latency        1.06ms   301.29us     5.33ms
  Latency Distribution
     50%     1.00ms
     75%     1.29ms
     90%     1.62ms
     99%     2.28ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     62087.70    4110.32   65591.71
  Latency        1.59ms   417.91us     4.90ms
  Latency Distribution
     50%     1.50ms
     75%     1.89ms
     90%     2.35ms
     99%     3.36ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     89276.50    5657.49   92914.28
  Latency        1.11ms   330.06us     4.80ms
  Latency Distribution
     50%     1.05ms
     75%     1.36ms
     90%     1.70ms
     99%     2.65ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     85009.95    5039.07   89310.70
  Latency        1.15ms   384.81us     5.87ms
  Latency Distribution
     50%     1.06ms
     75%     1.43ms
     90%     1.85ms
     99%     2.71ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     87801.02    5960.77   92910.52
  Latency        1.11ms   383.63us     4.64ms
  Latency Distribution
     50%     0.99ms
     75%     1.39ms
     90%     1.84ms
     99%     2.77ms
### CBV Response Types (/cbv-response)
  Reqs/sec     94312.65    5151.65   98264.99
  Latency        1.04ms   314.79us     5.21ms
  Latency Distribution
     50%     0.98ms
     75%     1.26ms
     90%     1.56ms
     99%     2.37ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16606.16    1448.76   21819.83
  Latency        6.04ms     1.08ms    13.88ms
  Latency Distribution
     50%     5.96ms
     75%     6.77ms
     90%     7.89ms
     99%     9.37ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     94654.87    5262.99   98679.91
  Latency        1.03ms   290.07us     4.94ms
  Latency Distribution
     50%     0.96ms
     75%     1.28ms
     90%     1.60ms
     99%     2.30ms
### File Upload (POST /upload)
  Reqs/sec     85632.56    7212.68   89944.98
  Latency        1.15ms   427.79us     4.70ms
  Latency Distribution
     50%     1.04ms
     75%     1.46ms
     90%     1.91ms
     99%     3.07ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     76251.61    3068.33   80885.25
  Latency        1.29ms   495.88us     5.66ms
  Latency Distribution
     50%     1.16ms
     75%     1.65ms
     90%     2.22ms
     99%     3.39ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec     10016.44    7061.17   61376.99
  Latency       10.96ms     3.05ms    39.85ms
  Latency Distribution
     50%    10.65ms
     75%    12.66ms
     90%    14.89ms
     99%    21.61ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    100564.84    8920.83  107345.04
  Latency        0.97ms   362.02us     5.52ms
  Latency Distribution
     50%     0.89ms
     75%     1.21ms
     90%     1.56ms
     99%     2.34ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     94410.40    7568.60  100445.25
  Latency        1.01ms   301.11us     5.54ms
  Latency Distribution
     50%     0.96ms
     75%     1.23ms
     90%     1.53ms
     99%     2.27ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     88576.98    7520.90   94810.54
  Latency        1.11ms   369.97us     5.51ms
  Latency Distribution
     50%     1.03ms
     75%     1.33ms
     90%     1.66ms
     99%     2.73ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     99035.31    7594.15  104234.43
  Latency        0.98ms   258.02us     5.61ms
  Latency Distribution
     50%     0.94ms
     75%     1.19ms
     90%     1.46ms
     99%     2.00ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    107434.82    8916.74  112727.16
  Latency        0.92ms   355.36us     5.54ms
  Latency Distribution
     50%   848.00us
     75%     1.11ms
     90%     1.43ms
     99%     2.28ms

### Path Parameter - int (/items/12345)
  Reqs/sec    101633.84    7127.15  105433.65
  Latency        0.97ms   327.90us     4.66ms
  Latency Distribution
     50%     0.90ms
     75%     1.20ms
     90%     1.51ms
     99%     2.34ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec     98483.37    7514.57  105412.69
  Latency        1.00ms   353.12us     4.13ms
  Latency Distribution
     50%     0.91ms
     75%     1.25ms
     90%     1.61ms
     99%     2.65ms

### Header Parameter (/header)
  Reqs/sec    103617.43    6443.26  109032.55
  Latency        0.95ms   321.44us     5.47ms
  Latency Distribution
     50%     0.88ms
     75%     1.14ms
     90%     1.44ms
     99%     2.11ms

### Cookie Parameter (/cookie)
  Reqs/sec    103458.21    6731.54  107447.31
  Latency        0.95ms   304.84us     4.00ms
  Latency Distribution
     50%     0.87ms
     75%     1.22ms
     90%     1.57ms
     99%     2.32ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     81411.36   11370.63   89619.03
  Latency        1.23ms   431.60us     6.62ms
  Latency Distribution
     50%     1.15ms
     75%     1.52ms
     90%     1.90ms
     99%     3.21ms

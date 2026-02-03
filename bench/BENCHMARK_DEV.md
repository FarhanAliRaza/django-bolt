# Django-Bolt Benchmark
Generated: Tue 03 Feb 2026 10:20:36 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    100483.48   11051.99  110803.35
  Latency        0.98ms   411.31us     5.88ms
  Latency Distribution
     50%     0.89ms
     75%     1.17ms
     90%     1.57ms
     99%     2.92ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     79807.35    7525.23   86345.40
  Latency        1.21ms   504.70us     7.52ms
  Latency Distribution
     50%     1.10ms
     75%     1.47ms
     90%     1.88ms
     99%     3.60ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     81976.67    8928.07   99709.01
  Latency        1.24ms   390.13us     5.08ms
  Latency Distribution
     50%     1.16ms
     75%     1.54ms
     90%     1.99ms
     99%     2.88ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     93845.35    8216.73  100964.92
  Latency        1.05ms   411.39us     5.66ms
  Latency Distribution
     50%     0.94ms
     75%     1.32ms
     90%     1.74ms
     99%     2.79ms
### Cookie Endpoint (/cookie)
  Reqs/sec     94329.29    5477.96  101135.72
  Latency        1.04ms   378.12us     5.18ms
  Latency Distribution
     50%     0.95ms
     75%     1.29ms
     90%     1.68ms
     99%     2.68ms
### Exception Endpoint (/exc)
  Reqs/sec     91862.49    6314.26   97448.56
  Latency        1.07ms   359.62us     5.78ms
  Latency Distribution
     50%     0.99ms
     75%     1.35ms
     90%     1.72ms
     99%     2.60ms
### HTML Response (/html)
  Reqs/sec     99125.82    6921.61  105510.57
  Latency        0.99ms   318.02us     5.50ms
  Latency Distribution
     50%     0.92ms
     75%     1.23ms
     90%     1.57ms
     99%     2.32ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     28243.16    6322.73   35216.38
  Latency        3.54ms     2.09ms    28.64ms
  Latency Distribution
     50%     3.06ms
     75%     4.20ms
     90%     5.76ms
     99%    11.25ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     76921.62    5112.71   81500.86
  Latency        1.29ms   418.54us     5.50ms
  Latency Distribution
     50%     1.20ms
     75%     1.54ms
     90%     1.93ms
     99%     3.25ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17791.55    6604.88   52620.50
  Latency        5.98ms     1.51ms    14.47ms
  Latency Distribution
     50%     5.82ms
     75%     6.94ms
     90%     8.40ms
     99%    10.33ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     14968.68    1553.03   18510.71
  Latency        6.66ms     2.10ms    20.77ms
  Latency Distribution
     50%     6.30ms
     75%     8.18ms
     90%     9.91ms
     99%    13.38ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     81078.67   11653.06  102909.28
  Latency        1.26ms   416.98us     4.81ms
  Latency Distribution
     50%     1.18ms
     75%     1.54ms
     90%     1.94ms
     99%     3.21ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     89815.70   10328.78  102850.94
  Latency        1.08ms   404.43us     5.23ms
  Latency Distribution
     50%     0.99ms
     75%     1.36ms
     90%     1.79ms
     99%     2.94ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     89027.73    7316.00   94710.51
  Latency        1.10ms   412.60us     4.70ms
  Latency Distribution
     50%     1.00ms
     75%     1.37ms
     90%     1.80ms
     99%     3.04ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     14050.37    1042.38   15185.60
  Latency        7.09ms     1.89ms    16.95ms
  Latency Distribution
     50%     6.98ms
     75%     8.54ms
     90%     9.88ms
     99%    12.58ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12186.51    1017.93   13814.32
  Latency        8.17ms     2.64ms    25.22ms
  Latency Distribution
     50%     7.64ms
     75%    10.11ms
     90%    12.18ms
     99%    16.40ms
### Users Mini10 (Async) (/users/mini10)
 0 / 10000 [---------------------------------------------------------------------------------------------------------------------------------------------]   0.00% 3207 / 10000 [=========================================>----------------------------------------------------------------------------------------]  32.07% 15983/s 6487 / 10000 [====================================================================================>---------------------------------------------]  64.87% 16183/s 9775 / 10000 [===============================================================================================================================>--]  97.75% 16259/s 10000 / 10000 [=================================================================================================================================] 100.00% 12462/s 10000 / 10000 [==============================================================================================================================] 100.00% 12459/s 0s
  Reqs/sec     16392.04    1103.68   19746.91
  Latency        6.09ms     1.63ms    14.78ms
  Latency Distribution
     50%     5.86ms
     75%     7.28ms
     90%     8.71ms
     99%    11.17ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13679.88    1474.18   16565.57
  Latency        7.29ms     3.32ms    26.94ms
  Latency Distribution
     50%     6.36ms
     75%     9.07ms
     90%    12.47ms
     99%    18.69ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    101663.10    7148.75  108920.10
  Latency        0.97ms   347.71us     4.58ms
  Latency Distribution
     50%     0.88ms
     75%     1.19ms
     90%     1.51ms
     99%     2.66ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    107010.78   26841.26  159979.13
  Latency        1.01ms   337.34us     5.43ms
  Latency Distribution
     50%     0.95ms
     75%     1.25ms
     90%     1.57ms
     99%     2.46ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     65847.24    5652.86   71270.37
  Latency        1.50ms   437.49us     5.93ms
  Latency Distribution
     50%     1.42ms
     75%     1.77ms
     90%     2.19ms
     99%     3.29ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     91951.09    5400.72   96009.05
  Latency        1.07ms   368.50us     5.30ms
  Latency Distribution
     50%     0.98ms
     75%     1.33ms
     90%     1.70ms
     99%     2.69ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     88206.03    6414.58   93834.27
  Latency        1.11ms   395.31us     6.56ms
  Latency Distribution
     50%     1.03ms
     75%     1.40ms
     90%     1.74ms
     99%     2.59ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     92342.88    5970.30   97048.50
  Latency        1.05ms   345.56us     4.93ms
  Latency Distribution
     50%     0.98ms
     75%     1.31ms
     90%     1.68ms
     99%     2.46ms
### CBV Response Types (/cbv-response)
  Reqs/sec    102109.76   15881.85  132254.01
  Latency        1.02ms   357.90us     4.78ms
  Latency Distribution
     50%     0.93ms
     75%     1.27ms
     90%     1.67ms
     99%     2.49ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16815.81    1418.96   19211.14
  Latency        5.93ms     1.43ms    15.98ms
  Latency Distribution
     50%     5.77ms
     75%     6.93ms
     90%     8.05ms
     99%    10.68ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     88355.58    4464.38   95173.26
  Latency        1.11ms   398.59us     5.35ms
  Latency Distribution
     50%     1.02ms
     75%     1.37ms
     90%     1.76ms
     99%     2.76ms
### File Upload (POST /upload)
  Reqs/sec     84720.57   10348.46  103597.42
  Latency        1.20ms   428.91us     5.61ms
  Latency Distribution
     50%     1.13ms
     75%     1.48ms
     90%     1.90ms
     99%     3.04ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     78008.98    6195.22   83168.79
  Latency        1.27ms   396.59us     4.92ms
  Latency Distribution
     50%     1.18ms
     75%     1.57ms
     90%     2.00ms
     99%     2.95ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9082.16     885.18   10765.03
  Latency       10.97ms     2.81ms    24.60ms
  Latency Distribution
     50%    11.11ms
     75%    12.90ms
     90%    14.92ms
     99%    18.95ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     97130.32    8244.82  107088.78
  Latency        1.03ms   405.83us     5.56ms
  Latency Distribution
     50%     0.93ms
     75%     1.27ms
     90%     1.66ms
     99%     2.74ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     88697.45    5536.26   93529.97
  Latency        1.11ms   370.45us     5.44ms
  Latency Distribution
     50%     1.01ms
     75%     1.38ms
     90%     1.77ms
     99%     2.79ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     85079.30    6150.76   90446.91
  Latency        1.16ms   407.68us     4.56ms
  Latency Distribution
     50%     1.06ms
     75%     1.42ms
     90%     1.88ms
     99%     2.99ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     92245.05    8998.34   97625.81
  Latency        1.06ms   376.84us     5.52ms
  Latency Distribution
     50%     0.96ms
     75%     1.37ms
     90%     1.71ms
     99%     2.63ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    106671.79    8763.97  112544.87
  Latency        0.92ms   368.13us     6.06ms
  Latency Distribution
     50%   848.00us
     75%     1.12ms
     90%     1.45ms
     99%     2.45ms

### Path Parameter - int (/items/12345)
  Reqs/sec    101544.69    8864.18  108149.22
  Latency        0.96ms   331.30us     4.88ms
  Latency Distribution
     50%     0.90ms
     75%     1.19ms
     90%     1.50ms
     99%     2.49ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec     98864.54    5975.88  103360.13
  Latency        0.99ms   281.82us     3.37ms
  Latency Distribution
     50%     0.92ms
     75%     1.21ms
     90%     1.53ms
     99%     2.30ms

### Header Parameter (/header)
  Reqs/sec     95546.57    7624.69  104358.55
  Latency        1.03ms   394.64us     7.17ms
  Latency Distribution
     50%     0.96ms
     75%     1.24ms
     90%     1.57ms
     99%     2.53ms

### Cookie Parameter (/cookie)
  Reqs/sec     84385.44    8477.98   99539.34
  Latency        1.16ms   465.81us     4.88ms
  Latency Distribution
     50%     1.04ms
     75%     1.43ms
     90%     1.91ms
     99%     3.41ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     52877.01   11725.83   71421.85
  Latency        1.91ms     0.96ms     9.23ms
  Latency Distribution
     50%     1.68ms
     75%     2.43ms
     90%     3.34ms
     99%     6.13ms

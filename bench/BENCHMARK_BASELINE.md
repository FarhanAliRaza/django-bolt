# Django-Bolt Benchmark
Generated: Sat 31 Jan 2026 10:51:11 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    100323.22    5192.80  105890.03
  Latency        0.98ms   329.12us     4.87ms
  Latency Distribution
     50%     0.91ms
     75%     1.22ms
     90%     1.56ms
     99%     2.36ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     89603.13    6399.33   95627.24
  Latency        1.10ms   305.13us     4.57ms
  Latency Distribution
     50%     1.03ms
     75%     1.32ms
     90%     1.63ms
     99%     2.38ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     83909.29    5706.67   90100.48
  Latency        1.17ms   446.21us     5.79ms
  Latency Distribution
     50%     1.04ms
     75%     1.48ms
     90%     1.95ms
     99%     3.09ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    104221.05    9326.36  112401.41
  Latency        0.94ms   288.64us     4.81ms
  Latency Distribution
     50%     0.88ms
     75%     1.17ms
     90%     1.48ms
     99%     2.17ms
### Cookie Endpoint (/cookie)
  Reqs/sec    106416.69    8108.72  112283.09
  Latency        0.92ms   281.08us     4.09ms
  Latency Distribution
     50%     0.86ms
     75%     1.12ms
     90%     1.43ms
     99%     2.11ms
### Exception Endpoint (/exc)
  Reqs/sec    103117.84    7230.29  107997.33
  Latency        0.95ms   305.12us     4.92ms
  Latency Distribution
     50%     0.89ms
     75%     1.16ms
     90%     1.44ms
     99%     2.14ms
### HTML Response (/html)
  Reqs/sec    107097.75    6658.07  111677.51
  Latency        0.92ms   314.69us     5.63ms
  Latency Distribution
     50%   835.00us
     75%     1.13ms
     90%     1.47ms
     99%     2.15ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     34508.94    9900.96   63178.44
  Latency        3.04ms     1.44ms    16.96ms
  Latency Distribution
     50%     2.65ms
     75%     3.67ms
     90%     4.86ms
     99%     9.05ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     76009.56    4921.33   80338.91
  Latency        1.29ms   427.07us     5.58ms
  Latency Distribution
     50%     1.18ms
     75%     1.57ms
     90%     2.01ms
     99%     3.10ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     16399.78    2728.03   19093.82
  Latency        6.08ms     1.72ms    20.45ms
  Latency Distribution
     50%     5.96ms
     75%     6.84ms
     90%     7.79ms
     99%    14.06ms
### Get User via Dependency (/auth/me-dependency)
 0 / 10000 [--------------------------------------------------------------]   0.00% 3013 / 10000 [===============>-----------------------------------]  30.13% 15027/s 6099 / 10000 [===============================>-------------------]  60.99% 15215/s 9236 / 10000 [===============================================>---]  92.36% 15364/s 10000 / 10000 [==================================================] 100.00% 12471/s 10000 / 10000 [===============================================] 100.00% 12470/s 0s
  Reqs/sec     15621.48    1732.97   23039.91
  Latency        6.44ms     1.81ms    19.31ms
  Latency Distribution
     50%     6.29ms
     75%     7.93ms
     90%     9.25ms
     99%    11.80ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     85500.16    8382.01   94557.34
  Latency        1.15ms   372.07us     5.05ms
  Latency Distribution
     50%     1.07ms
     75%     1.42ms
     90%     1.83ms
     99%     2.72ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     98662.21    8076.63  108265.97
  Latency        0.98ms   330.19us     5.51ms
  Latency Distribution
     50%     0.90ms
     75%     1.21ms
     90%     1.57ms
     99%     2.45ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     98066.36    7917.29  109706.59
  Latency        1.02ms   357.56us     4.38ms
  Latency Distribution
     50%     0.93ms
     75%     1.26ms
     90%     1.67ms
     99%     2.58ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     14149.43     918.80   14873.44
  Latency        7.03ms     1.63ms    15.68ms
  Latency Distribution
     50%     7.06ms
     75%     8.23ms
     90%     9.30ms
     99%    11.97ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12746.54    1011.13   16494.98
  Latency        7.84ms     2.03ms    18.70ms
  Latency Distribution
     50%     7.47ms
     75%     9.55ms
     90%    11.03ms
     99%    13.80ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     15880.76    1769.66   18115.00
  Latency        6.21ms     1.70ms    17.76ms
  Latency Distribution
     50%     6.06ms
     75%     7.34ms
     90%     8.60ms
     99%    12.19ms
### Users Mini10 (Sync) (/users/sync-mini10)
 0 / 10000 [--------------------------------------------------------------]   0.00% 2597 / 10000 [=============>-------------------------------------]  25.97% 12936/s 5412 / 10000 [===========================>-----------------------]  54.12% 13494/s 8199 / 10000 [=========================================>---------]  81.99% 13626/s 10000 / 10000 [==================================================] 100.00% 12467/s 10000 / 10000 [===============================================] 100.00% 12465/s 0s
  Reqs/sec     13706.94    1386.99   15536.31
  Latency        7.28ms     2.76ms    26.93ms
  Latency Distribution
     50%     6.83ms
     75%     9.03ms
     90%    11.31ms
     99%    16.35ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    104584.29    6979.87  111848.76
  Latency        0.94ms   352.17us     4.16ms
  Latency Distribution
     50%     0.86ms
     75%     1.17ms
     90%     1.53ms
     99%     2.62ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    100625.71    8513.30  107110.05
  Latency        0.98ms   357.94us     5.25ms
  Latency Distribution
     50%     0.90ms
     75%     1.20ms
     90%     1.47ms
     99%     2.48ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     65265.80    5464.01   71181.79
  Latency        1.51ms   468.11us     5.71ms
  Latency Distribution
     50%     1.43ms
     75%     1.81ms
     90%     2.30ms
     99%     3.57ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     85132.74   10338.60   92508.01
  Latency        1.16ms   392.51us     4.94ms
  Latency Distribution
     50%     1.06ms
     75%     1.46ms
     90%     1.86ms
     99%     2.83ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     92209.16    6436.14   97419.84
  Latency        1.06ms   393.08us     5.05ms
  Latency Distribution
     50%     0.94ms
     75%     1.33ms
     90%     1.71ms
     99%     2.90ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     96235.86   10354.01  104565.49
  Latency        1.03ms   377.12us     6.25ms
  Latency Distribution
     50%     0.94ms
     75%     1.27ms
     90%     1.65ms
     99%     2.68ms
### CBV Response Types (/cbv-response)
  Reqs/sec    101471.20    8812.05  109632.99
  Latency        0.97ms   357.38us     5.90ms
  Latency Distribution
     50%     0.88ms
     75%     1.19ms
     90%     1.51ms
     99%     2.36ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16636.84    1564.11   18762.40
  Latency        5.98ms     1.56ms    24.49ms
  Latency Distribution
     50%     5.86ms
     75%     6.99ms
     90%     8.17ms
     99%    11.18ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     92288.24    7687.65  100048.21
  Latency        1.06ms   392.95us     6.53ms
  Latency Distribution
     50%     0.97ms
     75%     1.34ms
     90%     1.77ms
     99%     2.78ms
### File Upload (POST /upload)
  Reqs/sec     82573.08    7376.56   91500.32
  Latency        1.19ms   408.00us     6.07ms
  Latency Distribution
     50%     1.11ms
     75%     1.50ms
     90%     1.89ms
     99%     2.84ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     83509.73    4728.84   89058.13
  Latency        1.18ms   360.81us     4.98ms
  Latency Distribution
     50%     1.10ms
     75%     1.45ms
     90%     1.80ms
     99%     2.68ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9632.15     989.51   13516.69
  Latency       10.41ms     2.04ms    20.66ms
  Latency Distribution
     50%    10.47ms
     75%    11.92ms
     90%    13.18ms
     99%    16.27ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    104108.21    7792.01  108171.20
  Latency        0.94ms   323.79us     6.16ms
  Latency Distribution
     50%     0.88ms
     75%     1.15ms
     90%     1.46ms
     99%     2.21ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     97700.05    7044.81  104007.81
  Latency        1.00ms   345.83us     5.04ms
  Latency Distribution
     50%     0.92ms
     75%     1.24ms
     90%     1.55ms
     99%     2.56ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     88309.85    5132.51   94353.03
  Latency        1.11ms   388.79us     4.59ms
  Latency Distribution
     50%     1.00ms
     75%     1.35ms
     90%     1.74ms
     99%     2.97ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     78773.45   16949.29  106624.70
  Latency        1.28ms   631.84us     8.38ms
  Latency Distribution
     50%     1.13ms
     75%     1.52ms
     90%     2.14ms
     99%     4.37ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    113218.10    8362.03  121038.76
  Latency        0.87ms   288.34us     4.22ms
  Latency Distribution
     50%   807.00us
     75%     1.05ms
     90%     1.33ms
     99%     2.00ms

### Path Parameter - int (/items/12345)
  Reqs/sec    104266.54    7821.69  111947.96
  Latency        0.94ms   278.63us     4.33ms
  Latency Distribution
     50%     0.88ms
     75%     1.14ms
     90%     1.43ms
     99%     2.03ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    105631.53    7731.07  110753.91
  Latency        0.93ms   257.65us     4.36ms
  Latency Distribution
     50%     0.89ms
     75%     1.13ms
     90%     1.43ms
     99%     2.07ms

### Header Parameter (/header)
  Reqs/sec    102002.80    8567.95  109722.03
  Latency        0.97ms   333.77us     4.93ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.49ms
     99%     2.44ms

### Cookie Parameter (/cookie)
  Reqs/sec    101882.69    7879.76  110721.30
  Latency        0.96ms   312.86us     5.36ms
  Latency Distribution
     50%     0.89ms
     75%     1.18ms
     90%     1.49ms
     99%     2.25ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     87577.88    7107.48   92351.53
  Latency        1.13ms   324.72us     4.65ms
  Latency Distribution
     50%     1.07ms
     75%     1.36ms
     90%     1.69ms
     99%     2.44ms

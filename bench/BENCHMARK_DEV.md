# Django-Bolt Benchmark
Generated: Sun Feb 22 06:42:03 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    115369.68    9532.14  122848.64
  Latency        0.86ms   275.51us     5.99ms
  Latency Distribution
     50%   794.00us
     75%     1.05ms
     90%     1.31ms
     99%     1.90ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     90623.23    6553.32   95371.29
  Latency        1.09ms   310.48us     5.12ms
  Latency Distribution
     50%     1.01ms
     75%     1.32ms
     90%     1.65ms
     99%     2.47ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     89556.09    7383.62   95790.05
  Latency        1.11ms   372.36us     6.86ms
  Latency Distribution
     50%     1.03ms
     75%     1.38ms
     90%     1.70ms
     99%     2.50ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    104930.01    6106.66  109100.28
  Latency        0.93ms   272.46us     4.73ms
  Latency Distribution
     50%     0.87ms
     75%     1.15ms
     90%     1.45ms
     99%     2.18ms
### Cookie Endpoint (/cookie)
  Reqs/sec    105742.81    7709.43  110942.77
  Latency        0.93ms   288.92us     5.01ms
  Latency Distribution
     50%     0.88ms
     75%     1.12ms
     90%     1.39ms
     99%     1.94ms
### Exception Endpoint (/exc)
  Reqs/sec    100021.77    4821.26  103851.26
  Latency        0.98ms   308.44us     4.75ms
  Latency Distribution
     50%     0.90ms
     75%     1.22ms
     90%     1.57ms
     99%     2.33ms
### HTML Response (/html)
  Reqs/sec    111978.30    8416.91  118251.42
  Latency        0.88ms   267.64us     4.82ms
  Latency Distribution
     50%   816.00us
     75%     1.08ms
     90%     1.36ms
     99%     1.99ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     35851.62    8436.24   41610.14
  Latency        2.78ms     1.45ms    20.05ms
  Latency Distribution
     50%     2.55ms
     75%     3.14ms
     90%     3.82ms
     99%     8.05ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     78761.71    4239.89   81674.19
  Latency        1.24ms   279.60us     4.28ms
  Latency Distribution
     50%     1.19ms
     75%     1.48ms
     90%     1.79ms
     99%     2.40ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17519.75    1426.30   20096.15
  Latency        5.70ms     1.96ms    15.18ms
  Latency Distribution
     50%     5.32ms
     75%     7.30ms
     90%     9.04ms
     99%    11.97ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15392.91     990.93   17033.57
  Latency        6.46ms     1.82ms    14.61ms
  Latency Distribution
     50%     6.26ms
     75%     8.02ms
     90%     9.43ms
     99%    11.84ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     86620.25    5786.88   90485.92
  Latency        1.14ms   336.34us     4.75ms
  Latency Distribution
     50%     1.05ms
     75%     1.39ms
     90%     1.76ms
     99%     2.65ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    105159.47    6655.54  111221.05
  Latency        0.93ms   281.10us     4.61ms
  Latency Distribution
     50%     0.87ms
     75%     1.14ms
     90%     1.44ms
     99%     2.07ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     99650.26    6039.07  106232.96
  Latency        0.99ms   296.48us     4.50ms
  Latency Distribution
     50%     0.92ms
     75%     1.20ms
     90%     1.53ms
     99%     2.30ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
 0 / 10000 [-----------------------------------------------------------]   0.00% 2690 / 10000 [============>-----------------------------------]  26.90% 13413/s 5523 / 10000 [==========================>---------------------]  55.23% 13780/s 8332 / 10000 [=======================================>--------]  83.32% 13863/s 10000 / 10000 [===============================================] 100.00% 12467/s 10000 / 10000 [============================================] 100.00% 12466/s 0s
  Reqs/sec     13929.90     960.48   15159.78
  Latency        7.14ms     1.48ms    18.84ms
  Latency Distribution
     50%     7.00ms
     75%     7.92ms
     90%     9.78ms
     99%    11.49ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec      4623.44     956.88   13430.27
  Latency       21.92ms     8.11ms    55.60ms
  Latency Distribution
     50%    20.46ms
     75%    27.79ms
     90%    34.18ms
     99%    43.07ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     15917.96    1223.43   17182.89
  Latency        6.19ms     1.74ms    12.61ms
  Latency Distribution
     50%     6.69ms
     75%     7.91ms
     90%     8.70ms
     99%    10.01ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13564.74    1099.92   15757.59
  Latency        7.33ms     3.61ms    26.09ms
  Latency Distribution
     50%     6.32ms
     75%     9.59ms
     90%    13.30ms
     99%    19.01ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    111805.27    9115.43  117172.63
  Latency        0.88ms   330.52us     6.03ms
  Latency Distribution
     50%   819.00us
     75%     1.06ms
     90%     1.36ms
     99%     2.21ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    104457.95    7574.56  109086.27
  Latency        0.94ms   278.99us     4.30ms
  Latency Distribution
     50%     0.87ms
     75%     1.17ms
     90%     1.52ms
     99%     2.16ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     68562.98    4553.41   74879.07
  Latency        1.45ms   441.46us     7.04ms
  Latency Distribution
     50%     1.33ms
     75%     1.76ms
     90%     2.23ms
     99%     3.36ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    101656.06    6979.88  108294.00
  Latency        0.97ms   297.07us     4.56ms
  Latency Distribution
     50%     0.90ms
     75%     1.18ms
     90%     1.48ms
     99%     2.16ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    100229.99    8057.08  105938.55
  Latency        0.98ms   283.19us     3.89ms
  Latency Distribution
     50%     0.93ms
     75%     1.20ms
     90%     1.50ms
     99%     2.18ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    101600.77    6627.79  106286.30
  Latency        0.96ms   283.66us     4.13ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.48ms
     99%     2.19ms
### CBV Response Types (/cbv-response)
  Reqs/sec    107138.52    8400.83  111946.34
  Latency        0.91ms   281.95us     5.82ms
  Latency Distribution
     50%     0.85ms
     75%     1.14ms
     90%     1.44ms
     99%     2.06ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
 0 / 10000 [-----------------------------------------------------------]   0.00% 3252 / 10000 [===============>--------------------------------]  32.52% 16214/s 6621 / 10000 [===============================>----------------]  66.21% 16520/s 9999 / 10000 [================================================]  99.99% 16639/s 10000 / 10000 [===============================================] 100.00% 12479/s 10000 / 10000 [============================================] 100.00% 12478/s 0s
  Reqs/sec     16671.33    1163.56   18546.31
  Latency        5.97ms     1.06ms    13.62ms
  Latency Distribution
     50%     5.96ms
     75%     6.77ms
     90%     7.58ms
     99%     9.21ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    100216.70    8648.24  106394.25
  Latency        0.98ms   321.55us     4.59ms
  Latency Distribution
     50%     0.92ms
     75%     1.20ms
     90%     1.49ms
     99%     2.38ms
### File Upload (POST /upload)
  Reqs/sec     90170.16    4988.14   94457.80
  Latency        1.09ms   296.72us     4.69ms
  Latency Distribution
     50%     1.03ms
     75%     1.34ms
     90%     1.65ms
     99%     2.29ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     87192.76    6218.81   92177.27
  Latency        1.13ms   325.12us     4.63ms
  Latency Distribution
     50%     1.07ms
     75%     1.38ms
     90%     1.71ms
     99%     2.48ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9815.31     929.76   11839.12
  Latency       10.15ms     2.38ms    22.96ms
  Latency Distribution
     50%    10.28ms
     75%    11.98ms
     90%    13.37ms
     99%    16.75ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    102574.54    7270.61  107004.66
  Latency        0.96ms   346.13us     4.38ms
  Latency Distribution
     50%     0.88ms
     75%     1.19ms
     90%     1.58ms
     99%     2.45ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     97936.49    5430.82  102217.55
  Latency        1.00ms   308.31us     4.46ms
  Latency Distribution
     50%     0.93ms
     75%     1.23ms
     90%     1.57ms
     99%     2.22ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     89556.89    7388.03   94689.64
  Latency        1.10ms   374.05us     5.05ms
  Latency Distribution
     50%     1.02ms
     75%     1.35ms
     90%     1.71ms
     99%     2.70ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     99990.27    6719.16  104788.66
  Latency        0.98ms   285.42us     5.38ms
  Latency Distribution
     50%     0.92ms
     75%     1.19ms
     90%     1.48ms
     99%     2.13ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    117052.70    9293.65  123235.09
  Latency      836.13us   235.98us     4.57ms
  Latency Distribution
     50%   792.00us
     75%     1.02ms
     90%     1.24ms
     99%     1.83ms

### Path Parameter - int (/items/12345)
  Reqs/sec    107752.05    6540.41  111791.08
  Latency        0.91ms   263.30us     4.37ms
  Latency Distribution
     50%     0.86ms
     75%     1.11ms
     90%     1.36ms
     99%     2.04ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    106890.20    8037.88  110918.77
  Latency        0.92ms   291.96us     5.37ms
  Latency Distribution
     50%     0.87ms
     75%     1.12ms
     90%     1.39ms
     99%     2.04ms

### Header Parameter (/header)
  Reqs/sec    108028.91    7199.54  112037.10
  Latency        0.91ms   272.00us     4.36ms
  Latency Distribution
     50%   849.00us
     75%     1.14ms
     90%     1.44ms
     99%     2.12ms

### Cookie Parameter (/cookie)
  Reqs/sec    108131.08    8497.55  114731.21
  Latency        0.91ms   262.87us     4.27ms
  Latency Distribution
     50%     0.86ms
     75%     1.11ms
     90%     1.37ms
     99%     2.00ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     87391.52    5626.50   91637.76
  Latency        1.12ms   345.21us     3.88ms
  Latency Distribution
     50%     1.02ms
     75%     1.39ms
     90%     1.85ms
     99%     2.64ms

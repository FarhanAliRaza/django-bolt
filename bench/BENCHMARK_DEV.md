# Django-Bolt Benchmark
Generated: Mon 23 Feb 2026 01:10:55 AM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    107200.01    8744.52  115174.52
  Latency        0.92ms   375.72us     5.28ms
  Latency Distribution
     50%   828.00us
     75%     1.13ms
     90%     1.47ms
     99%     2.64ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     84163.11    9868.77   90361.42
  Latency        1.17ms   396.90us     5.69ms
  Latency Distribution
     50%     1.09ms
     75%     1.42ms
     90%     1.78ms
     99%     2.81ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     82549.44    5871.10   88357.93
  Latency        1.19ms   389.57us     5.56ms
  Latency Distribution
     50%     1.11ms
     75%     1.51ms
     90%     1.91ms
     99%     2.87ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    102541.16    7589.13  108042.25
  Latency        0.96ms   332.45us     5.19ms
  Latency Distribution
     50%     0.89ms
     75%     1.16ms
     90%     1.47ms
     99%     2.31ms
### Cookie Endpoint (/cookie)
  Reqs/sec     92285.57    5019.65   96633.06
  Latency        1.07ms   328.85us     5.26ms
  Latency Distribution
     50%     1.00ms
     75%     1.33ms
     90%     1.70ms
     99%     2.44ms
### Exception Endpoint (/exc)
  Reqs/sec     95847.99    7030.24  102311.51
  Latency        1.02ms   314.51us     5.35ms
  Latency Distribution
     50%     0.96ms
     75%     1.24ms
     90%     1.56ms
     99%     2.34ms
### HTML Response (/html)
  Reqs/sec     70848.93   12716.63   89120.80
  Latency        1.39ms   704.11us     8.34ms
  Latency Distribution
     50%     1.22ms
     75%     1.73ms
     90%     2.28ms
     99%     4.61ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     28760.67    7270.74   35806.68
  Latency        3.47ms     1.90ms    24.94ms
  Latency Distribution
     50%     3.02ms
     75%     4.01ms
     90%     5.22ms
     99%    12.44ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     74982.07    5215.40   77936.19
  Latency        1.31ms   401.23us     5.42ms
  Latency Distribution
     50%     1.21ms
     75%     1.67ms
     90%     2.09ms
     99%     2.91ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     16270.21    1530.20   18002.46
  Latency        6.12ms     2.13ms    17.61ms
  Latency Distribution
     50%     5.54ms
     75%     7.85ms
     90%     9.84ms
     99%    12.75ms
### Get User via Dependency (/auth/me-dependency)
 0 / 10000 [-----------------------------------]   0.00% 2918 / 10000 [=======>----------------]  29.18% 14562/s 5956 / 10000 [==============>---------]  59.56% 14871/s 8975 / 10000 [=====================>--]  89.75% 14942/s 10000 / 10000 [=======================] 100.00% 12472/s 10000 / 10000 [====================] 100.00% 12470/s 0s
  Reqs/sec     15053.91     864.31   16883.76
  Latency        6.61ms     1.73ms    14.88ms
  Latency Distribution
     50%     6.60ms
     75%     7.96ms
     90%     9.25ms
     99%    11.69ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     86210.00   14945.63  117611.55
  Latency        1.21ms   382.79us     5.10ms
  Latency Distribution
     50%     1.12ms
     75%     1.49ms
     90%     1.92ms
     99%     2.79ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     94490.34    8033.49  103129.06
  Latency        1.02ms   353.92us     4.33ms
  Latency Distribution
     50%     0.95ms
     75%     1.33ms
     90%     1.76ms
     99%     2.54ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     94344.81    7274.17  103033.61
  Latency        1.06ms   342.76us     4.53ms
  Latency Distribution
     50%     0.98ms
     75%     1.29ms
     90%     1.65ms
     99%     2.64ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13791.49    1134.96   17040.14
  Latency        7.24ms     1.54ms    17.73ms
  Latency Distribution
     50%     7.44ms
     75%     8.47ms
     90%     9.26ms
     99%    11.34ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     10066.48    1017.00   12026.72
  Latency        9.87ms     5.06ms    40.85ms
  Latency Distribution
     50%     8.55ms
     75%    12.62ms
     90%    17.90ms
     99%    26.23ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     15840.95     769.89   17108.72
  Latency        6.27ms     2.30ms    16.96ms
  Latency Distribution
     50%     5.99ms
     75%     8.28ms
     90%    10.00ms
     99%    12.62ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     12012.55     889.02   14449.76
  Latency        8.30ms     3.62ms    30.08ms
  Latency Distribution
     50%     7.27ms
     75%    10.19ms
     90%    13.82ms
     99%    21.07ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    103137.23    7593.57  109038.63
  Latency        0.95ms   293.13us     5.58ms
  Latency Distribution
     50%     0.89ms
     75%     1.17ms
     90%     1.47ms
     99%     2.21ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     98655.95    9655.87  115568.22
  Latency        1.03ms   291.09us     4.54ms
  Latency Distribution
     50%     0.96ms
     75%     1.27ms
     90%     1.58ms
     99%     2.32ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     64395.22    3876.90   66799.84
  Latency        1.53ms   478.74us     7.10ms
  Latency Distribution
     50%     1.42ms
     75%     1.86ms
     90%     2.39ms
     99%     3.47ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     97746.19    7223.87  108300.55
  Latency        1.03ms   295.28us     4.64ms
  Latency Distribution
     50%     0.96ms
     75%     1.26ms
     90%     1.57ms
     99%     2.25ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     92525.46    5911.60   97069.84
  Latency        1.07ms   345.69us     6.68ms
  Latency Distribution
     50%     0.99ms
     75%     1.32ms
     90%     1.67ms
     99%     2.45ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     92397.81    6154.78   98414.80
  Latency        1.06ms   332.81us     4.62ms
  Latency Distribution
     50%     0.97ms
     75%     1.32ms
     90%     1.72ms
     99%     2.49ms
### CBV Response Types (/cbv-response)
  Reqs/sec     95987.10    5742.11  100373.92
  Latency        1.03ms   337.67us     5.57ms
  Latency Distribution
     50%     0.95ms
     75%     1.24ms
     90%     1.60ms
     99%     2.45ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16288.89    1129.79   18625.29
  Latency        6.11ms     1.52ms    14.91ms
  Latency Distribution
     50%     5.87ms
     75%     7.57ms
     90%     8.60ms
     99%    10.50ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     95308.41    7083.82   99442.10
  Latency        1.04ms   368.42us     5.61ms
  Latency Distribution
     50%     0.99ms
     75%     1.27ms
     90%     1.59ms
     99%     2.49ms
### File Upload (POST /upload)
  Reqs/sec     82806.97    8108.17   89932.26
  Latency        1.18ms   361.96us     5.37ms
  Latency Distribution
     50%     1.13ms
     75%     1.49ms
     90%     1.83ms
     99%     2.63ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     77699.45    8037.19   88854.38
  Latency        1.23ms   372.61us     4.62ms
  Latency Distribution
     50%     1.15ms
     75%     1.51ms
     90%     1.91ms
     99%     2.88ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9806.31    1209.59   16222.25
  Latency       10.26ms     2.31ms    22.37ms
  Latency Distribution
     50%    10.20ms
     75%    11.72ms
     90%    13.47ms
     99%    17.59ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     94191.36    5957.77   99877.07
  Latency        1.04ms   360.86us     5.13ms
  Latency Distribution
     50%     0.96ms
     75%     1.29ms
     90%     1.67ms
     99%     2.47ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     93199.19    6926.98  101343.35
  Latency        1.06ms   331.61us     4.82ms
  Latency Distribution
     50%     1.00ms
     75%     1.32ms
     90%     1.69ms
     99%     2.47ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     86932.99    6475.71   90740.40
  Latency        1.13ms   363.91us     5.51ms
  Latency Distribution
     50%     1.05ms
     75%     1.38ms
     90%     1.70ms
     99%     2.68ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     92474.15    5481.54   96453.29
  Latency        1.06ms   363.91us     4.52ms
  Latency Distribution
     50%     0.99ms
     75%     1.34ms
     90%     1.74ms
     99%     2.64ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    106125.49    6808.59  111451.92
  Latency        0.93ms   340.56us     4.88ms
  Latency Distribution
     50%     0.85ms
     75%     1.12ms
     90%     1.45ms
     99%     2.25ms

### Path Parameter - int (/items/12345)
  Reqs/sec    103055.52    5731.56  106645.56
  Latency        0.96ms   287.21us     4.85ms
  Latency Distribution
     50%     0.89ms
     75%     1.18ms
     90%     1.50ms
     99%     2.27ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec     97787.89    6281.05  103745.89
  Latency        1.01ms   343.23us     5.42ms
  Latency Distribution
     50%     0.92ms
     75%     1.28ms
     90%     1.65ms
     99%     2.46ms

### Header Parameter (/header)
  Reqs/sec    100536.70    6810.07  105460.46
  Latency        0.98ms   307.12us     4.20ms
  Latency Distribution
     50%     0.92ms
     75%     1.20ms
     90%     1.52ms
     99%     2.27ms

### Cookie Parameter (/cookie)
  Reqs/sec     98320.59    9385.99  111641.12
  Latency        1.02ms   330.50us     5.29ms
  Latency Distribution
     50%     0.95ms
     75%     1.29ms
     90%     1.65ms
     99%     2.44ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     83331.08    6436.14   87027.20
  Latency        1.18ms   320.98us     4.21ms
  Latency Distribution
     50%     1.12ms
     75%     1.45ms
     90%     1.79ms
     99%     2.55ms

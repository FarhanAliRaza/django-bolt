# Django-Bolt Benchmark
Generated: Wed 04 Feb 2026 10:38:30 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    102019.44    7183.94  107468.57
  Latency        0.96ms   358.80us     5.16ms
  Latency Distribution
     50%     0.88ms
     75%     1.18ms
     90%     1.54ms
     99%     2.58ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     88703.94    7127.62   92487.43
  Latency        1.11ms   338.49us     5.32ms
  Latency Distribution
     50%     1.03ms
     75%     1.35ms
     90%     1.69ms
     99%     2.68ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     88660.45    5231.82   92552.33
  Latency        1.11ms   336.66us     5.03ms
  Latency Distribution
     50%     1.04ms
     75%     1.35ms
     90%     1.67ms
     99%     2.49ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    101412.79    8267.70  109282.37
  Latency        0.97ms   301.89us     4.19ms
  Latency Distribution
     50%     0.92ms
     75%     1.21ms
     90%     1.49ms
     99%     2.22ms
### Cookie Endpoint (/cookie)
  Reqs/sec    101304.01    7862.89  105989.42
  Latency        0.97ms   306.66us     5.04ms
  Latency Distribution
     50%     0.90ms
     75%     1.20ms
     90%     1.50ms
     99%     2.28ms
### Exception Endpoint (/exc)
  Reqs/sec     99456.52    7648.54  105296.08
  Latency        0.99ms   337.50us     5.25ms
  Latency Distribution
     50%     0.91ms
     75%     1.22ms
     90%     1.55ms
     99%     2.40ms
### HTML Response (/html)
  Reqs/sec    106332.10    7869.63  113962.63
  Latency        0.92ms   327.27us     4.45ms
  Latency Distribution
     50%     0.86ms
     75%     1.15ms
     90%     1.45ms
     99%     2.31ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     33403.98    8159.85   39016.62
  Latency        2.99ms     1.53ms    21.07ms
  Latency Distribution
     50%     2.70ms
     75%     3.44ms
     90%     4.32ms
     99%     9.04ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     77366.60    5713.28   83343.65
  Latency        1.27ms   373.71us     4.12ms
  Latency Distribution
     50%     1.23ms
     75%     1.60ms
     90%     1.96ms
     99%     2.82ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17828.09    1283.29   19822.54
  Latency        5.59ms     1.23ms    13.71ms
  Latency Distribution
     50%     5.37ms
     75%     6.21ms
     90%     7.60ms
     99%     9.96ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     16143.30    1252.35   21124.16
  Latency        6.21ms     1.64ms    14.05ms
  Latency Distribution
     50%     5.99ms
     75%     7.48ms
     90%     8.93ms
     99%    11.27ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     85911.88    6133.33   92784.86
  Latency        1.14ms   403.00us     5.46ms
  Latency Distribution
     50%     1.04ms
     75%     1.43ms
     90%     1.89ms
     99%     2.96ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    101888.85    7408.66  108529.09
  Latency        0.96ms   335.65us     5.69ms
  Latency Distribution
     50%     0.89ms
     75%     1.17ms
     90%     1.50ms
     99%     2.29ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     94068.07    7525.02  100767.06
  Latency        1.03ms   372.17us     5.36ms
  Latency Distribution
     50%     0.95ms
     75%     1.26ms
     90%     1.64ms
     99%     2.69ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     14566.35     968.49   16619.85
  Latency        6.85ms     1.94ms    16.71ms
  Latency Distribution
     50%     6.54ms
     75%     7.96ms
     90%    10.02ms
     99%    13.16ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     13156.29    1259.47   19337.20
  Latency        7.64ms     2.18ms    21.51ms
  Latency Distribution
     50%     7.35ms
     75%     9.28ms
     90%    11.15ms
     99%    14.21ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     16662.84     815.45   17762.99
  Latency        5.96ms     2.06ms    15.27ms
  Latency Distribution
     50%     5.48ms
     75%     7.59ms
     90%     9.45ms
     99%    12.49ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13752.70    1446.90   16202.35
  Latency        7.21ms     3.36ms    33.26ms
  Latency Distribution
     50%     6.24ms
     75%     8.88ms
     90%    12.54ms
     99%    18.77ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    102619.90    7727.74  108364.49
  Latency        0.96ms   325.23us     4.36ms
  Latency Distribution
     50%     0.89ms
     75%     1.19ms
     90%     1.49ms
     99%     2.36ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     84597.15   32558.15  104093.88
  Latency        1.01ms   373.69us     5.54ms
  Latency Distribution
     50%     0.93ms
     75%     1.22ms
     90%     1.56ms
     99%     2.55ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     64902.64    3900.83   67867.27
  Latency        1.52ms   443.55us     4.95ms
  Latency Distribution
     50%     1.47ms
     75%     1.89ms
     90%     2.38ms
     99%     3.18ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     95791.95    7085.79  101534.82
  Latency        1.03ms   372.34us     4.76ms
  Latency Distribution
     50%     0.94ms
     75%     1.25ms
     90%     1.62ms
     99%     2.71ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     93817.47    7180.61   97852.34
  Latency        1.04ms   284.46us     3.84ms
  Latency Distribution
     50%     0.99ms
     75%     1.29ms
     90%     1.60ms
     99%     2.34ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     95744.94    8735.29  108901.92
  Latency        1.04ms   346.77us     6.23ms
  Latency Distribution
     50%     0.96ms
     75%     1.30ms
     90%     1.66ms
     99%     2.45ms
### CBV Response Types (/cbv-response)
  Reqs/sec    100417.11   11319.13  121408.93
  Latency        1.02ms   335.47us     4.67ms
  Latency Distribution
     50%     0.95ms
     75%     1.26ms
     90%     1.62ms
     99%     2.55ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     17075.70    1380.75   20960.42
  Latency        5.86ms     1.54ms    15.90ms
  Latency Distribution
     50%     5.75ms
     75%     7.13ms
     90%     8.25ms
     99%    10.51ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     92381.95    7206.38   97869.43
  Latency        1.06ms   352.06us     4.42ms
  Latency Distribution
     50%     0.99ms
     75%     1.31ms
     90%     1.66ms
     99%     2.71ms
### File Upload (POST /upload)
  Reqs/sec     87469.95    7678.94   93469.11
  Latency        1.12ms   367.93us     5.56ms
  Latency Distribution
     50%     1.05ms
     75%     1.36ms
     90%     1.70ms
     99%     2.57ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     85466.33    5777.30   90065.41
  Latency        1.15ms   375.55us     4.90ms
  Latency Distribution
     50%     1.08ms
     75%     1.44ms
     90%     1.81ms
     99%     2.75ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
 0 / 10000 [---------------------------------------------------------------------------------------------------------------------------------------------]   0.00% 1860 / 10000 [========================>----------------------------------------------------------------------------------------------------------]  18.60% 9266/s 3842 / 10000 [==================================================>--------------------------------------------------------------------------------]  38.42% 9582/s 5850 / 10000 [============================================================================>------------------------------------------------------]  58.50% 9729/s 7832 / 10000 [======================================================================================================>----------------------------]  78.32% 9769/s 9816 / 10000 [================================================================================================================================>--]  98.16% 9796/s 10000 / 10000 [==================================================================================================================================] 100.00% 8311/s 10000 / 10000 [===============================================================================================================================] 100.00% 8310/s 1s
  Reqs/sec      9822.77     965.38   11047.74
  Latency       10.15ms     2.97ms    25.20ms
  Latency Distribution
     50%     9.57ms
     75%    12.95ms
     90%    14.66ms
     99%    18.81ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    100971.20   10399.12  118104.28
  Latency        1.01ms   379.33us     4.91ms
  Latency Distribution
     50%     0.93ms
     75%     1.22ms
     90%     1.56ms
     99%     2.85ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     98218.33   10586.34  116730.89
  Latency        1.03ms   366.11us     5.30ms
  Latency Distribution
     50%     0.96ms
     75%     1.26ms
     90%     1.62ms
     99%     2.56ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     85592.21    6644.27   90837.46
  Latency        1.15ms   435.32us     5.03ms
  Latency Distribution
     50%     1.05ms
     75%     1.37ms
     90%     1.82ms
     99%     3.17ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     97545.16    9631.59  114048.56
  Latency        1.03ms   337.74us     4.92ms
  Latency Distribution
     50%     0.96ms
     75%     1.25ms
     90%     1.60ms
     99%     2.42ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    113649.57   10184.87  121767.00
  Latency        0.88ms   309.35us     5.05ms
  Latency Distribution
     50%   824.00us
     75%     1.05ms
     90%     1.30ms
     99%     2.04ms

### Path Parameter - int (/items/12345)
  Reqs/sec    103442.75    7099.86  108371.94
  Latency        0.95ms   291.92us     5.22ms
  Latency Distribution
     50%     0.91ms
     75%     1.17ms
     90%     1.47ms
     99%     2.09ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    103954.34    6632.69  107507.82
  Latency        0.94ms   268.85us     5.50ms
  Latency Distribution
     50%     0.89ms
     75%     1.16ms
     90%     1.47ms
     99%     2.08ms

### Header Parameter (/header)
  Reqs/sec    102079.89    6607.44  106222.04
  Latency        0.96ms   293.39us     4.47ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.48ms
     99%     2.16ms

### Cookie Parameter (/cookie)
  Reqs/sec    103906.33    7104.19  108231.57
  Latency        0.95ms   301.73us     4.89ms
  Latency Distribution
     50%     0.88ms
     75%     1.16ms
     90%     1.44ms
     99%     2.18ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     85980.69    5365.32   89839.38
  Latency        1.15ms   351.72us     4.90ms
  Latency Distribution
     50%     1.07ms
     75%     1.42ms
     90%     1.81ms
     99%     2.64ms

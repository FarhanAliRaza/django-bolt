# Django-Bolt Benchmark
Generated: Mon Jan  5 07:48:11 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    123358.70   13183.68  134349.03
  Latency      792.26us   272.77us     4.57ms
  Latency Distribution
     50%   729.00us
     75%     0.95ms
     90%     1.20ms
     99%     1.97ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     96852.74    9654.48  110071.97
  Latency        1.03ms   320.82us     4.86ms
  Latency Distribution
     50%     0.96ms
     75%     1.27ms
     90%     1.59ms
     99%     2.36ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     99577.59    7972.28  104403.82
  Latency        0.98ms   272.23us     4.07ms
  Latency Distribution
     50%     0.92ms
     75%     1.19ms
     90%     1.48ms
     99%     2.30ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    115278.57    7642.43  120487.40
  Latency      849.01us   253.69us     3.41ms
  Latency Distribution
     50%   795.00us
     75%     1.06ms
     90%     1.36ms
     99%     1.98ms
### Cookie Endpoint (/cookie)
  Reqs/sec    116889.87    8196.86  124053.37
  Latency      827.96us   235.55us     4.07ms
  Latency Distribution
     50%   773.00us
     75%     0.99ms
     90%     1.26ms
     99%     1.86ms
### Exception Endpoint (/exc)
  Reqs/sec    120545.52   11992.30  135206.55
  Latency      832.16us   224.25us     3.51ms
  Latency Distribution
     50%   773.00us
     75%     1.00ms
     90%     1.25ms
     99%     1.89ms
### HTML Response (/html)
  Reqs/sec    124039.57   11470.65  131969.54
  Latency      791.36us   274.12us     4.48ms
  Latency Distribution
     50%   735.00us
     75%     0.96ms
     90%     1.21ms
     99%     1.96ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     35739.47    9522.18   43116.59
  Latency        2.79ms     1.67ms    22.74ms
  Latency Distribution
     50%     2.48ms
     75%     3.15ms
     90%     3.88ms
     99%    12.21ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     86286.99    6255.00   90314.20
  Latency        1.14ms   322.09us     4.00ms
  Latency Distribution
     50%     1.10ms
     75%     1.41ms
     90%     1.74ms
     99%     2.51ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     18469.77    1570.68   20330.75
  Latency        5.39ms     1.07ms    13.54ms
  Latency Distribution
     50%     5.36ms
     75%     6.12ms
     90%     6.93ms
     99%     9.06ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     16862.39    1177.01   18125.42
  Latency        5.89ms     1.96ms    15.86ms
  Latency Distribution
     50%     5.53ms
     75%     7.47ms
     90%     9.04ms
     99%    11.84ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     89872.59    7671.88   97870.57
  Latency        1.07ms   339.93us     5.67ms
  Latency Distribution
     50%     1.01ms
     75%     1.32ms
     90%     1.66ms
     99%     2.51ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    104408.06    5355.71  108221.75
  Latency        0.94ms   279.87us     3.97ms
  Latency Distribution
     50%     0.90ms
     75%     1.18ms
     90%     1.47ms
     99%     2.22ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     75670.31   16564.28   91512.86
  Latency        1.31ms   761.65us     8.49ms
  Latency Distribution
     50%     1.09ms
     75%     1.68ms
     90%     2.26ms
     99%     4.95ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     15136.27    2565.50   16861.33
  Latency        6.41ms     1.96ms    46.73ms
  Latency Distribution
     50%     6.32ms
     75%     7.32ms
     90%     8.58ms
     99%    11.07ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     13417.89    2022.81   17958.62
  Latency        7.46ms     5.87ms    72.41ms
  Latency Distribution
     50%     7.09ms
     75%     8.63ms
     90%    10.21ms
     99%    15.52ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     18032.72    1068.77   20262.39
  Latency        5.52ms     1.41ms    12.51ms
  Latency Distribution
     50%     5.39ms
     75%     6.62ms
     90%     7.73ms
     99%     9.94ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     15823.09    1693.86   18016.14
  Latency        6.30ms     2.99ms    26.96ms
  Latency Distribution
     50%     5.56ms
     75%     7.98ms
     90%    10.77ms
     99%    16.97ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    124336.12    9487.96  131571.65
  Latency      789.77us   274.58us     4.18ms
  Latency Distribution
     50%   735.00us
     75%     0.95ms
     90%     1.20ms
     99%     2.10ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    121162.29   10539.44  131954.38
  Latency      821.64us   232.61us     4.19ms
  Latency Distribution
     50%   764.00us
     75%     0.99ms
     90%     1.24ms
     99%     1.82ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     69447.65    8917.12   80590.79
  Latency        1.43ms   568.01us     7.51ms
  Latency Distribution
     50%     1.26ms
     75%     1.63ms
     90%     2.12ms
     99%     4.32ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    107126.16    5776.27  111696.79
  Latency        0.92ms   316.11us     3.79ms
  Latency Distribution
     50%   847.00us
     75%     1.12ms
     90%     1.45ms
     99%     2.50ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    111674.78    7652.88  117040.76
  Latency        0.88ms   261.75us     4.12ms
  Latency Distribution
     50%   817.00us
     75%     1.08ms
     90%     1.36ms
     99%     2.00ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    113572.93   10344.32  122319.85
  Latency        0.86ms   360.36us     6.43ms
  Latency Distribution
     50%   805.00us
     75%     1.04ms
     90%     1.29ms
     99%     2.09ms
### CBV Response Types (/cbv-response)
  Reqs/sec    124156.18   12901.98  142633.37
  Latency      816.90us   248.69us     3.73ms
  Latency Distribution
     50%   763.00us
     75%     1.01ms
     90%     1.26ms
     99%     1.98ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     18689.53    2249.76   26970.96
  Latency        5.40ms     2.39ms    54.63ms
  Latency Distribution
     50%     5.29ms
     75%     6.43ms
     90%     7.92ms
     99%    10.79ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     86357.68   16083.35  109685.20
  Latency        1.19ms   694.03us    12.60ms
  Latency Distribution
     50%     1.07ms
     75%     1.42ms
     90%     1.89ms
     99%     4.05ms
### File Upload (POST /upload)
  Reqs/sec    100308.54    7024.32  105787.25
  Latency        0.97ms   283.06us     4.64ms
  Latency Distribution
     50%     0.92ms
     75%     1.20ms
     90%     1.47ms
     99%     2.21ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     98754.19    7569.89  106055.41
  Latency        0.99ms   297.81us     4.46ms
  Latency Distribution
     50%     0.94ms
     75%     1.21ms
     90%     1.50ms
     99%     2.30ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec     14292.09    4219.91   17548.59
  Latency        6.70ms     5.85ms    84.13ms
  Latency Distribution
     50%     5.96ms
     75%     7.12ms
     90%     8.74ms
     99%    12.78ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    117899.55   12773.91  131406.32
  Latency      843.52us   300.17us     4.72ms
  Latency Distribution
     50%   763.00us
     75%     1.04ms
     90%     1.32ms
     99%     2.11ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec    111887.53    9352.95  118780.90
  Latency        0.87ms   260.96us     4.87ms
  Latency Distribution
     50%   800.00us
     75%     1.08ms
     90%     1.35ms
     99%     1.97ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec    105862.93   10586.28  114581.67
  Latency        0.93ms   266.98us     4.31ms
  Latency Distribution
     50%     0.86ms
     75%     1.10ms
     90%     1.37ms
     99%     2.09ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    115700.23    8983.55  122981.06
  Latency        0.86ms   240.26us     3.86ms
  Latency Distribution
     50%   803.00us
     75%     1.03ms
     90%     1.30ms
     99%     1.94ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    128580.86   10418.53  135216.94
  Latency      757.35us   259.16us     3.97ms
  Latency Distribution
     50%   688.00us
     75%     0.92ms
     90%     1.18ms
     99%     2.01ms

### Path Parameter - int (/items/12345)
  Reqs/sec    121262.49   13345.38  140859.92
  Latency      829.64us   242.21us     4.34ms
  Latency Distribution
     50%   775.00us
     75%     1.00ms
     90%     1.26ms
     99%     1.89ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    115142.45    9469.79  122421.07
  Latency        0.86ms   243.90us     3.75ms
  Latency Distribution
     50%   806.00us
     75%     1.05ms
     90%     1.30ms
     99%     1.96ms

### Header Parameter (/header)
  Reqs/sec    117294.33   10342.34  129388.02
  Latency      849.86us   286.16us     3.89ms
  Latency Distribution
     50%   787.00us
     75%     1.05ms
     90%     1.36ms
     99%     2.04ms

### Cookie Parameter (/cookie)
  Reqs/sec    124853.76   15556.16  147298.30
  Latency      816.69us   226.33us     3.58ms
  Latency Distribution
     50%   768.00us
     75%     0.99ms
     90%     1.25ms
     99%     1.85ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec    101451.11    8509.06  105676.47
  Latency        0.97ms   299.28us     5.08ms
  Latency Distribution
     50%     0.91ms
     75%     1.16ms
     90%     1.44ms
     99%     2.23ms

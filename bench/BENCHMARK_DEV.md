# Django-Bolt Benchmark
Generated: Mon Jan  5 06:14:13 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    124593.20   14090.13  144749.01
  Latency      816.00us   310.76us     4.63ms
  Latency Distribution
     50%   746.00us
     75%     0.99ms
     90%     1.27ms
     99%     2.15ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     99898.31    7185.02  103902.49
  Latency        0.98ms   283.85us     4.64ms
  Latency Distribution
     50%     0.92ms
     75%     1.16ms
     90%     1.48ms
     99%     2.15ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     99419.33    8900.38  107840.14
  Latency        1.00ms   304.41us     5.08ms
  Latency Distribution
     50%     0.93ms
     75%     1.19ms
     90%     1.49ms
     99%     2.27ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    117846.19    8065.11  124721.32
  Latency      841.40us   246.03us     4.10ms
  Latency Distribution
     50%   791.00us
     75%     1.02ms
     90%     1.30ms
     99%     1.91ms
### Cookie Endpoint (/cookie)
  Reqs/sec    119244.26    8257.31  125126.97
  Latency      831.70us   260.43us     3.60ms
  Latency Distribution
     50%   752.00us
     75%     1.02ms
     90%     1.32ms
     99%     2.03ms
### Exception Endpoint (/exc)
  Reqs/sec    116750.60    9421.85  121735.60
  Latency      841.00us   282.64us     4.85ms
  Latency Distribution
     50%   774.00us
     75%     1.04ms
     90%     1.36ms
     99%     2.06ms
### HTML Response (/html)
  Reqs/sec    123662.74   11795.60  130982.07
  Latency      790.08us   265.91us     5.02ms
  Latency Distribution
     50%   733.00us
     75%     0.94ms
     90%     1.21ms
     99%     1.87ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     33651.42    9718.60   41841.78
  Latency        2.96ms     2.40ms    30.90ms
  Latency Distribution
     50%     2.40ms
     75%     3.58ms
     90%     4.95ms
     99%    13.94ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     84614.23    8971.55   90352.03
  Latency        1.16ms   389.09us     4.28ms
  Latency Distribution
     50%     1.07ms
     75%     1.41ms
     90%     1.83ms
     99%     2.96ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     21790.85   17763.42  112074.96
  Latency        5.39ms     1.38ms    15.66ms
  Latency Distribution
     50%     5.34ms
     75%     6.39ms
     90%     7.53ms
     99%     9.67ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     16836.18    1366.37   18880.75
  Latency        5.89ms     1.37ms    14.14ms
  Latency Distribution
     50%     5.80ms
     75%     6.86ms
     90%     7.94ms
     99%    10.32ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     77403.30    6331.44   85693.14
  Latency        1.25ms   406.21us     7.27ms
  Latency Distribution
     50%     1.22ms
     75%     1.56ms
     90%     1.98ms
     99%     2.96ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    102977.26    7235.97  107510.83
  Latency        0.95ms   323.52us     4.44ms
  Latency Distribution
     50%     0.86ms
     75%     1.18ms
     90%     1.58ms
     99%     2.43ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec    105491.77    7310.06  109822.77
  Latency        0.93ms   291.16us     3.92ms
  Latency Distribution
     50%     0.86ms
     75%     1.14ms
     90%     1.49ms
     99%     2.17ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     15263.43    2209.37   18329.12
  Latency        6.37ms     1.64ms    17.77ms
  Latency Distribution
     50%     6.18ms
     75%     7.38ms
     90%     8.91ms
     99%    11.91ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     13316.90    1693.87   16530.24
  Latency        7.48ms     5.81ms    70.77ms
  Latency Distribution
     50%     6.78ms
     75%     8.37ms
     90%     9.96ms
     99%    14.82ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     17956.76     904.59   19827.23
  Latency        5.52ms     1.83ms    13.74ms
  Latency Distribution
     50%     5.38ms
     75%     6.95ms
     90%     8.45ms
     99%    10.87ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     15653.91    1826.59   18753.31
  Latency        6.35ms     2.97ms    30.86ms
  Latency Distribution
     50%     5.54ms
     75%     7.72ms
     90%    10.52ms
     99%    17.86ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    124184.00   10197.10  131480.63
  Latency      792.25us   261.82us     4.68ms
  Latency Distribution
     50%   741.00us
     75%     0.96ms
     90%     1.21ms
     99%     2.01ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    111683.01   10278.89  123876.76
  Latency        0.89ms   312.71us     4.75ms
  Latency Distribution
     50%   809.00us
     75%     1.09ms
     90%     1.42ms
     99%     2.25ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     73872.46    5439.82   79928.76
  Latency        1.34ms   415.84us     5.49ms
  Latency Distribution
     50%     1.24ms
     75%     1.59ms
     90%     2.04ms
     99%     3.10ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    111191.17    8011.18  117683.84
  Latency        0.89ms   264.58us     4.19ms
  Latency Distribution
     50%   815.00us
     75%     1.07ms
     90%     1.37ms
     99%     2.10ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    110521.01    6808.41  118006.78
  Latency        0.88ms   242.65us     3.54ms
  Latency Distribution
     50%   823.00us
     75%     1.07ms
     90%     1.36ms
     99%     1.99ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    112611.00    8008.19  119910.97
  Latency        0.86ms   228.93us     3.67ms
  Latency Distribution
     50%   817.00us
     75%     1.08ms
     90%     1.34ms
     99%     1.84ms
### CBV Response Types (/cbv-response)
  Reqs/sec    120902.48   14644.29  143775.60
  Latency      833.46us   261.67us     5.07ms
  Latency Distribution
     50%   778.00us
     75%     1.02ms
     90%     1.28ms
     99%     2.04ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     17921.57    1801.02   20045.44
  Latency        5.55ms     3.17ms    79.78ms
  Latency Distribution
     50%     5.20ms
     75%     6.79ms
     90%     8.21ms
     99%    13.13ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    110497.97    8163.39  115777.91
  Latency        0.89ms   319.19us     5.32ms
  Latency Distribution
     50%   815.00us
     75%     1.07ms
     90%     1.34ms
     99%     2.24ms
### File Upload (POST /upload)
  Reqs/sec    101912.84    6554.43  106961.30
  Latency        0.96ms   276.58us     4.28ms
  Latency Distribution
     50%     0.91ms
     75%     1.18ms
     90%     1.47ms
     99%     2.20ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     95022.04    9442.74  101635.28
  Latency        1.00ms   310.76us     5.94ms
  Latency Distribution
     50%     0.95ms
     75%     1.23ms
     90%     1.54ms
     99%     2.32ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec     14324.95    3913.38   17670.30
  Latency        6.55ms     4.80ms    76.60ms
  Latency Distribution
     50%     5.91ms
     75%     7.81ms
     90%     9.58ms
     99%    13.62ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    117309.14   11984.91  130591.53
  Latency      845.57us   254.75us     4.83ms
  Latency Distribution
     50%   784.00us
     75%     1.06ms
     90%     1.35ms
     99%     1.94ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec    113835.04   10315.62  120409.98
  Latency        0.87ms   270.40us     4.20ms
  Latency Distribution
     50%   816.00us
     75%     1.04ms
     90%     1.30ms
     99%     2.08ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec    104554.57    7363.51  111135.92
  Latency        0.93ms   265.79us     4.84ms
  Latency Distribution
     50%     0.87ms
     75%     1.12ms
     90%     1.39ms
     99%     2.06ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    115474.77   11083.68  125688.64
  Latency      849.63us   237.43us     3.87ms
  Latency Distribution
     50%   785.00us
     75%     1.02ms
     90%     1.31ms
     99%     1.92ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    127352.55   12287.94  135131.74
  Latency      770.31us   282.27us     4.68ms
  Latency Distribution
     50%   714.00us
     75%     0.95ms
     90%     1.22ms
     99%     1.92ms

### Path Parameter - int (/items/12345)
  Reqs/sec    114068.01   12828.39  124656.89
  Latency      844.19us   274.86us     4.50ms
  Latency Distribution
     50%   781.00us
     75%     1.01ms
     90%     1.30ms
     99%     2.10ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    113842.84    9184.50  121012.14
  Latency        0.87ms   251.19us     3.44ms
  Latency Distribution
     50%   802.00us
     75%     1.07ms
     90%     1.38ms
     99%     2.03ms

### Header Parameter (/header)
  Reqs/sec    118135.10    9380.55  123663.43
  Latency      834.57us   286.52us     5.03ms
  Latency Distribution
     50%   776.00us
     75%     1.00ms
     90%     1.26ms
     99%     1.87ms

### Cookie Parameter (/cookie)
  Reqs/sec    117883.11   10753.71  124013.37
  Latency      837.18us   285.09us     4.22ms
  Latency Distribution
     50%   773.00us
     75%     1.03ms
     90%     1.30ms
     99%     2.04ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     90060.43    3691.87   94280.59
  Latency        1.08ms   360.16us     4.44ms
  Latency Distribution
     50%     1.00ms
     75%     1.30ms
     90%     1.70ms
     99%     2.62ms

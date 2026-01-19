# Django-Bolt Benchmark
Generated: Mon Jan 19 08:49:10 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    122305.37   10078.08  130880.24
  Latency      797.44us   337.88us     5.80ms
  Latency Distribution
     50%   730.00us
     75%     0.97ms
     90%     1.20ms
     99%     1.96ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec    106778.59   23502.04  152385.26
  Latency        1.01ms   312.72us     4.52ms
  Latency Distribution
     50%     0.94ms
     75%     1.20ms
     90%     1.50ms
     99%     2.42ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     98804.92    8087.60  105653.65
  Latency        0.99ms   302.30us     5.09ms
  Latency Distribution
     50%     0.93ms
     75%     1.17ms
     90%     1.48ms
     99%     2.37ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    115019.94   12428.37  124559.07
  Latency      845.44us   312.30us     5.79ms
  Latency Distribution
     50%   785.00us
     75%     1.02ms
     90%     1.30ms
     99%     2.02ms
### Cookie Endpoint (/cookie)
  Reqs/sec    118561.19    8995.87  124449.22
  Latency      828.89us   273.82us     4.57ms
  Latency Distribution
     50%   768.00us
     75%     1.03ms
     90%     1.33ms
     99%     1.93ms
### Exception Endpoint (/exc)
  Reqs/sec    118398.50    9603.23  124337.00
  Latency      833.07us   291.49us     4.52ms
  Latency Distribution
     50%   767.00us
     75%     1.01ms
     90%     1.30ms
     99%     1.98ms
### HTML Response (/html)
  Reqs/sec    123012.45   11346.80  135547.84
  Latency      817.23us   255.54us     4.99ms
  Latency Distribution
     50%   764.00us
     75%     1.00ms
     90%     1.26ms
     99%     1.84ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     23953.13   16429.95   40337.11
  Latency        4.23ms    11.78ms   165.09ms
  Latency Distribution
     50%     2.59ms
     75%     3.51ms
     90%     4.82ms
     99%    42.79ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     87681.85    5307.00   91069.27
  Latency        1.13ms   331.52us     6.14ms
  Latency Distribution
     50%     1.05ms
     75%     1.34ms
     90%     1.69ms
     99%     2.63ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     18378.21    1501.66   20882.11
  Latency        5.43ms     1.26ms    14.83ms
  Latency Distribution
     50%     5.33ms
     75%     6.33ms
     90%     7.50ms
     99%     9.50ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     16767.98    1218.12   18042.68
  Latency        5.89ms     1.41ms    12.77ms
  Latency Distribution
     50%     5.79ms
     75%     7.08ms
     90%     8.15ms
     99%     9.93ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     83568.76    6492.25   92953.20
  Latency        1.18ms   393.59us     4.41ms
  Latency Distribution
     50%     1.07ms
     75%     1.48ms
     90%     1.95ms
     99%     2.85ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    111012.39    7473.89  121532.32
  Latency        0.88ms   268.56us     4.01ms
  Latency Distribution
     50%   813.00us
     75%     1.09ms
     90%     1.40ms
     99%     2.05ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec    104550.40   11311.17  115320.72
  Latency        0.94ms   328.00us     4.72ms
  Latency Distribution
     50%     0.86ms
     75%     1.14ms
     90%     1.50ms
     99%     2.31ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13945.35    2443.24   16798.16
  Latency        6.89ms     3.28ms    73.74ms
  Latency Distribution
     50%     6.28ms
     75%     8.60ms
     90%    10.62ms
     99%    14.22ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12853.33    2534.81   15907.72
  Latency        7.48ms     5.75ms    68.44ms
  Latency Distribution
     50%     6.80ms
     75%     8.67ms
     90%    10.61ms
     99%    25.93ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     18270.17    1181.11   22279.35
  Latency        5.47ms     1.66ms    14.23ms
  Latency Distribution
     50%     5.40ms
     75%     6.82ms
     90%     8.02ms
     99%    10.30ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     15883.62    2003.61   17752.00
  Latency        6.26ms     3.58ms    38.21ms
  Latency Distribution
     50%     5.09ms
     75%     7.86ms
     90%    11.69ms
     99%    19.34ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    118606.95   10573.58  127557.94
  Latency      821.69us   352.37us     4.20ms
  Latency Distribution
     50%   691.00us
     75%     1.04ms
     90%     1.44ms
     99%     2.41ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    117093.82    9484.87  124260.37
  Latency      840.61us   279.30us     4.54ms
  Latency Distribution
     50%   771.00us
     75%     1.03ms
     90%     1.32ms
     99%     2.15ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     73663.04    5040.87   76981.70
  Latency        1.34ms   352.95us     5.89ms
  Latency Distribution
     50%     1.26ms
     75%     1.56ms
     90%     1.94ms
     99%     2.82ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    114153.41    8879.56  120434.70
  Latency        0.86ms   250.69us     4.40ms
  Latency Distribution
     50%   802.00us
     75%     1.05ms
     90%     1.31ms
     99%     1.91ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    110259.50    9643.50  117113.01
  Latency        0.89ms   312.28us     5.38ms
  Latency Distribution
     50%   808.00us
     75%     1.10ms
     90%     1.43ms
     99%     2.30ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    109814.20   11810.06  120811.11
  Latency        0.88ms   235.58us     3.93ms
  Latency Distribution
     50%   826.00us
     75%     1.07ms
     90%     1.35ms
     99%     1.95ms
### CBV Response Types (/cbv-response)
  Reqs/sec    114102.39   16126.87  127493.76
  Latency      808.01us   236.22us     5.14ms
  Latency Distribution
     50%   760.00us
     75%     0.98ms
     90%     1.22ms
     99%     1.84ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     18311.10    1343.00   19787.42
  Latency        5.42ms     2.71ms    60.26ms
  Latency Distribution
     50%     5.36ms
     75%     6.45ms
     90%     7.79ms
     99%    10.84ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    103180.40   11264.88  114688.14
  Latency        0.94ms   350.32us     4.75ms
  Latency Distribution
     50%     0.85ms
     75%     1.15ms
     90%     1.48ms
     99%     2.62ms
### File Upload (POST /upload)
  Reqs/sec    100336.07   11558.29  119534.99
  Latency        1.01ms   328.05us     5.08ms
  Latency Distribution
     50%     0.95ms
     75%     1.24ms
     90%     1.62ms
     99%     2.46ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     98898.36    7369.46  103108.62
  Latency        0.99ms   287.19us     4.91ms
  Latency Distribution
     50%     0.94ms
     75%     1.19ms
     90%     1.51ms
     99%     2.27ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9131.46    1253.11   11401.53
  Latency       10.92ms     6.58ms    78.39ms
  Latency Distribution
     50%    11.10ms
     75%    12.54ms
     90%    13.51ms
     99%    21.98ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    121803.70   12046.02  136470.72
  Latency      828.06us   278.81us     4.78ms
  Latency Distribution
     50%   767.00us
     75%     1.00ms
     90%     1.26ms
     99%     1.97ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec    112581.71    9922.82  119073.61
  Latency        0.87ms   290.51us     4.83ms
  Latency Distribution
     50%   814.00us
     75%     1.06ms
     90%     1.39ms
     99%     2.29ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec    104264.13    9950.27  110025.37
  Latency        0.93ms   319.46us     5.02ms
  Latency Distribution
     50%     0.86ms
     75%     1.11ms
     90%     1.40ms
     99%     2.25ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    111034.52    8448.00  118050.97
  Latency        0.88ms   251.59us     4.07ms
  Latency Distribution
     50%   836.00us
     75%     1.09ms
     90%     1.36ms
     99%     1.91ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    126982.05    9947.91  132853.67
  Latency      771.85us   283.95us     4.59ms
  Latency Distribution
     50%   708.00us
     75%     0.93ms
     90%     1.17ms
     99%     2.00ms

### Path Parameter - int (/items/12345)
  Reqs/sec    119000.11    9452.51  126726.96
  Latency      823.87us   251.93us     4.45ms
  Latency Distribution
     50%   767.00us
     75%     1.00ms
     90%     1.23ms
     99%     1.94ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    117962.07    9317.05  124243.87
  Latency      836.85us   250.21us     4.36ms
  Latency Distribution
     50%   781.00us
     75%     1.01ms
     90%     1.27ms
     99%     1.91ms

### Header Parameter (/header)
  Reqs/sec    116412.13   10260.71  126240.59
  Latency      822.14us   247.94us     4.01ms
  Latency Distribution
     50%   762.00us
     75%     1.01ms
     90%     1.28ms
     99%     1.97ms

### Cookie Parameter (/cookie)
  Reqs/sec    123653.90   14782.04  146029.40
  Latency      820.82us   263.90us     4.24ms
  Latency Distribution
     50%   754.00us
     75%     1.02ms
     90%     1.29ms
     99%     2.02ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     98747.39    7292.93  103943.71
  Latency        1.00ms   312.69us     4.95ms
  Latency Distribution
     50%     0.94ms
     75%     1.25ms
     90%     1.56ms
     99%     2.27ms

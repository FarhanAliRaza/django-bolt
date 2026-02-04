# Django-Bolt Benchmark
Generated: Tue 03 Feb 2026 10:26:03 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec     85359.54   12228.09   99845.88
  Latency        1.14ms   477.42us     5.40ms
  Latency Distribution
     50%     1.03ms
     75%     1.42ms
     90%     1.87ms
     99%     3.26ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     84714.58    7279.42   90190.71
  Latency        1.17ms   429.68us     7.88ms
  Latency Distribution
     50%     1.07ms
     75%     1.42ms
     90%     1.80ms
     99%     2.94ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     75523.48   18749.28   88806.56
  Latency        1.20ms   383.30us     6.26ms
  Latency Distribution
     50%     1.12ms
     75%     1.46ms
     90%     1.80ms
     99%     2.96ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     92605.39    9010.14  101563.61
  Latency        1.04ms   399.06us     6.71ms
  Latency Distribution
     50%     0.96ms
     75%     1.30ms
     90%     1.68ms
     99%     2.75ms
### Cookie Endpoint (/cookie)
  Reqs/sec     94388.31    5764.50   99628.86
  Latency        1.04ms   385.49us     4.62ms
  Latency Distribution
     50%     0.94ms
     75%     1.28ms
     90%     1.65ms
     99%     2.88ms
### Exception Endpoint (/exc)
  Reqs/sec     97861.80    8504.75  106983.83
  Latency        1.03ms   375.11us     5.76ms
  Latency Distribution
     50%     0.94ms
     75%     1.27ms
     90%     1.62ms
     99%     2.78ms
### HTML Response (/html)
  Reqs/sec     93465.91    7227.24  105635.19
  Latency        1.03ms   401.83us     4.43ms
  Latency Distribution
     50%     0.93ms
     75%     1.26ms
     90%     1.66ms
     99%     3.07ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     26844.93    8215.76   42540.92
  Latency        3.86ms     2.49ms    37.65ms
  Latency Distribution
     50%     3.25ms
     75%     4.43ms
     90%     6.18ms
     99%    14.96ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     75264.67    6142.55   81960.16
  Latency        1.30ms   455.54us     7.20ms
  Latency Distribution
     50%     1.21ms
     75%     1.58ms
     90%     2.03ms
     99%     3.24ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     16281.86    1502.23   17739.83
  Latency        6.12ms     2.53ms    17.98ms
  Latency Distribution
     50%     6.23ms
     75%     8.40ms
     90%     9.85ms
     99%    13.77ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15242.08     965.15   16987.93
  Latency        6.52ms     1.84ms    14.75ms
  Latency Distribution
     50%     6.36ms
     75%     7.99ms
     90%     9.47ms
     99%    12.12ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec    140748.37  157827.03  498442.37
  Latency        1.21ms   433.55us     4.95ms
  Latency Distribution
     50%     1.11ms
     75%     1.50ms
     90%     1.93ms
     99%     3.11ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     99209.19   10572.00  108991.83
  Latency        1.01ms   354.96us     6.35ms
  Latency Distribution
     50%     0.93ms
     75%     1.23ms
     90%     1.57ms
     99%     2.42ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     87486.67    6804.86   92724.44
  Latency        1.12ms   380.58us     5.54ms
  Latency Distribution
     50%     1.05ms
     75%     1.41ms
     90%     1.78ms
     99%     2.80ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     14376.77     979.79   15431.40
  Latency        6.93ms     1.39ms    16.55ms
  Latency Distribution
     50%     6.84ms
     75%     7.87ms
     90%     8.79ms
     99%    11.41ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12838.06    1183.34   18538.20
  Latency        7.82ms     1.98ms    18.13ms
  Latency Distribution
     50%     7.60ms
     75%     9.31ms
     90%    10.84ms
     99%    13.81ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     16370.20     912.50   17685.62
  Latency        6.08ms     2.05ms    21.84ms
  Latency Distribution
     50%     5.69ms
     75%     7.10ms
     90%     9.16ms
     99%    13.26ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13626.40    1381.67   15703.50
  Latency        7.30ms     3.49ms    29.12ms
  Latency Distribution
     50%     6.25ms
     75%     9.19ms
     90%    12.90ms
     99%    18.96ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    105956.96    9630.94  114240.16
  Latency        0.93ms   385.40us     5.05ms
  Latency Distribution
     50%     0.86ms
     75%     1.12ms
     90%     1.42ms
     99%     2.88ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     99968.45    6177.98  105044.42
  Latency        0.98ms   315.31us     6.14ms
  Latency Distribution
     50%     0.92ms
     75%     1.24ms
     90%     1.59ms
     99%     2.36ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     68394.53    4006.09   73581.63
  Latency        1.46ms   389.74us     4.69ms
  Latency Distribution
     50%     1.38ms
     75%     1.74ms
     90%     2.14ms
     99%     3.11ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     98071.00    7982.52  105870.92
  Latency        1.01ms   305.54us     4.15ms
  Latency Distribution
     50%     0.94ms
     75%     1.23ms
     90%     1.53ms
     99%     2.47ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     92866.76    5635.59   97705.93
  Latency        1.04ms   307.54us     4.25ms
  Latency Distribution
     50%     0.97ms
     75%     1.30ms
     90%     1.63ms
     99%     2.37ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    100199.67   11958.39  120061.98
  Latency        1.01ms   322.83us     5.47ms
  Latency Distribution
     50%     0.95ms
     75%     1.24ms
     90%     1.59ms
     99%     2.29ms
### CBV Response Types (/cbv-response)
  Reqs/sec    101703.11    6230.14  107237.19
  Latency        0.96ms   350.03us     5.16ms
  Latency Distribution
     50%     0.89ms
     75%     1.19ms
     90%     1.52ms
     99%     2.56ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16764.07    1168.76   18039.12
  Latency        5.92ms     2.07ms    17.20ms
  Latency Distribution
     50%     5.32ms
     75%     7.47ms
     90%     9.52ms
     99%    12.32ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     90644.20    6780.10   97313.51
  Latency        1.08ms   344.03us     4.49ms
  Latency Distribution
     50%     1.01ms
     75%     1.34ms
     90%     1.64ms
     99%     2.68ms
### File Upload (POST /upload)
  Reqs/sec     87659.04    5743.12   92811.43
  Latency        1.12ms   356.92us     5.34ms
  Latency Distribution
     50%     1.06ms
     75%     1.38ms
     90%     1.72ms
     99%     2.65ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     83624.57    6840.29   89325.79
  Latency        1.18ms   426.29us     5.20ms
  Latency Distribution
     50%     1.06ms
     75%     1.50ms
     90%     2.01ms
     99%     3.00ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9512.75    1016.36   12333.22
  Latency       10.51ms     2.83ms    26.78ms
  Latency Distribution
     50%     9.87ms
     75%    11.80ms
     90%    15.34ms
     99%    20.01ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    103658.81    8878.18  110225.91
  Latency        0.94ms   334.84us     6.63ms
  Latency Distribution
     50%     0.86ms
     75%     1.15ms
     90%     1.46ms
     99%     2.29ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     96994.64    8663.06  103832.20
  Latency        1.02ms   354.96us     5.01ms
  Latency Distribution
     50%     0.93ms
     75%     1.25ms
     90%     1.59ms
     99%     2.58ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     89289.23    6453.89   94941.43
  Latency        1.11ms   360.97us     5.12ms
  Latency Distribution
     50%     1.04ms
     75%     1.34ms
     90%     1.66ms
     99%     2.60ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     94742.63    6730.57  101901.00
  Latency        1.03ms   332.64us     4.68ms
  Latency Distribution
     50%     0.96ms
     75%     1.25ms
     90%     1.59ms
     99%     2.45ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    108900.86    7968.64  115752.44
  Latency        0.90ms   354.07us     5.01ms
  Latency Distribution
     50%   814.00us
     75%     1.12ms
     90%     1.48ms
     99%     2.52ms

### Path Parameter - int (/items/12345)
  Reqs/sec    100807.66    5833.40  108965.18
  Latency        0.97ms   323.71us     5.69ms
  Latency Distribution
     50%     0.90ms
     75%     1.19ms
     90%     1.50ms
     99%     2.18ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec     97379.81    9882.34  113021.64
  Latency        1.04ms   382.86us     5.38ms
  Latency Distribution
     50%     0.96ms
     75%     1.28ms
     90%     1.63ms
     99%     2.75ms

### Header Parameter (/header)
  Reqs/sec     99676.17    8281.65  111130.46
  Latency        0.98ms   320.28us     4.41ms
  Latency Distribution
     50%     0.92ms
     75%     1.20ms
     90%     1.49ms
     99%     2.42ms

### Cookie Parameter (/cookie)
  Reqs/sec     99859.99    8102.40  107042.10
  Latency        0.98ms   374.56us     5.02ms
  Latency Distribution
     50%     0.90ms
     75%     1.23ms
     90%     1.59ms
     99%     2.67ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     83851.51    5680.88   89785.72
  Latency        1.17ms   392.98us     6.19ms
  Latency Distribution
     50%     1.09ms
     75%     1.44ms
     90%     1.82ms
     99%     2.98ms

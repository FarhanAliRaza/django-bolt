# Django-Bolt Benchmark
Generated: Sat Jan  3 10:19:52 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    112054.18    8325.44  119732.47
  Latency        0.89ms   356.55us     5.00ms
  Latency Distribution
     50%   798.00us
     75%     1.07ms
     90%     1.37ms
     99%     2.69ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec    101886.54    9579.18  117919.47
  Latency        1.00ms   327.90us     4.43ms
  Latency Distribution
     50%     0.92ms
     75%     1.22ms
     90%     1.51ms
     99%     2.49ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     99371.17    9394.68  112022.96
  Latency        1.01ms   352.91us     4.80ms
  Latency Distribution
     50%     0.92ms
     75%     1.23ms
     90%     1.54ms
     99%     2.62ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    104765.41    9405.35  114785.80
  Latency        0.92ms   348.69us     4.49ms
  Latency Distribution
     50%   834.00us
     75%     1.12ms
     90%     1.48ms
     99%     2.60ms
### Cookie Endpoint (/cookie)
  Reqs/sec    117551.42   10858.49  126148.69
  Latency      841.79us   276.75us     4.41ms
  Latency Distribution
     50%   768.00us
     75%     1.03ms
     90%     1.30ms
     99%     2.05ms
### Exception Endpoint (/exc)
  Reqs/sec    115489.85   11936.86  131325.88
  Latency        0.87ms   246.83us     3.53ms
  Latency Distribution
     50%   808.00us
     75%     1.06ms
     90%     1.36ms
     99%     1.99ms
### HTML Response (/html)
  Reqs/sec    123247.93   10553.32  128597.50
  Latency      795.55us   280.67us     4.68ms
  Latency Distribution
     50%   737.00us
     75%     0.98ms
     90%     1.24ms
     99%     1.96ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     36291.72    8415.81   40979.69
  Latency        2.74ms     1.64ms    18.95ms
  Latency Distribution
     50%     2.45ms
     75%     3.25ms
     90%     4.14ms
     99%     8.31ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     81163.76    7136.47   88429.13
  Latency        1.22ms   432.00us     6.86ms
  Latency Distribution
     50%     1.11ms
     75%     1.48ms
     90%     1.92ms
     99%     3.29ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17576.12    1462.83   20408.54
  Latency        5.68ms     1.71ms    13.70ms
  Latency Distribution
     50%     5.81ms
     75%     7.28ms
     90%     8.38ms
     99%    10.67ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15161.81    2433.11   18224.09
  Latency        6.56ms     3.27ms    31.75ms
  Latency Distribution
     50%     5.60ms
     75%     7.87ms
     90%    11.72ms
     99%    18.50ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     87182.70    6308.66   93677.81
  Latency        1.13ms   433.28us     5.32ms
  Latency Distribution
     50%     1.04ms
     75%     1.42ms
     90%     1.86ms
     99%     3.05ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    105107.50    6668.64  109725.43
  Latency        0.92ms   346.64us     4.77ms
  Latency Distribution
     50%   845.00us
     75%     1.11ms
     90%     1.44ms
     99%     2.64ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec    105101.02    8485.33  114002.38
  Latency        0.94ms   275.43us     3.80ms
  Latency Distribution
     50%     0.88ms
     75%     1.16ms
     90%     1.47ms
     99%     2.12ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     14802.45    1461.30   16790.04
  Latency        6.67ms     3.20ms    73.58ms
  Latency Distribution
     50%     5.77ms
     75%     8.56ms
     90%    10.87ms
     99%    14.21ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12462.66    2288.27   18108.60
  Latency        8.05ms     7.03ms    92.89ms
  Latency Distribution
     50%     7.04ms
     75%     9.21ms
     90%    11.52ms
     99%    18.66ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     17339.80    2628.73   20119.30
  Latency        5.59ms     1.54ms    15.24ms
  Latency Distribution
     50%     5.35ms
     75%     6.59ms
     90%     8.06ms
     99%    10.77ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     15689.92    1899.85   18374.92
  Latency        6.34ms     2.86ms    26.95ms
  Latency Distribution
     50%     5.78ms
     75%     8.09ms
     90%    10.78ms
     99%    15.81ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    112778.70   20422.43  129671.32
  Latency      808.53us   287.38us     4.26ms
  Latency Distribution
     50%   734.00us
     75%     0.98ms
     90%     1.24ms
     99%     2.25ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    109633.62    7302.06  116944.77
  Latency        0.89ms   339.46us     4.12ms
  Latency Distribution
     50%   805.00us
     75%     1.10ms
     90%     1.49ms
     99%     2.58ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     71611.12    6355.07   77581.60
  Latency        1.38ms   489.47us     7.59ms
  Latency Distribution
     50%     1.26ms
     75%     1.60ms
     90%     2.02ms
     99%     3.83ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    104646.66    9663.95  113177.13
  Latency        0.94ms   328.65us     6.77ms
  Latency Distribution
     50%     0.87ms
     75%     1.15ms
     90%     1.46ms
     99%     2.31ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    105530.23    6752.85  113267.86
  Latency        0.93ms   315.68us     5.62ms
  Latency Distribution
     50%   848.00us
     75%     1.14ms
     90%     1.50ms
     99%     2.42ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    111909.10    8354.10  117429.27
  Latency        0.88ms   266.60us     4.20ms
  Latency Distribution
     50%   811.00us
     75%     1.08ms
     90%     1.36ms
     99%     2.15ms
### CBV Response Types (/cbv-response)
  Reqs/sec    108211.86   11487.25  116668.32
  Latency        0.91ms   504.91us     7.50ms
  Latency Distribution
     50%   800.00us
     75%     1.12ms
     90%     1.47ms
     99%     2.74ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     17859.16    1481.64   19797.86
  Latency        5.56ms     2.33ms    59.03ms
  Latency Distribution
     50%     5.22ms
     75%     6.51ms
     90%     8.19ms
     99%    11.73ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    102953.00    7572.77  109587.01
  Latency        0.96ms   329.17us     4.95ms
  Latency Distribution
     50%     0.90ms
     75%     1.22ms
     90%     1.55ms
     99%     2.44ms
### File Upload (POST /upload)
  Reqs/sec     94651.69    6730.37  102676.04
  Latency        1.02ms   309.51us     5.25ms
  Latency Distribution
     50%     0.95ms
     75%     1.25ms
     90%     1.60ms
     99%     2.36ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec    102416.84   17180.44  134961.29
  Latency        1.03ms   321.27us     4.69ms
  Latency Distribution
     50%     0.98ms
     75%     1.24ms
     90%     1.54ms
     99%     2.41ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec     13263.70    4486.35   17171.09
  Latency        7.11ms     5.60ms    78.70ms
  Latency Distribution
     50%     6.14ms
     75%     7.74ms
     90%     9.65ms
     99%    20.73ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    115528.57    8955.02  121545.55
  Latency        0.85ms   311.72us     4.56ms
  Latency Distribution
     50%   775.00us
     75%     1.02ms
     90%     1.31ms
     99%     2.17ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec    108343.80    6611.29  115457.62
  Latency        0.90ms   278.03us     6.34ms
  Latency Distribution
     50%   831.00us
     75%     1.08ms
     90%     1.35ms
     99%     2.07ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     98180.54    7985.95  107470.33
  Latency        1.00ms   330.48us     4.17ms
  Latency Distribution
     50%     0.92ms
     75%     1.20ms
     90%     1.58ms
     99%     2.57ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    109992.95    8370.46  114546.39
  Latency        0.90ms   281.23us     3.59ms
  Latency Distribution
     50%   840.00us
     75%     1.11ms
     90%     1.43ms
     99%     2.15ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    126430.32   10147.87  134283.68
  Latency      769.39us   271.63us     4.61ms
  Latency Distribution
     50%   714.00us
     75%     0.93ms
     90%     1.20ms
     99%     1.84ms

### Path Parameter - int (/items/12345)
  Reqs/sec    111907.33    8469.29  123743.12
  Latency        0.87ms   294.46us     4.21ms
  Latency Distribution
     50%   801.00us
     75%     1.08ms
     90%     1.38ms
     99%     2.25ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    106280.22   14405.16  116317.08
  Latency        0.93ms   419.62us     6.64ms
  Latency Distribution
     50%   848.00us
     75%     1.11ms
     90%     1.41ms
     99%     2.76ms

### Header Parameter (/header)
  Reqs/sec    110955.39    8229.28  120052.68
  Latency        0.88ms   306.46us     5.94ms
  Latency Distribution
     50%   805.00us
     75%     1.08ms
     90%     1.38ms
     99%     2.20ms

### Cookie Parameter (/cookie)
  Reqs/sec    112038.80   11058.23  121013.67
  Latency        0.89ms   320.09us     4.48ms
  Latency Distribution
     50%   823.00us
     75%     1.07ms
     90%     1.40ms
     99%     2.30ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     93119.81    6241.64   97435.72
  Latency        1.06ms   358.95us     5.18ms
  Latency Distribution
     50%     0.98ms
     75%     1.31ms
     90%     1.65ms
     99%     2.54ms

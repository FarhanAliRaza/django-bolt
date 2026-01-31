# Django-Bolt Benchmark
Generated: Sun 01 Feb 2026 01:00:11 AM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    106104.99    9422.25  116983.45
  Latency        0.94ms   326.66us     4.05ms
  Latency Distribution
     50%     0.86ms
     75%     1.15ms
     90%     1.50ms
     99%     2.50ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     87771.51    8194.32   92755.83
  Latency        1.12ms   351.41us     5.40ms
  Latency Distribution
     50%     1.05ms
     75%     1.37ms
     90%     1.75ms
     99%     2.56ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     85511.99    6380.95   91961.68
  Latency        1.14ms   332.79us     5.35ms
  Latency Distribution
     50%     1.07ms
     75%     1.42ms
     90%     1.78ms
     99%     2.48ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    101463.35    8363.81  108280.94
  Latency        0.97ms   356.43us     5.02ms
  Latency Distribution
     50%     0.89ms
     75%     1.23ms
     90%     1.56ms
     99%     2.58ms
### Cookie Endpoint (/cookie)
  Reqs/sec    103140.27    8344.63  108075.27
  Latency        0.95ms   292.08us     5.50ms
  Latency Distribution
     50%     0.89ms
     75%     1.17ms
     90%     1.46ms
     99%     2.12ms
### Exception Endpoint (/exc)
  Reqs/sec    101959.68    8534.82  108999.30
  Latency        0.96ms   311.63us     4.38ms
  Latency Distribution
     50%     0.88ms
     75%     1.18ms
     90%     1.51ms
     99%     2.39ms
### HTML Response (/html)
  Reqs/sec    112614.52    7336.94  117462.41
  Latency        0.88ms   272.23us     4.50ms
  Latency Distribution
     50%   827.00us
     75%     1.05ms
     90%     1.30ms
     99%     1.91ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     33304.68    7954.03   44030.33
  Latency        3.05ms     1.59ms    20.76ms
  Latency Distribution
     50%     2.77ms
     75%     3.48ms
     90%     4.36ms
     99%    10.44ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     62714.95   24040.98   81608.44
  Latency        1.40ms   651.99us     6.37ms
  Latency Distribution
     50%     1.20ms
     75%     1.67ms
     90%     2.38ms
     99%     4.33ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17232.36    1646.59   18663.47
  Latency        5.78ms     1.36ms    13.90ms
  Latency Distribution
     50%     5.80ms
     75%     6.83ms
     90%     7.76ms
     99%     9.79ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15144.36     921.20   16393.02
  Latency        6.57ms     1.89ms    16.04ms
  Latency Distribution
     50%     6.14ms
     75%     7.81ms
     90%     9.79ms
     99%    12.65ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     79498.24    4973.85   86154.01
  Latency        1.26ms   442.65us     4.93ms
  Latency Distribution
     50%     1.16ms
     75%     1.55ms
     90%     2.04ms
     99%     3.11ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    101321.94    7740.21  109658.70
  Latency        0.96ms   304.58us     4.50ms
  Latency Distribution
     50%     0.88ms
     75%     1.18ms
     90%     1.51ms
     99%     2.35ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     93389.31    9451.49  102942.08
  Latency        1.03ms   345.42us     4.30ms
  Latency Distribution
     50%     0.94ms
     75%     1.26ms
     90%     1.66ms
     99%     2.70ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13909.32    1059.50   15691.00
  Latency        7.16ms     1.70ms    17.95ms
  Latency Distribution
     50%     7.48ms
     75%     8.44ms
     90%     9.20ms
     99%    11.48ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec      9808.68    1366.68   12230.15
  Latency       10.15ms     3.57ms    36.67ms
  Latency Distribution
     50%     9.39ms
     75%    12.42ms
     90%    15.21ms
     99%    22.64ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     14312.24    2559.16   20582.14
  Latency        7.04ms     2.52ms    30.21ms
  Latency Distribution
     50%     6.54ms
     75%     8.20ms
     90%    10.45ms
     99%    15.97ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13255.40    1485.07   14974.74
  Latency        7.53ms     3.03ms    27.01ms
  Latency Distribution
     50%     6.84ms
     75%     9.14ms
     90%    12.15ms
     99%    17.93ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    103695.58   12609.57  116200.12
  Latency        0.94ms   324.15us     6.01ms
  Latency Distribution
     50%     0.87ms
     75%     1.15ms
     90%     1.41ms
     99%     2.29ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     97986.11    8225.93  105699.04
  Latency        1.00ms   301.09us     4.70ms
  Latency Distribution
     50%     0.94ms
     75%     1.23ms
     90%     1.54ms
     99%     2.34ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     64977.47    5207.08   70434.21
  Latency        1.52ms   414.79us     5.58ms
  Latency Distribution
     50%     1.43ms
     75%     1.84ms
     90%     2.28ms
     99%     3.24ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     99400.79    8239.21  106175.33
  Latency        0.99ms   332.43us     5.15ms
  Latency Distribution
     50%     0.93ms
     75%     1.21ms
     90%     1.52ms
     99%     2.37ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     85884.87    3561.96   91884.51
  Latency        1.15ms   422.34us     4.86ms
  Latency Distribution
     50%     1.04ms
     75%     1.42ms
     90%     1.86ms
     99%     3.11ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     92076.13   10384.34  102438.37
  Latency        1.07ms   420.28us     6.90ms
  Latency Distribution
     50%     0.95ms
     75%     1.32ms
     90%     1.78ms
     99%     2.78ms
### CBV Response Types (/cbv-response)
  Reqs/sec    100495.69    6928.19  109045.43
  Latency        0.97ms   287.35us     3.96ms
  Latency Distribution
     50%     0.90ms
     75%     1.20ms
     90%     1.51ms
     99%     2.24ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16597.64    1532.41   22473.22
  Latency        6.05ms     1.42ms    19.84ms
  Latency Distribution
     50%     5.97ms
     75%     7.12ms
     90%     8.13ms
     99%    10.43ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     98916.21    9212.16  113888.27
  Latency        1.02ms   298.48us     4.01ms
  Latency Distribution
     50%     0.97ms
     75%     1.25ms
     90%     1.55ms
     99%     2.35ms
### File Upload (POST /upload)
  Reqs/sec     85624.16    5065.61   92651.87
  Latency        1.14ms   385.55us     6.53ms
  Latency Distribution
     50%     1.06ms
     75%     1.41ms
     90%     1.75ms
     99%     2.70ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     85009.27    6352.45   88485.83
  Latency        1.15ms   373.50us     5.16ms
  Latency Distribution
     50%     1.09ms
     75%     1.40ms
     90%     1.80ms
     99%     2.71ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9275.77     890.46   10408.53
  Latency       10.74ms     2.98ms    23.91ms
  Latency Distribution
     50%    10.23ms
     75%    12.71ms
     90%    15.39ms
     99%    20.00ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     85443.45   10761.06   99885.51
  Latency        1.14ms   458.76us     6.43ms
  Latency Distribution
     50%     1.03ms
     75%     1.39ms
     90%     1.82ms
     99%     3.44ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     92692.74    8279.21  103157.75
  Latency        1.07ms   368.72us     6.05ms
  Latency Distribution
     50%     0.99ms
     75%     1.31ms
     90%     1.66ms
     99%     2.50ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     78753.50    6468.68   88060.26
  Latency        1.24ms   453.08us     5.43ms
  Latency Distribution
     50%     1.13ms
     75%     1.51ms
     90%     1.96ms
     99%     3.27ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     87392.81    6475.63   93427.45
  Latency        1.13ms   387.02us     5.24ms
  Latency Distribution
     50%     1.04ms
     75%     1.40ms
     90%     1.80ms
     99%     2.78ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    106924.28   13095.79  117730.37
  Latency        0.90ms   342.40us     5.10ms
  Latency Distribution
     50%   827.00us
     75%     1.11ms
     90%     1.39ms
     99%     2.25ms

### Path Parameter - int (/items/12345)
  Reqs/sec     99480.05    7032.73  105513.35
  Latency        0.98ms   388.11us     5.21ms
  Latency Distribution
     50%     0.85ms
     75%     1.20ms
     90%     1.62ms
     99%     2.93ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    103218.96   15776.23  130487.41
  Latency        1.00ms   340.89us     5.94ms
  Latency Distribution
     50%     0.89ms
     75%     1.26ms
     90%     1.64ms
     99%     2.51ms

### Header Parameter (/header)
  Reqs/sec    104207.33    9226.99  111460.77
  Latency        0.94ms   315.55us     5.46ms
  Latency Distribution
     50%     0.88ms
     75%     1.13ms
     90%     1.42ms
     99%     2.23ms

### Cookie Parameter (/cookie)
  Reqs/sec    100908.29    8376.81  108632.92
  Latency        0.97ms   309.99us     5.25ms
  Latency Distribution
     50%     0.90ms
     75%     1.21ms
     90%     1.55ms
     99%     2.30ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     85369.04    6962.67   89419.74
  Latency        1.14ms   373.20us     6.97ms
  Latency Distribution
     50%     1.06ms
     75%     1.44ms
     90%     1.83ms
     99%     2.79ms

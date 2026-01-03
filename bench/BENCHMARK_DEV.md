# Django-Bolt Benchmark
Generated: Sat Jan  3 08:09:00 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    123328.27   10560.22  131780.98
  Latency      805.50us   293.13us     4.86ms
  Latency Distribution
     50%   746.00us
     75%     0.98ms
     90%     1.26ms
     99%     1.93ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec    106057.82   21469.83  145293.93
  Latency        1.00ms   315.50us     4.77ms
  Latency Distribution
     50%     0.92ms
     75%     1.19ms
     90%     1.53ms
     99%     2.46ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     97375.37    7118.31  103976.98
  Latency        1.01ms   309.18us     4.10ms
  Latency Distribution
     50%     0.95ms
     75%     1.20ms
     90%     1.53ms
     99%     2.42ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    117243.63    8700.59  122396.06
  Latency      844.13us   262.75us     3.68ms
  Latency Distribution
     50%   777.00us
     75%     1.04ms
     90%     1.33ms
     99%     2.08ms
### Cookie Endpoint (/cookie)
  Reqs/sec    118743.75    8331.31  128651.89
  Latency      840.32us   270.78us     3.78ms
  Latency Distribution
     50%   784.00us
     75%     1.03ms
     90%     1.32ms
     99%     2.08ms
### Exception Endpoint (/exc)
  Reqs/sec    120338.70   10087.60  132692.60
  Latency      833.29us   286.57us     4.78ms
  Latency Distribution
     50%   766.00us
     75%     1.01ms
     90%     1.27ms
     99%     2.08ms
### HTML Response (/html)
  Reqs/sec    124291.19    9618.52  130621.44
  Latency      786.02us   279.93us     3.99ms
  Latency Distribution
     50%   711.00us
     75%     0.96ms
     90%     1.27ms
     99%     2.08ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     38621.91    6184.20   50840.18
  Latency        2.63ms     0.98ms    12.43ms
  Latency Distribution
     50%     2.45ms
     75%     3.07ms
     90%     3.76ms
     99%     7.18ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     82374.60    5926.21   86753.32
  Latency        1.19ms   394.33us     8.89ms
  Latency Distribution
     50%     1.11ms
     75%     1.42ms
     90%     1.76ms
     99%     2.60ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     18446.36    1425.35   19946.30
  Latency        5.41ms     1.13ms    13.40ms
  Latency Distribution
     50%     5.37ms
     75%     6.14ms
     90%     7.15ms
     99%     9.28ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     16792.13    1259.22   18083.94
  Latency        5.92ms     1.64ms    15.48ms
  Latency Distribution
     50%     5.68ms
     75%     7.25ms
     90%     8.51ms
     99%    11.01ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     84213.58    6238.58   91857.02
  Latency        1.16ms   373.06us     4.63ms
  Latency Distribution
     50%     1.12ms
     75%     1.46ms
     90%     1.86ms
     99%     2.69ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    103785.89    6443.53  111335.92
  Latency        0.95ms   291.31us     3.84ms
  Latency Distribution
     50%     0.89ms
     75%     1.19ms
     90%     1.49ms
     99%     2.19ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec    101731.28    5631.58  107289.76
  Latency        0.96ms   285.78us     4.13ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.51ms
     99%     2.18ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
 0 / 10000 [---------------------------------------------------------------]   0.00% 2999 / 10000 [===============>------------------------------------]  29.99% 14949/s 6120 / 10000 [===============================>--------------------]  61.20% 15267/s 9240 / 10000 [================================================>---]  92.40% 15371/s 10000 / 10000 [===================================================] 100.00% 12472/s 10000 / 10000 [================================================] 100.00% 12471/s 0s
  Reqs/sec     15454.08    1236.78   17821.58
  Latency        6.45ms     2.08ms    16.70ms
  Latency Distribution
     50%     6.00ms
     75%     8.12ms
     90%     9.79ms
     99%    13.01ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12843.14    2283.67   16534.48
  Latency        7.51ms     5.66ms    69.62ms
  Latency Distribution
     50%     6.71ms
     75%     8.86ms
     90%    10.89ms
     99%    16.42ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     17785.40    1406.91   22357.79
  Latency        5.63ms     3.15ms    63.94ms
  Latency Distribution
     50%     5.22ms
     75%     7.30ms
     90%     8.94ms
     99%    12.00ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     15350.55    2269.38   17879.94
  Latency        6.38ms     3.99ms    32.62ms
  Latency Distribution
     50%     5.19ms
     75%     7.38ms
     90%    11.05ms
     99%    23.16ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    132683.78   26921.85  178429.53
  Latency      808.03us   300.53us     4.90ms
  Latency Distribution
     50%   745.00us
     75%     0.98ms
     90%     1.22ms
     99%     2.06ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    114734.07    9531.22  121231.83
  Latency        0.86ms   292.42us     3.84ms
  Latency Distribution
     50%   787.00us
     75%     1.06ms
     90%     1.38ms
     99%     2.24ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     73211.02    3468.61   76369.72
  Latency        1.35ms   381.04us     5.32ms
  Latency Distribution
     50%     1.26ms
     75%     1.63ms
     90%     2.07ms
     99%     2.96ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    109553.81    7736.78  113655.64
  Latency        0.90ms   265.17us     5.07ms
  Latency Distribution
     50%   842.00us
     75%     1.09ms
     90%     1.37ms
     99%     2.08ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    110184.62    7113.90  115513.16
  Latency        0.89ms   254.99us     3.46ms
  Latency Distribution
     50%   827.00us
     75%     1.07ms
     90%     1.36ms
     99%     2.02ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    112405.12    9615.68  119506.47
  Latency        0.88ms   345.71us     5.56ms
  Latency Distribution
     50%   810.00us
     75%     1.06ms
     90%     1.34ms
     99%     2.27ms
### CBV Response Types (/cbv-response)
  Reqs/sec    113240.59    9621.08  122928.67
  Latency        0.87ms   281.20us     4.01ms
  Latency Distribution
     50%   808.00us
     75%     1.06ms
     90%     1.34ms
     99%     2.03ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     18219.02    1602.62   20467.25
  Latency        5.46ms     2.61ms    56.52ms
  Latency Distribution
     50%     5.53ms
     75%     6.85ms
     90%     8.13ms
     99%    11.02ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    106646.73    9652.65  113684.83
  Latency        0.92ms   359.87us     5.92ms
  Latency Distribution
     50%   818.00us
     75%     1.13ms
     90%     1.51ms
     99%     2.43ms
### File Upload (POST /upload)
  Reqs/sec    104594.31   17032.71  136050.23
  Latency        1.00ms   288.55us     4.22ms
  Latency Distribution
     50%     0.94ms
     75%     1.21ms
     90%     1.56ms
     99%     2.27ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     98158.77    6364.14  103627.06
  Latency        1.00ms   302.31us     4.55ms
  Latency Distribution
     50%     0.94ms
     75%     1.24ms
     90%     1.55ms
     99%     2.39ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec     14384.37    3796.55   18236.94
  Latency        6.54ms     4.23ms    67.35ms
  Latency Distribution
     50%     5.69ms
     75%     7.79ms
     90%     8.93ms
     99%    12.37ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    114516.05   10930.52  121465.16
  Latency        0.86ms   301.08us     5.64ms
  Latency Distribution
     50%   796.00us
     75%     1.05ms
     90%     1.34ms
     99%     2.13ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec    109370.48    7510.25  115208.17
  Latency        0.90ms   283.11us     4.56ms
  Latency Distribution
     50%   842.00us
     75%     1.12ms
     90%     1.43ms
     99%     2.11ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec    102803.74    8344.78  107414.04
  Latency        0.96ms   299.78us     5.10ms
  Latency Distribution
     50%     0.88ms
     75%     1.17ms
     90%     1.52ms
     99%     2.24ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    112265.29    6917.48  117427.38
  Latency        0.88ms   252.02us     3.62ms
  Latency Distribution
     50%   817.00us
     75%     1.06ms
     90%     1.33ms
     99%     2.00ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    125902.54   11263.96  133255.27
  Latency      776.08us   272.65us     4.46ms
  Latency Distribution
     50%   730.00us
     75%     0.95ms
     90%     1.17ms
     99%     1.97ms

### Path Parameter - int (/items/12345)
  Reqs/sec    116062.24    8752.75  121548.07
  Latency      844.74us   308.35us     5.48ms
  Latency Distribution
     50%   774.00us
     75%     1.01ms
     90%     1.29ms
     99%     1.99ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    112366.39    7148.11  119011.35
  Latency        0.88ms   275.99us     3.33ms
  Latency Distribution
     50%   812.00us
     75%     1.06ms
     90%     1.41ms
     99%     2.12ms

### Header Parameter (/header)
  Reqs/sec    116872.41    9227.25  125105.13
  Latency      826.33us   261.11us     4.30ms
  Latency Distribution
     50%   771.00us
     75%     1.00ms
     90%     1.24ms
     99%     1.91ms

### Cookie Parameter (/cookie)
  Reqs/sec    118558.80   10581.26  131121.65
  Latency      843.01us   266.06us     3.63ms
  Latency Distribution
     50%   774.00us
     75%     1.03ms
     90%     1.32ms
     99%     2.12ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     85368.70   30231.77  101091.15
  Latency        1.01ms   316.79us     4.28ms
  Latency Distribution
     50%     0.95ms
     75%     1.22ms
     90%     1.52ms
     99%     2.37ms

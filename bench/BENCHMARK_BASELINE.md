# Django-Bolt Benchmark
Generated: Mon 23 Feb 2026 01:40:06 AM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    107276.38    8065.67  112479.05
  Latency        0.92ms   292.76us     4.96ms
  Latency Distribution
     50%   849.00us
     75%     1.12ms
     90%     1.39ms
     99%     2.10ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     84340.10    7757.48   89761.65
  Latency        1.17ms   395.43us     4.63ms
  Latency Distribution
     50%     1.07ms
     75%     1.43ms
     90%     1.83ms
     99%     2.94ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     85329.91    5808.34   88946.17
  Latency        1.16ms   348.27us     5.83ms
  Latency Distribution
     50%     1.08ms
     75%     1.40ms
     90%     1.75ms
     99%     2.52ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     89859.07   20104.79  104403.82
  Latency        1.00ms   288.01us     5.35ms
  Latency Distribution
     50%     0.94ms
     75%     1.25ms
     90%     1.57ms
     99%     2.23ms
### Cookie Endpoint (/cookie)
  Reqs/sec    104322.08    6426.56  108460.24
  Latency        0.94ms   236.64us     4.45ms
  Latency Distribution
     50%     0.89ms
     75%     1.15ms
     90%     1.41ms
     99%     1.94ms
### Exception Endpoint (/exc)
  Reqs/sec     95252.37    6591.35  100779.26
  Latency        1.04ms   335.13us     5.04ms
  Latency Distribution
     50%     0.96ms
     75%     1.29ms
     90%     1.65ms
     99%     2.37ms
### HTML Response (/html)
  Reqs/sec    103749.47    9221.04  110713.42
  Latency        0.95ms   303.72us     4.95ms
  Latency Distribution
     50%     0.89ms
     75%     1.17ms
     90%     1.47ms
     99%     2.23ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     29230.52    7286.95   39977.87
  Latency        3.46ms     1.72ms    26.73ms
  Latency Distribution
     50%     3.12ms
     75%     4.12ms
     90%     5.26ms
     99%    11.17ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     74840.63    5906.54   80626.77
  Latency        1.32ms   440.95us     5.77ms
  Latency Distribution
     50%     1.22ms
     75%     1.65ms
     90%     2.11ms
     99%     3.24ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     16389.70    1288.79   18369.46
  Latency        6.08ms     2.00ms    18.48ms
  Latency Distribution
     50%     6.22ms
     75%     7.56ms
     90%     9.09ms
     99%    11.58ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     14917.93     783.17   15959.47
  Latency        6.68ms     1.34ms    13.29ms
  Latency Distribution
     50%     6.58ms
     75%     7.70ms
     90%     8.76ms
     99%    10.81ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     80265.10    5612.08   84375.40
  Latency        1.22ms   395.19us     6.37ms
  Latency Distribution
     50%     1.16ms
     75%     1.52ms
     90%     1.91ms
     99%     2.80ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     94173.02    6627.50  100915.03
  Latency        1.02ms   343.68us     4.64ms
  Latency Distribution
     50%     0.95ms
     75%     1.29ms
     90%     1.64ms
     99%     2.42ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     90669.92    5349.13   94779.98
  Latency        1.09ms   366.18us     4.54ms
  Latency Distribution
     50%     1.01ms
     75%     1.36ms
     90%     1.76ms
     99%     2.68ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13513.29     827.47   14672.54
  Latency        7.36ms     1.53ms    17.39ms
  Latency Distribution
     50%     7.89ms
     75%     8.85ms
     90%     9.46ms
     99%    10.47ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec      9716.76     942.23   12575.79
  Latency       10.28ms     3.95ms    34.18ms
  Latency Distribution
     50%     9.44ms
     75%    12.49ms
     90%    16.24ms
     99%    23.47ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     15663.21     746.97   17019.47
  Latency        6.34ms     1.23ms    13.32ms
  Latency Distribution
     50%     6.41ms
     75%     7.41ms
     90%     8.28ms
     99%     9.74ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     11794.29     741.39   13187.71
  Latency        8.42ms     3.68ms    28.94ms
  Latency Distribution
     50%     7.62ms
     75%    10.61ms
     90%    14.07ms
     99%    20.48ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    102465.35    9720.51  107753.37
  Latency        0.96ms   347.88us     5.27ms
  Latency Distribution
     50%     0.90ms
     75%     1.18ms
     90%     1.48ms
     99%     2.40ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     97806.25    5723.34  101341.12
  Latency        1.01ms   290.69us     4.03ms
  Latency Distribution
     50%     0.94ms
     75%     1.25ms
     90%     1.60ms
     99%     2.26ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     65929.77    5109.45   72542.90
  Latency        1.51ms   374.32us     5.83ms
  Latency Distribution
     50%     1.43ms
     75%     1.77ms
     90%     2.16ms
     99%     2.96ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     94708.11    6715.57  100345.54
  Latency        1.05ms   387.37us     4.69ms
  Latency Distribution
     50%     0.95ms
     75%     1.32ms
     90%     1.76ms
     99%     2.79ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     95285.05    5787.32  101772.72
  Latency        1.04ms   298.65us     4.87ms
  Latency Distribution
     50%     0.98ms
     75%     1.28ms
     90%     1.59ms
     99%     2.30ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     98203.02    7726.30  103638.43
  Latency        1.01ms   336.92us     5.71ms
  Latency Distribution
     50%     0.94ms
     75%     1.23ms
     90%     1.55ms
     99%     2.31ms
### CBV Response Types (/cbv-response)
  Reqs/sec    101086.48    6498.97  105736.18
  Latency        0.97ms   316.75us     4.84ms
  Latency Distribution
     50%     0.90ms
     75%     1.22ms
     90%     1.55ms
     99%     2.34ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     15901.95    1420.00   17310.92
  Latency        6.19ms     1.59ms    16.60ms
  Latency Distribution
     50%     6.00ms
     75%     7.83ms
     90%     8.77ms
     99%    10.45ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     95725.75    7125.98  103198.12
  Latency        1.04ms   333.51us     5.21ms
  Latency Distribution
     50%     0.97ms
     75%     1.24ms
     90%     1.55ms
     99%     2.38ms
### File Upload (POST /upload)
  Reqs/sec     82752.78    5839.90   90683.06
  Latency        1.21ms   392.97us     5.56ms
  Latency Distribution
     50%     1.14ms
     75%     1.50ms
     90%     1.85ms
     99%     2.78ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     82083.67    5283.31   85823.09
  Latency        1.20ms   361.90us     4.82ms
  Latency Distribution
     50%     1.13ms
     75%     1.47ms
     90%     1.84ms
     99%     2.68ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
 0 / 10000 [-----------------------------------]   0.00% 1769 / 10000 [====>--------------------]  17.69% 8821/s 3639 / 10000 [=========>---------------]  36.39% 9078/s 5553 / 10000 [=============>-----------]  55.53% 9231/s 7451 / 10000 [==================>------]  74.51% 9293/s 9375 / 10000 [=======================>-]  93.75% 9353/s 10000 / 10000 [========================] 100.00% 8311/s 10000 / 10000 [=====================] 100.00% 8311/s 1s
  Reqs/sec      9549.65    1541.79   18561.58
  Latency       10.60ms     2.98ms    25.18ms
  Latency Distribution
     50%    10.23ms
     75%    12.69ms
     90%    15.06ms
     99%    19.10ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     98790.68    8998.03  104943.09
  Latency        0.99ms   323.18us     4.93ms
  Latency Distribution
     50%     0.92ms
     75%     1.21ms
     90%     1.53ms
     99%     2.31ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     92836.84    7986.02   98343.25
  Latency        1.05ms   333.15us     5.72ms
  Latency Distribution
     50%     0.97ms
     75%     1.31ms
     90%     1.67ms
     99%     2.64ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     85571.93    6688.51   90359.33
  Latency        1.15ms   405.96us     4.75ms
  Latency Distribution
     50%     1.06ms
     75%     1.41ms
     90%     1.80ms
     99%     3.03ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     97253.79    7382.83  108403.05
  Latency        1.02ms   281.97us     4.33ms
  Latency Distribution
     50%     0.97ms
     75%     1.26ms
     90%     1.56ms
     99%     2.22ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    108466.06    9045.38  112690.11
  Latency        0.91ms   252.72us     2.91ms
  Latency Distribution
     50%     0.86ms
     75%     1.12ms
     90%     1.40ms
     99%     2.09ms

### Path Parameter - int (/items/12345)
  Reqs/sec    101515.98    7874.20  105877.18
  Latency        0.97ms   319.18us     6.69ms
  Latency Distribution
     50%     0.90ms
     75%     1.22ms
     90%     1.51ms
     99%     2.30ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec     99396.20    7362.87  103489.92
  Latency        0.99ms   340.08us     4.64ms
  Latency Distribution
     50%     0.92ms
     75%     1.22ms
     90%     1.58ms
     99%     2.46ms

### Header Parameter (/header)
  Reqs/sec    102994.99    6891.08  108565.21
  Latency        0.95ms   278.91us     5.39ms
  Latency Distribution
     50%     0.92ms
     75%     1.16ms
     90%     1.42ms
     99%     2.12ms

### Cookie Parameter (/cookie)
  Reqs/sec    101147.16    6734.84  106362.64
  Latency        0.97ms   298.51us     5.29ms
  Latency Distribution
     50%     0.90ms
     75%     1.18ms
     90%     1.50ms
     99%     2.16ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     82625.32    4113.28   87054.09
  Latency        1.19ms   324.59us     5.17ms
  Latency Distribution
     50%     1.14ms
     75%     1.44ms
     90%     1.76ms
     99%     2.41ms

# Django-Bolt Benchmark
Generated: Sat Jan 10 11:33:22 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    114871.13   14070.21  126853.09
  Latency      811.97us   319.10us     5.71ms
  Latency Distribution
     50%   744.00us
     75%     0.99ms
     90%     1.24ms
     99%     2.08ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     95884.05    8169.51  102176.97
  Latency        1.03ms   377.95us     5.77ms
  Latency Distribution
     50%     0.94ms
     75%     1.24ms
     90%     1.60ms
     99%     2.53ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     88245.22   23926.21  104175.13
  Latency        1.01ms   358.01us     6.45ms
  Latency Distribution
     50%     0.93ms
     75%     1.20ms
     90%     1.50ms
     99%     2.39ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    114019.96   10197.11  122244.39
  Latency        0.86ms   361.09us     5.38ms
  Latency Distribution
     50%   777.00us
     75%     1.05ms
     90%     1.33ms
     99%     2.28ms
### Cookie Endpoint (/cookie)
  Reqs/sec    119156.10   12997.09  131077.15
  Latency      834.78us   313.33us     4.84ms
  Latency Distribution
     50%   765.00us
     75%     0.99ms
     90%     1.27ms
     99%     2.13ms
### Exception Endpoint (/exc)
  Reqs/sec    111230.86    8130.06  119531.93
  Latency        0.87ms   331.67us     4.60ms
  Latency Distribution
     50%   781.00us
     75%     1.06ms
     90%     1.44ms
     99%     2.32ms
### HTML Response (/html)
  Reqs/sec    116167.83   11155.98  127497.46
  Latency        0.86ms   299.32us     4.76ms
  Latency Distribution
     50%   792.00us
     75%     1.07ms
     90%     1.34ms
     99%     2.12ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     26786.09   12193.43   40168.28
  Latency        3.73ms     4.83ms    84.61ms
  Latency Distribution
     50%     2.77ms
     75%     3.81ms
     90%     5.43ms
     99%    31.02ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     83483.37    5488.27   88541.53
  Latency        1.17ms   408.36us     4.77ms
  Latency Distribution
     50%     1.05ms
     75%     1.46ms
     90%     1.89ms
     99%     3.01ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17771.29    1265.73   18996.75
  Latency        5.58ms     1.90ms    15.30ms
  Latency Distribution
     50%     5.16ms
     75%     7.06ms
     90%     8.83ms
     99%    11.52ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     16614.61    1288.44   20949.25
  Latency        6.02ms     1.46ms    13.12ms
  Latency Distribution
     50%     5.99ms
     75%     7.12ms
     90%     8.20ms
     99%    10.56ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     92230.44    9944.18  101711.11
  Latency        1.07ms   346.25us     4.75ms
  Latency Distribution
     50%     1.01ms
     75%     1.30ms
     90%     1.64ms
     99%     2.60ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    106091.60    7843.34  115177.44
  Latency        0.93ms   312.62us     4.39ms
  Latency Distribution
     50%   843.00us
     75%     1.13ms
     90%     1.47ms
     99%     2.46ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec    105140.64    8952.29  114210.11
  Latency        0.94ms   308.90us     4.15ms
  Latency Distribution
     50%     0.85ms
     75%     1.16ms
     90%     1.48ms
     99%     2.33ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     15086.67    1393.37   18273.66
  Latency        6.62ms     3.34ms    65.51ms
  Latency Distribution
     50%     6.52ms
     75%     8.18ms
     90%     9.93ms
     99%    13.09ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     13483.93    1779.51   15992.33
  Latency        7.41ms     5.16ms    73.48ms
  Latency Distribution
     50%     7.00ms
     75%     8.64ms
     90%    10.34ms
     99%    14.06ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     17609.55    1313.16   19468.34
  Latency        5.65ms     2.83ms    60.10ms
  Latency Distribution
     50%     5.40ms
     75%     6.53ms
     90%     7.71ms
     99%    10.38ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     15927.54    2157.80   19612.53
  Latency        6.22ms     2.62ms    21.57ms
  Latency Distribution
     50%     5.64ms
     75%     7.68ms
     90%    10.10ms
     99%    15.71ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    121202.42   15532.63  136943.62
  Latency      831.77us   289.20us     4.09ms
  Latency Distribution
     50%   763.00us
     75%     1.01ms
     90%     1.32ms
     99%     2.31ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    112543.30    9143.30  118933.39
  Latency        0.88ms   262.13us     3.49ms
  Latency Distribution
     50%   825.00us
     75%     1.08ms
     90%     1.34ms
     99%     2.07ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     72316.59    4800.36   76082.02
  Latency        1.36ms   421.16us     4.47ms
  Latency Distribution
     50%     1.25ms
     75%     1.63ms
     90%     2.08ms
     99%     3.30ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    105686.13    8036.26  116353.95
  Latency        0.92ms   300.85us     5.31ms
  Latency Distribution
     50%     0.85ms
     75%     1.12ms
     90%     1.41ms
     99%     2.17ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    105168.53    6935.62  109976.25
  Latency        0.93ms   284.39us     4.01ms
  Latency Distribution
     50%     0.85ms
     75%     1.14ms
     90%     1.45ms
     99%     2.21ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    110136.26    8342.33  118338.73
  Latency        0.89ms   305.26us     4.22ms
  Latency Distribution
     50%   819.00us
     75%     1.09ms
     90%     1.42ms
     99%     2.30ms
### CBV Response Types (/cbv-response)
  Reqs/sec    115223.11    8482.77  123843.98
  Latency        0.86ms   315.88us     4.76ms
  Latency Distribution
     50%   770.00us
     75%     1.06ms
     90%     1.38ms
     99%     2.42ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     18032.67    1271.65   19869.90
  Latency        5.51ms     1.72ms    15.72ms
  Latency Distribution
     50%     5.38ms
     75%     6.74ms
     90%     8.09ms
     99%    11.01ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    104039.61   11885.72  114313.04
  Latency        0.92ms   295.04us     5.66ms
  Latency Distribution
     50%     0.86ms
     75%     1.14ms
     90%     1.48ms
     99%     2.23ms
### File Upload (POST /upload)
  Reqs/sec     97296.38    7562.54  104129.84
  Latency        1.00ms   312.28us     4.59ms
  Latency Distribution
     50%     0.94ms
     75%     1.23ms
     90%     1.55ms
     99%     2.42ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     92040.09    6783.81  100252.33
  Latency        1.05ms   325.02us     5.28ms
  Latency Distribution
     50%     0.98ms
     75%     1.29ms
     90%     1.63ms
     99%     2.37ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec     13885.16    4146.70   16380.26
  Latency        6.70ms     4.61ms    76.31ms
  Latency Distribution
     50%     6.42ms
     75%     7.44ms
     90%     8.11ms
     99%    12.79ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    113191.39    7300.22  118449.05
  Latency        0.87ms   299.76us     5.84ms
  Latency Distribution
     50%   794.00us
     75%     1.05ms
     90%     1.32ms
     99%     2.21ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec    107159.27    7800.26  113447.71
  Latency        0.92ms   287.67us     4.47ms
  Latency Distribution
     50%     0.86ms
     75%     1.12ms
     90%     1.43ms
     99%     2.29ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec    102469.11    8038.03  110861.25
  Latency        0.96ms   298.04us     4.21ms
  Latency Distribution
     50%     0.89ms
     75%     1.15ms
     90%     1.44ms
     99%     2.33ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    110111.15   10250.67  121252.05
  Latency        0.89ms   298.48us     4.65ms
  Latency Distribution
     50%   823.00us
     75%     1.08ms
     90%     1.38ms
     99%     2.15ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    135629.44   30077.50  183464.36
  Latency      776.46us   239.70us     3.64ms
  Latency Distribution
     50%   723.00us
     75%     0.94ms
     90%     1.19ms
     99%     1.85ms

### Path Parameter - int (/items/12345)
  Reqs/sec    116736.12   11952.58  124653.31
  Latency      824.70us   229.77us     6.31ms
  Latency Distribution
     50%   773.00us
     75%     1.00ms
     90%     1.26ms
     99%     1.83ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    116304.77   10350.86  126687.53
  Latency        0.85ms   294.71us     5.33ms
  Latency Distribution
     50%   777.00us
     75%     1.05ms
     90%     1.33ms
     99%     2.12ms

### Header Parameter (/header)
  Reqs/sec    125260.15   20648.01  159786.54
  Latency      838.58us   289.81us     5.50ms
  Latency Distribution
     50%   772.00us
     75%     1.00ms
     90%     1.31ms
     99%     1.94ms

### Cookie Parameter (/cookie)
  Reqs/sec    122002.31   10797.98  134940.68
  Latency      820.71us   263.89us     4.23ms
  Latency Distribution
     50%   759.00us
     75%     0.99ms
     90%     1.27ms
     99%     1.96ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     94771.22    9314.77  103008.40
  Latency        1.04ms   376.94us     6.02ms
  Latency Distribution
     50%     0.98ms
     75%     1.26ms
     90%     1.55ms
     99%     2.42ms

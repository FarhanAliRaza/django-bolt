# Django-Bolt Benchmark
Generated: Sun 15 Feb 2026 12:13:06 AM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    108107.95    7653.06  114142.38
  Latency        0.91ms   281.41us     4.63ms
  Latency Distribution
     50%     0.85ms
     75%     1.13ms
     90%     1.44ms
     99%     2.10ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     86557.87    5717.60   92067.73
  Latency        1.14ms   356.00us     4.68ms
  Latency Distribution
     50%     1.04ms
     75%     1.37ms
     90%     1.79ms
     99%     2.60ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     87425.85    5774.89   91490.73
  Latency        1.12ms   303.76us     6.15ms
  Latency Distribution
     50%     1.06ms
     75%     1.35ms
     90%     1.67ms
     99%     2.38ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     99988.66    5875.19  103745.67
  Latency        0.98ms   334.79us     4.91ms
  Latency Distribution
     50%     0.91ms
     75%     1.23ms
     90%     1.58ms
     99%     2.31ms
### Cookie Endpoint (/cookie)
  Reqs/sec    102790.14    6616.89  107485.12
  Latency        0.96ms   316.54us     4.84ms
  Latency Distribution
     50%     0.89ms
     75%     1.15ms
     90%     1.44ms
     99%     2.39ms
### Exception Endpoint (/exc)
  Reqs/sec     98791.50    6975.80  104648.39
  Latency        1.00ms   296.28us     4.71ms
  Latency Distribution
     50%     0.94ms
     75%     1.21ms
     90%     1.49ms
     99%     2.14ms
### HTML Response (/html)
  Reqs/sec    103219.42    7677.80  107546.59
  Latency        0.95ms   346.66us     4.62ms
  Latency Distribution
     50%   842.00us
     75%     1.21ms
     90%     1.64ms
     99%     2.48ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     33982.91    7623.02   38051.55
  Latency        2.93ms     1.47ms    18.44ms
  Latency Distribution
     50%     2.70ms
     75%     3.48ms
     90%     4.31ms
     99%     8.22ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     80936.53    6165.33   85763.39
  Latency        1.22ms   350.94us     5.40ms
  Latency Distribution
     50%     1.15ms
     75%     1.50ms
     90%     1.88ms
     99%     2.72ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17418.65    1390.34   19239.89
  Latency        5.72ms     1.18ms    13.31ms
  Latency Distribution
     50%     5.75ms
     75%     6.68ms
     90%     7.44ms
     99%     9.46ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15263.63     757.32   15901.00
  Latency        6.51ms     1.48ms    13.22ms
  Latency Distribution
     50%     6.53ms
     75%     7.81ms
     90%     8.81ms
     99%    10.38ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     85726.55    5558.17   90033.94
  Latency        1.14ms   319.39us     4.60ms
  Latency Distribution
     50%     1.09ms
     75%     1.37ms
     90%     1.75ms
     99%     2.49ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    101498.43    7118.25  105616.15
  Latency        0.97ms   299.26us     4.90ms
  Latency Distribution
     50%     0.91ms
     75%     1.18ms
     90%     1.46ms
     99%     2.24ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     94466.52    5358.24   99565.52
  Latency        1.04ms   306.09us     4.76ms
  Latency Distribution
     50%     0.98ms
     75%     1.28ms
     90%     1.59ms
     99%     2.36ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13776.17     888.61   15357.89
  Latency        7.23ms     1.78ms    18.45ms
  Latency Distribution
     50%     6.80ms
     75%     9.18ms
     90%    10.33ms
     99%    11.59ms
### Users Full10 (Sync) (/users/sync-full10)
 0 / 10000 [-------------------------------------------------------------]   0.00% 2368 / 10000 [===========>--------------------------------------]  23.68% 11808/s 4799 / 10000 [=======================>--------------------------]  47.99% 11976/s 7223 / 10000 [====================================>-------------]  72.23% 12021/s 9652 / 10000 [================================================>-]  96.52% 12045/s 10000 / 10000 [==================================================] 100.00% 9975/s 10000 / 10000 [===============================================] 100.00% 9974/s 1s
  Reqs/sec     12237.67    1328.55   19818.42
  Latency        8.23ms     0.91ms    17.12ms
  Latency Distribution
     50%     8.20ms
     75%     8.96ms
     90%     9.65ms
     99%    10.92ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     15846.30     710.43   16373.82
  Latency        6.25ms     2.41ms    15.98ms
  Latency Distribution
     50%     5.49ms
     75%     8.09ms
     90%    10.89ms
     99%    12.65ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13335.31    1122.43   16202.26
  Latency        7.47ms     3.10ms    29.40ms
  Latency Distribution
     50%     6.72ms
     75%     9.06ms
     90%    12.16ms
     99%    18.49ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    108669.05    8418.94  114642.54
  Latency        0.91ms   300.95us     5.41ms
  Latency Distribution
     50%     0.85ms
     75%     1.11ms
     90%     1.40ms
     99%     2.09ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    102059.55    7527.11  106509.35
  Latency        0.96ms   303.65us     4.63ms
  Latency Distribution
     50%     0.90ms
     75%     1.18ms
     90%     1.48ms
     99%     2.21ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     66694.94    4347.65   69874.13
  Latency        1.47ms   442.84us     4.83ms
  Latency Distribution
     50%     1.35ms
     75%     1.78ms
     90%     2.33ms
     99%     3.37ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    100744.13    6577.55  105028.35
  Latency        0.98ms   291.29us     4.42ms
  Latency Distribution
     50%     0.92ms
     75%     1.17ms
     90%     1.46ms
     99%     2.19ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     97425.16    6582.87  103999.14
  Latency        1.02ms   307.02us     5.16ms
  Latency Distribution
     50%     0.97ms
     75%     1.23ms
     90%     1.52ms
     99%     2.25ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     97689.01    9511.37  104631.35
  Latency        1.01ms   339.64us     6.69ms
  Latency Distribution
     50%     0.92ms
     75%     1.25ms
     90%     1.63ms
     99%     2.40ms
### CBV Response Types (/cbv-response)
  Reqs/sec    102689.28    8929.68  109485.30
  Latency        0.96ms   314.71us     4.35ms
  Latency Distribution
     50%     0.88ms
     75%     1.21ms
     90%     1.55ms
     99%     2.29ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16286.61    1040.36   17224.44
  Latency        6.10ms     1.55ms    15.20ms
  Latency Distribution
     50%     5.85ms
     75%     7.55ms
     90%     8.79ms
     99%    10.25ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    107708.95   26918.52  160855.68
  Latency        1.01ms   294.41us     5.04ms
  Latency Distribution
     50%     0.94ms
     75%     1.24ms
     90%     1.54ms
     99%     2.23ms
### File Upload (POST /upload)
  Reqs/sec     87803.99    6021.99   92873.85
  Latency        1.13ms   340.40us     5.02ms
  Latency Distribution
     50%     1.08ms
     75%     1.40ms
     90%     1.73ms
     99%     2.49ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     85703.81    6209.78   90674.95
  Latency        1.15ms   365.41us     5.43ms
  Latency Distribution
     50%     1.07ms
     75%     1.40ms
     90%     1.75ms
     99%     2.74ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
 0 / 10000 [-------------------------------------------------------------]   0.00% 1850 / 10000 [=========>-----------------------------------------]  18.50% 9226/s 3804 / 10000 [===================>-------------------------------]  38.04% 9487/s 5780 / 10000 [=============================>---------------------]  57.80% 9615/s 7742 / 10000 [=======================================>-----------]  77.42% 9662/s 9707 / 10000 [=================================================>-]  97.07% 9692/s 10000 / 10000 [==================================================] 100.00% 8316/s 10000 / 10000 [===============================================] 100.00% 8315/s 1s
  Reqs/sec      9810.15    1138.27   14963.09
  Latency       10.24ms     3.06ms    25.27ms
  Latency Distribution
     50%     9.38ms
     75%    11.24ms
     90%    16.20ms
     99%    20.91ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    102266.00    7324.65  106384.89
  Latency        0.96ms   323.47us     5.26ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.49ms
     99%     2.26ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     90778.15   14919.89  100661.46
  Latency        1.07ms   749.90us    12.52ms
  Latency Distribution
     50%     0.96ms
     75%     1.25ms
     90%     1.54ms
     99%     2.39ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     88118.78    7994.17   94400.65
  Latency        1.12ms   373.53us     5.80ms
  Latency Distribution
     50%     1.04ms
     75%     1.35ms
     90%     1.65ms
     99%     2.48ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     95318.13    6783.10  100939.89
  Latency        1.02ms   300.12us     5.56ms
  Latency Distribution
     50%     0.96ms
     75%     1.25ms
     90%     1.54ms
     99%     2.20ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    113291.18    9916.60  119120.77
  Latency        0.87ms   334.84us     5.53ms
  Latency Distribution
     50%   806.00us
     75%     1.04ms
     90%     1.28ms
     99%     2.18ms

### Path Parameter - int (/items/12345)
  Reqs/sec    103844.12    9489.33  109973.06
  Latency        0.95ms   279.31us     4.33ms
  Latency Distribution
     50%     0.89ms
     75%     1.18ms
     90%     1.48ms
     99%     2.18ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    103740.07    6891.37  108909.34
  Latency        0.95ms   281.93us     4.18ms
  Latency Distribution
     50%     0.91ms
     75%     1.16ms
     90%     1.42ms
     99%     2.10ms

### Header Parameter (/header)
  Reqs/sec    103213.80    7894.27  107962.76
  Latency        0.96ms   311.23us     5.65ms
  Latency Distribution
     50%     0.89ms
     75%     1.18ms
     90%     1.48ms
     99%     2.23ms

### Cookie Parameter (/cookie)
  Reqs/sec    104210.33    5580.35  107774.16
  Latency        0.94ms   263.01us     3.79ms
  Latency Distribution
     50%     0.89ms
     75%     1.16ms
     90%     1.41ms
     99%     2.02ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     85779.24    5489.98   90515.95
  Latency        1.15ms   331.13us     6.63ms
  Latency Distribution
     50%     1.08ms
     75%     1.42ms
     90%     1.78ms
     99%     2.47ms

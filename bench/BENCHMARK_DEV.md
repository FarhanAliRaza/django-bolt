# Django-Bolt Benchmark
Generated: Sun 01 Feb 2026 01:19:06 AM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    110057.11    7041.39  118264.76
  Latency        0.90ms   314.77us     6.42ms
  Latency Distribution
     50%   823.00us
     75%     1.10ms
     90%     1.42ms
     99%     2.30ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     85514.60    6994.03   90789.40
  Latency        1.15ms   388.38us     5.79ms
  Latency Distribution
     50%     1.07ms
     75%     1.38ms
     90%     1.73ms
     99%     2.67ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     74679.38   17078.82   86272.10
  Latency        1.22ms   453.18us     8.44ms
  Latency Distribution
     50%     1.14ms
     75%     1.46ms
     90%     1.92ms
     99%     3.16ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    103966.76    6680.44  109905.98
  Latency        0.95ms   350.03us     5.27ms
  Latency Distribution
     50%     0.87ms
     75%     1.15ms
     90%     1.48ms
     99%     2.39ms
### Cookie Endpoint (/cookie)
  Reqs/sec    102681.21    7360.55  109573.96
  Latency        0.95ms   289.62us     4.03ms
  Latency Distribution
     50%     0.89ms
     75%     1.20ms
     90%     1.52ms
     99%     2.23ms
### Exception Endpoint (/exc)
  Reqs/sec    101450.91    9093.68  108861.39
  Latency        0.97ms   305.40us     5.33ms
  Latency Distribution
     50%     0.92ms
     75%     1.18ms
     90%     1.49ms
     99%     2.12ms
### HTML Response (/html)
  Reqs/sec    106356.08   10006.51  113717.33
  Latency        0.93ms   290.11us     5.20ms
  Latency Distribution
     50%     0.86ms
     75%     1.13ms
     90%     1.46ms
     99%     2.16ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     33132.14    7485.26   38109.31
  Latency        3.03ms     1.72ms    21.38ms
  Latency Distribution
     50%     2.61ms
     75%     3.77ms
     90%     4.83ms
     99%    10.78ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     76628.03    5800.28   83294.05
  Latency        1.26ms   390.19us     6.44ms
  Latency Distribution
     50%     1.19ms
     75%     1.56ms
     90%     1.94ms
     99%     2.93ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     16767.30    1495.05   18152.60
  Latency        5.94ms     1.51ms    14.99ms
  Latency Distribution
     50%     6.20ms
     75%     7.19ms
     90%     7.97ms
     99%     9.99ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15392.23     840.25   17824.11
  Latency        6.48ms     2.04ms    16.16ms
  Latency Distribution
     50%     6.34ms
     75%     8.21ms
     90%     9.81ms
     99%    11.88ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     85683.72    7237.77   93895.93
  Latency        1.14ms   351.22us     5.46ms
  Latency Distribution
     50%     1.08ms
     75%     1.41ms
     90%     1.77ms
     99%     2.63ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     91791.71   10921.18  105833.63
  Latency        1.02ms   369.92us     5.02ms
  Latency Distribution
     50%     0.95ms
     75%     1.26ms
     90%     1.60ms
     99%     2.63ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     89615.05   19290.08  101602.71
  Latency        1.00ms   299.81us     4.27ms
  Latency Distribution
     50%     0.94ms
     75%     1.24ms
     90%     1.57ms
     99%     2.30ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13958.44     864.67   15106.77
  Latency        7.11ms     2.51ms    19.20ms
  Latency Distribution
     50%     6.57ms
     75%     9.41ms
     90%    11.48ms
     99%    13.68ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12306.33    1083.61   13837.58
  Latency        8.00ms     2.08ms    19.78ms
  Latency Distribution
     50%     7.88ms
     75%     9.40ms
     90%    11.41ms
     99%    14.03ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     16195.78     780.57   16986.98
  Latency        6.14ms     1.95ms    16.55ms
  Latency Distribution
     50%     5.82ms
     75%     7.74ms
     90%     9.44ms
     99%    11.52ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13378.76    1279.61   14774.23
  Latency        7.45ms     3.08ms    27.23ms
  Latency Distribution
     50%     6.79ms
     75%     9.33ms
     90%    12.17ms
     99%    17.41ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    104475.88    8954.51  112705.82
  Latency        0.94ms   326.28us     4.81ms
  Latency Distribution
     50%     0.88ms
     75%     1.15ms
     90%     1.46ms
     99%     2.34ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     94772.67   10402.59  109579.34
  Latency        1.02ms   382.72us     5.77ms
  Latency Distribution
     50%     0.95ms
     75%     1.26ms
     90%     1.60ms
     99%     2.45ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     65902.52    4607.84   69076.43
  Latency        1.50ms   429.99us     7.28ms
  Latency Distribution
     50%     1.43ms
     75%     1.80ms
     90%     2.25ms
     99%     3.25ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     94124.50   12056.34  102309.91
  Latency        1.01ms   340.58us     5.30ms
  Latency Distribution
     50%     0.94ms
     75%     1.25ms
     90%     1.58ms
     99%     2.47ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     89813.75    8383.77   96287.52
  Latency        1.09ms   387.63us     6.18ms
  Latency Distribution
     50%     1.01ms
     75%     1.35ms
     90%     1.71ms
     99%     2.87ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     99622.08    8349.84  107053.02
  Latency        0.98ms   331.64us     4.78ms
  Latency Distribution
     50%     0.91ms
     75%     1.21ms
     90%     1.52ms
     99%     2.41ms
### CBV Response Types (/cbv-response)
  Reqs/sec    104374.21    9764.50  111770.12
  Latency        0.94ms   296.20us     4.70ms
  Latency Distribution
     50%     0.88ms
     75%     1.17ms
     90%     1.44ms
     99%     2.24ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16655.26    1517.49   22348.12
  Latency        6.03ms     1.54ms    15.38ms
  Latency Distribution
     50%     6.00ms
     75%     7.28ms
     90%     8.34ms
     99%    10.73ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     94572.38    8186.23  102655.80
  Latency        1.02ms   337.05us     4.63ms
  Latency Distribution
     50%     0.95ms
     75%     1.25ms
     90%     1.57ms
     99%     2.52ms
### File Upload (POST /upload)
  Reqs/sec     87229.45    5554.65   92640.56
  Latency        1.12ms   320.86us     4.35ms
  Latency Distribution
     50%     1.06ms
     75%     1.36ms
     90%     1.69ms
     99%     2.51ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     83643.44    5055.09   88360.12
  Latency        1.18ms   411.29us     4.87ms
  Latency Distribution
     50%     1.08ms
     75%     1.49ms
     90%     1.91ms
     99%     3.04ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9460.67    1017.13   13332.05
  Latency       10.60ms     2.93ms    25.47ms
  Latency Distribution
     50%     9.73ms
     75%    13.41ms
     90%    15.31ms
     99%    18.49ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    103456.88    8640.42  107825.80
  Latency        0.95ms   285.93us     4.16ms
  Latency Distribution
     50%     0.88ms
     75%     1.17ms
     90%     1.50ms
     99%     2.21ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     96952.39    6639.71  103301.59
  Latency        1.01ms   317.00us     4.36ms
  Latency Distribution
     50%     0.92ms
     75%     1.24ms
     90%     1.60ms
     99%     2.37ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     88528.35    5106.99   95483.18
  Latency        1.10ms   366.17us     5.25ms
  Latency Distribution
     50%     1.01ms
     75%     1.34ms
     90%     1.72ms
     99%     2.75ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    104773.51   19022.30  140708.29
  Latency        1.01ms   340.83us     4.50ms
  Latency Distribution
     50%     0.92ms
     75%     1.25ms
     90%     1.60ms
     99%     2.52ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    107850.78   10364.73  117816.64
  Latency        0.89ms   322.44us     5.22ms
  Latency Distribution
     50%   832.00us
     75%     1.08ms
     90%     1.36ms
     99%     2.23ms

### Path Parameter - int (/items/12345)
  Reqs/sec     99671.42    6925.86  107943.69
  Latency        0.99ms   315.44us     4.65ms
  Latency Distribution
     50%     0.91ms
     75%     1.22ms
     90%     1.52ms
     99%     2.38ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    102595.31    7485.79  108693.87
  Latency        0.96ms   277.82us     3.76ms
  Latency Distribution
     50%     0.92ms
     75%     1.19ms
     90%     1.46ms
     99%     2.24ms

### Header Parameter (/header)
  Reqs/sec    101991.49    8266.91  109661.09
  Latency        0.96ms   305.77us     6.05ms
  Latency Distribution
     50%     0.91ms
     75%     1.19ms
     90%     1.51ms
     99%     2.28ms

### Cookie Parameter (/cookie)
  Reqs/sec    105879.20    8806.09  114570.18
  Latency        0.93ms   262.83us     5.14ms
  Latency Distribution
     50%     0.87ms
     75%     1.14ms
     90%     1.42ms
     99%     2.00ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     80616.55    7464.14   87433.79
  Latency        1.23ms   492.00us     7.10ms
  Latency Distribution
     50%     1.14ms
     75%     1.54ms
     90%     1.98ms
     99%     3.17ms

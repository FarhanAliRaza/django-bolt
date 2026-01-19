# Django-Bolt Benchmark
Generated: Sat Jan 10 11:44:50 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    122850.90    8391.28  130313.94
  Latency      796.82us   293.50us     5.42ms
  Latency Distribution
     50%   725.00us
     75%     0.98ms
     90%     1.25ms
     99%     2.01ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     99504.33    7828.70  104871.86
  Latency        0.99ms   301.82us     4.57ms
  Latency Distribution
     50%     0.93ms
     75%     1.21ms
     90%     1.50ms
     99%     2.38ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec    100114.64    8788.39  104353.76
  Latency        0.97ms   283.07us     5.74ms
  Latency Distribution
     50%     0.91ms
     75%     1.17ms
     90%     1.44ms
     99%     2.21ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    114547.79    7854.02  120679.47
  Latency        0.86ms   285.38us     5.53ms
  Latency Distribution
     50%   791.00us
     75%     1.08ms
     90%     1.37ms
     99%     2.01ms
### Cookie Endpoint (/cookie)
  Reqs/sec    117836.13    9933.53  125026.18
  Latency      823.66us   248.14us     3.88ms
  Latency Distribution
     50%   762.00us
     75%     1.02ms
     90%     1.33ms
     99%     1.99ms
### Exception Endpoint (/exc)
  Reqs/sec    117574.01    8958.78  123699.21
  Latency      836.55us   237.06us     3.79ms
  Latency Distribution
     50%   776.00us
     75%     1.03ms
     90%     1.29ms
     99%     1.93ms
### HTML Response (/html)
  Reqs/sec    124433.48   11365.04  133643.08
  Latency      782.32us   237.12us     4.05ms
  Latency Distribution
     50%   729.00us
     75%     0.96ms
     90%     1.21ms
     99%     1.78ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     35657.13    8154.79   43003.08
  Latency        2.80ms     1.50ms    19.84ms
  Latency Distribution
     50%     2.49ms
     75%     3.22ms
     90%     4.17ms
     99%     8.15ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     86986.79    6680.12   91857.11
  Latency        1.13ms   317.51us     5.13ms
  Latency Distribution
     50%     1.07ms
     75%     1.35ms
     90%     1.68ms
     99%     2.42ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     18421.83    1327.38   19345.64
  Latency        5.39ms     1.05ms    13.70ms
  Latency Distribution
     50%     5.26ms
     75%     6.31ms
     90%     7.04ms
     99%     8.54ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     16918.49    1184.87   18245.34
  Latency        5.87ms     1.67ms    13.84ms
  Latency Distribution
     50%     5.72ms
     75%     7.24ms
     90%     8.54ms
     99%    10.95ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     85943.37    8124.50   92152.27
  Latency        1.12ms   340.35us     5.33ms
  Latency Distribution
     50%     1.04ms
     75%     1.41ms
     90%     1.78ms
     99%     2.55ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    110561.35    9292.87  120397.52
  Latency        0.87ms   262.63us     4.02ms
  Latency Distribution
     50%   795.00us
     75%     1.07ms
     90%     1.38ms
     99%     2.01ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec    102802.66    8525.13  114440.14
  Latency        0.94ms   296.02us     4.38ms
  Latency Distribution
     50%     0.87ms
     75%     1.17ms
     90%     1.55ms
     99%     2.33ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     15138.23    1967.37   16849.63
  Latency        6.45ms     2.62ms    54.85ms
  Latency Distribution
     50%     6.30ms
     75%     7.88ms
     90%     9.31ms
     99%    12.06ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     13711.74    1706.08   17394.37
  Latency        7.28ms     4.75ms    65.12ms
  Latency Distribution
     50%     7.01ms
     75%     8.41ms
     90%    10.14ms
     99%    14.08ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     17767.52    1342.82   21222.57
  Latency        5.62ms     3.20ms    59.96ms
  Latency Distribution
     50%     5.23ms
     75%     6.80ms
     90%     8.37ms
     99%    11.65ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     15803.53    1932.46   18695.54
  Latency        6.28ms     2.75ms    27.87ms
  Latency Distribution
     50%     5.62ms
     75%     7.78ms
     90%    10.43ms
     99%    16.04ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    122829.14    9329.61  129201.43
  Latency      800.00us   253.36us     4.67ms
  Latency Distribution
     50%   744.00us
     75%     0.97ms
     90%     1.24ms
     99%     1.82ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    118894.38    8738.43  124644.26
  Latency      833.04us   253.55us     3.92ms
  Latency Distribution
     50%   776.00us
     75%     1.01ms
     90%     1.30ms
     99%     2.02ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     74455.83    6170.93   77627.27
  Latency        1.33ms   438.08us     6.85ms
  Latency Distribution
     50%     1.25ms
     75%     1.54ms
     90%     1.95ms
     99%     2.90ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    112502.31    8881.01  120506.29
  Latency        0.86ms   286.53us     4.77ms
  Latency Distribution
     50%   793.00us
     75%     1.06ms
     90%     1.32ms
     99%     2.00ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    111044.26    6120.12  114885.69
  Latency        0.89ms   269.95us     4.31ms
  Latency Distribution
     50%   826.00us
     75%     1.09ms
     90%     1.38ms
     99%     2.15ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    114310.80    6604.37  119432.82
  Latency        0.86ms   245.42us     2.88ms
  Latency Distribution
     50%   814.00us
     75%     1.07ms
     90%     1.36ms
     99%     2.04ms
### CBV Response Types (/cbv-response)
  Reqs/sec    114703.88    7880.74  120839.78
  Latency      839.34us   308.99us     5.35ms
  Latency Distribution
     50%   774.00us
     75%     1.03ms
     90%     1.29ms
     99%     2.10ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     17404.04    2098.57   19776.72
  Latency        5.72ms     3.66ms    68.85ms
  Latency Distribution
     50%     5.04ms
     75%     7.08ms
     90%     8.94ms
     99%    13.47ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    110132.73    8924.72  116587.36
  Latency        0.89ms   285.10us     5.02ms
  Latency Distribution
     50%   836.00us
     75%     1.09ms
     90%     1.39ms
     99%     2.19ms
### File Upload (POST /upload)
  Reqs/sec    100460.50   13728.40  124368.31
  Latency        1.02ms   287.10us     4.09ms
  Latency Distribution
     50%     0.96ms
     75%     1.26ms
     90%     1.59ms
     99%     2.23ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     96647.75    6778.73  102392.99
  Latency        1.02ms   355.52us     6.00ms
  Latency Distribution
     50%     0.95ms
     75%     1.25ms
     90%     1.56ms
     99%     2.53ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec     14156.90    4059.46   17095.90
  Latency        6.69ms     5.34ms    80.26ms
  Latency Distribution
     50%     6.25ms
     75%     6.88ms
     90%     8.45ms
     99%    12.71ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    117571.02    8015.22  125373.77
  Latency      838.95us   289.08us     4.86ms
  Latency Distribution
     50%   763.00us
     75%     1.04ms
     90%     1.33ms
     99%     2.14ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec    113452.57    7011.21  118513.59
  Latency        0.87ms   255.55us     3.47ms
  Latency Distribution
     50%   822.00us
     75%     1.06ms
     90%     1.34ms
     99%     2.10ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec    102046.86    8831.67  107451.90
  Latency        0.96ms   298.50us     6.74ms
  Latency Distribution
     50%     0.88ms
     75%     1.15ms
     90%     1.47ms
     99%     2.25ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    111088.80    8134.89  116479.66
  Latency        0.88ms   315.98us     6.00ms
  Latency Distribution
     50%   791.00us
     75%     1.08ms
     90%     1.43ms
     99%     2.28ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    128936.27   11737.38  136769.49
  Latency      763.10us   266.40us     3.95ms
  Latency Distribution
     50%   699.00us
     75%     0.92ms
     90%     1.19ms
     99%     1.93ms

### Path Parameter - int (/items/12345)
  Reqs/sec    121115.05   10134.06  134313.14
  Latency      831.09us   300.39us     5.04ms
  Latency Distribution
     50%   771.00us
     75%     1.00ms
     90%     1.27ms
     99%     2.06ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    118131.74    8941.88  127334.67
  Latency      841.52us   277.51us     4.37ms
  Latency Distribution
     50%   766.00us
     75%     1.06ms
     90%     1.35ms
     99%     2.05ms

### Header Parameter (/header)
  Reqs/sec    119902.50    9140.37  125583.55
  Latency      817.82us   246.73us     3.66ms
  Latency Distribution
     50%   752.00us
     75%     1.01ms
     90%     1.27ms
     99%     2.05ms

### Cookie Parameter (/cookie)
  Reqs/sec    116527.59   11523.68  123108.83
  Latency      817.04us   233.38us     4.78ms
  Latency Distribution
     50%   766.00us
     75%     0.99ms
     90%     1.25ms
     99%     1.86ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     97751.62    6893.78  101897.03
  Latency        1.00ms   296.88us     6.31ms
  Latency Distribution
     50%     0.94ms
     75%     1.22ms
     90%     1.54ms
     99%     2.26ms

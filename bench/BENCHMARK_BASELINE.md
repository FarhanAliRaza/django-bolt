# Django-Bolt Benchmark
Generated: Wed 18 Feb 2026 07:03:12 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    107277.05   10635.92  116474.48
  Latency        0.92ms   292.85us     4.62ms
  Latency Distribution
     50%   841.00us
     75%     1.17ms
     90%     1.49ms
     99%     2.19ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     86532.70    7780.90   91897.48
  Latency        1.14ms   351.69us     4.88ms
  Latency Distribution
     50%     1.07ms
     75%     1.40ms
     90%     1.74ms
     99%     2.67ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     83122.34    6277.40   88532.29
  Latency        1.19ms   369.02us     4.37ms
  Latency Distribution
     50%     1.11ms
     75%     1.46ms
     90%     1.83ms
     99%     2.83ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    102353.25    7220.11  106955.72
  Latency        0.96ms   285.45us     4.98ms
  Latency Distribution
     50%     0.89ms
     75%     1.18ms
     90%     1.48ms
     99%     2.13ms
### Cookie Endpoint (/cookie)
  Reqs/sec    100877.37    6017.03  105355.28
  Latency        0.97ms   320.15us     4.97ms
  Latency Distribution
     50%     0.90ms
     75%     1.23ms
     90%     1.56ms
     99%     2.31ms
### Exception Endpoint (/exc)
  Reqs/sec     94667.03    5739.18   98638.63
  Latency        1.04ms   331.03us     4.61ms
  Latency Distribution
     50%     0.98ms
     75%     1.29ms
     90%     1.66ms
     99%     2.55ms
### HTML Response (/html)
  Reqs/sec    103278.78    6368.29  108982.52
  Latency        0.95ms   346.11us     4.68ms
  Latency Distribution
     50%     0.87ms
     75%     1.17ms
     90%     1.53ms
     99%     2.42ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     32062.05    7161.19   37100.13
  Latency        3.10ms     1.63ms    24.31ms
  Latency Distribution
     50%     2.88ms
     75%     3.75ms
     90%     4.78ms
     99%     8.61ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     76190.38    5558.74   80482.20
  Latency        1.30ms   387.66us     5.08ms
  Latency Distribution
     50%     1.21ms
     75%     1.55ms
     90%     1.93ms
     99%     2.91ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     16918.21    2800.70   29103.62
  Latency        6.02ms     1.68ms    17.61ms
  Latency Distribution
     50%     5.75ms
     75%     7.27ms
     90%     8.59ms
     99%    11.64ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15141.70     775.79   16246.50
  Latency        6.57ms     1.88ms    15.68ms
  Latency Distribution
     50%     6.09ms
     75%     7.97ms
     90%     9.79ms
     99%    12.49ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     83459.41    5001.06   87957.33
  Latency        1.18ms   361.89us     6.08ms
  Latency Distribution
     50%     1.11ms
     75%     1.46ms
     90%     1.79ms
     99%     2.68ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     99678.25    5159.04  102953.38
  Latency        0.98ms   341.99us     5.84ms
  Latency Distribution
     50%     0.92ms
     75%     1.23ms
     90%     1.57ms
     99%     2.33ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     96392.52    7828.73  109295.64
  Latency        1.04ms   319.46us     4.51ms
  Latency Distribution
     50%     0.97ms
     75%     1.28ms
     90%     1.61ms
     99%     2.48ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13904.75     944.64   15785.32
  Latency        7.18ms     1.12ms    17.38ms
  Latency Distribution
     50%     7.04ms
     75%     7.91ms
     90%     8.97ms
     99%    10.58ms
### Users Full10 (Sync) (/users/sync-full10)
 0 / 10000 [---------------------------------------------------------------------------------------------------------------------------------------------------------]   0.00% 869 / 10000 [===========>-----------------------------------------------------------------------------------------------------------------------------]   8.69% 4316/s 00m02s 1782 / 10000 [========================>---------------------------------------------------------------------------------------------------------------]  17.82% 4438/s 00m01s 2700 / 10000 [====================================>---------------------------------------------------------------------------------------------------]  27.00% 4486/s 00m01s 3621 / 10000 [=================================================>--------------------------------------------------------------------------------------]  36.21% 4514/s 00m01s 4544 / 10000 [=============================================================>--------------------------------------------------------------------------]  45.44% 4532/s 00m01s 5456 / 10000 [==========================================================================>-------------------------------------------------------------]  54.56% 4535/s 00m01s 6374 / 10000 [===========================================================================================>---------------------------------------------------]  63.74% 4540/s 7290 / 10000 [========================================================================================================>--------------------------------------]  72.90% 4544/s 8204 / 10000 [=====================================================================================================================>-------------------------]  82.04% 4547/s 9105 / 10000 [==================================================================================================================================>------------]  91.05% 4542/s 10000 / 10000 [==============================================================================================================================================] 100.00% 4534/s 10000 / 10000 [===========================================================================================================================================] 100.00% 4534/s 2s
  Reqs/sec      4552.30     434.54    5548.23
  Latency       21.88ms     6.35ms    48.02ms
  Latency Distribution
     50%    22.35ms
     75%    26.23ms
     90%    30.45ms
     99%    37.59ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     15770.29    1815.63   17865.02
  Latency        6.19ms     1.34ms    12.29ms
  Latency Distribution
     50%     6.17ms
     75%     7.55ms
     90%     8.40ms
     99%     9.78ms
### Users Mini10 (Sync) (/users/sync-mini10)
 0 / 10000 [---------------------------------------------------------------------------------------------------------------------------------------------------------]   0.00% 2675 / 10000 [=====================================>--------------------------------------------------------------------------------------------------------]  26.75% 13342/s 5386 / 10000 [============================================================================>-----------------------------------------------------------------]  53.86% 13438/s 8146 / 10000 [===================================================================================================================>--------------------------]  81.46% 13551/s 10000 / 10000 [=============================================================================================================================================] 100.00% 12473/s 10000 / 10000 [==========================================================================================================================================] 100.00% 12471/s 0s
  Reqs/sec     13574.12    1130.01   15223.85
  Latency        7.32ms     3.05ms    25.12ms
  Latency Distribution
     50%     6.57ms
     75%     8.97ms
     90%    11.97ms
     99%    17.98ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    107688.06    9344.12  114423.48
  Latency        0.91ms   291.97us     4.59ms
  Latency Distribution
     50%     0.86ms
     75%     1.11ms
     90%     1.35ms
     99%     2.18ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     93627.83   14882.29  105490.60
  Latency        1.00ms   361.84us     5.47ms
  Latency Distribution
     50%     0.92ms
     75%     1.24ms
     90%     1.59ms
     99%     2.39ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     66294.99    4374.43   69057.25
  Latency        1.49ms   482.99us     5.39ms
  Latency Distribution
     50%     1.39ms
     75%     1.87ms
     90%     2.39ms
     99%     3.49ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     99181.58    6483.99  103255.54
  Latency        0.99ms   323.62us     4.89ms
  Latency Distribution
     50%     0.92ms
     75%     1.23ms
     90%     1.55ms
     99%     2.35ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    101064.39   12752.81  124480.92
  Latency        1.02ms   334.49us     4.75ms
  Latency Distribution
     50%     0.94ms
     75%     1.25ms
     90%     1.62ms
     99%     2.42ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     94427.13    9318.07  101908.35
  Latency        1.00ms   344.16us     4.31ms
  Latency Distribution
     50%     0.91ms
     75%     1.24ms
     90%     1.61ms
     99%     2.58ms
### CBV Response Types (/cbv-response)
  Reqs/sec    103006.16    7636.28  109406.30
  Latency        0.95ms   301.20us     5.33ms
  Latency Distribution
     50%     0.90ms
     75%     1.18ms
     90%     1.43ms
     99%     2.07ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16526.29    1148.33   19902.17
  Latency        6.05ms     0.86ms    13.28ms
  Latency Distribution
     50%     6.06ms
     75%     6.67ms
     90%     7.27ms
     99%     8.72ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     93847.95    8088.62  103820.36
  Latency        1.03ms   378.50us     4.85ms
  Latency Distribution
     50%     0.94ms
     75%     1.27ms
     90%     1.66ms
     99%     2.69ms
### File Upload (POST /upload)
  Reqs/sec     87197.58    5729.85   91629.89
  Latency        1.13ms   334.56us     4.88ms
  Latency Distribution
     50%     1.06ms
     75%     1.41ms
     90%     1.75ms
     99%     2.58ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     85093.52    5551.00   88848.56
  Latency        1.16ms   311.24us     3.99ms
  Latency Distribution
     50%     1.10ms
     75%     1.43ms
     90%     1.74ms
     99%     2.53ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9662.07    1282.83   16345.86
  Latency       10.42ms     2.98ms    23.41ms
  Latency Distribution
     50%    10.44ms
     75%    12.75ms
     90%    14.72ms
     99%    18.57ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    101551.52    7884.00  107546.64
  Latency        0.97ms   305.55us     4.03ms
  Latency Distribution
     50%     0.90ms
     75%     1.19ms
     90%     1.51ms
     99%     2.35ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     94981.37    5630.36   99881.70
  Latency        1.03ms   372.73us     6.08ms
  Latency Distribution
     50%     0.94ms
     75%     1.26ms
     90%     1.69ms
     99%     2.60ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     87924.16    6312.95   91812.54
  Latency        1.12ms   363.91us     5.71ms
  Latency Distribution
     50%     1.04ms
     75%     1.36ms
     90%     1.69ms
     99%     2.58ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     96138.13    7004.77  101412.04
  Latency        1.03ms   349.80us     5.02ms
  Latency Distribution
     50%     0.94ms
     75%     1.26ms
     90%     1.60ms
     99%     2.61ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    113418.43    9380.86  120635.34
  Latency        0.88ms   298.04us     4.21ms
  Latency Distribution
     50%   823.00us
     75%     1.05ms
     90%     1.32ms
     99%     2.10ms

### Path Parameter - int (/items/12345)
  Reqs/sec    104714.39    7737.34  109932.48
  Latency        0.94ms   327.08us     5.55ms
  Latency Distribution
     50%     0.88ms
     75%     1.16ms
     90%     1.48ms
     99%     2.18ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    103515.10    6927.30  110221.83
  Latency        0.95ms   326.70us     5.20ms
  Latency Distribution
     50%     0.89ms
     75%     1.16ms
     90%     1.45ms
     99%     2.45ms

### Header Parameter (/header)
  Reqs/sec    103140.81    7554.32  107558.14
  Latency        0.95ms   332.09us     5.81ms
  Latency Distribution
     50%     0.88ms
     75%     1.18ms
     90%     1.51ms
     99%     2.25ms

### Cookie Parameter (/cookie)
  Reqs/sec    103533.13    6455.80  108697.62
  Latency        0.95ms   292.77us     4.44ms
  Latency Distribution
     50%     0.88ms
     75%     1.17ms
     90%     1.50ms
     99%     2.21ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     84031.93    5509.41   87211.80
  Latency        1.17ms   396.96us     4.99ms
  Latency Distribution
     50%     1.07ms
     75%     1.42ms
     90%     1.82ms
     99%     2.96ms

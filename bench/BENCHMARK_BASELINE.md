# Django-Bolt Benchmark
Generated: Sun 22 Feb 2026 09:22:09 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    108908.90    9240.18  117322.16
  Latency        0.90ms   291.22us     4.79ms
  Latency Distribution
     50%   846.00us
     75%     1.09ms
     90%     1.39ms
     99%     2.15ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     87278.06    6262.81   91559.02
  Latency        1.11ms   357.45us     6.07ms
  Latency Distribution
     50%     1.03ms
     75%     1.36ms
     90%     1.75ms
     99%     2.55ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     88229.67    6090.98   93007.64
  Latency        1.12ms   372.15us     5.41ms
  Latency Distribution
     50%     1.03ms
     75%     1.34ms
     90%     1.71ms
     99%     2.88ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    102158.30    6874.26  105679.49
  Latency        0.96ms   299.15us     5.13ms
  Latency Distribution
     50%     0.90ms
     75%     1.18ms
     90%     1.49ms
     99%     2.16ms
### Cookie Endpoint (/cookie)
  Reqs/sec    103414.72    6010.15  108900.34
  Latency        0.94ms   301.42us     4.87ms
  Latency Distribution
     50%     0.88ms
     75%     1.16ms
     90%     1.44ms
     99%     2.19ms
### Exception Endpoint (/exc)
  Reqs/sec     97569.83    6432.55  101847.16
  Latency        1.01ms   310.85us     5.06ms
  Latency Distribution
     50%     0.95ms
     75%     1.24ms
     90%     1.59ms
     99%     2.23ms
### HTML Response (/html)
  Reqs/sec    104147.23    9666.84  113660.86
  Latency        0.94ms   290.04us     4.69ms
  Latency Distribution
     50%     0.89ms
     75%     1.16ms
     90%     1.44ms
     99%     2.22ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     32109.04    7706.05   49871.58
  Latency        3.21ms     1.41ms    16.11ms
  Latency Distribution
     50%     3.00ms
     75%     3.87ms
     90%     4.82ms
     99%     9.13ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     73661.44    5573.55   77600.33
  Latency        1.33ms   393.88us     5.79ms
  Latency Distribution
     50%     1.24ms
     75%     1.60ms
     90%     1.99ms
     99%     3.00ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     15865.33    2074.09   18992.22
  Latency        6.29ms     1.94ms    19.36ms
  Latency Distribution
     50%     6.08ms
     75%     7.46ms
     90%     8.85ms
     99%    13.61ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15379.86    1079.11   17914.54
  Latency        6.48ms     1.98ms    16.90ms
  Latency Distribution
     50%     6.19ms
     75%     7.87ms
     90%     9.64ms
     99%    12.77ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     66574.14    6405.16   76783.72
  Latency        1.50ms   627.26us     7.69ms
  Latency Distribution
     50%     1.35ms
     75%     1.91ms
     90%     2.46ms
     99%     3.97ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     81782.65    7686.33   86769.49
  Latency        1.20ms   438.51us     6.06ms
  Latency Distribution
     50%     1.11ms
     75%     1.51ms
     90%     1.94ms
     99%     2.96ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     88434.79    8790.45   94810.00
  Latency        1.12ms   445.43us     5.81ms
  Latency Distribution
     50%     1.01ms
     75%     1.36ms
     90%     1.78ms
     99%     3.03ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
 0 / 10000 [---------------------------------------------------------------------------------------------------------------------------------------------------------------------]   0.00% 2740 / 10000 [==========================================>---------------------------------------------------------------------------------------------------------------]  27.40% 13665/s 5590 / 10000 [======================================================================================>-------------------------------------------------------------------]  55.90% 13950/s 8454 / 10000 [==================================================================================================================================>-----------------------]  84.54% 14065/s 10000 / 10000 [=========================================================================================================================================================] 100.00% 12468/s 10000 / 10000 [======================================================================================================================================================] 100.00% 12466/s 0s
  Reqs/sec     14140.32    1028.55   16416.50
  Latency        7.06ms     2.13ms    19.03ms
  Latency Distribution
     50%     7.07ms
     75%     8.75ms
     90%    10.26ms
     99%    13.50ms
### Users Full10 (Sync) (/users/sync-full10)
 0 / 10000 [---------------------------------------------------------------------------------------------------------------------------------------------------------------------]   0.00% 881 / 10000 [=============>---------------------------------------------------------------------------------------------------------------------------------------]   8.81% 4386/s 00m02s 1757 / 10000 [==========================>-------------------------------------------------------------------------------------------------------------------------]  17.57% 4377/s 00m01s 2637 / 10000 [=======================================>------------------------------------------------------------------------------------------------------------]  26.37% 4380/s 00m01s 3513 / 10000 [===================================================>------------------------------------------------------------------------------------------------]  35.13% 4379/s 00m01s 4383 / 10000 [================================================================>-----------------------------------------------------------------------------------]  43.83% 4370/s 00m01s 5256 / 10000 [=============================================================================>----------------------------------------------------------------------]  52.56% 4368/s 00m01s 6137 / 10000 [===============================================================================================>-----------------------------------------------------------]  61.37% 4372/s 6998 / 10000 [============================================================================================================>----------------------------------------------]  69.98% 4363/s 7899 / 10000 [==========================================================================================================================>--------------------------------]  78.99% 4377/s 8796 / 10000 [========================================================================================================================================>------------------]  87.96% 4387/s 9727 / 10000 [======================================================================================================================================================>----]  97.27% 4410/s 10000 / 10000 [==========================================================================================================================================================] 100.00% 4156/s 10000 / 10000 [=======================================================================================================================================================] 100.00% 4155/s 2s
  Reqs/sec      4412.96     470.05    6265.65
  Latency       22.54ms     6.33ms    50.43ms
  Latency Distribution
     50%    23.01ms
     75%    26.88ms
     90%    30.89ms
     99%    38.09ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     16437.22    1012.13   19107.21
  Latency        6.06ms     1.76ms    14.53ms
  Latency Distribution
     50%     5.97ms
     75%     7.44ms
     90%     8.77ms
     99%    11.31ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13650.00    1405.48   16058.44
  Latency        7.29ms     2.80ms    21.96ms
  Latency Distribution
     50%     6.82ms
     75%     9.05ms
     90%    11.38ms
     99%    16.25ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    104730.65    8622.86  111417.24
  Latency        0.93ms   297.94us     5.39ms
  Latency Distribution
     50%     0.86ms
     75%     1.15ms
     90%     1.46ms
     99%     2.08ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     99604.15    9721.00  107020.91
  Latency        0.98ms   304.36us     4.05ms
  Latency Distribution
     50%     0.91ms
     75%     1.19ms
     90%     1.55ms
     99%     2.27ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     66387.28    4068.36   69337.71
  Latency        1.49ms   468.66us     6.40ms
  Latency Distribution
     50%     1.40ms
     75%     1.84ms
     90%     2.30ms
     99%     3.42ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     98667.55    6583.95  104523.54
  Latency        0.99ms   307.31us     4.24ms
  Latency Distribution
     50%     0.93ms
     75%     1.24ms
     90%     1.54ms
     99%     2.48ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     94515.91    6745.61   99845.23
  Latency        1.04ms   318.50us     6.18ms
  Latency Distribution
     50%     0.97ms
     75%     1.29ms
     90%     1.60ms
     99%     2.40ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     99431.58    9469.75  112935.00
  Latency        1.01ms   302.62us     4.21ms
  Latency Distribution
     50%     0.95ms
     75%     1.25ms
     90%     1.56ms
     99%     2.29ms
### CBV Response Types (/cbv-response)
  Reqs/sec    100374.77    7799.88  106434.01
  Latency        0.97ms   318.13us     4.60ms
  Latency Distribution
     50%     0.90ms
     75%     1.21ms
     90%     1.57ms
     99%     2.37ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
 0 / 10000 [---------------------------------------------------------------------------------------------------------------------------------------------------------------------]   0.00% 3299 / 10000 [==================================================>-------------------------------------------------------------------------------------------------------]  32.99% 16450/s 6729 / 10000 [=======================================================================================================>--------------------------------------------------]  67.29% 16785/s 10000 / 10000 [=========================================================================================================================================================] 100.00% 16609/s 10000 / 10000 [======================================================================================================================================================] 100.00% 16605/s 0s
  Reqs/sec     17094.79    1620.50   22718.13
  Latency        5.86ms     1.41ms    14.08ms
  Latency Distribution
     50%     5.78ms
     75%     6.82ms
     90%     7.99ms
     99%    10.35ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     91274.99    7017.98   96137.31
  Latency        1.09ms   417.77us     5.47ms
  Latency Distribution
     50%     1.00ms
     75%     1.30ms
     90%     1.69ms
     99%     3.11ms
### File Upload (POST /upload)
  Reqs/sec     81507.92    6994.85   85983.53
  Latency        1.21ms   373.67us     4.80ms
  Latency Distribution
     50%     1.14ms
     75%     1.50ms
     90%     1.88ms
     99%     2.80ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     80083.20    4943.17   85332.16
  Latency        1.22ms   390.26us     5.35ms
  Latency Distribution
     50%     1.14ms
     75%     1.51ms
     90%     1.92ms
     99%     2.90ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9691.82    1056.46   12178.44
  Latency       10.31ms     2.31ms    22.03ms
  Latency Distribution
     50%    10.34ms
     75%    11.83ms
     90%    13.42ms
     99%    17.24ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     93989.01    6951.09   99922.67
  Latency        1.06ms   423.16us     5.18ms
  Latency Distribution
     50%     0.96ms
     75%     1.31ms
     90%     1.69ms
     99%     3.22ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     90686.97    6694.48   95253.77
  Latency        1.08ms   342.19us     5.06ms
  Latency Distribution
     50%     1.00ms
     75%     1.34ms
     90%     1.67ms
     99%     2.61ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     87302.20    6958.57   92157.20
  Latency        1.13ms   351.88us     4.77ms
  Latency Distribution
     50%     1.06ms
     75%     1.34ms
     90%     1.66ms
     99%     2.58ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     92036.61   12441.31  100773.82
  Latency        1.02ms   301.79us     3.98ms
  Latency Distribution
     50%     0.96ms
     75%     1.22ms
     90%     1.56ms
     99%     2.40ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    106266.95   10620.84  113928.20
  Latency        0.93ms   342.15us     4.33ms
  Latency Distribution
     50%     0.85ms
     75%     1.14ms
     90%     1.47ms
     99%     2.55ms

### Path Parameter - int (/items/12345)
  Reqs/sec    100428.83    9187.19  111520.02
  Latency        1.00ms   354.89us     4.56ms
  Latency Distribution
     50%     0.90ms
     75%     1.22ms
     90%     1.59ms
     99%     2.57ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec     97757.73    7540.26  103365.79
  Latency        1.01ms   334.19us     4.40ms
  Latency Distribution
     50%     0.94ms
     75%     1.23ms
     90%     1.58ms
     99%     2.48ms

### Header Parameter (/header)
  Reqs/sec     97381.55    4740.78  101362.27
  Latency        1.01ms   305.61us     4.21ms
  Latency Distribution
     50%     0.95ms
     75%     1.25ms
     90%     1.58ms
     99%     2.38ms

### Cookie Parameter (/cookie)
  Reqs/sec    100262.23    6595.19  106658.62
  Latency        0.98ms   348.91us     6.01ms
  Latency Distribution
     50%     0.89ms
     75%     1.21ms
     90%     1.54ms
     99%     2.40ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     81613.16    5914.13   85923.22
  Latency        1.20ms   444.02us     5.45ms
  Latency Distribution
     50%     1.08ms
     75%     1.50ms
     90%     2.00ms
     99%     3.28ms

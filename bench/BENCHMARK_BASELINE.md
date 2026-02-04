# Django-Bolt Benchmark
Generated: Wed 04 Feb 2026 09:25:35 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    106040.26    7078.95  111339.86
  Latency        0.93ms   305.04us     4.36ms
  Latency Distribution
     50%     0.87ms
     75%     1.14ms
     90%     1.43ms
     99%     2.25ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     87914.84    7174.09   93355.22
  Latency        1.12ms   331.49us     5.81ms
  Latency Distribution
     50%     1.04ms
     75%     1.37ms
     90%     1.69ms
     99%     2.46ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     83229.06    7694.50   89169.31
  Latency        1.19ms   406.77us     6.03ms
  Latency Distribution
     50%     1.10ms
     75%     1.46ms
     90%     1.84ms
     99%     2.90ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     98543.47    6517.75  103586.94
  Latency        0.99ms   309.06us     3.95ms
  Latency Distribution
     50%     0.93ms
     75%     1.21ms
     90%     1.52ms
     99%     2.41ms
### Cookie Endpoint (/cookie)
  Reqs/sec     99438.38    9581.59  107219.34
  Latency        0.99ms   338.35us     6.07ms
  Latency Distribution
     50%     0.93ms
     75%     1.20ms
     90%     1.48ms
     99%     2.25ms
### Exception Endpoint (/exc)
  Reqs/sec    110201.25   33969.40  178801.87
  Latency        1.01ms   312.60us     4.65ms
  Latency Distribution
     50%     0.94ms
     75%     1.24ms
     90%     1.56ms
     99%     2.42ms
### HTML Response (/html)
  Reqs/sec     99334.45    7751.50  107005.97
  Latency        0.99ms   312.42us     4.55ms
  Latency Distribution
     50%     0.92ms
     75%     1.21ms
     90%     1.51ms
     99%     2.31ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     29696.70    6776.03   37050.25
  Latency        3.36ms     1.74ms    21.53ms
  Latency Distribution
     50%     2.97ms
     75%     3.96ms
     90%     5.26ms
     99%    11.13ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     76552.39    5111.11   81078.57
  Latency        1.29ms   390.39us     5.71ms
  Latency Distribution
     50%     1.21ms
     75%     1.59ms
     90%     1.97ms
     99%     2.85ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     16379.85    1789.25   17467.36
  Latency        5.98ms     2.08ms    16.25ms
  Latency Distribution
     50%     5.50ms
     75%     6.97ms
     90%    10.19ms
     99%    12.36ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15117.04     891.44   17319.33
  Latency        6.58ms     1.30ms    12.72ms
  Latency Distribution
     50%     6.70ms
     75%     7.65ms
     90%     8.50ms
     99%    10.10ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     74412.96    4935.66   79144.63
  Latency        1.31ms   463.39us     5.48ms
  Latency Distribution
     50%     1.21ms
     75%     1.64ms
     90%     2.14ms
     99%     3.24ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     79003.94   20921.00  109275.05
  Latency        1.28ms   783.12us    12.64ms
  Latency Distribution
     50%     1.06ms
     75%     1.57ms
     90%     2.28ms
     99%     4.82ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     95065.63    7078.25  100279.55
  Latency        1.04ms   330.73us     5.75ms
  Latency Distribution
     50%     0.97ms
     75%     1.27ms
     90%     1.60ms
     99%     2.36ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13690.15     921.89   15938.04
  Latency        7.29ms     1.03ms    17.45ms
  Latency Distribution
     50%     7.33ms
     75%     8.12ms
     90%     8.76ms
     99%    10.15ms
### Users Full10 (Sync) (/users/sync-full10)
 0 / 10000 [-------------------------------------------------------]   0.00% 2350 / 10000 [==========>---------------------------------]  23.50% 11717/s 4765 / 10000 [====================>-----------------------]  47.65% 11888/s 7154 / 10000 [===============================>------------]  71.54% 11903/s 9562 / 10000 [==========================================>-]  95.62% 11934/s 10000 / 10000 [============================================] 100.00% 9979/s 10000 / 10000 [=========================================] 100.00% 9978/s 1s
  Reqs/sec     12004.19     617.89   14246.38
  Latency        8.30ms     1.70ms    16.16ms
  Latency Distribution
     50%     7.72ms
     75%     9.52ms
     90%    11.69ms
     99%    13.27ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     15892.85     860.81   18692.03
  Latency        6.28ms     1.32ms    11.74ms
  Latency Distribution
     50%     6.12ms
     75%     7.53ms
     90%     8.59ms
     99%     9.80ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13265.46    1104.20   14927.98
  Latency        7.48ms     3.96ms    30.34ms
  Latency Distribution
     50%     6.42ms
     75%     9.28ms
     90%    14.08ms
     99%    20.90ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    102119.77   10415.79  111020.02
  Latency        0.96ms   332.46us     5.74ms
  Latency Distribution
     50%     0.89ms
     75%     1.17ms
     90%     1.50ms
     99%     2.36ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     99457.97    5930.49  103433.50
  Latency        0.99ms   299.14us     4.64ms
  Latency Distribution
     50%     0.93ms
     75%     1.21ms
     90%     1.50ms
     99%     2.27ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     66354.10    4334.87   71272.88
  Latency        1.50ms   436.64us     5.01ms
  Latency Distribution
     50%     1.40ms
     75%     1.82ms
     90%     2.31ms
     99%     3.26ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     92289.00    7471.52  100052.68
  Latency        1.06ms   355.90us     4.61ms
  Latency Distribution
     50%     0.97ms
     75%     1.33ms
     90%     1.71ms
     99%     2.58ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     95030.52    6437.97  100035.25
  Latency        1.04ms   354.45us     5.04ms
  Latency Distribution
     50%     0.97ms
     75%     1.27ms
     90%     1.57ms
     99%     2.40ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     98989.78   10398.22  117766.68
  Latency        1.03ms   328.13us     4.68ms
  Latency Distribution
     50%     0.95ms
     75%     1.26ms
     90%     1.58ms
     99%     2.43ms
### CBV Response Types (/cbv-response)
  Reqs/sec    102628.77    8916.60  108670.16
  Latency        0.95ms   294.05us     4.73ms
  Latency Distribution
     50%     0.89ms
     75%     1.15ms
     90%     1.46ms
     99%     2.13ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     16022.47    1100.50   17538.11
  Latency        6.19ms     1.75ms    14.84ms
  Latency Distribution
     50%     5.89ms
     75%     7.58ms
     90%     9.26ms
     99%    11.39ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     97270.26   11221.77  113735.24
  Latency        1.03ms   321.40us     5.78ms
  Latency Distribution
     50%     0.97ms
     75%     1.25ms
     90%     1.55ms
     99%     2.31ms
### File Upload (POST /upload)
  Reqs/sec     86190.03    6755.16   91530.92
  Latency        1.15ms   345.15us     5.33ms
  Latency Distribution
     50%     1.07ms
     75%     1.41ms
     90%     1.75ms
     99%     2.61ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     84047.07    5297.83   88745.45
  Latency        1.17ms   374.63us     5.14ms
  Latency Distribution
     50%     1.09ms
     75%     1.45ms
     90%     1.84ms
     99%     2.61ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
 0 / 10000 [-------------------------------------------------------]   0.00% 1831 / 10000 [========>------------------------------------]  18.31% 9126/s 3767 / 10000 [================>----------------------------]  37.67% 9386/s 5646 / 10000 [=========================>-------------------]  56.46% 9380/s 7568 / 10000 [==================================>----------]  75.68% 9427/s 9475 / 10000 [==========================================>--]  94.75% 9445/s 10000 / 10000 [============================================] 100.00% 8306/s 10000 / 10000 [=========================================] 100.00% 8305/s 1s
  Reqs/sec      9493.27     873.74   10932.95
  Latency       10.50ms     3.04ms    22.68ms
  Latency Distribution
     50%    10.97ms
     75%    13.22ms
     90%    14.59ms
     99%    18.48ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     98160.93    7845.86  106011.44
  Latency        0.99ms   356.70us     5.94ms
  Latency Distribution
     50%     0.89ms
     75%     1.22ms
     90%     1.58ms
     99%     2.54ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     99703.76    9044.26  112686.26
  Latency        1.01ms   297.14us     4.70ms
  Latency Distribution
     50%     0.95ms
     75%     1.22ms
     90%     1.53ms
     99%     2.29ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     88354.37    7322.97   95719.02
  Latency        1.11ms   324.37us     4.93ms
  Latency Distribution
     50%     1.05ms
     75%     1.33ms
     90%     1.66ms
     99%     2.51ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     95742.69    5706.46  100977.06
  Latency        1.02ms   309.19us     4.59ms
  Latency Distribution
     50%     0.94ms
     75%     1.25ms
     90%     1.54ms
     99%     2.30ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec     99848.40    8365.09  107074.53
  Latency        0.98ms   349.44us     4.35ms
  Latency Distribution
     50%     0.90ms
     75%     1.20ms
     90%     1.54ms
     99%     2.69ms

### Path Parameter - int (/items/12345)
  Reqs/sec     89737.09    6935.23   95856.25
  Latency        1.10ms   360.51us     5.66ms
  Latency Distribution
     50%     1.03ms
     75%     1.35ms
     90%     1.68ms
     99%     2.58ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec     93632.27    6418.85   99057.22
  Latency        1.06ms   283.65us     4.03ms
  Latency Distribution
     50%     1.02ms
     75%     1.30ms
     90%     1.57ms
     99%     2.24ms

### Header Parameter (/header)
  Reqs/sec     91032.09    5754.91   97361.86
  Latency        1.08ms   367.63us     5.01ms
  Latency Distribution
     50%     1.01ms
     75%     1.32ms
     90%     1.67ms
     99%     2.57ms

### Cookie Parameter (/cookie)
  Reqs/sec     89837.53    5028.59   95356.22
  Latency        1.10ms   306.98us     4.39ms
  Latency Distribution
     50%     1.05ms
     75%     1.36ms
     90%     1.67ms
     99%     2.41ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     78953.15    4100.76   81729.47
  Latency        1.24ms   333.18us     4.61ms
  Latency Distribution
     50%     1.18ms
     75%     1.50ms
     90%     1.85ms
     99%     2.68ms

# Django-Bolt Benchmark
Generated: Wed 04 Feb 2026 05:49:03 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    109582.95   12067.06  116082.93
  Latency        0.90ms   366.02us     5.30ms
  Latency Distribution
     50%   829.00us
     75%     1.08ms
     90%     1.36ms
     99%     2.23ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     86825.26    9244.73   91919.44
  Latency        1.14ms     0.88ms    12.01ms
  Latency Distribution
     50%     1.01ms
     75%     1.35ms
     90%     1.69ms
     99%     2.57ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     89248.02    5317.91   93985.31
  Latency        1.10ms   311.96us     4.64ms
  Latency Distribution
     50%     1.03ms
     75%     1.33ms
     90%     1.64ms
     99%     2.32ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    101740.68    7088.26  105716.52
  Latency        0.97ms   299.85us     5.15ms
  Latency Distribution
     50%     0.90ms
     75%     1.22ms
     90%     1.55ms
     99%     2.27ms
### Cookie Endpoint (/cookie)
  Reqs/sec    103258.76    9124.11  110341.19
  Latency        0.95ms   317.44us     6.20ms
  Latency Distribution
     50%     0.89ms
     75%     1.19ms
     90%     1.47ms
     99%     2.21ms
### Exception Endpoint (/exc)
  Reqs/sec    101129.55    7443.08  105676.02
  Latency        0.97ms   321.93us     4.87ms
  Latency Distribution
     50%     0.90ms
     75%     1.21ms
     90%     1.54ms
     99%     2.21ms
### HTML Response (/html)
  Reqs/sec    107419.02    8857.53  112791.80
  Latency        0.92ms   306.81us     4.97ms
  Latency Distribution
     50%     0.86ms
     75%     1.12ms
     90%     1.41ms
     99%     2.12ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     34314.62    7593.85   38435.92
  Latency        2.91ms     1.63ms    22.28ms
  Latency Distribution
     50%     2.51ms
     75%     3.54ms
     90%     4.53ms
     99%    10.89ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     80581.29    6545.27   90113.44
  Latency        1.24ms   335.57us     4.66ms
  Latency Distribution
     50%     1.15ms
     75%     1.51ms
     90%     1.88ms
     99%     2.71ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     17289.63    1369.19   18554.94
  Latency        5.75ms     1.33ms    13.84ms
  Latency Distribution
     50%     5.72ms
     75%     6.55ms
     90%     7.88ms
     99%    10.27ms
### Get User via Dependency (/auth/me-dependency)
 0 / 10000 [-------------------------------------------------------]   0.00% 2987 / 10000 [=============>------------------------------]  29.87% 14905/s 6050 / 10000 [==========================>-----------------]  60.50% 15101/s 9115 / 10000 [========================================>---]  91.15% 15171/s 10000 / 10000 [===========================================] 100.00% 12471/s 10000 / 10000 [========================================] 100.00% 12469/s 0s
  Reqs/sec     15232.85     866.05   16861.25
  Latency        6.53ms     1.14ms    12.15ms
  Latency Distribution
     50%     6.42ms
     75%     7.40ms
     90%     8.37ms
     99%    10.23ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     84231.61    6466.50   90132.06
  Latency        1.16ms   417.52us     4.90ms
  Latency Distribution
     50%     1.05ms
     75%     1.45ms
     90%     1.88ms
     99%     3.10ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    100396.13    6294.84  104738.77
  Latency        0.98ms   316.53us     4.63ms
  Latency Distribution
     50%     0.92ms
     75%     1.21ms
     90%     1.57ms
     99%     2.33ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     93836.55    5049.40   97480.83
  Latency        1.03ms   354.36us     5.40ms
  Latency Distribution
     50%     0.95ms
     75%     1.27ms
     90%     1.63ms
     99%     2.59ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     13866.33    1120.31   16505.37
  Latency        7.21ms     1.55ms    17.01ms
  Latency Distribution
     50%     7.34ms
     75%     8.64ms
     90%     9.36ms
     99%    11.29ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     12175.08     791.15   13418.41
  Latency        8.18ms     1.96ms    19.09ms
  Latency Distribution
     50%     8.11ms
     75%     9.96ms
     90%    11.14ms
     99%    13.62ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     16144.81    1400.34   22766.90
  Latency        6.23ms     1.91ms    15.77ms
  Latency Distribution
     50%     5.90ms
     75%     7.49ms
     90%     9.48ms
     99%    11.73ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     13349.33    1925.89   15775.40
  Latency        7.47ms     3.01ms    41.72ms
  Latency Distribution
     50%     6.95ms
     75%     9.12ms
     90%    11.41ms
     99%    17.50ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    107886.18   10669.94  116169.88
  Latency        0.92ms   352.12us     5.45ms
  Latency Distribution
     50%     0.86ms
     75%     1.12ms
     90%     1.38ms
     99%     2.13ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    101562.76   13112.76  125066.31
  Latency        1.02ms   308.07us     4.49ms
  Latency Distribution
     50%     0.96ms
     75%     1.25ms
     90%     1.55ms
     99%     2.34ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     66146.99    4675.44   71410.39
  Latency        1.49ms   479.10us     6.99ms
  Latency Distribution
     50%     1.39ms
     75%     1.86ms
     90%     2.36ms
     99%     3.62ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     96618.01    8638.72  102275.80
  Latency        1.02ms   362.75us     5.73ms
  Latency Distribution
     50%     0.94ms
     75%     1.24ms
     90%     1.60ms
     99%     2.65ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     93135.06    6073.25  100494.71
  Latency        1.05ms   360.32us     5.22ms
  Latency Distribution
     50%     0.98ms
     75%     1.26ms
     90%     1.62ms
     99%     2.53ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     97799.71    7241.04  106601.61
  Latency        1.00ms   303.83us     5.63ms
  Latency Distribution
     50%     0.95ms
     75%     1.21ms
     90%     1.51ms
     99%     2.19ms
### CBV Response Types (/cbv-response)
  Reqs/sec    104028.05    9013.75  112590.88
  Latency        0.94ms   271.23us     3.73ms
  Latency Distribution
     50%     0.88ms
     75%     1.16ms
     90%     1.45ms
     99%     2.15ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     15958.59    1529.90   17448.54
  Latency        6.19ms     1.81ms    17.62ms
  Latency Distribution
     50%     5.91ms
     75%     7.85ms
     90%     8.95ms
     99%    12.01ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     98092.83   11434.08  115101.01
  Latency        1.04ms   368.58us     6.02ms
  Latency Distribution
     50%     0.95ms
     75%     1.26ms
     90%     1.64ms
     99%     2.66ms
### File Upload (POST /upload)
  Reqs/sec     88383.53    6246.55   92247.92
  Latency        1.11ms   317.83us     5.01ms
  Latency Distribution
     50%     1.06ms
     75%     1.37ms
     90%     1.70ms
     99%     2.42ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     84878.30    6374.70   88456.57
  Latency        1.16ms   339.65us     6.12ms
  Latency Distribution
     50%     1.09ms
     75%     1.41ms
     90%     1.72ms
     99%     2.60ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
 0 / 10000 [-------------------------------------------------------]   0.00% 1744 / 10000 [=======>-------------------------------------]  17.44% 8688/s 3610 / 10000 [================>----------------------------]  36.10% 9003/s 5487 / 10000 [========================>--------------------]  54.87% 9127/s 7383 / 10000 [=================================>-----------]  73.83% 9205/s 9275 / 10000 [=========================================>---]  92.75% 9251/s 10000 / 10000 [============================================] 100.00% 8309/s 10000 / 10000 [=========================================] 100.00% 8309/s 1s
  Reqs/sec      9329.30     818.91   11716.89
  Latency       10.70ms     2.54ms    23.36ms
  Latency Distribution
     50%    11.14ms
     75%    12.73ms
     90%    14.12ms
     99%    17.18ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    101567.56   10688.26  108044.75
  Latency        0.96ms   327.38us     6.33ms
  Latency Distribution
     50%     0.89ms
     75%     1.16ms
     90%     1.49ms
     99%     2.12ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     80618.42   13846.87   99533.30
  Latency        1.22ms   640.55us     8.17ms
  Latency Distribution
     50%     1.03ms
     75%     1.47ms
     90%     2.07ms
     99%     4.26ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     88807.26    5695.68   92762.16
  Latency        1.11ms   356.62us     4.87ms
  Latency Distribution
     50%     1.03ms
     75%     1.35ms
     90%     1.75ms
     99%     2.68ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     95584.69    6818.10  100701.34
  Latency        1.04ms   321.88us     4.92ms
  Latency Distribution
     50%     0.97ms
     75%     1.26ms
     90%     1.59ms
     99%     2.42ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    108038.05    9674.54  113755.10
  Latency        0.92ms   277.78us     3.68ms
  Latency Distribution
     50%     0.86ms
     75%     1.11ms
     90%     1.38ms
     99%     2.22ms

### Path Parameter - int (/items/12345)
  Reqs/sec    100743.01    6521.54  104592.06
  Latency        0.98ms   276.44us     4.43ms
  Latency Distribution
     50%     0.93ms
     75%     1.19ms
     90%     1.50ms
     99%     2.17ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec     90013.81   21121.28  102758.27
  Latency        1.00ms   319.17us     5.59ms
  Latency Distribution
     50%     0.93ms
     75%     1.24ms
     90%     1.56ms
     99%     2.25ms

### Header Parameter (/header)
  Reqs/sec     99026.68    7412.94  105050.05
  Latency        0.99ms   323.87us     5.78ms
  Latency Distribution
     50%     0.92ms
     75%     1.21ms
     90%     1.54ms
     99%     2.29ms

### Cookie Parameter (/cookie)
  Reqs/sec    101380.76    6677.22  104649.75
  Latency        0.97ms   351.21us     5.82ms
  Latency Distribution
     50%     0.90ms
     75%     1.17ms
     90%     1.47ms
     99%     2.35ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     65309.57    9776.72   79643.04
  Latency        1.51ms   683.67us     6.30ms
  Latency Distribution
     50%     1.32ms
     75%     1.83ms
     90%     2.55ms
     99%     4.67ms

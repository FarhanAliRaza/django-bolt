# Django-Bolt Benchmark
Generated: Sun 01 Feb 2026 12:58:06 AM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec     25527.38    2477.42   29561.33
  Latency        3.92ms   570.41us    15.18ms
  Latency Distribution
     50%     4.01ms
     75%     4.46ms
     90%     4.89ms
     99%     6.05ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
 0 / 10000 [---------------------------------]   0.00% 3372 / 10000 [=======>--------------]  33.72% 16786/s 7090 / 10000 [===============>------]  70.90% 17673/s 10000 / 10000 [=====================] 100.00% 16607/s 10000 / 10000 [==================] 100.00% 16605/s 0s
  Reqs/sec     18061.93    2436.43   23888.49
  Latency        5.54ms     0.96ms    11.22ms
  Latency Distribution
     50%     5.69ms
     75%     6.50ms
     90%     7.17ms
     99%     8.23ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     18252.37    2607.38   25118.02
  Latency        5.50ms     0.94ms    11.74ms
  Latency Distribution
     50%     5.61ms
     75%     6.32ms
     90%     7.03ms
     99%     8.57ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     22757.45    2294.28   28505.51
  Latency        4.38ms   730.84us     8.92ms
  Latency Distribution
     50%     4.67ms
     75%     5.12ms
     90%     5.74ms
     99%     6.69ms
### Cookie Endpoint (/cookie)
  Reqs/sec     23447.05    2749.77   30447.33
  Latency        4.28ms   700.55us     8.17ms
  Latency Distribution
     50%     4.57ms
     75%     4.98ms
     90%     5.41ms
     99%     6.69ms
### Exception Endpoint (/exc)
 0 / 10000 [---------------------------------]   0.00% 4650 / 10000 [==========>-----------]  46.50% 23148/s 9008 / 10000 [===================>--]  90.08% 22443/s 10000 / 10000 [=====================] 100.00% 16614/s 10000 / 10000 [==================] 100.00% 16611/s 0s
  Reqs/sec     26052.29   17385.64  105277.01
  Latency        4.42ms   772.09us     9.08ms
  Latency Distribution
     50%     4.60ms
     75%     5.07ms
     90%     5.51ms
     99%     7.30ms
### HTML Response (/html)
  Reqs/sec     24558.26    2726.05   32298.39
  Latency        4.09ms   605.28us     8.59ms
  Latency Distribution
     50%     4.28ms
     75%     4.68ms
     90%     5.06ms
     99%     6.07ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     12054.08    1791.55   16195.55
  Latency        8.30ms     1.19ms    18.59ms
  Latency Distribution
     50%     8.01ms
     75%     8.54ms
     90%     9.28ms
     99%    16.04ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     20333.49    2792.63   27663.24
  Latency        4.92ms     0.99ms    11.64ms
  Latency Distribution
     50%     5.17ms
     75%     5.66ms
     90%     6.37ms
     99%     8.48ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
 0 / 10000 [---------------------------------]   0.00% 522 / 10000 [>----------------]   5.22% 2598/s 00m03s 999 / 10000 [=>---------------]   9.99% 2490/s 00m03s 1472 / 10000 [==>-------------]  14.72% 2447/s 00m03s 1979 / 10000 [===>------------]  19.79% 2468/s 00m03s 2552 / 10000 [====>-----------]  25.52% 2547/s 00m02s 3140 / 10000 [=====>----------]  31.40% 2612/s 00m02s 3649 / 10000 [=====>----------]  36.49% 2602/s 00m02s 4234 / 10000 [======>---------]  42.34% 2641/s 00m02s 4835 / 10000 [=======>--------]  48.35% 2681/s 00m01s 5415 / 10000 [========>-------]  54.15% 2703/s 00m01s 6012 / 10000 [=========>------]  60.12% 2728/s 00m01s 6603 / 10000 [==========>-----]  66.03% 2746/s 00m01s 7186 / 10000 [===========>----]  71.86% 2759/s 00m01s 7798 / 10000 [=================>-----]  77.98% 2779/s 8298 / 10000 [===================>---]  82.98% 2760/s 8894 / 10000 [====================>--]  88.94% 2773/s 9448 / 10000 [=====================>-]  94.48% 2773/s 10000 / 10000 [======================] 100.00% 2772/s 10000 / 10000 [===================] 100.00% 2772/s 3s
  Reqs/sec      2812.15     779.16    6680.23
  Latency       35.63ms     4.28ms    50.85ms
  Latency Distribution
     50%    35.25ms
     75%    38.10ms
     90%    41.93ms
     99%    47.98ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec      2604.59     278.08    4035.45
  Latency       38.35ms     2.36ms    54.95ms
  Latency Distribution
     50%    38.14ms
     75%    39.49ms
     90%    41.45ms
     99%    45.72ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     22733.78   15286.94   97016.44
  Latency        5.01ms   790.06us     9.66ms
  Latency Distribution
     50%     5.36ms
     75%     5.82ms
     90%     6.30ms
     99%     7.64ms

## Items GET Performance (/items/1?q=hello)
 0 / 10000 [---------------------------------]   0.00% 4454 / 10000 [=========>------------]  44.54% 22189/s 8575 / 10000 [==================>---]  85.75% 21387/s 10000 / 10000 [=====================] 100.00% 16612/s 10000 / 10000 [==================] 100.00% 16610/s 0s
  Reqs/sec     21762.63    2972.41   26119.07
  Latency        4.58ms     0.91ms     9.55ms
  Latency Distribution
     50%     4.79ms
     75%     5.22ms
     90%     6.00ms
     99%     8.05ms

## Items PUT JSON Performance (/items/1)
 0 / 10000 [---------------------------------]   0.00% 4290 / 10000 [=========>------------]  42.90% 21402/s 8538 / 10000 [==================>---]  85.38% 21312/s 10000 / 10000 [=====================] 100.00% 16630/s 10000 / 10000 [==================] 100.00% 16628/s 0s
  Reqs/sec     21679.68    2304.52   29390.66
  Latency        4.65ms   526.26us     8.28ms
  Latency Distribution
     50%     4.51ms
     75%     5.16ms
     90%     5.60ms
     99%     6.96ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec      2479.22     264.78    3607.87
  Latency       40.22ms     2.86ms    54.90ms
  Latency Distribution
     50%    39.40ms
     75%    41.70ms
     90%    44.21ms
     99%    51.39ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec      1974.61     242.23    3830.32
  Latency       50.68ms     3.71ms    65.31ms
  Latency Distribution
     50%    50.25ms
     75%    52.61ms
     90%    55.15ms
     99%    61.91ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec      2630.42     339.07    5127.01
  Latency       38.09ms     2.91ms    52.15ms
  Latency Distribution
     50%    37.70ms
     75%    39.48ms
     90%    41.90ms
     99%    46.86ms
### Users Mini10 (Sync) (/users/sync-mini10)
 0 / 10000 [---------------------------------]   0.00% 311 / 10000 [>----------------]   3.11% 1546/s 00m06s 711 / 10000 [=>---------------]   7.11% 1771/s 00m05s 1109 / 10000 [=>--------------]  11.09% 1843/s 00m04s 1495 / 10000 [==>-------------]  14.95% 1863/s 00m04s 1889 / 10000 [===>------------]  18.89% 1882/s 00m04s 2291 / 10000 [===>------------]  22.91% 1903/s 00m04s 2686 / 10000 [====>-----------]  26.86% 1912/s 00m03s 3080 / 10000 [====>-----------]  30.80% 1919/s 00m03s 3466 / 10000 [=====>----------]  34.66% 1920/s 00m03s 3844 / 10000 [======>---------]  38.44% 1917/s 00m03s 4241 / 10000 [======>---------]  42.41% 1922/s 00m02s 4646 / 10000 [=======>--------]  46.46% 1930/s 00m02s 5064 / 10000 [========>-------]  50.64% 1941/s 00m02s 5459 / 10000 [========>-------]  54.59% 1944/s 00m02s 5856 / 10000 [=========>------]  58.56% 1946/s 00m02s 6244 / 10000 [=========>------]  62.44% 1945/s 00m01s 6637 / 10000 [==========>-----]  66.37% 1946/s 00m01s 7045 / 10000 [===========>----]  70.45% 1951/s 00m01s 7423 / 10000 [===========>----]  74.23% 1948/s 00m01s 7823 / 10000 [============>---]  78.23% 1950/s 00m01s 8206 / 10000 [==================>----]  82.06% 1948/s 8606 / 10000 [===================>---]  86.06% 1950/s 9015 / 10000 [====================>--]  90.15% 1954/s 9399 / 10000 [=====================>-]  93.99% 1952/s 9813 / 10000 [=======================]  98.13% 1957/s 10000 / 10000 [======================] 100.00% 1917/s 10000 / 10000 [===================] 100.00% 1917/s 5s
  Reqs/sec      1982.97     574.58    7973.17
  Latency       50.68ms     5.13ms    91.67ms
  Latency Distribution
     50%    49.35ms
     75%    54.75ms
     90%    58.20ms
     99%    62.76ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec     21659.89    3256.18   32289.93
  Latency        4.67ms   738.31us     8.27ms
  Latency Distribution
     50%     4.67ms
     75%     5.29ms
     90%     6.04ms
     99%     7.16ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     22099.64   11438.83   77404.12
  Latency        5.00ms   662.10us     9.71ms
  Latency Distribution
     50%     4.92ms
     75%     5.52ms
     90%     6.19ms
     99%     7.88ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     11580.46    1508.41   15759.29
  Latency        8.66ms     1.55ms    15.89ms
  Latency Distribution
     50%     8.80ms
     75%    10.13ms
     90%    11.11ms
     99%    12.72ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     21064.12    6867.19   53569.09
  Latency        5.02ms     0.93ms    10.43ms
  Latency Distribution
     50%     5.04ms
     75%     5.65ms
     90%     6.34ms
     99%     8.48ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     20001.40    2375.46   28448.10
  Latency        5.05ms   633.53us     7.99ms
  Latency Distribution
     50%     4.95ms
     75%     5.64ms
     90%     6.32ms
     99%     7.50ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
 0 / 10000 [---------------------------------]   0.00% 4078 / 10000 [========>-------------]  40.78% 20346/s 8175 / 10000 [=================>----]  81.75% 20404/s 10000 / 10000 [=====================] 100.00% 16624/s 10000 / 10000 [==================] 100.00% 16622/s 0s
  Reqs/sec     20378.53    2067.17   25675.16
  Latency        4.91ms   620.83us     8.68ms
  Latency Distribution
     50%     4.71ms
     75%     5.39ms
     90%     6.14ms
     99%     7.54ms
### CBV Response Types (/cbv-response)
  Reqs/sec     21058.19    3941.17   36994.31
  Latency        4.85ms   812.03us     8.52ms
  Latency Distribution
     50%     4.98ms
     75%     5.59ms
     90%     6.29ms
     99%     7.63ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec      2618.99     287.56    4226.90
  Latency       38.08ms     2.42ms    47.63ms
  Latency Distribution
     50%    37.95ms
     75%    39.51ms
     90%    41.40ms
     99%    45.30ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     20152.64    2835.83   30518.89
  Latency        5.03ms   783.84us    21.68ms
  Latency Distribution
     50%     4.88ms
     75%     5.57ms
     90%     6.08ms
     99%     7.59ms
### File Upload (POST /upload)
 0 / 10000 [---------------------------------]   0.00% 3750 / 10000 [========>-------------]  37.50% 18636/s 7621 / 10000 [================>-----]  76.21% 18962/s 10000 / 10000 [=====================] 100.00% 16595/s 10000 / 10000 [==================] 100.00% 16593/s 0s
  Reqs/sec     18943.72    1994.83   24313.62
  Latency        5.29ms   615.23us     8.66ms
  Latency Distribution
     50%     5.11ms
     75%     5.86ms
     90%     6.47ms
     99%     7.92ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     18201.98    2297.06   23788.85
  Latency        5.50ms   781.61us     9.48ms
  Latency Distribution
     50%     5.32ms
     75%     6.03ms
     90%     6.82ms
     99%     8.75ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      1278.21   12847.29  278541.05
  Latency      117.83ms   778.22ms      7.95s
  Latency Distribution
     50%    52.23ms
     75%    57.46ms
     90%    63.16ms
     99%   141.83ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     99995.70    8699.85  108680.75
  Latency        0.98ms   338.30us     6.58ms
  Latency Distribution
     50%     0.92ms
     75%     1.19ms
     90%     1.51ms
     99%     2.35ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     94319.51    8423.39  102680.87
  Latency        1.01ms   329.65us     5.36ms
  Latency Distribution
     50%     0.94ms
     75%     1.23ms
     90%     1.57ms
     99%     2.40ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     79751.94    2585.97   82214.31
  Latency        1.23ms   391.02us     5.88ms
  Latency Distribution
     50%     1.16ms
     75%     1.47ms
     90%     1.84ms
     99%     2.85ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     89100.65    4031.50   93461.14
  Latency        1.11ms   372.89us     4.80ms
  Latency Distribution
     50%     1.03ms
     75%     1.35ms
     90%     1.73ms
     99%     2.64ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    110282.63    7872.97  118944.59
  Latency        0.89ms   344.77us     5.32ms
  Latency Distribution
     50%   809.00us
     75%     1.07ms
     90%     1.41ms
     99%     2.17ms

### Path Parameter - int (/items/12345)
  Reqs/sec    101469.43    7897.55  111266.95
  Latency        0.96ms   300.82us     5.10ms
  Latency Distribution
     50%     0.91ms
     75%     1.18ms
     90%     1.48ms
     99%     2.28ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    102064.04    8212.01  108605.42
  Latency        0.96ms   304.98us     4.68ms
  Latency Distribution
     50%     0.89ms
     75%     1.17ms
     90%     1.47ms
     99%     2.35ms

### Header Parameter (/header)
  Reqs/sec     99376.49   11444.44  113000.73
  Latency        1.01ms   355.19us     4.41ms
  Latency Distribution
     50%     0.93ms
     75%     1.24ms
     90%     1.58ms
     99%     2.65ms

### Cookie Parameter (/cookie)
  Reqs/sec     97181.39    8875.67  103374.12
  Latency        1.01ms   301.89us     5.04ms
  Latency Distribution
     50%     0.95ms
     75%     1.24ms
     90%     1.55ms
     99%     2.24ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     75642.48    7122.66   83708.26
  Latency        1.30ms   412.37us     5.89ms
  Latency Distribution
     50%     1.22ms
     75%     1.62ms
     90%     2.04ms
     99%     3.04ms

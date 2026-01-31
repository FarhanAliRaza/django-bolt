# Django-Bolt Benchmark
Generated: Sun 01 Feb 2026 01:18:19 AM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec     28258.32    1554.42   30090.65
  Latency        3.50ms     1.01ms     9.99ms
  Latency Distribution
     50%     3.33ms
     75%     4.12ms
     90%     5.15ms
     99%     7.19ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     25743.96    1309.84   27794.12
  Latency        3.85ms     1.28ms    10.71ms
  Latency Distribution
     50%     3.71ms
     75%     4.78ms
     90%     6.02ms
     99%     8.29ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     26321.22    2113.34   32178.68
  Latency        3.82ms     1.18ms    12.45ms
  Latency Distribution
     50%     3.73ms
     75%     4.64ms
     90%     5.73ms
     99%     7.88ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     27850.99    2518.46   35924.80
  Latency        3.62ms     1.16ms    10.37ms
  Latency Distribution
     50%     3.34ms
     75%     4.36ms
     90%     5.39ms
     99%     8.20ms
### Cookie Endpoint (/cookie)
  Reqs/sec     27679.06    1476.22   30037.74
  Latency        3.59ms     0.97ms     9.15ms
  Latency Distribution
     50%     3.43ms
     75%     4.20ms
     90%     5.18ms
     99%     7.17ms
### Exception Endpoint (/exc)
  Reqs/sec     27309.78    1911.29   32908.40
  Latency        3.66ms     1.00ms     9.76ms
  Latency Distribution
     50%     3.51ms
     75%     4.32ms
     90%     5.22ms
     99%     7.40ms
### HTML Response (/html)
  Reqs/sec     28242.63    1627.38   30282.02
  Latency        3.52ms     0.88ms     9.10ms
  Latency Distribution
     50%     3.34ms
     75%     4.12ms
     90%     4.96ms
     99%     6.68ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     18649.60    3200.62   25890.42
  Latency        5.41ms     1.77ms    22.09ms
  Latency Distribution
     50%     5.18ms
     75%     6.36ms
     90%     7.44ms
     99%    11.55ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     26197.72    1388.64   28708.65
  Latency        3.79ms     1.10ms     9.70ms
  Latency Distribution
     50%     3.58ms
     75%     4.49ms
     90%     5.67ms
     99%     7.63ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     13625.14   15329.08  113879.00
  Latency        8.76ms     2.85ms    22.05ms
  Latency Distribution
     50%     8.38ms
     75%    10.52ms
     90%    13.54ms
     99%    17.44ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     10161.28     819.89   13741.30
  Latency        9.84ms     2.46ms    22.80ms
  Latency Distribution
     50%     9.10ms
     75%    11.53ms
     90%    14.44ms
     99%    17.62ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     25977.37    1721.77   29981.04
  Latency        3.84ms     1.09ms     9.89ms
  Latency Distribution
     50%     3.66ms
     75%     4.55ms
     90%     5.59ms
     99%     8.09ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     27053.23    1804.55   29086.47
  Latency        3.67ms     1.00ms    10.28ms
  Latency Distribution
     50%     3.53ms
     75%     4.36ms
     90%     5.34ms
     99%     7.22ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     26337.25    1436.19   27722.30
  Latency        3.77ms     1.07ms     9.72ms
  Latency Distribution
     50%     3.59ms
     75%     4.49ms
     90%     5.53ms
     99%     7.74ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec      9449.69    1154.49   14857.64
  Latency       10.62ms     2.44ms    22.99ms
  Latency Distribution
     50%    10.60ms
     75%    12.13ms
     90%    14.28ms
     99%    17.93ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec      8622.39     639.86    9604.03
  Latency       11.53ms     5.10ms    34.73ms
  Latency Distribution
     50%     9.23ms
     75%    13.52ms
     90%    23.12ms
     99%    26.89ms
### Users Mini10 (Async) (/users/mini10)
 0 / 10000 [---------------------------------]   0.00% 1814 / 10000 [====>------------------]  18.14% 9044/s 3899 / 10000 [========>--------------]  38.99% 9729/s 6028 / 10000 [=============>--------]  60.28% 10031/s 8186 / 10000 [==================>---]  81.86% 10219/s 10000 / 10000 [======================] 100.00% 9980/s 10000 / 10000 [===================] 100.00% 9979/s 1s
  Reqs/sec     10387.37    1111.30   14381.61
  Latency        9.64ms     1.91ms    25.32ms
  Latency Distribution
     50%     9.39ms
     75%    10.66ms
     90%    12.20ms
     99%    17.36ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec      9613.83     872.54   11019.79
  Latency       10.37ms     3.70ms    28.41ms
  Latency Distribution
     50%     9.67ms
     75%    12.70ms
     90%    15.94ms
     99%    21.83ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec     27865.34    2021.55   29914.64
  Latency        3.56ms     1.06ms    11.60ms
  Latency Distribution
     50%     3.32ms
     75%     4.22ms
     90%     5.22ms
     99%     7.88ms
### Simple APIView POST (/cbv-simple)
 0 / 10000 [---------------------------------]   0.00% 5399 / 10000 [===========>----------]  53.99% 26866/s 10000 / 10000 [=====================] 100.00% 24911/s 10000 / 10000 [==================] 100.00% 24904/s 0s
  Reqs/sec     27343.63    1611.53   29355.34
  Latency        3.64ms     1.05ms    10.89ms
  Latency Distribution
     50%     3.55ms
     75%     4.35ms
     90%     5.34ms
     99%     7.16ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     23240.95    1434.63   24797.40
  Latency        4.26ms     1.34ms    11.60ms
  Latency Distribution
     50%     4.07ms
     75%     5.17ms
     90%     6.36ms
     99%     8.98ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     26901.61    1589.32   29726.62
  Latency        3.71ms     1.28ms    11.40ms
  Latency Distribution
     50%     3.39ms
     75%     4.55ms
     90%     5.76ms
     99%     8.79ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     26294.23    1565.80   28354.45
  Latency        3.77ms     1.03ms    10.43ms
  Latency Distribution
     50%     3.60ms
     75%     4.43ms
     90%     5.48ms
     99%     7.42ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     26170.02    3519.04   33454.27
  Latency        3.84ms     1.33ms    16.16ms
  Latency Distribution
     50%     3.57ms
     75%     4.52ms
     90%     5.79ms
     99%     9.21ms
### CBV Response Types (/cbv-response)
  Reqs/sec     27707.80    1676.55   30426.11
  Latency        3.58ms     0.94ms    10.42ms
  Latency Distribution
     50%     3.39ms
     75%     4.19ms
     90%     5.08ms
     99%     7.08ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     10643.45    1055.10   14518.21
  Latency        9.40ms     1.80ms    19.55ms
  Latency Distribution
     50%     9.29ms
     75%    10.65ms
     90%    12.16ms
     99%    14.81ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     26803.73    2373.21   32084.95
  Latency        3.73ms     1.17ms    10.72ms
  Latency Distribution
     50%     3.43ms
     75%     4.47ms
     90%     5.72ms
     99%     8.11ms
### File Upload (POST /upload)
  Reqs/sec     25898.59    1447.31   27494.92
  Latency        3.84ms     1.18ms    10.15ms
  Latency Distribution
     50%     3.60ms
     75%     4.57ms
     90%     5.74ms
     99%     8.24ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     26154.84    2502.34   34453.07
  Latency        3.85ms     1.19ms    10.26ms
  Latency Distribution
     50%     3.60ms
     75%     4.71ms
     90%     5.87ms
     99%     7.99ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      9441.36     915.05   10722.17
  Latency       10.55ms     2.76ms    24.31ms
  Latency Distribution
     50%    10.08ms
     75%    12.97ms
     90%    14.86ms
     99%    18.39ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    105461.11    7796.38  110314.99
  Latency        0.93ms   279.41us     3.99ms
  Latency Distribution
     50%     0.86ms
     75%     1.13ms
     90%     1.43ms
     99%     2.08ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec    103038.41   13518.70  127661.75
  Latency        1.00ms   315.38us     4.26ms
  Latency Distribution
     50%     0.93ms
     75%     1.21ms
     90%     1.53ms
     99%     2.33ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     89366.94    5709.33   95323.07
  Latency        1.10ms   333.94us     5.39ms
  Latency Distribution
     50%     1.02ms
     75%     1.35ms
     90%     1.71ms
     99%     2.46ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     98175.51   10612.48  113434.59
  Latency        1.03ms   346.85us     4.18ms
  Latency Distribution
     50%     0.94ms
     75%     1.28ms
     90%     1.64ms
     99%     2.62ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    112513.74    9239.24  120708.67
  Latency        0.87ms   343.03us     5.22ms
  Latency Distribution
     50%   802.00us
     75%     1.05ms
     90%     1.33ms
     99%     2.38ms

### Path Parameter - int (/items/12345)
  Reqs/sec    100427.99    5156.09  107714.48
  Latency        0.98ms   313.79us     3.96ms
  Latency Distribution
     50%     0.91ms
     75%     1.21ms
     90%     1.54ms
     99%     2.34ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    104001.63    8016.54  108138.50
  Latency        0.95ms   303.37us     4.30ms
  Latency Distribution
     50%     0.90ms
     75%     1.16ms
     90%     1.44ms
     99%     2.19ms

### Header Parameter (/header)
  Reqs/sec    101161.29    7563.83  108647.31
  Latency        0.97ms   335.00us     4.66ms
  Latency Distribution
     50%     0.90ms
     75%     1.19ms
     90%     1.51ms
     99%     2.47ms

### Cookie Parameter (/cookie)
  Reqs/sec     98999.93    7730.10  106152.18
  Latency        1.00ms   360.95us     5.18ms
  Latency Distribution
     50%     0.92ms
     75%     1.25ms
     90%     1.54ms
     99%     2.45ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     84233.12    7158.62   90480.82
  Latency        1.17ms   387.91us     5.62ms
  Latency Distribution
     50%     1.07ms
     75%     1.43ms
     90%     1.85ms
     99%     2.81ms

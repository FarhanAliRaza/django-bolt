# Django-Bolt Benchmark
Generated: Sat Jan  3 12:52:29 AM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    118039.82   10732.43  130360.14
  Latency      812.67us   250.43us     3.42ms
  Latency Distribution
     50%   755.00us
     75%     1.00ms
     90%     1.29ms
     99%     1.89ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     96632.83   12786.60  114487.86
  Latency        1.04ms   422.62us     6.89ms
  Latency Distribution
     50%     0.95ms
     75%     1.22ms
     90%     1.55ms
     99%     2.60ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec    100910.94   12321.06  123397.50
  Latency        1.01ms   327.86us     5.21ms
  Latency Distribution
     50%     0.93ms
     75%     1.22ms
     90%     1.55ms
     99%     2.55ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    114638.12    9717.94  119728.00
  Latency        0.86ms   292.55us     3.93ms
  Latency Distribution
     50%   800.00us
     75%     1.03ms
     90%     1.33ms
     99%     2.28ms
### Cookie Endpoint (/cookie)
  Reqs/sec    110821.09    9977.38  122105.58
  Latency        0.87ms   299.04us     6.75ms
  Latency Distribution
     50%   806.00us
     75%     1.07ms
     90%     1.35ms
     99%     2.20ms
### Exception Endpoint (/exc)
  Reqs/sec    112428.43   11579.01  121837.66
  Latency        0.88ms   318.56us     4.34ms
  Latency Distribution
     50%   785.00us
     75%     1.07ms
     90%     1.43ms
     99%     2.33ms
### HTML Response (/html)
  Reqs/sec    120487.82   13698.86  133959.33
  Latency      827.15us   301.25us     4.26ms
  Latency Distribution
     50%   753.00us
     75%     1.03ms
     90%     1.32ms
     99%     2.04ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     34348.87    9642.69   43595.48
  Latency        2.89ms     2.12ms    26.59ms
  Latency Distribution
     50%     2.31ms
     75%     3.41ms
     90%     4.85ms
     99%     9.79ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     79843.44    5522.47   88229.98
  Latency        1.24ms   413.76us     5.29ms
  Latency Distribution
     50%     1.15ms
     75%     1.48ms
     90%     1.87ms
     99%     3.21ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     18198.14    1776.46   20105.28
  Latency        5.48ms     1.54ms    15.41ms
  Latency Distribution
     50%     5.30ms
     75%     6.72ms
     90%     7.87ms
     99%    10.42ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     16423.93    1360.94   18242.42
  Latency        6.03ms     1.64ms    16.60ms
  Latency Distribution
     50%     5.79ms
     75%     7.07ms
     90%     8.53ms
     99%    11.45ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     92517.10    5615.36   97820.96
  Latency        1.06ms   359.61us     4.55ms
  Latency Distribution
     50%     0.96ms
     75%     1.35ms
     90%     1.73ms
     99%     2.61ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    104984.81    8519.27  112368.66
  Latency        0.94ms   343.12us     4.83ms
  Latency Distribution
     50%     0.87ms
     75%     1.15ms
     90%     1.45ms
     99%     2.48ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec    102682.17   10880.20  111755.35
  Latency        0.93ms   254.29us     4.44ms
  Latency Distribution
     50%     0.87ms
     75%     1.13ms
     90%     1.39ms
     99%     2.09ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     15368.76    1190.79   16993.18
  Latency        6.46ms     2.06ms    18.43ms
  Latency Distribution
     50%     6.09ms
     75%     7.67ms
     90%     9.63ms
     99%    13.63ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     13270.99    1857.16   16463.42
  Latency        7.51ms     6.13ms    74.65ms
  Latency Distribution
     50%     6.35ms
     75%     8.44ms
     90%    11.16ms
     99%    26.60ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     18025.51    1226.06   19802.80
  Latency        5.52ms     1.81ms    14.99ms
  Latency Distribution
     50%     5.24ms
     75%     6.81ms
     90%     8.38ms
     99%    11.44ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     16041.10    2247.55   20685.36
  Latency        6.25ms     3.03ms    26.50ms
  Latency Distribution
     50%     5.56ms
     75%     7.89ms
     90%    10.87ms
     99%    16.80ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    120159.39   14698.95  135165.32
  Latency      838.88us   334.16us     4.79ms
  Latency Distribution
     50%   772.00us
     75%     1.00ms
     90%     1.29ms
     99%     2.29ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    113249.02   10669.01  119256.30
  Latency        0.87ms   307.28us     4.60ms
  Latency Distribution
     50%   815.00us
     75%     1.07ms
     90%     1.35ms
     99%     2.59ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     71360.23    7198.56   77278.40
  Latency        1.39ms   420.49us     4.75ms
  Latency Distribution
     50%     1.32ms
     75%     1.68ms
     90%     2.12ms
     99%     3.24ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    105357.88    9221.78  111669.00
  Latency        0.93ms   351.77us     6.06ms
  Latency Distribution
     50%     0.85ms
     75%     1.13ms
     90%     1.44ms
     99%     2.41ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    106093.68    7726.14  114406.09
  Latency        0.92ms   311.70us     4.87ms
  Latency Distribution
     50%     0.86ms
     75%     1.12ms
     90%     1.41ms
     99%     2.28ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    100457.85   18349.63  118246.15
  Latency        1.01ms   456.39us     8.00ms
  Latency Distribution
     50%     0.91ms
     75%     1.25ms
     90%     1.62ms
     99%     3.24ms
### CBV Response Types (/cbv-response)
  Reqs/sec    111800.93    7950.47  119682.50
  Latency        0.86ms   274.36us     4.31ms
  Latency Distribution
     50%   806.00us
     75%     1.05ms
     90%     1.38ms
     99%     2.04ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     18431.69    1989.93   23334.34
  Latency        5.43ms     2.94ms    62.98ms
  Latency Distribution
     50%     4.94ms
     75%     6.32ms
     90%     8.06ms
     99%    11.51ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     85921.49   13571.59  110427.31
  Latency        1.17ms   446.47us     5.40ms
  Latency Distribution
     50%     1.05ms
     75%     1.39ms
     90%     1.91ms
     99%     3.34ms
### File Upload (POST /upload)
  Reqs/sec     61618.68    5216.99   69662.76
  Latency        1.63ms   536.36us     6.20ms
  Latency Distribution
     50%     1.51ms
     75%     1.88ms
     90%     2.50ms
     99%     4.06ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     62371.25    6994.93   68886.29
  Latency        1.58ms   561.61us     8.72ms
  Latency Distribution
     50%     1.48ms
     75%     1.83ms
     90%     2.29ms
     99%     3.95ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec     15618.56    1512.49   16697.91
  Latency        6.38ms     1.55ms    16.37ms
  Latency Distribution
     50%     6.66ms
     75%     7.35ms
     90%     8.15ms
     99%    11.31ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    116695.02   11054.32  125483.84
  Latency        0.85ms   295.76us     4.79ms
  Latency Distribution
     50%   794.00us
     75%     1.02ms
     90%     1.32ms
     99%     2.09ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec    112265.13   11416.90  118845.99
  Latency        0.89ms   348.08us     5.39ms
  Latency Distribution
     50%   809.00us
     75%     1.06ms
     90%     1.37ms
     99%     2.43ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec    100497.31    7793.79  107637.78
  Latency        0.98ms   336.29us     4.74ms
  Latency Distribution
     50%     0.89ms
     75%     1.17ms
     90%     1.49ms
     99%     2.67ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    109965.40    8732.90  118764.63
  Latency        0.89ms   279.97us     5.42ms
  Latency Distribution
     50%   814.00us
     75%     1.08ms
     90%     1.38ms
     99%     2.13ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    110245.49   34843.02  135716.63
  Latency      765.52us   231.42us     3.34ms
  Latency Distribution
     50%   687.00us
     75%     0.94ms
     90%     1.24ms
     99%     1.86ms

### Path Parameter - int (/items/12345)
  Reqs/sec    112227.62   11870.78  121856.06
  Latency      834.56us   255.18us     4.64ms
  Latency Distribution
     50%   778.00us
     75%     1.00ms
     90%     1.25ms
     99%     2.01ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    111372.35    9873.94  119768.12
  Latency        0.88ms   265.45us     5.42ms
  Latency Distribution
     50%   812.00us
     75%     1.08ms
     90%     1.36ms
     99%     2.02ms

### Header Parameter (/header)
  Reqs/sec    113630.02    9255.63  123562.90
  Latency        0.86ms   264.68us     3.81ms
  Latency Distribution
     50%   801.00us
     75%     1.06ms
     90%     1.34ms
     99%     2.06ms

### Cookie Parameter (/cookie)
  Reqs/sec    116463.86    9336.89  124583.51
  Latency      846.38us   287.25us     4.30ms
  Latency Distribution
     50%   784.00us
     75%     1.04ms
     90%     1.31ms
     99%     2.11ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec    105383.24   20997.78  146403.36
  Latency        1.01ms   343.92us     4.38ms
  Latency Distribution
     50%     0.93ms
     75%     1.25ms
     90%     1.64ms
     99%     2.54ms

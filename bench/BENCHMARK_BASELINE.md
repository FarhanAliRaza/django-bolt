# Django-Bolt Benchmark
Generated: Fri Jan  9 08:28:57 PM PKT 2026
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    112067.12   13071.81  133204.60
  Latency        0.87ms   369.26us     4.96ms
  Latency Distribution
     50%   777.00us
     75%     1.04ms
     90%     1.37ms
     99%     2.82ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     96841.17    9113.08  102665.00
  Latency        1.02ms   373.12us     5.39ms
  Latency Distribution
     50%     0.92ms
     75%     1.24ms
     90%     1.60ms
     99%     2.72ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     97428.62   10020.17  105528.99
  Latency        0.99ms   287.54us     5.77ms
  Latency Distribution
     50%     0.94ms
     75%     1.22ms
     90%     1.52ms
     99%     2.26ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    113387.69   19520.76  128638.08
  Latency      808.27us   268.08us     5.29ms
  Latency Distribution
     50%   743.00us
     75%     0.99ms
     90%     1.25ms
     99%     1.96ms
### Cookie Endpoint (/cookie)
  Reqs/sec    122068.65    8576.01  129587.46
  Latency      797.35us   233.39us     4.71ms
  Latency Distribution
     50%   742.00us
     75%     0.97ms
     90%     1.24ms
     99%     1.79ms
### Exception Endpoint (/exc)
  Reqs/sec    119855.54   12033.11  132272.13
  Latency      829.60us   249.93us     4.67ms
  Latency Distribution
     50%   769.00us
     75%     1.00ms
     90%     1.25ms
     99%     1.91ms
### HTML Response (/html)
  Reqs/sec    119740.49   13371.46  136797.18
  Latency      841.32us   297.04us     3.56ms
  Latency Distribution
     50%   748.00us
     75%     1.04ms
     90%     1.40ms
     99%     2.22ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     33773.41    9130.79   50029.78
  Latency        3.03ms     2.06ms    58.66ms
  Latency Distribution
     50%     2.56ms
     75%     3.55ms
     90%     5.11ms
     99%    11.72ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     78803.63    5878.91   84757.23
  Latency        1.24ms   415.39us     4.22ms
  Latency Distribution
     50%     1.13ms
     75%     1.56ms
     90%     2.03ms
     99%     3.06ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     18592.20    2387.95   26710.27
  Latency        5.43ms     1.24ms    15.22ms
  Latency Distribution
     50%     5.44ms
     75%     6.31ms
     90%     7.10ms
     99%     9.88ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     16796.27    1118.44   17994.62
  Latency        5.90ms     1.51ms    12.97ms
  Latency Distribution
     50%     5.84ms
     75%     7.08ms
     90%     8.19ms
     99%    10.63ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     86450.97    7899.52   96955.18
  Latency        1.12ms   342.66us     3.88ms
  Latency Distribution
     50%     1.05ms
     75%     1.43ms
     90%     1.88ms
     99%     2.55ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec    100725.65    8637.21  110064.22
  Latency        0.97ms   252.47us     3.88ms
  Latency Distribution
     50%     0.94ms
     75%     1.24ms
     90%     1.48ms
     99%     2.05ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     92230.99   17166.38  111814.78
  Latency        1.10ms   591.27us    11.73ms
  Latency Distribution
     50%     0.97ms
     75%     1.39ms
     90%     1.76ms
     99%     3.77ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     14674.71    3736.50   18815.42
  Latency        6.44ms     2.03ms    38.38ms
  Latency Distribution
     50%     6.48ms
     75%     7.67ms
     90%     8.73ms
     99%    11.38ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec     13951.47    2011.16   22237.44
  Latency        7.23ms     4.62ms    63.18ms
  Latency Distribution
     50%     6.84ms
     75%     8.30ms
     90%    10.06ms
     99%    13.67ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     17855.72    1153.38   19185.05
  Latency        5.57ms     2.31ms    56.16ms
  Latency Distribution
     50%     5.50ms
     75%     6.66ms
     90%     7.74ms
     99%    10.10ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     15748.07    2179.82   22141.99
  Latency        6.35ms     3.24ms    71.68ms
  Latency Distribution
     50%     5.83ms
     75%     7.75ms
     90%     9.87ms
     99%    13.74ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    125302.35   12997.30  133989.58
  Latency      767.97us   196.04us     3.28ms
  Latency Distribution
     50%   722.00us
     75%     0.94ms
     90%     1.17ms
     99%     1.67ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec    118163.75    8489.89  125329.18
  Latency      829.86us   239.60us     3.70ms
  Latency Distribution
     50%   774.00us
     75%     1.01ms
     90%     1.27ms
     99%     2.01ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     74792.44    6320.18   79177.12
  Latency        1.32ms   395.90us     5.59ms
  Latency Distribution
     50%     1.22ms
     75%     1.62ms
     90%     2.03ms
     99%     3.07ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec    108269.17    6900.35  114108.08
  Latency        0.90ms   292.70us     5.56ms
  Latency Distribution
     50%   836.00us
     75%     1.12ms
     90%     1.43ms
     99%     2.25ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec    109195.01    7070.07  116494.40
  Latency        0.89ms   256.82us     4.72ms
  Latency Distribution
     50%   837.00us
     75%     1.08ms
     90%     1.33ms
     99%     1.96ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec    114365.55    8255.72  119732.95
  Latency        0.85ms   252.84us     5.63ms
  Latency Distribution
     50%   798.00us
     75%     1.04ms
     90%     1.28ms
     99%     1.89ms
### CBV Response Types (/cbv-response)
  Reqs/sec    120039.75   11208.19  127552.06
  Latency      806.36us   214.26us     3.60ms
  Latency Distribution
     50%   752.00us
     75%     1.00ms
     90%     1.26ms
     99%     1.79ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     18625.84    1505.32   19950.68
  Latency        5.33ms     1.94ms    15.15ms
  Latency Distribution
     50%     4.95ms
     75%     6.79ms
     90%     8.46ms
     99%    11.86ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec    111784.16    9917.03  116676.80
  Latency        0.88ms   323.60us     4.43ms
  Latency Distribution
     50%   825.00us
     75%     1.06ms
     90%     1.32ms
     99%     2.15ms
### File Upload (POST /upload)
  Reqs/sec    100691.12    6515.29  105142.99
  Latency        0.98ms   284.93us     3.75ms
  Latency Distribution
     50%     0.91ms
     75%     1.21ms
     90%     1.51ms
     99%     2.31ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     98724.87    7960.43  105025.86
  Latency        1.00ms   303.98us     4.28ms
  Latency Distribution
     50%     0.94ms
     75%     1.20ms
     90%     1.51ms
     99%     2.29ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec     14298.06    4087.20   17840.67
  Latency        6.72ms     5.90ms    79.91ms
  Latency Distribution
     50%     6.31ms
     75%     7.29ms
     90%     8.40ms
     99%    13.76ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec    117552.96    9037.38  123241.20
  Latency      840.50us   278.63us     4.44ms
  Latency Distribution
     50%   763.00us
     75%     1.05ms
     90%     1.38ms
     99%     2.04ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec    109212.73   10175.88  117319.79
  Latency        0.89ms   264.39us     6.01ms
  Latency Distribution
     50%   845.00us
     75%     1.12ms
     90%     1.44ms
     99%     2.00ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec    103525.73    7566.89  109069.56
  Latency        0.94ms   279.16us     4.34ms
  Latency Distribution
     50%     0.88ms
     75%     1.14ms
     90%     1.47ms
     99%     2.24ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec    109927.01    6283.23  117244.61
  Latency        0.88ms   260.39us     5.18ms
  Latency Distribution
     50%   820.00us
     75%     1.07ms
     90%     1.36ms
     99%     2.06ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec    130982.43   11311.69  136756.88
  Latency      750.98us   258.36us     4.99ms
  Latency Distribution
     50%   694.00us
     75%     0.92ms
     90%     1.11ms
     99%     1.77ms

### Path Parameter - int (/items/12345)
  Reqs/sec    118630.44   14131.19  127424.52
  Latency      811.08us   281.17us     8.21ms
  Latency Distribution
     50%   755.00us
     75%     1.01ms
     90%     1.26ms
     99%     1.82ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec    123028.43   15095.20  143101.97
  Latency      821.95us   265.38us     4.85ms
  Latency Distribution
     50%   765.00us
     75%     1.00ms
     90%     1.22ms
     99%     1.96ms

### Header Parameter (/header)
  Reqs/sec    120918.09   14153.41  134170.88
  Latency      821.76us   283.66us     5.34ms
  Latency Distribution
     50%   754.00us
     75%     1.01ms
     90%     1.26ms
     99%     2.05ms

### Cookie Parameter (/cookie)
  Reqs/sec    122995.14   10387.10  131506.87
  Latency      806.45us   244.52us     4.24ms
  Latency Distribution
     50%   764.00us
     75%     0.97ms
     90%     1.21ms
     99%     1.88ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     98945.71    7089.64  103580.46
  Latency        0.98ms   276.85us     3.69ms
  Latency Distribution
     50%     0.94ms
     75%     1.21ms
     90%     1.52ms
     99%     2.22ms

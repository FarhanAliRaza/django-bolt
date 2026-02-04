# Django-Bolt Benchmark
Generated: Wed 04 Feb 2026 10:24:13 PM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec    106477.71    8829.22  113311.10
  Latency        0.93ms   348.56us     5.34ms
  Latency Distribution
     50%     0.85ms
     75%     1.14ms
     90%     1.46ms
     99%     2.42ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     88632.77    6271.16   93200.43
  Latency        1.11ms   366.57us     4.82ms
  Latency Distribution
     50%     1.03ms
     75%     1.34ms
     90%     1.69ms
     99%     2.97ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     90166.46    6519.38   95881.09
  Latency        1.10ms   346.46us     4.97ms
  Latency Distribution
     50%     1.02ms
     75%     1.33ms
     90%     1.73ms
     99%     2.55ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec    103199.60    8667.56  109417.44
  Latency        0.95ms   311.85us     4.61ms
  Latency Distribution
     50%     0.88ms
     75%     1.16ms
     90%     1.48ms
     99%     2.33ms
### Cookie Endpoint (/cookie)
  Reqs/sec    100814.82    5473.50  105985.46
  Latency        0.97ms   337.49us     5.74ms
  Latency Distribution
     50%     0.90ms
     75%     1.19ms
     90%     1.51ms
     99%     2.53ms
### Exception Endpoint (/exc)
  Reqs/sec     90988.16    6361.09   99007.30
  Latency        1.09ms   416.91us     5.34ms
  Latency Distribution
     50%     0.99ms
     75%     1.34ms
     90%     1.72ms
     99%     2.98ms
### HTML Response (/html)
  Reqs/sec    106179.82    8520.32  113131.15
  Latency        0.93ms   324.18us     4.50ms
  Latency Distribution
     50%   847.00us
     75%     1.15ms
     90%     1.49ms
     99%     2.33ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     31607.94    7324.18   37693.42
  Latency        3.16ms     1.59ms    21.73ms
  Latency Distribution
     50%     2.81ms
     75%     3.65ms
     90%     4.72ms
     99%    10.34ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
  Reqs/sec     65743.44   11385.50   79954.38
  Latency        1.48ms   615.31us    10.51ms
  Latency Distribution
     50%     1.33ms
     75%     1.76ms
     90%     2.29ms
     99%     4.12ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
  Reqs/sec     16935.56    1629.76   18858.61
  Latency        5.86ms     1.94ms    16.97ms
  Latency Distribution
     50%     5.74ms
     75%     7.41ms
     90%     8.79ms
     99%    11.80ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec     15969.77    1307.35   20101.10
  Latency        6.29ms     2.07ms    21.39ms
  Latency Distribution
     50%     6.09ms
     75%     7.88ms
     90%     9.48ms
     99%    12.46ms
### Get Auth Context (/auth/context) validated jwt no db
  Reqs/sec     83442.61    6735.94   90370.79
  Latency        1.18ms   424.41us     5.61ms
  Latency Distribution
     50%     1.08ms
     75%     1.46ms
     90%     1.94ms
     99%     3.05ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     84785.31    7539.84   96608.94
  Latency        1.15ms   470.22us     5.58ms
  Latency Distribution
     50%     1.04ms
     75%     1.42ms
     90%     1.82ms
     99%     3.67ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     76053.76    6237.32   83213.06
  Latency        1.28ms   476.61us     7.17ms
  Latency Distribution
     50%     1.15ms
     75%     1.63ms
     90%     2.14ms
     99%     3.29ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
  Reqs/sec     14623.92    1352.01   17957.44
  Latency        6.83ms     1.97ms    19.85ms
  Latency Distribution
     50%     6.54ms
     75%     8.14ms
     90%     9.68ms
     99%    13.28ms
### Users Full10 (Sync) (/users/sync-full10)
 0 / 10000 [---------------------------------------------------------------------------------------------------------------------------------------------]   0.00% 2599 / 10000 [=================================>------------------------------------------------------------------------------------------------]  25.99% 12953/s 5223 / 10000 [===================================================================>--------------------------------------------------------------]  52.23% 13023/s 7851 / 10000 [======================================================================================================>---------------------------]  78.51% 13054/s 10000 / 10000 [=================================================================================================================================] 100.00% 12459/s 10000 / 10000 [==============================================================================================================================] 100.00% 12457/s 0s
  Reqs/sec     13026.74     771.19   14168.37
  Latency        7.61ms     2.41ms    18.48ms
  Latency Distribution
     50%     7.36ms
     75%     9.63ms
     90%    11.37ms
     99%    14.81ms
### Users Mini10 (Async) (/users/mini10)
  Reqs/sec     17284.91    1515.89   24055.84
  Latency        5.82ms     1.48ms    13.20ms
  Latency Distribution
     50%     5.61ms
     75%     6.91ms
     90%     8.15ms
     99%    10.60ms
### Users Mini10 (Sync) (/users/sync-mini10)
  Reqs/sec     14273.00    1726.45   17102.50
  Latency        6.96ms     2.62ms    22.85ms
  Latency Distribution
     50%     6.49ms
     75%     8.50ms
     90%    10.89ms
     99%    15.97ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec    107521.75   10267.04  116444.22
  Latency        0.91ms   331.71us     4.77ms
  Latency Distribution
     50%   840.00us
     75%     1.11ms
     90%     1.42ms
     99%     2.31ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     91259.08   17291.43  104726.25
  Latency        1.01ms   337.99us     5.22ms
  Latency Distribution
     50%     0.92ms
     75%     1.23ms
     90%     1.58ms
     99%     2.54ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     60027.19    9851.66   74754.31
  Latency        1.67ms   722.79us     9.60ms
  Latency Distribution
     50%     1.49ms
     75%     1.94ms
     90%     2.61ms
     99%     4.74ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     98093.24    5048.89  103944.49
  Latency        1.00ms   347.51us     5.61ms
  Latency Distribution
     50%     0.92ms
     75%     1.22ms
     90%     1.58ms
     99%     2.51ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     94460.81    5280.78   99373.77
  Latency        1.04ms   360.12us     4.54ms
  Latency Distribution
     50%     0.95ms
     75%     1.29ms
     90%     1.69ms
     99%     2.61ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     93209.31   10133.42   99454.97
  Latency        1.05ms   359.09us     6.05ms
  Latency Distribution
     50%     0.96ms
     75%     1.29ms
     90%     1.66ms
     99%     2.63ms
### CBV Response Types (/cbv-response)
  Reqs/sec     96262.25    5366.62  103020.33
  Latency        1.01ms   341.35us     7.09ms
  Latency Distribution
     50%     0.95ms
     75%     1.26ms
     90%     1.59ms
     99%     2.37ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
  Reqs/sec     17547.88    1394.24   20281.01
  Latency        5.69ms     1.48ms    13.69ms
  Latency Distribution
     50%     5.52ms
     75%     6.67ms
     90%     7.88ms
     99%    10.57ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     94551.99    8607.90  102860.77
  Latency        1.05ms   391.36us     4.84ms
  Latency Distribution
     50%     0.96ms
     75%     1.27ms
     90%     1.62ms
     99%     2.63ms
### File Upload (POST /upload)
  Reqs/sec     88785.74    7533.13   96266.46
  Latency        1.09ms   349.23us     6.21ms
  Latency Distribution
     50%     1.02ms
     75%     1.35ms
     90%     1.70ms
     99%     2.49ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     86339.52    6930.51   92841.16
  Latency        1.14ms   372.80us     5.70ms
  Latency Distribution
     50%     1.07ms
     75%     1.47ms
     90%     1.84ms
     99%     2.66ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering

# Django-Bolt Benchmark
Generated: Mon 23 Feb 2026 01:09:28 AM PKT
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
  Reqs/sec     22977.10    2464.92   25962.25
  Latency        4.34ms   702.19us     8.24ms
  Latency Distribution
     50%     4.58ms
     75%     5.06ms
     90%     5.45ms
     99%     6.84ms

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
  Reqs/sec     16902.99    1868.47   20001.87
  Latency        5.92ms     1.06ms    12.32ms
  Latency Distribution
     50%     6.31ms
     75%     6.96ms
     90%     7.61ms
     99%     8.92ms
### 10kb JSON (Sync) (/sync-10k-json)
  Reqs/sec     18035.79    2799.91   30730.07
  Latency        5.64ms   827.55us    11.24ms
  Latency Distribution
     50%     5.93ms
     75%     6.49ms
     90%     6.97ms
     99%     8.03ms

## Response Type Endpoints
### Header Endpoint (/header)
  Reqs/sec     22029.06    2371.79   27602.91
  Latency        4.54ms   703.08us     8.88ms
  Latency Distribution
     50%     4.84ms
     75%     5.30ms
     90%     5.67ms
     99%     6.93ms
### Cookie Endpoint (/cookie)
  Reqs/sec     22298.85    2517.73   28878.07
  Latency        4.50ms   726.59us     9.66ms
  Latency Distribution
     50%     4.83ms
     75%     5.27ms
     90%     5.69ms
     99%     7.01ms
### Exception Endpoint (/exc)
  Reqs/sec     19859.25    2782.08   30534.28
  Latency        5.09ms   723.14us     9.78ms
  Latency Distribution
     50%     5.02ms
     75%     5.72ms
     90%     6.29ms
     99%     7.80ms
### HTML Response (/html)
  Reqs/sec     22344.76    2243.96   29137.13
  Latency        4.49ms   601.92us     8.49ms
  Latency Distribution
     50%     4.54ms
     75%     5.02ms
     90%     5.47ms
     99%     6.58ms
### Redirect Response (/redirect)
### File Static via FileResponse (/file-static)
  Reqs/sec     11519.61    3921.40   34218.81
  Latency        9.01ms     1.62ms    25.88ms
  Latency Distribution
     50%     8.67ms
     75%     9.34ms
     90%    10.15ms
     99%    17.68ms

## Authentication & Authorization Performance
### Auth NO User Access (/auth/no-user-access) - lazy loading, no DB query
 0 / 10000 [-----------------------------------]   0.00% 3597 / 10000 [========>---------------]  35.97% 17926/s 7450 / 10000 [=================>------]  74.50% 18580/s 10000 / 10000 [=======================] 100.00% 16630/s 10000 / 10000 [====================] 100.00% 16628/s 0s
  Reqs/sec     19134.84    2335.46   26902.65
  Latency        5.26ms   772.52us    10.07ms
  Latency Distribution
     50%     5.83ms
     75%     6.21ms
     90%     6.60ms
     99%     7.46ms
### Get Authenticated User (/auth/me) - accesses request.user, triggers DB query
 0 / 10000 [-----------------------------------]   0.00% 512 / 10000 [>------------------]   5.12% 2552/s 00m03s 1098 / 10000 [=>----------------]  10.98% 2734/s 00m03s 1679 / 10000 [===>--------------]  16.79% 2790/s 00m02s 2286 / 10000 [====>-------------]  22.86% 2850/s 00m02s 2950 / 10000 [=====>------------]  29.50% 2942/s 00m02s 3605 / 10000 [======>-----------]  36.05% 2995/s 00m02s 4263 / 10000 [=======>----------]  42.63% 3037/s 00m01s 4906 / 10000 [========>---------]  49.06% 3058/s 00m01s 5493 / 10000 [=========>--------]  54.93% 3043/s 00m01s 6162 / 10000 [===========>------]  61.62% 3071/s 00m01s 6860 / 10000 [============>-----]  68.60% 3108/s 00m01s 7500 / 10000 [==================>------]  75.00% 3115/s 8143 / 10000 [====================>----]  81.43% 3123/s 8790 / 10000 [=====================>---]  87.90% 3130/s 9450 / 10000 [=======================>-]  94.50% 3141/s 10000 / 10000 [========================] 100.00% 3115/s 10000 / 10000 [=====================] 100.00% 3115/s 3s
  Reqs/sec      3165.24     603.85    7733.36
  Latency       31.58ms     4.36ms    63.99ms
  Latency Distribution
     50%    30.76ms
     75%    35.17ms
     90%    37.55ms
     99%    42.01ms
### Get User via Dependency (/auth/me-dependency)
  Reqs/sec      2553.12     824.68    9187.34
  Latency       39.32ms     5.28ms    75.61ms
  Latency Distribution
     50%    37.95ms
     75%    44.44ms
     90%    47.32ms
     99%    50.92ms
### Get Auth Context (/auth/context) validated jwt no db
 0 / 10000 [-----------------------------------]   0.00% 3388 / 10000 [========>---------------]  33.88% 16840/s 7050 / 10000 [================>-------]  70.50% 17523/s 10000 / 10000 [=======================] 100.00% 16579/s 10000 / 10000 [====================] 100.00% 16577/s 0s
  Reqs/sec     17874.16    2463.43   23702.22
  Latency        5.59ms     0.97ms    13.22ms
  Latency Distribution
     50%     6.01ms
     75%     6.43ms
     90%     7.04ms
     99%     9.22ms

## Items GET Performance (/items/1?q=hello)
  Reqs/sec     20451.99    3052.11   28517.73
  Latency        4.91ms     0.95ms     9.59ms
  Latency Distribution
     50%     5.09ms
     75%     5.75ms
     90%     6.41ms
     99%     8.68ms

## Items PUT JSON Performance (/items/1)
  Reqs/sec     20042.02    1708.70   22844.47
  Latency        4.98ms   548.50us     8.21ms
  Latency Distribution
     50%     4.86ms
     75%     5.51ms
     90%     6.08ms
     99%     7.24ms

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
 0 / 10000 [-----------------------------------]   0.00% 413 / 10000 [>------------------]   4.13% 2057/s 00m04s 875 / 10000 [=>-----------------]   8.75% 2180/s 00m04s 1308 / 10000 [==>---------------]  13.08% 2174/s 00m03s 1757 / 10000 [===>--------------]  17.57% 2190/s 00m03s 2214 / 10000 [===>--------------]  22.14% 2208/s 00m03s 2665 / 10000 [====>-------------]  26.65% 2215/s 00m03s 3124 / 10000 [=====>------------]  31.24% 2226/s 00m03s 3570 / 10000 [======>-----------]  35.70% 2225/s 00m02s 4007 / 10000 [=======>----------]  40.07% 2220/s 00m02s 4465 / 10000 [========>---------]  44.65% 2227/s 00m02s 4914 / 10000 [========>---------]  49.14% 2228/s 00m02s 5370 / 10000 [=========>--------]  53.70% 2232/s 00m02s 5817 / 10000 [==========>-------]  58.17% 2232/s 00m01s 6263 / 10000 [===========>------]  62.63% 2232/s 00m01s 6715 / 10000 [============>-----]  67.15% 2233/s 00m01s 7173 / 10000 [============>-----]  71.73% 2236/s 00m01s 7637 / 10000 [=============>----]  76.37% 2241/s 00m01s 8090 / 10000 [====================>----]  80.90% 2242/s 8529 / 10000 [=====================>---]  85.29% 2240/s 8985 / 10000 [======================>--]  89.85% 2241/s 9440 / 10000 [=======================>-]  94.40% 2243/s 9890 / 10000 [=========================]  98.90% 2243/s 10000 / 10000 [========================] 100.00% 2169/s 10000 / 10000 [=====================] 100.00% 2169/s 4s
  Reqs/sec      2252.60     214.51    3686.20
  Latency       44.26ms     2.47ms    59.73ms
  Latency Distribution
     50%    44.12ms
     75%    45.20ms
     90%    46.62ms
     99%    52.41ms
### Users Full10 (Sync) (/users/sync-full10)
  Reqs/sec      1601.36    1146.16   11424.25
  Latency       63.35ms    11.41ms   108.44ms
  Latency Distribution
     50%    68.04ms
     75%    73.02ms
     90%    76.47ms
     99%    82.08ms
### Users Mini10 (Async) (/users/mini10)
 0 / 10000 [-----------------------------------]   0.00% 473 / 10000 [>------------------]   4.73% 2359/s 00m04s 993 / 10000 [=>-----------------]   9.93% 2477/s 00m03s 1485 / 10000 [==>---------------]  14.85% 2470/s 00m03s 2009 / 10000 [===>--------------]  20.09% 2507/s 00m03s 2551 / 10000 [====>-------------]  25.51% 2546/s 00m02s 3076 / 10000 [=====>------------]  30.76% 2559/s 00m02s 3604 / 10000 [======>-----------]  36.04% 2570/s 00m02s 4114 / 10000 [=======>----------]  41.14% 2567/s 00m02s 4622 / 10000 [========>---------]  46.22% 2564/s 00m02s 5145 / 10000 [=========>--------]  51.45% 2568/s 00m01s 5671 / 10000 [==========>-------]  56.71% 2573/s 00m01s 6182 / 10000 [===========>------]  61.82% 2572/s 00m01s 6709 / 10000 [============>-----]  67.09% 2576/s 00m01s 7203 / 10000 [============>-----]  72.03% 2568/s 00m01s 7710 / 10000 [===================>-----]  77.10% 2566/s 8239 / 10000 [====================>----]  82.39% 2571/s 8750 / 10000 [=====================>---]  87.50% 2569/s 9258 / 10000 [=======================>-]  92.58% 2568/s 9755 / 10000 [=========================]  97.55% 2563/s 10000 / 10000 [========================] 100.00% 2496/s 10000 / 10000 [=====================] 100.00% 2496/s 4s
  Reqs/sec      2578.13     283.51    4623.96
  Latency       38.70ms     2.29ms    56.07ms
  Latency Distribution
     50%    38.48ms
     75%    39.85ms
     90%    41.31ms
     99%    45.31ms
### Users Mini10 (Sync) (/users/sync-mini10)
 0 / 10000 [-----------------------------------]   0.00% 313 / 10000 [>------------------]   3.13% 1559/s 00m06s 706 / 10000 [=>-----------------]   7.06% 1760/s 00m05s 1099 / 10000 [=>----------------]  10.99% 1826/s 00m04s 1498 / 10000 [==>---------------]  14.98% 1868/s 00m04s 1898 / 10000 [===>--------------]  18.98% 1894/s 00m04s 2286 / 10000 [====>-------------]  22.86% 1900/s 00m04s 2688 / 10000 [====>-------------]  26.88% 1915/s 00m03s 3083 / 10000 [=====>------------]  30.83% 1922/s 00m03s 3479 / 10000 [======>-----------]  34.79% 1928/s 00m03s 3874 / 10000 [======>-----------]  38.74% 1932/s 00m03s 4273 / 10000 [=======>----------]  42.73% 1938/s 00m02s 4670 / 10000 [========>---------]  46.70% 1941/s 00m02s 5034 / 10000 [=========>--------]  50.34% 1932/s 00m02s 5423 / 10000 [=========>--------]  54.23% 1933/s 00m02s 5830 / 10000 [==========>-------]  58.30% 1939/s 00m02s 6219 / 10000 [===========>------]  62.19% 1939/s 00m01s 6619 / 10000 [===========>------]  66.19% 1943/s 00m01s 7020 / 10000 [============>-----]  70.20% 1946/s 00m01s 7415 / 10000 [=============>----]  74.15% 1947/s 00m01s 7812 / 10000 [==============>---]  78.12% 1949/s 00m01s 8178 / 10000 [====================>----]  81.78% 1943/s 8577 / 10000 [=====================>---]  85.77% 1945/s 8968 / 10000 [======================>--]  89.68% 1946/s 9405 / 10000 [=======================>-]  94.05% 1955/s 9745 / 10000 [=========================]  97.45% 1945/s 10000 / 10000 [========================] 100.00% 1919/s 10000 / 10000 [=====================] 100.00% 1919/s 5s
  Reqs/sec      1977.53     787.94    8419.18
  Latency       50.87ms     7.74ms    91.47ms
  Latency Distribution
     50%    48.73ms
     75%    57.32ms
     90%    60.19ms
     99%    79.97ms
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
  Reqs/sec     22923.00    7602.54   57476.68
  Latency        4.62ms   757.64us     8.27ms
  Latency Distribution
     50%     4.87ms
     75%     5.40ms
     90%     6.02ms
     99%     6.97ms
### Simple APIView POST (/cbv-simple)
  Reqs/sec     20488.75    2180.61   26970.93
  Latency        4.90ms   625.06us     9.22ms
  Latency Distribution
     50%     4.79ms
     75%     5.43ms
     90%     6.05ms
     99%     7.45ms
### Items100 ViewSet GET (/cbv-items100)
  Reqs/sec     11923.91    1332.79   14678.27
  Latency        8.38ms     1.54ms    14.50ms
  Latency Distribution
     50%     8.97ms
     75%    10.00ms
     90%    10.75ms
     99%    12.34ms

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
  Reqs/sec     20354.56    2125.80   24585.37
  Latency        4.92ms     0.88ms     9.78ms
  Latency Distribution
     50%     5.21ms
     75%     5.68ms
     90%     6.48ms
     99%     7.68ms
### CBV Items PUT (Update) (/cbv-items/1)
  Reqs/sec     19939.11    2721.52   26624.52
  Latency        5.05ms   697.03us     9.56ms
  Latency Distribution
     50%     4.87ms
     75%     5.53ms
     90%     6.34ms
     99%     7.94ms

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
  Reqs/sec     21305.89    2195.12   28325.84
  Latency        4.71ms   467.99us     8.06ms
  Latency Distribution
     50%     4.52ms
     75%     5.24ms
     90%     5.57ms
     99%     6.70ms
### CBV Response Types (/cbv-response)
  Reqs/sec     21823.64    3221.48   33469.41
  Latency        4.65ms   792.84us     8.58ms
  Latency Distribution
     50%     4.95ms
     75%     5.40ms
     90%     5.94ms
     99%     7.43ms

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
 0 / 10000 [-----------------------------------]   0.00% 533 / 10000 [=>-----------------]   5.33% 2658/s 00m03s 1058 / 10000 [=>----------------]  10.58% 2640/s 00m03s 1601 / 10000 [==>---------------]  16.01% 2664/s 00m03s 2150 / 10000 [===>--------------]  21.50% 2683/s 00m02s 2701 / 10000 [====>-------------]  27.01% 2696/s 00m02s 3250 / 10000 [=====>------------]  32.50% 2704/s 00m02s 3807 / 10000 [======>-----------]  38.07% 2715/s 00m02s 4371 / 10000 [=======>----------]  43.71% 2727/s 00m02s 4923 / 10000 [========>---------]  49.23% 2731/s 00m01s 5474 / 10000 [=========>--------]  54.74% 2733/s 00m01s 6019 / 10000 [==========>-------]  60.19% 2732/s 00m01s 6566 / 10000 [===========>------]  65.66% 2732/s 00m01s 7070 / 10000 [============>-----]  70.70% 2715/s 00m01s 7628 / 10000 [===================>-----]  76.28% 2720/s 8169 / 10000 [====================>----]  81.69% 2719/s 8727 / 10000 [=====================>---]  87.27% 2723/s 9285 / 10000 [=======================>-]  92.85% 2727/s 9813 / 10000 [=========================]  98.13% 2722/s 10000 / 10000 [========================] 100.00% 2628/s 10000 / 10000 [=====================] 100.00% 2628/s 3s
  Reqs/sec      2735.95     297.41    4235.89
  Latency       36.46ms     2.44ms    51.91ms
  Latency Distribution
     50%    36.27ms
     75%    37.42ms
     90%    38.83ms
     99%    44.25ms
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
  Reqs/sec     20187.90    2683.01   31329.97
  Latency        5.03ms   550.42us     7.93ms
  Latency Distribution
     50%     4.88ms
     75%     5.58ms
     90%     6.17ms
     99%     7.19ms
### File Upload (POST /upload)
  Reqs/sec     17084.71    1936.49   22765.33
  Latency        5.87ms   725.50us     9.74ms
  Latency Distribution
     50%     5.63ms
     75%     6.50ms
     90%     7.21ms
     99%     8.99ms
### Mixed Form with Files (POST /mixed-form)
  Reqs/sec     17868.37    4869.83   42142.91
  Latency        5.82ms   736.99us    10.75ms
  Latency Distribution
     50%     5.58ms
     75%     6.45ms
     90%     7.15ms
     99%     9.03ms

## Django Middleware Performance
### Django Middleware + Messages Framework (/middleware/demo)
Tests: SessionMiddleware, AuthenticationMiddleware, MessageMiddleware, custom middleware, template rendering
  Reqs/sec      1867.97     809.06    5783.80
  Latency       53.63ms    13.30ms   151.13ms
  Latency Distribution
     50%    50.49ms
     75%    54.76ms
     90%    59.58ms
     99%   118.54ms

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
  Reqs/sec     20541.32    1750.19   23536.45
  Latency        4.86ms   533.48us     8.26ms
  Latency Distribution
     50%     4.79ms
     75%     5.39ms
     90%     5.90ms
     99%     6.87ms

## Serializer Performance Benchmarks
### Raw msgspec Serializer (POST /bench/serializer-raw)
  Reqs/sec     19410.99    1499.78   22148.16
  Latency        5.14ms   560.46us     8.59ms
  Latency Distribution
     50%     5.01ms
     75%     5.64ms
     90%     6.24ms
     99%     7.21ms
### Django-Bolt Serializer with Validators (POST /bench/serializer-validated)
  Reqs/sec     16936.17    2448.36   21316.03
  Latency        5.91ms     0.90ms    11.18ms
  Latency Distribution
     50%     5.71ms
     75%     6.56ms
     90%     7.57ms
     99%     9.41ms
### Users msgspec Serializer (POST /users/bench/msgspec)
  Reqs/sec     20207.80    1627.77   23415.54
  Latency        4.94ms   527.24us     8.12ms
  Latency Distribution
     50%     4.80ms
     75%     5.51ms
     90%     5.98ms
     99%     6.80ms

## Latency Percentile Benchmarks
Measures p50/p75/p90/p99 latency for type coercion overhead analysis

### Baseline - No Parameters (/)
  Reqs/sec     22190.31    3300.87   29860.98
  Latency        4.52ms     0.90ms    10.12ms
  Latency Distribution
     50%     4.76ms
     75%     5.18ms
     90%     5.88ms
     99%     8.51ms

### Path Parameter - int (/items/12345)
 0 / 10000 [-----------------------------------]   0.00% 4099 / 10000 [=========>--------------]  40.99% 20446/s 8460 / 10000 [====================>---]  84.60% 21098/s 10000 / 10000 [=======================] 100.00% 16635/s 10000 / 10000 [====================] 100.00% 16632/s 0s
  Reqs/sec     22079.57    4461.71   40917.38
  Latency        4.65ms   769.01us     9.22ms
  Latency Distribution
     50%     4.74ms
     75%     5.28ms
     90%     5.95ms
     99%     7.24ms

### Path + Query Parameters (/items/12345?q=hello)
  Reqs/sec     21508.91    2583.69   30603.28
  Latency        4.68ms   655.76us    10.45ms
  Latency Distribution
     50%     4.63ms
     75%     5.27ms
     90%     5.88ms
     99%     7.36ms

### Header Parameter (/header)
  Reqs/sec     21901.86    4067.25   36445.11
  Latency        4.65ms     0.92ms     9.80ms
  Latency Distribution
     50%     4.90ms
     75%     5.33ms
     90%     5.96ms
     99%     8.64ms

### Cookie Parameter (/cookie)
 0 / 10000 [-----------------------------------]   0.00% 3990 / 10000 [=========>--------------]  39.90% 19862/s 8306 / 10000 [===================>----]  83.06% 20688/s 10000 / 10000 [=======================] 100.00% 16610/s 10000 / 10000 [====================] 100.00% 16607/s 0s
  Reqs/sec     21194.73    2473.96   27487.78
  Latency        4.73ms   750.94us    10.97ms
  Latency Distribution
     50%     4.72ms
     75%     5.34ms
     90%     5.80ms
     99%     7.33ms

### Auth Context - JWT validated, no DB (/auth/context)
  Reqs/sec     17387.57    1864.74   19735.90
  Latency        5.75ms     1.06ms    11.79ms
  Latency Distribution
     50%     6.16ms
     75%     6.72ms
     90%     7.39ms
     99%     9.94ms

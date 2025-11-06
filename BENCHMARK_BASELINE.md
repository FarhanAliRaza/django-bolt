# Django-Bolt Benchmark
Generated: Thu Nov  6 11:09:38 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    56270.50 [#/sec] (mean)
Time per request:       1.777 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    73410.66 [#/sec] (mean)
Time per request:       1.362 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    77904.68 [#/sec] (mean)
Time per request:       1.284 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    93144.56 [#/sec] (mean)
Time per request:       1.074 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    94663.80 [#/sec] (mean)
Time per request:       1.056 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    89770.64 [#/sec] (mean)
Time per request:       1.114 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    63809.29 [#/sec] (mean)
Time per request:       1.567 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    98531.88 [#/sec] (mean)
Time per request:       1.015 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    24322.67 [#/sec] (mean)
Time per request:       4.111 [ms] (mean)
Time per request:       0.041 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (Async) (/stream)
  Total:	0.2381 secs
  Slowest:	0.0128 secs
  Fastest:	0.0001 secs
  Average:	0.0023 secs
  Requests/sec:	42003.2490
Status code distribution:
### Streaming Plain Text (Sync) (/sync-stream)
  Total:	0.3179 secs
  Slowest:	0.0234 secs
  Fastest:	0.0001 secs
  Average:	0.0030 secs
  Requests/sec:	31459.0036
Status code distribution:
### Server-Sent Events (Async) (/sse)
  Total:	0.2119 secs
  Slowest:	0.0103 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	47199.9133
Status code distribution:
### Server-Sent Events (Sync) (/sync-sse)
  Total:	0.2145 secs
  Slowest:	0.0171 secs
  Fastest:	0.0001 secs
  Average:	0.0020 secs
  Requests/sec:	46622.7040
Status code distribution:
### Server-Sent Events (Async Generator) (/sse-async)
  Total:	0.4975 secs
  Slowest:	0.0302 secs
  Fastest:	0.0002 secs
  Average:	0.0047 secs
  Requests/sec:	20101.4928
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6783 secs
  Slowest:	0.0345 secs
  Fastest:	0.0004 secs
  Average:	0.0064 secs
  Requests/sec:	14742.0693
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.9983 secs
  Slowest:	0.0622 secs
  Fastest:	0.0004 secs
  Average:	0.0093 secs
  Requests/sec:	10017.1503
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    55191.90 [#/sec] (mean)
Time per request:       1.812 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    73546.18 [#/sec] (mean)
Time per request:       1.360 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15701.37 [#/sec] (mean)
Time per request:       6.369 [ms] (mean)
Time per request:       0.064 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    14249.34 [#/sec] (mean)
Time per request:       7.018 [ms] (mean)
Time per request:       0.070 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    19421.51 [#/sec] (mean)
Time per request:       5.149 [ms] (mean)
Time per request:       0.051 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    19210.93 [#/sec] (mean)
Time per request:       5.205 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    99275.29 [#/sec] (mean)
Time per request:       1.007 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    90018.72 [#/sec] (mean)
Time per request:       1.111 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    67909.87 [#/sec] (mean)
Time per request:       1.473 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    93936.41 [#/sec] (mean)
Time per request:       1.065 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    87104.98 [#/sec] (mean)
Time per request:       1.148 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    75130.92 [#/sec] (mean)
Time per request:       1.331 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    96180.67 [#/sec] (mean)
Time per request:       1.040 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.2195 secs
  Slowest:	0.0165 secs
  Fastest:	0.0001 secs
  Average:	0.0021 secs
  Requests/sec:	45549.6930
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.1957 secs
  Slowest:	0.0114 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	51096.2885
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.8758 secs
  Slowest:	0.0358 secs
  Fastest:	0.0005 secs
  Average:	0.0084 secs
  Requests/sec:	11418.5994
Status code distribution:

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    17515.40 [#/sec] (mean)
Time per request:       5.709 [ms] (mean)
Time per request:       0.057 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    77707.93 [#/sec] (mean)
Time per request:       1.287 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    59021.77 [#/sec] (mean)
Time per request:       1.694 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    56646.31 [#/sec] (mean)
Time per request:       1.765 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    90647.04 [#/sec] (mean)
Time per request:       1.103 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

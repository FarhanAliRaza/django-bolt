# Django-Bolt Benchmark
Generated: Thu Nov  6 08:16:21 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    102435.93 [#/sec] (mean)
Time per request:       0.976 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON  (/10k-json)
Failed requests:        0
Requests per second:    85316.22 [#/sec] (mean)
Time per request:       1.172 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    102375.10 [#/sec] (mean)
Time per request:       0.977 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    103580.79 [#/sec] (mean)
Time per request:       0.965 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    96319.63 [#/sec] (mean)
Time per request:       1.038 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    104227.47 [#/sec] (mean)
Time per request:       0.959 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    105316.37 [#/sec] (mean)
Time per request:       0.950 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    32542.55 [#/sec] (mean)
Time per request:       3.073 [ms] (mean)
Time per request:       0.031 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2227 secs
  Slowest:	0.0114 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	44905.2788
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1962 secs
  Slowest:	0.0102 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	50960.2579
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3501 secs
  Slowest:	0.0113 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	28562.8714
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.5574 secs
  Slowest:	0.0223 secs
  Fastest:	0.0003 secs
  Average:	0.0053 secs
  Requests/sec:	17940.5557
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.6684 secs
  Slowest:	0.0165 secs
  Fastest:	0.0004 secs
  Average:	0.0064 secs
  Requests/sec:	14960.4014
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    96102.10 [#/sec] (mean)
Time per request:       1.041 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    91581.80 [#/sec] (mean)
Time per request:       1.092 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    15791.60 [#/sec] (mean)
Time per request:       6.332 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    17697.42 [#/sec] (mean)
Time per request:       5.651 [ms] (mean)
Time per request:       0.057 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    101126.55 [#/sec] (mean)
Time per request:       0.989 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    96274.19 [#/sec] (mean)
Time per request:       1.039 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    69059.82 [#/sec] (mean)
Time per request:       1.448 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    93088.20 [#/sec] (mean)
Time per request:       1.074 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    92376.19 [#/sec] (mean)
Time per request:       1.083 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    96214.91 [#/sec] (mean)
Time per request:       1.039 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    100572.26 [#/sec] (mean)
Time per request:       0.994 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.1894 secs
  Slowest:	0.0125 secs
  Fastest:	0.0001 secs
  Average:	0.0018 secs
  Requests/sec:	52786.4302
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.1666 secs
  Slowest:	0.0081 secs
  Fastest:	0.0001 secs
  Average:	0.0016 secs
  Requests/sec:	60038.1683
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.7214 secs
  Slowest:	0.0229 secs
  Fastest:	0.0005 secs
  Average:	0.0069 secs
  Requests/sec:	13862.5085
Status code distribution:

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    16771.46 [#/sec] (mean)
Time per request:       5.963 [ms] (mean)
Time per request:       0.060 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    78135.38 [#/sec] (mean)
Time per request:       1.280 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    61976.68 [#/sec] (mean)
Time per request:       1.614 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    58103.73 [#/sec] (mean)
Time per request:       1.721 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    96369.75 [#/sec] (mean)
Time per request:       1.038 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

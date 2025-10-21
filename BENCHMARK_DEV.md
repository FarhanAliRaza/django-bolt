# Django-Bolt Benchmark
Generated: Tue Oct 21 09:44:38 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    32314.77 [#/sec] (mean)
Time per request:       3.095 [ms] (mean)
Time per request:       0.031 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    81941.02 [#/sec] (mean)
Time per request:       1.220 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    86536.63 [#/sec] (mean)
Time per request:       1.156 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    81748.77 [#/sec] (mean)
Time per request:       1.223 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    88640.69 [#/sec] (mean)
Time per request:       1.128 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    84498.71 [#/sec] (mean)
Time per request:       1.183 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    29158.60 [#/sec] (mean)
Time per request:       3.430 [ms] (mean)
Time per request:       0.034 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2085 secs
  Slowest:	0.0127 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	47964.3905
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1895 secs
  Slowest:	0.0129 secs
  Fastest:	0.0001 secs
  Average:	0.0018 secs
  Requests/sec:	52781.4527
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3663 secs
  Slowest:	0.0168 secs
  Fastest:	0.0003 secs
  Average:	0.0035 secs
  Requests/sec:	27303.3775
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6583 secs
  Slowest:	0.0187 secs
  Fastest:	0.0004 secs
  Average:	0.0062 secs
  Requests/sec:	15190.4789
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8079 secs
  Slowest:	0.0366 secs
  Fastest:	0.0005 secs
  Average:	0.0076 secs
  Requests/sec:	12377.8297
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    82596.84 [#/sec] (mean)
Time per request:       1.211 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    73156.64 [#/sec] (mean)
Time per request:       1.367 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    13486.50 [#/sec] (mean)
Time per request:       7.415 [ms] (mean)
Time per request:       0.074 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14651.97 [#/sec] (mean)
Time per request:       6.825 [ms] (mean)
Time per request:       0.068 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    82676.74 [#/sec] (mean)
Time per request:       1.210 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    76554.44 [#/sec] (mean)
Time per request:       1.306 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    42265.61 [#/sec] (mean)
Time per request:       2.366 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    80368.41 [#/sec] (mean)
Time per request:       1.244 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    77923.49 [#/sec] (mean)
Time per request:       1.283 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    79826.94 [#/sec] (mean)
Time per request:       1.253 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    85608.38 [#/sec] (mean)
Time per request:       1.168 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3696 secs
  Slowest:	0.0179 secs
  Fastest:	0.0002 secs
  Average:	0.0035 secs
  Requests/sec:	27058.6794
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3668 secs
  Slowest:	0.0245 secs
  Fastest:	0.0002 secs
  Average:	0.0035 secs
  Requests/sec:	27265.1322
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.9190 secs
  Slowest:	0.0414 secs
  Fastest:	0.0005 secs
  Average:	0.0088 secs
  Requests/sec:	10880.8757
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    16713.07 [#/sec] (mean)
Time per request:       5.983 [ms] (mean)
Time per request:       0.060 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    68652.08 [#/sec] (mean)
Time per request:       1.457 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    54037.99 [#/sec] (mean)
Time per request:       1.851 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    52107.49 [#/sec] (mean)
Time per request:       1.919 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    82082.94 [#/sec] (mean)
Time per request:       1.218 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

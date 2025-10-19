# Django-Bolt Benchmark
Generated: Sun Oct 19 11:50:08 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    40286.03 [#/sec] (mean)
Time per request:       2.482 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    43614.41 [#/sec] (mean)
Time per request:       2.293 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    43890.83 [#/sec] (mean)
Time per request:       2.278 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    42856.65 [#/sec] (mean)
Time per request:       2.333 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    45007.34 [#/sec] (mean)
Time per request:       2.222 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    46106.53 [#/sec] (mean)
Time per request:       2.169 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    21904.17 [#/sec] (mean)
Time per request:       4.565 [ms] (mean)
Time per request:       0.046 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3775 secs
  Slowest:	0.0117 secs
  Fastest:	0.0002 secs
  Average:	0.0037 secs
  Requests/sec:	26492.7399
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3328 secs
  Slowest:	0.0089 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	30044.1492
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7143 secs
  Slowest:	0.0155 secs
  Fastest:	0.0003 secs
  Average:	0.0069 secs
  Requests/sec:	13999.2010
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1310 secs
  Slowest:	0.0292 secs
  Fastest:	0.0004 secs
  Average:	0.0110 secs
  Requests/sec:	8841.5470
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5219 secs
  Slowest:	0.0307 secs
  Fastest:	0.0005 secs
  Average:	0.0148 secs
  Requests/sec:	6570.6277
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    41043.66 [#/sec] (mean)
Time per request:       2.436 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    37585.65 [#/sec] (mean)
Time per request:       2.661 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7070.42 [#/sec] (mean)
Time per request:       14.143 [ms] (mean)
Time per request:       0.141 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8282.83 [#/sec] (mean)
Time per request:       12.073 [ms] (mean)
Time per request:       0.121 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    45070.63 [#/sec] (mean)
Time per request:       2.219 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    40946.86 [#/sec] (mean)
Time per request:       2.442 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    22702.04 [#/sec] (mean)
Time per request:       4.405 [ms] (mean)
Time per request:       0.044 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    40680.83 [#/sec] (mean)
Time per request:       2.458 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    40160.16 [#/sec] (mean)
Time per request:       2.490 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    40552.49 [#/sec] (mean)
Time per request:       2.466 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    43791.08 [#/sec] (mean)
Time per request:       2.284 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.4132 secs
  Slowest:	0.0338 secs
  Fastest:	0.0002 secs
  Average:	0.0040 secs
  Requests/sec:	24199.5504
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3549 secs
  Slowest:	0.0166 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	28178.4626
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	1.4741 secs
  Slowest:	0.0361 secs
  Fastest:	0.0005 secs
  Average:	0.0141 secs
  Requests/sec:	6783.8136
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    8401.36 [#/sec] (mean)
Time per request:       11.903 [ms] (mean)
Time per request:       0.119 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    35004.94 [#/sec] (mean)
Time per request:       2.857 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    7275.61 [#/sec] (mean)
Time per request:       13.745 [ms] (mean)
Time per request:       0.137 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    7469.65 [#/sec] (mean)
Time per request:       13.387 [ms] (mean)
Time per request:       0.134 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    41397.75 [#/sec] (mean)
Time per request:       2.416 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

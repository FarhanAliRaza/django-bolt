# Django-Bolt Benchmark
Generated: Fri Oct 17 09:41:29 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    41526.34 [#/sec] (mean)
Time per request:       2.408 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    42047.55 [#/sec] (mean)
Time per request:       2.378 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    42410.80 [#/sec] (mean)
Time per request:       2.358 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    41639.77 [#/sec] (mean)
Time per request:       2.402 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    44197.92 [#/sec] (mean)
Time per request:       2.263 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    44937.96 [#/sec] (mean)
Time per request:       2.225 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    23239.92 [#/sec] (mean)
Time per request:       4.303 [ms] (mean)
Time per request:       0.043 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3801 secs
  Slowest:	0.0136 secs
  Fastest:	0.0002 secs
  Average:	0.0037 secs
  Requests/sec:	26305.9222
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3321 secs
  Slowest:	0.0091 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	30109.1978
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7243 secs
  Slowest:	0.0147 secs
  Fastest:	0.0003 secs
  Average:	0.0070 secs
  Requests/sec:	13806.4108
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1653 secs
  Slowest:	0.0300 secs
  Fastest:	0.0004 secs
  Average:	0.0113 secs
  Requests/sec:	8581.3756
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5087 secs
  Slowest:	0.0282 secs
  Fastest:	0.0005 secs
  Average:	0.0146 secs
  Requests/sec:	6628.3045
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    40891.93 [#/sec] (mean)
Time per request:       2.445 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    36881.04 [#/sec] (mean)
Time per request:       2.711 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7005.57 [#/sec] (mean)
Time per request:       14.274 [ms] (mean)
Time per request:       0.143 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8056.06 [#/sec] (mean)
Time per request:       12.413 [ms] (mean)
Time per request:       0.124 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    44987.09 [#/sec] (mean)
Time per request:       2.223 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    40596.77 [#/sec] (mean)
Time per request:       2.463 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    21672.51 [#/sec] (mean)
Time per request:       4.614 [ms] (mean)
Time per request:       0.046 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    40021.77 [#/sec] (mean)
Time per request:       2.499 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    39258.49 [#/sec] (mean)
Time per request:       2.547 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    40107.17 [#/sec] (mean)
Time per request:       2.493 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    42746.00 [#/sec] (mean)
Time per request:       2.339 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3927 secs
  Slowest:	0.0185 secs
  Fastest:	0.0002 secs
  Average:	0.0038 secs
  Requests/sec:	25465.5177
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3508 secs
  Slowest:	0.0128 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	28508.2020
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	1.4840 secs
  Slowest:	0.0288 secs
  Fastest:	0.0005 secs
  Average:	0.0144 secs
  Requests/sec:	6738.3609
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    8409.55 [#/sec] (mean)
Time per request:       11.891 [ms] (mean)
Time per request:       0.119 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    34808.28 [#/sec] (mean)
Time per request:       2.873 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    7371.19 [#/sec] (mean)
Time per request:       13.566 [ms] (mean)
Time per request:       0.136 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    7419.87 [#/sec] (mean)
Time per request:       13.477 [ms] (mean)
Time per request:       0.135 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    39568.23 [#/sec] (mean)
Time per request:       2.527 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

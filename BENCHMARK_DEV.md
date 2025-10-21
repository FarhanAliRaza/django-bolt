# Django-Bolt Benchmark
Generated: Tue Oct 21 09:15:09 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    16547.80 [#/sec] (mean)
Time per request:       6.043 [ms] (mean)
Time per request:       0.060 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    37074.39 [#/sec] (mean)
Time per request:       2.697 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    37981.80 [#/sec] (mean)
Time per request:       2.633 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    37404.85 [#/sec] (mean)
Time per request:       2.673 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    37918.72 [#/sec] (mean)
Time per request:       2.637 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    38290.56 [#/sec] (mean)
Time per request:       2.612 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    21029.17 [#/sec] (mean)
Time per request:       4.755 [ms] (mean)
Time per request:       0.048 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.4306 secs
  Slowest:	0.0106 secs
  Fastest:	0.0002 secs
  Average:	0.0042 secs
  Requests/sec:	23222.4585
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3863 secs
  Slowest:	0.0142 secs
  Fastest:	0.0002 secs
  Average:	0.0037 secs
  Requests/sec:	25885.4219
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7904 secs
  Slowest:	0.0208 secs
  Fastest:	0.0003 secs
  Average:	0.0075 secs
  Requests/sec:	12651.1581
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1734 secs
  Slowest:	0.0238 secs
  Fastest:	0.0004 secs
  Average:	0.0114 secs
  Requests/sec:	8522.2263
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5802 secs
  Slowest:	0.0335 secs
  Fastest:	0.0005 secs
  Average:	0.0151 secs
  Requests/sec:	6328.1241
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    35420.55 [#/sec] (mean)
Time per request:       2.823 [ms] (mean)
Time per request:       0.028 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    32596.76 [#/sec] (mean)
Time per request:       3.068 [ms] (mean)
Time per request:       0.031 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6840.13 [#/sec] (mean)
Time per request:       14.620 [ms] (mean)
Time per request:       0.146 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    7842.66 [#/sec] (mean)
Time per request:       12.751 [ms] (mean)
Time per request:       0.128 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    39282.70 [#/sec] (mean)
Time per request:       2.546 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    35442.27 [#/sec] (mean)
Time per request:       2.821 [ms] (mean)
Time per request:       0.028 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    20364.61 [#/sec] (mean)
Time per request:       4.910 [ms] (mean)
Time per request:       0.049 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    34483.12 [#/sec] (mean)
Time per request:       2.900 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    32908.48 [#/sec] (mean)
Time per request:       3.039 [ms] (mean)
Time per request:       0.030 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    34785.03 [#/sec] (mean)
Time per request:       2.875 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    36967.35 [#/sec] (mean)
Time per request:       2.705 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.4538 secs
  Slowest:	0.0148 secs
  Fastest:	0.0002 secs
  Average:	0.0044 secs
  Requests/sec:	22037.6515
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.4124 secs
  Slowest:	0.0149 secs
  Fastest:	0.0002 secs
  Average:	0.0040 secs
  Requests/sec:	24251.1115
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	1.5287 secs
  Slowest:	0.0269 secs
  Fastest:	0.0005 secs
  Average:	0.0150 secs
  Requests/sec:	6541.6648
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    8179.09 [#/sec] (mean)
Time per request:       12.226 [ms] (mean)
Time per request:       0.122 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    30090.30 [#/sec] (mean)
Time per request:       3.323 [ms] (mean)
Time per request:       0.033 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    24650.40 [#/sec] (mean)
Time per request:       4.057 [ms] (mean)
Time per request:       0.041 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    23619.89 [#/sec] (mean)
Time per request:       4.234 [ms] (mean)
Time per request:       0.042 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    35150.13 [#/sec] (mean)
Time per request:       2.845 [ms] (mean)
Time per request:       0.028 [ms] (mean, across all concurrent requests)

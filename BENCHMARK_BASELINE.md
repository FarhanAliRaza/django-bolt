# Django-Bolt Benchmark
Generated: Tue Oct 21 05:50:17 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    17357.40 [#/sec] (mean)
Time per request:       5.761 [ms] (mean)
Time per request:       0.058 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    44139.78 [#/sec] (mean)
Time per request:       2.266 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    42671.22 [#/sec] (mean)
Time per request:       2.344 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    42490.27 [#/sec] (mean)
Time per request:       2.353 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    46829.85 [#/sec] (mean)
Time per request:       2.135 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    45881.03 [#/sec] (mean)
Time per request:       2.180 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    19768.82 [#/sec] (mean)
Time per request:       5.058 [ms] (mean)
Time per request:       0.051 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2696 secs
  Slowest:	0.0093 secs
  Fastest:	0.0002 secs
  Average:	0.0026 secs
  Requests/sec:	37088.7122
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2663 secs
  Slowest:	0.0098 secs
  Fastest:	0.0001 secs
  Average:	0.0026 secs
  Requests/sec:	37546.2835
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.2596 secs
  Slowest:	0.0087 secs
  Fastest:	0.0001 secs
  Average:	0.0025 secs
  Requests/sec:	38517.0868
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.2780 secs
  Slowest:	0.0088 secs
  Fastest:	0.0001 secs
  Average:	0.0027 secs
  Requests/sec:	35974.6721
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.2784 secs
  Slowest:	0.0099 secs
  Fastest:	0.0002 secs
  Average:	0.0027 secs
  Requests/sec:	35916.1518
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    42937.44 [#/sec] (mean)
Time per request:       2.329 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    38173.62 [#/sec] (mean)
Time per request:       2.620 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7475.33 [#/sec] (mean)
Time per request:       13.377 [ms] (mean)
Time per request:       0.134 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8444.05 [#/sec] (mean)
Time per request:       11.843 [ms] (mean)
Time per request:       0.118 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    46971.07 [#/sec] (mean)
Time per request:       2.129 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    41413.01 [#/sec] (mean)
Time per request:       2.415 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    23245.60 [#/sec] (mean)
Time per request:       4.302 [ms] (mean)
Time per request:       0.043 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    42859.96 [#/sec] (mean)
Time per request:       2.333 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    40860.69 [#/sec] (mean)
Time per request:       2.447 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    41270.64 [#/sec] (mean)
Time per request:       2.423 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    45130.63 [#/sec] (mean)
Time per request:       2.216 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3208 secs
  Slowest:	0.0138 secs
  Fastest:	0.0002 secs
  Average:	0.0031 secs
  Requests/sec:	31169.9727
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3173 secs
  Slowest:	0.0176 secs
  Fastest:	0.0002 secs
  Average:	0.0030 secs
  Requests/sec:	31517.0997
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.3305 secs
  Slowest:	0.0136 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	30255.9894
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    8865.52 [#/sec] (mean)
Time per request:       11.280 [ms] (mean)
Time per request:       0.113 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    36722.58 [#/sec] (mean)
Time per request:       2.723 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    7577.09 [#/sec] (mean)
Time per request:       13.198 [ms] (mean)
Time per request:       0.132 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    8019.55 [#/sec] (mean)
Time per request:       12.470 [ms] (mean)
Time per request:       0.125 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    41493.60 [#/sec] (mean)
Time per request:       2.410 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

# Django-Bolt Benchmark
Generated: Sat Oct 18 12:49:06 AM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    40983.27 [#/sec] (mean)
Time per request:       2.440 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    42890.84 [#/sec] (mean)
Time per request:       2.332 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    42526.41 [#/sec] (mean)
Time per request:       2.351 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    43493.58 [#/sec] (mean)
Time per request:       2.299 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    45212.25 [#/sec] (mean)
Time per request:       2.212 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    44796.44 [#/sec] (mean)
Time per request:       2.232 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    21658.48 [#/sec] (mean)
Time per request:       4.617 [ms] (mean)
Time per request:       0.046 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3813 secs
  Slowest:	0.0101 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	26224.3558
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3354 secs
  Slowest:	0.0110 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	29812.1442
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7343 secs
  Slowest:	0.0174 secs
  Fastest:	0.0003 secs
  Average:	0.0071 secs
  Requests/sec:	13619.1451
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1388 secs
  Slowest:	0.0255 secs
  Fastest:	0.0004 secs
  Average:	0.0110 secs
  Requests/sec:	8780.8745
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5168 secs
  Slowest:	0.0325 secs
  Fastest:	0.0005 secs
  Average:	0.0148 secs
  Requests/sec:	6592.8514
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    40951.89 [#/sec] (mean)
Time per request:       2.442 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    37361.81 [#/sec] (mean)
Time per request:       2.677 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6998.91 [#/sec] (mean)
Time per request:       14.288 [ms] (mean)
Time per request:       0.143 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8021.32 [#/sec] (mean)
Time per request:       12.467 [ms] (mean)
Time per request:       0.125 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    45106.00 [#/sec] (mean)
Time per request:       2.217 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    40089.48 [#/sec] (mean)
Time per request:       2.494 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    21931.22 [#/sec] (mean)
Time per request:       4.560 [ms] (mean)
Time per request:       0.046 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    40408.94 [#/sec] (mean)
Time per request:       2.475 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    39077.15 [#/sec] (mean)
Time per request:       2.559 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    39930.20 [#/sec] (mean)
Time per request:       2.504 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    43763.68 [#/sec] (mean)
Time per request:       2.285 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.4161 secs
  Slowest:	0.0167 secs
  Fastest:	0.0002 secs
  Average:	0.0040 secs
  Requests/sec:	24033.7428
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3840 secs
  Slowest:	0.0165 secs
  Fastest:	0.0002 secs
  Average:	0.0037 secs
  Requests/sec:	26042.4787
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	1.5248 secs
  Slowest:	0.0342 secs
  Fastest:	0.0005 secs
  Average:	0.0148 secs
  Requests/sec:	6558.3997
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    8269.70 [#/sec] (mean)
Time per request:       12.092 [ms] (mean)
Time per request:       0.121 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    34718.36 [#/sec] (mean)
Time per request:       2.880 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    7285.73 [#/sec] (mean)
Time per request:       13.725 [ms] (mean)
Time per request:       0.137 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    7305.53 [#/sec] (mean)
Time per request:       13.688 [ms] (mean)
Time per request:       0.137 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    40937.97 [#/sec] (mean)
Time per request:       2.443 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

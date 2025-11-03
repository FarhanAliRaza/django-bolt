# Django-Bolt Benchmark
Generated: Mon Nov  3 10:26:40 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    104689.02 [#/sec] (mean)
Time per request:       0.955 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON  (/10k-json)
Failed requests:        0
Requests per second:    83010.97 [#/sec] (mean)
Time per request:       1.205 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    104919.68 [#/sec] (mean)
Time per request:       0.953 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    105427.40 [#/sec] (mean)
Time per request:       0.949 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    104456.10 [#/sec] (mean)
Time per request:       0.957 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    105462.98 [#/sec] (mean)
Time per request:       0.948 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    105593.28 [#/sec] (mean)
Time per request:       0.947 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    36530.75 [#/sec] (mean)
Time per request:       2.737 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.1898 secs
  Slowest:	0.0089 secs
  Fastest:	0.0002 secs
  Average:	0.0018 secs
  Requests/sec:	52687.6181
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1692 secs
  Slowest:	0.0071 secs
  Fastest:	0.0001 secs
  Average:	0.0016 secs
  Requests/sec:	59085.0852
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3223 secs
  Slowest:	0.0100 secs
  Fastest:	0.0002 secs
  Average:	0.0031 secs
  Requests/sec:	31025.6232
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.5336 secs
  Slowest:	0.0173 secs
  Fastest:	0.0003 secs
  Average:	0.0051 secs
  Requests/sec:	18739.3131
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.6468 secs
  Slowest:	0.0200 secs
  Fastest:	0.0005 secs
  Average:	0.0062 secs
  Requests/sec:	15461.7519
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    99712.83 [#/sec] (mean)
Time per request:       1.003 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    97601.92 [#/sec] (mean)
Time per request:       1.025 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    18441.00 [#/sec] (mean)
Time per request:       5.423 [ms] (mean)
Time per request:       0.054 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    19241.28 [#/sec] (mean)
Time per request:       5.197 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    101341.76 [#/sec] (mean)
Time per request:       0.987 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    87352.27 [#/sec] (mean)
Time per request:       1.145 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    66887.84 [#/sec] (mean)
Time per request:       1.495 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    100264.70 [#/sec] (mean)
Time per request:       0.997 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    97465.89 [#/sec] (mean)
Time per request:       1.026 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    99916.07 [#/sec] (mean)
Time per request:       1.001 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    104197.06 [#/sec] (mean)
Time per request:       0.960 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.1790 secs
  Slowest:	0.0083 secs
  Fastest:	0.0001 secs
  Average:	0.0017 secs
  Requests/sec:	55866.1556
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.1642 secs
  Slowest:	0.0070 secs
  Fastest:	0.0001 secs
  Average:	0.0016 secs
  Requests/sec:	60899.2132
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.7215 secs
  Slowest:	0.0338 secs
  Fastest:	0.0004 secs
  Average:	0.0069 secs
  Requests/sec:	13859.4308
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    22145.26 [#/sec] (mean)
Time per request:       4.516 [ms] (mean)
Time per request:       0.045 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    78050.61 [#/sec] (mean)
Time per request:       1.281 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    62012.04 [#/sec] (mean)
Time per request:       1.613 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    59961.03 [#/sec] (mean)
Time per request:       1.668 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    99219.15 [#/sec] (mean)
Time per request:       1.008 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

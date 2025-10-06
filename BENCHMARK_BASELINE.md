# Django-Bolt Benchmark
Generated: Sun Oct  5 01:51:26 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    45848.00 [#/sec] (mean)
Time per request:       2.181 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    46095.06 [#/sec] (mean)
Time per request:       2.169 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    45562.86 [#/sec] (mean)
Time per request:       2.195 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    46486.55 [#/sec] (mean)
Time per request:       2.151 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    50621.63 [#/sec] (mean)
Time per request:       1.975 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    50156.99 [#/sec] (mean)
Time per request:       1.994 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2421.58 [#/sec] (mean)
Time per request:       41.295 [ms] (mean)
Time per request:       0.413 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3562 secs
  Slowest:	0.0103 secs
  Fastest:	0.0002 secs
  Average:	0.0035 secs
  Requests/sec:	28077.9186
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3164 secs
  Slowest:	0.0139 secs
  Fastest:	0.0002 secs
  Average:	0.0031 secs
  Requests/sec:	31608.7793
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7036 secs
  Slowest:	0.0168 secs
  Fastest:	0.0003 secs
  Average:	0.0068 secs
  Requests/sec:	14213.0615
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1632 secs
  Slowest:	0.0401 secs
  Fastest:	0.0004 secs
  Average:	0.0110 secs
  Requests/sec:	8597.0977
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.4591 secs
  Slowest:	0.0355 secs
  Fastest:	0.0005 secs
  Average:	0.0142 secs
  Requests/sec:	6853.5767
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    38986.35 [#/sec] (mean)
Time per request:       2.565 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    39060.06 [#/sec] (mean)
Time per request:       2.560 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6898.37 [#/sec] (mean)
Time per request:       14.496 [ms] (mean)
Time per request:       0.145 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8222.18 [#/sec] (mean)
Time per request:       12.162 [ms] (mean)
Time per request:       0.122 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    37618.88 [#/sec] (mean)
Time per request:       2.658 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    43945.61 [#/sec] (mean)
Time per request:       2.276 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    44195.38 [#/sec] (mean)
Time per request:       2.263 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    43565.58 [#/sec] (mean)
Time per request:       2.295 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

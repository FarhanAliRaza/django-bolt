# Django-Bolt Benchmark
Generated: Fri Oct 10 04:36:21 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    42430.59 [#/sec] (mean)
Time per request:       2.357 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    41534.28 [#/sec] (mean)
Time per request:       2.408 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    41909.74 [#/sec] (mean)
Time per request:       2.386 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    41541.70 [#/sec] (mean)
Time per request:       2.407 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    43174.54 [#/sec] (mean)
Time per request:       2.316 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    42519.36 [#/sec] (mean)
Time per request:       2.352 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2419.38 [#/sec] (mean)
Time per request:       41.333 [ms] (mean)
Time per request:       0.413 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3831 secs
  Slowest:	0.0149 secs
  Fastest:	0.0002 secs
  Average:	0.0037 secs
  Requests/sec:	26100.1734
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3417 secs
  Slowest:	0.0150 secs
  Fastest:	0.0001 secs
  Average:	0.0033 secs
  Requests/sec:	29263.4521
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7277 secs
  Slowest:	0.0210 secs
  Fastest:	0.0003 secs
  Average:	0.0071 secs
  Requests/sec:	13741.5396
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1299 secs
  Slowest:	0.0449 secs
  Fastest:	0.0004 secs
  Average:	0.0108 secs
  Requests/sec:	8849.9527
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5337 secs
  Slowest:	0.0379 secs
  Fastest:	0.0004 secs
  Average:	0.0144 secs
  Requests/sec:	6520.1329
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    39099.31 [#/sec] (mean)
Time per request:       2.558 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    36378.58 [#/sec] (mean)
Time per request:       2.749 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6829.41 [#/sec] (mean)
Time per request:       14.643 [ms] (mean)
Time per request:       0.146 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8103.29 [#/sec] (mean)
Time per request:       12.341 [ms] (mean)
Time per request:       0.123 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    33304.36 [#/sec] (mean)
Time per request:       3.003 [ms] (mean)
Time per request:       0.030 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    12251.13 [#/sec] (mean)
Time per request:       8.163 [ms] (mean)
Time per request:       0.082 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    12437.36 [#/sec] (mean)
Time per request:       8.040 [ms] (mean)
Time per request:       0.080 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    39873.52 [#/sec] (mean)
Time per request:       2.508 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

# Django-Bolt Benchmark
Generated: Fri Oct 10 08:48:49 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    74260.00 [#/sec] (mean)
Time per request:       1.347 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    74605.71 [#/sec] (mean)
Time per request:       1.340 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    72842.76 [#/sec] (mean)
Time per request:       1.373 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    68657.74 [#/sec] (mean)
Time per request:       1.456 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    69828.50 [#/sec] (mean)
Time per request:       1.432 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    73083.92 [#/sec] (mean)
Time per request:       1.368 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2376.98 [#/sec] (mean)
Time per request:       42.070 [ms] (mean)
Time per request:       0.421 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2515 secs
  Slowest:	0.0119 secs
  Fastest:	0.0002 secs
  Average:	0.0024 secs
  Requests/sec:	39764.3695
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2464 secs
  Slowest:	0.0278 secs
  Fastest:	0.0001 secs
  Average:	0.0023 secs
  Requests/sec:	40581.3712
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.5016 secs
  Slowest:	0.0205 secs
  Fastest:	0.0003 secs
  Average:	0.0048 secs
  Requests/sec:	19935.4208
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.7185 secs
  Slowest:	0.0531 secs
  Fastest:	0.0004 secs
  Average:	0.0067 secs
  Requests/sec:	13918.0172
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8695 secs
  Slowest:	0.0318 secs
  Fastest:	0.0005 secs
  Average:	0.0083 secs
  Requests/sec:	11500.4193
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    54862.46 [#/sec] (mean)
Time per request:       1.823 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    60681.45 [#/sec] (mean)
Time per request:       1.648 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    11494.15 [#/sec] (mean)
Time per request:       8.700 [ms] (mean)
Time per request:       0.087 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14091.69 [#/sec] (mean)
Time per request:       7.096 [ms] (mean)
Time per request:       0.071 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    45988.22 [#/sec] (mean)
Time per request:       2.174 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    17112.36 [#/sec] (mean)
Time per request:       5.844 [ms] (mean)
Time per request:       0.058 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    19174.68 [#/sec] (mean)
Time per request:       5.215 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    69399.62 [#/sec] (mean)
Time per request:       1.441 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

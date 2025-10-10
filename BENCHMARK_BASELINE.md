# Django-Bolt Benchmark
Generated: Fri Oct 10 04:35:55 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    76429.23 [#/sec] (mean)
Time per request:       1.308 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    80546.43 [#/sec] (mean)
Time per request:       1.242 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    70091.33 [#/sec] (mean)
Time per request:       1.427 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    70024.58 [#/sec] (mean)
Time per request:       1.428 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    61400.92 [#/sec] (mean)
Time per request:       1.629 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    72019.65 [#/sec] (mean)
Time per request:       1.389 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2421.35 [#/sec] (mean)
Time per request:       41.299 [ms] (mean)
Time per request:       0.413 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2187 secs
  Slowest:	0.0111 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	45724.2148
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2174 secs
  Slowest:	0.0161 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	46008.4684
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.4065 secs
  Slowest:	0.0177 secs
  Fastest:	0.0003 secs
  Average:	0.0039 secs
  Requests/sec:	24600.5801
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6451 secs
  Slowest:	0.0270 secs
  Fastest:	0.0004 secs
  Average:	0.0061 secs
  Requests/sec:	15502.5211
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8082 secs
  Slowest:	0.0246 secs
  Fastest:	0.0005 secs
  Average:	0.0078 secs
  Requests/sec:	12372.7696
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    54148.89 [#/sec] (mean)
Time per request:       1.847 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    67998.99 [#/sec] (mean)
Time per request:       1.471 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12027.05 [#/sec] (mean)
Time per request:       8.315 [ms] (mean)
Time per request:       0.083 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14760.98 [#/sec] (mean)
Time per request:       6.775 [ms] (mean)
Time per request:       0.068 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    63367.74 [#/sec] (mean)
Time per request:       1.578 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    21602.89 [#/sec] (mean)
Time per request:       4.629 [ms] (mean)
Time per request:       0.046 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    23177.28 [#/sec] (mean)
Time per request:       4.315 [ms] (mean)
Time per request:       0.043 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    69904.16 [#/sec] (mean)
Time per request:       1.431 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

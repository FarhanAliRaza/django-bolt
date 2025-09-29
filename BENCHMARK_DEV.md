# Django-Bolt Benchmark
Generated: Tue Sep 30 12:14:47 AM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    44317.79 [#/sec] (mean)
Time per request:       2.256 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    44969.89 [#/sec] (mean)
Time per request:       2.224 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    44183.66 [#/sec] (mean)
Time per request:       2.263 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    44740.73 [#/sec] (mean)
Time per request:       2.235 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    46280.66 [#/sec] (mean)
Time per request:       2.161 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    45719.09 [#/sec] (mean)
Time per request:       2.187 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2430.34 [#/sec] (mean)
Time per request:       41.147 [ms] (mean)
Time per request:       0.411 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3953 secs
  Slowest:	0.0171 secs
  Fastest:	0.0002 secs
  Average:	0.0038 secs
  Requests/sec:	25296.0978
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.3670 secs
  Slowest:	0.0142 secs
  Fastest:	0.0002 secs
  Average:	0.0035 secs
  Requests/sec:	27244.4725
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.7788 secs
  Slowest:	0.0212 secs
  Fastest:	0.0003 secs
  Average:	0.0072 secs
  Requests/sec:	12840.3014
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1796 secs
  Slowest:	0.0245 secs
  Fastest:	0.0004 secs
  Average:	0.0111 secs
  Requests/sec:	8477.6964
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5291 secs
  Slowest:	0.0275 secs
  Fastest:	0.0005 secs
  Average:	0.0146 secs
  Requests/sec:	6539.8349
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    40015.37 [#/sec] (mean)
Time per request:       2.499 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    38197.10 [#/sec] (mean)
Time per request:       2.618 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6733.79 [#/sec] (mean)
Time per request:       14.850 [ms] (mean)
Time per request:       0.149 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8011.92 [#/sec] (mean)
Time per request:       12.481 [ms] (mean)
Time per request:       0.125 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    35471.06 [#/sec] (mean)
Time per request:       2.819 [ms] (mean)
Time per request:       0.028 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    42658.48 [#/sec] (mean)
Time per request:       2.344 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    42318.91 [#/sec] (mean)
Time per request:       2.363 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    42748.38 [#/sec] (mean)
Time per request:       2.339 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

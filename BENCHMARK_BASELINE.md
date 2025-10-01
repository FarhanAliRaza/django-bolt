# Django-Bolt Benchmark
Generated: Wed Oct  1 11:14:24 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    86608.58 [#/sec] (mean)
Time per request:       1.155 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    75318.79 [#/sec] (mean)
Time per request:       1.328 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    83778.06 [#/sec] (mean)
Time per request:       1.194 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    77538.01 [#/sec] (mean)
Time per request:       1.290 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    87858.79 [#/sec] (mean)
Time per request:       1.138 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    77929.57 [#/sec] (mean)
Time per request:       1.283 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2428.07 [#/sec] (mean)
Time per request:       41.185 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.2173 secs
  Slowest:	0.0129 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	46014.2394
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.2173 secs
  Slowest:	0.0173 secs
  Fastest:	0.0001 secs
  Average:	0.0021 secs
  Requests/sec:	46015.6649
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.3908 secs
  Slowest:	0.0193 secs
  Fastest:	0.0002 secs
  Average:	0.0037 secs
  Requests/sec:	25589.2659
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6307 secs
  Slowest:	0.0260 secs
  Fastest:	0.0004 secs
  Average:	0.0060 secs
  Requests/sec:	15856.4933
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.7980 secs
  Slowest:	0.0330 secs
  Fastest:	0.0005 secs
  Average:	0.0075 secs
  Requests/sec:	12531.6103
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    63279.12 [#/sec] (mean)
Time per request:       1.580 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    71422.45 [#/sec] (mean)
Time per request:       1.400 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12174.53 [#/sec] (mean)
Time per request:       8.214 [ms] (mean)
Time per request:       0.082 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14897.18 [#/sec] (mean)
Time per request:       6.713 [ms] (mean)
Time per request:       0.067 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    63296.35 [#/sec] (mean)
Time per request:       1.580 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    80692.01 [#/sec] (mean)
Time per request:       1.239 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    73378.34 [#/sec] (mean)
Time per request:       1.363 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    75761.02 [#/sec] (mean)
Time per request:       1.320 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

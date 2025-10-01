# Django-Bolt Benchmark
Generated: Wed Oct  1 11:34:17 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    86540.38 [#/sec] (mean)
Time per request:       1.156 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    86596.58 [#/sec] (mean)
Time per request:       1.155 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    85188.31 [#/sec] (mean)
Time per request:       1.174 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    80435.64 [#/sec] (mean)
Time per request:       1.243 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    88794.18 [#/sec] (mean)
Time per request:       1.126 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    88184.98 [#/sec] (mean)
Time per request:       1.134 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2431.83 [#/sec] (mean)
Time per request:       41.121 [ms] (mean)
Time per request:       0.411 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.2125 secs
  Slowest:	0.0094 secs
  Fastest:	0.0001 secs
  Average:	0.0020 secs
  Requests/sec:	47057.5132
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.1919 secs
  Slowest:	0.0101 secs
  Fastest:	0.0001 secs
  Average:	0.0018 secs
  Requests/sec:	52117.5754
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.3665 secs
  Slowest:	0.0111 secs
  Fastest:	0.0003 secs
  Average:	0.0035 secs
  Requests/sec:	27282.8279
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6296 secs
  Slowest:	0.0183 secs
  Fastest:	0.0004 secs
  Average:	0.0060 secs
  Requests/sec:	15883.6985
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.7761 secs
  Slowest:	0.0270 secs
  Fastest:	0.0004 secs
  Average:	0.0074 secs
  Requests/sec:	12884.2536
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    62452.77 [#/sec] (mean)
Time per request:       1.601 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    78057.31 [#/sec] (mean)
Time per request:       1.281 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12019.00 [#/sec] (mean)
Time per request:       8.320 [ms] (mean)
Time per request:       0.083 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14924.75 [#/sec] (mean)
Time per request:       6.700 [ms] (mean)
Time per request:       0.067 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    69365.93 [#/sec] (mean)
Time per request:       1.442 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    78717.22 [#/sec] (mean)
Time per request:       1.270 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    81675.99 [#/sec] (mean)
Time per request:       1.224 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    81267.78 [#/sec] (mean)
Time per request:       1.231 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

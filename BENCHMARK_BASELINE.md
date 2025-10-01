# Django-Bolt Benchmark
Generated: Wed Oct  1 10:47:52 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    85471.55 [#/sec] (mean)
Time per request:       1.170 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    84116.32 [#/sec] (mean)
Time per request:       1.189 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    83676.41 [#/sec] (mean)
Time per request:       1.195 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    81686.67 [#/sec] (mean)
Time per request:       1.224 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    65533.38 [#/sec] (mean)
Time per request:       1.526 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    89091.62 [#/sec] (mean)
Time per request:       1.122 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2426.66 [#/sec] (mean)
Time per request:       41.209 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.2121 secs
  Slowest:	0.0103 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	47146.0937
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.1946 secs
  Slowest:	0.0103 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	51383.2394
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.3853 secs
  Slowest:	0.0197 secs
  Fastest:	0.0003 secs
  Average:	0.0037 secs
  Requests/sec:	25952.3107
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6171 secs
  Slowest:	0.0234 secs
  Fastest:	0.0004 secs
  Average:	0.0059 secs
  Requests/sec:	16206.1206
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.7997 secs
  Slowest:	0.0259 secs
  Fastest:	0.0004 secs
  Average:	0.0074 secs
  Requests/sec:	12503.9543
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    61498.35 [#/sec] (mean)
Time per request:       1.626 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    79719.39 [#/sec] (mean)
Time per request:       1.254 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12447.33 [#/sec] (mean)
Time per request:       8.034 [ms] (mean)
Time per request:       0.080 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    15500.51 [#/sec] (mean)
Time per request:       6.451 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    66072.46 [#/sec] (mean)
Time per request:       1.513 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    72598.97 [#/sec] (mean)
Time per request:       1.377 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    82927.68 [#/sec] (mean)
Time per request:       1.206 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    44537.68 [#/sec] (mean)
Time per request:       2.245 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

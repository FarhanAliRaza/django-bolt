# Django-Bolt Benchmark
Generated: Wed Oct  1 11:14:49 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    76667.13 [#/sec] (mean)
Time per request:       1.304 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    84788.88 [#/sec] (mean)
Time per request:       1.179 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    87006.46 [#/sec] (mean)
Time per request:       1.149 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    77270.20 [#/sec] (mean)
Time per request:       1.294 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    80348.39 [#/sec] (mean)
Time per request:       1.245 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    78051.83 [#/sec] (mean)
Time per request:       1.281 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2427.19 [#/sec] (mean)
Time per request:       41.200 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.2346 secs
  Slowest:	0.0204 secs
  Fastest:	0.0002 secs
  Average:	0.0022 secs
  Requests/sec:	42625.4135
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.2456 secs
  Slowest:	0.0232 secs
  Fastest:	0.0001 secs
  Average:	0.0024 secs
  Requests/sec:	40712.0414
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.4260 secs
  Slowest:	0.0212 secs
  Fastest:	0.0002 secs
  Average:	0.0041 secs
  Requests/sec:	23472.9037
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6417 secs
  Slowest:	0.0216 secs
  Fastest:	0.0004 secs
  Average:	0.0061 secs
  Requests/sec:	15582.7130
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8248 secs
  Slowest:	0.0385 secs
  Fastest:	0.0005 secs
  Average:	0.0077 secs
  Requests/sec:	12123.9315
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    57258.03 [#/sec] (mean)
Time per request:       1.746 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    70093.79 [#/sec] (mean)
Time per request:       1.427 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    11853.38 [#/sec] (mean)
Time per request:       8.436 [ms] (mean)
Time per request:       0.084 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    15031.31 [#/sec] (mean)
Time per request:       6.653 [ms] (mean)
Time per request:       0.067 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    68828.34 [#/sec] (mean)
Time per request:       1.453 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    76105.24 [#/sec] (mean)
Time per request:       1.314 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    81012.33 [#/sec] (mean)
Time per request:       1.234 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    67141.58 [#/sec] (mean)
Time per request:       1.489 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

# Django-Bolt Benchmark
Generated: Wed Oct  1 11:33:45 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    79276.37 [#/sec] (mean)
Time per request:       1.261 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    79770.26 [#/sec] (mean)
Time per request:       1.254 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    63905.11 [#/sec] (mean)
Time per request:       1.565 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    80130.13 [#/sec] (mean)
Time per request:       1.248 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    78846.94 [#/sec] (mean)
Time per request:       1.268 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    83064.76 [#/sec] (mean)
Time per request:       1.204 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2394.23 [#/sec] (mean)
Time per request:       41.767 [ms] (mean)
Time per request:       0.418 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.2060 secs
  Slowest:	0.0110 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	48532.6076
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.1877 secs
  Slowest:	0.0093 secs
  Fastest:	0.0001 secs
  Average:	0.0018 secs
  Requests/sec:	53273.1514
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.3609 secs
  Slowest:	0.0138 secs
  Fastest:	0.0003 secs
  Average:	0.0035 secs
  Requests/sec:	27709.8634
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6269 secs
  Slowest:	0.0221 secs
  Fastest:	0.0004 secs
  Average:	0.0059 secs
  Requests/sec:	15951.1734
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.7777 secs
  Slowest:	0.0265 secs
  Fastest:	0.0005 secs
  Average:	0.0074 secs
  Requests/sec:	12858.3147
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    59973.25 [#/sec] (mean)
Time per request:       1.667 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    76698.88 [#/sec] (mean)
Time per request:       1.304 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12282.84 [#/sec] (mean)
Time per request:       8.141 [ms] (mean)
Time per request:       0.081 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    15042.39 [#/sec] (mean)
Time per request:       6.648 [ms] (mean)
Time per request:       0.066 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    70370.01 [#/sec] (mean)
Time per request:       1.421 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    81932.96 [#/sec] (mean)
Time per request:       1.221 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    81505.57 [#/sec] (mean)
Time per request:       1.227 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    43292.48 [#/sec] (mean)
Time per request:       2.310 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

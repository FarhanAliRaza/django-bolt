# Django-Bolt Benchmark
Generated: Wed Oct  1 10:22:47 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    45943.64 [#/sec] (mean)
Time per request:       2.177 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    45183.85 [#/sec] (mean)
Time per request:       2.213 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    45294.78 [#/sec] (mean)
Time per request:       2.208 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    45401.92 [#/sec] (mean)
Time per request:       2.203 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    46752.35 [#/sec] (mean)
Time per request:       2.139 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    45914.31 [#/sec] (mean)
Time per request:       2.178 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2415.14 [#/sec] (mean)
Time per request:       41.406 [ms] (mean)
Time per request:       0.414 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3540 secs
  Slowest:	0.0107 secs
  Fastest:	0.0001 secs
  Average:	0.0035 secs
  Requests/sec:	28247.7667
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.3199 secs
  Slowest:	0.0095 secs
  Fastest:	0.0002 secs
  Average:	0.0031 secs
  Requests/sec:	31260.3498
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.6999 secs
  Slowest:	0.0164 secs
  Fastest:	0.0003 secs
  Average:	0.0068 secs
  Requests/sec:	14288.5198
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.0582 secs
  Slowest:	0.0205 secs
  Fastest:	0.0005 secs
  Average:	0.0102 secs
  Requests/sec:	9449.6184
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.4527 secs
  Slowest:	0.0291 secs
  Fastest:	0.0005 secs
  Average:	0.0139 secs
  Requests/sec:	6883.6402
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    38707.33 [#/sec] (mean)
Time per request:       2.583 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    39894.84 [#/sec] (mean)
Time per request:       2.507 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6923.97 [#/sec] (mean)
Time per request:       14.443 [ms] (mean)
Time per request:       0.144 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8394.36 [#/sec] (mean)
Time per request:       11.913 [ms] (mean)
Time per request:       0.119 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    35914.51 [#/sec] (mean)
Time per request:       2.784 [ms] (mean)
Time per request:       0.028 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    42970.46 [#/sec] (mean)
Time per request:       2.327 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    42386.89 [#/sec] (mean)
Time per request:       2.359 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    42695.08 [#/sec] (mean)
Time per request:       2.342 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

# Django-Bolt Benchmark
Generated: Wed Oct  1 10:22:07 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    42819.95 [#/sec] (mean)
Time per request:       2.335 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    41080.08 [#/sec] (mean)
Time per request:       2.434 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    41790.82 [#/sec] (mean)
Time per request:       2.393 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    42401.63 [#/sec] (mean)
Time per request:       2.358 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    43657.83 [#/sec] (mean)
Time per request:       2.291 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    43371.91 [#/sec] (mean)
Time per request:       2.306 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2421.50 [#/sec] (mean)
Time per request:       41.297 [ms] (mean)
Time per request:       0.413 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3934 secs
  Slowest:	0.0110 secs
  Fastest:	0.0001 secs
  Average:	0.0038 secs
  Requests/sec:	25419.1887
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.3512 secs
  Slowest:	0.0129 secs
  Fastest:	0.0001 secs
  Average:	0.0033 secs
  Requests/sec:	28472.6606
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.7353 secs
  Slowest:	0.0160 secs
  Fastest:	0.0003 secs
  Average:	0.0071 secs
  Requests/sec:	13600.7711
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.0830 secs
  Slowest:	0.0230 secs
  Fastest:	0.0004 secs
  Average:	0.0106 secs
  Requests/sec:	9233.8696
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5201 secs
  Slowest:	0.0345 secs
  Fastest:	0.0004 secs
  Average:	0.0140 secs
  Requests/sec:	6578.3189
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    36722.72 [#/sec] (mean)
Time per request:       2.723 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    37187.16 [#/sec] (mean)
Time per request:       2.689 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6891.60 [#/sec] (mean)
Time per request:       14.510 [ms] (mean)
Time per request:       0.145 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8242.79 [#/sec] (mean)
Time per request:       12.132 [ms] (mean)
Time per request:       0.121 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    32824.88 [#/sec] (mean)
Time per request:       3.046 [ms] (mean)
Time per request:       0.030 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    42916.61 [#/sec] (mean)
Time per request:       2.330 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    42115.02 [#/sec] (mean)
Time per request:       2.374 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    41857.47 [#/sec] (mean)
Time per request:       2.389 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

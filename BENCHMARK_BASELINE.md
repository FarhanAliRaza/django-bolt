# Django-Bolt Benchmark
Generated: Mon Sep 22 09:57:44 PM PKT 2025
Config: 4 processes × 1 workers | C=50 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    50060.07 [#/sec] (mean)
Time per request:       0.999 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    52865.02 [#/sec] (mean)
Time per request:       0.946 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    51670.51 [#/sec] (mean)
Time per request:       0.968 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    52230.23 [#/sec] (mean)
Time per request:       0.957 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    54626.00 [#/sec] (mean)
Time per request:       0.915 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    54445.77 [#/sec] (mean)
Time per request:       0.918 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    1206.08 [#/sec] (mean)
Time per request:       41.457 [ms] (mean)
Time per request:       0.829 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	8.2665 secs
  Slowest:	0.0595 secs
  Fastest:	0.0006 secs
  Average:	0.0404 secs
  Requests/sec:	1209.7003
Status code distribution:

### Server-Sent Events (/sse)
  Total:	8.2821 secs
  Slowest:	0.0460 secs
  Fastest:	0.0003 secs
  Average:	0.0412 secs
  Requests/sec:	1207.4200
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	8.2737 secs
  Slowest:	0.0454 secs
  Fastest:	0.0028 secs
  Average:	0.0412 secs
  Requests/sec:	1208.6459
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	8.3080 secs
  Slowest:	0.0601 secs
  Fastest:	0.0078 secs
  Average:	0.0414 secs
  Requests/sec:	1203.6555
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	9.9917 secs
  Slowest:	0.0770 secs
  Fastest:	0.0041 secs
  Average:	0.0482 secs
  Requests/sec:	1000.8275
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    49134.50 [#/sec] (mean)
Time per request:       1.018 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    46534.35 [#/sec] (mean)
Time per request:       1.074 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7268.02 [#/sec] (mean)
Time per request:       6.879 [ms] (mean)
Time per request:       0.138 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8714.39 [#/sec] (mean)
Time per request:       5.738 [ms] (mean)
Time per request:       0.115 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    40290.09 [#/sec] (mean)
Time per request:       1.241 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    48338.13 [#/sec] (mean)
Time per request:       1.034 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    49245.32 [#/sec] (mean)
Time per request:       1.015 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    49565.07 [#/sec] (mean)
Time per request:       1.009 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

# Django-Bolt Benchmark
Generated: Wed Sep 24 04:44:06 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    52928.26 [#/sec] (mean)
Time per request:       1.889 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    50245.20 [#/sec] (mean)
Time per request:       1.990 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    49618.93 [#/sec] (mean)
Time per request:       2.015 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    50924.28 [#/sec] (mean)
Time per request:       1.964 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    52619.95 [#/sec] (mean)
Time per request:       1.900 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    53135.25 [#/sec] (mean)
Time per request:       1.882 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2435.47 [#/sec] (mean)
Time per request:       41.060 [ms] (mean)
Time per request:       0.411 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3652 secs
  Slowest:	0.0108 secs
  Fastest:	0.0001 secs
  Average:	0.0035 secs
  Requests/sec:	27383.8580
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.3111 secs
  Slowest:	0.0089 secs
  Fastest:	0.0002 secs
  Average:	0.0030 secs
  Requests/sec:	32145.4866
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.2920 secs
  Slowest:	0.0108 secs
  Fastest:	0.0001 secs
  Average:	0.0028 secs
  Requests/sec:	34245.8936
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.0370 secs
  Slowest:	0.0181 secs
  Fastest:	0.0004 secs
  Average:	0.0100 secs
  Requests/sec:	9643.0331
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.3010 secs
  Slowest:	0.0090 secs
  Fastest:	0.0002 secs
  Average:	0.0029 secs
  Requests/sec:	33218.1170
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    47058.60 [#/sec] (mean)
Time per request:       2.125 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    46285.80 [#/sec] (mean)
Time per request:       2.160 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7145.38 [#/sec] (mean)
Time per request:       13.995 [ms] (mean)
Time per request:       0.140 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8549.20 [#/sec] (mean)
Time per request:       11.697 [ms] (mean)
Time per request:       0.117 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    40718.44 [#/sec] (mean)
Time per request:       2.456 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    48366.89 [#/sec] (mean)
Time per request:       2.068 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    49412.24 [#/sec] (mean)
Time per request:       2.024 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    50305.35 [#/sec] (mean)
Time per request:       1.988 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

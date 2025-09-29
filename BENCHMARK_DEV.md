# Django-Bolt Benchmark
Generated: Mon Sep 29 07:26:40 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    49963.78 [#/sec] (mean)
Time per request:       2.001 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    48572.46 [#/sec] (mean)
Time per request:       2.059 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    47821.03 [#/sec] (mean)
Time per request:       2.091 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    48898.08 [#/sec] (mean)
Time per request:       2.045 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    51173.93 [#/sec] (mean)
Time per request:       1.954 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    49371.99 [#/sec] (mean)
Time per request:       2.025 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2426.62 [#/sec] (mean)
Time per request:       41.210 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3593 secs
  Slowest:	0.0095 secs
  Fastest:	0.0002 secs
  Average:	0.0035 secs
  Requests/sec:	27831.8610
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.3185 secs
  Slowest:	0.0117 secs
  Fastest:	0.0001 secs
  Average:	0.0031 secs
  Requests/sec:	31396.6936
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.7031 secs
  Slowest:	0.0146 secs
  Fastest:	0.0003 secs
  Average:	0.0069 secs
  Requests/sec:	14222.6948
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.0626 secs
  Slowest:	0.0241 secs
  Fastest:	0.0004 secs
  Average:	0.0100 secs
  Requests/sec:	9411.2306
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.4784 secs
  Slowest:	0.0265 secs
  Fastest:	0.0004 secs
  Average:	0.0141 secs
  Requests/sec:	6763.9655
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    48196.95 [#/sec] (mean)
Time per request:       2.075 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    45476.46 [#/sec] (mean)
Time per request:       2.199 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7200.74 [#/sec] (mean)
Time per request:       13.887 [ms] (mean)
Time per request:       0.139 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8500.38 [#/sec] (mean)
Time per request:       11.764 [ms] (mean)
Time per request:       0.118 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    40616.56 [#/sec] (mean)
Time per request:       2.462 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    48439.76 [#/sec] (mean)
Time per request:       2.064 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    48510.72 [#/sec] (mean)
Time per request:       2.061 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    43437.28 [#/sec] (mean)
Time per request:       2.302 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

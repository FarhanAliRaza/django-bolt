# Django-Bolt Benchmark
Generated: Mon Sep 22 10:11:31 PM PKT 2025
Config: 4 processes × 1 workers | C=50 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    60351.85 [#/sec] (mean)
Time per request:       0.828 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    63646.43 [#/sec] (mean)
Time per request:       0.786 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    59238.55 [#/sec] (mean)
Time per request:       0.844 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    63642.38 [#/sec] (mean)
Time per request:       0.786 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    66432.38 [#/sec] (mean)
Time per request:       0.753 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    65836.69 [#/sec] (mean)
Time per request:       0.759 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    1204.09 [#/sec] (mean)
Time per request:       41.525 [ms] (mean)
Time per request:       0.831 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	8.3041 secs
  Slowest:	0.0546 secs
  Fastest:	0.0005 secs
  Average:	0.0406 secs
  Requests/sec:	1204.2235
Status code distribution:

### Server-Sent Events (/sse)
  Total:	8.2955 secs
  Slowest:	0.0460 secs
  Fastest:	0.0004 secs
  Average:	0.0411 secs
  Requests/sec:	1205.4760
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	8.3053 secs
  Slowest:	0.0460 secs
  Fastest:	0.0018 secs
  Average:	0.0412 secs
  Requests/sec:	1204.0456
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	8.3291 secs
  Slowest:	0.0768 secs
  Fastest:	0.0048 secs
  Average:	0.0414 secs
  Requests/sec:	1200.6110
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	9.8116 secs
  Slowest:	0.0720 secs
  Fastest:	0.0047 secs
  Average:	0.0477 secs
  Requests/sec:	1019.2044
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    62675.88 [#/sec] (mean)
Time per request:       0.798 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    56957.34 [#/sec] (mean)
Time per request:       0.878 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6964.50 [#/sec] (mean)
Time per request:       7.179 [ms] (mean)
Time per request:       0.144 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8386.29 [#/sec] (mean)
Time per request:       5.962 [ms] (mean)
Time per request:       0.119 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    40500.75 [#/sec] (mean)
Time per request:       1.235 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    46521.58 [#/sec] (mean)
Time per request:       1.075 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    47803.43 [#/sec] (mean)
Time per request:       1.046 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    48110.92 [#/sec] (mean)
Time per request:       1.039 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

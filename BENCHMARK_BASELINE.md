# Django-Bolt Benchmark
Generated: Mon Sep 29 05:26:46 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    55070.02 [#/sec] (mean)
Time per request:       1.816 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    53656.42 [#/sec] (mean)
Time per request:       1.864 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    53755.06 [#/sec] (mean)
Time per request:       1.860 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    54256.42 [#/sec] (mean)
Time per request:       1.843 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    55699.76 [#/sec] (mean)
Time per request:       1.795 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    56574.21 [#/sec] (mean)
Time per request:       1.768 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2424.63 [#/sec] (mean)
Time per request:       41.243 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3339 secs
  Slowest:	0.0089 secs
  Fastest:	0.0002 secs
  Average:	0.0033 secs
  Requests/sec:	29945.5760
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.2955 secs
  Slowest:	0.0083 secs
  Fastest:	0.0002 secs
  Average:	0.0029 secs
  Requests/sec:	33837.8972
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	4.1700 secs
  Slowest:	0.0671 secs
  Fastest:	0.0031 secs
  Average:	0.0413 secs
  Requests/sec:	2398.0827
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.0375 secs
  Slowest:	0.0224 secs
  Fastest:	0.0004 secs
  Average:	0.0101 secs
  Requests/sec:	9638.4244
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	4.4943 secs
  Slowest:	0.0978 secs
  Fastest:	0.0012 secs
  Average:	0.0437 secs
  Requests/sec:	2225.0495
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    49854.18 [#/sec] (mean)
Time per request:       2.006 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    48186.97 [#/sec] (mean)
Time per request:       2.075 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7336.61 [#/sec] (mean)
Time per request:       13.630 [ms] (mean)
Time per request:       0.136 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8579.20 [#/sec] (mean)
Time per request:       11.656 [ms] (mean)
Time per request:       0.117 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    43035.74 [#/sec] (mean)
Time per request:       2.324 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    51834.15 [#/sec] (mean)
Time per request:       1.929 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    52130.03 [#/sec] (mean)
Time per request:       1.918 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    52797.75 [#/sec] (mean)
Time per request:       1.894 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

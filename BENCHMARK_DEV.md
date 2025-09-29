# Django-Bolt Benchmark
Generated: Mon Sep 29 10:24:00 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    52730.10 [#/sec] (mean)
Time per request:       1.896 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    52528.18 [#/sec] (mean)
Time per request:       1.904 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    52677.33 [#/sec] (mean)
Time per request:       1.898 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    51337.86 [#/sec] (mean)
Time per request:       1.948 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    53138.35 [#/sec] (mean)
Time per request:       1.882 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    53970.04 [#/sec] (mean)
Time per request:       1.853 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2411.19 [#/sec] (mean)
Time per request:       41.473 [ms] (mean)
Time per request:       0.415 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3340 secs
  Slowest:	0.0106 secs
  Fastest:	0.0001 secs
  Average:	0.0032 secs
  Requests/sec:	29937.1109
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.3066 secs
  Slowest:	0.0140 secs
  Fastest:	0.0002 secs
  Average:	0.0029 secs
  Requests/sec:	32619.2698
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.6945 secs
  Slowest:	0.0171 secs
  Fastest:	0.0003 secs
  Average:	0.0066 secs
  Requests/sec:	14397.9502
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.0550 secs
  Slowest:	0.0244 secs
  Fastest:	0.0004 secs
  Average:	0.0103 secs
  Requests/sec:	9478.8926
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.4530 secs
  Slowest:	0.0245 secs
  Fastest:	0.0005 secs
  Average:	0.0142 secs
  Requests/sec:	6882.4266
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    48984.55 [#/sec] (mean)
Time per request:       2.041 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    47199.65 [#/sec] (mean)
Time per request:       2.119 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7061.22 [#/sec] (mean)
Time per request:       14.162 [ms] (mean)
Time per request:       0.142 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8524.71 [#/sec] (mean)
Time per request:       11.731 [ms] (mean)
Time per request:       0.117 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    42360.86 [#/sec] (mean)
Time per request:       2.361 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    50216.94 [#/sec] (mean)
Time per request:       1.991 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    50237.88 [#/sec] (mean)
Time per request:       1.991 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    50619.07 [#/sec] (mean)
Time per request:       1.976 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

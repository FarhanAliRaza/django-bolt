# Django-Bolt Benchmark
Generated: Mon Sep 29 05:28:55 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    54544.36 [#/sec] (mean)
Time per request:       1.833 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    54302.97 [#/sec] (mean)
Time per request:       1.842 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    52611.09 [#/sec] (mean)
Time per request:       1.901 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    52854.12 [#/sec] (mean)
Time per request:       1.892 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    54020.18 [#/sec] (mean)
Time per request:       1.851 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    53810.31 [#/sec] (mean)
Time per request:       1.858 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2424.32 [#/sec] (mean)
Time per request:       41.249 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3312 secs
  Slowest:	0.0109 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	30193.1825
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.3075 secs
  Slowest:	0.0187 secs
  Fastest:	0.0001 secs
  Average:	0.0030 secs
  Requests/sec:	32517.2447
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	4.1634 secs
  Slowest:	0.0660 secs
  Fastest:	0.0032 secs
  Average:	0.0413 secs
  Requests/sec:	2401.8654
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.0450 secs
  Slowest:	0.0215 secs
  Fastest:	0.0003 secs
  Average:	0.0099 secs
  Requests/sec:	9569.4291
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	4.5279 secs
  Slowest:	0.0799 secs
  Fastest:	0.0013 secs
  Average:	0.0442 secs
  Requests/sec:	2208.5112
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    49117.36 [#/sec] (mean)
Time per request:       2.036 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    48012.52 [#/sec] (mean)
Time per request:       2.083 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7270.96 [#/sec] (mean)
Time per request:       13.753 [ms] (mean)
Time per request:       0.138 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8721.24 [#/sec] (mean)
Time per request:       11.466 [ms] (mean)
Time per request:       0.115 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    42674.13 [#/sec] (mean)
Time per request:       2.343 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    51498.34 [#/sec] (mean)
Time per request:       1.942 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    51399.88 [#/sec] (mean)
Time per request:       1.946 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    53159.82 [#/sec] (mean)
Time per request:       1.881 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

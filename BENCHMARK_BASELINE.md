# Django-Bolt Benchmark
Generated: Mon Sep 29 11:55:16 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    43387.34 [#/sec] (mean)
Time per request:       2.305 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    41520.82 [#/sec] (mean)
Time per request:       2.408 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    42276.15 [#/sec] (mean)
Time per request:       2.365 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    42515.74 [#/sec] (mean)
Time per request:       2.352 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    45865.04 [#/sec] (mean)
Time per request:       2.180 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    44363.41 [#/sec] (mean)
Time per request:       2.254 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2425.50 [#/sec] (mean)
Time per request:       41.229 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3741 secs
  Slowest:	0.0097 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	26734.0185
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.3398 secs
  Slowest:	0.0098 secs
  Fastest:	0.0001 secs
  Average:	0.0033 secs
  Requests/sec:	29429.1702
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.7520 secs
  Slowest:	0.0178 secs
  Fastest:	0.0002 secs
  Average:	0.0069 secs
  Requests/sec:	13298.0870
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.0766 secs
  Slowest:	0.0216 secs
  Fastest:	0.0004 secs
  Average:	0.0104 secs
  Requests/sec:	9288.4592
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.4989 secs
  Slowest:	0.0308 secs
  Fastest:	0.0005 secs
  Average:	0.0144 secs
  Requests/sec:	6671.5183
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    40946.02 [#/sec] (mean)
Time per request:       2.442 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    37725.03 [#/sec] (mean)
Time per request:       2.651 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6989.33 [#/sec] (mean)
Time per request:       14.308 [ms] (mean)
Time per request:       0.143 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8323.75 [#/sec] (mean)
Time per request:       12.014 [ms] (mean)
Time per request:       0.120 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    33863.87 [#/sec] (mean)
Time per request:       2.953 [ms] (mean)
Time per request:       0.030 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    41216.38 [#/sec] (mean)
Time per request:       2.426 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    40970.17 [#/sec] (mean)
Time per request:       2.441 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    40824.16 [#/sec] (mean)
Time per request:       2.450 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

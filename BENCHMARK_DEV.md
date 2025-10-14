# Django-Bolt Benchmark
Generated: Wed Oct 15 12:30:01 AM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    78482.46 [#/sec] (mean)
Time per request:       1.274 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    78733.34 [#/sec] (mean)
Time per request:       1.270 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    79840.32 [#/sec] (mean)
Time per request:       1.252 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    79003.29 [#/sec] (mean)
Time per request:       1.266 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    79770.90 [#/sec] (mean)
Time per request:       1.254 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    83503.12 [#/sec] (mean)
Time per request:       1.198 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    32177.21 [#/sec] (mean)
Time per request:       3.108 [ms] (mean)
Time per request:       0.031 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2198 secs
  Slowest:	0.0109 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	45498.3335
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2264 secs
  Slowest:	0.0105 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	44161.2804
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3806 secs
  Slowest:	0.0132 secs
  Fastest:	0.0003 secs
  Average:	0.0036 secs
  Requests/sec:	26273.8985
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6706 secs
  Slowest:	0.0229 secs
  Fastest:	0.0004 secs
  Average:	0.0063 secs
  Requests/sec:	14911.6486
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8404 secs
  Slowest:	0.0290 secs
  Fastest:	0.0005 secs
  Average:	0.0078 secs
  Requests/sec:	11899.4476
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    79562.72 [#/sec] (mean)
Time per request:       1.257 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    73060.96 [#/sec] (mean)
Time per request:       1.369 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12469.65 [#/sec] (mean)
Time per request:       8.019 [ms] (mean)
Time per request:       0.080 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14637.20 [#/sec] (mean)
Time per request:       6.832 [ms] (mean)
Time per request:       0.068 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    66949.19 [#/sec] (mean)
Time per request:       1.494 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    12231.11 [#/sec] (mean)
Time per request:       8.176 [ms] (mean)
Time per request:       0.082 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    12694.74 [#/sec] (mean)
Time per request:       7.877 [ms] (mean)
Time per request:       0.079 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    77464.13 [#/sec] (mean)
Time per request:       1.291 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

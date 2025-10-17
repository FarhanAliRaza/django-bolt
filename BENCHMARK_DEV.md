# Django-Bolt Benchmark
Generated: Thu Oct 16 11:38:57 PM PKT 2025
Config: 10 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    66443.86 [#/sec] (mean)
Time per request:       1.505 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    77643.37 [#/sec] (mean)
Time per request:       1.288 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    76355.70 [#/sec] (mean)
Time per request:       1.310 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    82522.55 [#/sec] (mean)
Time per request:       1.212 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    78097.54 [#/sec] (mean)
Time per request:       1.280 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    80430.46 [#/sec] (mean)
Time per request:       1.243 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    25505.06 [#/sec] (mean)
Time per request:       3.921 [ms] (mean)
Time per request:       0.039 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2041 secs
  Slowest:	0.0089 secs
  Fastest:	0.0002 secs
  Average:	0.0019 secs
  Requests/sec:	48992.4219
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2004 secs
  Slowest:	0.0223 secs
  Fastest:	0.0002 secs
  Average:	0.0019 secs
  Requests/sec:	49910.9673
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3384 secs
  Slowest:	0.0137 secs
  Fastest:	0.0003 secs
  Average:	0.0032 secs
  Requests/sec:	29547.9374
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.5648 secs
  Slowest:	0.0219 secs
  Fastest:	0.0004 secs
  Average:	0.0053 secs
  Requests/sec:	17706.5818
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.7220 secs
  Slowest:	0.0379 secs
  Fastest:	0.0005 secs
  Average:	0.0069 secs
  Requests/sec:	13849.8900
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    80434.99 [#/sec] (mean)
Time per request:       1.243 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    69915.89 [#/sec] (mean)
Time per request:       1.430 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance

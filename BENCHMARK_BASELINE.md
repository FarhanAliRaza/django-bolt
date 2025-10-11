# Django-Bolt Benchmark
Generated: Sat Oct 11 06:43:04 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    80593.82 [#/sec] (mean)
Time per request:       1.241 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    76541.55 [#/sec] (mean)
Time per request:       1.306 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    76537.45 [#/sec] (mean)
Time per request:       1.307 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    75887.50 [#/sec] (mean)
Time per request:       1.318 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    78574.35 [#/sec] (mean)
Time per request:       1.273 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    80398.78 [#/sec] (mean)
Time per request:       1.244 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2426.92 [#/sec] (mean)
Time per request:       41.204 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2721 secs
  Slowest:	0.0110 secs
  Fastest:	0.0002 secs
  Average:	0.0026 secs
  Requests/sec:	36750.0307
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3472 secs
  Slowest:	0.0148 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	28805.9561
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.5735 secs
  Slowest:	0.1023 secs
  Fastest:	0.0003 secs
  Average:	0.0055 secs
  Requests/sec:	17436.4014
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.8617 secs
  Slowest:	0.0373 secs
  Fastest:	0.0004 secs
  Average:	0.0082 secs
  Requests/sec:	11604.3517
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8942 secs
  Slowest:	0.0258 secs
  Fastest:	0.0005 secs
  Average:	0.0085 secs
  Requests/sec:	11182.6880
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    58184.19 [#/sec] (mean)
Time per request:       1.719 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    56585.41 [#/sec] (mean)
Time per request:       1.767 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## ORM Performance

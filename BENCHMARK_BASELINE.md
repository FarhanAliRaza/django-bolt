# Django-Bolt Benchmark
Generated: Thu Oct 16 11:32:38 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    77972.10 [#/sec] (mean)
Time per request:       1.283 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    77184.32 [#/sec] (mean)
Time per request:       1.296 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    67764.45 [#/sec] (mean)
Time per request:       1.476 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    69515.89 [#/sec] (mean)
Time per request:       1.439 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    83867.29 [#/sec] (mean)
Time per request:       1.192 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    85279.85 [#/sec] (mean)
Time per request:       1.173 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    28136.28 [#/sec] (mean)
Time per request:       3.554 [ms] (mean)
Time per request:       0.036 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2327 secs
  Slowest:	0.0231 secs
  Fastest:	0.0002 secs
  Average:	0.0022 secs
  Requests/sec:	42966.1245
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1949 secs
  Slowest:	0.0105 secs
  Fastest:	0.0001 secs
  Average:	0.0018 secs
  Requests/sec:	51313.5857
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3749 secs
  Slowest:	0.0172 secs
  Fastest:	0.0003 secs
  Average:	0.0036 secs
  Requests/sec:	26674.3852
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6586 secs
  Slowest:	0.0264 secs
  Fastest:	0.0004 secs
  Average:	0.0063 secs
  Requests/sec:	15184.4297
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
(chat async stream timed out after 60s)

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    79822.47 [#/sec] (mean)
Time per request:       1.253 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    70452.80 [#/sec] (mean)
Time per request:       1.419 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance

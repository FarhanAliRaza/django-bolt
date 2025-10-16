# Django-Bolt Benchmark
Generated: Thu Oct 16 11:33:07 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    75986.69 [#/sec] (mean)
Time per request:       1.316 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    71224.56 [#/sec] (mean)
Time per request:       1.404 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    75382.38 [#/sec] (mean)
Time per request:       1.327 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    73473.77 [#/sec] (mean)
Time per request:       1.361 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    81432.56 [#/sec] (mean)
Time per request:       1.228 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    80192.46 [#/sec] (mean)
Time per request:       1.247 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    27379.56 [#/sec] (mean)
Time per request:       3.652 [ms] (mean)
Time per request:       0.037 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2695 secs
  Slowest:	0.0155 secs
  Fastest:	0.0001 secs
  Average:	0.0026 secs
  Requests/sec:	37100.4056
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2172 secs
  Slowest:	0.0263 secs
  Fastest:	0.0001 secs
  Average:	0.0021 secs
  Requests/sec:	46046.3261
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3489 secs
  Slowest:	0.0309 secs
  Fastest:	0.0003 secs
  Average:	0.0033 secs
  Requests/sec:	28663.4417
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.5498 secs
  Slowest:	0.0225 secs
  Fastest:	0.0004 secs
  Average:	0.0052 secs
  Requests/sec:	18187.2470
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
(chat async stream timed out after 60s)

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    79577.29 [#/sec] (mean)
Time per request:       1.257 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)

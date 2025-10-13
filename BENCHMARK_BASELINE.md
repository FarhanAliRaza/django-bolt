# Django-Bolt Benchmark
Generated: Mon Oct 13 09:29:15 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    73983.10 [#/sec] (mean)
Time per request:       1.352 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    62557.08 [#/sec] (mean)
Time per request:       1.599 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    76628.35 [#/sec] (mean)
Time per request:       1.305 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    72077.79 [#/sec] (mean)
Time per request:       1.387 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    76202.09 [#/sec] (mean)
Time per request:       1.312 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    79288.31 [#/sec] (mean)
Time per request:       1.261 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    29538.78 [#/sec] (mean)
Time per request:       3.385 [ms] (mean)
Time per request:       0.034 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2358 secs
  Slowest:	0.0144 secs
  Fastest:	0.0001 secs
  Average:	0.0022 secs
  Requests/sec:	42416.0812
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2358 secs
  Slowest:	0.0211 secs
  Fastest:	0.0002 secs
  Average:	0.0022 secs
  Requests/sec:	42414.1814
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3784 secs
  Slowest:	0.0137 secs
  Fastest:	0.0003 secs
  Average:	0.0036 secs
  Requests/sec:	26425.3220
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6284 secs
  Slowest:	0.0181 secs
  Fastest:	0.0004 secs
  Average:	0.0060 secs
  Requests/sec:	15914.5855
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.7992 secs
  Slowest:	0.0283 secs
  Fastest:	0.0004 secs
  Average:	0.0075 secs
  Requests/sec:	12512.4358
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    77941.11 [#/sec] (mean)
Time per request:       1.283 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    72430.18 [#/sec] (mean)
Time per request:       1.381 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance

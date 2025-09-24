# Django-Bolt Benchmark
Generated: Wed Sep 24 04:42:26 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    18898.05 [#/sec] (mean)
Time per request:       5.292 [ms] (mean)
Time per request:       0.053 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    19258.03 [#/sec] (mean)
Time per request:       5.193 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    20070.37 [#/sec] (mean)
Time per request:       4.982 [ms] (mean)
Time per request:       0.050 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    19177.99 [#/sec] (mean)
Time per request:       5.214 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    19904.78 [#/sec] (mean)
Time per request:       5.024 [ms] (mean)
Time per request:       0.050 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    20215.17 [#/sec] (mean)
Time per request:       4.947 [ms] (mean)
Time per request:       0.049 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    8503.75 [#/sec] (mean)
Time per request:       11.760 [ms] (mean)
Time per request:       0.118 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.5991 secs
  Slowest:	0.0322 secs
  Fastest:	0.0003 secs
  Average:	0.0057 secs
  Requests/sec:	16690.9219
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.3742 secs
  Slowest:	0.0181 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	26721.6240
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.2008 secs
  Slowest:	0.0144 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	49798.6005
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.9555 secs
  Slowest:	0.0552 secs
  Fastest:	0.0004 secs
  Average:	0.0091 secs
  Requests/sec:	10465.3110
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.2060 secs
  Slowest:	0.0099 secs
  Fastest:	0.0001 secs
  Average:	0.0020 secs
  Requests/sec:	48538.5574
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    19774.14 [#/sec] (mean)
Time per request:       5.057 [ms] (mean)
Time per request:       0.051 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    19657.41 [#/sec] (mean)
Time per request:       5.087 [ms] (mean)
Time per request:       0.051 [ms] (mean, across all concurrent requests)

## ORM Performance

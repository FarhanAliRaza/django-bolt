# Django-Bolt Benchmark
Generated: Thu Oct 16 11:38:33 PM PKT 2025
Config: 20 processes × 2 workers | C=1000 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    47860.17 [#/sec] (mean)
Time per request:       20.894 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    50693.23 [#/sec] (mean)
Time per request:       19.727 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    47017.67 [#/sec] (mean)
Time per request:       21.269 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    46703.44 [#/sec] (mean)
Time per request:       21.412 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    42515.02 [#/sec] (mean)
Time per request:       23.521 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    49567.28 [#/sec] (mean)
Time per request:       20.175 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    12850.99 [#/sec] (mean)
Time per request:       77.815 [ms] (mean)
Time per request:       0.078 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2821 secs
  Slowest:	0.2010 secs
  Fastest:	0.0002 secs
  Average:	0.0249 secs
  Requests/sec:	35446.1412
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2779 secs
  Slowest:	0.1934 secs
  Fastest:	0.0002 secs
  Average:	0.0215 secs
  Requests/sec:	35981.0768
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.4057 secs
  Slowest:	0.2242 secs
  Fastest:	0.0003 secs
  Average:	0.0344 secs
  Requests/sec:	24649.9171
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6053 secs
  Slowest:	0.2751 secs
  Fastest:	0.0004 secs
  Average:	0.0520 secs
  Requests/sec:	16520.2878
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.7439 secs
  Slowest:	0.3109 secs
  Fastest:	0.0007 secs
  Average:	0.0656 secs
  Requests/sec:	13442.7099
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    46590.72 [#/sec] (mean)
Time per request:       21.463 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    46575.53 [#/sec] (mean)
Time per request:       21.471 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

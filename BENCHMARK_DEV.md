# Django-Bolt Benchmark
Generated: Mon Oct 13 09:30:40 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    73656.14 [#/sec] (mean)
Time per request:       1.358 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    78275.44 [#/sec] (mean)
Time per request:       1.278 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    78796.62 [#/sec] (mean)
Time per request:       1.269 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    75236.05 [#/sec] (mean)
Time per request:       1.329 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    77021.43 [#/sec] (mean)
Time per request:       1.298 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    76678.30 [#/sec] (mean)
Time per request:       1.304 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    27468.75 [#/sec] (mean)
Time per request:       3.640 [ms] (mean)
Time per request:       0.036 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2461 secs
  Slowest:	0.0333 secs
  Fastest:	0.0002 secs
  Average:	0.0023 secs
  Requests/sec:	40639.6884
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1981 secs
  Slowest:	0.0096 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	50470.8652
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.4104 secs
  Slowest:	0.0198 secs
  Fastest:	0.0002 secs
  Average:	0.0039 secs
  Requests/sec:	24364.0018
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6758 secs
  Slowest:	0.0205 secs
  Fastest:	0.0005 secs
  Average:	0.0063 secs
  Requests/sec:	14796.3945
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8492 secs
  Slowest:	0.0268 secs
  Fastest:	0.0005 secs
  Average:	0.0080 secs
  Requests/sec:	11776.3194
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    71055.03 [#/sec] (mean)
Time per request:       1.407 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    64433.40 [#/sec] (mean)
Time per request:       1.552 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12642.74 [#/sec] (mean)
Time per request:       7.910 [ms] (mean)
Time per request:       0.079 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14955.69 [#/sec] (mean)
Time per request:       6.686 [ms] (mean)
Time per request:       0.067 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    62990.54 [#/sec] (mean)
Time per request:       1.588 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    12391.97 [#/sec] (mean)
Time per request:       8.070 [ms] (mean)
Time per request:       0.081 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    12620.30 [#/sec] (mean)
Time per request:       7.924 [ms] (mean)
Time per request:       0.079 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    73888.53 [#/sec] (mean)
Time per request:       1.353 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

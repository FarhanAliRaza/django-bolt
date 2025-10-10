# Django-Bolt Benchmark
Generated: Fri Oct 10 09:32:57 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    84381.78 [#/sec] (mean)
Time per request:       1.185 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    75646.97 [#/sec] (mean)
Time per request:       1.322 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    81452.46 [#/sec] (mean)
Time per request:       1.228 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    78829.54 [#/sec] (mean)
Time per request:       1.269 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    77340.12 [#/sec] (mean)
Time per request:       1.293 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    84278.66 [#/sec] (mean)
Time per request:       1.187 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2420.15 [#/sec] (mean)
Time per request:       41.320 [ms] (mean)
Time per request:       0.413 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2219 secs
  Slowest:	0.0095 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	45067.5579
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2067 secs
  Slowest:	0.0095 secs
  Fastest:	0.0002 secs
  Average:	0.0019 secs
  Requests/sec:	48377.2348
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.4074 secs
  Slowest:	0.0195 secs
  Fastest:	0.0003 secs
  Average:	0.0039 secs
  Requests/sec:	24547.3004
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6584 secs
  Slowest:	0.0393 secs
  Fastest:	0.0004 secs
  Average:	0.0062 secs
  Requests/sec:	15187.6877
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8366 secs
  Slowest:	0.0480 secs
  Fastest:	0.0005 secs
  Average:	0.0079 secs
  Requests/sec:	11952.9597
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    64409.75 [#/sec] (mean)
Time per request:       1.553 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    62373.69 [#/sec] (mean)
Time per request:       1.603 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12326.87 [#/sec] (mean)
Time per request:       8.112 [ms] (mean)
Time per request:       0.081 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14449.97 [#/sec] (mean)
Time per request:       6.920 [ms] (mean)
Time per request:       0.069 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    63927.99 [#/sec] (mean)
Time per request:       1.564 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    21614.94 [#/sec] (mean)
Time per request:       4.626 [ms] (mean)
Time per request:       0.046 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    22523.44 [#/sec] (mean)
Time per request:       4.440 [ms] (mean)
Time per request:       0.044 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    72519.47 [#/sec] (mean)
Time per request:       1.379 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

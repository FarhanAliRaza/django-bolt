# Django-Bolt Benchmark
Generated: Fri Oct 10 05:47:13 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    68547.61 [#/sec] (mean)
Time per request:       1.459 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    69148.64 [#/sec] (mean)
Time per request:       1.446 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    75927.84 [#/sec] (mean)
Time per request:       1.317 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    76145.80 [#/sec] (mean)
Time per request:       1.313 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    76315.49 [#/sec] (mean)
Time per request:       1.310 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    78278.50 [#/sec] (mean)
Time per request:       1.277 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2427.32 [#/sec] (mean)
Time per request:       41.198 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2277 secs
  Slowest:	0.0096 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	43925.3736
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1975 secs
  Slowest:	0.0084 secs
  Fastest:	0.0002 secs
  Average:	0.0019 secs
  Requests/sec:	50644.6710
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3828 secs
  Slowest:	0.0157 secs
  Fastest:	0.0003 secs
  Average:	0.0037 secs
  Requests/sec:	26126.6267
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6708 secs
  Slowest:	0.0220 secs
  Fastest:	0.0004 secs
  Average:	0.0063 secs
  Requests/sec:	14906.9249
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8262 secs
  Slowest:	0.0435 secs
  Fastest:	0.0005 secs
  Average:	0.0077 secs
  Requests/sec:	12103.9923
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    62242.86 [#/sec] (mean)
Time per request:       1.607 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    65065.20 [#/sec] (mean)
Time per request:       1.537 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    11458.28 [#/sec] (mean)
Time per request:       8.727 [ms] (mean)
Time per request:       0.087 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14098.82 [#/sec] (mean)
Time per request:       7.093 [ms] (mean)
Time per request:       0.071 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    60856.86 [#/sec] (mean)
Time per request:       1.643 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    13835.76 [#/sec] (mean)
Time per request:       7.228 [ms] (mean)
Time per request:       0.072 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    14212.54 [#/sec] (mean)
Time per request:       7.036 [ms] (mean)
Time per request:       0.070 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    70103.12 [#/sec] (mean)
Time per request:       1.426 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

# Django-Bolt Benchmark
Generated: Sat Oct 11 09:10:17 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    80010.24 [#/sec] (mean)
Time per request:       1.250 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    79472.94 [#/sec] (mean)
Time per request:       1.258 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    63339.65 [#/sec] (mean)
Time per request:       1.579 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    77683.18 [#/sec] (mean)
Time per request:       1.287 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    81324.62 [#/sec] (mean)
Time per request:       1.230 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    80712.20 [#/sec] (mean)
Time per request:       1.239 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2425.36 [#/sec] (mean)
Time per request:       41.231 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2240 secs
  Slowest:	0.0090 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	44652.0383
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2030 secs
  Slowest:	0.0080 secs
  Fastest:	0.0002 secs
  Average:	0.0019 secs
  Requests/sec:	49255.1758
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3881 secs
  Slowest:	0.0146 secs
  Fastest:	0.0003 secs
  Average:	0.0037 secs
  Requests/sec:	25769.3849
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6688 secs
  Slowest:	0.0204 secs
  Fastest:	0.0004 secs
  Average:	0.0062 secs
  Requests/sec:	14951.3505
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8278 secs
  Slowest:	0.0266 secs
  Fastest:	0.0005 secs
  Average:	0.0077 secs
  Requests/sec:	12080.6903
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    76477.74 [#/sec] (mean)
Time per request:       1.308 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    70156.73 [#/sec] (mean)
Time per request:       1.425 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12191.54 [#/sec] (mean)
Time per request:       8.202 [ms] (mean)
Time per request:       0.082 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14502.72 [#/sec] (mean)
Time per request:       6.895 [ms] (mean)
Time per request:       0.069 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    60682.19 [#/sec] (mean)
Time per request:       1.648 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    21055.91 [#/sec] (mean)
Time per request:       4.749 [ms] (mean)
Time per request:       0.047 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    21448.00 [#/sec] (mean)
Time per request:       4.662 [ms] (mean)
Time per request:       0.047 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    73789.30 [#/sec] (mean)
Time per request:       1.355 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

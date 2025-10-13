# Django-Bolt Benchmark
Generated: Sat Oct 11 08:17:31 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    70475.64 [#/sec] (mean)
Time per request:       1.419 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    80534.75 [#/sec] (mean)
Time per request:       1.242 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    79703.50 [#/sec] (mean)
Time per request:       1.255 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    77419.16 [#/sec] (mean)
Time per request:       1.292 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    79023.27 [#/sec] (mean)
Time per request:       1.265 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    79368.86 [#/sec] (mean)
Time per request:       1.260 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2407.61 [#/sec] (mean)
Time per request:       41.535 [ms] (mean)
Time per request:       0.415 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2350 secs
  Slowest:	0.0348 secs
  Fastest:	0.0002 secs
  Average:	0.0022 secs
  Requests/sec:	42555.9578
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2145 secs
  Slowest:	0.0120 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	46618.5546
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.4365 secs
  Slowest:	0.0593 secs
  Fastest:	0.0003 secs
  Average:	0.0042 secs
  Requests/sec:	22908.4015
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6559 secs
  Slowest:	0.0228 secs
  Fastest:	0.0004 secs
  Average:	0.0061 secs
  Requests/sec:	15247.0971
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8199 secs
  Slowest:	0.0269 secs
  Fastest:	0.0005 secs
  Average:	0.0078 secs
  Requests/sec:	12195.9254
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    75351.14 [#/sec] (mean)
Time per request:       1.327 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    68917.99 [#/sec] (mean)
Time per request:       1.451 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12276.55 [#/sec] (mean)
Time per request:       8.146 [ms] (mean)
Time per request:       0.081 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14851.74 [#/sec] (mean)
Time per request:       6.733 [ms] (mean)
Time per request:       0.067 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    45614.61 [#/sec] (mean)
Time per request:       2.192 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    20191.01 [#/sec] (mean)
Time per request:       4.953 [ms] (mean)
Time per request:       0.050 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    21878.87 [#/sec] (mean)
Time per request:       4.571 [ms] (mean)
Time per request:       0.046 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    27013.59 [#/sec] (mean)
Time per request:       3.702 [ms] (mean)
Time per request:       0.037 [ms] (mean, across all concurrent requests)

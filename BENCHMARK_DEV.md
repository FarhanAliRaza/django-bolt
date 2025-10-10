# Django-Bolt Benchmark
Generated: Fri Oct 10 11:30:11 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    81195.19 [#/sec] (mean)
Time per request:       1.232 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    78653.45 [#/sec] (mean)
Time per request:       1.271 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    80119.86 [#/sec] (mean)
Time per request:       1.248 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    75948.02 [#/sec] (mean)
Time per request:       1.317 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    81445.83 [#/sec] (mean)
Time per request:       1.228 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    80305.16 [#/sec] (mean)
Time per request:       1.245 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2420.79 [#/sec] (mean)
Time per request:       41.309 [ms] (mean)
Time per request:       0.413 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2242 secs
  Slowest:	0.0116 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	44612.1383
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2139 secs
  Slowest:	0.0215 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	46751.5742
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.4358 secs
  Slowest:	0.0558 secs
  Fastest:	0.0003 secs
  Average:	0.0041 secs
  Requests/sec:	22947.8232
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6885 secs
  Slowest:	0.0272 secs
  Fastest:	0.0004 secs
  Average:	0.0067 secs
  Requests/sec:	14524.2432
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8584 secs
  Slowest:	0.0274 secs
  Fastest:	0.0005 secs
  Average:	0.0079 secs
  Requests/sec:	11649.3196
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    76297.44 [#/sec] (mean)
Time per request:       1.311 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    69799.26 [#/sec] (mean)
Time per request:       1.433 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    11666.07 [#/sec] (mean)
Time per request:       8.572 [ms] (mean)
Time per request:       0.086 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14218.99 [#/sec] (mean)
Time per request:       7.033 [ms] (mean)
Time per request:       0.070 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    62471.89 [#/sec] (mean)
Time per request:       1.601 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    20952.63 [#/sec] (mean)
Time per request:       4.773 [ms] (mean)
Time per request:       0.048 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    21275.28 [#/sec] (mean)
Time per request:       4.700 [ms] (mean)
Time per request:       0.047 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    68052.21 [#/sec] (mean)
Time per request:       1.469 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

# Django-Bolt Benchmark
Generated: Fri Oct 10 07:59:19 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    45024.56 [#/sec] (mean)
Time per request:       2.221 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    43734.77 [#/sec] (mean)
Time per request:       2.287 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    47480.68 [#/sec] (mean)
Time per request:       2.106 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    42326.61 [#/sec] (mean)
Time per request:       2.363 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    45344.28 [#/sec] (mean)
Time per request:       2.205 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    46042.64 [#/sec] (mean)
Time per request:       2.172 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2424.46 [#/sec] (mean)
Time per request:       41.246 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3924 secs
  Slowest:	0.0092 secs
  Fastest:	0.0002 secs
  Average:	0.0038 secs
  Requests/sec:	25481.0968
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3572 secs
  Slowest:	0.0118 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	27996.5166
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7607 secs
  Slowest:	0.0170 secs
  Fastest:	0.0003 secs
  Average:	0.0075 secs
  Requests/sec:	13146.1879
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1851 secs
  Slowest:	0.0450 secs
  Fastest:	0.0004 secs
  Average:	0.0115 secs
  Requests/sec:	8438.1352
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5543 secs
  Slowest:	0.0505 secs
  Fastest:	0.0005 secs
  Average:	0.0149 secs
  Requests/sec:	6433.8914
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    42687.43 [#/sec] (mean)
Time per request:       2.343 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    34956.72 [#/sec] (mean)
Time per request:       2.861 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6640.26 [#/sec] (mean)
Time per request:       15.060 [ms] (mean)
Time per request:       0.151 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    7902.73 [#/sec] (mean)
Time per request:       12.654 [ms] (mean)
Time per request:       0.127 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    31080.61 [#/sec] (mean)
Time per request:       3.217 [ms] (mean)
Time per request:       0.032 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    11626.03 [#/sec] (mean)
Time per request:       8.601 [ms] (mean)
Time per request:       0.086 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    11872.93 [#/sec] (mean)
Time per request:       8.423 [ms] (mean)
Time per request:       0.084 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    40416.29 [#/sec] (mean)
Time per request:       2.474 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

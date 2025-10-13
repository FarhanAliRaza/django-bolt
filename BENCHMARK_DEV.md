# Django-Bolt Benchmark
Generated: Mon Oct 13 06:09:54 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    41046.52 [#/sec] (mean)
Time per request:       2.436 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    43108.84 [#/sec] (mean)
Time per request:       2.320 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    42516.46 [#/sec] (mean)
Time per request:       2.352 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    41111.66 [#/sec] (mean)
Time per request:       2.432 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    44303.85 [#/sec] (mean)
Time per request:       2.257 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    48163.52 [#/sec] (mean)
Time per request:       2.076 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2428.78 [#/sec] (mean)
Time per request:       41.173 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3826 secs
  Slowest:	0.0113 secs
  Fastest:	0.0002 secs
  Average:	0.0037 secs
  Requests/sec:	26137.8142
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3496 secs
  Slowest:	0.0104 secs
  Fastest:	0.0002 secs
  Average:	0.0033 secs
  Requests/sec:	28606.5534
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7605 secs
  Slowest:	0.0182 secs
  Fastest:	0.0003 secs
  Average:	0.0073 secs
  Requests/sec:	13148.4789
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1473 secs
  Slowest:	0.0219 secs
  Fastest:	0.0004 secs
  Average:	0.0110 secs
  Requests/sec:	8716.3943
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5363 secs
  Slowest:	0.0312 secs
  Fastest:	0.0005 secs
  Average:	0.0145 secs
  Requests/sec:	6509.2250
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    42960.68 [#/sec] (mean)
Time per request:       2.328 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    35981.06 [#/sec] (mean)
Time per request:       2.779 [ms] (mean)
Time per request:       0.028 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7070.79 [#/sec] (mean)
Time per request:       14.143 [ms] (mean)
Time per request:       0.141 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8206.41 [#/sec] (mean)
Time per request:       12.186 [ms] (mean)
Time per request:       0.122 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    34371.11 [#/sec] (mean)
Time per request:       2.909 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    12102.67 [#/sec] (mean)
Time per request:       8.263 [ms] (mean)
Time per request:       0.083 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    12183.65 [#/sec] (mean)
Time per request:       8.208 [ms] (mean)
Time per request:       0.082 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    40529.97 [#/sec] (mean)
Time per request:       2.467 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

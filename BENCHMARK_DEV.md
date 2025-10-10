# Django-Bolt Benchmark
Generated: Fri Oct 10 08:01:48 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    45422.54 [#/sec] (mean)
Time per request:       2.202 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    44109.21 [#/sec] (mean)
Time per request:       2.267 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    45410.17 [#/sec] (mean)
Time per request:       2.202 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    43196.17 [#/sec] (mean)
Time per request:       2.315 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    45851.58 [#/sec] (mean)
Time per request:       2.181 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    45106.61 [#/sec] (mean)
Time per request:       2.217 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2421.73 [#/sec] (mean)
Time per request:       41.293 [ms] (mean)
Time per request:       0.413 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3864 secs
  Slowest:	0.0122 secs
  Fastest:	0.0002 secs
  Average:	0.0037 secs
  Requests/sec:	25882.2362
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3415 secs
  Slowest:	0.0107 secs
  Fastest:	0.0002 secs
  Average:	0.0033 secs
  Requests/sec:	29285.4244
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7330 secs
  Slowest:	0.0390 secs
  Fastest:	0.0003 secs
  Average:	0.0070 secs
  Requests/sec:	13642.7822
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.2151 secs
  Slowest:	0.0516 secs
  Fastest:	0.0004 secs
  Average:	0.0116 secs
  Requests/sec:	8230.0009
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5346 secs
  Slowest:	0.0284 secs
  Fastest:	0.0005 secs
  Average:	0.0146 secs
  Requests/sec:	6516.4505
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    39316.68 [#/sec] (mean)
Time per request:       2.543 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    36544.63 [#/sec] (mean)
Time per request:       2.736 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6864.20 [#/sec] (mean)
Time per request:       14.568 [ms] (mean)
Time per request:       0.146 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    7768.71 [#/sec] (mean)
Time per request:       12.872 [ms] (mean)
Time per request:       0.129 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    35250.12 [#/sec] (mean)
Time per request:       2.837 [ms] (mean)
Time per request:       0.028 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    11691.12 [#/sec] (mean)
Time per request:       8.554 [ms] (mean)
Time per request:       0.086 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    12357.69 [#/sec] (mean)
Time per request:       8.092 [ms] (mean)
Time per request:       0.081 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    42564.60 [#/sec] (mean)
Time per request:       2.349 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

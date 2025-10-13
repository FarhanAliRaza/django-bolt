# Django-Bolt Benchmark
Generated: Mon Oct 13 07:18:07 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    39705.39 [#/sec] (mean)
Time per request:       2.519 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    41378.40 [#/sec] (mean)
Time per request:       2.417 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    40942.33 [#/sec] (mean)
Time per request:       2.442 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    41100.34 [#/sec] (mean)
Time per request:       2.433 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    43650.01 [#/sec] (mean)
Time per request:       2.291 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    43536.56 [#/sec] (mean)
Time per request:       2.297 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    33851.26 [#/sec] (mean)
Time per request:       2.954 [ms] (mean)
Time per request:       0.030 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.4136 secs
  Slowest:	0.0277 secs
  Fastest:	0.0002 secs
  Average:	0.0039 secs
  Requests/sec:	24176.3941
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3336 secs
  Slowest:	0.0108 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	29978.9865
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7444 secs
  Slowest:	0.0186 secs
  Fastest:	0.0003 secs
  Average:	0.0072 secs
  Requests/sec:	13432.8842
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.2342 secs
  Slowest:	0.0290 secs
  Fastest:	0.0004 secs
  Average:	0.0119 secs
  Requests/sec:	8102.4329
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5724 secs
  Slowest:	0.0363 secs
  Fastest:	0.0004 secs
  Average:	0.0147 secs
  Requests/sec:	6359.7720
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    39565.73 [#/sec] (mean)
Time per request:       2.527 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    37110.43 [#/sec] (mean)
Time per request:       2.695 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6748.54 [#/sec] (mean)
Time per request:       14.818 [ms] (mean)
Time per request:       0.148 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    7746.17 [#/sec] (mean)
Time per request:       12.910 [ms] (mean)
Time per request:       0.129 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    34364.26 [#/sec] (mean)
Time per request:       2.910 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    11862.45 [#/sec] (mean)
Time per request:       8.430 [ms] (mean)
Time per request:       0.084 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    12241.72 [#/sec] (mean)
Time per request:       8.169 [ms] (mean)
Time per request:       0.082 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    40814.33 [#/sec] (mean)
Time per request:       2.450 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

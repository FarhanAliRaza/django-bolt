# Django-Bolt Benchmark
Generated: Mon Sep 29 09:47:03 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    53559.57 [#/sec] (mean)
Time per request:       1.867 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    52305.91 [#/sec] (mean)
Time per request:       1.912 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    51496.49 [#/sec] (mean)
Time per request:       1.942 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    50315.22 [#/sec] (mean)
Time per request:       1.987 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    53409.67 [#/sec] (mean)
Time per request:       1.872 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    54271.43 [#/sec] (mean)
Time per request:       1.843 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2421.86 [#/sec] (mean)
Time per request:       41.291 [ms] (mean)
Time per request:       0.413 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3411 secs
  Slowest:	0.0131 secs
  Fastest:	0.0002 secs
  Average:	0.0033 secs
  Requests/sec:	29319.5693
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.2981 secs
  Slowest:	0.0105 secs
  Fastest:	0.0001 secs
  Average:	0.0029 secs
  Requests/sec:	33542.5426
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.7008 secs
  Slowest:	0.0178 secs
  Fastest:	0.0002 secs
  Average:	0.0067 secs
  Requests/sec:	14269.0776
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1146 secs
  Slowest:	0.0252 secs
  Fastest:	0.0004 secs
  Average:	0.0101 secs
  Requests/sec:	8971.9169
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.4549 secs
  Slowest:	0.0256 secs
  Fastest:	0.0005 secs
  Average:	0.0141 secs
  Requests/sec:	6873.2881
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    48064.21 [#/sec] (mean)
Time per request:       2.081 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    46532.62 [#/sec] (mean)
Time per request:       2.149 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7210.01 [#/sec] (mean)
Time per request:       13.870 [ms] (mean)
Time per request:       0.139 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8517.61 [#/sec] (mean)
Time per request:       11.740 [ms] (mean)
Time per request:       0.117 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    41633.01 [#/sec] (mean)
Time per request:       2.402 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    50350.69 [#/sec] (mean)
Time per request:       1.986 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    49677.59 [#/sec] (mean)
Time per request:       2.013 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    49985.00 [#/sec] (mean)
Time per request:       2.001 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

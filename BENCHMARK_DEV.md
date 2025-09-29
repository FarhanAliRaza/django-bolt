# Django-Bolt Benchmark
Generated: Mon Sep 29 07:57:29 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    53383.44 [#/sec] (mean)
Time per request:       1.873 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    51953.18 [#/sec] (mean)
Time per request:       1.925 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    51262.33 [#/sec] (mean)
Time per request:       1.951 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    52524.87 [#/sec] (mean)
Time per request:       1.904 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    53855.81 [#/sec] (mean)
Time per request:       1.857 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    54019.31 [#/sec] (mean)
Time per request:       1.851 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2427.69 [#/sec] (mean)
Time per request:       41.191 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3419 secs
  Slowest:	0.0094 secs
  Fastest:	0.0002 secs
  Average:	0.0033 secs
  Requests/sec:	29245.7381
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.3210 secs
  Slowest:	0.0153 secs
  Fastest:	0.0002 secs
  Average:	0.0031 secs
  Requests/sec:	31152.1949
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.7101 secs
  Slowest:	0.0206 secs
  Fastest:	0.0003 secs
  Average:	0.0066 secs
  Requests/sec:	14082.9453
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1086 secs
  Slowest:	0.0239 secs
  Fastest:	0.0004 secs
  Average:	0.0105 secs
  Requests/sec:	9020.0129
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.4530 secs
  Slowest:	0.0296 secs
  Fastest:	0.0005 secs
  Average:	0.0142 secs
  Requests/sec:	6882.2131
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    48641.92 [#/sec] (mean)
Time per request:       2.056 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    46744.48 [#/sec] (mean)
Time per request:       2.139 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6874.24 [#/sec] (mean)
Time per request:       14.547 [ms] (mean)
Time per request:       0.145 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8310.04 [#/sec] (mean)
Time per request:       12.034 [ms] (mean)
Time per request:       0.120 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    41676.91 [#/sec] (mean)
Time per request:       2.399 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    49633.70 [#/sec] (mean)
Time per request:       2.015 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    49135.94 [#/sec] (mean)
Time per request:       2.035 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    48755.99 [#/sec] (mean)
Time per request:       2.051 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

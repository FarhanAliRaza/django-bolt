# Django-Bolt Benchmark
Generated: Sat Sep 27 01:22:05 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    49610.56 [#/sec] (mean)
Time per request:       2.016 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    48422.63 [#/sec] (mean)
Time per request:       2.065 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    48653.04 [#/sec] (mean)
Time per request:       2.055 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    49111.33 [#/sec] (mean)
Time per request:       2.036 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    51217.96 [#/sec] (mean)
Time per request:       1.952 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    51650.49 [#/sec] (mean)
Time per request:       1.936 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2435.27 [#/sec] (mean)
Time per request:       41.063 [ms] (mean)
Time per request:       0.411 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3539 secs
  Slowest:	0.0116 secs
  Fastest:	0.0001 secs
  Average:	0.0034 secs
  Requests/sec:	28255.4188
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.3092 secs
  Slowest:	0.0100 secs
  Fastest:	0.0001 secs
  Average:	0.0030 secs
  Requests/sec:	32345.4742
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	4.1418 secs
  Slowest:	0.0476 secs
  Fastest:	0.0026 secs
  Average:	0.0411 secs
  Requests/sec:	2414.4055
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.0586 secs
  Slowest:	0.0200 secs
  Fastest:	0.0003 secs
  Average:	0.0102 secs
  Requests/sec:	9446.8568
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	5.8984 secs
  Slowest:	0.0851 secs
  Fastest:	0.0049 secs
  Average:	0.0577 secs
  Requests/sec:	1695.3683
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    48128.75 [#/sec] (mean)
Time per request:       2.078 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    45103.96 [#/sec] (mean)
Time per request:       2.217 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7132.31 [#/sec] (mean)
Time per request:       14.021 [ms] (mean)
Time per request:       0.140 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8560.18 [#/sec] (mean)
Time per request:       11.682 [ms] (mean)
Time per request:       0.117 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    41322.83 [#/sec] (mean)
Time per request:       2.420 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    48928.95 [#/sec] (mean)
Time per request:       2.044 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    48835.28 [#/sec] (mean)
Time per request:       2.048 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    49618.19 [#/sec] (mean)
Time per request:       2.015 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

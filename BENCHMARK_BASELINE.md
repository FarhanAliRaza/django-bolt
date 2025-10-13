# Django-Bolt Benchmark
Generated: Mon Oct 13 07:17:30 PM PKT 2025
Config: 10 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    73654.52 [#/sec] (mean)
Time per request:       1.358 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    80402.01 [#/sec] (mean)
Time per request:       1.244 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    81269.10 [#/sec] (mean)
Time per request:       1.230 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    77578.32 [#/sec] (mean)
Time per request:       1.289 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    79730.19 [#/sec] (mean)
Time per request:       1.254 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    79048.88 [#/sec] (mean)
Time per request:       1.265 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    19811.00 [#/sec] (mean)
Time per request:       5.048 [ms] (mean)
Time per request:       0.050 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2137 secs
  Slowest:	0.0100 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	46803.6954
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1940 secs
  Slowest:	0.0101 secs
  Fastest:	0.0002 secs
  Average:	0.0018 secs
  Requests/sec:	51549.3061
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3523 secs
  Slowest:	0.0181 secs
  Fastest:	0.0003 secs
  Average:	0.0033 secs
  Requests/sec:	28384.1935
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.5980 secs
  Slowest:	0.0207 secs
  Fastest:	0.0004 secs
  Average:	0.0058 secs
  Requests/sec:	16723.4567
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.7182 secs
  Slowest:	0.0283 secs
  Fastest:	0.0005 secs
  Average:	0.0068 secs
  Requests/sec:	13923.8457
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    77323.37 [#/sec] (mean)
Time per request:       1.293 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    72434.37 [#/sec] (mean)
Time per request:       1.381 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    14902.17 [#/sec] (mean)
Time per request:       6.710 [ms] (mean)
Time per request:       0.067 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    18240.72 [#/sec] (mean)
Time per request:       5.482 [ms] (mean)
Time per request:       0.055 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    57031.73 [#/sec] (mean)
Time per request:       1.753 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    19091.37 [#/sec] (mean)
Time per request:       5.238 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    16174.24 [#/sec] (mean)
Time per request:       6.183 [ms] (mean)
Time per request:       0.062 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    73080.72 [#/sec] (mean)
Time per request:       1.368 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

# Django-Bolt Benchmark
Generated: Mon Oct  6 12:16:07 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    45820.06 [#/sec] (mean)
Time per request:       2.182 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    45222.88 [#/sec] (mean)
Time per request:       2.211 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    45112.51 [#/sec] (mean)
Time per request:       2.217 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    45627.72 [#/sec] (mean)
Time per request:       2.192 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    49833.31 [#/sec] (mean)
Time per request:       2.007 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    46873.32 [#/sec] (mean)
Time per request:       2.133 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2421.48 [#/sec] (mean)
Time per request:       41.297 [ms] (mean)
Time per request:       0.413 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3642 secs
  Slowest:	0.0137 secs
  Fastest:	0.0002 secs
  Average:	0.0035 secs
  Requests/sec:	27454.3430
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3038 secs
  Slowest:	0.0098 secs
  Fastest:	0.0002 secs
  Average:	0.0029 secs
  Requests/sec:	32912.9346
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7105 secs
  Slowest:	0.0238 secs
  Fastest:	0.0003 secs
  Average:	0.0068 secs
  Requests/sec:	14074.2062
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1170 secs
  Slowest:	0.0253 secs
  Fastest:	0.0004 secs
  Average:	0.0101 secs
  Requests/sec:	8952.1887
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.4798 secs
  Slowest:	0.0328 secs
  Fastest:	0.0004 secs
  Average:	0.0137 secs
  Requests/sec:	6757.6858
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    38398.48 [#/sec] (mean)
Time per request:       2.604 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    39534.76 [#/sec] (mean)
Time per request:       2.529 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6831.11 [#/sec] (mean)
Time per request:       14.639 [ms] (mean)
Time per request:       0.146 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8112.81 [#/sec] (mean)
Time per request:       12.326 [ms] (mean)
Time per request:       0.123 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    36746.47 [#/sec] (mean)
Time per request:       2.721 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    43040.74 [#/sec] (mean)
Time per request:       2.323 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    43146.59 [#/sec] (mean)
Time per request:       2.318 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    42168.47 [#/sec] (mean)
Time per request:       2.371 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

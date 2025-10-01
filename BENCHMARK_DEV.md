# Django-Bolt Benchmark
Generated: Wed Oct  1 10:59:04 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    85536.61 [#/sec] (mean)
Time per request:       1.169 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    80460.88 [#/sec] (mean)
Time per request:       1.243 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    85438.68 [#/sec] (mean)
Time per request:       1.170 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    79528.55 [#/sec] (mean)
Time per request:       1.257 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    84876.67 [#/sec] (mean)
Time per request:       1.178 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    81384.18 [#/sec] (mean)
Time per request:       1.229 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2424.35 [#/sec] (mean)
Time per request:       41.248 [ms] (mean)
Time per request:       0.412 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.2183 secs
  Slowest:	0.0179 secs
  Fastest:	0.0001 secs
  Average:	0.0021 secs
  Requests/sec:	45814.2911
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.2109 secs
  Slowest:	0.0112 secs
  Fastest:	0.0001 secs
  Average:	0.0020 secs
  Requests/sec:	47408.9870
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.4045 secs
  Slowest:	0.0177 secs
  Fastest:	0.0003 secs
  Average:	0.0039 secs
  Requests/sec:	24719.6004
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6576 secs
  Slowest:	0.0236 secs
  Fastest:	0.0004 secs
  Average:	0.0061 secs
  Requests/sec:	15205.9619
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8023 secs
  Slowest:	0.0277 secs
  Fastest:	0.0005 secs
  Average:	0.0076 secs
  Requests/sec:	12463.8539
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    60255.85 [#/sec] (mean)
Time per request:       1.660 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    77987.91 [#/sec] (mean)
Time per request:       1.282 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12037.10 [#/sec] (mean)
Time per request:       8.308 [ms] (mean)
Time per request:       0.083 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    15197.13 [#/sec] (mean)
Time per request:       6.580 [ms] (mean)
Time per request:       0.066 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    65723.75 [#/sec] (mean)
Time per request:       1.522 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    75130.92 [#/sec] (mean)
Time per request:       1.331 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    81619.33 [#/sec] (mean)
Time per request:       1.225 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    73170.55 [#/sec] (mean)
Time per request:       1.367 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

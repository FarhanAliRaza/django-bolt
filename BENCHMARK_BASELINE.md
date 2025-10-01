# Django-Bolt Benchmark
Generated: Wed Oct  1 10:47:08 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    84563.74 [#/sec] (mean)
Time per request:       1.183 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    83329.86 [#/sec] (mean)
Time per request:       1.200 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    86281.28 [#/sec] (mean)
Time per request:       1.159 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    85339.52 [#/sec] (mean)
Time per request:       1.172 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    84552.30 [#/sec] (mean)
Time per request:       1.183 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    69525.56 [#/sec] (mean)
Time per request:       1.438 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2433.14 [#/sec] (mean)
Time per request:       41.099 [ms] (mean)
Time per request:       0.411 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.2189 secs
  Slowest:	0.0118 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	45689.3582
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.1981 secs
  Slowest:	0.0092 secs
  Fastest:	0.0002 secs
  Average:	0.0019 secs
  Requests/sec:	50482.7578
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.3685 secs
  Slowest:	0.0134 secs
  Fastest:	0.0003 secs
  Average:	0.0035 secs
  Requests/sec:	27137.4290
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6111 secs
  Slowest:	0.0203 secs
  Fastest:	0.0004 secs
  Average:	0.0059 secs
  Requests/sec:	16362.9087
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.7757 secs
  Slowest:	0.0217 secs
  Fastest:	0.0004 secs
  Average:	0.0072 secs
  Requests/sec:	12891.8214
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    61950.19 [#/sec] (mean)
Time per request:       1.614 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    74234.09 [#/sec] (mean)
Time per request:       1.347 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12593.02 [#/sec] (mean)
Time per request:       7.941 [ms] (mean)
Time per request:       0.079 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    15449.46 [#/sec] (mean)
Time per request:       6.473 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    70052.54 [#/sec] (mean)
Time per request:       1.427 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    82609.13 [#/sec] (mean)
Time per request:       1.211 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    80074.95 [#/sec] (mean)
Time per request:       1.249 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    81713.37 [#/sec] (mean)
Time per request:       1.224 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

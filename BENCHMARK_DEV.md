# Django-Bolt Benchmark
Generated: Sun Sep 28 03:41:40 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    54862.16 [#/sec] (mean)
Time per request:       1.823 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    54463.56 [#/sec] (mean)
Time per request:       1.836 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    54026.89 [#/sec] (mean)
Time per request:       1.851 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    53786.86 [#/sec] (mean)
Time per request:       1.859 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    56136.88 [#/sec] (mean)
Time per request:       1.781 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    56253.73 [#/sec] (mean)
Time per request:       1.778 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2434.26 [#/sec] (mean)
Time per request:       41.080 [ms] (mean)
Time per request:       0.411 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3296 secs
  Slowest:	0.0077 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	30339.4403
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.2936 secs
  Slowest:	0.0095 secs
  Fastest:	0.0002 secs
  Average:	0.0028 secs
  Requests/sec:	34060.3080
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	4.1530 secs
  Slowest:	0.0513 secs
  Fastest:	0.0018 secs
  Average:	0.0411 secs
  Requests/sec:	2407.9007
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.0310 secs
  Slowest:	0.0200 secs
  Fastest:	0.0004 secs
  Average:	0.0100 secs
  Requests/sec:	9699.1753
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	4.1900 secs
  Slowest:	0.0644 secs
  Fastest:	0.0146 secs
  Average:	0.0416 secs
  Requests/sec:	2386.6345
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    50672.68 [#/sec] (mean)
Time per request:       1.973 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    47128.91 [#/sec] (mean)
Time per request:       2.122 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7035.77 [#/sec] (mean)
Time per request:       14.213 [ms] (mean)
Time per request:       0.142 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8687.45 [#/sec] (mean)
Time per request:       11.511 [ms] (mean)
Time per request:       0.115 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    42026.70 [#/sec] (mean)
Time per request:       2.379 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    52681.21 [#/sec] (mean)
Time per request:       1.898 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    49916.64 [#/sec] (mean)
Time per request:       2.003 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    47717.66 [#/sec] (mean)
Time per request:       2.096 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

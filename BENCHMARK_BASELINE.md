# Django-Bolt Benchmark
Generated: Sat Sep 27 01:15:36 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    53121.13 [#/sec] (mean)
Time per request:       1.882 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    50452.30 [#/sec] (mean)
Time per request:       1.982 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    52463.70 [#/sec] (mean)
Time per request:       1.906 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    52632.41 [#/sec] (mean)
Time per request:       1.900 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    54759.71 [#/sec] (mean)
Time per request:       1.826 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    54729.15 [#/sec] (mean)
Time per request:       1.827 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2435.72 [#/sec] (mean)
Time per request:       41.056 [ms] (mean)
Time per request:       0.411 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3303 secs
  Slowest:	0.0122 secs
  Fastest:	0.0001 secs
  Average:	0.0032 secs
  Requests/sec:	30271.8030
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.2919 secs
  Slowest:	0.0105 secs
  Fastest:	0.0001 secs
  Average:	0.0028 secs
  Requests/sec:	34252.8665
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	4.1378 secs
  Slowest:	0.0474 secs
  Fastest:	0.0036 secs
  Average:	0.0411 secs
  Requests/sec:	2416.7440
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.0696 secs
  Slowest:	0.0225 secs
  Fastest:	0.0004 secs
  Average:	0.0103 secs
  Requests/sec:	9349.6393
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	5.7827 secs
  Slowest:	0.0835 secs
  Fastest:	0.0042 secs
  Average:	0.0570 secs
  Requests/sec:	1729.2951
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    49568.01 [#/sec] (mean)
Time per request:       2.017 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    47098.05 [#/sec] (mean)
Time per request:       2.123 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7206.17 [#/sec] (mean)
Time per request:       13.877 [ms] (mean)
Time per request:       0.139 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8618.49 [#/sec] (mean)
Time per request:       11.603 [ms] (mean)
Time per request:       0.116 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    42224.92 [#/sec] (mean)
Time per request:       2.368 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    49747.04 [#/sec] (mean)
Time per request:       2.010 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    51675.05 [#/sec] (mean)
Time per request:       1.935 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    52512.18 [#/sec] (mean)
Time per request:       1.904 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

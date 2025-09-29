# Django-Bolt Benchmark
Generated: Mon Sep 29 06:06:10 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    52275.01 [#/sec] (mean)
Time per request:       1.913 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Response Type Endpoints

### Header Endpoint (/header)
Failed requests:        0
Requests per second:    51411.50 [#/sec] (mean)
Time per request:       1.945 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    50578.36 [#/sec] (mean)
Time per request:       1.977 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    50694.77 [#/sec] (mean)
Time per request:       1.973 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### HTML Response (/html)
Failed requests:        0
Requests per second:    49912.65 [#/sec] (mean)
Time per request:       2.003 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    52293.05 [#/sec] (mean)
Time per request:       1.912 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2423.96 [#/sec] (mean)
Time per request:       41.255 [ms] (mean)
Time per request:       0.413 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance

### Streaming Plain Text (/stream)
  Total:	0.3600 secs
  Slowest:	0.0091 secs
  Fastest:	0.0001 secs
  Average:	0.0035 secs
  Requests/sec:	27776.0240
Status code distribution:

### Server-Sent Events (/sse)
  Total:	0.3160 secs
  Slowest:	0.0102 secs
  Fastest:	0.0001 secs
  Average:	0.0031 secs
  Requests/sec:	31641.6338
Status code distribution:

### Server-Sent Events (async) (/sse-async)
  Total:	0.7074 secs
  Slowest:	0.0153 secs
  Fastest:	0.0003 secs
  Average:	0.0068 secs
  Requests/sec:	14136.4657
Status code distribution:

### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.0533 secs
  Slowest:	0.0206 secs
  Fastest:	0.0004 secs
  Average:	0.0100 secs
  Requests/sec:	9493.8152
Status code distribution:

### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.2103 secs
  Slowest:	0.0237 secs
  Fastest:	0.0004 secs
  Average:	0.0118 secs
  Requests/sec:	8262.2976
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    47399.65 [#/sec] (mean)
Time per request:       2.110 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    45887.77 [#/sec] (mean)
Time per request:       2.179 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    7297.46 [#/sec] (mean)
Time per request:       13.703 [ms] (mean)
Time per request:       0.137 [ms] (mean, across all concurrent requests)
\n### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8687.73 [#/sec] (mean)
Time per request:       11.510 [ms] (mean)
Time per request:       0.115 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
\n### Form Data (POST /form)
Failed requests:        0
Requests per second:    41625.21 [#/sec] (mean)
Time per request:       2.402 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
\n### File Upload (POST /upload)
Failed requests:        0
Requests per second:    47932.20 [#/sec] (mean)
Time per request:       2.086 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
\n### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    49053.27 [#/sec] (mean)
Time per request:       2.039 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    46572.28 [#/sec] (mean)
Time per request:       2.147 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

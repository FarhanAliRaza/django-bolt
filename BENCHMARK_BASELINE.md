# Django-Bolt Benchmark
Generated: Fri Oct 10 11:05:09 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    75416.49 [#/sec] (mean)
Time per request:       1.326 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    55969.73 [#/sec] (mean)
Time per request:       1.787 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    81802.27 [#/sec] (mean)
Time per request:       1.222 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    72805.64 [#/sec] (mean)
Time per request:       1.374 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    78597.81 [#/sec] (mean)
Time per request:       1.272 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    71927.96 [#/sec] (mean)
Time per request:       1.390 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2407.28 [#/sec] (mean)
Time per request:       41.541 [ms] (mean)
Time per request:       0.415 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.4097 secs
  Slowest:	0.0541 secs
  Fastest:	0.0002 secs
  Average:	0.0039 secs
  Requests/sec:	24409.5371
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3905 secs
  Slowest:	0.0197 secs
  Fastest:	0.0002 secs
  Average:	0.0037 secs
  Requests/sec:	25606.1128
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.5543 secs
  Slowest:	0.0528 secs
  Fastest:	0.0003 secs
  Average:	0.0052 secs
  Requests/sec:	18041.9943
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.7840 secs
  Slowest:	0.0345 secs
  Fastest:	0.0004 secs
  Average:	0.0073 secs
  Requests/sec:	12754.6834
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.9109 secs
  Slowest:	0.0385 secs
  Fastest:	0.0005 secs
  Average:	0.0088 secs
  Requests/sec:	10978.2976
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    75717.42 [#/sec] (mean)
Time per request:       1.321 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    70633.94 [#/sec] (mean)
Time per request:       1.416 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12130.24 [#/sec] (mean)
Time per request:       8.244 [ms] (mean)
Time per request:       0.082 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    15205.38 [#/sec] (mean)
Time per request:       6.577 [ms] (mean)
Time per request:       0.066 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    58710.94 [#/sec] (mean)
Time per request:       1.703 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    21488.88 [#/sec] (mean)
Time per request:       4.654 [ms] (mean)
Time per request:       0.047 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    21754.45 [#/sec] (mean)
Time per request:       4.597 [ms] (mean)
Time per request:       0.046 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    68299.95 [#/sec] (mean)
Time per request:       1.464 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

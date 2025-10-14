# Django-Bolt Benchmark
Generated: Wed Oct 15 12:15:53 AM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    30414.09 [#/sec] (mean)
Time per request:       3.288 [ms] (mean)
Time per request:       0.033 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    31708.79 [#/sec] (mean)
Time per request:       3.154 [ms] (mean)
Time per request:       0.032 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    31800.55 [#/sec] (mean)
Time per request:       3.145 [ms] (mean)
Time per request:       0.031 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    32078.12 [#/sec] (mean)
Time per request:       3.117 [ms] (mean)
Time per request:       0.031 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    32905.45 [#/sec] (mean)
Time per request:       3.039 [ms] (mean)
Time per request:       0.030 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    32932.87 [#/sec] (mean)
Time per request:       3.036 [ms] (mean)
Time per request:       0.030 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    18628.22 [#/sec] (mean)
Time per request:       5.368 [ms] (mean)
Time per request:       0.054 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.4680 secs
  Slowest:	0.0133 secs
  Fastest:	0.0002 secs
  Average:	0.0045 secs
  Requests/sec:	21367.8663
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.4145 secs
  Slowest:	0.0131 secs
  Fastest:	0.0002 secs
  Average:	0.0040 secs
  Requests/sec:	24125.5517
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.8188 secs
  Slowest:	0.0244 secs
  Fastest:	0.0004 secs
  Average:	0.0078 secs
  Requests/sec:	12212.3902
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.2598 secs
  Slowest:	0.0291 secs
  Fastest:	0.0004 secs
  Average:	0.0117 secs
  Requests/sec:	7937.7269
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.6248 secs
  Slowest:	0.0386 secs
  Fastest:	0.0005 secs
  Average:	0.0150 secs
  Requests/sec:	6154.6089
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    30666.85 [#/sec] (mean)
Time per request:       3.261 [ms] (mean)
Time per request:       0.033 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    28729.77 [#/sec] (mean)
Time per request:       3.481 [ms] (mean)
Time per request:       0.035 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6659.45 [#/sec] (mean)
Time per request:       15.016 [ms] (mean)
Time per request:       0.150 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    7608.98 [#/sec] (mean)
Time per request:       13.142 [ms] (mean)
Time per request:       0.131 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    27225.33 [#/sec] (mean)
Time per request:       3.673 [ms] (mean)
Time per request:       0.037 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    6924.63 [#/sec] (mean)
Time per request:       14.441 [ms] (mean)
Time per request:       0.144 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    7038.10 [#/sec] (mean)
Time per request:       14.208 [ms] (mean)
Time per request:       0.142 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    31897.52 [#/sec] (mean)
Time per request:       3.135 [ms] (mean)
Time per request:       0.031 [ms] (mean, across all concurrent requests)

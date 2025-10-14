# Django-Bolt Benchmark
Generated: Wed Oct 15 12:17:47 AM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    30684.54 [#/sec] (mean)
Time per request:       3.259 [ms] (mean)
Time per request:       0.033 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    31510.55 [#/sec] (mean)
Time per request:       3.174 [ms] (mean)
Time per request:       0.032 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    31095.78 [#/sec] (mean)
Time per request:       3.216 [ms] (mean)
Time per request:       0.032 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    31360.45 [#/sec] (mean)
Time per request:       3.189 [ms] (mean)
Time per request:       0.032 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    32562.90 [#/sec] (mean)
Time per request:       3.071 [ms] (mean)
Time per request:       0.031 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    32101.70 [#/sec] (mean)
Time per request:       3.115 [ms] (mean)
Time per request:       0.031 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    19023.96 [#/sec] (mean)
Time per request:       5.257 [ms] (mean)
Time per request:       0.053 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.4603 secs
  Slowest:	0.0168 secs
  Fastest:	0.0002 secs
  Average:	0.0044 secs
  Requests/sec:	21724.7825
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.4089 secs
  Slowest:	0.0169 secs
  Fastest:	0.0002 secs
  Average:	0.0039 secs
  Requests/sec:	24456.9859
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.8347 secs
  Slowest:	0.0191 secs
  Fastest:	0.0003 secs
  Average:	0.0081 secs
  Requests/sec:	11980.0432
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.2654 secs
  Slowest:	0.0324 secs
  Fastest:	0.0004 secs
  Average:	0.0119 secs
  Requests/sec:	7902.5983
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.7199 secs
  Slowest:	0.0372 secs
  Fastest:	0.0005 secs
  Average:	0.0152 secs
  Requests/sec:	5814.1762
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    30021.74 [#/sec] (mean)
Time per request:       3.331 [ms] (mean)
Time per request:       0.033 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    28432.68 [#/sec] (mean)
Time per request:       3.517 [ms] (mean)
Time per request:       0.035 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6202.79 [#/sec] (mean)
Time per request:       16.122 [ms] (mean)
Time per request:       0.161 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    7159.21 [#/sec] (mean)
Time per request:       13.968 [ms] (mean)
Time per request:       0.140 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    26674.56 [#/sec] (mean)
Time per request:       3.749 [ms] (mean)
Time per request:       0.037 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    6505.50 [#/sec] (mean)
Time per request:       15.372 [ms] (mean)
Time per request:       0.154 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    6815.07 [#/sec] (mean)
Time per request:       14.673 [ms] (mean)
Time per request:       0.147 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    30082.15 [#/sec] (mean)
Time per request:       3.324 [ms] (mean)
Time per request:       0.033 [ms] (mean, across all concurrent requests)

# Django-Bolt Benchmark
Generated: Fri Oct 10 08:46:48 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    43043.89 [#/sec] (mean)
Time per request:       2.323 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    42453.47 [#/sec] (mean)
Time per request:       2.356 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    42691.26 [#/sec] (mean)
Time per request:       2.342 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    41198.89 [#/sec] (mean)
Time per request:       2.427 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    43709.35 [#/sec] (mean)
Time per request:       2.288 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    43291.54 [#/sec] (mean)
Time per request:       2.310 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    2422.17 [#/sec] (mean)
Time per request:       41.285 [ms] (mean)
Time per request:       0.413 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3665 secs
  Slowest:	0.0141 secs
  Fastest:	0.0002 secs
  Average:	0.0035 secs
  Requests/sec:	27281.8105
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3456 secs
  Slowest:	0.0232 secs
  Fastest:	0.0001 secs
  Average:	0.0033 secs
  Requests/sec:	28938.7385
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7350 secs
  Slowest:	0.0395 secs
  Fastest:	0.0003 secs
  Average:	0.0070 secs
  Requests/sec:	13606.3178
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1427 secs
  Slowest:	0.0466 secs
  Fastest:	0.0004 secs
  Average:	0.0111 secs
  Requests/sec:	8751.2652
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5437 secs
  Slowest:	0.0284 secs
  Fastest:	0.0006 secs
  Average:	0.0149 secs
  Requests/sec:	6478.0502
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    40012.64 [#/sec] (mean)
Time per request:       2.499 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    35857.97 [#/sec] (mean)
Time per request:       2.789 [ms] (mean)
Time per request:       0.028 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6675.87 [#/sec] (mean)
Time per request:       14.979 [ms] (mean)
Time per request:       0.150 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    7834.87 [#/sec] (mean)
Time per request:       12.763 [ms] (mean)
Time per request:       0.128 [ms] (mean, across all concurrent requests)

## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    34237.78 [#/sec] (mean)
Time per request:       2.921 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    11565.45 [#/sec] (mean)
Time per request:       8.646 [ms] (mean)
Time per request:       0.086 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    11996.00 [#/sec] (mean)
Time per request:       8.336 [ms] (mean)
Time per request:       0.083 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    37561.79 [#/sec] (mean)
Time per request:       2.662 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

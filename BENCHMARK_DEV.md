# Django-Bolt Benchmark
Generated: Tue Oct 21 06:03:46 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    29860.73 [#/sec] (mean)
Time per request:       3.349 [ms] (mean)
Time per request:       0.033 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    82566.84 [#/sec] (mean)
Time per request:       1.211 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    78851.92 [#/sec] (mean)
Time per request:       1.268 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    80044.18 [#/sec] (mean)
Time per request:       1.249 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    82157.79 [#/sec] (mean)
Time per request:       1.217 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    83992.68 [#/sec] (mean)
Time per request:       1.191 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    20022.83 [#/sec] (mean)
Time per request:       4.994 [ms] (mean)
Time per request:       0.050 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2180 secs
  Slowest:	0.0105 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	45881.8725
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2129 secs
  Slowest:	0.0222 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	46974.4656
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3914 secs
  Slowest:	0.0181 secs
  Fastest:	0.0003 secs
  Average:	0.0037 secs
  Requests/sec:	25550.5664
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.7111 secs
  Slowest:	0.0295 secs
  Fastest:	0.0004 secs
  Average:	0.0066 secs
  Requests/sec:	14061.7954
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8743 secs
  Slowest:	0.0257 secs
  Fastest:	0.0004 secs
  Average:	0.0079 secs
  Requests/sec:	11437.6015
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    79082.64 [#/sec] (mean)
Time per request:       1.265 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    67773.18 [#/sec] (mean)
Time per request:       1.476 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12216.22 [#/sec] (mean)
Time per request:       8.186 [ms] (mean)
Time per request:       0.082 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14347.22 [#/sec] (mean)
Time per request:       6.970 [ms] (mean)
Time per request:       0.070 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    73098.88 [#/sec] (mean)
Time per request:       1.368 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    69074.61 [#/sec] (mean)
Time per request:       1.448 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    38497.96 [#/sec] (mean)
Time per request:       2.598 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    67981.43 [#/sec] (mean)
Time per request:       1.471 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    73869.43 [#/sec] (mean)
Time per request:       1.354 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    74611.28 [#/sec] (mean)
Time per request:       1.340 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    80461.53 [#/sec] (mean)
Time per request:       1.243 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3757 secs
  Slowest:	0.0194 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	26613.5454
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3606 secs
  Slowest:	0.0215 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	27731.7964
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.8659 secs
  Slowest:	0.0296 secs
  Fastest:	0.0005 secs
  Average:	0.0083 secs
  Requests/sec:	11548.8699
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    15169.88 [#/sec] (mean)
Time per request:       6.592 [ms] (mean)
Time per request:       0.066 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    63206.33 [#/sec] (mean)
Time per request:       1.582 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    12015.91 [#/sec] (mean)
Time per request:       8.322 [ms] (mean)
Time per request:       0.083 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    11273.08 [#/sec] (mean)
Time per request:       8.871 [ms] (mean)
Time per request:       0.089 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    77350.29 [#/sec] (mean)
Time per request:       1.293 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

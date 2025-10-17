# Django-Bolt Benchmark
Generated: Sat Oct 18 12:41:24 AM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    37567.43 [#/sec] (mean)
Time per request:       2.662 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    44142.51 [#/sec] (mean)
Time per request:       2.265 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    42932.46 [#/sec] (mean)
Time per request:       2.329 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    42099.95 [#/sec] (mean)
Time per request:       2.375 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    45474.39 [#/sec] (mean)
Time per request:       2.199 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    45148.36 [#/sec] (mean)
Time per request:       2.215 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    18456.69 [#/sec] (mean)
Time per request:       5.418 [ms] (mean)
Time per request:       0.054 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3774 secs
  Slowest:	0.0126 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	26497.3948
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3471 secs
  Slowest:	0.0230 secs
  Fastest:	0.0002 secs
  Average:	0.0033 secs
  Requests/sec:	28811.9604
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7192 secs
  Slowest:	0.0171 secs
  Fastest:	0.0003 secs
  Average:	0.0070 secs
  Requests/sec:	13903.5586
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1489 secs
  Slowest:	0.0230 secs
  Fastest:	0.0004 secs
  Average:	0.0109 secs
  Requests/sec:	8704.1751
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5605 secs
  Slowest:	0.0443 secs
  Fastest:	0.0005 secs
  Average:	0.0143 secs
  Requests/sec:	6408.3195
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    40794.51 [#/sec] (mean)
Time per request:       2.451 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    36431.47 [#/sec] (mean)
Time per request:       2.745 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6900.28 [#/sec] (mean)
Time per request:       14.492 [ms] (mean)
Time per request:       0.145 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8107.38 [#/sec] (mean)
Time per request:       12.334 [ms] (mean)
Time per request:       0.123 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    45217.77 [#/sec] (mean)
Time per request:       2.212 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    40215.39 [#/sec] (mean)
Time per request:       2.487 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    21766.34 [#/sec] (mean)
Time per request:       4.594 [ms] (mean)
Time per request:       0.046 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    39836.83 [#/sec] (mean)
Time per request:       2.510 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    39078.53 [#/sec] (mean)
Time per request:       2.559 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    39609.92 [#/sec] (mean)
Time per request:       2.525 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    42841.41 [#/sec] (mean)
Time per request:       2.334 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.4026 secs
  Slowest:	0.0165 secs
  Fastest:	0.0002 secs
  Average:	0.0039 secs
  Requests/sec:	24838.4183
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3583 secs
  Slowest:	0.0179 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	27911.2445
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	1.5259 secs
  Slowest:	0.0324 secs
  Fastest:	0.0005 secs
  Average:	0.0145 secs
  Requests/sec:	6553.3101
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    8407.60 [#/sec] (mean)
Time per request:       11.894 [ms] (mean)
Time per request:       0.119 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    35386.46 [#/sec] (mean)
Time per request:       2.826 [ms] (mean)
Time per request:       0.028 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    7241.09 [#/sec] (mean)
Time per request:       13.810 [ms] (mean)
Time per request:       0.138 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    7420.36 [#/sec] (mean)
Time per request:       13.476 [ms] (mean)
Time per request:       0.135 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    40723.41 [#/sec] (mean)
Time per request:       2.456 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

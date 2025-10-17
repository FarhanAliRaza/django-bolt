# Django-Bolt Benchmark
Generated: Fri Oct 17 11:39:01 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    40142.91 [#/sec] (mean)
Time per request:       2.491 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    43660.11 [#/sec] (mean)
Time per request:       2.290 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    42594.15 [#/sec] (mean)
Time per request:       2.348 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    41690.46 [#/sec] (mean)
Time per request:       2.399 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    44241.72 [#/sec] (mean)
Time per request:       2.260 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    45401.30 [#/sec] (mean)
Time per request:       2.203 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    19379.32 [#/sec] (mean)
Time per request:       5.160 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3788 secs
  Slowest:	0.0124 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	26397.5962
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3312 secs
  Slowest:	0.0114 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	30189.9548
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7183 secs
  Slowest:	0.0158 secs
  Fastest:	0.0003 secs
  Average:	0.0070 secs
  Requests/sec:	13921.7263
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1377 secs
  Slowest:	0.0253 secs
  Fastest:	0.0004 secs
  Average:	0.0108 secs
  Requests/sec:	8789.8787
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5319 secs
  Slowest:	0.0306 secs
  Fastest:	0.0007 secs
  Average:	0.0146 secs
  Requests/sec:	6527.7309
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    41146.51 [#/sec] (mean)
Time per request:       2.430 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    37017.71 [#/sec] (mean)
Time per request:       2.701 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6811.11 [#/sec] (mean)
Time per request:       14.682 [ms] (mean)
Time per request:       0.147 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8030.01 [#/sec] (mean)
Time per request:       12.453 [ms] (mean)
Time per request:       0.125 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    45126.15 [#/sec] (mean)
Time per request:       2.216 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    40607.49 [#/sec] (mean)
Time per request:       2.463 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    21532.98 [#/sec] (mean)
Time per request:       4.644 [ms] (mean)
Time per request:       0.046 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    40461.75 [#/sec] (mean)
Time per request:       2.471 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    39903.91 [#/sec] (mean)
Time per request:       2.506 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    40734.36 [#/sec] (mean)
Time per request:       2.455 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    43079.87 [#/sec] (mean)
Time per request:       2.321 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3977 secs
  Slowest:	0.0139 secs
  Fastest:	0.0002 secs
  Average:	0.0039 secs
  Requests/sec:	25146.5274
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3691 secs
  Slowest:	0.0162 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	27090.8014
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	1.4840 secs
  Slowest:	0.0281 secs
  Fastest:	0.0006 secs
  Average:	0.0145 secs
  Requests/sec:	6738.5138
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    8246.42 [#/sec] (mean)
Time per request:       12.126 [ms] (mean)
Time per request:       0.121 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    35013.64 [#/sec] (mean)
Time per request:       2.856 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    7204.19 [#/sec] (mean)
Time per request:       13.881 [ms] (mean)
Time per request:       0.139 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    6973.18 [#/sec] (mean)
Time per request:       14.341 [ms] (mean)
Time per request:       0.143 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    40832.49 [#/sec] (mean)
Time per request:       2.449 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

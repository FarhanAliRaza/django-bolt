# Django-Bolt Benchmark
Generated: Wed Oct 22 05:14:13 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    30904.83 [#/sec] (mean)
Time per request:       3.236 [ms] (mean)
Time per request:       0.032 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    83195.37 [#/sec] (mean)
Time per request:       1.202 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    83455.04 [#/sec] (mean)
Time per request:       1.198 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    80549.02 [#/sec] (mean)
Time per request:       1.241 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    81713.37 [#/sec] (mean)
Time per request:       1.224 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    82135.52 [#/sec] (mean)
Time per request:       1.217 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    20075.36 [#/sec] (mean)
Time per request:       4.981 [ms] (mean)
Time per request:       0.050 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2188 secs
  Slowest:	0.0119 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	45700.2911
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2417 secs
  Slowest:	0.0292 secs
  Fastest:	0.0002 secs
  Average:	0.0023 secs
  Requests/sec:	41365.5570
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.4309 secs
  Slowest:	0.0174 secs
  Fastest:	0.0003 secs
  Average:	0.0041 secs
  Requests/sec:	23207.0002
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6716 secs
  Slowest:	0.0198 secs
  Fastest:	0.0004 secs
  Average:	0.0063 secs
  Requests/sec:	14890.1641
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8472 secs
  Slowest:	0.0288 secs
  Fastest:	0.0005 secs
  Average:	0.0082 secs
  Requests/sec:	11804.2182
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    76845.05 [#/sec] (mean)
Time per request:       1.301 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    69434.80 [#/sec] (mean)
Time per request:       1.440 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12812.66 [#/sec] (mean)
Time per request:       7.805 [ms] (mean)
Time per request:       0.078 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    13316.04 [#/sec] (mean)
Time per request:       7.510 [ms] (mean)
Time per request:       0.075 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    83102.72 [#/sec] (mean)
Time per request:       1.203 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    73336.36 [#/sec] (mean)
Time per request:       1.364 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    39265.11 [#/sec] (mean)
Time per request:       2.547 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    73094.61 [#/sec] (mean)
Time per request:       1.368 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    73768.62 [#/sec] (mean)
Time per request:       1.356 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    69824.11 [#/sec] (mean)
Time per request:       1.432 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    80120.50 [#/sec] (mean)
Time per request:       1.248 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.4329 secs
  Slowest:	0.0318 secs
  Fastest:	0.0002 secs
  Average:	0.0041 secs
  Requests/sec:	23101.3831
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.4497 secs
  Slowest:	0.0337 secs
  Fastest:	0.0002 secs
  Average:	0.0043 secs
  Requests/sec:	22236.6198
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.9296 secs
  Slowest:	0.0377 secs
  Fastest:	0.0005 secs
  Average:	0.0089 secs
  Requests/sec:	10757.2875
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    15486.76 [#/sec] (mean)
Time per request:       6.457 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    66963.09 [#/sec] (mean)
Time per request:       1.493 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    51252.35 [#/sec] (mean)
Time per request:       1.951 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    47151.35 [#/sec] (mean)
Time per request:       2.121 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    57552.63 [#/sec] (mean)
Time per request:       1.738 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

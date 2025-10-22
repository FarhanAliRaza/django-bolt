# Django-Bolt Benchmark
Generated: Wed Oct 22 05:05:34 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    30511.62 [#/sec] (mean)
Time per request:       3.277 [ms] (mean)
Time per request:       0.033 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    80506.22 [#/sec] (mean)
Time per request:       1.242 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    76755.40 [#/sec] (mean)
Time per request:       1.303 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    79473.57 [#/sec] (mean)
Time per request:       1.258 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    80580.18 [#/sec] (mean)
Time per request:       1.241 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    73737.61 [#/sec] (mean)
Time per request:       1.356 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    25210.06 [#/sec] (mean)
Time per request:       3.967 [ms] (mean)
Time per request:       0.040 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2375 secs
  Slowest:	0.0103 secs
  Fastest:	0.0002 secs
  Average:	0.0023 secs
  Requests/sec:	42105.3990
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2051 secs
  Slowest:	0.0093 secs
  Fastest:	0.0002 secs
  Average:	0.0019 secs
  Requests/sec:	48762.0983
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.4429 secs
  Slowest:	0.0222 secs
  Fastest:	0.0003 secs
  Average:	0.0042 secs
  Requests/sec:	22579.5649
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6842 secs
  Slowest:	0.0256 secs
  Fastest:	0.0004 secs
  Average:	0.0065 secs
  Requests/sec:	14614.8207
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8247 secs
  Slowest:	0.0287 secs
  Fastest:	0.0006 secs
  Average:	0.0079 secs
  Requests/sec:	12125.8222
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    76576.71 [#/sec] (mean)
Time per request:       1.306 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    69956.49 [#/sec] (mean)
Time per request:       1.429 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    11423.49 [#/sec] (mean)
Time per request:       8.754 [ms] (mean)
Time per request:       0.088 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    11891.89 [#/sec] (mean)
Time per request:       8.409 [ms] (mean)
Time per request:       0.084 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    77657.24 [#/sec] (mean)
Time per request:       1.288 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    68313.48 [#/sec] (mean)
Time per request:       1.464 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    39287.95 [#/sec] (mean)
Time per request:       2.545 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    75248.51 [#/sec] (mean)
Time per request:       1.329 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    70695.36 [#/sec] (mean)
Time per request:       1.415 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    76890.55 [#/sec] (mean)
Time per request:       1.301 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    76851.55 [#/sec] (mean)
Time per request:       1.301 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.4731 secs
  Slowest:	0.0347 secs
  Fastest:	0.0002 secs
  Average:	0.0045 secs
  Requests/sec:	21137.3682
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.4000 secs
  Slowest:	0.0207 secs
  Fastest:	0.0002 secs
  Average:	0.0038 secs
  Requests/sec:	25002.7779
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.9669 secs
  Slowest:	0.0408 secs
  Fastest:	0.0005 secs
  Average:	0.0092 secs
  Requests/sec:	10341.9553
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    15668.41 [#/sec] (mean)
Time per request:       6.382 [ms] (mean)
Time per request:       0.064 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    66286.18 [#/sec] (mean)
Time per request:       1.509 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    50754.72 [#/sec] (mean)
Time per request:       1.970 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    49229.80 [#/sec] (mean)
Time per request:       2.031 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    77822.22 [#/sec] (mean)
Time per request:       1.285 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

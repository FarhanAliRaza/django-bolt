# Django-Bolt Benchmark
Generated: Wed Oct 22 10:49:09 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    71470.94 [#/sec] (mean)
Time per request:       1.399 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    81404.06 [#/sec] (mean)
Time per request:       1.228 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    78562.62 [#/sec] (mean)
Time per request:       1.273 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    76780.15 [#/sec] (mean)
Time per request:       1.302 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    86457.32 [#/sec] (mean)
Time per request:       1.157 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    87109.53 [#/sec] (mean)
Time per request:       1.148 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    28955.88 [#/sec] (mean)
Time per request:       3.454 [ms] (mean)
Time per request:       0.035 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2426 secs
  Slowest:	0.0178 secs
  Fastest:	0.0002 secs
  Average:	0.0023 secs
  Requests/sec:	41212.1137
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2347 secs
  Slowest:	0.0126 secs
  Fastest:	0.0002 secs
  Average:	0.0022 secs
  Requests/sec:	42614.8619
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.4145 secs
  Slowest:	0.0160 secs
  Fastest:	0.0003 secs
  Average:	0.0040 secs
  Requests/sec:	24123.1802
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6919 secs
  Slowest:	0.0298 secs
  Fastest:	0.0004 secs
  Average:	0.0064 secs
  Requests/sec:	14452.3152
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8078 secs
  Slowest:	0.0260 secs
  Fastest:	0.0005 secs
  Average:	0.0074 secs
  Requests/sec:	12378.8866
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    77733.90 [#/sec] (mean)
Time per request:       1.286 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    70103.12 [#/sec] (mean)
Time per request:       1.426 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    13764.04 [#/sec] (mean)
Time per request:       7.265 [ms] (mean)
Time per request:       0.073 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14535.52 [#/sec] (mean)
Time per request:       6.880 [ms] (mean)
Time per request:       0.069 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    86652.86 [#/sec] (mean)
Time per request:       1.154 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    79289.57 [#/sec] (mean)
Time per request:       1.261 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    60864.27 [#/sec] (mean)
Time per request:       1.643 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    80945.44 [#/sec] (mean)
Time per request:       1.235 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    79090.77 [#/sec] (mean)
Time per request:       1.264 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    79413.61 [#/sec] (mean)
Time per request:       1.259 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    83361.82 [#/sec] (mean)
Time per request:       1.200 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3813 secs
  Slowest:	0.0326 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	26223.8282
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3717 secs
  Slowest:	0.0239 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	26902.1297
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.8458 secs
  Slowest:	0.0336 secs
  Fastest:	0.0005 secs
  Average:	0.0081 secs
  Requests/sec:	11823.5406
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    16044.69 [#/sec] (mean)
Time per request:       6.233 [ms] (mean)
Time per request:       0.062 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    66452.25 [#/sec] (mean)
Time per request:       1.505 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    52877.32 [#/sec] (mean)
Time per request:       1.891 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    49988.25 [#/sec] (mean)
Time per request:       2.000 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    80301.29 [#/sec] (mean)
Time per request:       1.245 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

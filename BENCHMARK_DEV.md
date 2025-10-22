# Django-Bolt Benchmark
Generated: Wed Oct 22 11:50:02 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    87911.32 [#/sec] (mean)
Time per request:       1.138 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON  (/10k-json)
Failed requests:        0
Requests per second:    69789.03 [#/sec] (mean)
Time per request:       1.433 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    83795.61 [#/sec] (mean)
Time per request:       1.193 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    82520.51 [#/sec] (mean)
Time per request:       1.212 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    82648.73 [#/sec] (mean)
Time per request:       1.210 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    86434.91 [#/sec] (mean)
Time per request:       1.157 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    86174.21 [#/sec] (mean)
Time per request:       1.160 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    32293.17 [#/sec] (mean)
Time per request:       3.097 [ms] (mean)
Time per request:       0.031 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2098 secs
  Slowest:	0.0100 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	47661.8461
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1915 secs
  Slowest:	0.0114 secs
  Fastest:	0.0002 secs
  Average:	0.0018 secs
  Requests/sec:	52219.9816
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3733 secs
  Slowest:	0.0154 secs
  Fastest:	0.0003 secs
  Average:	0.0035 secs
  Requests/sec:	26786.2922
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6960 secs
  Slowest:	0.0441 secs
  Fastest:	0.0004 secs
  Average:	0.0064 secs
  Requests/sec:	14367.9304
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8356 secs
  Slowest:	0.0270 secs
  Fastest:	0.0005 secs
  Average:	0.0079 secs
  Requests/sec:	11967.9144
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    82157.12 [#/sec] (mean)
Time per request:       1.217 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    73552.67 [#/sec] (mean)
Time per request:       1.360 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12584.05 [#/sec] (mean)
Time per request:       7.947 [ms] (mean)
Time per request:       0.079 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14530.32 [#/sec] (mean)
Time per request:       6.882 [ms] (mean)
Time per request:       0.069 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    87136.10 [#/sec] (mean)
Time per request:       1.148 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    77909.53 [#/sec] (mean)
Time per request:       1.284 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    59903.56 [#/sec] (mean)
Time per request:       1.669 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    80071.74 [#/sec] (mean)
Time per request:       1.249 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    76502.90 [#/sec] (mean)
Time per request:       1.307 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    77787.72 [#/sec] (mean)
Time per request:       1.286 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    84578.04 [#/sec] (mean)
Time per request:       1.182 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3853 secs
  Slowest:	0.0177 secs
  Fastest:	0.0002 secs
  Average:	0.0037 secs
  Requests/sec:	25954.4278
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3769 secs
  Slowest:	0.0206 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	26535.4889
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.8573 secs
  Slowest:	0.0341 secs
  Fastest:	0.0005 secs
  Average:	0.0082 secs
  Requests/sec:	11665.1607
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    16705.87 [#/sec] (mean)
Time per request:       5.986 [ms] (mean)
Time per request:       0.060 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    68089.28 [#/sec] (mean)
Time per request:       1.469 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    54708.49 [#/sec] (mean)
Time per request:       1.828 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    51391.16 [#/sec] (mean)
Time per request:       1.946 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    28811.80 [#/sec] (mean)
Time per request:       3.471 [ms] (mean)
Time per request:       0.035 [ms] (mean, across all concurrent requests)

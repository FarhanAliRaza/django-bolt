# Django-Bolt Benchmark
Generated: Wed Oct 22 10:51:09 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    84935.79 [#/sec] (mean)
Time per request:       1.177 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    87234.15 [#/sec] (mean)
Time per request:       1.146 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    83315.28 [#/sec] (mean)
Time per request:       1.200 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    83151.09 [#/sec] (mean)
Time per request:       1.203 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    86200.21 [#/sec] (mean)
Time per request:       1.160 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    85856.07 [#/sec] (mean)
Time per request:       1.165 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    29642.36 [#/sec] (mean)
Time per request:       3.374 [ms] (mean)
Time per request:       0.034 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2261 secs
  Slowest:	0.0133 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	44228.7458
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2068 secs
  Slowest:	0.0095 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	48358.1670
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3686 secs
  Slowest:	0.0138 secs
  Fastest:	0.0003 secs
  Average:	0.0035 secs
  Requests/sec:	27131.1431
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6329 secs
  Slowest:	0.0165 secs
  Fastest:	0.0004 secs
  Average:	0.0060 secs
  Requests/sec:	15800.6622
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8341 secs
  Slowest:	0.0289 secs
  Fastest:	0.0005 secs
  Average:	0.0080 secs
  Requests/sec:	11989.2200
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    83546.38 [#/sec] (mean)
Time per request:       1.197 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    73000.69 [#/sec] (mean)
Time per request:       1.370 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    13712.38 [#/sec] (mean)
Time per request:       7.293 [ms] (mean)
Time per request:       0.073 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14913.95 [#/sec] (mean)
Time per request:       6.705 [ms] (mean)
Time per request:       0.067 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    84317.03 [#/sec] (mean)
Time per request:       1.186 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    78823.95 [#/sec] (mean)
Time per request:       1.269 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    60946.62 [#/sec] (mean)
Time per request:       1.641 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    79273.22 [#/sec] (mean)
Time per request:       1.261 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    74232.99 [#/sec] (mean)
Time per request:       1.347 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    74170.22 [#/sec] (mean)
Time per request:       1.348 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    82762.96 [#/sec] (mean)
Time per request:       1.208 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.4052 secs
  Slowest:	0.0179 secs
  Fastest:	0.0002 secs
  Average:	0.0039 secs
  Requests/sec:	24679.6220
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3646 secs
  Slowest:	0.0249 secs
  Fastest:	0.0002 secs
  Average:	0.0035 secs
  Requests/sec:	27427.4343
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.8333 secs
  Slowest:	0.0276 secs
  Fastest:	0.0005 secs
  Average:	0.0080 secs
  Requests/sec:	11999.9905
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    16308.11 [#/sec] (mean)
Time per request:       6.132 [ms] (mean)
Time per request:       0.061 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    68178.87 [#/sec] (mean)
Time per request:       1.467 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    54183.51 [#/sec] (mean)
Time per request:       1.846 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    52519.08 [#/sec] (mean)
Time per request:       1.904 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    80486.78 [#/sec] (mean)
Time per request:       1.242 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

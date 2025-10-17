# Django-Bolt Benchmark
Generated: Fri Oct 17 08:44:08 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    41504.80 [#/sec] (mean)
Time per request:       2.409 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    43459.18 [#/sec] (mean)
Time per request:       2.301 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    42063.82 [#/sec] (mean)
Time per request:       2.377 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    41752.26 [#/sec] (mean)
Time per request:       2.395 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    44636.88 [#/sec] (mean)
Time per request:       2.240 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    44825.36 [#/sec] (mean)
Time per request:       2.231 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    23630.72 [#/sec] (mean)
Time per request:       4.232 [ms] (mean)
Time per request:       0.042 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3712 secs
  Slowest:	0.0089 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	26940.1525
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3324 secs
  Slowest:	0.0134 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	30083.8499
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7311 secs
  Slowest:	0.0188 secs
  Fastest:	0.0003 secs
  Average:	0.0070 secs
  Requests/sec:	13678.7740
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1365 secs
  Slowest:	0.0238 secs
  Fastest:	0.0004 secs
  Average:	0.0107 secs
  Requests/sec:	8799.0563
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.4823 secs
  Slowest:	0.0394 secs
  Fastest:	0.0005 secs
  Average:	0.0145 secs
  Requests/sec:	6746.4848
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    40637.19 [#/sec] (mean)
Time per request:       2.461 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    37607.84 [#/sec] (mean)
Time per request:       2.659 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6991.29 [#/sec] (mean)
Time per request:       14.304 [ms] (mean)
Time per request:       0.143 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8099.76 [#/sec] (mean)
Time per request:       12.346 [ms] (mean)
Time per request:       0.123 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    44309.55 [#/sec] (mean)
Time per request:       2.257 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    40121.65 [#/sec] (mean)
Time per request:       2.492 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    20293.24 [#/sec] (mean)
Time per request:       4.928 [ms] (mean)
Time per request:       0.049 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    40046.29 [#/sec] (mean)
Time per request:       2.497 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    38762.24 [#/sec] (mean)
Time per request:       2.580 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    39176.36 [#/sec] (mean)
Time per request:       2.553 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    41672.74 [#/sec] (mean)
Time per request:       2.400 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3960 secs
  Slowest:	0.0150 secs
  Fastest:	0.0002 secs
  Average:	0.0038 secs
  Requests/sec:	25255.4509
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3672 secs
  Slowest:	0.0229 secs
  Fastest:	0.0002 secs
  Average:	0.0035 secs
  Requests/sec:	27230.0386
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	1.4845 secs
  Slowest:	0.0297 secs
  Fastest:	0.0005 secs
  Average:	0.0145 secs
  Requests/sec:	6736.3499
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    8650.47 [#/sec] (mean)
Time per request:       11.560 [ms] (mean)
Time per request:       0.116 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    34994.28 [#/sec] (mean)
Time per request:       2.858 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    7130.39 [#/sec] (mean)
Time per request:       14.024 [ms] (mean)
Time per request:       0.140 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    7323.64 [#/sec] (mean)
Time per request:       13.654 [ms] (mean)
Time per request:       0.137 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    41151.92 [#/sec] (mean)
Time per request:       2.430 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

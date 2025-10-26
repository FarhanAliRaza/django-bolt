# Django-Bolt Benchmark
Generated: Sun Oct 26 08:16:54 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    87222.74 [#/sec] (mean)
Time per request:       1.146 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON  (/10k-json)
Failed requests:        0
Requests per second:    72048.19 [#/sec] (mean)
Time per request:       1.388 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    85033.29 [#/sec] (mean)
Time per request:       1.176 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    82033.78 [#/sec] (mean)
Time per request:       1.219 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    80627.61 [#/sec] (mean)
Time per request:       1.240 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    86764.13 [#/sec] (mean)
Time per request:       1.153 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    87570.28 [#/sec] (mean)
Time per request:       1.142 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    32227.40 [#/sec] (mean)
Time per request:       3.103 [ms] (mean)
Time per request:       0.031 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2005 secs
  Slowest:	0.0096 secs
  Fastest:	0.0002 secs
  Average:	0.0019 secs
  Requests/sec:	49863.7329
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2125 secs
  Slowest:	0.0273 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	47067.4835
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3738 secs
  Slowest:	0.0120 secs
  Fastest:	0.0003 secs
  Average:	0.0035 secs
  Requests/sec:	26755.1136
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6406 secs
  Slowest:	0.0250 secs
  Fastest:	0.0004 secs
  Average:	0.0060 secs
  Requests/sec:	15609.7589
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8088 secs
  Slowest:	0.0248 secs
  Fastest:	0.0005 secs
  Average:	0.0075 secs
  Requests/sec:	12363.4794
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    76583.75 [#/sec] (mean)
Time per request:       1.306 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    70008.40 [#/sec] (mean)
Time per request:       1.428 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    13184.07 [#/sec] (mean)
Time per request:       7.585 [ms] (mean)
Time per request:       0.076 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14790.32 [#/sec] (mean)
Time per request:       6.761 [ms] (mean)
Time per request:       0.068 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    87033.72 [#/sec] (mean)
Time per request:       1.149 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    79251.23 [#/sec] (mean)
Time per request:       1.262 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    59658.75 [#/sec] (mean)
Time per request:       1.676 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    81070.13 [#/sec] (mean)
Time per request:       1.234 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    77258.26 [#/sec] (mean)
Time per request:       1.294 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    67257.18 [#/sec] (mean)
Time per request:       1.487 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    77826.46 [#/sec] (mean)
Time per request:       1.285 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3670 secs
  Slowest:	0.0168 secs
  Fastest:	0.0002 secs
  Average:	0.0035 secs
  Requests/sec:	27244.8829
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3554 secs
  Slowest:	0.0165 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	28133.4238
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.8324 secs
  Slowest:	0.0304 secs
  Fastest:	0.0005 secs
  Average:	0.0080 secs
  Requests/sec:	12013.5817
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    16835.44 [#/sec] (mean)
Time per request:       5.940 [ms] (mean)
Time per request:       0.059 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    68462.20 [#/sec] (mean)
Time per request:       1.461 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    53837.83 [#/sec] (mean)
Time per request:       1.857 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    51677.98 [#/sec] (mean)
Time per request:       1.935 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    79510.22 [#/sec] (mean)
Time per request:       1.258 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

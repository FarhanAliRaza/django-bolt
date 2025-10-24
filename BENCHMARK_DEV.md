# Django-Bolt Benchmark
Generated: Fri Oct 24 05:56:12 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    87840.27 [#/sec] (mean)
Time per request:       1.138 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON  (/10k-json)
Failed requests:        0
Requests per second:    71328.71 [#/sec] (mean)
Time per request:       1.402 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    85293.67 [#/sec] (mean)
Time per request:       1.172 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    84059.04 [#/sec] (mean)
Time per request:       1.190 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    81412.67 [#/sec] (mean)
Time per request:       1.228 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    86917.98 [#/sec] (mean)
Time per request:       1.151 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    87673.15 [#/sec] (mean)
Time per request:       1.141 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    34137.62 [#/sec] (mean)
Time per request:       2.929 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2034 secs
  Slowest:	0.0082 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	49162.5890
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1872 secs
  Slowest:	0.0132 secs
  Fastest:	0.0001 secs
  Average:	0.0018 secs
  Requests/sec:	53414.5051
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3687 secs
  Slowest:	0.0120 secs
  Fastest:	0.0003 secs
  Average:	0.0035 secs
  Requests/sec:	27121.9008
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6428 secs
  Slowest:	0.0220 secs
  Fastest:	0.0004 secs
  Average:	0.0061 secs
  Requests/sec:	15556.1622
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8006 secs
  Slowest:	0.0236 secs
  Fastest:	0.0005 secs
  Average:	0.0076 secs
  Requests/sec:	12491.2285
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    82850.73 [#/sec] (mean)
Time per request:       1.207 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    75356.81 [#/sec] (mean)
Time per request:       1.327 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    13093.00 [#/sec] (mean)
Time per request:       7.638 [ms] (mean)
Time per request:       0.076 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    15226.19 [#/sec] (mean)
Time per request:       6.568 [ms] (mean)
Time per request:       0.066 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    88028.94 [#/sec] (mean)
Time per request:       1.136 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    81185.96 [#/sec] (mean)
Time per request:       1.232 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    61632.14 [#/sec] (mean)
Time per request:       1.623 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    78497.86 [#/sec] (mean)
Time per request:       1.274 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    78306.08 [#/sec] (mean)
Time per request:       1.277 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    80048.03 [#/sec] (mean)
Time per request:       1.249 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    85391.26 [#/sec] (mean)
Time per request:       1.171 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3420 secs
  Slowest:	0.0171 secs
  Fastest:	0.0002 secs
  Average:	0.0033 secs
  Requests/sec:	29241.3125
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3238 secs
  Slowest:	0.0187 secs
  Fastest:	0.0001 secs
  Average:	0.0031 secs
  Requests/sec:	30880.5706
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.8282 secs
  Slowest:	0.0289 secs
  Fastest:	0.0005 secs
  Average:	0.0079 secs
  Requests/sec:	12074.9066
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    15936.33 [#/sec] (mean)
Time per request:       6.275 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    68825.97 [#/sec] (mean)
Time per request:       1.453 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    53646.63 [#/sec] (mean)
Time per request:       1.864 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    52002.35 [#/sec] (mean)
Time per request:       1.923 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    80501.04 [#/sec] (mean)
Time per request:       1.242 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

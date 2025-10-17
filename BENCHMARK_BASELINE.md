# Django-Bolt Benchmark
Generated: Fri Oct 17 10:01:09 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    41883.24 [#/sec] (mean)
Time per request:       2.388 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    42904.09 [#/sec] (mean)
Time per request:       2.331 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    42853.35 [#/sec] (mean)
Time per request:       2.334 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    42024.75 [#/sec] (mean)
Time per request:       2.380 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    44892.17 [#/sec] (mean)
Time per request:       2.228 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    44215.51 [#/sec] (mean)
Time per request:       2.262 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    23663.82 [#/sec] (mean)
Time per request:       4.226 [ms] (mean)
Time per request:       0.042 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3671 secs
  Slowest:	0.0092 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	27243.3130
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3440 secs
  Slowest:	0.0262 secs
  Fastest:	0.0001 secs
  Average:	0.0033 secs
  Requests/sec:	29073.4512
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7286 secs
  Slowest:	0.0152 secs
  Fastest:	0.0003 secs
  Average:	0.0069 secs
  Requests/sec:	13725.1178
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.1014 secs
  Slowest:	0.0208 secs
  Fastest:	0.0004 secs
  Average:	0.0106 secs
  Requests/sec:	9079.3786
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.4865 secs
  Slowest:	0.0289 secs
  Fastest:	0.0005 secs
  Average:	0.0145 secs
  Requests/sec:	6727.2343
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    40913.01 [#/sec] (mean)
Time per request:       2.444 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    37767.06 [#/sec] (mean)
Time per request:       2.648 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6508.26 [#/sec] (mean)
Time per request:       15.365 [ms] (mean)
Time per request:       0.154 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8093.13 [#/sec] (mean)
Time per request:       12.356 [ms] (mean)
Time per request:       0.124 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    45385.85 [#/sec] (mean)
Time per request:       2.203 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    40560.88 [#/sec] (mean)
Time per request:       2.465 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    21761.70 [#/sec] (mean)
Time per request:       4.595 [ms] (mean)
Time per request:       0.046 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    40201.81 [#/sec] (mean)
Time per request:       2.487 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    39324.25 [#/sec] (mean)
Time per request:       2.543 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    40064.58 [#/sec] (mean)
Time per request:       2.496 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    43170.06 [#/sec] (mean)
Time per request:       2.316 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3974 secs
  Slowest:	0.0153 secs
  Fastest:	0.0002 secs
  Average:	0.0038 secs
  Requests/sec:	25166.1639
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3574 secs
  Slowest:	0.0133 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	27979.6831
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	1.5235 secs
  Slowest:	0.0383 secs
  Fastest:	0.0005 secs
  Average:	0.0147 secs
  Requests/sec:	6564.0068
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    8367.58 [#/sec] (mean)
Time per request:       11.951 [ms] (mean)
Time per request:       0.120 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    34834.10 [#/sec] (mean)
Time per request:       2.871 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    7224.27 [#/sec] (mean)
Time per request:       13.842 [ms] (mean)
Time per request:       0.138 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    7448.96 [#/sec] (mean)
Time per request:       13.425 [ms] (mean)
Time per request:       0.134 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    41087.17 [#/sec] (mean)
Time per request:       2.434 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

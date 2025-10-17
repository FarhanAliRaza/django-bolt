# Django-Bolt Benchmark
Generated: Fri Oct 17 09:39:54 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    75508.74 [#/sec] (mean)
Time per request:       1.324 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    79408.57 [#/sec] (mean)
Time per request:       1.259 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    79238.05 [#/sec] (mean)
Time per request:       1.262 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    75986.11 [#/sec] (mean)
Time per request:       1.316 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    81794.24 [#/sec] (mean)
Time per request:       1.223 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    74943.98 [#/sec] (mean)
Time per request:       1.334 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    13061.36 [#/sec] (mean)
Time per request:       7.656 [ms] (mean)
Time per request:       0.077 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2333 secs
  Slowest:	0.0144 secs
  Fastest:	0.0002 secs
  Average:	0.0022 secs
  Requests/sec:	42871.3573
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2219 secs
  Slowest:	0.0120 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	45056.6806
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3899 secs
  Slowest:	0.0148 secs
  Fastest:	0.0003 secs
  Average:	0.0037 secs
  Requests/sec:	25650.0096
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6545 secs
  Slowest:	0.0213 secs
  Fastest:	0.0004 secs
  Average:	0.0062 secs
  Requests/sec:	15279.1686
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8302 secs
  Slowest:	0.0265 secs
  Fastest:	0.0005 secs
  Average:	0.0079 secs
  Requests/sec:	12045.3226
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    66755.23 [#/sec] (mean)
Time per request:       1.498 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    67348.68 [#/sec] (mean)
Time per request:       1.485 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    11540.39 [#/sec] (mean)
Time per request:       8.665 [ms] (mean)
Time per request:       0.087 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14826.41 [#/sec] (mean)
Time per request:       6.745 [ms] (mean)
Time per request:       0.067 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    82139.57 [#/sec] (mean)
Time per request:       1.217 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    74588.46 [#/sec] (mean)
Time per request:       1.341 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    37295.34 [#/sec] (mean)
Time per request:       2.681 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    75644.11 [#/sec] (mean)
Time per request:       1.322 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    72261.64 [#/sec] (mean)
Time per request:       1.384 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    74194.43 [#/sec] (mean)
Time per request:       1.348 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    79532.35 [#/sec] (mean)
Time per request:       1.257 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3737 secs
  Slowest:	0.0167 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	26762.7182
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3506 secs
  Slowest:	0.0158 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	28520.7358
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.8604 secs
  Slowest:	0.0291 secs
  Fastest:	0.0005 secs
  Average:	0.0082 secs
  Requests/sec:	11621.9528
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    15335.05 [#/sec] (mean)
Time per request:       6.521 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    65323.61 [#/sec] (mean)
Time per request:       1.531 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    12509.60 [#/sec] (mean)
Time per request:       7.994 [ms] (mean)
Time per request:       0.080 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    12666.98 [#/sec] (mean)
Time per request:       7.895 [ms] (mean)
Time per request:       0.079 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    74349.44 [#/sec] (mean)
Time per request:       1.345 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

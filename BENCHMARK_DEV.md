# Django-Bolt Benchmark
Generated: Tue Oct 21 05:51:08 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    29624.28 [#/sec] (mean)
Time per request:       3.376 [ms] (mean)
Time per request:       0.034 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    70677.37 [#/sec] (mean)
Time per request:       1.415 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    67562.55 [#/sec] (mean)
Time per request:       1.480 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    47987.87 [#/sec] (mean)
Time per request:       2.084 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    68583.81 [#/sec] (mean)
Time per request:       1.458 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    72734.68 [#/sec] (mean)
Time per request:       1.375 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    24893.77 [#/sec] (mean)
Time per request:       4.017 [ms] (mean)
Time per request:       0.040 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.1770 secs
  Slowest:	0.0079 secs
  Fastest:	0.0001 secs
  Average:	0.0017 secs
  Requests/sec:	56486.0359
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1777 secs
  Slowest:	0.0081 secs
  Fastest:	0.0001 secs
  Average:	0.0017 secs
  Requests/sec:	56263.8467
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.1764 secs
  Slowest:	0.0106 secs
  Fastest:	0.0002 secs
  Average:	0.0017 secs
  Requests/sec:	56675.4601
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.1939 secs
  Slowest:	0.0096 secs
  Fastest:	0.0002 secs
  Average:	0.0018 secs
  Requests/sec:	51564.1458
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.1926 secs
  Slowest:	0.0101 secs
  Fastest:	0.0001 secs
  Average:	0.0018 secs
  Requests/sec:	51922.5225
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    65095.27 [#/sec] (mean)
Time per request:       1.536 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    63207.13 [#/sec] (mean)
Time per request:       1.582 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    11535.14 [#/sec] (mean)
Time per request:       8.669 [ms] (mean)
Time per request:       0.087 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    13398.36 [#/sec] (mean)
Time per request:       7.464 [ms] (mean)
Time per request:       0.075 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    77180.74 [#/sec] (mean)
Time per request:       1.296 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    69162.51 [#/sec] (mean)
Time per request:       1.446 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    37644.79 [#/sec] (mean)
Time per request:       2.656 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    69011.21 [#/sec] (mean)
Time per request:       1.449 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    67304.26 [#/sec] (mean)
Time per request:       1.486 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    68443.93 [#/sec] (mean)
Time per request:       1.461 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    73467.83 [#/sec] (mean)
Time per request:       1.361 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3331 secs
  Slowest:	0.0220 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	30018.4312
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3783 secs
  Slowest:	0.0167 secs
  Fastest:	0.0002 secs
  Average:	0.0035 secs
  Requests/sec:	26436.0079
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.3440 secs
  Slowest:	0.0272 secs
  Fastest:	0.0002 secs
  Average:	0.0033 secs
  Requests/sec:	29072.1867
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    14270.38 [#/sec] (mean)
Time per request:       7.008 [ms] (mean)
Time per request:       0.070 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    59543.66 [#/sec] (mean)
Time per request:       1.679 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    12653.09 [#/sec] (mean)
Time per request:       7.903 [ms] (mean)
Time per request:       0.079 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    11832.15 [#/sec] (mean)
Time per request:       8.452 [ms] (mean)
Time per request:       0.085 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    67063.23 [#/sec] (mean)
Time per request:       1.491 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

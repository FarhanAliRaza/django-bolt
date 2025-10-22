# Django-Bolt Benchmark
Generated: Wed Oct 22 08:55:39 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    63052.50 [#/sec] (mean)
Time per request:       1.586 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    85772.86 [#/sec] (mean)
Time per request:       1.166 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    81914.17 [#/sec] (mean)
Time per request:       1.221 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    78523.75 [#/sec] (mean)
Time per request:       1.274 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    81135.90 [#/sec] (mean)
Time per request:       1.232 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    83169.07 [#/sec] (mean)
Time per request:       1.202 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    26699.77 [#/sec] (mean)
Time per request:       3.745 [ms] (mean)
Time per request:       0.037 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2309 secs
  Slowest:	0.0122 secs
  Fastest:	0.0002 secs
  Average:	0.0022 secs
  Requests/sec:	43316.5875
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1981 secs
  Slowest:	0.0130 secs
  Fastest:	0.0002 secs
  Average:	0.0019 secs
  Requests/sec:	50473.6783
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3960 secs
  Slowest:	0.0188 secs
  Fastest:	0.0003 secs
  Average:	0.0038 secs
  Requests/sec:	25249.6565
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6476 secs
  Slowest:	0.0233 secs
  Fastest:	0.0004 secs
  Average:	0.0060 secs
  Requests/sec:	15441.4009
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8505 secs
  Slowest:	0.0325 secs
  Fastest:	0.0004 secs
  Average:	0.0081 secs
  Requests/sec:	11758.0167
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    79867.74 [#/sec] (mean)
Time per request:       1.252 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    73493.75 [#/sec] (mean)
Time per request:       1.361 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    13355.38 [#/sec] (mean)
Time per request:       7.488 [ms] (mean)
Time per request:       0.075 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    15568.56 [#/sec] (mean)
Time per request:       6.423 [ms] (mean)
Time per request:       0.064 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    37372.14 [#/sec] (mean)
Time per request:       2.676 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    37892.85 [#/sec] (mean)
Time per request:       2.639 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    36158.39 [#/sec] (mean)
Time per request:       2.766 [ms] (mean)
Time per request:       0.028 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    48730.57 [#/sec] (mean)
Time per request:       2.052 [ms] (mean)
Time per request:       0.021 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    28075.30 [#/sec] (mean)
Time per request:       3.562 [ms] (mean)
Time per request:       0.036 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    39183.42 [#/sec] (mean)
Time per request:       2.552 [ms] (mean)
Time per request:       0.026 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    42789.17 [#/sec] (mean)
Time per request:       2.337 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.8854 secs
  Slowest:	0.0814 secs
  Fastest:	0.0002 secs
  Average:	0.0086 secs
  Requests/sec:	11294.2813
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.5063 secs
  Slowest:	0.0350 secs
  Fastest:	0.0002 secs
  Average:	0.0049 secs
  Requests/sec:	19750.1603
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.9910 secs
  Slowest:	0.0419 secs
  Fastest:	0.0005 secs
  Average:	0.0096 secs
  Requests/sec:	10091.2390
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    15895.65 [#/sec] (mean)
Time per request:       6.291 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    58393.14 [#/sec] (mean)
Time per request:       1.713 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    51584.42 [#/sec] (mean)
Time per request:       1.939 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    50926.61 [#/sec] (mean)
Time per request:       1.964 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    75681.32 [#/sec] (mean)
Time per request:       1.321 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

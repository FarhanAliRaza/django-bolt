# Django-Bolt Benchmark
Generated: Fri Oct 31 10:35:56 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    98888.49 [#/sec] (mean)
Time per request:       1.011 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON  (/10k-json)
Failed requests:        0
Requests per second:    85926.16 [#/sec] (mean)
Time per request:       1.164 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    102042.90 [#/sec] (mean)
Time per request:       0.980 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    102332.15 [#/sec] (mean)
Time per request:       0.977 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    97669.60 [#/sec] (mean)
Time per request:       1.024 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    103250.32 [#/sec] (mean)
Time per request:       0.969 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    104254.63 [#/sec] (mean)
Time per request:       0.959 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    28891.30 [#/sec] (mean)
Time per request:       3.461 [ms] (mean)
Time per request:       0.035 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.1992 secs
  Slowest:	0.0079 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	50213.0356
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1974 secs
  Slowest:	0.0205 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	50655.1332
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3430 secs
  Slowest:	0.0136 secs
  Fastest:	0.0002 secs
  Average:	0.0033 secs
  Requests/sec:	29152.0414
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.5582 secs
  Slowest:	0.0148 secs
  Fastest:	0.0004 secs
  Average:	0.0054 secs
  Requests/sec:	17913.9818
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.6828 secs
  Slowest:	0.0185 secs
  Fastest:	0.0004 secs
  Average:	0.0066 secs
  Requests/sec:	14646.5489
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    94557.28 [#/sec] (mean)
Time per request:       1.058 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    87180.92 [#/sec] (mean)
Time per request:       1.147 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    14486.43 [#/sec] (mean)
Time per request:       6.903 [ms] (mean)
Time per request:       0.069 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    16800.28 [#/sec] (mean)
Time per request:       5.952 [ms] (mean)
Time per request:       0.060 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    89463.04 [#/sec] (mean)
Time per request:       1.118 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    75276.83 [#/sec] (mean)
Time per request:       1.328 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    60311.81 [#/sec] (mean)
Time per request:       1.658 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    97608.59 [#/sec] (mean)
Time per request:       1.024 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    91640.55 [#/sec] (mean)
Time per request:       1.091 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    91746.49 [#/sec] (mean)
Time per request:       1.090 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    97331.18 [#/sec] (mean)
Time per request:       1.027 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.1993 secs
  Slowest:	0.0135 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	50175.9090
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.1935 secs
  Slowest:	0.0122 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	51674.0506
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.7287 secs
  Slowest:	0.0280 secs
  Fastest:	0.0004 secs
  Average:	0.0071 secs
  Requests/sec:	13723.1401
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    18096.40 [#/sec] (mean)
Time per request:       5.526 [ms] (mean)
Time per request:       0.055 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    79348.08 [#/sec] (mean)
Time per request:       1.260 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    59703.63 [#/sec] (mean)
Time per request:       1.675 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    59385.95 [#/sec] (mean)
Time per request:       1.684 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    92951.49 [#/sec] (mean)
Time per request:       1.076 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

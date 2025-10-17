# Django-Bolt Benchmark
Generated: Fri Oct 17 10:20:19 PM PKT 2025
Config: 4 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    41478.97 [#/sec] (mean)
Time per request:       2.411 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    42808.40 [#/sec] (mean)
Time per request:       2.336 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    42629.93 [#/sec] (mean)
Time per request:       2.346 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    41841.70 [#/sec] (mean)
Time per request:       2.390 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    44256.21 [#/sec] (mean)
Time per request:       2.260 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    44760.15 [#/sec] (mean)
Time per request:       2.234 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    19315.20 [#/sec] (mean)
Time per request:       5.177 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3740 secs
  Slowest:	0.0107 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	26736.4669
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.3427 secs
  Slowest:	0.0155 secs
  Fastest:	0.0002 secs
  Average:	0.0033 secs
  Requests/sec:	29181.4142
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.7467 secs
  Slowest:	0.0174 secs
  Fastest:	0.0003 secs
  Average:	0.0072 secs
  Requests/sec:	13391.4879
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	1.2319 secs
  Slowest:	0.0316 secs
  Fastest:	0.0004 secs
  Average:	0.0113 secs
  Requests/sec:	8117.2230
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.5218 secs
  Slowest:	0.0329 secs
  Fastest:	0.0005 secs
  Average:	0.0145 secs
  Requests/sec:	6571.3629
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    40892.27 [#/sec] (mean)
Time per request:       2.445 [ms] (mean)
Time per request:       0.024 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    36562.40 [#/sec] (mean)
Time per request:       2.735 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    6930.66 [#/sec] (mean)
Time per request:       14.429 [ms] (mean)
Time per request:       0.144 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    8010.81 [#/sec] (mean)
Time per request:       12.483 [ms] (mean)
Time per request:       0.125 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    45280.83 [#/sec] (mean)
Time per request:       2.208 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    40502.56 [#/sec] (mean)
Time per request:       2.469 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    21345.40 [#/sec] (mean)
Time per request:       4.685 [ms] (mean)
Time per request:       0.047 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    40441.13 [#/sec] (mean)
Time per request:       2.473 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    39793.55 [#/sec] (mean)
Time per request:       2.513 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    40348.29 [#/sec] (mean)
Time per request:       2.478 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    42680.87 [#/sec] (mean)
Time per request:       2.343 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.4061 secs
  Slowest:	0.0153 secs
  Fastest:	0.0002 secs
  Average:	0.0039 secs
  Requests/sec:	24622.4895
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3531 secs
  Slowest:	0.0174 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	28319.6159
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	1.4796 secs
  Slowest:	0.0330 secs
  Fastest:	0.0005 secs
  Average:	0.0143 secs
  Requests/sec:	6758.3749
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    8332.75 [#/sec] (mean)
Time per request:       12.001 [ms] (mean)
Time per request:       0.120 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    34837.62 [#/sec] (mean)
Time per request:       2.870 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    7311.56 [#/sec] (mean)
Time per request:       13.677 [ms] (mean)
Time per request:       0.137 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    7486.27 [#/sec] (mean)
Time per request:       13.358 [ms] (mean)
Time per request:       0.134 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    39995.20 [#/sec] (mean)
Time per request:       2.500 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

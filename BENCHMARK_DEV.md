# Django-Bolt Benchmark
Generated: Wed Oct 22 06:27:51 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    66594.30 [#/sec] (mean)
Time per request:       1.502 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    85508.82 [#/sec] (mean)
Time per request:       1.169 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    84712.02 [#/sec] (mean)
Time per request:       1.180 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    78683.16 [#/sec] (mean)
Time per request:       1.271 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    84160.21 [#/sec] (mean)
Time per request:       1.188 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    84645.34 [#/sec] (mean)
Time per request:       1.181 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    23598.88 [#/sec] (mean)
Time per request:       4.237 [ms] (mean)
Time per request:       0.042 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2290 secs
  Slowest:	0.0124 secs
  Fastest:	0.0002 secs
  Average:	0.0022 secs
  Requests/sec:	43670.2884
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2001 secs
  Slowest:	0.0144 secs
  Fastest:	0.0002 secs
  Average:	0.0019 secs
  Requests/sec:	49974.8444
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3842 secs
  Slowest:	0.0149 secs
  Fastest:	0.0003 secs
  Average:	0.0036 secs
  Requests/sec:	26029.6070
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.7209 secs
  Slowest:	0.0261 secs
  Fastest:	0.0004 secs
  Average:	0.0067 secs
  Requests/sec:	13871.8428
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8417 secs
  Slowest:	0.0311 secs
  Fastest:	0.0005 secs
  Average:	0.0080 secs
  Requests/sec:	11881.0109
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    81958.48 [#/sec] (mean)
Time per request:       1.220 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    75212.85 [#/sec] (mean)
Time per request:       1.330 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12605.30 [#/sec] (mean)
Time per request:       7.933 [ms] (mean)
Time per request:       0.079 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14857.85 [#/sec] (mean)
Time per request:       6.730 [ms] (mean)
Time per request:       0.067 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    88423.58 [#/sec] (mean)
Time per request:       1.131 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    80032.01 [#/sec] (mean)
Time per request:       1.250 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    59884.90 [#/sec] (mean)
Time per request:       1.670 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    79695.88 [#/sec] (mean)
Time per request:       1.255 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    80642.56 [#/sec] (mean)
Time per request:       1.240 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    76620.72 [#/sec] (mean)
Time per request:       1.305 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    86522.40 [#/sec] (mean)
Time per request:       1.156 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3563 secs
  Slowest:	0.0193 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	28065.4807
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3408 secs
  Slowest:	0.0178 secs
  Fastest:	0.0002 secs
  Average:	0.0033 secs
  Requests/sec:	29343.6451
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.8471 secs
  Slowest:	0.0312 secs
  Fastest:	0.0005 secs
  Average:	0.0081 secs
  Requests/sec:	11805.3511
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    15808.40 [#/sec] (mean)
Time per request:       6.326 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    66090.80 [#/sec] (mean)
Time per request:       1.513 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    53464.50 [#/sec] (mean)
Time per request:       1.870 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    50634.71 [#/sec] (mean)
Time per request:       1.975 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    37490.67 [#/sec] (mean)
Time per request:       2.667 [ms] (mean)
Time per request:       0.027 [ms] (mean, across all concurrent requests)

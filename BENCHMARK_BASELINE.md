# Django-Bolt Benchmark
Generated: Tue Oct 21 09:44:00 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    31070.66 [#/sec] (mean)
Time per request:       3.218 [ms] (mean)
Time per request:       0.032 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    80033.93 [#/sec] (mean)
Time per request:       1.249 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    77538.01 [#/sec] (mean)
Time per request:       1.290 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    81842.44 [#/sec] (mean)
Time per request:       1.222 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    79053.26 [#/sec] (mean)
Time per request:       1.265 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    79598.19 [#/sec] (mean)
Time per request:       1.256 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    21025.50 [#/sec] (mean)
Time per request:       4.756 [ms] (mean)
Time per request:       0.048 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.3253 secs
  Slowest:	0.0353 secs
  Fastest:	0.0002 secs
  Average:	0.0030 secs
  Requests/sec:	30736.4604
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2118 secs
  Slowest:	0.0116 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	47213.2018
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.4097 secs
  Slowest:	0.0180 secs
  Fastest:	0.0003 secs
  Average:	0.0039 secs
  Requests/sec:	24406.8849
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6974 secs
  Slowest:	0.0255 secs
  Fastest:	0.0004 secs
  Average:	0.0067 secs
  Requests/sec:	14339.1857
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.9724 secs
  Slowest:	0.0403 secs
  Fastest:	0.0005 secs
  Average:	0.0093 secs
  Requests/sec:	10284.1791
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    65407.78 [#/sec] (mean)
Time per request:       1.529 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    64652.94 [#/sec] (mean)
Time per request:       1.547 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    10852.26 [#/sec] (mean)
Time per request:       9.215 [ms] (mean)
Time per request:       0.092 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    13582.45 [#/sec] (mean)
Time per request:       7.362 [ms] (mean)
Time per request:       0.074 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    81057.64 [#/sec] (mean)
Time per request:       1.234 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    75354.54 [#/sec] (mean)
Time per request:       1.327 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    40695.90 [#/sec] (mean)
Time per request:       2.457 [ms] (mean)
Time per request:       0.025 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    61095.94 [#/sec] (mean)
Time per request:       1.637 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    65159.74 [#/sec] (mean)
Time per request:       1.535 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    77671.71 [#/sec] (mean)
Time per request:       1.287 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    79361.30 [#/sec] (mean)
Time per request:       1.260 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.4254 secs
  Slowest:	0.0209 secs
  Fastest:	0.0002 secs
  Average:	0.0040 secs
  Requests/sec:	23506.6588
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3805 secs
  Slowest:	0.0185 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	26283.7653
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.8742 secs
  Slowest:	0.0334 secs
  Fastest:	0.0005 secs
  Average:	0.0084 secs
  Requests/sec:	11439.2915
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    16533.46 [#/sec] (mean)
Time per request:       6.048 [ms] (mean)
Time per request:       0.060 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    68219.80 [#/sec] (mean)
Time per request:       1.466 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    53493.10 [#/sec] (mean)
Time per request:       1.869 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    49112.54 [#/sec] (mean)
Time per request:       2.036 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    80933.00 [#/sec] (mean)
Time per request:       1.236 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

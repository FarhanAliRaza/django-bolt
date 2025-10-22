# Django-Bolt Benchmark
Generated: Wed Oct 22 08:56:08 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    72130.82 [#/sec] (mean)
Time per request:       1.386 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    84356.86 [#/sec] (mean)
Time per request:       1.185 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    84878.84 [#/sec] (mean)
Time per request:       1.178 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    81726.05 [#/sec] (mean)
Time per request:       1.224 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    87408.00 [#/sec] (mean)
Time per request:       1.144 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    88983.80 [#/sec] (mean)
Time per request:       1.124 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    27302.11 [#/sec] (mean)
Time per request:       3.663 [ms] (mean)
Time per request:       0.037 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2246 secs
  Slowest:	0.0162 secs
  Fastest:	0.0001 secs
  Average:	0.0021 secs
  Requests/sec:	44531.5476
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1938 secs
  Slowest:	0.0087 secs
  Fastest:	0.0002 secs
  Average:	0.0018 secs
  Requests/sec:	51593.4314
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3745 secs
  Slowest:	0.0136 secs
  Fastest:	0.0003 secs
  Average:	0.0036 secs
  Requests/sec:	26705.5397
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6607 secs
  Slowest:	0.0252 secs
  Fastest:	0.0004 secs
  Average:	0.0063 secs
  Requests/sec:	15136.3376
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8199 secs
  Slowest:	0.0266 secs
  Fastest:	0.0005 secs
  Average:	0.0076 secs
  Requests/sec:	12195.8912
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    84959.60 [#/sec] (mean)
Time per request:       1.177 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    74461.83 [#/sec] (mean)
Time per request:       1.343 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12950.92 [#/sec] (mean)
Time per request:       7.721 [ms] (mean)
Time per request:       0.077 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    15087.14 [#/sec] (mean)
Time per request:       6.628 [ms] (mean)
Time per request:       0.066 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    87501.31 [#/sec] (mean)
Time per request:       1.143 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    79988.48 [#/sec] (mean)
Time per request:       1.250 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    61162.83 [#/sec] (mean)
Time per request:       1.635 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    81286.27 [#/sec] (mean)
Time per request:       1.230 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    72836.39 [#/sec] (mean)
Time per request:       1.373 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    79762.63 [#/sec] (mean)
Time per request:       1.254 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    86267.13 [#/sec] (mean)
Time per request:       1.159 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3663 secs
  Slowest:	0.0186 secs
  Fastest:	0.0002 secs
  Average:	0.0035 secs
  Requests/sec:	27296.6721
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3348 secs
  Slowest:	0.0167 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	29866.7674
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.9424 secs
  Slowest:	0.0446 secs
  Fastest:	0.0005 secs
  Average:	0.0090 secs
  Requests/sec:	10610.9903
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    16017.22 [#/sec] (mean)
Time per request:       6.243 [ms] (mean)
Time per request:       0.062 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    66242.71 [#/sec] (mean)
Time per request:       1.510 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    50382.91 [#/sec] (mean)
Time per request:       1.985 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    49623.36 [#/sec] (mean)
Time per request:       2.015 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    80582.77 [#/sec] (mean)
Time per request:       1.241 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

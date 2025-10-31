# Django-Bolt Benchmark
Generated: Fri Oct 31 10:56:08 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    101021.33 [#/sec] (mean)
Time per request:       0.990 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON  (/10k-json)
Failed requests:        0
Requests per second:    83884.17 [#/sec] (mean)
Time per request:       1.192 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    100206.43 [#/sec] (mean)
Time per request:       0.998 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    97078.90 [#/sec] (mean)
Time per request:       1.030 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    97846.40 [#/sec] (mean)
Time per request:       1.022 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    102054.35 [#/sec] (mean)
Time per request:       0.980 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    101326.36 [#/sec] (mean)
Time per request:       0.987 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    21057.15 [#/sec] (mean)
Time per request:       4.749 [ms] (mean)
Time per request:       0.047 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2191 secs
  Slowest:	0.0133 secs
  Fastest:	0.0001 secs
  Average:	0.0021 secs
  Requests/sec:	45639.3454
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1911 secs
  Slowest:	0.0087 secs
  Fastest:	0.0001 secs
  Average:	0.0018 secs
  Requests/sec:	52338.0410
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3585 secs
  Slowest:	0.0144 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	27891.7389
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.5844 secs
  Slowest:	0.0179 secs
  Fastest:	0.0003 secs
  Average:	0.0056 secs
  Requests/sec:	17112.8772
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.7211 secs
  Slowest:	0.0209 secs
  Fastest:	0.0005 secs
  Average:	0.0067 secs
  Requests/sec:	13867.4423
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    70965.77 [#/sec] (mean)
Time per request:       1.409 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    82165.22 [#/sec] (mean)
Time per request:       1.217 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    14509.11 [#/sec] (mean)
Time per request:       6.892 [ms] (mean)
Time per request:       0.069 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    16262.62 [#/sec] (mean)
Time per request:       6.149 [ms] (mean)
Time per request:       0.061 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    101748.03 [#/sec] (mean)
Time per request:       0.983 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    93984.08 [#/sec] (mean)
Time per request:       1.064 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    70886.79 [#/sec] (mean)
Time per request:       1.411 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    96781.06 [#/sec] (mean)
Time per request:       1.033 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    91161.86 [#/sec] (mean)
Time per request:       1.097 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    93008.55 [#/sec] (mean)
Time per request:       1.075 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    101316.10 [#/sec] (mean)
Time per request:       0.987 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.1922 secs
  Slowest:	0.0094 secs
  Fastest:	0.0001 secs
  Average:	0.0018 secs
  Requests/sec:	52024.1120
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.1664 secs
  Slowest:	0.0075 secs
  Fastest:	0.0001 secs
  Average:	0.0016 secs
  Requests/sec:	60096.1759
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.7358 secs
  Slowest:	0.0298 secs
  Fastest:	0.0004 secs
  Average:	0.0071 secs
  Requests/sec:	13591.4714
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    18272.98 [#/sec] (mean)
Time per request:       5.473 [ms] (mean)
Time per request:       0.055 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    72707.71 [#/sec] (mean)
Time per request:       1.375 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    62093.29 [#/sec] (mean)
Time per request:       1.610 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    58302.58 [#/sec] (mean)
Time per request:       1.715 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    88763.44 [#/sec] (mean)
Time per request:       1.127 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

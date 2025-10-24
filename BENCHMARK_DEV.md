# Django-Bolt Benchmark
Generated: Fri Oct 24 06:19:30 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    88285.41 [#/sec] (mean)
Time per request:       1.133 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON  (/10k-json)
Failed requests:        0
Requests per second:    70240.01 [#/sec] (mean)
Time per request:       1.424 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    84286.47 [#/sec] (mean)
Time per request:       1.186 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    83989.85 [#/sec] (mean)
Time per request:       1.191 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    82489.87 [#/sec] (mean)
Time per request:       1.212 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    87746.24 [#/sec] (mean)
Time per request:       1.140 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    88004.15 [#/sec] (mean)
Time per request:       1.136 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    34436.21 [#/sec] (mean)
Time per request:       2.904 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2044 secs
  Slowest:	0.0085 secs
  Fastest:	0.0002 secs
  Average:	0.0019 secs
  Requests/sec:	48930.2188
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1822 secs
  Slowest:	0.0074 secs
  Fastest:	0.0002 secs
  Average:	0.0017 secs
  Requests/sec:	54896.3878
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3923 secs
  Slowest:	0.0156 secs
  Fastest:	0.0003 secs
  Average:	0.0036 secs
  Requests/sec:	25491.1793
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6629 secs
  Slowest:	0.0206 secs
  Fastest:	0.0004 secs
  Average:	0.0062 secs
  Requests/sec:	15085.7799
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8085 secs
  Slowest:	0.0275 secs
  Fastest:	0.0005 secs
  Average:	0.0077 secs
  Requests/sec:	12369.3016
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    83663.81 [#/sec] (mean)
Time per request:       1.195 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    73721.85 [#/sec] (mean)
Time per request:       1.356 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    13181.53 [#/sec] (mean)
Time per request:       7.586 [ms] (mean)
Time per request:       0.076 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    15205.12 [#/sec] (mean)
Time per request:       6.577 [ms] (mean)
Time per request:       0.066 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    87876.55 [#/sec] (mean)
Time per request:       1.138 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    80516.59 [#/sec] (mean)
Time per request:       1.242 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    61083.62 [#/sec] (mean)
Time per request:       1.637 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    79926.47 [#/sec] (mean)
Time per request:       1.251 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    78868.09 [#/sec] (mean)
Time per request:       1.268 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    78679.44 [#/sec] (mean)
Time per request:       1.271 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    87933.73 [#/sec] (mean)
Time per request:       1.137 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3408 secs
  Slowest:	0.0155 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	29345.2999
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3192 secs
  Slowest:	0.0160 secs
  Fastest:	0.0002 secs
  Average:	0.0030 secs
  Requests/sec:	31323.9348
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.8195 secs
  Slowest:	0.0273 secs
  Fastest:	0.0005 secs
  Average:	0.0078 secs
  Requests/sec:	12202.1721
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    15768.32 [#/sec] (mean)
Time per request:       6.342 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    68852.50 [#/sec] (mean)
Time per request:       1.452 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    54965.59 [#/sec] (mean)
Time per request:       1.819 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    52050.80 [#/sec] (mean)
Time per request:       1.921 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    80083.29 [#/sec] (mean)
Time per request:       1.249 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

# Django-Bolt Benchmark
Generated: Sun Oct 26 08:16:27 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    86844.76 [#/sec] (mean)
Time per request:       1.151 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON  (/10k-json)
Failed requests:        0
Requests per second:    65474.16 [#/sec] (mean)
Time per request:       1.527 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    78442.45 [#/sec] (mean)
Time per request:       1.275 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    81461.75 [#/sec] (mean)
Time per request:       1.228 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    81399.42 [#/sec] (mean)
Time per request:       1.229 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    87572.58 [#/sec] (mean)
Time per request:       1.142 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    87607.87 [#/sec] (mean)
Time per request:       1.141 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    32728.40 [#/sec] (mean)
Time per request:       3.055 [ms] (mean)
Time per request:       0.031 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2203 secs
  Slowest:	0.0106 secs
  Fastest:	0.0002 secs
  Average:	0.0021 secs
  Requests/sec:	45391.2251
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1937 secs
  Slowest:	0.0108 secs
  Fastest:	0.0002 secs
  Average:	0.0018 secs
  Requests/sec:	51628.5599
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3621 secs
  Slowest:	0.0155 secs
  Fastest:	0.0003 secs
  Average:	0.0035 secs
  Requests/sec:	27617.2559
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6261 secs
  Slowest:	0.0196 secs
  Fastest:	0.0004 secs
  Average:	0.0060 secs
  Requests/sec:	15972.5148
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.7968 secs
  Slowest:	0.0252 secs
  Fastest:	0.0005 secs
  Average:	0.0075 secs
  Requests/sec:	12549.6355
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    80848.59 [#/sec] (mean)
Time per request:       1.237 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    75244.54 [#/sec] (mean)
Time per request:       1.329 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    13753.08 [#/sec] (mean)
Time per request:       7.271 [ms] (mean)
Time per request:       0.073 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14591.57 [#/sec] (mean)
Time per request:       6.853 [ms] (mean)
Time per request:       0.069 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    85832.49 [#/sec] (mean)
Time per request:       1.165 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    78260.73 [#/sec] (mean)
Time per request:       1.278 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    59200.67 [#/sec] (mean)
Time per request:       1.689 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    81760.80 [#/sec] (mean)
Time per request:       1.223 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    77332.34 [#/sec] (mean)
Time per request:       1.293 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    77139.66 [#/sec] (mean)
Time per request:       1.296 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    85659.71 [#/sec] (mean)
Time per request:       1.167 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.4248 secs
  Slowest:	0.0241 secs
  Fastest:	0.0002 secs
  Average:	0.0041 secs
  Requests/sec:	23539.4832
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3642 secs
  Slowest:	0.0220 secs
  Fastest:	0.0002 secs
  Average:	0.0035 secs
  Requests/sec:	27456.6322
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.8483 secs
  Slowest:	0.0312 secs
  Fastest:	0.0005 secs
  Average:	0.0082 secs
  Requests/sec:	11787.5952
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    16788.47 [#/sec] (mean)
Time per request:       5.956 [ms] (mean)
Time per request:       0.060 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    67969.41 [#/sec] (mean)
Time per request:       1.471 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    55385.40 [#/sec] (mean)
Time per request:       1.806 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    51656.89 [#/sec] (mean)
Time per request:       1.936 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    79096.40 [#/sec] (mean)
Time per request:       1.264 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

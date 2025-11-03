# Django-Bolt Benchmark
Generated: Mon Nov  3 10:21:46 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    103936.06 [#/sec] (mean)
Time per request:       0.962 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON  (/10k-json)
Failed requests:        0
Requests per second:    84720.63 [#/sec] (mean)
Time per request:       1.180 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    106315.12 [#/sec] (mean)
Time per request:       0.941 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    103991.18 [#/sec] (mean)
Time per request:       0.962 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    102510.48 [#/sec] (mean)
Time per request:       0.976 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    106889.00 [#/sec] (mean)
Time per request:       0.936 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    104135.21 [#/sec] (mean)
Time per request:       0.960 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    31097.82 [#/sec] (mean)
Time per request:       3.216 [ms] (mean)
Time per request:       0.032 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.1984 secs
  Slowest:	0.0089 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	50393.0583
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1730 secs
  Slowest:	0.0062 secs
  Fastest:	0.0001 secs
  Average:	0.0016 secs
  Requests/sec:	57818.4719
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3364 secs
  Slowest:	0.0162 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	29730.7319
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.5515 secs
  Slowest:	0.0176 secs
  Fastest:	0.0004 secs
  Average:	0.0053 secs
  Requests/sec:	18132.9888
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.6711 secs
  Slowest:	0.0202 secs
  Fastest:	0.0004 secs
  Average:	0.0064 secs
  Requests/sec:	14901.6687
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    98983.44 [#/sec] (mean)
Time per request:       1.010 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    86167.53 [#/sec] (mean)
Time per request:       1.161 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    18610.81 [#/sec] (mean)
Time per request:       5.373 [ms] (mean)
Time per request:       0.054 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    21344.67 [#/sec] (mean)
Time per request:       4.685 [ms] (mean)
Time per request:       0.047 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    105593.28 [#/sec] (mean)
Time per request:       0.947 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    100032.01 [#/sec] (mean)
Time per request:       1.000 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    71564.03 [#/sec] (mean)
Time per request:       1.397 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    97677.24 [#/sec] (mean)
Time per request:       1.024 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    96863.56 [#/sec] (mean)
Time per request:       1.032 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    99177.82 [#/sec] (mean)
Time per request:       1.008 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    105846.99 [#/sec] (mean)
Time per request:       0.945 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.1923 secs
  Slowest:	0.0190 secs
  Fastest:	0.0001 secs
  Average:	0.0018 secs
  Requests/sec:	52008.2161
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.1690 secs
  Slowest:	0.0100 secs
  Fastest:	0.0001 secs
  Average:	0.0016 secs
  Requests/sec:	59172.9523
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.6958 secs
  Slowest:	0.0230 secs
  Fastest:	0.0004 secs
  Average:	0.0067 secs
  Requests/sec:	14371.4796
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    22627.86 [#/sec] (mean)
Time per request:       4.419 [ms] (mean)
Time per request:       0.044 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    82297.75 [#/sec] (mean)
Time per request:       1.215 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    63778.76 [#/sec] (mean)
Time per request:       1.568 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    59048.26 [#/sec] (mean)
Time per request:       1.694 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    101126.55 [#/sec] (mean)
Time per request:       0.989 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

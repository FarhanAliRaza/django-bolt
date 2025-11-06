# Django-Bolt Benchmark
Generated: Thu Nov  6 09:31:00 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    99970.01 [#/sec] (mean)
Time per request:       1.000 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON  (/10k-json)
Failed requests:        0
Requests per second:    83144.18 [#/sec] (mean)
Time per request:       1.203 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    101559.96 [#/sec] (mean)
Time per request:       0.985 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    101851.66 [#/sec] (mean)
Time per request:       0.982 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    98711.81 [#/sec] (mean)
Time per request:       1.013 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    105282.00 [#/sec] (mean)
Time per request:       0.950 [ms] (mean)
Time per request:       0.009 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    102079.36 [#/sec] (mean)
Time per request:       0.980 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    33346.78 [#/sec] (mean)
Time per request:       2.999 [ms] (mean)
Time per request:       0.030 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2112 secs
  Slowest:	0.0108 secs
  Fastest:	0.0001 secs
  Average:	0.0020 secs
  Requests/sec:	47348.8521
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1780 secs
  Slowest:	0.0073 secs
  Fastest:	0.0001 secs
  Average:	0.0017 secs
  Requests/sec:	56165.4730
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3287 secs
  Slowest:	0.0087 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	30422.7901
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.5688 secs
  Slowest:	0.0194 secs
  Fastest:	0.0003 secs
  Average:	0.0054 secs
  Requests/sec:	17580.8132
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.6782 secs
  Slowest:	0.0184 secs
  Fastest:	0.0005 secs
  Average:	0.0065 secs
  Requests/sec:	14744.0258
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    95255.33 [#/sec] (mean)
Time per request:       1.050 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    91225.06 [#/sec] (mean)
Time per request:       1.096 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    15787.09 [#/sec] (mean)
Time per request:       6.334 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    15972.86 [#/sec] (mean)
Time per request:       6.261 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    95524.67 [#/sec] (mean)
Time per request:       1.047 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    92874.66 [#/sec] (mean)
Time per request:       1.077 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    65391.53 [#/sec] (mean)
Time per request:       1.529 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    92756.63 [#/sec] (mean)
Time per request:       1.078 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    91717.88 [#/sec] (mean)
Time per request:       1.090 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    94909.08 [#/sec] (mean)
Time per request:       1.054 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    99825.31 [#/sec] (mean)
Time per request:       1.002 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.1942 secs
  Slowest:	0.0103 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	51504.9104
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.1797 secs
  Slowest:	0.0075 secs
  Fastest:	0.0001 secs
  Average:	0.0017 secs
  Requests/sec:	55652.6896
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.7736 secs
  Slowest:	0.0335 secs
  Fastest:	0.0005 secs
  Average:	0.0073 secs
  Requests/sec:	12926.7507
Status code distribution:

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    17752.81 [#/sec] (mean)
Time per request:       5.633 [ms] (mean)
Time per request:       0.056 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    76509.92 [#/sec] (mean)
Time per request:       1.307 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    61656.46 [#/sec] (mean)
Time per request:       1.622 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    58304.96 [#/sec] (mean)
Time per request:       1.715 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    94820.88 [#/sec] (mean)
Time per request:       1.055 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

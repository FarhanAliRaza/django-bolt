# Django-Bolt Benchmark
Generated: Thu Nov  6 07:59:56 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    98580.44 [#/sec] (mean)
Time per request:       1.014 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON  (/10k-json)
Failed requests:        0
Requests per second:    79466.62 [#/sec] (mean)
Time per request:       1.258 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    97598.11 [#/sec] (mean)
Time per request:       1.025 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    99584.73 [#/sec] (mean)
Time per request:       1.004 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    96669.73 [#/sec] (mean)
Time per request:       1.034 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    99536.16 [#/sec] (mean)
Time per request:       1.005 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    101253.52 [#/sec] (mean)
Time per request:       0.988 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    29858.50 [#/sec] (mean)
Time per request:       3.349 [ms] (mean)
Time per request:       0.033 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2290 secs
  Slowest:	0.0109 secs
  Fastest:	0.0001 secs
  Average:	0.0022 secs
  Requests/sec:	43669.1659
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2111 secs
  Slowest:	0.0195 secs
  Fastest:	0.0001 secs
  Average:	0.0020 secs
  Requests/sec:	47362.2948
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3703 secs
  Slowest:	0.0176 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	27004.5359
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6035 secs
  Slowest:	0.0167 secs
  Fastest:	0.0004 secs
  Average:	0.0058 secs
  Requests/sec:	16569.0678
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.7227 secs
  Slowest:	0.0179 secs
  Fastest:	0.0005 secs
  Average:	0.0068 secs
  Requests/sec:	13836.8957
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    88929.99 [#/sec] (mean)
Time per request:       1.124 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    87918.27 [#/sec] (mean)
Time per request:       1.137 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    15403.43 [#/sec] (mean)
Time per request:       6.492 [ms] (mean)
Time per request:       0.065 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    15242.76 [#/sec] (mean)
Time per request:       6.560 [ms] (mean)
Time per request:       0.066 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    95274.39 [#/sec] (mean)
Time per request:       1.050 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    97151.52 [#/sec] (mean)
Time per request:       1.029 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    68581.93 [#/sec] (mean)
Time per request:       1.458 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    94502.77 [#/sec] (mean)
Time per request:       1.058 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    92465.88 [#/sec] (mean)
Time per request:       1.081 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    93842.96 [#/sec] (mean)
Time per request:       1.066 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    99091.33 [#/sec] (mean)
Time per request:       1.009 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.2075 secs
  Slowest:	0.0101 secs
  Fastest:	0.0001 secs
  Average:	0.0020 secs
  Requests/sec:	48193.1692
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.1845 secs
  Slowest:	0.0080 secs
  Fastest:	0.0001 secs
  Average:	0.0018 secs
  Requests/sec:	54208.4567
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.7901 secs
  Slowest:	0.0316 secs
  Fastest:	0.0005 secs
  Average:	0.0076 secs
  Requests/sec:	12657.0301
Status code distribution:

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    17419.18 [#/sec] (mean)
Time per request:       5.741 [ms] (mean)
Time per request:       0.057 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    78414.15 [#/sec] (mean)
Time per request:       1.275 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    60898.74 [#/sec] (mean)
Time per request:       1.642 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    57161.15 [#/sec] (mean)
Time per request:       1.749 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    95878.20 [#/sec] (mean)
Time per request:       1.043 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

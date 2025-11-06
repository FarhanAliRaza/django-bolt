# Django-Bolt Benchmark
Generated: Thu Nov  6 11:10:36 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    103595.81 [#/sec] (mean)
Time per request:       0.965 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    86509.68 [#/sec] (mean)
Time per request:       1.156 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    85656.04 [#/sec] (mean)
Time per request:       1.167 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    103352.76 [#/sec] (mean)
Time per request:       0.968 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    104357.99 [#/sec] (mean)
Time per request:       0.958 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    100739.43 [#/sec] (mean)
Time per request:       0.993 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    104575.16 [#/sec] (mean)
Time per request:       0.956 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    104902.07 [#/sec] (mean)
Time per request:       0.953 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    34099.78 [#/sec] (mean)
Time per request:       2.933 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (Async) (/stream)
  Total:	0.1989 secs
  Slowest:	0.0092 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	50271.4667
Status code distribution:
### Streaming Plain Text (Sync) (/sync-stream)
  Total:	0.1941 secs
  Slowest:	0.0091 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	51516.5661
Status code distribution:
### Server-Sent Events (Async) (/sse)
  Total:	0.1712 secs
  Slowest:	0.0086 secs
  Fastest:	0.0001 secs
  Average:	0.0016 secs
  Requests/sec:	58426.5570
Status code distribution:
### Server-Sent Events (Sync) (/sync-sse)
  Total:	0.1690 secs
  Slowest:	0.0092 secs
  Fastest:	0.0001 secs
  Average:	0.0016 secs
  Requests/sec:	59179.6180
Status code distribution:
### Server-Sent Events (Async Generator) (/sse-async)
  Total:	0.3364 secs
  Slowest:	0.0118 secs
  Fastest:	0.0003 secs
  Average:	0.0032 secs
  Requests/sec:	29723.4999
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.5787 secs
  Slowest:	0.0208 secs
  Fastest:	0.0003 secs
  Average:	0.0055 secs
  Requests/sec:	17280.8517
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.7240 secs
  Slowest:	0.0209 secs
  Fastest:	0.0004 secs
  Average:	0.0070 secs
  Requests/sec:	13812.7518
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    91570.90 [#/sec] (mean)
Time per request:       1.092 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    96390.19 [#/sec] (mean)
Time per request:       1.037 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15963.37 [#/sec] (mean)
Time per request:       6.264 [ms] (mean)
Time per request:       0.063 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    15531.28 [#/sec] (mean)
Time per request:       6.439 [ms] (mean)
Time per request:       0.064 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    18258.57 [#/sec] (mean)
Time per request:       5.477 [ms] (mean)
Time per request:       0.055 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    19610.73 [#/sec] (mean)
Time per request:       5.099 [ms] (mean)
Time per request:       0.051 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    103752.74 [#/sec] (mean)
Time per request:       0.964 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    98805.44 [#/sec] (mean)
Time per request:       1.012 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    64496.99 [#/sec] (mean)
Time per request:       1.550 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    92184.59 [#/sec] (mean)
Time per request:       1.085 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    91655.67 [#/sec] (mean)
Time per request:       1.091 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    90983.53 [#/sec] (mean)
Time per request:       1.099 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    98601.83 [#/sec] (mean)
Time per request:       1.014 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.1864 secs
  Slowest:	0.0125 secs
  Fastest:	0.0001 secs
  Average:	0.0018 secs
  Requests/sec:	53633.9739
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.1717 secs
  Slowest:	0.0107 secs
  Fastest:	0.0001 secs
  Average:	0.0016 secs
  Requests/sec:	58238.7639
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.7766 secs
  Slowest:	0.0413 secs
  Fastest:	0.0005 secs
  Average:	0.0075 secs
  Requests/sec:	12876.3461
Status code distribution:

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    18020.58 [#/sec] (mean)
Time per request:       5.549 [ms] (mean)
Time per request:       0.055 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    80350.97 [#/sec] (mean)
Time per request:       1.245 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    61914.14 [#/sec] (mean)
Time per request:       1.615 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    59149.55 [#/sec] (mean)
Time per request:       1.691 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    93332.34 [#/sec] (mean)
Time per request:       1.071 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

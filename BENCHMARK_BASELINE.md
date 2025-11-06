# Django-Bolt Benchmark
Generated: Thu Nov  6 09:30:20 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    99674.07 [#/sec] (mean)
Time per request:       1.003 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON  (/10k-json)
Failed requests:        0
Requests per second:    82323.50 [#/sec] (mean)
Time per request:       1.215 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    101166.45 [#/sec] (mean)
Time per request:       0.988 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    100168.28 [#/sec] (mean)
Time per request:       0.998 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    97623.84 [#/sec] (mean)
Time per request:       1.024 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    103578.64 [#/sec] (mean)
Time per request:       0.965 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    103092.78 [#/sec] (mean)
Time per request:       0.970 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    35147.16 [#/sec] (mean)
Time per request:       2.845 [ms] (mean)
Time per request:       0.028 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2030 secs
  Slowest:	0.0098 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	49253.3442
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1800 secs
  Slowest:	0.0122 secs
  Fastest:	0.0001 secs
  Average:	0.0017 secs
  Requests/sec:	55569.0974
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3328 secs
  Slowest:	0.0125 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	30045.4454
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6462 secs
  Slowest:	0.0407 secs
  Fastest:	0.0004 secs
  Average:	0.0061 secs
  Requests/sec:	15473.8889
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.6719 secs
  Slowest:	0.0189 secs
  Fastest:	0.0004 secs
  Average:	0.0065 secs
  Requests/sec:	14882.7491
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    93540.99 [#/sec] (mean)
Time per request:       1.069 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    91966.71 [#/sec] (mean)
Time per request:       1.087 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    15619.07 [#/sec] (mean)
Time per request:       6.402 [ms] (mean)
Time per request:       0.064 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    18331.13 [#/sec] (mean)
Time per request:       5.455 [ms] (mean)
Time per request:       0.055 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    102998.28 [#/sec] (mean)
Time per request:       0.971 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    96363.25 [#/sec] (mean)
Time per request:       1.038 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    66865.93 [#/sec] (mean)
Time per request:       1.496 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    82990.31 [#/sec] (mean)
Time per request:       1.205 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    93919.64 [#/sec] (mean)
Time per request:       1.065 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    94385.93 [#/sec] (mean)
Time per request:       1.059 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    100406.65 [#/sec] (mean)
Time per request:       0.996 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.1867 secs
  Slowest:	0.0087 secs
  Fastest:	0.0002 secs
  Average:	0.0018 secs
  Requests/sec:	53548.9299
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.1692 secs
  Slowest:	0.0085 secs
  Fastest:	0.0001 secs
  Average:	0.0016 secs
  Requests/sec:	59087.5793
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.7745 secs
  Slowest:	0.0346 secs
  Fastest:	0.0005 secs
  Average:	0.0075 secs
  Requests/sec:	12911.6297
Status code distribution:

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    17409.86 [#/sec] (mean)
Time per request:       5.744 [ms] (mean)
Time per request:       0.057 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    77289.31 [#/sec] (mean)
Time per request:       1.294 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    61312.08 [#/sec] (mean)
Time per request:       1.631 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    58566.87 [#/sec] (mean)
Time per request:       1.707 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    91441.11 [#/sec] (mean)
Time per request:       1.094 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

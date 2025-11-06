# Django-Bolt Benchmark
Generated: Thu Nov  6 11:16:11 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    102606.20 [#/sec] (mean)
Time per request:       0.975 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON (Async) (/10k-json)
Failed requests:        0
Requests per second:    85665.58 [#/sec] (mean)
Time per request:       1.167 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### 10kb JSON (Sync) (/sync-10k-json)
Failed requests:        0
Requests per second:    85689.07 [#/sec] (mean)
Time per request:       1.167 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    103736.59 [#/sec] (mean)
Time per request:       0.964 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    104261.15 [#/sec] (mean)
Time per request:       0.959 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    101429.14 [#/sec] (mean)
Time per request:       0.986 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    104636.44 [#/sec] (mean)
Time per request:       0.956 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    105236.57 [#/sec] (mean)
Time per request:       0.950 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    35882.03 [#/sec] (mean)
Time per request:       2.787 [ms] (mean)
Time per request:       0.028 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (Async) (/stream)
  Total:	0.1985 secs
  Slowest:	0.0109 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	50383.1096
Status code distribution:
### Streaming Plain Text (Sync) (/sync-stream)
  Total:	0.1960 secs
  Slowest:	0.0074 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	51011.8202
Status code distribution:
### Server-Sent Events (Async) (/sse)
  Total:	0.1770 secs
  Slowest:	0.0134 secs
  Fastest:	0.0001 secs
  Average:	0.0017 secs
  Requests/sec:	56499.2385
Status code distribution:
### Server-Sent Events (Sync) (/sync-sse)
  Total:	0.1704 secs
  Slowest:	0.0121 secs
  Fastest:	0.0001 secs
  Average:	0.0016 secs
  Requests/sec:	58681.4516
Status code distribution:
### Server-Sent Events (Async Generator) (/sse-async)
  Total:	0.3380 secs
  Slowest:	0.0124 secs
  Fastest:	0.0003 secs
  Average:	0.0032 secs
  Requests/sec:	29587.7443
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.5766 secs
  Slowest:	0.0157 secs
  Fastest:	0.0003 secs
  Average:	0.0055 secs
  Requests/sec:	17344.0338
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.7168 secs
  Slowest:	0.0172 secs
  Fastest:	0.0004 secs
  Average:	0.0066 secs
  Requests/sec:	13950.9096
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    96514.85 [#/sec] (mean)
Time per request:       1.036 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    94961.35 [#/sec] (mean)
Time per request:       1.053 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## ORM Performance
Seeding 1000 users for benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users Full10 (Async) (/users/full10)
Failed requests:        0
Requests per second:    15722.01 [#/sec] (mean)
Time per request:       6.361 [ms] (mean)
Time per request:       0.064 [ms] (mean, across all concurrent requests)
### Users Full10 (Sync) (/users/sync-full10)
Failed requests:        0
Requests per second:    14291.23 [#/sec] (mean)
Time per request:       6.997 [ms] (mean)
Time per request:       0.070 [ms] (mean, across all concurrent requests)
### Users Mini10 (Async) (/users/mini10)
Failed requests:        0
Requests per second:    19289.57 [#/sec] (mean)
Time per request:       5.184 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)
### Users Mini10 (Sync) (/users/sync-mini10)
Failed requests:        0
Requests per second:    19217.46 [#/sec] (mean)
Time per request:       5.204 [ms] (mean)
Time per request:       0.052 [ms] (mean, across all concurrent requests)
Cleaning up test users...

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    104070.18 [#/sec] (mean)
Time per request:       0.961 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    97787.08 [#/sec] (mean)
Time per request:       1.023 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    70465.71 [#/sec] (mean)
Time per request:       1.419 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    97763.18 [#/sec] (mean)
Time per request:       1.023 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    90009.00 [#/sec] (mean)
Time per request:       1.111 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    93073.47 [#/sec] (mean)
Time per request:       1.074 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    98952.10 [#/sec] (mean)
Time per request:       1.011 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.2002 secs
  Slowest:	0.0107 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	49952.1778
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.1795 secs
  Slowest:	0.0080 secs
  Fastest:	0.0001 secs
  Average:	0.0017 secs
  Requests/sec:	55716.0211
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.7791 secs
  Slowest:	0.0267 secs
  Fastest:	0.0004 secs
  Average:	0.0075 secs
  Requests/sec:	12835.8742
Status code distribution:

## ORM Performance with CBV
Seeding 1000 users for CBV benchmark...
Successfully seeded users
Validated: 10 users exist in database
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    17499.50 [#/sec] (mean)
Time per request:       5.714 [ms] (mean)
Time per request:       0.057 [ms] (mean, across all concurrent requests)
Cleaning up test users...


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    81118.13 [#/sec] (mean)
Time per request:       1.233 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    63690.62 [#/sec] (mean)
Time per request:       1.570 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    58944.54 [#/sec] (mean)
Time per request:       1.697 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    96520.44 [#/sec] (mean)
Time per request:       1.036 [ms] (mean)
Time per request:       0.010 [ms] (mean, across all concurrent requests)

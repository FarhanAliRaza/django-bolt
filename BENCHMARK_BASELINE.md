# Django-Bolt Benchmark
Generated: Tue Oct 21 09:13:59 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    28608.37 [#/sec] (mean)
Time per request:       3.495 [ms] (mean)
Time per request:       0.035 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    65410.35 [#/sec] (mean)
Time per request:       1.529 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    64286.77 [#/sec] (mean)
Time per request:       1.556 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    64705.24 [#/sec] (mean)
Time per request:       1.545 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    66665.78 [#/sec] (mean)
Time per request:       1.500 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    66114.83 [#/sec] (mean)
Time per request:       1.513 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    27920.01 [#/sec] (mean)
Time per request:       3.582 [ms] (mean)
Time per request:       0.036 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2378 secs
  Slowest:	0.0120 secs
  Fastest:	0.0002 secs
  Average:	0.0022 secs
  Requests/sec:	42056.7442
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2338 secs
  Slowest:	0.0138 secs
  Fastest:	0.0002 secs
  Average:	0.0022 secs
  Requests/sec:	42765.0839
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.4106 secs
  Slowest:	0.0147 secs
  Fastest:	0.0003 secs
  Average:	0.0040 secs
  Requests/sec:	24356.0905
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6545 secs
  Slowest:	0.0185 secs
  Fastest:	0.0004 secs
  Average:	0.0063 secs
  Requests/sec:	15279.2748
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8286 secs
  Slowest:	0.0235 secs
  Fastest:	0.0005 secs
  Average:	0.0080 secs
  Requests/sec:	12068.1484
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    62021.27 [#/sec] (mean)
Time per request:       1.612 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    55373.75 [#/sec] (mean)
Time per request:       1.806 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    11801.11 [#/sec] (mean)
Time per request:       8.474 [ms] (mean)
Time per request:       0.085 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    13245.79 [#/sec] (mean)
Time per request:       7.550 [ms] (mean)
Time per request:       0.075 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    68690.75 [#/sec] (mean)
Time per request:       1.456 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    59124.02 [#/sec] (mean)
Time per request:       1.691 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    35923.28 [#/sec] (mean)
Time per request:       2.784 [ms] (mean)
Time per request:       0.028 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    60783.99 [#/sec] (mean)
Time per request:       1.645 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    58903.22 [#/sec] (mean)
Time per request:       1.698 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    61312.83 [#/sec] (mean)
Time per request:       1.631 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    58703.70 [#/sec] (mean)
Time per request:       1.703 [ms] (mean)
Time per request:       0.017 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3934 secs
  Slowest:	0.0191 secs
  Fastest:	0.0002 secs
  Average:	0.0038 secs
  Requests/sec:	25417.2451
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3827 secs
  Slowest:	0.0190 secs
  Fastest:	0.0002 secs
  Average:	0.0036 secs
  Requests/sec:	26131.1344
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.8661 secs
  Slowest:	0.0283 secs
  Fastest:	0.0005 secs
  Average:	0.0084 secs
  Requests/sec:	11545.8689
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    14836.73 [#/sec] (mean)
Time per request:       6.740 [ms] (mean)
Time per request:       0.067 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    53009.34 [#/sec] (mean)
Time per request:       1.886 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    43631.73 [#/sec] (mean)
Time per request:       2.292 [ms] (mean)
Time per request:       0.023 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    35063.36 [#/sec] (mean)
Time per request:       2.852 [ms] (mean)
Time per request:       0.029 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    60622.96 [#/sec] (mean)
Time per request:       1.650 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

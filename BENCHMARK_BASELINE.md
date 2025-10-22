# Django-Bolt Benchmark
Generated: Wed Oct 22 11:49:31 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    75788.01 [#/sec] (mean)
Time per request:       1.319 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## 10kb JSON Response Performance
### 10kb JSON  (/10k-json)
Failed requests:        0
Requests per second:    62156.20 [#/sec] (mean)
Time per request:       1.609 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    73022.55 [#/sec] (mean)
Time per request:       1.369 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    71119.20 [#/sec] (mean)
Time per request:       1.406 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    69398.18 [#/sec] (mean)
Time per request:       1.441 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    75268.33 [#/sec] (mean)
Time per request:       1.329 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    81905.45 [#/sec] (mean)
Time per request:       1.221 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    22422.03 [#/sec] (mean)
Time per request:       4.460 [ms] (mean)
Time per request:       0.045 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2433 secs
  Slowest:	0.0146 secs
  Fastest:	0.0002 secs
  Average:	0.0023 secs
  Requests/sec:	41097.7240
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.2444 secs
  Slowest:	0.0121 secs
  Fastest:	0.0002 secs
  Average:	0.0023 secs
  Requests/sec:	40918.9412
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.4208 secs
  Slowest:	0.0164 secs
  Fastest:	0.0003 secs
  Average:	0.0040 secs
  Requests/sec:	23766.0131
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.7807 secs
  Slowest:	0.0328 secs
  Fastest:	0.0005 secs
  Average:	0.0068 secs
  Requests/sec:	12808.5086
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	1.0009 secs
  Slowest:	0.0465 secs
  Fastest:	0.0005 secs
  Average:	0.0094 secs
  Requests/sec:	9990.9942
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    69759.33 [#/sec] (mean)
Time per request:       1.433 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    65544.54 [#/sec] (mean)
Time per request:       1.526 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12058.51 [#/sec] (mean)
Time per request:       8.293 [ms] (mean)
Time per request:       0.083 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    13532.07 [#/sec] (mean)
Time per request:       7.390 [ms] (mean)
Time per request:       0.074 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    74997.94 [#/sec] (mean)
Time per request:       1.333 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    65872.68 [#/sec] (mean)
Time per request:       1.518 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    52685.93 [#/sec] (mean)
Time per request:       1.898 [ms] (mean)
Time per request:       0.019 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    68210.50 [#/sec] (mean)
Time per request:       1.466 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    66305.52 [#/sec] (mean)
Time per request:       1.508 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    70979.88 [#/sec] (mean)
Time per request:       1.409 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    75799.50 [#/sec] (mean)
Time per request:       1.319 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.5386 secs
  Slowest:	0.0587 secs
  Fastest:	0.0002 secs
  Average:	0.0052 secs
  Requests/sec:	18567.4536
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.4330 secs
  Slowest:	0.0231 secs
  Fastest:	0.0002 secs
  Average:	0.0041 secs
  Requests/sec:	23096.7184
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.9752 secs
  Slowest:	0.0433 secs
  Fastest:	0.0005 secs
  Average:	0.0094 secs
  Requests/sec:	10253.8036
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    15136.79 [#/sec] (mean)
Time per request:       6.606 [ms] (mean)
Time per request:       0.066 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    55836.60 [#/sec] (mean)
Time per request:       1.791 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    46085.50 [#/sec] (mean)
Time per request:       2.170 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    45716.38 [#/sec] (mean)
Time per request:       2.187 [ms] (mean)
Time per request:       0.022 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    72966.07 [#/sec] (mean)
Time per request:       1.371 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

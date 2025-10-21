<<<<<<< HEAD
=======
# Django-Bolt Benchmark
Generated: Tue Oct 21 05:57:15 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    29916.03 [#/sec] (mean)
Time per request:       3.343 [ms] (mean)
Time per request:       0.033 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    68651.61 [#/sec] (mean)
Time per request:       1.457 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    69030.26 [#/sec] (mean)
Time per request:       1.449 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    63452.98 [#/sec] (mean)
Time per request:       1.576 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    66885.16 [#/sec] (mean)
Time per request:       1.495 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    69931.05 [#/sec] (mean)
Time per request:       1.430 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    24206.04 [#/sec] (mean)
Time per request:       4.131 [ms] (mean)
Time per request:       0.041 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.1958 secs
  Slowest:	0.0137 secs
  Fastest:	0.0002 secs
  Average:	0.0019 secs
  Requests/sec:	51073.6731
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1762 secs
  Slowest:	0.0080 secs
  Fastest:	0.0002 secs
  Average:	0.0017 secs
  Requests/sec:	56754.5252
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.1773 secs
  Slowest:	0.0091 secs
  Fastest:	0.0002 secs
  Average:	0.0017 secs
  Requests/sec:	56387.0118
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.1962 secs
  Slowest:	0.0077 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	50979.5696
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.2061 secs
  Slowest:	0.0151 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	48531.5710
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    65684.03 [#/sec] (mean)
Time per request:       1.522 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    62727.78 [#/sec] (mean)
Time per request:       1.594 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    11866.86 [#/sec] (mean)
Time per request:       8.427 [ms] (mean)
Time per request:       0.084 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    13636.63 [#/sec] (mean)
Time per request:       7.333 [ms] (mean)
Time per request:       0.073 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    72991.64 [#/sec] (mean)
Time per request:       1.370 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    67399.98 [#/sec] (mean)
Time per request:       1.484 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    32551.34 [#/sec] (mean)
Time per request:       3.072 [ms] (mean)
Time per request:       0.031 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    66263.34 [#/sec] (mean)
Time per request:       1.509 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    66199.74 [#/sec] (mean)
Time per request:       1.511 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    66183.09 [#/sec] (mean)
Time per request:       1.511 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    71271.77 [#/sec] (mean)
Time per request:       1.403 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.3356 secs
  Slowest:	0.0166 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	29797.1203
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3548 secs
  Slowest:	0.0176 secs
  Fastest:	0.0002 secs
  Average:	0.0034 secs
  Requests/sec:	28185.9618
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.4017 secs
  Slowest:	0.0207 secs
  Fastest:	0.0002 secs
  Average:	0.0038 secs
  Requests/sec:	24894.4221
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    13944.16 [#/sec] (mean)
Time per request:       7.171 [ms] (mean)
Time per request:       0.072 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    50420.76 [#/sec] (mean)
Time per request:       1.983 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    12409.60 [#/sec] (mean)
Time per request:       8.058 [ms] (mean)
Time per request:       0.081 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    10778.72 [#/sec] (mean)
Time per request:       9.278 [ms] (mean)
Time per request:       0.093 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    61642.40 [#/sec] (mean)
Time per request:       1.622 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)
>>>>>>> df3b0bd (bench)

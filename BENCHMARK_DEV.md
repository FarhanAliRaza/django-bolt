# Django-Bolt Benchmark
Generated: Wed Oct 22 06:13:00 PM PKT 2025
Config: 8 processes × 1 workers | C=100 N=10000

## Root Endpoint Performance
Failed requests:        0
Requests per second:    67743.79 [#/sec] (mean)
Time per request:       1.476 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)

## Response Type Endpoints
### Header Endpoint (/header)
Failed requests:        0
Requests per second:    81757.46 [#/sec] (mean)
Time per request:       1.223 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Cookie Endpoint (/cookie)
Failed requests:        0
Requests per second:    84253.10 [#/sec] (mean)
Time per request:       1.187 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Exception Endpoint (/exc)
Failed requests:        0
Requests per second:    82053.98 [#/sec] (mean)
Time per request:       1.219 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### HTML Response (/html)
Failed requests:        0
Requests per second:    86134.87 [#/sec] (mean)
Time per request:       1.161 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Redirect Response (/redirect)
Failed requests:        0
Requests per second:    87738.54 [#/sec] (mean)
Time per request:       1.140 [ms] (mean)
Time per request:       0.011 [ms] (mean, across all concurrent requests)
### File Static via FileResponse (/file-static)
Failed requests:        0
Requests per second:    14288.94 [#/sec] (mean)
Time per request:       6.998 [ms] (mean)
Time per request:       0.070 [ms] (mean, across all concurrent requests)

## Streaming and SSE Performance
### Streaming Plain Text (/stream)
  Total:	0.2130 secs
  Slowest:	0.0126 secs
  Fastest:	0.0002 secs
  Average:	0.0020 secs
  Requests/sec:	46955.8331
Status code distribution:
### Server-Sent Events (/sse)
  Total:	0.1952 secs
  Slowest:	0.0112 secs
  Fastest:	0.0001 secs
  Average:	0.0019 secs
  Requests/sec:	51217.8790
Status code distribution:
### Server-Sent Events (async) (/sse-async)
  Total:	0.3836 secs
  Slowest:	0.0119 secs
  Fastest:	0.0003 secs
  Average:	0.0037 secs
  Requests/sec:	26071.2555
Status code distribution:
### OpenAI Chat Completions (stream) (/v1/chat/completions)
  Total:	0.6605 secs
  Slowest:	0.0182 secs
  Fastest:	0.0004 secs
  Average:	0.0064 secs
  Requests/sec:	15140.4305
Status code distribution:
### OpenAI Chat Completions (async stream) (/v1/chat/completions-async)
  Total:	0.8361 secs
  Slowest:	0.0253 secs
  Fastest:	0.0005 secs
  Average:	0.0079 secs
  Requests/sec:	11960.3476
Status code distribution:

## Items GET Performance (/items/1?q=hello)
Failed requests:        0
Requests per second:    80592.52 [#/sec] (mean)
Time per request:       1.241 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)

## Items PUT JSON Performance (/items/1)
Failed requests:        0
Requests per second:    69761.28 [#/sec] (mean)
Time per request:       1.433 [ms] (mean)
Time per request:       0.014 [ms] (mean, across all concurrent requests)

## ORM Performance
### Users Full10 (/users/full10)
Failed requests:        0
Requests per second:    12861.98 [#/sec] (mean)
Time per request:       7.775 [ms] (mean)
Time per request:       0.078 [ms] (mean, across all concurrent requests)
### Users Mini10 (/users/mini10)
Failed requests:        0
Requests per second:    14985.65 [#/sec] (mean)
Time per request:       6.673 [ms] (mean)
Time per request:       0.067 [ms] (mean, across all concurrent requests)

## Class-Based Views (CBV) Performance
### Simple APIView GET (/cbv-simple)
Failed requests:        0
Requests per second:    85343.89 [#/sec] (mean)
Time per request:       1.172 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Simple APIView POST (/cbv-simple)
Failed requests:        0
Requests per second:    80019.84 [#/sec] (mean)
Time per request:       1.250 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### Items100 ViewSet GET (/cbv-items100)
Failed requests:        0
Requests per second:    60618.92 [#/sec] (mean)
Time per request:       1.650 [ms] (mean)
Time per request:       0.016 [ms] (mean, across all concurrent requests)

## CBV Items - Basic Operations
### CBV Items GET (Retrieve) (/cbv-items/1)
Failed requests:        0
Requests per second:    79249.98 [#/sec] (mean)
Time per request:       1.262 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Items PUT (Update) (/cbv-items/1)
Failed requests:        0
Requests per second:    77732.69 [#/sec] (mean)
Time per request:       1.286 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)

## CBV Additional Benchmarks
### CBV Bench Parse (POST /cbv-bench-parse)
Failed requests:        0
Requests per second:    77271.99 [#/sec] (mean)
Time per request:       1.294 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
### CBV Response Types (/cbv-response)
Failed requests:        0
Requests per second:    86749.08 [#/sec] (mean)
Time per request:       1.153 [ms] (mean)
Time per request:       0.012 [ms] (mean, across all concurrent requests)
### CBV Streaming Plain Text (/cbv-stream)
  Total:	0.4188 secs
  Slowest:	0.0241 secs
  Fastest:	0.0002 secs
  Average:	0.0040 secs
  Requests/sec:	23876.9627
Status code distribution:
### CBV Server-Sent Events (/cbv-sse)
  Total:	0.3357 secs
  Slowest:	0.0152 secs
  Fastest:	0.0002 secs
  Average:	0.0032 secs
  Requests/sec:	29790.3272
Status code distribution:
### CBV Chat Completions (stream) (/cbv-chat-completions)
  Total:	0.8769 secs
  Slowest:	0.0331 secs
  Fastest:	0.0006 secs
  Average:	0.0084 secs
  Requests/sec:	11403.4751
Status code distribution:

## ORM Performance with CBV
### Users CBV Mini10 (List) (/users/cbv-mini10)
Failed requests:        0
Requests per second:    15647.08 [#/sec] (mean)
Time per request:       6.391 [ms] (mean)
Time per request:       0.064 [ms] (mean, across all concurrent requests)


## Form and File Upload Performance
### Form Data (POST /form)
Failed requests:        0
Requests per second:    68310.21 [#/sec] (mean)
Time per request:       1.464 [ms] (mean)
Time per request:       0.015 [ms] (mean, across all concurrent requests)
### File Upload (POST /upload)
Failed requests:        0
Requests per second:    54374.72 [#/sec] (mean)
Time per request:       1.839 [ms] (mean)
Time per request:       0.018 [ms] (mean, across all concurrent requests)
### Mixed Form with Files (POST /mixed-form)
Failed requests:        0
Requests per second:    51154.82 [#/sec] (mean)
Time per request:       1.955 [ms] (mean)
Time per request:       0.020 [ms] (mean, across all concurrent requests)

## Django Ninja-style Benchmarks
### JSON Parse/Validate (POST /bench/parse)
Failed requests:        0
Requests per second:    79588.69 [#/sec] (mean)
Time per request:       1.256 [ms] (mean)
Time per request:       0.013 [ms] (mean, across all concurrent requests)
